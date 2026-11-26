"""Official Opal v1 API adapter for the published K562 growth bundle."""

from pathlib import Path

import numpy as np

API_METHOD = "Opal-v1-API-K562"
K562_TASK = "horlbeck_K562"
K562_LAB = "HORLBECK18"
GROWTH_MANIFEST_SHA256 = "fa8490abe83e5a5d0d0f8456639d11df16a2a6ca3ed440fb40bfd74459488e72"


def training_genes(root):
    """Genes with at least one labeled training pair in the exported schema."""
    with np.load(Path(root) / "tasks" / K562_TASK / "schema.npz") as schema:
        return frozenset(schema["gene_names"][schema["train_degree"] > 0].tolist())


def api_method(root):
    """Use fixed K562 outputs for supported pairs and target MID otherwise."""
    from opal.trained_growth import TrainedGrowth

    model = TrainedGrowth.load(root, expected_manifest_sha256=GROWTH_MANIFEST_SHA256).model(K562_TASK)
    scale = max(-np.quantile(model.stored_singles(), 0.05), 0.1)
    values = {}

    def predict(cal, ev):
        point = ev.MID.to_numpy(copy=True)
        if ev.empty or ev.lab.iat[0] == K562_LAB:
            return point
        pairs = list(zip(ev.a, ev.b))
        missing = list(dict.fromkeys(pair for pair in pairs if pair not in values))
        if missing:
            response = model.predict(missing)
            values.update((pair, row["value"]) for pair, row in zip(missing, response, strict=True))
        raw = np.array([values[pair] for pair in pairs], dtype=float)
        return np.where(np.isnan(raw), point, raw / scale)

    return lambda train: predict
