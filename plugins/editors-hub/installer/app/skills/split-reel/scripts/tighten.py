#!/usr/bin/env python3
"""OPTIONAL: only when the creator asks to tighten silences on their cut (they normally make the cuts themselves).
   tighten.py <cut.mp4> <out.mp4> [--gap 0.32]
Energy-based: speech = audio > -52 dBFS; every silence longer than --gap is cut down to ~0.21s
(0.14s tail after the word, 0.07s lead before the next). Frame-snapped, 8ms audio crossfades,
video re-encoded hevc_videotoolbox 40M (macOS). Prints what it removed. The default gap is the creator's
`tighten_gap` answer from setup (0.32 s unless they chose otherwise). Re-transcribe the result to check no word got clipped.
Needs numpy and soundfile (pip3 install numpy soundfile).
"""
import json, subprocess, sys, os, tempfile
import numpy as np, soundfile as sf
from fractions import Fraction
src, out = sys.argv[1], sys.argv[2]
def _default_gap():
    try:
        return float("@@TIGHTEN_GAP@@")          # filled from the creator's setup answer
    except ValueError:
        return 0.32
GAP = float(sys.argv[sys.argv.index("--gap") + 1]) if "--gap" in sys.argv else _default_gap()
THR, PRE, POST = -52, 0.07, 0.14
fr = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", src]).decode().strip()
FPS = float(Fraction(fr))
tmp = tempfile.mkdtemp(); wav = os.path.join(tmp, "a.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-c:a", "pcm_s24le", wav], check=True)
a, sr = sf.read(wav, always_2d=True); m = a.mean(1); h = sr // 100; n = len(m) // h
db = 20 * np.log10(np.sqrt((m[: n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
sp = np.convolve(db, np.ones(3) / 3, "same") > THR
runs, i = [], 0
while i < n:
    if sp[i]:
        j = i
        while j < n and sp[j]: j += 1
        if j - i >= 3: runs.append([i / 100, j / 100])
        i = j
    else: i += 1
merged = []
for r in runs:
    if merged and r[0] - merged[-1][1] <= GAP: merged[-1][1] = r[1]
    else: merged.append(r)
keeps = []
for s, e in merged:
    fs_, fe = int(round(max(s - PRE, 0) * FPS)), int(round((e + POST) * FPS))
    if keeps and fs_ <= keeps[-1][1]: keeps[-1][1] = max(keeps[-1][1], fe)
    else: keeps.append([fs_, fe])
dur = n / 100; tot = sum(e - s for s, e in keeps) / FPS
print(f"{len(keeps)} keeps, {dur:.2f}s -> {tot:.2f}s (removed {dur - tot:.2f}s)")
X = int(0.008 * sr); parts = []
for s, e in keeps:
    c = a[int(s / FPS * sr): int(e / FPS * sr)].copy(); r = np.linspace(0, 1, X)[:, None]
    c[:X] *= r; c[-X:] *= r[::-1]; parts.append(c)
aw = os.path.join(tmp, "t.wav"); sf.write(aw, np.concatenate(parts), sr, subtype="PCM_24")
json.dump(keeps, open(out + ".keeps.json", "w"))
# ffmpeg select dies past ~100 between() terms: render in chunks then concat
chunks, lst = [keeps[i:i + 60] for i in range(0, len(keeps), 60)], os.path.join(tmp, "l.txt")
with open(lst, "w") as L:
    for k, ch in enumerate(chunks):
        sel = "+".join(f"between(n,{s},{e - 1})" for s, e in ch); p = os.path.join(tmp, f"p{k}.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-an", "-vf", f"select='{sel}',setpts=N/({fr})/TB", "-r", fr,
                        "-c:v", "hevc_videotoolbox", "-b:v", "40M", "-tag:v", "hvc1", p], check=True)
        L.write(f"file '{p}'\n")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", aw, "-map", "0:v", "-map", "1:a",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-shortest", out], check=True)
print("wrote", out)
