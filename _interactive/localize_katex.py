#!/usr/bin/env python3
"""Post-render step (registered in _quarto.yml): point the KaTeX embeds
at the vendored copy under assets/katex/ instead of the jsdelivr CDN.

Pandoc emits the KaTeX script without `defer`, so it blocks the page -
and behind the StatiCrypt password gate every page re-loads it after
decryption. Serving it same-origin (and cached) removes the last
external dependency from the pages. KaTeX 0.18.7 is vendored; re-run
`npm pack katex` and refresh assets/katex/ to upgrade.
"""
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "_site"
CDN = re.compile(r"https://cdn\.jsdelivr\.net/npm/katex@[^/\"]+/dist/")

changed = 0
for page in SITE.rglob("*.html"):
    text = page.read_text()
    if not CDN.search(text):
        continue
    depth = len(page.relative_to(SITE).parts) - 1
    prefix = "../" * depth + "assets/katex/"
    page.write_text(CDN.sub(prefix, text))
    changed += 1
print(f"localize_katex: rewrote {changed} pages to {('../' * 0)}assets/katex/")
