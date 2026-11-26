"""Supplemental scores on the existing few-shot splits and draws."""

import numpy as np
import pandas as pd

from . import fewshot

REPORT_FIELDS = [
    ("mse", "MSE"), ("any_gene_mse", "unseen MSE"), ("one_gene_mse", "one unseen MSE"),
    ("both_gene_mse", "both unseen MSE"), ("synergy_precision", "synergy precision"),
    ("synergy_recall", "synergy recall"), ("buffering_precision", "buffering precision"),
    ("buffering_recall", "buffering recall"), ("interval_coverage", "90% coverage"),
    ("interval_width", "mean interval width"),
]


def unseen_gene_counts(training_genes, cal, ev):
    seen = training_genes.union(cal.a, cal.b)
    return (~ev.a.isin(seen)).to_numpy(dtype=int) + (~ev.b.isin(seen)).to_numpy(dtype=int)


def hit_sets(effect, keys):
    count = (len(effect) + 19) // 20
    order = np.lexsort((keys, effect))
    return order[:count], order[len(order) - count:]


def residual_interval(predictor, cal, ev, point, refit, seed):
    """Build a 90% interval from target calibration pairs unused in its fit."""
    if refit:
        order = np.random.default_rng(seed).permutation(len(cal))
        fit, holdout = cal.iloc[order[:len(cal) // 2]], cal.iloc[order[len(cal) // 2:]]
    else:
        fit, holdout = cal.iloc[:0], cal
    rank = (9 * (len(holdout) + 1) + 9) // 10
    if rank > len(holdout):
        return point
    actual = holdout.y.to_numpy()
    predicted = predictor(fit, fewshot.predictor_inputs(holdout))
    radius = np.partition(np.abs(actual - predicted), rank - 1)[rank - 1]
    center = predictor(fit, ev) if refit else point
    return fewshot.Prediction(point, center - radius, center + radius)


def training_interval_radius(predictor, reference, k, seed):
    """Calibrate on one allowed source screen at the target predictor's budget."""
    mask = np.zeros(len(reference), dtype=bool)
    mask[np.random.default_rng(seed).choice(len(reference), k, replace=False)] = True
    fit, holdout = reference[mask], reference[~mask]
    predicted = predictor(fewshot.predictor_inputs(fit, labeled=True), fewshot.predictor_inputs(holdout))
    residuals = np.abs(holdout.y.to_numpy() - predicted)
    rank = (9 * (len(residuals) + 1) + 9) // 10
    return np.partition(residuals, rank - 1)[rank - 1]


def run(split, methods, data, budgets=None, unseen_methods=None, interval_methods=None,
        unseen_pretraining=None, training_intervals=False):
    """Return per-draw scores. Only methods eligible for unseen genes get those columns."""
    records = []
    unseen_methods = set(methods) if unseen_methods is None else set(unseen_methods)
    interval_methods = {} if interval_methods is None else interval_methods
    unseen_pretraining = {} if unseen_pretraining is None else unseen_pretraining
    # Only built-ins and fixed-checkpoint Opal use this cache. Their predictors
    # do not fit on the split's training frame.
    training_radii = {}
    for unit, lab, screen, train, seed in fewshot.units(split, data):
        training_genes = frozenset(train.a).union(train.b) if unseen_methods else frozenset()
        rosters = dict.fromkeys(unseen_methods, training_genes)
        for method, (extra_genes, source_lab) in unseen_pretraining.items():
            if lab == source_lab:
                rosters.pop(method, None)
            elif method in rosters:
                rosters[method] = training_genes.union(extra_genes)
        unique_rosters = set(rosters.values())
        source_sizes = train.groupby("lab", sort=True).size() if training_intervals else None
        predict = {name: factory(train) for name, factory in methods.items()}
        for k, draw, mask in fewshot.draws(screen, split, seed):
            if (budgets is not None and k not in budgets) or mask.all():
                continue
            cal, ev = fewshot.predictor_inputs(screen[mask], labeled=True), screen[~mask]
            inputs = fewshot.predictor_inputs(ev)
            labels = ev.y.to_numpy()
            additive, keys = ev.ADD.to_numpy(), ev.key.to_numpy()
            actual_hits = hit_sets(labels - additive, keys)
            unseen_counts = {roster: unseen_gene_counts(roster, cal, ev) for roster in unique_rosters}
            for method, predictor in predict.items():
                result = predictor(cal, inputs)
                if result is None:
                    records.append(dict(unit=unit, lab=lab, k=k, draw=draw, method=method, scored=False))
                    continue
                interval_source = None
                if method in interval_methods:
                    refit = interval_methods[method]
                    result = residual_interval(predictor, cal, inputs, result, refit,
                                               fewshot.mseed("interval", split, unit, k, draw))
                    if training_intervals and not isinstance(result, fewshot.Prediction):
                        source_k = k if refit else 0
                        candidates = source_sizes[source_sizes >= source_k + 9]
                        if method in unseen_pretraining:
                            candidates = candidates.drop(unseen_pretraining[method][1], errors="ignore")
                        if candidates.empty:
                            raise ValueError(f"No allowed training screen can calibrate {method} at k={k} for {unit}")
                        source = candidates.idxmax()
                        cache_key = method, source, source_k
                        if cache_key not in training_radii:
                            reference = train[train.lab == source]
                            training_radii[cache_key] = training_interval_radius(
                                predictor, reference, source_k, fewshot.mseed("training-interval", source, source_k)
                            )
                        radius = training_radii[cache_key]
                        result = fewshot.Prediction(result, result - radius, result + radius)
                        interval_source = "training_screen"
                interval = isinstance(result, fewshot.Prediction)
                point = fewshot.prediction_vector(result.point if interval else result, len(ev), f"{method} prediction")
                squared_error = (point - labels) ** 2
                row = dict(unit=unit, lab=lab, k=k, draw=draw, method=method, scored=True,
                           mse=float(squared_error.mean()))
                for tail, actual, predicted in zip(
                    ("synergy", "buffering"), actual_hits, hit_sets(point - additive, keys)
                ):
                    hits = np.intersect1d(actual, predicted, assume_unique=True).size
                    row[f"{tail}_precision"] = hits / len(predicted)
                    row[f"{tail}_recall"] = hits / len(actual)
                if method in rosters:
                    counts = unseen_counts[rosters[method]]
                    for cohort, eligible in (("one", counts == 1), ("both", counts == 2),
                                             ("any", counts > 0)):
                        row[f"{cohort}_gene_pairs"] = int(eligible.sum())
                        if eligible.any():
                            row[f"{cohort}_gene_mse"] = float(squared_error[eligible].mean())
                if interval:
                    lower = fewshot.prediction_vector(result.lower, len(ev), f"{method} lower bound")
                    upper = fewshot.prediction_vector(result.upper, len(ev), f"{method} upper bound")
                    if (lower > upper).any() or not np.isfinite(upper - lower).all():
                        raise ValueError(f"{method} must return ordered bounds with finite widths")
                    row["interval_coverage"] = float(((lower <= labels) & (labels <= upper)).mean())
                    row["interval_width"] = float((upper - lower).mean())
                    if interval_source or result.interval_source:
                        row["interval_source"] = interval_source or result.interval_source
                records.append(row)
    return pd.DataFrame(records)


def summarize(records):
    if records.empty:
        return []
    rows = []
    for (k, method), group in records.groupby(["k", "method"]):
        if not group.scored.any():
            continue
        if not group.scored.all():
            raise ValueError(f"{method} must predict every draw in a budget or skip the entire budget")
        if "interval_coverage" in group:
            has_interval = group.interval_coverage.notna()
            if has_interval.any() and not has_interval.all():
                raise ValueError(f"{method} must return intervals for every draw in an interval budget")
        source = {}
        if "interval_source" in group:
            sources = group.interval_source.dropna()
            if not sources.empty:
                if len(sources) != len(group) or sources.nunique() != 1:
                    raise ValueError(f"{method} must use the same interval source for every draw in a budget")
                source["interval_source"] = sources.iat[0]
        metrics = group.drop(columns=["k", "method", "draw", "scored", "interval_source"],
                             errors="ignore")
        counts = [col for col in metrics if col.endswith("_pairs")]
        averages = (metrics.drop(columns=counts).groupby(["lab", "unit"]).mean()
                    .groupby(level="lab").mean().mean().dropna())
        rows.append({
            "k": int(k),
            "method": method,
            **averages.to_dict(),
            **source,
            **{col: int(metrics[col].sum()) for col in counts if metrics[col].notna().any()},
        })
    return rows


def include_historical_methods(rows, history, budgets):
    """Make missing scores explicit for methods previously entered at this budget."""
    scored = {(row["k"], row["method"]): row for row in rows}
    for k, method in history[["k", "model"]].drop_duplicates().itertuples(index=False, name=None):
        if budgets is None or k in budgets:
            scored.setdefault((k, method), {"k": k, "method": method})
    return [scored[key] for key in sorted(scored)]


def markdown(results):
    md = ["# Opal-Bench supplemental scores", ""]
    if any(row.get("interval_source") == "training_screen" for rows in results.values() for row in rows):
        md.extend(["† The interval radius came from an allowed training screen.", ""])
    for split, rows in results.items():
        md.extend([f"## {split}", ""])
        if not rows:
            md.extend(["No eligible scores.", ""])
        for budget in sorted({row["k"] for row in rows}):
            entries = [row for row in rows if row["k"] == budget]
            scored = [row for row in entries if "mse" in row]
            unavailable = [row["method"] for row in entries if "mse" not in row]
            md.extend([f"### Measured pairs, k = {budget}", ""])
            if scored:
                fields = [(key, label) for key, label in REPORT_FIELDS if any(key in row for row in scored)]
                md += ["| method | " + " | ".join(label for _, label in fields) + " |",
                       "|---|" + "---|" * len(fields)]
                for row in scored:
                    cells = []
                    for key, _ in fields:
                        cell = f"{row[key]:.4f}" if key in row else "—"
                        if key.startswith("interval_") and row.get("interval_source") == "training_screen":
                            cell += " †"
                        cells.append(cell)
                    md.append("| " + " | ".join([row["method"], *cells]) + " |")
                md.append("")
            if unavailable:
                models = ", ".join(f"`{method}`" for method in unavailable)
                md.extend([f"Historical few-shot scores only for {models}.", ""])
    return "\n".join(md)
