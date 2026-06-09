# -*- coding: utf-8 -*-
"""Build Kwork portfolio upload assets from raw captures in screenshots/kwork/.
Outputs: cover.jpg (designed cover) + 01-hero / 02-catalog / 03-product / 04-mobile gallery JPGs."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = os.path.join(ROOT, "screenshots", "kwork")
F = "C:/Windows/Fonts/"


def font(name, size):
    return ImageFont.truetype(F + name, size)


def load(n):
    return Image.open(os.path.join(K, n)).convert("RGB")


def save_jpg(im, name, q=88, maxw=2560):
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    im.convert("RGB").save(os.path.join(K, name), "JPEG", quality=q, optimize=True, progressive=True)
    kb = os.path.getsize(os.path.join(K, name)) / 1024
    print("  %-16s %dx%d  %.0fKB" % (name, im.width, im.height, kb))


def rounded_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0], size[1]], radius=r, fill=255)
    return m


def shadow(size, r, blur, alpha=150, pad=80):
    s = Image.new("RGBA", (size[0] + pad * 2, size[1] + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    d.rounded_rectangle([pad, pad, pad + size[0], pad + size[1]], radius=r, fill=(0, 0, 0, alpha))
    return s.filter(ImageFilter.GaussianBlur(blur))


def browser(content, bw, radius=18):
    """Mac-style browser window around content image scaled to width bw."""
    bar = max(40, int(bw * 0.052))
    ch = round(content.height * bw / content.width)
    inner = content.resize((bw, ch), Image.LANCZOS)
    H = bar + ch
    win = Image.new("RGB", (bw, H), (255, 255, 255))
    win.paste(inner, (0, bar))
    d = ImageDraw.Draw(win)
    d.rectangle([0, 0, bw, bar], fill=(237, 235, 231))
    d.line([0, bar, bw, bar], fill=(214, 210, 202))
    cy = bar // 2
    for i, col in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
        d.ellipse([22 + i * 26, cy - 8, 22 + i * 26 + 16, cy + 8], fill=col)
    win.putalpha(rounded_mask((bw, H), radius))
    return win


def phone(content, pw, radius=46, bezel=12):
    iw = pw - bezel * 2
    ih = round(content.height * iw / content.width)
    inner = content.resize((iw, ih), Image.LANCZOS)
    inner.putalpha(rounded_mask((iw, ih), radius - bezel + 2))
    H = ih + bezel * 2
    body = Image.new("RGBA", (pw, H), (0, 0, 0, 0))
    ImageDraw.Draw(body).rounded_rectangle([0, 0, pw, H], radius=radius, fill=(12, 16, 22, 255))
    body.alpha_composite(inner, (bezel, bezel))
    # notch
    nd = ImageDraw.Draw(body)
    nw = pw // 3
    nd.rounded_rectangle([pw // 2 - nw // 2, bezel + 4, pw // 2 + nw // 2, bezel + 22], radius=9, fill=(12, 16, 22, 255))
    return body


def vgrad(w, h, top, bot):
    g = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        g.putpixel((0, y), tuple(round(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return g.resize((w, h))


def text_w(d, s, fnt):
    b = d.textbbox((0, 0), s, font=fnt)
    return b[2] - b[0]


# ---------------- gallery (plain hi-res) ----------------
print("gallery:")
hero = load("cap-hero.png")
save_jpg(hero, "01-hero.jpg")

cat = load("cap-cat.png")  # 2560x7700, sf2; catalog head ~2078*2=4156, 2nd row bottom ~3729*2=7458
save_jpg(cat.crop((0, 4090, cat.width, 7180)), "02-catalog.jpg")

modal = load("cap-modal.png")
save_jpg(modal, "03-product.jpg")

# ---------------- 04 mobile (two phones on brand bg) ----------------
print("mobile gallery:")
mhome = load("cap-mhome.png")                 # 1170x2532 full home
mcat_full = load("cap-mcat.png")              # 780x9200, catalog band ~3752*2=7504..
mcat = mcat_full.crop((0, 7360, 780, 9100))   # catalog heading + chips + card

W, H = 1920, 1280
bg = vgrad(W, H, (32, 41, 53), (15, 22, 31))
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(glow).ellipse([W - 760, -260, W + 200, 520], fill=(217, 119, 6, 46))
bg = Image.alpha_composite(bg.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(120)))

ph = phone(mhome, 470)
pc = phone(mcat, 470)
for img, x, y in [(pc, 1090, 150), (ph, 560, 230)]:
    sh = shadow(img.size, 46, 40, 150)
    bg.alpha_composite(sh, (x - 80, y - 60))
    bg.alpha_composite(img, (x, y))

d = ImageDraw.Draw(bg)
d.text((120, 250), "АДАПТИВ", font=font("seguisb.ttf", 30), fill=(247, 183, 120))
d.text((120, 300), "Один сайт —\nтелефон, планшет,\nдесктоп", font=font("segoeuib.ttf", 70), fill=(255, 255, 255), spacing=10)
d.text((122, 560), "Меню-бургер, сетка 1→2→3 колонки,\nбез горизонтальной прокрутки.", font=font("segoeui.ttf", 30), fill=(197, 205, 214), spacing=8)
save_jpg(bg, "04-mobile.jpg", maxw=1920)

# ---------------- cover ----------------
print("cover:")
W, H = 1920, 1280
bg = vgrad(W, H, (33, 42, 54), (13, 19, 27))
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(glow).ellipse([W - 900, -320, W + 260, 560], fill=(217, 119, 6, 60))
bg = Image.alpha_composite(bg.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(140)))

# right-side mockups: desktop browser (catalog) + phone in front
cat_crop = cat.crop((0, 3980, cat.width, 7180))   # heading + ~2 rows
brow = browser(cat_crop, 980)
bx, by = 980, 250
bsh = shadow(brow.size, 18, 46, 165)
bg.alpha_composite(bsh, (bx - 80, by - 50))
bg.alpha_composite(brow, (bx, by))

pcover = phone(mhome, 360)
px, py = 1560, 470
psh = shadow(pcover.size, 46, 40, 170)
bg.alpha_composite(psh, (px - 80, py - 55))
bg.alpha_composite(pcover, (px, py))

d = ImageDraw.Draw(bg)
# logo mark + brand
d.rounded_rectangle([110, 96, 168, 154], radius=14, fill=(31, 41, 55))
d.rounded_rectangle([118, 104, 160, 146], radius=9, outline=(217, 119, 6), width=3)
ff = font("segoeuib.ttf", 34)
d.text((132, 104), "Ф", font=font("segoeuib.ttf", 34), fill=(248, 247, 244))
d.text((184, 108), "Фактура", font=font("segoeuib.ttf", 34), fill=(255, 255, 255))

d.text((112, 250), "ВЁРСТКА · HTML · CSS · JS", font=font("seguisb.ttf", 30), fill=(247, 183, 120))
d.text((110, 300), "Сайт-каталог\nотделочных\nматериалов", font=font("segoeuib.ttf", 86), fill=(255, 255, 255), spacing=8)
d.text((114, 612), "Адаптивная витрина под заявки: каталог\nс фильтром и живым поиском, карточки\nтоваров, модалки, форма заявки.",
       font=font("segoeui.ttf", 32), fill=(200, 208, 217), spacing=9)

# feature pills
pills = ["Фильтр + поиск", "Модалки", "Адаптив", "Без сборки"]
fx = 114
pf = font("seguisb.ttf", 26)
for p in pills:
    w = text_w(d, p, pf)
    d.rounded_rectangle([fx, 820, fx + w + 44, 872], radius=26, fill=(255, 255, 255, 18), outline=(255, 255, 255), width=1)
    d.text((fx + 22, 831), p, font=pf, fill=(229, 233, 238))
    fx += w + 44 + 16

save_jpg(bg, "cover.jpg", maxw=1920)
print("done")
