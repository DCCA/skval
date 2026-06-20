"""Lenient JSON loading for agent-written artifacts.

Subagents and ``claude -p`` reliably wrap JSON in ```` ```json ```` fences or a line
of prose ("Here is the result:"). The consumers read those files, so a strict
``json.loads`` silently drops a run or skips a whole dimension. These helpers
recover the JSON from fences/prose so realistic agent output still parses.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def loads_lenient(text: str):
    """Parse JSON, tolerating surrounding code fences or prose. Raise ValueError if none."""
    if not text or not text.strip():
        raise ValueError("empty text")
    s = text.strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    m = _FENCE.search(s)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            s = m.group(1).strip()
    # Fall back to the outermost {...} or [...] span.
    candidates = []
    for op, cl in (("{", "}"), ("[", "]")):
        i, j = s.find(op), s.rfind(cl)
        if 0 <= i < j:
            candidates.append((i, s[i : j + 1]))
    for _, span in sorted(candidates):
        try:
            return json.loads(span)
        except json.JSONDecodeError:
            continue
    raise ValueError("no parseable JSON found")


def read_or(path, default=None):
    """Lenient read of a JSON file; return ``default`` if missing or unparseable."""
    p = Path(path)
    if not p.exists():
        return default
    try:
        return loads_lenient(p.read_text())
    except (OSError, ValueError):
        return default
