# -*- coding: utf-8 -*-
"""Build a labeled contact sheet of given img/ files for visual QA."""
import os, sys, math
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "img")

names = sys.argv[1:-1] if len(sys.argv) > 2 else None
out = sys.argv[-1] if len(sys.argv) > 1 else os.path.join(ROOT, "screenshots", "_montage.png")

if not names:
    order = ["oboi-1","oboi-2","oboi-3","oboi-4","pol-1","pol-2","pol-3","pol-4",
             "plitka-1","plitka-2","plitka-3","plitka-4","kraska-1","kraska-2","kraska-3","kraska-4",
             "shtukaturka-1","shtukaturka-2","shtukaturka-3","shtukaturka-4",
             "potolok-1","potolok-2","potolok-3","potolok-4",
             "cat-oboi","cat-pol","cat-plitka","cat-kraska","cat-shtukaturka","cat-potolok","hero"]
    names = order

CW, CH, LAB = 250, 188, 20
cols = 4
rows = math.ceil(len(names) / cols)
sheet = Image.new("RGB", (cols * CW, rows * (CH + LAB)), (240, 240, 240))
d = ImageDraw.Draw(sheet)
for i, name in enumerate(names):
    cx, cy = (i % cols) * CW, (i // cols) * (CH + LAB)
    d.rectangle([cx, cy, cx + CW, cy + LAB], fill=(30, 30, 30))
    d.text((cx + 4, cy + 5), name, fill=(255, 255, 255))
    p = os.path.join(IMG, name + ".jpg")
    if os.path.exists(p):
        im = Image.open(p).convert("RGB")
        im.thumbnail((CW - 4, CH - 4))
        sheet.paste(im, (cx + 2, cy + LAB + 2))
    else:
        d.text((cx + 8, cy + LAB + 40), "MISSING", fill=(200, 0, 0))
sheet.save(out)
print("saved", out, sheet.size)
