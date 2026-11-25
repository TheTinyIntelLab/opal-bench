"""python -m opal_bench.template --task {a,a_fs20,b,c} --out rows.csv : rows a submission must cover (plus fold / is_cal columns)."""
import argparse
from .data import load_pairs, calibration_mask, gene_split_rows
def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--task", required=True); ap.add_argument("--out", required=True); a = ap.parse_args(argv)
    P = load_pairs()
    if a.task in ("a", "c"): T = P[["lab", "key", "a", "b", "sa", "sb"]].copy()
    elif a.task == "a_fs20": T = P[["lab", "key", "a", "b", "sa", "sb"]].copy(); T["is_cal"] = calibration_mask(P); T["y_if_cal"] = P.y.where(T.is_cal)
    elif a.task == "b": G = gene_split_rows(P); T = G[["lab", "key", "a", "b", "sa", "sb", "fold"]].copy()
    T.insert(0, "task", a.task); T.to_csv(a.out, index=False); print(len(T), "rows ->", a.out)
if __name__ == "__main__": main()
