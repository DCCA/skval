"""D1 — Structural integrity checks (deterministic, no model calls).

Cheap, gameability-resistant hygiene checks on a skill directory: frontmatter
validity and the SKILL.md authoring rules (name kebab-case <=64, description
<=1024 with no angle brackets, allowed frontmatter keys, exactly one packaged
SKILL.md), plus a size budget and broken local references. Mirrors and extends
the rules in Anthropic's skill-creator ``quick_validate.py``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

ALLOWED_FRONTMATTER_KEYS = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
}

# Directories whose contents are not packaged as part of the skill, so a nested
# SKILL.md inside them does not count toward the single-SKILL.md rule.
_EXCLUDED_DIR_PARTS = {"__pycache__", "node_modules"}
_ROOT_EXCLUDED_DIR_PARTS = {"evals"}

_SEVERITY_WEIGHT = {"critical": 3, "major": 2, "minor": 1}

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
_MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_MD_REF_DEF_RE = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)", re.MULTILINE)
_LINE_BUDGET = 500
_TOKEN_BUDGET = 5000  # estimated tokens for the SKILL.md body


@dataclass
class Check:
    id: str
    passed: bool
    severity: str  # "critical" | "major" | "minor"
    detail: str


def parse_frontmatter(skill_md_text: str) -> dict:
    """Return the YAML frontmatter as a dict, or raise ValueError if malformed."""
    skill_md_text = skill_md_text.replace("\r\n", "\n").replace("\r", "\n")  # tolerate CRLF
    if not skill_md_text.startswith("---"):
        raise ValueError("no YAML frontmatter found")
    match = _FRONTMATTER_RE.match(skill_md_text)
    if not match:
        raise ValueError("invalid frontmatter delimiters")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a YAML mapping")
    return data


def skill_name(skill_md) -> str | None:
    """Best-effort skill name from a SKILL.md path; None if unreadable/missing."""
    try:
        return parse_frontmatter(Path(skill_md).read_text()).get("name")
    except (ValueError, OSError):
        return None


def _counts_as_skill_md(rel_path: Path) -> bool:
    dir_parts = rel_path.parts[:-1]
    if any(part in _EXCLUDED_DIR_PARTS for part in dir_parts):
        return False
    if dir_parts and dir_parts[0] in _ROOT_EXCLUDED_DIR_PARTS:
        return False
    return True


def _clean_target(raw: str) -> str:
    """Extract the path from a Markdown link/ref destination.

    Handles angle-bracket destinations (``<path>``), an optional "title" after the
    path, and a trailing ``#anchor``.
    """
    t = raw.strip()
    if t.startswith("<"):
        end = t.find(">")
        t = t[1:end] if end != -1 else t[1:]
    else:
        t = t.split()[0] if t.split() else ""
    return t.split("#")[0].strip()


def _broken_local_refs(skill_dir: Path, text: str) -> list[str]:
    broken = []
    # Inline links [t](path) and reference-style definitions [id]: path.
    for raw in _MD_LINK_RE.findall(text) + _MD_REF_DEF_RE.findall(text):
        target = _clean_target(raw)
        if not target or re.match(r"^[a-z]+://", target) or target.startswith(("#", "mailto:")):
            continue
        if not (skill_dir / target).exists():
            broken.append(target)
    return broken


def run_checks(skill_dir: Path) -> list[Check]:
    skill_dir = Path(skill_dir)
    checks: list[Check] = []

    def add(id_, passed, severity, detail=""):
        checks.append(Check(id_, passed, severity, detail))

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        add("frontmatter_present", False, "critical", "SKILL.md not found")
        return checks

    text = skill_md.read_text().replace("\r\n", "\n").replace("\r", "\n")

    # Frontmatter present + valid.
    has_fm = text.startswith("---")
    add("frontmatter_present", has_fm, "critical", "" if has_fm else "missing leading '---'")
    fm: dict = {}
    fm_ok = False
    try:
        fm = parse_frontmatter(text)
        fm_ok = True
        add("frontmatter_valid_yaml", True, "critical")
    except ValueError as e:
        add("frontmatter_valid_yaml", False, "critical", str(e))

    # Name.
    name = (fm.get("name") if fm_ok else None) or ""
    name = name.strip() if isinstance(name, str) else ""
    add("name_present", bool(name), "critical", "" if name else "missing 'name'")
    kebab_ok = bool(
        name
        and re.match(r"^[a-z0-9-]+$", name)
        and not (name.startswith("-") or name.endswith("-") or "--" in name)
        and len(name) <= 64
    )
    add(
        "name_kebab_case",
        kebab_ok,
        "major",
        "" if kebab_ok else f"name {name!r} must be kebab-case, <=64 chars",
    )

    # Description.
    desc = (fm.get("description") if fm_ok else None) or ""
    desc = desc.strip() if isinstance(desc, str) else ""
    add("description_present", bool(desc), "critical", "" if desc else "missing 'description'")
    len_ok = bool(desc) and len(desc) <= 1024
    add(
        "description_len",
        len_ok,
        "major",
        "" if len_ok else f"description is {len(desc)} chars (max 1024)",
    )
    no_angles = "<" not in desc and ">" not in desc
    add(
        "description_no_angle_brackets",
        no_angles,
        "major",
        "" if no_angles else "description contains '<' or '>'",
    )

    # Allowed keys.
    unexpected = set(fm.keys()) - ALLOWED_FRONTMATTER_KEYS if fm_ok else set()
    add(
        "allowed_frontmatter_keys",
        not unexpected,
        "minor",
        "" if not unexpected else f"unexpected key(s): {', '.join(sorted(unexpected))}",
    )

    # Exactly one packaged SKILL.md.
    packaged = [
        p for p in skill_dir.rglob("SKILL.md") if _counts_as_skill_md(p.relative_to(skill_dir))
    ]
    single_ok = len(packaged) <= 1
    add(
        "single_skill_md",
        single_ok,
        "critical",
        "" if single_ok else f"found {len(packaged)} packaged SKILL.md files (expected 1)",
    )

    # Size budget.
    n_lines = text.count("\n") + 1
    line_ok = n_lines <= _LINE_BUDGET
    add(
        "skill_md_line_budget",
        line_ok,
        "minor",
        "" if line_ok else f"SKILL.md is {n_lines} lines (> {_LINE_BUDGET}); consider splitting",
    )
    est_tokens = len(text) // 4
    tok_ok = est_tokens <= _TOKEN_BUDGET
    add(
        "token_budget",
        tok_ok,
        "minor",
        "" if tok_ok else f"SKILL.md ~{est_tokens} tokens (> {_TOKEN_BUDGET}); move detail to references/",
    )

    # Broken local references.
    broken = _broken_local_refs(skill_dir, text)
    add(
        "no_broken_local_refs",
        not broken,
        "major",
        "" if not broken else f"missing referenced path(s): {', '.join(broken)}",
    )

    return checks


def d1_score(checks: list[Check]) -> float:
    """Severity-weighted fraction of checks passed, in [0, 1]."""
    total = sum(_SEVERITY_WEIGHT[c.severity] for c in checks)
    if total == 0:
        return 0.0
    earned = sum(_SEVERITY_WEIGHT[c.severity] for c in checks if c.passed)
    return round(earned / total, 4)


if __name__ == "__main__":
    import sys

    results = run_checks(Path(sys.argv[1]))
    for c in results:
        mark = "PASS" if c.passed else "FAIL"
        print(f"[{mark}] {c.id} ({c.severity}) {c.detail}")
    print(f"\nD1 score: {d1_score(results):.3f}")
