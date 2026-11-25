"""Reproduces the Opal-Bench numbers from the shipped files. Run: pytest -q   (or: python tests/test_reproduce.py)
1. Built-in baselines re-scored on the shipped data equal the leaderboard rows for every shipped unit (dev, test, fresh).
2. Leaderboard tables (ratios, ranks, rank CIs) rebuilt from leaderboard/rows.csv.gz equal tests/expected/leaderboard.json.
3. Tasks a, a_fs20, b, c, d on the 17 shipped labs equal tests/expected/tasks_shipped.json.
4. Opal v1 rows (v1F, v1R) re-scored if OPAL_V1_DIR points at the Opal v1 growth bundle (otherwise skipped)."""
import json, os, tempfile
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
from opal_bench import fewshot as F, leaderboard as LB
from opal_bench.evaluate import main as evaluate
os.environ["OPAL_BENCH_DATA"] = os.path.join(os.path.dirname(HERE), "data", "redistributable")   # always test the shipped files
ROWS = pd.read_csv(os.path.join(os.path.dirname(HERE), "leaderboard", "rows.csv.gz"))
EXP = lambda f: json.load(open(os.path.join(HERE, "expected", f), encoding="utf-8"))

def _match(R, split, models):
    L = ROWS[(ROWS.split == split) & ROWS.model.isin(models)]
    m = R.merge(L, on=["unit", "k", "draw", "model"], suffixes=("", "_lb"), how="left")
    assert m.mse_lb.notna().all(), f"{split}: rows missing from leaderboard"
    assert np.allclose(m.mse, m.mse_lb, rtol=1e-8, atol=0), f"{split}: max rel diff {np.max(np.abs(m.mse / m.mse_lb - 1))}"
    return len(m)

def test_fewshot_baselines_match_leaderboard_rows():
    exp = EXP("fewshot_shipped.json")
    for s in ("dev", "test", "fresh"):
        R = F.run(s); n = _match(R, s, ["ADD", "MIN", "MID", "FS_LIN5_lam"]); assert n == len(R)
        got = LB.summary(LB.tables(R))
        for k in exp[s]:
            for m, v in exp[s][k].items(): assert abs(got[k][m] - v) < 1e-6, (s, k, m)

def test_leaderboard_tables():
    exp = EXP("leaderboard.json")
    for s, ks in exp.items():
        T = LB.tables(ROWS[ROWS.split == s])
        for k, rows in ks.items():
            for m, e in rows.items():
                r = T[int(k)].loc[m]
                assert abs(r.ratio_vs_MID - e["ratio"]) < 1e-6 and (int(r["rank"]), int(r.rank_lo), int(r.rank_hi)) == (e["rank"], e["rank_lo"], e["rank_hi"]), (s, k, m)

def test_tasks_shipped():
    exp = EXP("tasks_shipped.json")
    with tempfile.TemporaryDirectory() as d:
        js = os.path.join(d, "r.json"); evaluate(["--json", js, "--out", os.path.join(d, "lb.md")]); R = json.load(open(js, encoding="utf-8"))
    assert R["n_pairs"] == exp["n_pairs"] and R["n_labs"] == exp["n_labs"]
    for t in ("a", "a_fs20", "b"):
        for r in R[t]["rows"]:
            e = exp[t][r["method"]]; assert abs(r["geo_mse"] - e["geo_mse"]) < 1e-9
            for k, v in r.items():
                if k.startswith("vs_"): assert abs(v["geo_ratio"] - e[k]) < 1e-9, (t, r["method"], k)
    for r in R["c"]["rows"]: assert abs(r["auroc_median"] - exp["c"][r["method"]]) < 1e-9
    assert abs(R["d"]["median_rho"] - exp["d"]["median_rho"]) < 1e-9

def test_opal_v1_rows():
    if not os.environ.get("OPAL_V1_DIR"):
        print("skip: set OPAL_V1_DIR to re-score Opal v1"); return
    from opal_bench.opal_v1 import methods
    for s in ("dev", "test", "fresh"):
        R = F.run(s, methods(), with_builtin=False); _match(R, s, ["v1F", "v1R"])

if __name__ == "__main__":
    for f in [test_fewshot_baselines_match_leaderboard_rows, test_leaderboard_tables, test_tasks_shipped, test_opal_v1_rows]:
        f(); print("PASS", f.__name__)
