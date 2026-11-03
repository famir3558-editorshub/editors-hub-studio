#!/usr/bin/env python3
"""Step 5 - render the cut.   05_render_cut.py <slug>
Frame-accurate select from the source, 8 ms audio fades at every join. Writes "<out>/<name> - CUT.mp4" at the
source resolution and records it in meta.json. Run in the background for long or 4K sources."""
import subprocess, sys, tempfile
import numpy as np, soundfile as sf
from common import work, load, save
W = work(sys.argv[1]); M = load(W, "meta.json"); E = load(W, "edl.json"); keeps = E["keeps"]; FPS = E["fps"]; FR = M["fps"]; src = M["src"]
out = f"{M['out']}/{M['stem']} - CUT.mp4"; rate = "45M" if max(M["w"], M["h"]) >= 3000 else "20M"
tmp = tempfile.mkdtemp(dir=M["out"], prefix=".cut-"); wav = f"{tmp}/a.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-c:a", "pcm_s24le", wav], check=True)
a, sr = sf.read(wav, always_2d=True); X = int(0.008 * sr); r = np.linspace(0, 1, X)[:, None]; parts = []
for s, e in keeps:
    c = a[int(round(s / FPS * sr)): int(round(e / FPS * sr))].copy()
    if len(c) > 2 * X:
        c[:X] *= r; c[-X:] *= r[::-1]
    parts.append(c)
sf.write(f"{tmp}/t.wav", np.concatenate(parts), sr, subtype="PCM_24"); lst = f"{tmp}/l.txt"
with open(lst, "w") as L:                       # ffmpeg select dies past ~100 between() terms -> chunks of 50
    for k in range(0, len(keeps), 50):
        sel = "+".join(f"between(n,{s},{e - 1})" for s, e in keeps[k: k + 50]); p = f"{tmp}/p{k}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-an", "-vf", f"select='{sel}',setpts=N/({FR})/TB", "-r", FR,
                        "-c:v", "hevc_videotoolbox", "-b:v", rate, "-tag:v", "hvc1", p], check=True)
        L.write(f"file '{p}'\n")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", f"{tmp}/t.wav", "-map", "0:v", "-map", "1:a",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-shortest", out], check=True)
subprocess.run(["rm", "-rf", tmp])
M["cut"] = out; M["cut_dur"] = sum(e - s for s, e in keeps) / FPS; save(W, "meta.json", M)
print("wrote", out, f"{M['cut_dur']:.2f}s")
