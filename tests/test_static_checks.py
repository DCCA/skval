import textwrap

import static_checks as sc

GOOD = textwrap.dedent("""\
    ---
    name: my-skill
    description: Use when you need to do the thing in a specific situation.
    ---
    # My Skill
    Body text.
    """)


def _write(tmp_path, body, name="good"):
    d = tmp_path / name
    d.mkdir()
    (d / "SKILL.md").write_text(body)
    return d


def test_good_skill_passes_core_checks(tmp_path):
    d = _write(tmp_path, GOOD)
    checks = {c.id: c for c in sc.run_checks(d)}
    assert checks["frontmatter_valid_yaml"].passed
    assert checks["name_kebab_case"].passed
    assert checks["description_len"].passed
    assert checks["no_broken_local_refs"].passed
    assert sc.d1_score(list(checks.values())) > 0.9


def test_bad_name_and_description(tmp_path):
    body = "---\nname: My_Skill\ndescription: " + ("x" * 1100) + "\n---\n# x\n"
    d = _write(tmp_path, body, name="bad")
    checks = {c.id: c for c in sc.run_checks(d)}
    assert not checks["name_kebab_case"].passed
    assert not checks["description_len"].passed
    assert sc.d1_score(list(checks.values())) < 0.9


def test_missing_frontmatter(tmp_path):
    d = _write(tmp_path, "# no frontmatter\n", name="nofm")
    checks = {c.id: c for c in sc.run_checks(d)}
    assert not checks["frontmatter_present"].passed


def test_angle_brackets_and_unknown_keys(tmp_path):
    body = "---\nname: ok-name\ndescription: Use <when> things happen.\nfoo: bar\n---\n# x\n"
    d = _write(tmp_path, body, name="ang")
    checks = {c.id: c for c in sc.run_checks(d)}
    assert not checks["description_no_angle_brackets"].passed
    assert not checks["allowed_frontmatter_keys"].passed


def test_broken_reference_detected(tmp_path):
    body = GOOD + "\nSee [helper](scripts/missing.py) for details.\n"
    d = _write(tmp_path, body, name="ref")
    checks = {c.id: c for c in sc.run_checks(d)}
    assert not checks["no_broken_local_refs"].passed


def test_existing_reference_passes(tmp_path):
    d = _write(tmp_path, GOOD + "\nSee [helper](scripts/real.py).\n", name="ok-ref")
    (d / "scripts").mkdir()
    (d / "scripts" / "real.py").write_text("# ok\n")
    checks = {c.id: c for c in sc.run_checks(d)}
    assert checks["no_broken_local_refs"].passed


def test_parse_frontmatter_roundtrip():
    fm = sc.parse_frontmatter(GOOD)
    assert fm["name"] == "my-skill"
