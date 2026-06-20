#!/usr/bin/env bash
# PostToolUse(Edit|Write) hook: auto-format the edited file.
#
# Scope (per project decision): Python only, via `ruff format` (line-length set in
# pyproject.toml). The hand-tuned landing page (docs/index.html) and generated
# example JSON are intentionally NOT auto-formatted.
#
# Reads the hook payload (JSON) on stdin and extracts tool_input.file_path. Always
# exits 0 — formatting must never block or fail an edit.
set -uo pipefail

payload="$(cat)"
file="$(printf '%s' "$payload" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' \
  2>/dev/null || true)"

[ -n "${file}" ] && [ -f "${file}" ] || exit 0

case "${file}" in
  *.py)
    command -v ruff >/dev/null 2>&1 && ruff format -- "${file}" >/dev/null 2>&1 || true
    ;;
esac

exit 0
