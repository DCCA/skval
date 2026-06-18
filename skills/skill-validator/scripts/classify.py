"""Classify a skill by the kind of evaluation it needs, and recommend tools.

skval handles several skill shapes, and each wants a different eval strategy:

- **task** — one-shot input → output (default).
- **file_transform** — acts on / produces files (pdf, xlsx, docx, …): needs fixtures
  and file-aware grading.
- **interactive** — must ask / confirm / gather before acting: needs the multi-turn
  loop + user-simulator and interaction expectations.
- **discipline** — shapes *how* you work (TDD, debugging, review): judge adherence +
  artifact quality; expect a small single-task lift.
- **reference** — provides facts / answers: Q&A evals graded against a reference.

This picks the most likely shape from the SKILL.md using transparent keyword signals
(weighted toward the frontmatter ``description``) so the eval-generator / executor can
route automatically. It is a *default* — the agent may override with its own judgment.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_SIGNALS = {
    "file_transform": [
        r"\.(pdf|xlsx?|docx?|pptx?|csv)\b", r"spreadsheet", r"workbook", r"presentation",
        r"slide deck", r"\bPDFs?\b", r"\bExcel\b", r"\bPowerPoint\b", r"Word document",
        r"extract (text|tables|data|images)", r"merge (pdf|file|document)",
        r"convert .*(to|into) (pdf|docx|xlsx|pptx)", r"fill (out|in)[^.]*form", r"\bOCR\b",
        r"watermark", r"create (a |an )?(document|deck|report|workbook|spreadsheet)",
    ],
    "interactive": [
        r"clarif", r"concierge", r"gather (the )?(details|requirements|information|preferences)",
        r"confirm[^.]*before", r"before (ordering|booking|proceeding|purchasing|placing|scheduling)",
        r"walk (the user |you )?through", r"place an order",
        r"book(ing)? (a|an|the|appointment|service)", r"refill", r"schedule (a|an|the)",
        r"ask[^.]*(clarifying|question|before|about the|the user)", r"step[- ]by[- ]step with",
    ],
    "discipline": [
        r"test[- ]driven", r"\bTDD\b", r"red[- ]green", r"failing test first", r"refactor",
        r"methodology", r"systematic", r"code review", r"before (completing|finishing|marking)",
    ],
    "reference": [
        r"reference (knowledge|guide|for)", r"knowledge (base|about|to answer)",
        r"answer questions about", r"facts about", r"information about", r"guide to",
        r"documentation for", r"look up",
    ],
}
# Tie-break order (most specialized first); "task" is the fallback.
_PRIORITY = ["interactive", "file_transform", "discipline", "reference", "task"]

_FILE_LIBS = ("openpyxl", "python-docx", "docx", "pptx", "pypdf", "PyPDF2", "pdfplumber", "fitz", "pandas")


def _matches(text: str, patterns: list[str]) -> list[str]:
    return [p for p in patterns if re.search(p, text, re.I)]


def classify_skill(skill_md_text: str, skill_dir=None) -> dict:
    text = skill_md_text or ""
    m = re.search(r"description:\s*(.+)", text)
    desc = m.group(1) if m else ""

    scores: dict[str, int] = {}
    signals: dict[str, list[str]] = {}
    for typ, pats in _SIGNALS.items():
        body_hits = _matches(text, pats)
        desc_hits = _matches(desc, pats)  # description counts double
        signals[typ] = sorted(set(body_hits) | set(desc_hits))
        scores[typ] = len(body_hits) + len(desc_hits)

    # Bundled file libraries are a strong file_transform signal.
    if skill_dir:
        blob = ""
        for py in Path(skill_dir).rglob("*.py"):
            try:
                blob += py.read_text(errors="replace")
            except OSError:
                continue
        if any(lib in blob for lib in _FILE_LIBS):
            scores["file_transform"] += 2
            signals["file_transform"] = sorted(set(signals["file_transform"]) | {"bundled file library"})

    top = max(_SIGNALS, key=lambda t: (scores[t], -_PRIORITY.index(t)))
    if scores[top] == 0:
        top = "task"
    also = [t for t in _PRIORITY if t != top and scores.get(t, 0) > 0]
    return {"type": top, "scores": scores, "signals": signals, "also": also}


_STRATEGY = {
    "task": {"executor": "single_turn", "fixtures": False,
             "grading": "output correctness vs expected_output", "agents": ["eval-generator", "executor", "grader"]},
    "file_transform": {"executor": "single_turn", "fixtures": True,
                       "grading": "open & evaluate output files (recalc formulas)",
                       "agents": ["eval-generator", "executor", "grader"]},
    "interactive": {"executor": "multi_turn", "fixtures": False,
                    "grading": "interaction expectations via conversation.py + final deliverable",
                    "agents": ["eval-generator", "user-simulator", "executor", "grader"]},
    "discipline": {"executor": "scenario", "fixtures": False,
                   "grading": "process adherence + artifact quality (D4); expect small task lift",
                   "agents": ["eval-generator", "executor", "grader", "artifact-judge"]},
    "reference": {"executor": "single_turn", "fixtures": False,
                  "grading": "answer accuracy vs reference (expected_output)",
                  "agents": ["eval-generator", "executor", "grader"]},
}


def recommend_strategy(skill_type: str) -> dict:
    return _STRATEGY.get(skill_type, _STRATEGY["task"])


if __name__ == "__main__":
    d = Path(sys.argv[1])
    skill_md = d / "SKILL.md" if d.is_dir() else d
    res = classify_skill(skill_md.read_text(), skill_dir=skill_md.parent)
    strat = recommend_strategy(res["type"])
    print(f"type: {res['type']}" + (f"  (also: {', '.join(res['also'])})" if res["also"] else ""))
    print(f"scores: {res['scores']}")
    print(f"strategy: executor={strat['executor']} fixtures={strat['fixtures']}")
    print(f"          grading: {strat['grading']}")
    print(f"          agents: {', '.join(strat['agents'])}")
