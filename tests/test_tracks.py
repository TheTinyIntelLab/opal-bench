from hashlib import sha256
import sys
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from opal_bench import embedding_heads, fewshot, opal_v1, tracks


def test_unseen_gene_membership_includes_both_endpoints_and_calibration():
    cal = pd.DataFrame({"a": ["seen_b"], "b": ["cal"]})
    ev = pd.DataFrame({
        "a": ["seen_a", "cal", "unknown_a"],
        "b": ["seen_b", "unknown_b", "unknown_b"],
    })
    assert tracks.unseen_gene_counts({"seen_a", "seen_b"}, cal, ev).tolist() == [0, 1, 2]


def test_pretrained_roster_adds_seen_genes_and_excludes_its_source_lab(monkeypatch):
    screen = fewshot._basic(pd.DataFrame({
        "lab": "target", "unit": "target", "key": ["x", "y"],
        "a": ["trained", "novel"], "b": ["other", "other"],
        "sa": 0.0, "sb": 0.0, "y": 1.0,
    }))
    monkeypatch.setattr(fewshot, "units", lambda *_: [
        (lab, lab, screen, screen.iloc[:0], None) for lab in ("source", "target")
    ])
    monkeypatch.setattr(fewshot, "draws", lambda *_: [(0, 0, np.zeros(2, dtype=bool))])
    methods = {name: (lambda train: fewshot.BUILTIN["MID"]) for name in ("base", "pretrained")}
    rows = tracks.run("dev", methods, None, unseen_pretraining={
        "pretrained": (frozenset({"trained"}), "source")
    })
    [source, target] = rows[rows.method == "pretrained"].itertuples()
    assert source.mse == target.mse == 1.0
    assert pd.isna(source.any_gene_pairs)
    assert (target.one_gene_pairs, target.both_gene_pairs) == (1, 1)
    assert rows.loc[rows.method == "base", "both_gene_pairs"].tolist() == [2, 2]


def test_top_five_percent_rounds_up_and_breaks_ties_by_pair_key():
    keys = np.array([f"{i:02}" for i in reversed(range(21))])
    synergy, buffering = tracks.hit_sets(np.zeros(21), keys)
    assert keys[synergy].tolist() == ["00", "01"]
    assert keys[buffering].tolist() == ["19", "20"]


def test_track_scores_and_interval_validation(monkeypatch):
    screen = fewshot._basic(pd.DataFrame({
        "lab": "L", "unit": "U", "key": ["x", "y", "z"],
        "a": ["A", "A", "B"], "b": ["B", "C", "C"],
        "sa": 0.0, "sb": 0.0, "y": [-1.0, 0.0, 1.0],
        "gA": [-1.0, 0.0, 1.0], "z_gA": [-2.0, 0.0, 2.0], "strong_neg": [1, 0, 0],
    }))
    monkeypatch.setattr(fewshot, "units", lambda *_: [("U", "L", screen, screen.iloc[:0], None)])
    monkeypatch.setattr(fewshot, "draws", lambda *_: [(1, 0, np.array([False, True, False]))])
    point = np.array([-1.0, 1.0])

    def factory(train):
        def predict(cal, ev):
            assert cal.y.tolist() == [0.0]
            assert set(cal) - {"y"} == set(ev)
            assert {"gA", "z_gA", "strong_neg", "y"}.isdisjoint(ev)
            return fewshot.Prediction(point, point - 0.25, point + 0.25)
        return predict

    [row] = tracks.summarize(tracks.run("test", {"interval": factory}, None))
    assert row["synergy_precision"] == row["synergy_recall"] == 1.0
    assert row["buffering_precision"] == row["buffering_recall"] == 1.0
    assert row["one_gene_pairs"] == 2 and row["one_gene_mse"] == 0.0
    assert "both_gene_mse" not in row
    assert row["interval_coverage"] == 1.0 and row["interval_width"] == 0.5

    main = fewshot.run("test", {"interval": factory}, with_builtin=False)
    assert main.mse.tolist() == [0.0]
    with pytest.raises(ValueError, match="one finite value per evaluation pair"):
        fewshot.run("test", {"bad": lambda train: lambda cal, ev: 0}, with_builtin=False)

    bad = lambda train: lambda cal, ev: fewshot.Prediction(point, point + 1, point)
    with pytest.raises(ValueError, match="ordered bounds"):
        tracks.run("test", {"bad": bad}, None)


def test_residual_intervals_preserve_point_scores_and_hold_out_calibration_pairs():
    cal = pd.DataFrame({key: [""] * 20 for key in fewshot.PREDICTOR_COLUMNS})
    cal["y"] = np.arange(20, dtype=float)
    ev = cal.iloc[:2].assign(key=["eval_a", "eval_b"])
    point = np.full(len(ev), 5.0)

    def predict(fit, query):
        assert "y" not in query or query is ev
        if query is not ev:
            assert set(fit.index).isdisjoint(query.index)
        return np.full(len(query), float(len(fit)))

    fixed = tracks.residual_interval(predict, cal, ev, point, False, 42)
    assert fixed.point is point
    assert fixed.lower.tolist() == [-13.0, -13.0]
    assert fixed.upper.tolist() == [23.0, 23.0]
    adaptive = tracks.residual_interval(predict, cal, ev, point, True, 42)
    assert adaptive.point is point
    assert np.all((adaptive.lower + adaptive.upper) / 2 == 10)
    assert tracks.residual_interval(predict, cal.iloc[:5], ev, point, False, 42) is point
    assert tracks.residual_interval(predict, cal.iloc[:10], ev, point, True, 42) is point


def test_training_intervals_use_only_an_allowed_reference_screen(monkeypatch):
    screen = fewshot._basic(pd.DataFrame({
        "lab": "target", "unit": "target", "key": ["x"], "a": ["A"], "b": ["B"],
        "sa": 0.0, "sb": 0.0, "y": 2.0,
    }))
    source = pd.concat([
        screen.loc[screen.index.repeat(12)].assign(lab="checkpoint", unit="checkpoint", y=100.0),
        screen.loc[screen.index.repeat(9)].assign(lab="allowed", unit="allowed", y=3.0),
    ], ignore_index=True)
    monkeypatch.setattr(fewshot, "units", lambda *_: [("target", "target", screen, source, None)])
    monkeypatch.setattr(fewshot, "draws", lambda *_: [(0, 0, np.zeros(1, dtype=bool))])
    result = tracks.run(
        "test", {"fixed": lambda train: fewshot.BUILTIN["MID"]}, None,
        interval_methods={"fixed": False},
        unseen_pretraining={"fixed": (frozenset(), "checkpoint")},
        training_intervals=True,
    )
    [row] = tracks.summarize(result)
    assert row["mse"] == 4.0
    assert row["interval_coverage"] == 1.0
    assert row["interval_width"] == 6.0
    assert row["interval_source"] == "training_screen"


def test_historical_roster_lists_missing_models_without_metrics():
    scores = [{"k": 20, "method": "MID", "mse": 0.3}]
    history = pd.DataFrame({"k": [0, 20, 20, 20], "model": ["MID", "MID", "NET_ATT", "NET_ATT"]})
    assert tracks.include_historical_methods(scores, history, {20}) == [
        scores[0], {"k": 20, "method": "NET_ATT"},
    ]


def test_embedding_head_is_symmetric_and_keeps_reference_labels_out_of_point_fit(tmp_path, monkeypatch):
    bank = tmp_path / "semantic-GenePT" / "embedding.npz"
    bank.parent.mkdir()
    np.savez(bank, genes=["A", "B"], embedding=np.arange(32, dtype=np.float32).reshape(2, 16) / 32)
    monkeypatch.setenv("OPAL_BENCH_EMBEDDINGS", str(tmp_path))
    monkeypatch.setitem(embedding_heads.FEATURE_BANKS, "GenePT", sha256(bank.read_bytes()).hexdigest())
    train = fewshot._basic(pd.DataFrame({
        "lab": ["reference"] * 60 + ["fit"] * 2,
        "unit": "reference", "key": [str(i) for i in range(62)],
        "a": "A", "b": "B", "sa": 0.25, "sb": 0.5, "y": 1.0,
    }))
    ev = train.iloc[:1].assign(unit="target").drop(columns="y")
    reversed_ev = ev.assign(a=ev.b, b=ev.a, sa=ev.sb, sb=ev.sa)
    changed = train.assign(y=train.y.where(train.lab == "fit", 10.0))
    factory = embedding_heads.METHODS["GenePT-ridge"]
    original = factory(train)(train.iloc[:0], ev)
    comparison = factory(changed)(changed.iloc[:0], reversed_ev)
    assert original.interval_source == comparison.interval_source == "training_screen"
    np.testing.assert_array_equal(original.point, comparison.point)
    assert comparison.upper.item() - comparison.lower.item() > original.upper.item() - original.lower.item()


def test_hub_embedding_banks_follow_their_gene_order(tmp_path, monkeypatch):
    master = tmp_path / "master_gene_table.csv"
    master.write_text("ensembl_gene_id,gene_symbol\nE1,A\nE2,B\nE3,C\nE4,C\n", encoding="utf-8")
    folder = tmp_path / "embeddings" / "test-model"
    folder.mkdir(parents=True)
    genes = folder / "genes.tsv"
    genes.write_text("ensembl_gene_id\nE2\nE3\nE1\n", encoding="utf-8")
    bank = folder / "embeddings.npz"
    matrix = np.array([[1, 2], [5, 4], [3, 9]], dtype=np.float32)
    np.savez(bank, embeddings=matrix)
    monkeypatch.setattr(embedding_heads, "SYMBOLS_HASH", sha256(master.read_bytes()).hexdigest())
    monkeypatch.setitem(embedding_heads.HUB_BANKS, "test-model", (
        "test-model", sha256(genes.read_bytes()).hexdigest(), sha256(bank.read_bytes()).hexdigest()
    ))
    symbols, projected = embedding_heads._hub_bank(tmp_path, "test-model")
    assert symbols.tolist() == ["B", "A"]
    direction = np.random.default_rng(95831).standard_normal((2, 16), dtype=np.float32)
    expected = matrix @ direction
    expected = (expected - expected.mean(axis=0)) / expected.std(axis=0)
    np.testing.assert_allclose(projected, expected[[0, 2]], rtol=1e-6, atol=1e-7)


def test_official_api_keeps_its_source_screen_out_and_uses_mid_for_abstentions(monkeypatch):
    batches = []

    def predict(pairs):
        batches.append(pairs)
        return [{"value": -1.0}, {"value": None}]

    source = SimpleNamespace(stored_singles=lambda: np.array([-0.5, -0.5]), predict=predict)

    def load(root, expected_manifest_sha256):
        assert root == "bundle" and expected_manifest_sha256 == opal_v1.GROWTH_MANIFEST_SHA256
        return SimpleNamespace(model=lambda task: source if task == "horlbeck_K562" else None)

    monkeypatch.setitem(sys.modules, "opal.trained_growth", SimpleNamespace(
        TrainedGrowth=SimpleNamespace(load=load)
    ))
    frame = pd.DataFrame({"lab": "new", "a": ["A", "B"], "b": ["C", "D"], "MID": [-0.3, -0.4]})
    predictor = opal_v1.api_method("bundle")(None)
    np.testing.assert_array_equal(predictor(None, frame.assign(lab="HORLBECK18")), [-0.3, -0.4])
    assert not batches
    np.testing.assert_array_equal(predictor(None, frame), [-2.0, -0.4])
    np.testing.assert_array_equal(predictor(None, frame.assign(MID=-1.0)), [-2.0, -1.0])
    assert batches == [[("A", "C"), ("B", "D")]]
