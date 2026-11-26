"""Fixed growth heads on external human gene embeddings."""

from functools import lru_cache, partial
from hashlib import sha256
from pathlib import Path
import os

import numpy as np
import pandas as pd

from . import fewshot, tracks


FEATURE_BANKS = {
    "GenePT": "fee50b1732b1b0e3b8e5beae489b97897d657bfebd4d8d7b88c1d5115cd8bbc5",
    "ESM2": "3507a9ae0f105c29f2f32a966d94c5bf07809c4151fc3798688c9126ca46d1ba",
}
HUB_BANKS = {
    "Geneformer-v2-ridge": (
        "geneformer_v2_316m",
        "acebb7630a1f959f0af10257d90c2f5494d0ca73a1ef9ebb22b4335d8eb862ea",
        "b607f68fe8037192ac08be8b369d06efd517a4f867909b5d202518a7d320548b",
    ),
    "scGPT-human-ridge": (
        "scgpt_whole_human",
        "b58655dbdf19e3d626ac4d9b8521c6abea17bbb2563a7ea3980ccaee48abb7d7",
        "08357c888fd3ed26e61818a5a78fcc1d89d66010154726341faefe7ddf651846",
    ),
    "scGPT-pancancer-ridge": (
        "scgpt_pancancer",
        "436195c4c09e8d343b651ea4e34f7c307a7de0e9180d6c11bc6119510afa19bc",
        "3a434f4b9a9796905d192fa63bf7e983df80d9ef33325cdc978fc11e1d31b355",
    ),
    "GeneCompass-ridge": (
        "genecompass_base_gene_token",
        "c78979a23169388368fa5bff24cc610f060bd8f773333c895a95a7acca1ae539",
        "45edd21c2abc6024257dd70e47ec40658cb47e4a4ec9ca5e3be514e57acf164f",
    ),
    "UCE-33L-ridge": (
        "uce_33l",
        "5bcc1aeb558180f3d93f02baf1e928b68989bc9e3e5c52fe0d40dd7323af8e65",
        "5eadf023b312e28aff7a5c4a2227252b703c463d9c0aeca441e65074aba60208",
    ),
    "scFoundation-ridge": (
        "scfoundation_gene_pos",
        "1123556a3914ec629d879cb584851ce77ce601585ed9380d535597d50d06ccc1",
        "94bf44718249ff8e6dd444f90bfb8a6f61863f3602fe83ff9839a4e96b0c3b17",
    ),
    "scPRINT-ridge": (
        "scprint_medium_v1_5_gene",
        "9f8d8ac5a1e4aa04c90ad04e097610db88508bc90f4c2d4fbd437e3828dbb63e",
        "554e14c76bc61a32e6e3bb9533e5f52aab01b78f8e768db6710c48694a3d56eb",
    ),
}
SYMBOLS_HASH = "399e27fc3b5844823adc5860f217abf0de0001ec57b079fef0b9bfd867c00a7f"
RIDGE = 1.0
DIMENSIONS = 16
PARAMS = 6 + 2 * DIMENSIONS + 1


def _verify(path, expected):
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != expected:
        raise ValueError(f"Unexpected SHA-256 for {path}")


@lru_cache(maxsize=1)
def _hub_symbols(root):
    path = root / "master_gene_table.csv"
    _verify(path, SYMBOLS_HASH)
    table = pd.read_csv(path, usecols=["ensembl_gene_id", "gene_symbol"], dtype=str)
    table = table.dropna().drop_duplicates("gene_symbol", keep=False)
    return table.set_index("ensembl_gene_id").gene_symbol


@lru_cache(maxsize=len(HUB_BANKS))
def _hub_bank(root, name):
    folder, genes_hash, embeddings_hash = HUB_BANKS[name]
    genes_file, embeddings_file = (root / "embeddings" / folder / file
                                   for file in ("genes.tsv", "embeddings.npz"))
    _verify(genes_file, genes_hash)
    _verify(embeddings_file, embeddings_hash)
    ids = pd.read_csv(genes_file, sep="\t", usecols=["ensembl_gene_id"], dtype=str).ensembl_gene_id
    symbols = ids.map(_hub_symbols(root))
    with np.load(embeddings_file) as data:
        matrix = data["embeddings"]
    rng = np.random.default_rng(95831)
    projection = rng.standard_normal((matrix.shape[1], DIMENSIONS), dtype=np.float32)
    reduced = matrix @ projection
    reduced -= reduced.mean(axis=0)
    reduced /= reduced.std(axis=0)
    mapped = symbols.notna().to_numpy()
    return pd.Index(symbols[mapped]), reduced[mapped]


def _presage_bank(name):
    file = Path(os.environ["OPAL_BENCH_EMBEDDINGS"]) / f"semantic-{name}" / "embedding.npz"
    _verify(file, FEATURE_BANKS[name])
    with np.load(file) as data:
        return pd.Index(data["genes"]), data["embedding"]


def _factory(name, train):
    if name in HUB_BANKS:
        gene_index, bank = _hub_bank(Path(os.environ["OPAL_BENCH_GENE_HUB"]), name)
    else:
        gene_index, bank = _presage_bank(name)
    embeddings = np.vstack((bank, np.zeros((1, DIMENSIONS), dtype=np.float32)))

    def features(rows):
        ia = gene_index.get_indexer(rows.a)
        ib = gene_index.get_indexer(rows.b)
        a, b = embeddings[ia], embeddings[ib]
        return np.column_stack((fewshot.X6(rows), a + b, a * b,
                                (ia >= 0).astype(int) + (ib >= 0)))

    labs = train.groupby("lab", sort=True).size()
    eligible = labs[(labs >= max(fewshot.SPLITS["dev"]["ks"]) + 9) & (labs < len(train))]
    if eligible.empty:
        raise ValueError("The embedding head needs at least two training screens and a calibration reference")
    source = eligible.idxmax()
    reference = train[train.lab == source]
    fit = train[train.lab != source]
    weights = fewshot.ridge(features(fit), (fit.y - fit.MID).to_numpy(), RIDGE)
    reference_radii = {}

    def point(cal, ev):
        adjustment = weights
        if len(cal):
            x = features(cal)
            residual = (cal.y - cal.MID).to_numpy() - x @ weights
            adjustment = weights + fewshot.ridge(x, residual, RIDGE)
        return ev.MID.to_numpy() + features(ev) @ adjustment

    def predict(cal, ev):
        prediction = point(cal, ev)
        k = len(cal)
        unit = ev.unit.iat[0]
        interval = tracks.residual_interval(
            point, cal, ev, prediction, refit=True,
            seed=fewshot.mseed("embedding-interval", name, unit, k, *cal.key),
        )
        if isinstance(interval, fewshot.Prediction):
            return interval
        if k not in reference_radii:
            reference_radii[k] = tracks.training_interval_radius(
                point, reference, k, fewshot.mseed("embedding-reference", source, k)
            )
        radius = reference_radii[k]
        return fewshot.Prediction(prediction, prediction - radius, prediction + radius, "training_screen")

    return predict


METHODS = {
    "GenePT-ridge": partial(_factory, "GenePT"),
    "ESM2-ridge": partial(_factory, "ESM2"),
    **{name: partial(_factory, name) for name in HUB_BANKS},
}
