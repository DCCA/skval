"""D6 — Static safety / least-surprise scan (the hard gate).

A deterministic first pass for clearly dangerous or surprising content:
destructive shell commands, remote-code-execution pipes, and prompt-injection
markers. Any ``critical`` finding vetoes the whole scorecard (safety_pass=False),
so a high quality score can never mask an unsafe skill. An LLM safety reviewer
(M1) layers nuance on top of this floor; this stage stays cheap and obvious.
"""

from __future__ import annotations

import re
from pathlib import Path

_SCAN_SUFFIXES = {".md", ".py", ".sh", ".bash", ".js", ".ts", ".rb", ".pl"}
_SKIP_DIRS = {"__pycache__", "node_modules", ".git"}


# (regex, severity, label). All patterns are matched case-insensitively.
def _ci(pattern: str) -> re.Pattern:
    return re.compile(pattern, re.IGNORECASE)


_PATTERNS = [
    (_ci(r"rm\s+-[rf]{2}\s+/(?![\w.])"), "critical", "destructive: recursive delete of root"),
    (
        _ci(r"rm\s+-[rf]{2}\s+(~|\*|\$HOME)(?=/|\s|$)"),
        "critical",
        "destructive: recursive delete of home/glob",
    ),
    (_ci(r"\bmkfs(\.\w+)?\b"), "critical", "destructive: filesystem format"),
    (_ci(r"\bdd\b[^\n]*\bof=\s*/dev/"), "critical", "destructive: raw disk write"),
    (_ci(r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:"), "critical", "fork bomb"),
    (_ci(r">\s*/dev/sd[a-z]"), "critical", "destructive: overwrite block device"),
    (
        _ci(r"(curl|wget)\b[^\n|]*\|\s*(sudo\s+)?(sh|bash|zsh)\b"),
        "critical",
        "remote code execution: pipe to shell",
    ),
    (_ci(r"ignore\s+(all\s+)?(previous|prior)\s+instructions"), "critical", "prompt injection"),
    (
        _ci(r"disregard\s+(the\s+)?(system\s+prompt|previous|prior\s+instructions)"),
        "critical",
        "prompt injection",
    ),
]


_DEFENSIVE_RE = _ci(
    r"\b(deny|denylist|block|blocklist|disallow|forbid|reject|refuse|prevent|"
    r"detect|dangerous|guard|prohibit|warn)\b"
)


def _is_defensive(line: str, m: re.Match) -> bool:
    """True when a dangerous match is a string being *matched/blocked* or documented.

    Skills that guard against dangerous commands (a hook checking ``*"mkfs"*``) or
    document them ("block ``dd if=``…") quote the token or sit on a line with a
    defensive keyword — not an executable invocation. Real destructive commands
    are unquoted and lack that framing, so they stay flagged.
    """
    before, after = line[: m.start()], line[m.end() :]
    quoted = bool(re.search(r"[\"'][*]?\s*$", before)) and bool(re.match(r"\s*[*]?[\"']", after))
    return quoted or bool(_DEFENSIVE_RE.search(line))


def _iter_files(skill_dir: Path):
    for p in sorted(skill_dir.rglob("*")):
        if not p.is_file():
            continue
        if any(part in _SKIP_DIRS for part in p.relative_to(skill_dir).parts):
            continue
        if p.suffix.lower() in _SCAN_SUFFIXES:
            yield p


def scan(skill_dir: Path) -> dict:
    skill_dir = Path(skill_dir)
    findings: list[dict] = []
    for path in _iter_files(skill_dir):
        rel = str(path.relative_to(skill_dir))
        try:
            lines = path.read_text(errors="replace").splitlines()
        except OSError:
            continue
        for lineno, line in enumerate(lines, start=1):
            for pattern, severity, label in _PATTERNS:
                m = pattern.search(line)
                if m and not _is_defensive(line, m):
                    findings.append(
                        {
                            "pattern": label,
                            "severity": severity,
                            "file": rel,
                            "line": lineno,
                            "excerpt": line.strip()[:200],
                        }
                    )
    safety_pass = not any(f["severity"] == "critical" for f in findings)
    return {"safety_pass": safety_pass, "findings": findings}


if __name__ == "__main__":
    import json
    import sys

    print(json.dumps(scan(Path(sys.argv[1])), indent=2))
