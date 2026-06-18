import compare


def test_decide_pairwise_consistent_winner():
    # A wins regardless of presentation order -> A
    assert compare.decide_pairwise("A", "A") == "A"
    assert compare.decide_pairwise("B", "B") == "B"


def test_decide_pairwise_position_bias_is_tie():
    # judge picked the first-shown each time (A when A first, B when B first) -> tie
    assert compare.decide_pairwise("A", "B") == "tie"
    assert compare.decide_pairwise("tie", "A") == "tie"


def test_position_bias_detected():
    assert compare.position_bias_detected("A", "B") is True
    assert compare.position_bias_detected("A", "A") is False


def _sc(score, d2_mean, d2_se):
    return {
        "score": score,
        "verdict": "Ship" if score >= 80 else "Revise",
        "dimensions": {
            "D2": {"score": d2_mean, "pass_rate": {"mean": d2_mean, "std_error": d2_se}},
            "D1": {"score": 1.0},
        },
    }


def test_compare_scorecards_overall_and_dims():
    a = _sc(70, 0.6, 0.02)
    b = _sc(85, 0.9, 0.02)
    cmp = compare.compare_scorecards(a, b)
    assert cmp["overall_delta"] == 15
    assert cmp["dimensions"]["D2"]["delta"] == round(0.9 - 0.6, 4)
    assert cmp["dimensions"]["D2"]["significant"] is True
    assert cmp["verdict_change"] == "Revise -> Ship"


def test_compare_insignificant_dim():
    a = _sc(80, 0.80, 0.20)
    b = _sc(81, 0.82, 0.20)
    cmp = compare.compare_scorecards(a, b)
    # tiny D2 delta within the noise
    assert cmp["dimensions"]["D2"]["significant"] is False
