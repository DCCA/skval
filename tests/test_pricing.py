"""Tests for the per-model pricing table."""

import pytest

import pricing


def test_rate_known_models():
    assert pricing.rate("claude-opus-4-8") == (5.0, 25.0)
    assert pricing.rate("claude-sonnet-4-6") == (3.0, 15.0)
    assert pricing.rate("claude-haiku-4-5") == (1.0, 5.0)
    assert pricing.rate("claude-fable-5") == (10.0, 50.0)


def test_rate_unknown_raises_valueerror():
    with pytest.raises(ValueError, match="no price for model"):
        pricing.rate("gpt-4o")


def test_is_known():
    assert pricing.is_known("claude-opus-4-8")
    assert not pricing.is_known("nope")


def test_cost_usd_matches_rate():
    # 1M input + 1M output at opus rates = 5 + 25
    assert pricing.cost_usd("claude-opus-4-8", 1_000_000, 1_000_000) == pytest.approx(30.0)
    # output is 5x input on opus
    assert pricing.cost_usd("claude-opus-4-8", 0, 1_000_000) == pytest.approx(25.0)
    assert pricing.cost_usd("claude-haiku-4-5", 2_000_000, 0) == pytest.approx(2.0)
