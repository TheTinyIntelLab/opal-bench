"""Load data and assign labels and splits. Scores use the per-line scale c; additive growth is sa + sb."""
import os, hashlib, numpy as np, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K_FEWSHOT = 20          # calibration pairs per lab for the few-shot track
MIN_PAIRS_GENE_SPLIT = 1000
N_GENE_FOLDS = 5

def data_dir(path=None):
    for d in [path, os.environ.get("OPAL_BENCH_DATA"), os.path.join(ROOT, "data", "full"), os.path.join(ROOT, "data", "redistributable")]:
        if d and os.path.exists(os.path.join(d, "bench_pairs.csv.gz")):
            return d
    raise FileNotFoundError("bench_pairs.csv.gz not found. Run `python -m opal_bench.prepare` (see README) or set OPAL_BENCH_DATA.")

def load_pairs(path=None):
    d = data_dir(path)
    P = pd.read_csv(os.path.join(d, "bench_pairs.csv.gz"))
    P["lo"] = np.minimum(P.sa, P.sb); P["hi"] = np.maximum(P.sa, P.sb)
    P["ADD"] = P.sa + P.sb; P["MIN"] = P.lo; P["MID"] = 0.5 * (P.ADD + P.MIN)
    P["gA"] = P.y - P.ADD
    med = P.groupby("lab").gA.transform("median")
    mad = P.groupby("lab").gA.transform(lambda v: 1.4826 * np.median(np.abs(v - np.median(v))))
    P["z_gA"] = (P.gA - med) / mad
    P["strong_neg"] = (P.z_gA <= -2).astype(int)
    P["fa"] = P.a.map(gene_fold); P["fb"] = P.b.map(gene_fold)
    return P

def load_priors(path=None):
    d = data_dir(path); f = os.path.join(d, "bench_priors.csv.gz")
    return pd.read_csv(f) if os.path.exists(f) else None

def _h(s):
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)

_FOLD = {}
def gene_fold(g):
    if g not in _FOLD: _FOLD[g] = _h("fold:" + g) % N_GENE_FOLDS
    return _FOLD[g]

def calibration_mask(P, k=K_FEWSHOT):
    """Select the first k pairs per lab in md5(lab|key) order for task a_fs20 calibration."""
    h = np.array([_h("cal:" + l + "|" + k_) for l, k_ in zip(P.lab, P.key)])
    r = pd.Series(h).groupby(P.lab.values).rank(method="first").values
    return r <= k

def gene_split_rows(P):
    """Task b rows: labs with >= MIN_PAIRS_GENE_SPLIT pairs; pairs whose two genes fall in the same gene fold. Column 'fold'."""
    n = P.groupby("lab").key.transform("size")
    fa = P.fa; fb = P.fb
    m = (n >= MIN_PAIRS_GENE_SPLIT) & (fa == fb)
    out = P[m].copy(); out["fold"] = fa[m].values
    return out

def gene_split_train_mask(P, lab, fold):
    """Allowed in-lab training pairs for (lab, fold): neither gene in the fold. Other labs' data may also be used."""
    return (P.lab == lab) & (P.fa != fold) & (P.fb != fold)
