import batch


def _sc(name, score, grade, verdict):
    return {"score": score, "grade": grade, "verdict": verdict, "metadata": {"skill_name": name}}


def test_rank_scorecards_orders_by_score():
    cards = [_sc("a", 70, "C", "Revise"), _sc("b", 95, "A", "Ship"), _sc("c", 0, "F", "Reject")]
    ranked = batch.rank_scorecards(cards)
    assert [r["skill_name"] for r in ranked] == ["b", "a", "c"]
    assert ranked[0]["rank"] == 1 and ranked[-1]["rank"] == 3


def test_render_batch_table():
    ranked = batch.rank_scorecards([_sc("alpha", 88, "B", "Ship"), _sc("beta", 40, "F", "Reject")])
    md = batch.render_batch_table(ranked)
    assert "alpha" in md and "beta" in md
    assert "88" in md and "Reject" in md
