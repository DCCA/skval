"""Resolve a skill input to a canonical skill directory.

Accepts the forms in the PRD: an existing skill **directory**, a single
**SKILL.md** file (wrapped into a directory), or a packaged **archive**
(`.skill`/`.zip`/`.tar.gz`). Remote/git references are recognized and rejected
with a clear message for now (M1). Returns the canonical directory plus
provenance so a run is reproducible.
"""

from __future__ import annotations

import re
import shutil
import zipfile
from pathlib import Path

_REMOTE_RE = re.compile(r"^[a-z][a-z0-9+.\-]*://", re.IGNORECASE)
_ARCHIVE_SUFFIXES = {".zip", ".skill", ".tgz", ".tar", ".gz"}


def _find_skill_md(root: Path) -> Path:
    if (root / "SKILL.md").exists():
        return root / "SKILL.md"
    matches = sorted(root.rglob("SKILL.md"))
    if matches:
        return matches[0]
    raise FileNotFoundError(f"no SKILL.md found under {root}")


def _unpack(archive: Path, dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    name = archive.name.lower()
    if name.endswith((".zip", ".skill")):
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(dest)
    elif name.endswith((".tar", ".tar.gz", ".tgz", ".gz")):
        shutil.unpack_archive(str(archive), str(dest))
    else:
        raise ValueError(f"unsupported archive type: {archive.name}")
    return dest


def resolve(source: str, workdir: Path) -> dict:
    """Return {skill_dir, skill_md, kind, provenance} for a skill input."""
    workdir = Path(workdir)

    if _REMOTE_RE.match(source) or source.endswith(".git") or source.startswith("git@"):
        raise NotImplementedError(
            "remote/git skill references are not supported yet (planned for M1); "
            "clone or download the skill locally and pass its path"
        )

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"skill source not found: {source}")

    if path.is_dir():
        skill_md = path / "SKILL.md"
        if not skill_md.exists():
            raise FileNotFoundError(f"no SKILL.md in directory: {path}")
        kind = "dir"
        skill_dir = path
    elif path.suffix.lower() in _ARCHIVE_SUFFIXES or path.name.lower().endswith(".tar.gz"):
        extract_dir = _unpack(path, workdir / "unpacked")
        skill_md = _find_skill_md(extract_dir)
        skill_dir = skill_md.parent
        kind = "archive"
    elif path.suffix.lower() == ".md":
        dest = workdir / "skill"
        dest.mkdir(parents=True, exist_ok=True)
        skill_md = dest / "SKILL.md"
        shutil.copyfile(path, skill_md)
        skill_dir = dest
        kind = "file"
    else:
        raise ValueError(
            f"unrecognized skill source: {source} "
            "(expected a directory, a SKILL.md file, or a .skill/.zip archive)"
        )

    return {
        "skill_dir": skill_dir,
        "skill_md": skill_md,
        "kind": kind,
        "provenance": {"source": source, "kind": kind, "resolved_path": str(skill_dir)},
    }


if __name__ == "__main__":
    import json
    import sys
    import tempfile

    out = resolve(sys.argv[1], Path(tempfile.mkdtemp(prefix="skval-")))
    print(json.dumps({**out, "skill_dir": str(out["skill_dir"]), "skill_md": str(out["skill_md"])}, indent=2))
