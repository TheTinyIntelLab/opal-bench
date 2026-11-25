"""python -m opal_bench.prepare [--extra rebuilt_bench_pairs.csv.gz] [--extra-priors rebuilt_priors.csv.gz] [--test-units test_units.csv.gz]
Merge the 17 shipped labs with independently prepared compatible tables for the 5 restricted labs and locked-test cell lines.
Raw-source preprocessing isn't bundled. The scorer uses data/full when it exists; Git ignores that directory."""
import argparse, os, shutil, pandas as pd
from .data import ROOT
ALL = ["ABBVIE25", "BURGOLD25", "CHYMERA20", "DEDE20", "DIEHL21", "DU17", "HAN17", "HARLE25", "HORLBECK18", "IN4MER24", "ITO21", "KLINGBEIL24",
       "NAJM18", "PARRISH21", "SCHEMATIC25", "SHEN17", "SLC25", "SPIDR25", "TANG22", "THOMPSON21", "WONG16", "ZHAO18"]
def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--extra"); ap.add_argument("--extra-priors"); ap.add_argument("--test-units"); a = ap.parse_args(argv)
    red = os.path.join(ROOT, "data", "redistributable"); full = os.path.join(ROOT, "data", "full"); os.makedirs(full, exist_ok=True)
    P = pd.read_csv(os.path.join(red, "bench_pairs.csv.gz")); Q = pd.read_csv(os.path.join(red, "bench_priors.csv.gz"))
    if a.extra:
        E = pd.read_csv(a.extra); P = pd.concat([P, E[~E.lab.isin(set(P.lab))]], ignore_index=True)
    if a.extra_priors:
        Q = pd.concat([Q, pd.read_csv(a.extra_priors)]).drop_duplicates("key")
    P.sort_values(["lab", "key"], kind="stable").to_csv(os.path.join(full, "bench_pairs.csv.gz"), index=False); Q.to_csv(os.path.join(full, "bench_priors.csv.gz"), index=False)
    shutil.copy(a.test_units or os.path.join(red, "test_units.csv.gz"), os.path.join(full, "test_units.csv.gz"))
    have = sorted(set(P.lab)); print("labs present:", len(have), have); print("missing (not redistributed, see DATA_LICENSES.md):", [l for l in ALL if l not in have])
if __name__ == "__main__": main()
