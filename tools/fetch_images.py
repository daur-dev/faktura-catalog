# -*- coding: utf-8 -*-
"""
Build-time helper #2: fetch license-clean, topically-relevant photos from
Wikimedia Commons, center-crop to the exact catalog aspect ratios, and compress
to JPG within weight budgets. Records license/attribution to img/_gen/credits.json.

Re-runnable: edit MANIFEST / OVERRIDES and run again. Pass item names as argv to
fetch only those (pass 2 fixes).
"""
import urllib.request, urllib.parse, json, io, os, re, sys, time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "img")
GEN = os.path.join(IMG, "_gen")
os.makedirs(GEN, exist_ok=True)
from PIL import Image

UA = "catalog-otdelka-portfolio-demo/1.0 (https://example.com; daurjoy88@gmail.com)"
API = "https://commons.wikimedia.org/w/api.php"

# name -> (target_w, target_h, max_kb, search_term)
MANIFEST = {
    # --- products 800x600 ---
    "oboi-1":        (800, 600, 200, "textured white wallpaper"),
    "oboi-2":        (800, 600, 200, "damask wallpaper pattern"),
    "oboi-3":        (800, 600, 200, "vintage floral wallpaper"),
    "oboi-4":        (800, 600, 200, "botanical wallpaper"),
    "pol-1":         (800, 600, 200, "laminate flooring texture"),
    "pol-2":         (800, 600, 200, "vinyl plank flooring"),
    "pol-3":         (800, 600, 200, "linoleum flooring"),
    "pol-4":         (800, 600, 200, "oak parquet flooring"),
    "plitka-1":      (800, 600, 200, "white marble tile texture"),
    "plitka-2":      (800, 600, 200, "white ceramic tiles texture"),
    "plitka-3":      (800, 600, 200, "glass mosaic tile"),
    "plitka-4":      (800, 600, 200, "grey floor tiles texture"),
    "kraska-1":      (800, 600, 200, "paint roller painting wall"),
    "kraska-2":      (800, 600, 200, "house facade painting"),
    "kraska-3":      (800, 600, 200, "paint bucket"),
    "kraska-4":      (800, 600, 200, "open paint can"),
    "shtukaturka-1": (800, 600, 200, "plaster wall texture"),
    "shtukaturka-2": (800, 600, 200, "textured stucco wall"),
    "shtukaturka-3": (800, 600, 200, "concrete wall texture"),
    "shtukaturka-4": (800, 600, 200, "travertine stone texture"),
    "potolok-1":     (800, 600, 200, "drywall plasterboard"),
    "potolok-2":     (800, 600, 200, "steel stud framing construction"),
    "potolok-3":     (800, 600, 200, "plastering wall"),
    "potolok-4":     (800, 600, 200, "tile adhesive trowel"),
    # --- category thumbs 640x400 ---
    "cat-oboi":        (640, 400, 150, "wallpaper pattern"),
    "cat-pol":         (640, 400, 150, "wooden parquet floor"),
    "cat-plitka":      (640, 400, 150, "ceramic tiles wall"),
    "cat-kraska":      (640, 400, 150, "paint rollers and cans"),
    "cat-shtukaturka": (640, 400, 150, "decorative plaster wall"),
    "cat-potolok":     (640, 400, 150, "ceiling drywall construction"),
    # --- hero 1600x900 ---
    "hero":            (1600, 900, 400, "modern living room interior"),
}

# name -> candidate index to use (0 = top search hit). Tweak in pass 2.
OVERRIDES = {"plitka-4": 2, "kraska-4": 3, "potolok-3": 1, "cat-kraska": 1, "shtukaturka-3": 2}


def api_get(params):
    params = dict(params); params["format"] = "json"
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r)


def strip_html(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()


def search_images(term, limit=8, thumbw=1400):
    d = api_get({
        "action": "query", "generator": "search", "gsrsearch": term,
        "gsrnamespace": 6, "gsrlimit": limit, "prop": "imageinfo",
        "iiprop": "url|mime|size|extmetadata", "iiurlwidth": thumbw,
    })
    pages = d.get("query", {}).get("pages", {})
    items = sorted(pages.values(), key=lambda p: p.get("index", 999))
    out = []
    for p in items:
        ii = (p.get("imageinfo") or [{}])[0]
        if ii.get("mime") not in ("image/jpeg", "image/png"):
            continue
        if not ii.get("thumburl"):
            continue
        em = ii.get("extmetadata", {}) or {}
        out.append({
            "title": p.get("title"),
            "thumb": ii.get("thumburl"),
            "descurl": ii.get("descriptionurl"),
            "license": strip_html(em.get("LicenseShortName", {}).get("value", "")),
            "artist": strip_html(em.get("Artist", {}).get("value", "")),
            "w": ii.get("width"), "h": ii.get("height"),
        })
    return out


def download(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except Exception as e:
            last = e; time.sleep(1.5 * (i + 1))
    raise last


def process(data, out_path, tw, th, max_kb):
    im = Image.open(io.BytesIO(data)).convert("RGB")
    target = tw / th
    w, h = im.size
    cur = w / h
    if cur > target:
        nw = int(round(h * target)); x = (w - nw) // 2; im = im.crop((x, 0, x + nw, h))
    else:
        nh = int(round(w / target)); y = (h - nh) // 2; im = im.crop((0, y, w, y + nh))
    im = im.resize((tw, th), Image.LANCZOS)
    q = 90
    while True:
        im.save(out_path, "JPEG", quality=q, optimize=True, progressive=True)
        if os.path.getsize(out_path) <= max_kb * 1024 or q <= 50:
            break
        q -= 6
    return os.path.getsize(out_path), q


def main():
    only = set(sys.argv[1:])
    credits_path = os.path.join(GEN, "credits.json")
    credits = {}
    if os.path.exists(credits_path):
        credits = json.load(open(credits_path, encoding="utf-8"))

    names = [n for n in MANIFEST if not only or n in only]
    for name in names:
        tw, th, max_kb, term = MANIFEST[name]
        idx = OVERRIDES.get(name, 0)
        try:
            cands = search_images(term)
        except Exception as e:
            print("!! search failed", name, term, e); continue
        if not cands:
            print("!! NO CANDIDATES", name, "|", term); continue
        if idx >= len(cands):
            idx = 0
        c = cands[idx]
        try:
            data = download(c["thumb"])
            size, q = process(data, os.path.join(IMG, name + ".jpg"), tw, th, max_kb)
        except Exception as e:
            print("!! fetch/process failed", name, e); continue
        credits[name] = {
            "term": term, "idx": idx, "title": c["title"], "descurl": c["descurl"],
            "license": c["license"], "artist": c["artist"],
        }
        json.dump(credits, open(credits_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("OK  %-14s %5dKB q%-2d  %-18s  [%s] %s" % (
            name, size // 1024, q, term, c["license"], c["title"][:48]))
        time.sleep(0.4)

    print("\ncredits ->", os.path.relpath(credits_path, ROOT))


if __name__ == "__main__":
    main()
