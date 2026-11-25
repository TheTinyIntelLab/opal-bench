import numpy as np, pandas as pd

def per_lab_mse(lab, y, pred):
    return pd.Series((np.asarray(pred) - np.asarray(y)) ** 2).groupby(np.asarray(lab)).mean()

def geo_ratio(m, ref, n_boot=2000, seed=0):
    """Return the geometric mean of lab MSE ratios, win count and lab-bootstrap 95% interval."""
    r = np.log((m / ref).values); rng = np.random.default_rng(seed)
    bs = np.exp(np.array([r[rng.integers(0, len(r), len(r))].mean() for _ in range(n_boot)]))
    return {"geo_ratio": float(np.exp(r.mean())), "ci95": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))],
            "wins": int((r < 0).sum()), "n_labs": int(len(r))}

def auroc(y, s):
    y = np.asarray(y); s = np.asarray(s, float); ok = ~np.isnan(s); y, s = y[ok], s[ok]
    n1 = y.sum(); n0 = len(y) - n1
    if n1 == 0 or n0 == 0: return np.nan
    r = pd.Series(s).rank().values
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))

def per_lab_auroc(lab, y, s):
    d = pd.DataFrame({"lab": lab, "y": y, "s": s})
    return d.groupby("lab").apply(lambda g: auroc(g.y.values, g.s.values))

def median_ci(v, n_boot=2000, seed=0):
    v = np.asarray(v.dropna() if hasattr(v, "dropna") else v, float); rng = np.random.default_rng(seed)
    bs = [np.median(v[rng.integers(0, len(v), len(v))]) for _ in range(n_boot)]
    return {"median": float(np.median(v)), "ci95": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))], "n_labs": int(len(v))}
