"""Rank a batch of scorecards into a leaderboard."""

from __future__ import annotations


def rank_scorecards(cards: list[dict]) -> list[dict]:
    ranked = sorted(cards, key=lambda c: c.get("score", 0), reverse=True)
    return [
        {
            "rank": i,
            "skill_name": c.get("metadata", {}).get("skill_name"),
            "score": c.get("score"),
            "grade": c.get("grade"),
            "verdict": c.get("verdict"),
        }
        for i, c in enumerate(ranked, start=1)
    ]


def render_batch_table(ranked: list[dict]) -> str:
    lines = ["| Rank | Skill | Score | Grade | Verdict |", "|------|-------|-------|-------|---------|"]
    for r in ranked:
        lines.append(f"| {r['rank']} | {r['skill_name']} | {r['score']} | {r['grade']} | {r['verdict']} |")
    return "\n".join(lines) + "\n"
