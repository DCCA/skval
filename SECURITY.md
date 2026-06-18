# Security Policy

## Reporting a vulnerability

Please report security issues **privately** via GitHub's *Security → Report a vulnerability*
(private advisory) rather than opening a public issue. We'll respond as quickly as we can.

## Threat model & hardening

skval ingests **untrusted skills** — directories, `SKILL.md` files, and `.skill` / `.zip` /
`.tar.gz` archives — and runs deterministic checks on them.

- **Archive extraction is hardened** (`scripts/resolve_skill.py`): members that would escape
  the destination via path traversal (*zip-slip* / *tar-slip*), absolute paths, or
  symlink/hardlink members are **rejected before extraction**, and oversized archives are
  refused (decompression-bomb guard). This covers the CVE-2007-4559 class of `tarfile` issues.
- The **deterministic engine** (`scripts/*.py`) makes **no network calls** and parses
  frontmatter with `yaml.safe_load` (no arbitrary object construction). No `eval`/`exec`,
  `shell=True`, `os.system`, or `pickle`.
- The **behavioral** path *executes* the skill under test (via the agent / `claude -p`) to
  measure it. Only run full validation on skills you are willing to execute, ideally in a
  sandbox — this is inherent to behavioral evaluation, not a defect.

## Supported versions

The latest `main` is supported.
