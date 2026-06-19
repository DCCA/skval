import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "skill-validator" / "scripts"


def _run_script(script: str, *args: str):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_public_scripts_have_help():
    for script in [
        "validate_structural.py",
        "validate_full.py",
        "benchmark_export.py",
        "history.py",
        "calibrate.py",
    ]:
        result = _run_script(script, "--help")
        assert result.returncode == 0, result.stderr
        assert "usage:" in result.stdout
        assert "Traceback" not in result.stderr


def test_pyproject_exposes_skval_console_script():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert pyproject["project"]["scripts"]["skval"] == "skval_cli:main"
    assert pyproject["tool"]["setuptools"]["package-dir"][""] == "skills/skill-validator/scripts"
    packaged_modules = set(pyproject["tool"]["setuptools"]["py-modules"])
    assert {"skval_cli", "validate_structural", "validate_full", "benchmark_export", "batch", "compare"} <= packaged_modules
