"""Optional Opal v1 baselines (numpy only), so the v1F and v1R rows can be re-scored.
v1F: Opal v1 frozen K562 growth checkpoint (horlbeck_K562), inputs rescaled to K562 units and back.
v1R: the v1 architecture refit on the k calibration pairs (ridge 1.0 on [1, lo+hi, |hi-lo|, lo*hi] around the v1 node term).
Needs the public Opal v1 growth bundle (Hugging Face TheTinyIntelLab/opal-growth): set OPAL_V1_DIR to the folder that contains
tasks/horlbeck_K562/checkpoint.npz and schema.npz. v1O (the official v1 API with MID fallback) needs the Opal v1 package itself."""
import os, numpy as np, pandas as pd

def load(root=None, task="horlbeck_K562"):
    root = root or os.environ["OPAL_V1_DIR"]; t = os.path.join(root, "tasks", task)
    z = dict(np.load(os.path.join(t, "checkpoint.npz"))); s = dict(np.load(os.path.join(t, "schema.npz")))
    n = int(z["model__matrix_n"]); up = np.ascontiguousarray(z["model__matrix_upper_bytes"].T).reshape(-1).view(np.float64)
    M = np.zeros((n, n)); iu = np.triu_indices(n); M[iu] = up; M = M + M.T - np.diag(np.diag(M))
    return dict(names=[str(x) for x in s["gene_names"]], singles=z["base__singles"], center=z["base__center"], scale=z["base__scale"],
                coef=z["base__coefficient"], offset=float(z["base__offset"]), nodes=bool(z["base__nodes"]), M=M)

def _pred(m, sa, sb, ia, ib, use_nodes=True, use_matrix=True):
    x = np.c_[sa + sb, np.abs(sa - sb), sa * sb]; c, sc, w = m["center"], m["scale"], m["coef"]
    base = (sa + sb) + m["offset"] + ((x - c[:3]) / sc[:3]) @ w[:3]
    if m["nodes"]:   # one-hot gene terms, computed sparsely: sum_j (inc_j - c_j) / s_j * w_j
        wn = w[3:] / sc[3:]; base = base - float(c[3:] @ wn)
        if use_nodes:
            for col in (ia, ib):
                ok = col >= 0; base[ok] += wn[col[ok]]
    res = np.zeros(len(sa))
    if use_matrix:
        ok = (ia >= 0) & (ib >= 0); res[ok] = m["M"][ia[ok], ib[ok]]
    return base + res

def columns(m, D):
    """v1F and v1node columns (normalised units) for a frame with a, b, sa, sb."""
    c = -np.quantile(m["singles"], 0.05); idx = {g: i for i, g in enumerate(m["names"])}
    ia = pd.Series(D.a.values).map(idx).fillna(-1).astype(int).values; ib = pd.Series(D.b.values).map(idx).fillna(-1).astype(int).values
    sa, sb = D.sa.values * c, D.sb.values * c
    f = _pred(m, sa, sb, ia, ib) / c; return f, f - _pred(m, sa, sb, ia, ib, use_nodes=False, use_matrix=False) / c

def methods(root=None):
    m = load(root); cache = {}
    Vd = lambda D: np.c_[np.ones(len(D)), D.lo + D.hi, np.abs(D.hi - D.lo), D.lo * D.hi]
    def cols(D):   # per-unit cache: the v1 columns depend only on (unit, key)
        u = D.unit.iloc[0] if "unit" in D and len(D) else None
        if u not in cache:
            cache.clear(); cache[u] = {}
        c = cache[u]; miss = [k for k in D.key.values if k not in c]
        if miss:
            Dm = D[D.key.isin(set(miss))]; f, n = columns(m, Dm); c.update(zip(Dm.key.values, zip(f, n)))
        v = np.array([c[k] for k in D.key.values]).reshape(-1, 2); return v[:, 0], v[:, 1]
    def v1F(train):
        return lambda cal, ev: cols(ev)[0]
    def v1R(train):
        def p(cal, ev):
            if len(cal) == 0: return None
            fe, ne = cols(ev); _, nc = cols(cal); X = Vd(cal); t = cal.y.values - (cal.lo + cal.hi).values - nc
            w = np.linalg.solve(X.T @ X + np.eye(4), X.T @ t); return (ev.lo + ev.hi).values + ne + Vd(ev) @ w
        return p
    return {"v1F": v1F, "v1R": v1R}
