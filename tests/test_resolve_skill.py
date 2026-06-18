import shutil

import pytest

import resolve_skill

FM = "---\nname: a\ndescription: Use when needed.\n---\n# A\n"


def test_resolve_directory(tmp_path):
    s = tmp_path / "sk"
    s.mkdir()
    (s / "SKILL.md").write_text(FM)
    r = resolve_skill.resolve(str(s), tmp_path / "work")
    assert r["kind"] == "dir"
    assert r["skill_md"].name == "SKILL.md"
    assert r["skill_dir"] == s


def test_resolve_single_file(tmp_path):
    f = tmp_path / "SKILL.md"
    f.write_text(FM)
    r = resolve_skill.resolve(str(f), tmp_path / "work")
    assert r["kind"] == "file"
    assert (r["skill_dir"] / "SKILL.md").exists()
    assert r["skill_dir"] != tmp_path  # copied into workdir


def test_missing_skill_md_errors(tmp_path):
    s = tmp_path / "empty"
    s.mkdir()
    with pytest.raises(FileNotFoundError):
        resolve_skill.resolve(str(s), tmp_path / "work")


def test_nonexistent_source_errors(tmp_path):
    with pytest.raises(FileNotFoundError):
        resolve_skill.resolve(str(tmp_path / "nope"), tmp_path / "work")


def test_resolve_archive(tmp_path):
    src = tmp_path / "pkg"
    src.mkdir()
    (src / "SKILL.md").write_text(FM)
    archive = shutil.make_archive(str(tmp_path / "mskill"), "zip", root_dir=src)
    r = resolve_skill.resolve(archive, tmp_path / "work")
    assert r["kind"] == "archive"
    assert (r["skill_dir"] / "SKILL.md").exists()


def test_remote_reference_not_implemented(tmp_path):
    with pytest.raises(NotImplementedError):
        resolve_skill.resolve("https://example.com/skill.git", tmp_path / "work")


def test_provenance_recorded(tmp_path):
    s = tmp_path / "sk"
    s.mkdir()
    (s / "SKILL.md").write_text(FM)
    r = resolve_skill.resolve(str(s), tmp_path / "work")
    assert r["provenance"]["source"] == str(s)
    assert r["provenance"]["kind"] == "dir"
