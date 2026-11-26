"""Draw the README figures from published benchmark rows: python tools/plot_readme.py.

Install matplotlib alongside the benchmark dependencies. This script reads recorded scores; it doesn't fit models.
"""
from pathlib import Path
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
import pandas as pd
from opal_bench.leaderboard import RETIRED_OPAL_METHODS
from opal_bench.opal_v1 import API_METHOD

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images"
INK, MUTED, GRID = "#292520", "#605a52", "#e6e1da"
TEAL, GOLD, STONE = "#397c82", "#d7a550", "#b5b0a9"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9,
    "text.color": INK, "axes.labelcolor": MUTED, "axes.edgecolor": GRID,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False,
    "axes.spines.right": False, "svg.hashsalt": "Opal-Bench",
    "svg.fonttype": "none", "figure.facecolor": "white", "axes.facecolor": "white",
})


def save(fig, name):
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight", metadata={"Date": None})
    plt.close(fig)


def overview():
    fig, ax = plt.subplots(figsize=(12, 4.1))
    ax.set(xlim=(0, 12), ylim=(0, 4.1))
    ax.axis("off")
    ax.text(0, 3.85, "Opal-Bench: predict pairs in a lab you have never seen", fontsize=16, weight="bold")
    ax.text(0, 3.47, "Same calibration pairs. Same held-out pairs. One lab-balanced score.", color=MUTED, fontsize=11)
    boxes = [
        (0.05, 1.85, 2.6, 0.95, "Other labs", "Allowed training pairs", "#faf8f4"),
        (0.05, 0.45, 2.6, 0.95, "Target lab", "Singles + k measured pairs", "#faf8f4"),
        (3.65, 1.10, 2.5, 1.15, "Your method", "Fit / calibrate / predict", "#faf8f4"),
        (7.10, 1.10, 2.5, 1.15, "Unmeasured pairs", "Calibration pairs excluded", "#faf8f4"),
    ]
    for x, y, w, h, title, desc, color in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.10", facecolor=color, edgecolor="#a6a098", linewidth=0.8))
        ax.text(x+w/2, y+h*0.62, title, ha="center", va="center", fontsize=12, weight="bold")
        ax.text(x+w/2, y+h*0.30, desc, ha="center", va="center", fontsize=9, color=MUTED)
    for a, b in [((2.73, 2.30), (3.58, 1.92)), ((2.73, 0.92), (3.58, 1.40)), ((6.25, 1.67), (7.00, 1.67)), ((9.70, 1.67), (10.25, 1.67))]:
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=13, color=MUTED, linewidth=1.3))
    ax.text(11.08, 1.95, "MSE / MID", ha="center", fontsize=12, weight="bold", color=TEAL)
    ax.text(11.08, 1.52, "Geometric mean", ha="center", fontsize=9, color=MUTED)
    ax.text(11.08, 1.23, "over labs", ha="center", fontsize=9, color=MUTED)
    ax.text(3.68, 0.50, "k = 0, 10, 20, 50", fontsize=10, color=TEAL)
    ax.text(3.68, 0.16, "Fresh screen: k = 0, 5, 20", fontsize=9, color=MUTED)
    save(fig, "benchmark_overview")


def budget_curves(ratios):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.4), gridspec_kw={"wspace": 0.28})
    fig.subplots_adjust(top=0.74, bottom=0.19)
    fig.suptitle("A few measured pairs change the comparison", x=0.08, y=1.01, ha="left", fontsize=16, weight="bold")
    series = [("FS_LIN5_lam", "Six-coefficient ridge", TEAL, "o"), (API_METHOD, "Opal K562 API", GOLD, "s")]
    for ax, split, title, ks in zip(axes, ("test", "fresh"), ("Shipped locked test · 1 cell line", "Fresh SHEN26 · 2 cell lines"), ([0, 10, 20, 50], [0, 5, 20])):
        ax.set_title(title, loc="left", fontsize=11, pad=16)
        ax.axhline(1, color=INK, linewidth=1, linestyle=(0, (4, 3)))
        ax.text(0.98, 1.025, "MID = 1", transform=ax.get_yaxis_transform(), ha="right", fontsize=9, color=MUTED)
        for method, label, color, marker in series:
            values = ratios[(ratios.split == split) & (ratios.model == method)].sort_values("k")
            ax.plot(values.k, values.ratio, marker=marker, markersize=5, color=color, linewidth=2, label=label)
        ax.set(xticks=ks, xlabel="Measured target pairs (k)", ylabel="MSE / MID · lower is better", ylim=(0.05, 1.15) if split == "test" else (0.85, 1.48))
        ax.grid(axis="y", color=GRID, linewidth=0.7)
        ax.set_axisbelow(True)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper left", bbox_to_anchor=(0.075, 0.93), ncol=3, frameon=False, fontsize=10)
    fig.text(0.08, 0.025, "Shipped-data point estimates. The ridge requires calibration pairs.", fontsize=9, color=MUTED)
    save(fig, "label_budget")


def locked_leaderboard(ratios, expected):
    table = ratios[(ratios.split == "test") & (ratios.k == 20)].sort_values("ratio")
    fig, ax = plt.subplots(figsize=(12, 7.1))
    fig.subplots_adjust(left=0.23, right=0.79, top=0.84, bottom=0.13)
    fig.text(0.07, 0.96, "Locked test · 20 measured pairs", fontsize=16, weight="bold")
    fig.text(0.07, 0.905, f"{len(table)} displayed methods · 4 labs · 31 cell lines · lower is better", fontsize=11, color=MUTED)
    colors = [TEAL if m == "FS_LIN5_lam" else INK if m == "MID" else STONE for m in table.model]
    ax.barh(np.arange(len(table)), table.ratio, color=colors, height=0.63)
    ax.set(yticks=np.arange(len(table)), yticklabels=table.model, xlabel="MSE / MID", xlim=(0, 1.86))
    ax.invert_yaxis()
    ax.axvline(1, color=MUTED, linewidth=1, linestyle=(0, (4, 3)))
    ax.set_xticks([0, 0.5, 1, 1.5])
    ax.grid(axis="x", color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines[["left", "bottom"]].set_visible(False)
    ax.tick_params(axis="both", length=0, pad=8)
    for y, row in enumerate(table.itertuples()):
        e = expected["test"]["20"][row.model]
        ax.text(row.ratio+0.025, y, f"{row.ratio:.3f}", va="center", fontsize=9)
        ax.text(1.08, y, f"{e['rank']} [{e['rank_lo']}–{e['rank_hi']}]", transform=ax.get_yaxis_transform(), va="center", fontsize=9, color=MUTED)
    ax.text(1.08, 1.035, "Rank [95% CI]", transform=ax.transAxes, fontsize=9, color=MUTED)
    fig.text(0.07, 0.025, "Published ranks and intervals use the original comparison and 2,000 bootstrap replicates.", fontsize=9, color=MUTED)
    save(fig, "locked_test")


def coverage(pairs):
    counts = pairs.groupby("lab").size().sort_values()
    fig, ax = plt.subplots(figsize=(12, 6.1))
    fig.subplots_adjust(left=0.17, right=0.86, top=0.81, bottom=0.14)
    fig.text(0.065, 0.95, "Shipped data · 17 labs / 334,669 pairs", fontsize=16, weight="bold")
    fig.text(0.065, 0.89, "Lab sizes vary. The main metric gives every lab equal weight.", color=MUTED, fontsize=11)
    ax.barh(counts.index, counts.values, color=[TEAL if n == "BURGOLD25" else STONE for n in counts.index], height=0.63)
    for y, value in enumerate(counts):
        ax.text(value+1600, y, f"{value:,}", va="center", color=MUTED, fontsize=8.5)
    ax.set(xlabel="Lab-level gene pairs", xlim=(0, 174000), xticks=[0, 50000, 100000, 150000], xticklabels=["0", "50k", "100k", "150k"])
    ax.tick_params(axis="both", length=0, labelsize=9)
    ax.grid(axis="x", color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines[["left", "bottom"]].set_visible(False)
    fig.text(0.065, 0.025, "BURGOLD25 is the shipped locked-test lab. Five restricted labs are excluded; fresh SHEN26 ships separately (1,530 rows).", color=MUTED, fontsize=9)
    save(fig, "data_coverage")


def main():
    OUT.mkdir(exist_ok=True)
    rows_path = ROOT / "leaderboard/rows.csv.gz"
    shipped_path = ROOT / "leaderboard/shipped-fewshot.json"
    pairs_path = ROOT / "data/redistributable/bench_pairs.csv.gz"
    rows = pd.read_csv(rows_path)
    rows = rows[~rows.model.isin(RETIRED_OPAL_METHODS)]
    keys = ["split", "unit", "k", "draw"]
    mid = rows[rows.model == "MID"][keys + ["mse"]].rename(columns={"mse": "mid"})
    joined = rows.merge(mid, on=keys, validate="many_to_one")
    joined["lr"] = np.log(joined.mse / joined.mid)
    unit = joined.groupby(["split", "k", "model", "lab", "unit"]).lr.mean()
    lab = unit.groupby(["split", "k", "model", "lab"]).mean()
    ratios = np.exp(lab.groupby(["split", "k", "model"]).mean()).rename("ratio").reset_index()
    expected = json.loads((ROOT / "tests/expected/leaderboard.json").read_text(encoding="utf-8"))
    for row in ratios.itertuples():
        assert abs(row.ratio - expected[row.split][str(row.k)][row.model]["ratio"]) < 1e-6
    shipped = json.loads(shipped_path.read_text(encoding="utf-8"))
    budget_ratios = pd.DataFrame([
        {"split": split, "k": int(k), "model": method, "ratio": ratio}
        for split in ("test", "fresh") for k, methods in shipped[split].items()
        for method, ratio in methods.items() if method in ("FS_LIN5_lam", API_METHOD)
    ])
    pairs = pd.read_csv(pairs_path)
    assert len(pairs) == 334669 and pairs.lab.nunique() == 17
    overview()
    budget_curves(budget_ratios)
    locked_leaderboard(ratios, expected)
    coverage(pairs)
    provenance = {
        "sources": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (rows_path, shipped_path, pairs_path, ROOT / "tests/expected/leaderboard.json")},
        "metric": "exp(mean_labs(mean_units(mean_draws(log(MSE / MSE_MID)))))",
        "ratios": ratios.to_dict(orient="records"),
        "budget_figure_ratios": budget_ratios.to_dict(orient="records"),
        "shipped_pairs_by_lab": pairs.groupby("lab").size().to_dict(),
        "scope": "Budget curves use shipped-data scores. The locked-test plot shows published historical ranks for the displayed methods.",
    }
    (OUT / "figure_data.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print("Built four SVG figures and verified the historical ratios.")


if __name__ == "__main__":
    main()
