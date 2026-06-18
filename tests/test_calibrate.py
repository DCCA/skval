import calibrate


def test_spearman_perfect():
    assert calibrate.spearman([1, 2, 3, 4], [10, 20, 30, 40]) == 1.0
    assert calibrate.spearman([1, 2, 3, 4], [40, 30, 20, 10]) == -1.0


def test_evaluate_weights_correlation():
    # human score tracks D2 exactly
    examples = [
        {"dims": {"D2": 0.2, "D1": 0.9}, "human_score": 20},
        {"dims": {"D2": 0.5, "D1": 0.5}, "human_score": 50},
        {"dims": {"D2": 0.9, "D1": 0.1}, "human_score": 90},
    ]
    heavy_d2 = {"D2": 1.0, "D1": 0.0, "D3": 0.0, "D4": 0.0, "D5": 0.0}
    assert calibrate.evaluate_weights(examples, heavy_d2) > 0.99


def test_suggest_weights_finds_signal():
    examples = [
        {"dims": {"D2": v / 10, "D1": 1 - v / 10}, "human_score": v * 10}
        for v in (1, 3, 5, 7, 9)
    ]
    result = calibrate.suggest_weights(examples, samples=300, seed=7)
    assert abs(sum(result["weights"].values()) - 1.0) < 1e-6
    assert result["score"] > 0.9
    # D2 carries the signal, so it should earn the most weight
    assert result["weights"]["D2"] == max(result["weights"].values())
