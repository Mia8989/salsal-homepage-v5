#!/usr/bin/env python3
"""SALSAL v5 site builder: stamp the global nav + footer into every page.

Single source of truth: partials/nav.html and partials/footer.html.
Edit either, run `python3 build.py`, and EVERY *.html page under this folder
(any depth, including webinars/<slug>/index.html) gets the updated block.

Pages mark their nav/footer regions with:
  <!-- NAV:START --> ... <!-- NAV:END -->
  <!-- FOOTER:START --> ... <!-- FOOTER:END -->

{{B}} in the partials is replaced per page with the relative path back to the
site root ("" at root, "../" one level deep, "../../" two levels), so clean
folder-per-page URLs work locally and on GitHub Pages.
"""
import re, os, glob

HERE = os.path.dirname(os.path.abspath(__file__))

def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

nav_src = read(os.path.join(HERE, "partials", "nav.html")).strip()
foot_src = read(os.path.join(HERE, "partials", "footer.html")).strip()

RE_NAV = re.compile(r"<!-- NAV:START -->.*?<!-- NAV:END -->", re.S)
RE_FOOT = re.compile(r"<!-- FOOTER:START -->.*?<!-- FOOTER:END -->", re.S)

def base_for(path):
    rel = os.path.relpath(path, HERE)
    depth = rel.count(os.sep)          # index.html -> 0, mission-vision/index.html -> 1
    return "../" * depth

changed, skipped, nomarker = [], [], []
for path in sorted(glob.glob(os.path.join(HERE, "**", "*.html"), recursive=True)):
    if os.sep + "partials" + os.sep in path:
        continue
    html = read(path)
    orig = html
    b = base_for(path)
    nav_block = "<!-- NAV:START -->\n" + nav_src.replace("{{B}}", b) + "\n<!-- NAV:END -->"
    foot_block = "<!-- FOOTER:START -->\n" + foot_src.replace("{{B}}", b) + "\n<!-- FOOTER:END -->"

    if RE_NAV.search(html):
        html = RE_NAV.sub(lambda m: nav_block, html, count=1)
    else:
        nomarker.append(os.path.relpath(path, HERE) + " (nav)")
    if RE_FOOT.search(html):
        html = RE_FOOT.sub(lambda m: foot_block, html, count=1)
    else:
        nomarker.append(os.path.relpath(path, HERE) + " (footer)")

    if html != orig:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        changed.append(os.path.relpath(path, HERE))
    else:
        skipped.append(os.path.relpath(path, HERE))

print(f"updated:   {len(changed)} -> {', '.join(changed) if changed else 'none'}")
print(f"unchanged: {len(skipped)}")
if nomarker:
    print("MISSING MARKERS:")
    for m in nomarker:
        print("  !", m)
