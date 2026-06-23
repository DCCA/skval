#!/usr/bin/env python3
"""Deterministic share-readiness meta check for a web page (URL or local HTML file).

Reports presence of Open Graph / Twitter Card / canonical tags, JSON-LD validity, and
whether og:image is reachable with pixel dimensions matching the declared
og:image:width/height. Standard library only — no third-party deps, no model calls.

Usage:  python check_meta.py <url-or-file>
Exits non-zero if a REQUIRED tag is missing (so it can gate a publish step).
"""

from __future__ import annotations

import json
import re
import struct
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser

REQUIRED_OG = ["og:title", "og:description", "og:type", "og:url", "og:image", "og:site_name"]
RECOMMENDED_OG = ["og:image:width", "og:image:height", "og:image:alt"]
REQUIRED_TW = ["twitter:card", "twitter:title", "twitter:description", "twitter:image"]
_UA = {"User-Agent": "share-audit/1.0"}


class _MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta: dict[str, str] = {}
        self.canonical: str | None = None
        self.lang: str | None = None
        self.jsonld: list[str] = []
        self._in_ld = False
        self._ld: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html" and a.get("lang"):
            self.lang = a["lang"]
        elif tag == "meta":
            key = a.get("property") or a.get("name")
            if key and a.get("content") is not None:
                self.meta.setdefault(key, a["content"])
        elif tag == "link" and (a.get("rel") or "").lower() == "canonical":
            self.canonical = a.get("href")
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld, self._ld = True, []

    def handle_endtag(self, tag):
        if tag == "script" and self._in_ld:
            self._in_ld = False
            self.jsonld.append("".join(self._ld))

    def handle_data(self, data):
        if self._in_ld:
            self._ld.append(data)


def _is_url(s: str) -> bool:
    return bool(re.match(r"^https?://", s))


def _load(src: str) -> str:
    if _is_url(src):
        with urllib.request.urlopen(urllib.request.Request(src, headers=_UA), timeout=20) as r:
            return r.read().decode("utf-8", "replace")
    with open(src, encoding="utf-8", errors="replace") as f:
        return f.read()


def _fetch_bytes(img: str, base: str) -> bytes | None:
    if _is_url(img) or _is_url(base):
        url = urllib.parse.urljoin(base, img) if not _is_url(img) else img
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=_UA), timeout=20) as r:
                return r.read()
        except Exception:
            return None
    # both local: resolve relative to the html file's dir
    import os

    path = img if os.path.isabs(img) else os.path.join(os.path.dirname(base) or ".", img)
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError:
        return None


def _img_dims(b: bytes | None) -> tuple[int, int] | None:
    if not b:
        return None
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", b[16:24])
        return (w, h)
    if b[:2] == b"\xff\xd8":  # JPEG
        i = 2
        while i < len(b) - 9:
            if b[i] != 0xFF:
                i += 1
                continue
            marker = b[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3):
                h, w = struct.unpack(">HH", b[i + 5 : i + 9])
                return (w, h)
            i += 2 + struct.unpack(">H", b[i + 2 : i + 4])[0]
    return None


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python check_meta.py <url-or-file>", file=sys.stderr)
        return 2
    src = argv[1]
    p = _MetaParser()
    p.feed(_load(src))

    missing: list[str] = []

    def line(ok: bool, label: str, extra: str = "") -> None:
        print(f"  [{'x' if ok else ' '}] {label}{(' — ' + extra) if extra else ''}")

    print(f"share-audit · meta check · {src}\n")

    print("Open Graph:")
    for k in REQUIRED_OG:
        ok = k in p.meta
        line(ok, k, p.meta.get(k, "MISSING")[:80])
        if not ok:
            missing.append(k)
    for k in RECOMMENDED_OG:
        line(k in p.meta, k + " (recommended)", p.meta.get(k, "—")[:80])

    print("\nTwitter:")
    for k in REQUIRED_TW:
        ok = k in p.meta
        line(ok, k, p.meta.get(k, "MISSING")[:80])
        if not ok:
            missing.append(k)

    print("\nCanonical & lang:")
    line(bool(p.canonical), "rel=canonical", p.canonical or "MISSING")
    line(bool(p.lang), "html lang", p.lang or "MISSING")

    print("\nog:image:")
    img = p.meta.get("og:image")
    if not img:
        line(False, "og:image present", "MISSING")
    else:
        b = _fetch_bytes(img, src)
        line(bool(b), "reachable", img[:80])
        dims = _img_dims(b)
        if dims:
            dw, dh = dims
            declared = (p.meta.get("og:image:width"), p.meta.get("og:image:height"))
            match = declared == (str(dw), str(dh))
            ratio = dw / dh if dh else 0
            line(True, "actual pixels", f"{dw}x{dh} (ratio {ratio:.2f}; 1.91 is ideal)")
            if declared[0] or declared[1]:
                line(
                    match,
                    "declared width/height match actual",
                    f"declared {declared[0]}x{declared[1]}",
                )
        elif b:
            line(False, "decode dimensions", "not PNG/JPEG or unreadable header")

    print("\nJSON-LD:")
    if not p.jsonld:
        line(False, "structured data present", "none")
    for i, block in enumerate(p.jsonld):
        try:
            data = json.loads(block)
            t = data.get("@type") if isinstance(data, dict) else "(array)"
            line(True, f"block {i} valid JSON", f"@type={t}")
        except json.JSONDecodeError as e:
            line(False, f"block {i} valid JSON", str(e))

    print()
    if missing:
        print(f"RESULT: {len(missing)} required tag(s) MISSING: {', '.join(missing)}")
        return 1
    print("RESULT: all required Open Graph + Twitter tags present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
