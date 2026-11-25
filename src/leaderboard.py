"""Leaderboard tables from per-draw rows (unit, lab, k, draw, model, mse) with bootstrap rank intervals.
Ratio = geo-mean over labs of MSE/MSE_MID (units averaged within lab, draws within unit). Rank CI: 2,000 bootstrap
replicates, seed 0, over labs (dev) or labs then units within lab (test, fresh)."""
import numpy as np, pandas as pd

def tables(R, n_boot=2000, seed=0):
    rng = np.random.default_rng(seed)
    MIDm = R[R.model == "MID"][["unit", "k", "draw", "mse"]].rename(columns={"mse": "mid"})
    R = R.merge(MIDm, on=["unit", "k", "draw"]); R["lr"] = np.log(R.mse / R.mid); out = {}
    for k, Rk in R.groupby("k"):
        U = Rk.groupby(["model", "lab", "unit"]).lr.mean().unstack("model")
        labs = sorted(U.index.get_level_values("lab").unique())
        s = U.groupby(level="lab").mean().mean(); ranks = []
        for _ in range(n_boot):
            ls = rng.choice(labs, len(labs)); parts = []
            for l in ls:
                Ul = U.xs(l, level="lab", drop_level=False); parts.append(Ul.iloc[rng.integers(0, len(Ul), len(Ul))].mean())
            ranks.append(pd.DataFrame(parts).mean().rank())
        Rb = pd.DataFrame(ranks)
        T = pd.DataFrame({"ratio_vs_MID": np.exp(s), "rank": s.rank().astype(int), "rank_lo": Rb.quantile(0.025).round().astype(int),
                          "rank_hi": Rb.quantile(0.975).round().astype(int), "P_rank1": (Rb == 1).mean(),
                          "unit_wins_vs_MID": U.lt(0).sum().astype(int), "units": U.notna().sum().astype(int)}).sort_values(["rank", "ratio_vs_MID"])
        out[int(k)] = T
    return out

def markdown(tabs, notes=None):
    notes = notes or {}; md = []
    for k, T in tabs.items():
        md += [f"#### k = {k}", "", "| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |", "|---|---|---|---|---|"]
        for m, r in T.iterrows():
            md.append(f"| {m}{notes.get(m, '')} | {r.ratio_vs_MID:.3f} | {int(r['rank'])} [{int(r.rank_lo)}–{int(r.rank_hi)}] | {r.P_rank1:.3f} | {int(r.unit_wins_vs_MID)}/{int(r.units)} |")
        md.append("")
    return "\n".join(md)

def summary(tabs):
    return {str(k): {m: round(float(r.ratio_vs_MID), 6) for m, r in T.iterrows()} for k, T in tabs.items()}
