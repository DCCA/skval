"""Precision regression tests — real-world false positives skval used to flag.

Derived from a skval run over 75 installed skills (Anthropic plugins, Vercel,
Superpowers): the structural + safety scan over-flagged valid skills. Each test
pins a false-positive class so it can't regress, while a paired true-positive
keeps the check honest.
"""

from pathlib import Path

import safety_scan
import static_checks


def _skill(tmp_path: Path, body: str = "# Body\n", frontmatter: str = "name: x\ndescription: d"):
    (tmp_path / "SKILL.md").write_text(f"---\n{frontmatter}\n---\n{body}")
    return tmp_path


def _checks(skill_dir: Path) -> dict:
    return {c.id: c for c in static_checks.run_checks(skill_dir)}


# ---- ref detection: code / frontmatter are not markdown -------------------


def test_link_like_text_in_frontmatter_not_flagged(tmp_path):
    # A regex in frontmatter (e.g. Vercel's chainTo patterns) reads as [..](..).
    fm = 'name: x\ndescription: d\nchainTo: "[\'\\"](jsonwebtoken)"'
    _skill(tmp_path, body="# Body, no real links\n", frontmatter=fm)
    assert _checks(tmp_path)["no_broken_local_refs"].passed


def test_link_in_fenced_code_not_flagged(tmp_path):
    _skill(tmp_path, body="See:\n\n```js\nimport x from '[a](nope.py)'\n```\n")
    assert _checks(tmp_path)["no_broken_local_refs"].passed


def test_link_in_inline_code_not_flagged(tmp_path):
    _skill(tmp_path, body="Use `[x](missing.py)` as a pattern.\n")
    assert _checks(tmp_path)["no_broken_local_refs"].passed


def test_real_broken_body_link_still_flagged(tmp_path):
    _skill(tmp_path, body="See [the helper](scripts/missing.py).\n")
    assert not _checks(tmp_path)["no_broken_local_refs"].passed


# ---- frontmatter keys: widely-used keys are allowed ------------------------


def test_common_plugin_keys_allowed(tmp_path):
    fm = "name: x\ndescription: d\nversion: 1\nuser-invocable: true\ntools: [Read]"
    _skill(tmp_path, frontmatter=fm)
    assert _checks(tmp_path)["allowed_frontmatter_keys"].passed


def test_typo_key_still_flagged(tmp_path):
    _skill(tmp_path, frontmatter="name: x\ndescription: d\ndescriptionn: oops")
    assert not _checks(tmp_path)["allowed_frontmatter_keys"].passed


# ---- safety: defensive / documented dangerous commands are not unsafe ------


def test_blocking_hook_not_flagged_unsafe(tmp_path):
    (tmp_path / "validate.sh").write_text(
        'if [[ "$cmd" == *"mkfs"* ]] || [[ "$cmd" == *"dd if="* ]]; then deny; fi\n'
    )
    assert safety_scan.scan(tmp_path)["safety_pass"]


def test_documented_dangerous_command_not_flagged(tmp_path):
    (tmp_path / "SKILL.md").write_text(
        "---\nname: x\ndescription: d\n---\nBlock dd if=/dev/zero.\n"
    )
    assert safety_scan.scan(tmp_path)["safety_pass"]


def test_real_destructive_command_still_unsafe(tmp_path):
    (tmp_path / "run.sh").write_text("#!/bin/sh\nmkfs.ext4 /dev/sda\nrm -rf ~/data\n")
    assert not safety_scan.scan(tmp_path)["safety_pass"]


def test_dd_to_regular_file_not_flagged(tmp_path):
    # Creating a test file with dd is benign — only writes to a device are dangerous.
    (tmp_path / "doc.md").write_text(
        "Make a fixture: dd if=/dev/zero of=/tmp/big.bin bs=1M count=100\n"
    )
    assert safety_scan.scan(tmp_path)["safety_pass"]


def test_dd_to_block_device_still_unsafe(tmp_path):
    (tmp_path / "run.sh").write_text("dd if=/dev/zero of=/dev/sda bs=1M\n")
    assert not safety_scan.scan(tmp_path)["safety_pass"]
