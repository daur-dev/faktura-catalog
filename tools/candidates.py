# -*- coding: utf-8 -*-
"""Probe several search terms; for each, montage top-N candidate thumbnails with
index labels so we can choose the best (term, idx) before the final fetch."""
import urllib.request, urllib.parse, json, io, os, sys
from PIL import Image, ImageDraw

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "catalog-otdelka-portfolio-demo/1.0 (https://example.com; daurjoy88@gmail.com)"
API = "https://commons.wikimedia.org/w/api.php"

# item -> list of candidate terms to try (concatenated, indices continue across terms)
PROBES = {
    "plitka-2":      ["white ceramic tiles texture"],
    "kraska-4":      ["open paint can"],
    "shtukaturka-1": ["plaster wall texture"],
    "shtukaturka-3": ["concrete wall texture"],
    "cat-oboi":      ["wallpaper pattern"],
}
N_PER_TERM = 5


def api_get(params):
    params = dict(params); params["format"] = "json"
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r)


def search(term, limit, thumbw=360):
    d = api_get({"action": "query", "generator": "search", "gsrsearch": term,
                 "gsrnamespace": 6, "gsrlimit": limit, "prop": "imageinfo",
                 "iiprop": "url|mime", "iiurlwidth": thumbw})
    pages = d.get("query", {}).get("pages", {})
    items = sorted(pages.values(), key=lambda p: p.get("index", 999))
    res = []
    for p in items:
        ii = (p.get("imageinfo") or [{}])[0]
        if ii.get("mime") in ("image/jpeg", "image/png") and ii.get("thumburl"):
            res.append(ii["thumburl"])
    return res


def dl(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


items = sys.argv[1:] or list(PROBES.keys())
CW, CH, LAB = 240, 170, 18
rows = []
for item in items:
    thumbs = []
    for term in PROBES[item][:1]:
        try:
            thumbs += [(term, u) for u in search(term, N_PER_TERM)]
        except Exception as e:
            print("search fail", item, term, e)
    thumbs = thumbs[:5]
    row = Image.new("RGB", (len(thumbs) * CW, CH + LAB), (235, 235, 235))
    d = ImageDraw.Draw(row)
    for i, (term, u) in enumerate(thumbs):
        x = i * CW
        d.rectangle([x, 0, x + CW, LAB], fill=(20, 20, 20))
        d.text((x + 3, 4), "%s #%d" % (item, i), fill=(255, 255, 255))
        try:
            im = Image.open(io.BytesIO(dl(u))).convert("RGB"); im.thumbnail((CW - 4, CH - 4))
            row.paste(im, (x + 2, LAB + 2))
        except Exception:
            d.text((x + 6, LAB + 30), "ERR", fill=(200, 0, 0))
    rows.append(row)
    print("probed", item, "->", len(thumbs), "candidates")

W = max(r.width for r in rows)
H = sum(r.height for r in rows)
sheet = Image.new("RGB", (W, H), (255, 255, 255))
y = 0
for r in rows:
    sheet.paste(r, (0, y)); y += r.height
out = os.path.join(ROOT, "screenshots", "_candidates.png")
sheet.save(out)
print("saved", out, sheet.size)
