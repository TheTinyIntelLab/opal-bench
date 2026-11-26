"""Score Opal-Bench tracks or rebuild tables from published error rows.

  opal-bench-score fewshot [--split dev|test|fresh] [--method pkg.mod:make_method --name NAME ...] [--opal-v1 DIR]
                           [--embedding-heads [NAME ...]] [--rows out.csv.gz] [--out leaderboard.md] [--json summary.json] [--data DIR]
      Score ADD, MIN, MID and FS_LIN5_lam, the optional official K562 API, or your own adapter.
  opal-bench-score tasks [--pred preds.csv:NAME ...] [--out leaderboard.md] [--json results.json] [--data DIR]
      Run tasks a, a_fs20, b, c and d; see src/evaluate.py for the prediction schema.
  opal-bench-score tracks [--split dev|test|fresh] [--budget K] [--method pkg.mod:make_method --name NAME ...]
                           [--unseen-method NAME ...] [--embedding-heads [NAME ...]] [--opal-v1 DIR] [--out report.md] [--json report.json]
                           [--baseline-intervals] [--training-intervals] [--historical-rows leaderboard/rows.csv.gz]
      Score unseen-gene MSE, top-5% hits and optional 90% prediction intervals.
  opal-bench-score table ROWS.csv.gz [--out leaderboard.md]
      Rebuild ratios, ranks and rank intervals from per-draw MSE rows.
"""
import argparse, importlib, json, sys, pandas as pd
from pathlib import Path
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
        R = R[~R.model.isin(LB.RETIRED_OPAL_METHODS)]
        for s in ([None] if "split" not in R else sorted(R.split.unique())):
            Rs = R if s is None else R[R.split == s]
            md += [f"### {s or 'Combined'}", "", LB.markdown(LB.tables(Rs))]
        txt = "\n".join(md); print(txt)
        if a.out: open(a.out, "w", encoding="utf-8").write(txt + "\n")
        return
    if cmd not in ("fewshot", "tracks"):
        sys.exit(f"unknown command {cmd}; see opal-bench-score --help")
    from .embedding_heads import METHODS as embedding_heads
    from . import opal_v1

    ap.add_argument("--split", default="all"); ap.add_argument("--method", action="append", default=[]); ap.add_argument("--name", action="append", default=[])
    ap.add_argument("--opal-v1", metavar="DIR", help="Score the official K562 API using the published growth bundle")
    ap.add_argument("--data"); ap.add_argument("--rows"); ap.add_argument("--out"); ap.add_argument("--json")
    ap.add_argument("--embedding-heads", nargs="*", choices=embedding_heads, metavar="NAME",
                    help="Enable the pinned embedding heads. Omit names to enable every head.")
    if cmd == "tracks":
        ap.add_argument("--budget", type=int)
        ap.add_argument("--unseen-method", action="append", default=[])
        ap.add_argument("--baseline-intervals", action="store_true")
        ap.add_argument("--training-intervals", action="store_true",
                        help="Calibrate baseline intervals on an allowed training screen when target labels are insufficient")
        ap.add_argument("--historical-rows", type=Path)
    else:
        ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args(rest)
    if len(a.name) > len(a.method):
        ap.error("--name must correspond to a supplied --method")
    specs = [(a.name[i] if i < len(a.name) else spec.rsplit(":", 1)[-1], spec)
             for i, spec in enumerate(a.method)]
    names = [name for name, _ in specs]
    heads = {} if a.embedding_heads is None else {
        name: embedding_heads[name] for name in (a.embedding_heads or embedding_heads)
    }
    reserved = set(F.BUILTIN) | heads.keys() | LB.RETIRED_OPAL_METHODS
    if a.opal_v1:
        reserved.add(opal_v1.API_METHOD)
    if len(names) != len(set(names)) or reserved.intersection(names):
        ap.error("adapter names must be unique and differ from enabled baseline names")
    M = {**heads, **{name: _load(spec) for name, spec in specs}}
    if a.opal_v1:
        M[opal_v1.API_METHOD] = opal_v1.api_method(a.opal_v1)
    splits = list(F.SPLITS) if a.split == "all" else a.split.split(",")
    if cmd == "tracks":
        from . import tracks

        if any(s not in F.SPLITS for s in splits):
            ap.error("--split must name dev, test or fresh")
        if a.budget is not None and any(a.budget not in F.SPLITS[s]["ks"] for s in splits):
            ap.error("--budget must be supported by every selected split")
        if set(a.unseen_method) - set(M):
            ap.error("--unseen-method must name a supplied adapter")
        eligible = set(F.BUILTIN) | heads.keys() | set(a.unseen_method)
        pretraining = {}
        if a.opal_v1:
            roster = opal_v1.training_genes(a.opal_v1)
            pretraining = {opal_v1.API_METHOD: (roster, opal_v1.K562_LAB)}
            eligible.update(pretraining)
        adapters = {name: (lambda train, predict=predict: predict)
                    for name, predict in F.BUILTIN.items()}
        adapters.update(M)
        budgets = None if a.budget is None else {a.budget}
        if a.training_intervals and not a.baseline_intervals:
            ap.error("--training-intervals requires --baseline-intervals")
        intervals = {}
        if a.baseline_intervals:
            intervals = {name: name == "FS_LIN5_lam" for name in F.BUILTIN}
            if a.opal_v1:
                intervals[opal_v1.API_METHOD] = False
        history = (pd.read_csv(a.historical_rows, usecols=["split", "k", "model"])
                   if a.historical_rows else None)
        if history is not None:
            history = history[~history.model.isin(LB.RETIRED_OPAL_METHODS)]
        results = {}
        raw = []
        for split in splits:
            rows = tracks.run(split, adapters, a.data, budgets, eligible, intervals, pretraining,
                              training_intervals=a.training_intervals)
            if a.rows:
                raw.append(rows.assign(split=split))
            scored = tracks.summarize(rows)
            if history is not None:
                scored = tracks.include_historical_methods(scored, history[history.split == split], budgets)
            results[split] = scored
        report = tracks.markdown(results)
        print(report)
        if a.rows:
            pd.concat(raw).to_csv(a.rows, index=False)
        if a.out:
            Path(a.out).write_text(report, encoding="utf-8")
        if a.json:
            Path(a.json).write_text(json.dumps(results, indent=2, allow_nan=False) + "\n",
                                    encoding="utf-8")
        return
    allr = []; md = ["# Opal-Bench few-shot track", ""]; js = {}
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
