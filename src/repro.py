"""Report task d: Spearman correlation of gA = y - (sa + sb) for pairs shared by two labs."""
import itertools, numpy as np, pandas as pd

def _sp(x, y):
    return float(np.corrcoef(pd.Series(x).rank(), pd.Series(y).rank())[0, 1])

def report(P, min_shared=20, n_boot=2000, seed=0):
    W = P.pivot_table(index="key", columns="lab", values="gA"); rows = []
    for a, b in itertools.combinations(W.columns, 2):
        m = W[a].notna() & W[b].notna()
        if m.sum() >= min_shared: rows.append({"lab_a": a, "lab_b": b, "n_shared": int(m.sum()), "rho": _sp(W[a][m], W[b][m])})
    T = pd.DataFrame(rows); rng = np.random.default_rng(seed); labs = sorted(set(T.lab_a) | set(T.lab_b))
    bs = []
    for _ in range(n_boot):   # lab-level bootstrap of the median between-lab rho
        s = set(rng.choice(labs, len(labs), replace=True)); t = T[T.lab_a.isin(s) & T.lab_b.isin(s)]
        if len(t): bs.append(t.rho.median())
    per = {l: float(T[(T.lab_a == l) | (T.lab_b == l)].rho.median()) for l in labs}
    sp_n = _sp(np.log(T.n_shared), T.rho)
    rep = {"n_lab_pairs": int(len(T)), "median_rho": float(T.rho.median()), "ci95_lab_bootstrap": [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))],
           "spearman_rho_vs_log_overlap": sp_n, "per_lab_median_rho": per, "pairs": T.to_dict("records")}
    md = ["## Task d: cross-lab reproducibility (descriptive)",
          f"{len(T)} lab pairs with >= {min_shared} shared pairs. Median between-lab Spearman rho of gA = {rep['median_rho']:.3f} "
          f"(lab-bootstrap 95% CI {rep['ci95_lab_bootstrap'][0]:.3f} to {rep['ci95_lab_bootstrap'][1]:.3f}). rho vs log(overlap): {sp_n:+.3f}.", "",
          "| lab | median rho with other labs |", "|---|---|"] + [f"| {l} | {v:.3f} |" for l, v in sorted(per.items(), key=lambda x: -x[1])]
    return rep, "\n".join(md)

if __name__ == "__main__":
    from .data import load_pairs
    print(report(load_pairs())[1])
