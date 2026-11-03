#!/usr/bin/env python3
"""Step 9 - check a render.   09_check.py <slug> ["<file>"]     (default: the last file 08_render.py wrote)
Pulls frames from the RENDERED file and lays them out on labelled contact sheets in <work>/check/. LOOK AT EVERY SHEET:
  captions_NN.jpg   one tile for EVERY caption (the part of the frame around it): is it there, readable, spelled right,
                    below the speaker's chin / in the lower half of the picture, and off their face and hands?
  stacks_NN.jpg     every stack, full frame, as each line lands and just before it clears, plus the frame after
  picture_NN.jpg    b-roll (frame before, first, middle, last, frame after), every visible big jump cut, first and last frame
Also measures the silence at the head and tail of the audio and compares the length with the plan."""
import glob, os, subprocess, sys, tempfile
from fractions import Fraction
import numpy as np
from PIL import Image
from common import work, load, probe, grab, sheet
W = work(sys.argv[1]); M = load(W, "meta.json"); plan = load(W, "plan.json", {}); f = sys.argv[2] if len(sys.argv) > 2 else M["last"]
P = probe(f); FPS = float(Fraction(M["fps"])); F = 1 / FPS; TOT = M["cut_dur"]; cuts = load(W, "cuts.json", []); L = load(W, "layer.json")
B = sorted(plan.get("broll", []), key=lambda b: b["at"]); out = f"{W}/check"; os.makedirs(out, exist_ok=True)
[os.remove(p) for p in glob.glob(f"{out}/*.jpg")]; tmp = tempfile.mkdtemp(); k = [0]
def shot(t, crop=None):
    k[0] += 1; p = f"{tmp}/{k[0]}.jpg"; grab(f, max(0, min(TOT - F, t)), p); im = Image.open(p).convert("RGB")
    if crop:
        s = im.height / 1920; im = im.crop((0, int(crop[0] * s), im.width, int(crop[1] * s)))
    return im
def sheets(name, tiles, cols, tw, per):
    for s in range(0, len(tiles), per):
        p = f"{out}/{name}_{s // per + 1:02d}.jpg"; sheet(tiles[s:s + per], p, cols, tw); print(p)
caps = []
for c in L["captions"]:
    t = (c["at"] + min(c["end"], c["at"] + 1.0)) / 2
    caps.append((shot(t, (560, 1560)), f"{c['at']:.2f} {c['t'][:26]}"))
sheets("captions", caps, 6, 320, 36)
st = []
for c in L["cards"]:
    for i, l in enumerate(c["lines"]):
        nxt = c["lines"][i + 1]["at"] if i + 1 < len(c["lines"]) else c["end"]
        st.append((shot(min(l["at"] + 0.4, (l["at"] + nxt) / 2 + 0.1)), f"{c['id']} line {i + 1} in"))
    st += [(shot(c["end"] - 3 * F), f"{c['id']} full, last frames"), (shot(c["end"] + 2 * F), f"{c['id']} cleared")]
if st:
    sheets("stacks", st, 5, 380, 15)
pic = [(shot(0), "first frame")]
for n, b in enumerate(B, 1):
    e = b["at"] + b["dur"]
    pic += [(shot(b["at"] - 2 * F), f"before b-roll {n}"), (shot(b["at"] + F), f"b-roll {n} first {b['at']:.2f}"), (shot(b["at"] + b["dur"] / 2), f"b-roll {n} mid"),
            (shot(e - 2 * F), f"b-roll {n} last"), (shot(e + F), f"after b-roll {n}")]
for j in cuts:
    if j["big"] and not any(b["at"] <= j["t"] <= b["at"] + b["dur"] for b in B):
        pic += [(shot(j["t"] - 2 * F), f"cut {j['t']:.2f} before"), (shot(j["t"] + F), f"cut {j['t']:.2f} after")]
pic.append((shot(TOT - 2 * F), "last frame")); sheets("picture", pic, 5, 380, 15)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768; h = 160; m = len(a) // h
r = 20 * np.log10(np.sqrt((a[:m * h].reshape(m, h) ** 2).mean(1)) + 1e-9); on = np.where(r > -40)[0]
print(f"\n{os.path.basename(f)}: {P['w']}x{P['h']} {P['fps']} fps, {P['dur']:.2f}s (plan {TOT:.2f}s)" + ("" if abs(P["dur"] - TOT) < 0.15 else "  <-- LENGTH MISMATCH")
      + ("" if P["h"] * 9 == P["w"] * 16 else "  <-- NOT 9:16"))
print(f"sound starts {on[0] / 100:.2f}s in and ends {P['dur'] - on[-1] / 100:.2f}s before the end (both should be under ~0.25s)")
print(f"{len(caps)} caption tiles, {len(L['cards'])} stacks. Read every sheet; compare the caption tiles with {W}/captions.txt.")
