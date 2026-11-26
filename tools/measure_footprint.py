"""Measure each baseline in a fresh, single-threaded Python process."""

import argparse
import json
import os
import platform
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "redistributable"
SPLITS = ("dev", "test", "fresh")
# Exact counts from the original run, recorded in LEADERBOARD.md.
REPORTED_PARAMS = {"NET_ATT": 844_801, "NET_MLP": 582_657}
THREADS = {
    name: "1" for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                           "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")
}


def measure(task, method, checkpoint):
    start = time.process_time()
    import numpy as np
    from opal_bench import baselines, embedding_heads, fewshot, metrics, opal_v1
    from opal_bench.data import calibration_mask, gene_split_rows, load_pairs

    params = 0
    if task == "fewshot":
        if method in fewshot.BUILTIN:
            predict = fewshot.BUILTIN[method]
            factory = lambda train: predict
            params = 6 if method == "FS_LIN5_lam" else 0
        elif method in embedding_heads.METHODS:
            factory = embedding_heads.METHODS[method]
            params = embedding_heads.PARAMS
        elif method == opal_v1.API_METHOD:
            factory = opal_v1.api_method(checkpoint)
        else:
            raise ValueError(f"Unknown few-shot method: {method}")
        for split in SPLITS:
            fewshot.run(split, {method: factory}, data=DATA, with_builtin=False)
    else:
        pairs = load_pairs(DATA)
        selection = (method,)
        target = pairs
        if task == "a":
            predictions, _ = baselines.task_a(pairs, selection)
        elif task == "a_fs20":
            if method in baselines.CALIBRATION_METHODS:
                predictions = baselines.task_a_fewshot(pairs, methods=selection)
                mask = ~predictions.is_cal
            else:
                predictions, _ = baselines.task_a(pairs, selection)
                mask = ~calibration_mask(pairs)
            target, predictions = pairs[mask], predictions[mask]
        elif task == "b":
            target = gene_split_rows(pairs)
            predictions = baselines.task_b(pairs, selection)
        else:
            prior = None if method == "RULE_ADD_MINUS_MIN" else baselines.task_a(pairs, selection)[0]
            predictions = baselines.task_c(pairs, prior, selection)
        if task == "c":
            metrics.per_lab_auroc(target.lab, target.strong_neg, predictions[method])
        else:
            metrics.per_lab_mse(target.lab, target.y, predictions[method])
    seconds = time.process_time() - start
    if sys.platform == "win32":
        import psutil

        peak_bytes = psutil.Process().memory_info().peak_wset
    else:
        import resource

        peak_bytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if sys.platform != "darwin":
            peak_bytes *= 1024
    # Count fitted state after reading the process high-water mark.
    if method in {"LIN5", "FS_LIN5"}:
        params = 6
    elif method == "ATLAS":
        labs = target.lab.unique()
        params = max(pairs.loc[pairs.lab != lab, "key"].nunique() for lab in labs)
    elif method == opal_v1.API_METHOD:
        with np.load(Path(checkpoint) / "tasks" / opal_v1.K562_TASK / "checkpoint.npz") as state:
            residuals = state["model__matrix_upper_bytes"].shape[1]
            coefficients = state["base__coefficient"].size
            params = residuals + coefficients + 1
    return {"params": params, "peak_ram_mib": round(peak_bytes / 1024**2, 2),
            "cpu_seconds": round(seconds, 3)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--opal-v1", default=os.environ.get("OPAL_V1_DIR"))
    parser.add_argument("--out", type=Path, help="Write the footprint JSON")
    parser.add_argument("--cpu", help="CPU model for the report metadata")
    parser.add_argument("--embedding-heads", action="store_true",
                        help="Also profile growth heads on the pinned embedding banks")
    parser.add_argument("--worker", nargs=2, metavar=("TASK", "METHOD"), help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(measure(*args.worker, args.opal_v1)))
        return
    if not args.out:
        parser.error("--out is required")

    import numpy as np
    import pandas as pd
    from opal_bench import baselines, embedding_heads, fewshot, leaderboard, opal_v1

    families = {
        "a": baselines.LOLO_METHODS,
        "a_fs20": (*baselines.LOLO_METHODS, *baselines.CALIBRATION_METHODS),
        "b": baselines.LOLO_METHODS,
        "c": ("RULE_ADD_MINUS_MIN", "LIN5", "BEST_RULE", "ATLAS"),
    }
    methods = {}
    table = pd.read_csv(ROOT / "leaderboard" / "rows.csv.gz", usecols=["model"])
    for name in sorted(set(table.model) - leaderboard.RETIRED_OPAL_METHODS):
        methods[name] = None
    if args.embedding_heads:
        methods.update(dict.fromkeys(embedding_heads.METHODS))
    if args.opal_v1:
        methods[opal_v1.API_METHOD] = None
    auxiliary = {task: {} for task in families}
    for task, names in {"fewshot": methods, **families}.items():
        for method in names:
            if task == "fewshot" and not (
                method in fewshot.BUILTIN
                or (args.embedding_heads and method in embedding_heads.METHODS)
                or (args.opal_v1 and method == opal_v1.API_METHOD)
            ):
                continue
            print(f"Measuring {task} {method}", file=sys.stderr, flush=True)
            child = [sys.executable, __file__, "--worker", task, method]
            if args.opal_v1:
                child += ["--opal-v1", args.opal_v1]
            output = subprocess.check_output(child, cwd=ROOT, env={**os.environ, **THREADS})
            (methods if task == "fewshot" else auxiliary[task])[method] = json.loads(output)
    report = {
        "environment": {
            "os": platform.platform(),
            "cpu": args.cpu or platform.processor(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "blas_threads": 1,
        },
        "methods": methods,
        "reported_params": REPORTED_PARAMS,
        "auxiliary": auxiliary,
    }
    args.out.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
