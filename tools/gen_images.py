# -*- coding: utf-8 -*-
"""
Build-time helper: generates clean, deliberate SVG placeholder images for the
"Фактура" demo catalog. Output goes to ../img. The site itself ships only the
generated .svg files and has no dependency on this script.

Each placeholder is a category-themed gradient + material texture + a material
icon + a small "образец" / brand tag, so it reads as an intentional design-system
swatch (not a broken image) and clearly signals "replace with the client's photo".
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "img")
os.makedirs(IMG, exist_ok=True)

# --- category themes ---------------------------------------------------------
# key: (gradient dark, gradient light, label)
THEMES = {
    "oboi":        ("#b8502f", "#e69069", "Обои"),
    "pol":         ("#8a5a2b", "#c79256", "Напольные покрытия"),
    "plitka":      ("#2b6f6a", "#54a89f", "Плитка и керамогранит"),
    "kraska":      ("#3a5a78", "#7398bb", "Краски и грунты"),
    "shtukaturka": ("#796d60", "#ab9c8b", "Декоративная штукатурка"),
    "potolok":     ("#566170", "#8b97a6", "Потолки и смеси"),
}

# --- material icons (drawn in a 100x100 box, white shapes) --------------------

def icon_oboi():
    # a wallpaper roll: vertical sheet + curled top
    return """
      <rect x="34" y="26" width="32" height="56" rx="5"/>
      <ellipse cx="50" cy="26" rx="16" ry="6"/>
      <path d="M34 70 q16 12 32 0 v8 q-16 12 -32 0 z" opacity="0.65"/>
    """

def icon_pol():
    # stacked floor planks, offset
    return """
      <rect x="18" y="34" width="64" height="11" rx="3"/>
      <rect x="26" y="49" width="64" height="11" rx="3" transform="translate(-8 0)"/>
      <rect x="18" y="64" width="64" height="11" rx="3"/>
      <line x1="48" y1="34" x2="48" y2="45" stroke-width="2" opacity="0.45"/>
      <line x1="40" y1="64" x2="40" y2="75" stroke-width="2" opacity="0.45"/>
    """

def icon_plitka():
    # 2x2 grid of tiles
    g = ""
    for r in range(2):
        for c in range(2):
            g += '<rect x="%d" y="%d" width="26" height="26" rx="4"/>' % (28 + c * 30, 28 + r * 30)
    return g

def icon_kraska():
    # paint roller: drum + neck + handle
    return """
      <rect x="26" y="26" width="40" height="16" rx="4"/>
      <rect x="62" y="31" width="10" height="6" rx="2" opacity="0.7"/>
      <rect x="44" y="42" width="4" height="12" opacity="0.85"/>
      <path d="M40 54 h12 a3 3 0 0 1 3 3 v17 a5 5 0 0 1 -5 5 h-8 a5 5 0 0 1 -5 -5 v-17 a3 3 0 0 1 3 -3 z" opacity="0.85"/>
    """

def icon_shtukaturka():
    # trowel: blade + handle
    return """
      <path d="M20 40 h52 a3 3 0 0 1 3 3 v6 a3 3 0 0 1 -3 3 h-46 z"/>
      <rect x="44" y="26" width="6" height="16" rx="2" opacity="0.85"/>
      <path d="M40 22 h14 a4 4 0 0 1 4 4 v2 h-22 v-2 a4 4 0 0 1 4 -4 z" opacity="0.85"/>
    """

def icon_potolok():
    # suspended ceiling / panel grid 3x2
    g = '<rect x="20" y="28" width="60" height="44" rx="4" fill="none" stroke="white" stroke-width="4"/>'
    g += '<line x1="40" y1="28" x2="40" y2="72" stroke="white" stroke-width="3" opacity="0.8"/>'
    g += '<line x1="60" y1="28" x2="60" y2="72" stroke="white" stroke-width="3" opacity="0.8"/>'
    g += '<line x1="20" y1="50" x2="80" y2="50" stroke="white" stroke-width="3" opacity="0.8"/>'
    return g

ICONS = {
    "oboi": icon_oboi,
    "pol": icon_pol,
    "plitka": icon_plitka,
    "kraska": icon_kraska,
    "shtukaturka": icon_shtukaturka,
    "potolok": icon_potolok,
}

# --- texture patterns (white, low opacity, tiled) ----------------------------

def pattern(key, pid):
    """Return (defs, fill_id) for a category texture pattern."""
    pid = "pat_%s" % pid
    if key == "oboi":  # vertical wavy stripes
        body = '<path d="M20 0 C8 25 32 50 20 75 S8 100 20 120" fill="none" stroke="#fff" stroke-width="3"/>'
        p = '<pattern id="%s" width="40" height="120" patternUnits="userSpaceOnUse">%s</pattern>' % (pid, body)
    elif key == "pol":  # horizontal plank seams
        body = '<line x1="0" y1="0" x2="120" y2="0" stroke="#fff" stroke-width="2"/><line x1="60" y1="0" x2="60" y2="36" stroke="#fff" stroke-width="2"/>'
        p = '<pattern id="%s" width="120" height="36" patternUnits="userSpaceOnUse">%s</pattern>' % (pid, body)
    elif key == "plitka":  # tile grid
        body = '<rect x="0" y="0" width="56" height="56" fill="none" stroke="#fff" stroke-width="2"/>'
        p = '<pattern id="%s" width="56" height="56" patternUnits="userSpaceOnUse">%s</pattern>' % (pid, body)
    elif key == "kraska":  # scattered dots / drips
        body = '<circle cx="12" cy="14" r="3" fill="#fff"/><circle cx="40" cy="34" r="2" fill="#fff"/><circle cx="26" cy="50" r="2.5" fill="#fff"/>'
        p = '<pattern id="%s" width="56" height="64" patternUnits="userSpaceOnUse">%s</pattern>' % (pid, body)
    elif key == "shtukaturka":  # speckle / short strokes
        body = ('<g stroke="#fff" stroke-width="2" stroke-linecap="round">'
                '<line x1="6" y1="8" x2="12" y2="6"/><line x1="30" y1="18" x2="36" y2="16"/>'
                '<line x1="18" y1="34" x2="24" y2="32"/><line x1="42" y1="42" x2="48" y2="40"/>'
                '<line x1="8" y1="52" x2="14" y2="50"/></g>')
        p = '<pattern id="%s" width="56" height="60" patternUnits="userSpaceOnUse">%s</pattern>' % (pid, body)
    else:  # potolok: dotted grid
        body = '<circle cx="4" cy="4" r="2" fill="#fff"/>'
        p = '<pattern id="%s" width="34" height="34" patternUnits="userSpaceOnUse">%s</pattern>' % (pid, body)
    return p, pid


def svg(w, h, key, idx, with_brand=True, tag="образец", big_icon=True):
    dark, light, label = THEMES[key]
    angle = 25 + (idx * 17) % 60  # vary gradient angle per item
    # gradient coords from angle
    import math
    a = math.radians(angle)
    x2 = round(50 + 50 * math.cos(a), 2)
    y2 = round(50 + 50 * math.sin(a), 2)
    pat, pid = pattern(key, "%s%d" % (key, idx))
    icon = ICONS[key]()
    iscale = (min(w, h) * 0.0042)  # icon ~ 42% of min dim (icon box is 100)
    ix = w / 2 - 50 * iscale
    iy = h / 2 - 50 * iscale
    parts = []
    parts.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img">' % (w, h, w, h))
    parts.append('<defs>')
    parts.append('<linearGradient id="g_%s%d" x1="0%%" y1="0%%" x2="%s%%" y2="%s%%">' % (key, idx, x2, y2))
    parts.append('<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (dark, light))
    parts.append(pat)
    parts.append('</defs>')
    parts.append('<rect width="%d" height="%d" fill="url(#g_%s%d)"/>' % (w, h, key, idx))
    parts.append('<rect width="%d" height="%d" fill="url(#%s)" opacity="0.16"/>' % (w, h, pid))
    # soft vignette
    parts.append('<rect width="%d" height="%d" fill="#000" opacity="0.06"/>' % (w, h))
    if big_icon:
        # soft disc behind icon
        parts.append('<circle cx="%d" cy="%d" r="%d" fill="#fff" opacity="0.10"/>' % (w / 2, h / 2, int(54 * iscale)))
        parts.append('<g transform="translate(%.1f %.1f) scale(%.3f)" fill="#fff" fill-opacity="0.95" stroke="none">%s</g>' % (ix, iy, iscale, icon))
    if tag:
        parts.append('<g font-family="Manrope, Inter, Arial, sans-serif">')
        # tag pill bottom-left
        parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="#000" opacity="0.28"/>' % (int(w*0.04), int(h-h*0.13), int(w*0.30), int(h*0.085), int(h*0.04)))
        parts.append('<text x="%d" y="%d" fill="#fff" font-size="%d" font-weight="600" opacity="0.95">%s</text>' % (int(w*0.075), int(h-h*0.066), int(h*0.05), tag))
        if with_brand:
            parts.append('<text x="%d" y="%d" text-anchor="end" fill="#fff" font-size="%d" font-weight="800" letter-spacing="1" opacity="0.85">ФАКТУРА</text>' % (int(w-w*0.04), int(h-h*0.066), int(h*0.05)))
        parts.append('</g>')
    parts.append('</svg>')
    return "\n".join(parts)


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", os.path.relpath(path, ROOT))


# --- product images: 4 per category ------------------------------------------
for key in THEMES:
    for n in range(1, 5):
        write(os.path.join(IMG, "%s-%d.svg" % (key, n)), svg(800, 600, key, n))
    # category thumbnail (square, icon-forward, no tag)
    write(os.path.join(IMG, "cat-%s.svg" % key), svg(640, 640, key, 7, with_brand=False, tag=None))


# --- hero --------------------------------------------------------------------
def hero():
    w, h = 1600, 900
    p = []
    p.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img">' % (w, h, w, h))
    p.append('<defs>')
    p.append('<linearGradient id="hg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1f2937"/><stop offset="0.55" stop-color="#16202c"/><stop offset="1" stop-color="#0d141d"/></linearGradient>')
    p.append('<pattern id="hgrid" width="64" height="64" patternUnits="userSpaceOnUse"><rect x="0" y="0" width="64" height="64" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.5"/></pattern>')
    p.append('</defs>')
    p.append('<rect width="%d" height="%d" fill="url(#hg)"/>' % (w, h))
    p.append('<rect width="%d" height="%d" fill="url(#hgrid)" opacity="0.05"/>' % (w, h))
    # overlapping translucent material swatches on the right
    cols = ["#c2410c", "#d97706", "#2b6f6a", "#3a5a78", "#ab9c8b"]
    import math
    for i, c in enumerate(cols):
        x = 980 + i * 120
        y = 180 + (i % 2) * 130 + i * 36
        p.append('<rect x="%d" y="%d" width="300" height="300" rx="28" fill="%s" opacity="%.2f" transform="rotate(%d %d %d)"/>' % (x, y, c, 0.55 - i*0.06, -12 + i*6, x+150, y+150))
    # warm accent glow
    p.append('<circle cx="1180" cy="300" r="360" fill="#d97706" opacity="0.10"/>')
    # subtle bottom fade for text safety
    p.append('<rect x="0" y="0" width="900" height="%d" fill="#0d141d" opacity="0.25"/>' % h)
    p.append('</svg>')
    return "\n".join(p)

write(os.path.join(IMG, "hero.svg"), hero())


# --- favicon -----------------------------------------------------------------
def favicon():
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">'
            '<rect width="64" height="64" rx="14" fill="#1f2937"/>'
            '<rect x="8" y="8" width="48" height="48" rx="10" fill="none" stroke="#d97706" stroke-width="3" opacity="0.55"/>'
            '<text x="32" y="44" text-anchor="middle" font-family="Manrope, Arial, sans-serif" font-size="38" font-weight="800" fill="#f8f7f4">Ф</text>'
            '</svg>')

write(os.path.join(IMG, "favicon.svg"), favicon())


# --- open graph card ---------------------------------------------------------
def og():
    w, h = 1200, 630
    p = []
    p.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h))
    p.append('<defs><linearGradient id="og" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1f2937"/><stop offset="1" stop-color="#0d141d"/></linearGradient></defs>')
    p.append('<rect width="%d" height="%d" fill="url(#og)"/>' % (w, h))
    for i, c in enumerate(["#c2410c", "#d97706", "#2b6f6a", "#3a5a78"]):
        p.append('<rect x="%d" y="470" width="80" height="80" rx="14" fill="%s" opacity="0.8"/>' % (90 + i*96, c))
    p.append('<text x="90" y="240" font-family="Manrope, Arial, sans-serif" font-size="92" font-weight="800" fill="#f8f7f4">Фактура</text>')
    p.append('<text x="94" y="320" font-family="Inter, Arial, sans-serif" font-size="40" fill="#d97706" font-weight="600">Отделочные материалы для вашего ремонта</text>')
    p.append('<text x="94" y="392" font-family="Inter, Arial, sans-serif" font-size="30" fill="#cbd5e1">Каталог · более 1000 позиций · доставка по городу</text>')
    p.append('</svg>')
    return "\n".join(p)

write(os.path.join(IMG, "og.svg"), og())

print("\nDone.")
