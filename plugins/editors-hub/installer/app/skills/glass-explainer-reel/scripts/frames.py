#!/usr/bin/env python3
"""Gridded stills of the footage, for reading where the speaker's head is.   frames.py <slug> <t> [<t> ...]
Uses the rendered cut when there is one (times = cut timeline), otherwise the raw file. Grid labels are SOURCE pixels:
read off the top of the head/hair (or hat), the chin and the centre of the face, and put them in <work>/layout.json."""
import os, sys, tempfile
from PIL import Image, ImageDraw
from common import work, load, grab, label_font
W = work(sys.argv[1]); M = load(W, "meta.json"); src = M.get("cut") or M["src"]; os.makedirs(f"{W}/frames", exist_ok=True)
for t in map(float, sys.argv[2:]):
    p = tempfile.mktemp(suffix=".jpg"); grab(src, t, p); im = Image.open(p).convert("RGB"); os.remove(p)
    w, h = im.size; d = ImageDraw.Draw(im, "RGBA"); f = label_font(max(18, w // 70)); n = 16 if w >= h else 9
    for i in range(1, n):
        x = w * i // n; d.line([(x, 0), (x, h)], fill=(255, 255, 255, 110), width=max(1, w // 900)); d.text((x + 6, 6), str(x), fill=(255, 230, 0, 255), font=f)
    for i in range(1, 20):
        y = h * i // 20; d.line([(0, y), (w, y)], fill=(255, 255, 255, 110), width=max(1, w // 900)); d.text((6, y + 6), str(y), fill=(255, 230, 0, 255), font=f)
    s = 1920 / max(w, h); im = im.resize((int(w * s), int(h * s))) if s < 1 else im
    o = f"{W}/frames/f_{t:07.2f}.jpg"; im.save(o, quality=88); print(o, f"(source is {w}x{h})")
