"""Score Opal-Bench tracks or rebuild tables from published error rows.

  opal-bench-score fewshot [--split dev|test|fresh|all] [--method pkg.mod:make_method --name NAME ...] [--opal-v1 DIR]
                           [--rows out.csv.gz] [--out leaderboard.md] [--json summary.json] [--data DIR]
      Score ADD, MIN, MID and FS_LIN5_lam, optional Opal v1 methods, or your own adapter.
  opal-bench-score tasks [--pred preds.csv:NAME ...] [--out leaderboard.md] [--json results.json] [--data DIR]
      Run tasks a, a_fs20, b, c and d; see src/evaluate.py for the prediction schema.
  opal-bench-score table ROWS.csv.gz [--out leaderboard.md]
      Rebuild ratios, ranks and rank intervals from per-draw MSE rows.
"""
import argparse, importlib, json, sys, pandas as pd
from . import fewshot as F, leaderboard as LB

def _load(spec):
    mod, _, fn = spec.partition(":"); return getattr(importlib.import_module(mod), fn or "make_method")

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return
    cmd, rest = argv[0], argv[1:]
    if cmd == "tasks":
        from .evaluate import main as ev; return ev(rest)
    ap = argparse.ArgumentParser(prog=f"opal-bench-score {cmd}")
    if cmd == "table":
        ap.add_argument("rows"); ap.add_argument("--out"); a = ap.parse_args(rest); R = pd.read_csv(a.rows); md = []
        for s in ([None] if "split" not in R else sorted(R.split.unique())):
            Rs = R if s is None else R[R.split == s]; md += [f"### {s or 'all'}", "", LB.markdown(LB.tables(Rs))]
        txt = "\n".join(md); print(txt)
        if a.out: open(a.out, "w", encoding="utf-8").write(txt + "\n")
        return
    if cmd != "fewshot":
        sys.exit(f"unknown command {cmd}; see opal-bench-score --help")
    ap.add_argument("--split", default="all"); ap.add_argument("--method", action="append", default=[]); ap.add_argument("--name", action="append", default=[])
    ap.add_argument("--opal-v1"); ap.add_argument("--data"); ap.add_argument("--rows"); ap.add_argument("--out"); ap.add_argument("--json")
    ap.add_argument("--verbose", action="store_true"); a = ap.parse_args(rest)
    M = {}
    for i, spec in enumerate(a.method): M[a.name[i] if i < len(a.name) else spec.rsplit(":", 1)[-1]] = _load(spec)
    if a.opal_v1:
        from .opal_v1 import methods; M.update(methods(a.opal_v1))
    splits = ["dev", "test", "fresh"] if a.split == "all" else a.split.split(","); allr = []; md = ["# Opal-Bench few-shot track", ""]; js = {}
    for s in splits:
        try:
            R = F.run(s, M, data=a.data, verbose=a.verbose)
        except FileNotFoundError as e:
            print(f"skip {s}: {e}", file=sys.stderr); continue
        R.insert(0, "split", s); allr.append(R); T = LB.tables(R); js[s] = LB.summary(T)
        md += [f"## {s}: {R.lab.nunique()} labs, {R.unit.nunique()} units", "", LB.markdown(T)]
    txt = "\n".join(md); print(txt)
    if a.rows and allr: pd.concat(allr).to_csv(a.rows, index=False)
    if a.out: open(a.out, "w", encoding="utf-8").write(txt + "\n")
    if a.json: json.dump(js, open(a.json, "w", encoding="utf-8"), indent=1)

if __name__ == "__main__":
    main()
