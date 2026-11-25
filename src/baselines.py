"""Rules and fitted baselines for Opal-Bench. Each fit uses only the data allowed for its task."""
import numpy as np, pandas as pd
from .data import calibration_mask, gene_split_rows, gene_split_train_mask

RULES = ("ADD", "MIN", "MID")

def lin5_X(df):
    lo, hi = df.lo.values, df.hi.values
    return np.c_[np.ones(len(df)), lo, hi, lo + hi, lo * hi, np.abs(hi - lo)]

def fit_lin5(df, lab_weighted=True, ridge=1e-6):
    X = lin5_X(df); y = df.y.values
    w = 1.0 / df.groupby("lab").key.transform("size").values if lab_weighted else np.ones(len(df))
    A = X.T @ (X * w[:, None]) + ridge * np.eye(X.shape[1]); return np.linalg.solve(A, X.T @ (w * y))

def lab_mse(df, pred):
    e = (np.asarray(pred) - df.y.values) ** 2
    return pd.Series(e).groupby(df.lab.values).mean()

def best_rule(df):
    """Choose the rule with the lowest geometric mean of lab MSEs on df."""
    s = {r: float(np.mean(np.log(lab_mse(df, df[r].values)))) for r in RULES}
    return min(s, key=s.get)

def atlas_int(train, keys):
    """Mean over training labs of the pair's (y - MID); 0 if unseen. Lab means first, then mean over labs."""
    g = (train.y - train.MID).groupby([train.lab.values, train.key.values]).mean()
    at = g.groupby(level=1).mean()
    return pd.Series(keys).map(at).fillna(0.0).values

def task_a(P):
    """Held-out-lab (LOLO) zero-shot baselines. Returns DataFrame aligned with P."""
    out = pd.DataFrame({"lab": P.lab.values, "key": P.key.values})
    for r in RULES: out[r] = P[r].values
    out["LIN5"] = np.nan; out["BEST_RULE"] = np.nan; out["ATLAS"] = np.nan; chosen = {}
    for L in sorted(P.lab.unique()):
        te = (P.lab == L).values; tr = P[~te]
        out.loc[te, "LIN5"] = lin5_X(P[te]) @ fit_lin5(tr)
        b = best_rule(tr); chosen[L] = b; out.loc[te, "BEST_RULE"] = P.loc[te, b].values
        out.loc[te, "ATLAS"] = P.MID.values[te] + 0.5 * atlas_int(tr, P.key.values[te])
    return out, chosen

def task_a_fewshot(P, k=20):
    """Few-shot track: k calibration pairs per target lab may be used; evaluation excludes them."""
    cal = calibration_mask(P, k); out = pd.DataFrame({"lab": P.lab.values, "key": P.key.values, "is_cal": cal})
    out["FS_BEST_RULE"] = np.nan; out["FS_LIN5"] = np.nan
    for L in sorted(P.lab.unique()):
        te = (P.lab == L).values; c = P[te & cal]
        s = {r: np.mean((c[r] - c.y) ** 2) for r in RULES}; b = min(s, key=s.get)
        out.loc[te, "FS_BEST_RULE"] = P.loc[te, b].values
        w = fit_lin5(c, lab_weighted=False, ridge=1.0)   # ridge 1.0: 6 coefficients from 20 points
        out.loc[te, "FS_LIN5"] = lin5_X(P[te]) @ w
    return out

def task_b(P):
    """Held-out-gene split within lab (both genes unseen in-lab)."""
    G = gene_split_rows(P); out = pd.DataFrame({"lab": G.lab.values, "key": G.key.values, "fold": G.fold.values})
    for r in RULES: out[r] = G[r].values
    for c in ["LIN5", "BEST_RULE", "ATLAS"]: out[c] = np.nan
    for (L, f), idx in G.groupby(["lab", "fold"]).groups.items():
        rows = np.where((out.lab == L).values & (out.fold == f).values)[0]; te = G.loc[idx]
        tr = P[gene_split_train_mask(P, L, f)]
        out.loc[rows, "LIN5"] = lin5_X(te) @ fit_lin5(tr, lab_weighted=False)
        s = {r: np.mean((tr[r] - tr.y) ** 2) for r in RULES}; out.loc[rows, "BEST_RULE"] = te[min(s, key=s.get)].values
        other = P[P.lab != L]; out.loc[rows, "ATLAS"] = te.MID.values + 0.5 * atlas_int(other, te.key.values)
    return out

def task_c(P, a_preds):
    """Strong-negative-interaction scores (higher = more negative interaction expected). Built from task-a baselines."""
    out = pd.DataFrame({"lab": P.lab.values, "key": P.key.values})
    out["RULE_ADD_MINUS_MIN"] = (P.ADD - P.MIN).values           # zero-fit singles rule
    for c in ["LIN5", "BEST_RULE", "ATLAS"]: out[c] = P.ADD.values - a_preds[c].values
    return out
