"""python -m opal_bench.evaluate --pred preds.csv[:NAME] [--pred other.csv:NAME2] [--out leaderboard.md] [--json results.json]

preds.csv columns: task, lab, key, pred
  task a      held-out-lab, zero-shot: predict normalised pair score y for every (lab, key); train only on OTHER labs.
  task a_fs20 few-shot track: may also use the 20 calibration pairs of the target lab (see calibration_pairs.csv); scored on the rest.
  task b      held-out-gene within lab: rows from `python -m opal_bench.template --task b`; train only on that lab's pairs with
              neither gene in the row's fold (other labs allowed).
  task c      strong-negative-interaction score (higher = more likely z(gA) <= -2); same information rules as task a.
"""
import argparse, json, sys, numpy as np, pandas as pd
from .data import load_pairs, calibration_mask, gene_split_rows
from . import baselines as B
from .metrics import per_lab_mse, geo_ratio, per_lab_auroc, median_ci

def _merge(base, sub, name, allow_partial):
    s = sub[["lab", "key", "pred"]].drop_duplicates(["lab", "key"]).rename(columns={"pred": name})
    m = base.merge(s, on=["lab", "key"], how="left"); cov = float(m[name].notna().mean())
    if cov < 1 and not allow_partial:
        sys.exit(f"{name}: covers {cov:.1%} of rows for this task; use --allow-partial to score the covered subset.")
    return m, cov

def regression_table(df, methods, refs):
    rows = []; ok = df[methods].notna().all(axis=1); d = df[ok]
    M = {m: per_lab_mse(d.lab, d.y, d[m]) for m in methods}
    fixed = {r: float(np.exp(np.mean(np.log(M[r])))) for r in B.RULES if r in M}
    best_fixed = min(fixed, key=fixed.get) if fixed else None
    for m in methods:
        row = {"method": m, "geo_mse": float(np.exp(np.mean(np.log(M[m]))))}
        for rname in list(dict.fromkeys(refs + ([best_fixed] if best_fixed else []))):
            g = geo_ratio(M[m], M[rname]); row[f"vs_{rname}"] = g
        rows.append(row)
    return rows, best_fixed, {m: M[m].to_dict() for m in methods}, int(ok.sum())

def fmt_reg(rows, best_fixed, refs):
    cols = list(dict.fromkeys(refs + [best_fixed]))
    h = "| method | geo-mean MSE | " + " | ".join(f"vs {c}{' (best fixed rule)' if c == best_fixed else ''}: ratio [95% CI] wins" for c in cols) + " |"
    s = [h, "|" + "---|" * (2 + len(cols))]
    for r in sorted(rows, key=lambda r: r["geo_mse"]):
        cells = []
        for c in cols:
            g = r[f"vs_{c}"]; cells.append(f"{g['geo_ratio']:.3f} [{g['ci95'][0]:.3f}, {g['ci95'][1]:.3f}] {g['wins']}/{g['n_labs']}")
        s.append(f"| {r['method']} | {r['geo_mse']:.4f} | " + " | ".join(cells) + " |")
    return "\n".join(s)

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--pred", action="append", default=[]); ap.add_argument("--data")
    ap.add_argument("--out"); ap.add_argument("--json"); ap.add_argument("--allow-partial", action="store_true")
    ap.add_argument("--tasks", default="a,a_fs20,b,c,d"); a = ap.parse_args(argv)
    P = load_pairs(a.data); subs = []
    for spec in a.pred:
        f, _, nm = spec.partition(":"); subs.append((nm or f.rsplit("/", 1)[-1].replace(".csv", ""), pd.read_csv(f)))
    tasks = a.tasks.split(","); R = {"n_pairs": int(len(P)), "n_labs": int(P.lab.nunique())}; md = ["# Opal-Bench leaderboard", ""]
    A, chosen = B.task_a(P); A["y"] = P.y.values
    if "a" in tasks:
        base = A.copy(); meths = list(B.RULES) + ["LIN5", "BEST_RULE", "ATLAS"]
        for nm, s in subs:
            if (s.task == "a").any(): base, cov = _merge(base, s[s.task == "a"], nm, a.allow_partial); meths.append(nm)
        rows, bf, per, n = regression_table(base, meths, ["MID", "MIN"])
        R["a"] = {"rows": rows, "best_fixed_rule": bf, "per_lab_mse": per, "n_scored": n, "best_rule_chosen_per_lab": chosen}
        md += ["## Task a: held-out lab (LOLO), zero-shot pair-score MSE", f"{P.lab.nunique()} labs, {n:,} pairs. Ratios < 1 favour the method. CI = lab bootstrap.", "", fmt_reg(rows, bf, ["MID", "MIN"]), ""]
    if "a_fs20" in tasks:
        F = B.task_a_fewshot(P); base = A.merge(F, on=["lab", "key"]); base = base[~base.is_cal].copy()
        meths = list(B.RULES) + ["LIN5", "BEST_RULE", "ATLAS", "FS_BEST_RULE", "FS_LIN5"]
        for nm, s in subs:
            if (s.task == "a_fs20").any(): base, cov = _merge(base, s[s.task == "a_fs20"], nm, a.allow_partial); meths.append(nm)
        rows, bf, per, n = regression_table(base, meths, ["FS_BEST_RULE", "MID"])
        R["a_fs20"] = {"rows": rows, "best_fixed_rule": bf, "per_lab_mse": per, "n_scored": n}
        md += ["## Task a_fs20: held-out lab, few-shot track (20 calibration pairs per lab; scored on the rest)", "", fmt_reg(rows, bf, ["FS_BEST_RULE", "MID"]), ""]
    if "b" in tasks:
        Bt = B.task_b(P); G = gene_split_rows(P); Bt["y"] = G.y.values; meths = list(B.RULES) + ["LIN5", "BEST_RULE", "ATLAS"]
        for nm, s in subs:
            if (s.task == "b").any(): Bt, cov = _merge(Bt, s[s.task == "b"], nm, a.allow_partial); meths.append(nm)
        rows, bf, per, n = regression_table(Bt, meths, ["LIN5", "MID"])
        R["b"] = {"rows": rows, "best_fixed_rule": bf, "per_lab_mse": per, "n_scored": n}
        md += ["## Task b: held-out genes within lab (both genes unseen in-lab), MSE", f"{Bt.lab.nunique()} labs with >= 1,000 pairs, {n:,} test pairs.", "", fmt_reg(rows, bf, ["LIN5", "MID"]), ""]
    if "c" in tasks:
        C = B.task_c(P, A); C["label"] = P.strong_neg.values; meths = ["RULE_ADD_MINUS_MIN", "LIN5", "BEST_RULE", "ATLAS"]
        for nm, s in subs:
            if (s.task == "c").any(): C, cov = _merge(C, s[s.task == "c"], nm, a.allow_partial); meths.append(nm)
        ok = C[meths].notna().all(axis=1); C = C[ok]; AU = {m: per_lab_auroc(C.lab.values, C.label.values, C[m].values) for m in meths}
        rows = []
        for m in meths:
            d = AU[m] - AU["RULE_ADD_MINUS_MIN"]
            rows.append({"method": m, **{"auroc_" + k: v for k, v in median_ci(AU[m]).items()}, "wins_vs_rule": int((d > 0).sum()), "median_dAUROC_vs_rule": float(d.median())})
        R["c"] = {"rows": rows, "per_lab_auroc": {m: AU[m].to_dict() for m in meths}, "positives": int(C.label.sum())}
        md += ["## Task c: strong negative interaction (robust z of gA <= -2), per-lab AUROC", "", "| method | median AUROC [95% CI] | wins vs rule | median ΔAUROC vs rule |", "|---|---|---|---|"]
        md += [f"| {r['method']} | {r['auroc_median']:.3f} [{r['auroc_ci95'][0]:.3f}, {r['auroc_ci95'][1]:.3f}] | {r['wins_vs_rule']}/{r['auroc_n_labs']} | {r['median_dAUROC_vs_rule']:+.3f} |" for r in sorted(rows, key=lambda r: -r['auroc_median'])]
        md += [""]
    if "d" in tasks:
        from .repro import report
        rep, rmd = report(P); R["d"] = rep; md += [rmd, ""]
    txt = "\n".join(md); print(txt)
    if a.out: open(a.out, "w", encoding="utf-8").write(txt + "\n")
    if a.json: json.dump(R, open(a.json, "w", encoding="utf-8"), indent=1, default=float)

if __name__ == "__main__":
    main()
