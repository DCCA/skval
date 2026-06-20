"""Deterministic analysis of a multi-turn executor transcript.

Interactive skills (booking, ordering, requirements-gathering) are supposed to
**ask before they act**. The multi-turn executor records a transcript of
``{"role": "user"|"assistant", "content": ...}`` turns; these helpers make
interaction expectations like "asks at least 2 clarifying questions before
delivering" objectively checkable by the grader.
"""

from __future__ import annotations


def _content(turn) -> str:
    if isinstance(turn, dict):
        return str(turn.get("content") or "")
    return str(turn or "")


def _role(turn) -> str:
    return turn.get("role", "") if isinstance(turn, dict) else ""


def is_question(text: str) -> bool:
    return "?" in (text or "")


def count_questions(turns, role: str = "assistant") -> int:
    """Number of turns by ``role`` that ask at least one question."""
    return sum(1 for t in turns if _role(t) == role and is_question(_content(t)))


def questions_before_delivery(turns, delivered_at: int | None = None) -> int:
    """Count assistant question-turns before the delivery turn.

    ``delivered_at`` is an index into ``turns``; if omitted, the last assistant turn
    is treated as the delivery (questions are counted strictly before it).
    """
    turns = list(turns)
    if delivered_at is None:
        assistant_idx = [i for i, t in enumerate(turns) if _role(t) == "assistant"]
        delivered_at = assistant_idx[-1] if assistant_idx else len(turns)
    return sum(
        1
        for i, t in enumerate(turns)
        if i < delivered_at and _role(t) == "assistant" and is_question(_content(t))
    )


def meets_min_questions(turns, n: int, delivered_at: int | None = None) -> bool:
    return questions_before_delivery(turns, delivered_at) >= n


def asked_about(turns, keywords) -> dict:
    """Which ``keywords`` appear in the assistant's questions (case-insensitive)."""
    asked = " ".join(
        _content(t).lower() for t in turns if _role(t) == "assistant" and is_question(_content(t))
    )
    return {k: k.lower() in asked for k in keywords}
