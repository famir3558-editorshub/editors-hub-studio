#!/usr/bin/env python3
"""Frames from the cut with a pixel grid, for choosing where text can sit around the speaker.   frames.py <slug> <t> [<t> ...]
Writes <work>/frames/f_<t>.jpg. Grid labels are in output-frame pixels: use them for a text card's "anchor" and "width"."""
import os, sys
from PIL import ImageDraw
from common import work, load, base_frame, canvas, label_font
W = work(sys.argv[1]); M = load(W, "meta.json"); plan = load(W, "plan.json", {}); os.makedirs(f"{W}/frames", exist_ok=True)
CW, CH = canvas(M, plan)
for t in map(float, sys.argv[2:]):
    im = base_frame(M, plan, t); d = ImageDraw.Draw(im, "RGBA"); f = label_font(max(18, CW // 70))
    for i in range(1, 10):
        x, y = CW * i // 10, CH * i // 10
        d.line([(x, 0), (x, CH)], fill=(255, 255, 255, 110), width=max(1, CW // 900)); d.line([(0, y), (CW, y)], fill=(255, 255, 255, 110), width=max(1, CW // 900))
        d.text((x + 6, 6), str(x), fill=(255, 230, 0, 255), font=f); d.text((6, y + 6), str(y), fill=(255, 230, 0, 255), font=f)
    if max(CW, CH) > 1920:
        s = 1920 / max(CW, CH); im = im.resize((int(CW * s), int(CH * s)))
    p = f"{W}/frames/f_{t:07.2f}.jpg"; im.save(p, quality=88); print(p, f"(frame is {CW}x{CH})")
