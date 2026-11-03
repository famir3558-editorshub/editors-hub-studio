#!/usr/bin/env python3
"""Step 10 - final visual and audio review of a render.   10_review.py <slug> ["<render.mp4>"]   (default: the draft)
Prints PASS / FAIL lines for the file and the sound, and writes contact sheets into <project>/review/ that you must
open and read (see "Final visual and audio review" in SKILL.md for what to look for on each):
  ends.jpg       first and last frames            switches_NN.jpg  the frame before and after every mode switch
  captions_NN.jpg one tile per caption            beats_NN.jpg     every heading / graphic just after it lands
  cuts_NN.jpg    either side of every big jump cut"""
import json, os, subprocess, sys, tempfile, wave
import numpy as np
from PIL import Image
from common import PROJECTS_ROOT, work, load, grab, sheet
slug = sys.argv[1]; W = work(slug); PJ = f"{PROJECTS_ROOT}/{slug}-glass"; P = json.load(open(f"{PJ}/project.json")); B = json.load(open(f"{PJ}/beats.json"))
f = sys.argv[2] if len(sys.argv) > 2 else f"{PJ}/renders/draft.mp4"; R = f"{PJ}/review"; os.makedirs(R, exist_ok=True)
for old in os.listdir(R): os.remove(f"{R}/{old}")
ok = lambda c, msg: print(("PASS  " if c else "FAIL  ") + msg)
j = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", f]))
v = next(s for s in j["streams"] if s["codec_type"] == "video"); au = [s for s in j["streams"] if s["codec_type"] == "audio"]; dur = float(j["format"]["duration"])
ok(v["width"] == 1080 and v["height"] == 1920, f"frame {v['width']}x{v['height']} (must be 1080x1920)")
num, den = map(int, v["r_frame_rate"].split("/")); ok(abs(num / den - P["fps"]) < 0.02, f"frame rate {num / den:.3f} (source {P['fps']:.3f})")
ok(abs(dur - P["dur"]) < 0.1, f"length {dur:.2f}s (cut is {P['dur']:.2f}s)")
ok(bool(au), "has an audio track")
# ---- sound
tmp = tempfile.mktemp(suffix=".wav"); subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-vn", "-ac", "1", "-ar", "48000", tmp], check=True)
w = wave.open(tmp); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; os.remove(tmp)
env = lambda x: np.sqrt((x[: len(x) // 480 * 480].reshape(-1, 480) ** 2).mean(1))
e = env(a); loud = np.where(20 * np.log10(e + 1e-9) > -46)[0]
head, tail = loud[0] / 100, len(a) / 48000 - (loud[-1] + 1) / 100
ok(head < 0.25, f"first sound {head:.2f}s after the start (the speaker should be speaking at once)")
ok(tail < 0.35, f"{tail:.2f}s after the last sound (should end right after the last word)")
ok(tail > 0.02 or e[-1] < e.max() * 0.05, "last word is not cut off (the sound has died away at the end)")
peak = 20 * np.log10(np.abs(a).max() + 1e-9); ok(peak < -0.3, f"peak {peak:.1f} dBFS (no clipping)")
ln = subprocess.run(["ffmpeg", "-hide_banner", "-i", f, "-af", "loudnorm=print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
try:
    import re; I = float(re.search(r'"input_i"\s*:\s*"(-?[\d.]+)"', ln).group(1)); print(f"INFO  loudness {I:.1f} LUFS (Instagram/TikTok normalise to about -14; -16 to -12 is fine. Outside that, tell the creator rather than changing the sound)")
except Exception: print("INFO  could not read loudness")
if os.path.exists(f"{W}/edit.wav"):
    w = wave.open(f"{W}/edit.wav"); b = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; eb = env(b); n = min(len(e), len(eb))
    lags = range(-30, 31); best = max(lags, key=lambda L: float(np.dot(e[max(0, L): n + min(0, L)], eb[max(0, -L): n - max(0, L)])))
    ok(abs(best) <= 2, f"sound lines up with the verified cut (offset {best * 10} ms)")
    ok(abs(len(a) - len(b)) / 48000 < 0.1, f"sound length matches the verified cut ({len(a) / 48000:.2f}s vs {len(b) / 48000:.2f}s)")
# ---- sheets
def tile(t, lab): p = tempfile.mktemp(suffix=".jpg"); grab(f, min(max(0, t), dur - 2.5 / P["fps"]), p, (360, 640)); im = Image.open(p).convert("RGB"); os.remove(p); return im, lab
def sheets(name, tiles, cols=8, per=32):
    for k in range(0, len(tiles), per): sheet(tiles[k:k + per], f"{R}/{name}_{k // per + 1:02d}.jpg" if len(tiles) > per else f"{R}/{name}.jpg", cols, 270)
fd = 1 / P["fps"]
sheets("ends", [tile(0, "first frame"), tile(0.5, "0.5s"), tile(dur - 0.5, "end - 0.5s"), tile(dur - fd, "last frame")], 4)
sw = [x["t"] for x in B["beats"] if x["kind"] == "switch"]
if sw: sheets("switches", [t_ for s in sw for t_ in (tile(s - fd * 1.5, f"{s:.2f} before"), tile(s + fd * 1.5, f"{s:.2f} after"))])
caps = load(PJ, "captions.json", [])
txt = {round(c["start"], 2): "".join(p["t"] for p in c["parts"]).strip() for c in caps}
sheets("captions", [tile((a + b_) / 2, f"{a:.2f} {m} {next((v_ for k_, v_ in txt.items() if abs(k_ - a) < 0.02), '(cont.)')[:18]}") for a, b_, m in B["captions"]])
bt = [x for x in B["beats"] if x["kind"] != "switch"]
if bt: sheets("beats", [tile(x["t"] + 0.1, f"{x['t']:.2f} {x.get('text', x.get('id', ''))[:20]}") for x in bt])
big = [c for c in load(W, "cuts.json", []) if c["big"]]
if big: sheets("cuts", [t_ for c in big for t_ in (tile(c["t"] - fd * 1.5, f"{c['t']:.2f} before"), tile(c["t"] + fd * 1.5, f"{c['t']:.2f} after"))])
print(f"\nsheets in {R}: " + ", ".join(sorted(os.listdir(R))) + "\nOpen every one with Read and go through the review checklist in SKILL.md.")
