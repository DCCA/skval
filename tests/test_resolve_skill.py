import io
import shutil
import stat
import tarfile
import zipfile

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


def test_zip_slip_blocked(tmp_path):
    arc = tmp_path / "evil.zip"
    with zipfile.ZipFile(arc, "w") as z:
        z.writestr("SKILL.md", FM)
        z.writestr("../evil.txt", "pwned")
    with pytest.raises(ValueError, match="zip-slip"):
        resolve_skill.resolve(str(arc), tmp_path / "work")
    assert not (tmp_path / "evil.txt").exists()  # nothing extracted outside dest


def test_zip_symlink_blocked(tmp_path):
    arc = tmp_path / "sym.zip"
    with zipfile.ZipFile(arc, "w") as z:
        z.writestr("SKILL.md", FM)
        zi = zipfile.ZipInfo("link")
        zi.external_attr = (stat.S_IFLNK | 0o777) << 16
        z.writestr(zi, "/etc/passwd")
    with pytest.raises(ValueError, match="symlink"):
        resolve_skill.resolve(str(arc), tmp_path / "work")


def test_tar_slip_blocked(tmp_path):
    arc = tmp_path / "evil.tar.gz"
    with tarfile.open(arc, "w:gz") as t:
        data = FM.encode()
        si = tarfile.TarInfo("SKILL.md")
        si.size = len(data)
        t.addfile(si, io.BytesIO(data))
        ev = b"pwned"
        ei = tarfile.TarInfo("../evil.txt")
        ei.size = len(ev)
        t.addfile(ei, io.BytesIO(ev))
    with pytest.raises(ValueError, match="tar-slip"):
        resolve_skill.resolve(str(arc), tmp_path / "work")
    assert not (tmp_path / "evil.txt").exists()


def test_tar_symlink_blocked(tmp_path):
    arc = tmp_path / "lnk.tar"
    with tarfile.open(arc, "w") as t:
        data = FM.encode()
        si = tarfile.TarInfo("SKILL.md")
        si.size = len(data)
        t.addfile(si, io.BytesIO(data))
        li = tarfile.TarInfo("link")
        li.type = tarfile.SYMTYPE
        li.linkname = "/etc/passwd"
        t.addfile(li)
    with pytest.raises(ValueError, match="link"):
        resolve_skill.resolve(str(arc), tmp_path / "work")


def test_decompression_bomb_guard(tmp_path, monkeypatch):
    monkeypatch.setattr(resolve_skill, "_MAX_UNCOMPRESSED", 10)
    arc = tmp_path / "big.zip"
    with zipfile.ZipFile(arc, "w") as z:
        z.writestr("SKILL.md", FM)  # larger than the patched 10-byte cap
    with pytest.raises(ValueError, match="too large"):
        resolve_skill.resolve(str(arc), tmp_path / "work")


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
