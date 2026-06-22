"""Per-model token pricing for the cost estimator (USD per 1M tokens).

Isolated so price drift is a one-file edit. Rates are sourced from the
`claude-api` model/pricing reference (cached 2026-06-04); update them here when
Anthropic changes pricing. The cost estimator multiplies these by projected
input/output token counts — it never makes a model call.
"""

from __future__ import annotations

# model_id -> (input_usd_per_mtok, output_usd_per_mtok)
PRICES: dict[str, tuple[float, float]] = {
    "claude-fable-5": (10.0, 50.0),
    "claude-mythos-5": (10.0, 50.0),
    "claude-opus-4-8": (5.0, 25.0),
    "claude-opus-4-7": (5.0, 25.0),
    "claude-opus-4-6": (5.0, 25.0),
    "claude-opus-4-5": (5.0, 25.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-sonnet-4-5": (3.0, 15.0),
    "claude-haiku-4-5": (1.0, 5.0),
}

PER_MTOK = 1_000_000


def rate(model: str) -> tuple[float, float]:
    """Return ``(input_usd_per_mtok, output_usd_per_mtok)`` for ``model``.

    Raises ``ValueError`` for an unknown model so callers can surface a clear
    message (and list it as a pricing gap) rather than silently costing it $0.
    """
    try:
        return PRICES[model]
    except KeyError:
        raise ValueError(
            f"no price for model {model!r}; add it to pricing.PRICES "
            f"(known: {', '.join(sorted(PRICES))})"
        ) from None


def cost_usd(model: str, input_tokens: float, output_tokens: float) -> float:
    """Dollar cost of ``input_tokens`` + ``output_tokens`` at ``model``'s rates."""
    in_rate, out_rate = rate(model)
    return (input_tokens * in_rate + output_tokens * out_rate) / PER_MTOK


def is_known(model: str) -> bool:
    return model in PRICES
