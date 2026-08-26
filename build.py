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
import re, os, glob, datetime, json, html as _html

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

SEG_NAMES = {"webinars": "On-Demand Webinars"}   # friendly names for path segments

def breadcrumb_jsonld(path, leaf):
    d = rel_dir(path)
    if not d:
        return None                                  # no breadcrumb on home
    segs = d.split("/")
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"}]
    for i, seg in enumerate(segs):
        last = (i == len(segs) - 1)
        name = leaf if last else SEG_NAMES.get(seg, seg.replace("-", " ").title())
        items.append({"@type": "ListItem", "position": i + 2, "name": name,
                      "item": SITE + "/" + "/".join(segs[:i + 1]) + "/"})
    obj = {"@context": "https://schema.org", "@type": "BreadcrumbList",
           "itemListElement": items}
    return '<script type="application/ld+json">' + json.dumps(obj, separators=(",", ":")) + "</script>"

MONTHS = {m: i + 1 for i, m in enumerate(
    ["January","February","March","April","May","June","July","August",
     "September","October","November","December"])}

def _ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, separators=(",", ":")) + "</script>"

def webinar_schema(path, html, leaf):
    """VideoObject for recorded (Vimeo) webinars, EducationEvent for upcoming ones."""
    d = rel_dir(path)
    if not d.startswith("webinars/"):
        return None
    dm = re.search(r'<meta name="description" content="([^"]*)"', html)
    desc = _html.unescape(dm.group(1)) if dm else leaf
    thumb = f"{SITE}/assets/og/{d.replace('/', '-')}.png"
    vid = re.search(r'player\.vimeo\.com/video/(\d+)', html)
    if vid:
        return _ld({"@context": "https://schema.org", "@type": "VideoObject",
            "name": leaf, "description": desc, "thumbnailUrl": thumb,
            "embedUrl": f"https://player.vimeo.com/video/{vid.group(1)}",
            "publisher": {"@type": "Organization", "name": "Save a Leg, Save a Life Foundation",
                          "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/logo.png"}}})
    dt = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(\d{4})', html)
    if dt:
        tm = re.search(r'(\d{1,2}):(\d{2})\s*(AM|PM)\s*ET', html)
        hh, mm = 12, 0
        if tm:
            hh, mm = int(tm.group(1)), int(tm.group(2))
            if tm.group(3) == "PM" and hh != 12: hh += 12
            if tm.group(3) == "AM" and hh == 12: hh = 0
        start = f"{int(dt.group(3)):04d}-{MONTHS[dt.group(1)]:02d}-{int(dt.group(2)):02d}T{hh:02d}:{mm:02d}:00-04:00"
        return _ld({"@context": "https://schema.org", "@type": "EducationEvent",
            "name": leaf, "description": desc, "startDate": start, "image": thumb,
            "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled",
            "location": {"@type": "VirtualLocation", "url": clean_url(path)},
            "organizer": {"@type": "Organization", "name": "Save a Leg, Save a Life Foundation", "url": SITE + "/"},
            "isAccessibleForFree": True})
    return None

def seo_block(path, leaf, extra=None):
    d = rel_dir(path)
    robots = "noindex, nofollow" if (d in ALWAYS_NOINDEX or not LIVE) else "index, follow"
    lines = [
        "  <!-- SEO:START -->",
        f'  <link rel="canonical" href="{clean_url(path)}">',
        f'  <meta name="robots" content="{robots}">',
        "  " + ORG_JSONLD,
    ]
    crumb = breadcrumb_jsonld(path, leaf)
    if crumb:
        lines.append("  " + crumb)
    if extra:
        lines.append("  " + extra)
    lines.append("  <!-- SEO:END -->")
    return "\n" + "\n".join(lines)

changed, skipped, nomarker, pages = [], [], [], []
for path in sorted(glob.glob(os.path.join(HERE, "**", "*.html"), recursive=True)):
    if os.sep + "partials" + os.sep in path:
        continue
    pages.append(path)
    html = read(path); orig = html
    b = base_for(path)

    # nav / footer  ({{HOME}} = clean link to site root: "./" at root, "../" per depth)
    home = b if b else "./"
    nav_block  = "<!-- NAV:START -->\n"    + nav_src.replace("{{HOME}}", home).replace("{{B}}", b)  + "\n<!-- NAV:END -->"
    foot_block = "<!-- FOOTER:START -->\n" + foot_src.replace("{{HOME}}", home).replace("{{B}}", b) + "\n<!-- FOOTER:END -->"
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
    tm = re.search(r"<title>(.*?)</title>", html, re.S)
    leaf = _html.unescape(re.split(r"\s*\|\s*", tm.group(1).strip())[0]) if tm else "Page"
    wschema = webinar_schema(path, html, leaf)
    html = re.sub(r"(</title>)", lambda m: m.group(1) + seo_block(path, leaf, wschema), html, count=1)

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
