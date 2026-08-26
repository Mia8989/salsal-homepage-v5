#!/usr/bin/env python3
"""SALSAL v5 site builder.

Stamps the global nav + footer into every page, AND owns all domain-dependent
SEO output so switching from preview to the real domain is a ONE-LINE change.

=== TO GO LIVE ===
  1. set LIVE = True below
  2. (optional) confirm BASE_LIVE is the final domain
  3. run:  python3 build.py
  4. deploy, then submit BASE/sitemap.xml in Google Search Console
No content rebuild is needed: schema types, FAQ, alt text, and image names are
domain-independent and already baked in. Only canonical/OG/sitemap URLs and the
robots directive are recomputed from BASE.

Single source of truth: partials/nav.html and partials/footer.html.
Pages mark regions with <!-- NAV:START/END -->, <!-- FOOTER:START/END -->.
{{B}} in the partials = relative path back to site root.
"""
import re, os, glob, datetime

HERE = os.path.dirname(os.path.abspath(__file__))

# ============================ CONFIG (the launch switch) =====================
LIVE = False                                              # flip True at launch
BASE_LIVE    = "https://thesalsal.org"
BASE_PREVIEW = "https://mia8989.github.io/salsal-homepage-v5"
SITE = BASE_LIVE if LIVE else BASE_PREVIEW
KNOWN_BASES = [BASE_LIVE, BASE_PREVIEW]                   # rebased -> SITE
# pages that must stay out of search even when LIVE (relative dir):
ALWAYS_NOINDEX = {"sponsorship-packages"}
# ============================================================================

def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

nav_src = read(os.path.join(HERE, "partials", "nav.html")).strip()
foot_src = read(os.path.join(HERE, "partials", "footer.html")).strip()

RE_NAV  = re.compile(r"<!-- NAV:START -->.*?<!-- NAV:END -->", re.S)
RE_FOOT = re.compile(r"<!-- FOOTER:START -->.*?<!-- FOOTER:END -->", re.S)
RE_SEO  = re.compile(r"\n?[ \t]*<!-- SEO:START -->.*?<!-- SEO:END -->\n?", re.S)
RE_ROBOTS = re.compile(r'[ \t]*<meta\s+name="robots"[^>]*>\n?', re.I)

def base_for(path):
    rel = os.path.relpath(path, HERE)
    return "../" * rel.count(os.sep)

def rel_dir(path):
    d = os.path.relpath(os.path.dirname(path), HERE)
    return "" if d == "." else d.replace(os.sep, "/")

def clean_url(path):
    d = rel_dir(path)
    return SITE + "/" + (d + "/" if d else "")

ORG_JSONLD = (
    '<script type="application/ld+json">'
    '{"@context":"https://schema.org","@type":"NGO",'
    '"name":"Save a Leg, Save a Life Foundation","alternateName":"SALSAL",'
    f'"url":"{SITE}/","logo":"{SITE}/assets/logo.png",'
    '"description":"A 501(c)(3) nonprofit working to reduce preventable lower extremity amputations through community screenings, provider education, and patient advocacy.",'
    '"foundingDate":"2015","taxID":"32-0467696",'
    '"address":{"@type":"PostalAddress","streetAddress":"4403 5th Ave NE","addressLocality":"Bradenton","addressRegion":"FL","postalCode":"34208","addressCountry":"US"},'
    '"telephone":"+1-813-445-3857",'
    '"sameAs":["https://www.facebook.com/TheSALSALorg","https://twitter.com/thesalsalorg",'
    '"https://www.linkedin.com/company/the-save-a-leg-save-a-life-foundation/",'
    '"https://www.instagram.com/thesalsalfoundation",'
    '"https://www.youtube.com/channel/UC62XP_YydDhyI1agjEe9Rcw"]}'
    '</script>'
)

def seo_block(path):
    d = rel_dir(path)
    if d in ALWAYS_NOINDEX or not LIVE:
        robots = "noindex, nofollow"
    else:
        robots = "index, follow"
    lines = [
        "  <!-- SEO:START -->",
        f'  <link rel="canonical" href="{clean_url(path)}">',
        f'  <meta name="robots" content="{robots}">',
        "  " + ORG_JSONLD,
        "  <!-- SEO:END -->",
    ]
    return "\n" + "\n".join(lines)

changed, skipped, nomarker, pages = [], [], [], []
for path in sorted(glob.glob(os.path.join(HERE, "**", "*.html"), recursive=True)):
    if os.sep + "partials" + os.sep in path:
        continue
    pages.append(path)
    html = read(path); orig = html
    b = base_for(path)

    # nav / footer
    nav_block  = "<!-- NAV:START -->\n" + nav_src.replace("{{B}}", b) + "\n<!-- NAV:END -->"
    foot_block = "<!-- FOOTER:START -->\n" + foot_src.replace("{{B}}", b) + "\n<!-- FOOTER:END -->"
    if RE_NAV.search(html):  html = RE_NAV.sub(lambda m: nav_block, html, count=1)
    else: nomarker.append(os.path.relpath(path, HERE) + " (nav)")
    if RE_FOOT.search(html): html = RE_FOOT.sub(lambda m: foot_block, html, count=1)
    else: nomarker.append(os.path.relpath(path, HERE) + " (footer)")

    # rebase any known absolute base -> SITE (og:, twitter:, canonical, json-ld)
    for kb in KNOWN_BASES:
        if kb != SITE:
            html = html.replace(kb, SITE)

    # strip old SEO block + any raw robots meta, then stamp fresh SEO block after </title>
    html = RE_SEO.sub("\n", html)
    html = RE_ROBOTS.sub("", html)
    html = re.sub(r"(</title>)", lambda m: m.group(1) + seo_block(path), html, count=1)

    if html != orig:
        with open(path, "w", encoding="utf-8") as f: f.write(html)
        changed.append(os.path.relpath(path, HERE))
    else:
        skipped.append(os.path.relpath(path, HERE))

# ---- sitemap.xml + robots.txt (final URLs, ready for launch) ----
indexable = [p for p in pages if rel_dir(p) not in ALWAYS_NOINDEX]
urls = []
for p in sorted(indexable, key=clean_url):
    mtime = datetime.date.fromtimestamp(os.path.getmtime(p)).isoformat()
    urls.append(f"  <url><loc>{clean_url(p)}</loc><lastmod>{mtime}</lastmod></url>")
sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(urls) + "\n</urlset>\n")
with open(os.path.join(HERE, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write(sitemap)

robots_txt = (("User-agent: *\nDisallow:\n" if LIVE else "User-agent: *\nDisallow: /\n")
              + f"\nSitemap: {SITE}/sitemap.xml\n")
with open(os.path.join(HERE, "robots.txt"), "w", encoding="utf-8") as f:
    f.write(robots_txt)

print(f"MODE: {'LIVE (indexable)' if LIVE else 'PREVIEW (noindex)'}  base={SITE}")
print(f"updated:   {len(changed)}")
print(f"unchanged: {len(skipped)}")
print(f"sitemap:   {len(urls)} urls -> sitemap.xml")
print(f"robots.txt written ({'allow' if LIVE else 'disallow all'})")
if nomarker:
    print("MISSING MARKERS:")
    for m in nomarker: print("  !", m)
