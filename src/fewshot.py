"""Score the main Opal-Bench track with each target lab held out of training.

A method trains on other labs' pairs, receives k measured pairs from the target unit, and predicts its remaining pairs.
Ratio = exp(mean over labs of mean over units of mean over draws of log(MSE / MSE_MID)).

Splits
  dev    units = the 18 development labs (lab-level table), nested leave-one-lab-out: training = the other dev labs.
         k in {0, 10, 20, 50}, 20 draws, draw seed md5(lab|k|random|r).
  test   units = 31 cell lines of the 4 locked test labs, training = all dev labs.
         k in {0, 10, 20, 50}, 20 draws, draw seed md5(conf19|unit|k|r).
  fresh  units = the 2 SHEN26 cell lines (2026 screen, never used in development), training = every lab in the table.
         k in {0, 5, 20}, 50 draws, draw seed md5(conf32|unit|k|r).
At k = 0 there is one draw and the whole unit is scored. Calibration pairs are excluded from scoring.

Method interface (plain Python, numpy/pandas):
    def make_method(train: pd.DataFrame) -> predict      # called once per training set
    def predict(cal: pd.DataFrame, ev: pd.DataFrame) -> np.ndarray | Prediction | None
Columns available: lab, unit, key, a, b, sa, sb, lo, hi, ADD, MIN, MID (+ y for train/cal).
Evaluation includes optional published input columns where present.
Run:  opal-bench-score fewshot --method mypackage.mymodule:make_method --name MYMODEL
"""
import hashlib, os, numpy as np, pandas as pd
from dataclasses import dataclass
from .data import ROOT, load_pairs

TEST_LABS = ("BURGOLD25", "HAN17", "KLINGBEIL24", "SCHEMATIC25")
SPLITS = {"dev": dict(ks=(0, 10, 20, 50), draws=20), "test": dict(ks=(0, 10, 20, 50), draws=20), "fresh": dict(ks=(0, 5, 20), draws=50)}
FS_LIN5_LAM = 0.1   # ridge strength of FS_LIN5_lam, fixed before any test scoring
PREDICTOR_COLUMNS = ["lab", "unit", "key", "a", "b", "sa", "sb", "lo", "hi", "ADD", "MIN", "MID"]
OPTIONAL_INPUTS = ["n_lines", "scale_c", "string", "para_id", "fa", "fb"]


@dataclass(frozen=True)
class Prediction:
    """One point estimate and two bounds per evaluation pair for a 90% interval."""

    point: np.ndarray
    lower: np.ndarray
    upper: np.ndarray
    interval_source: str | None = None


def predictor_inputs(rows, *, labeled=False):
    columns = PREDICTOR_COLUMNS + [name for name in OPTIONAL_INPUTS if name in rows]
    return rows[columns + ["y"] if labeled else columns]


def prediction_vector(values, length, name):
    vector = np.asarray(values, dtype=float)
    if vector.shape != (length,) or not np.isfinite(vector).all():
        raise ValueError(f"{name} must contain one finite value per evaluation pair")
    return vector

def mseed(*a):
    return int(hashlib.md5("|".join(map(str, a)).encode()).hexdigest()[:8], 16)

def _basic(D):
    D = D.copy(); D["lo"] = np.minimum(D.sa, D.sb); D["hi"] = np.maximum(D.sa, D.sb)
    D["ADD"] = D.sa + D.sb; D["MIN"] = D.lo; D["MID"] = D.lo + 0.5 * D.hi; return D

def load_test_units(path=None):
    """Load locked-test cell lines. BURGOLD25 ships here; other labs need independently prepared local tables."""
    for d in [path, os.environ.get("OPAL_BENCH_DATA"), os.path.join(ROOT, "data", "full"), os.path.join(ROOT, "data", "redistributable")]:
        if d and os.path.exists(os.path.join(d, "test_units.csv.gz")):
            return _basic(pd.read_csv(os.path.join(d, "test_units.csv.gz")))
    raise FileNotFoundError("test_units.csv.gz not found")

def load_fresh():
    return _basic(pd.read_csv(os.path.join(ROOT, "data", "fresh", "SHEN26.csv.gz")))

def units(split, data=None):
    """Yields (unit, lab, D, train, seedfn) in the fixed order used for the leaderboard."""
    P = load_pairs(data); P["unit"] = P.lab
    if split == "dev":
        Pd = P[~P.lab.isin(TEST_LABS)].reset_index(drop=True)
        for L in sorted(Pd.lab.unique()):
            yield L, L, Pd[Pd.lab == L].reset_index(drop=True), Pd[Pd.lab != L].reset_index(drop=True), (lambda k, r, L=L: mseed(L, k, "random", r))
    elif split == "test":
        T = load_test_units(data); tr = P[~P.lab.isin(TEST_LABS)].reset_index(drop=True)
        for u, D in T.groupby("unit", sort=True):
            yield u, D.lab.iloc[0], D.reset_index(drop=True), tr, (lambda k, r, u=u: mseed("conf19", u, k, r))
    elif split == "fresh":
        F = load_fresh()
        for u, D in F.groupby("unit", sort=True):
            yield u, "SHEN26", D.reset_index(drop=True), P, (lambda k, r, u=u: mseed("conf32", u, k, r))
    else:
        raise ValueError(split)

def draws(D, split, seedfn):
    cfg = SPLITS[split]
    for k in cfg["ks"]:
        for r in (range(cfg["draws"]) if k else [0]):
            ci = np.random.default_rng(seedfn(k, r)).choice(len(D), min(k, len(D)), replace=False) if k else np.array([], int)
            m = np.zeros(len(D), bool); m[ci] = True
            yield k, r, m

# ---------------- built-in baselines ----------------
def X6(D):
    lo, hi = D.lo.values, D.hi.values; return np.c_[np.ones(len(D)), lo, hi, lo + hi, lo * hi, np.abs(hi - lo)]

def ridge(X, y, lam):
    return np.linalg.solve(X.T @ X + lam * np.eye(X.shape[1]), X.T @ y)

def _fewshot_ridge(cal, ev):
    if len(cal):
        return X6(ev) @ ridge(X6(cal), cal.y.values, FS_LIN5_LAM)


BUILTIN = {
    "ADD": lambda cal, ev: ev.ADD.values,
    "MIN": lambda cal, ev: ev.lo.values,
    "MID": lambda cal, ev: ev.MID.values,
    "FS_LIN5_lam": _fewshot_ridge,
}


def builtin(cal, ev, k):
    return {name: predict(cal, ev) for name, predict in BUILTIN.items()
            if name != "FS_LIN5_lam" or k}

def run(split, methods=None, data=None, with_builtin=True, verbose=False):
    """methods: {name: make_method}. Returns rows (unit, lab, k, draw, model, mse)."""
    methods = methods or {}; rows = []
    for u, lab, D, train, seedfn in units(split, data):
        preds = {n: mk(train) for n, mk in methods.items()}
        for k, r, m in draws(D, split, seedfn):
            if m.all():
                continue
            cal, ev = D[m], D[~m]
            predictions = builtin(cal, ev, k) if with_builtin else {}
            if preds:
                labeled, inputs = predictor_inputs(cal, labeled=True), predictor_inputs(ev)
                for name, predict in preds.items():
                    result = predict(labeled, inputs)
                    if result is not None:
                        point = result.point if isinstance(result, Prediction) else result
                        predictions[name] = prediction_vector(point, len(ev), f"{name} prediction")
            for name, point in predictions.items():
                mse = float(np.mean((point - ev.y.values) ** 2))
                rows.append(dict(unit=u, lab=lab, k=k, draw=r, model=name, mse=mse))
        if verbose: print(split, u, flush=True)
    return pd.DataFrame(rows, columns=["unit", "lab", "k", "draw", "model", "mse"])
