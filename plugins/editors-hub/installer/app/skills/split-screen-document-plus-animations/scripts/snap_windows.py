#!/usr/bin/env python3
"""snap_windows.py <slug> <base video (the 1080p cam.mp4 the edit is built on)>
windows.py predicts where the layout switches on the cut timeline; the real switch in the rendered base video can sit a
frame either side. This reads the frames around every predicted switch from the base video itself (document layout =
the left 40% of the frame is a white page) and rewrites <work root>/<slug>/windows.json with the measured frame, so
graphics, punch-ins and the camera drift can switch on exactly the same frame as the layout."""
import json, os, subprocess, sys
import numpy as np
slug, base = sys.argv[1], sys.argv[2]
WR = f"{os.path.expanduser('@@WORK_ROOT@@')}/{slug}"; P = f"{WR}/windows.json"; W = json.load(open(P))
E = json.load(open(f"{WR}/edl.json")); FPS = E["fps"]; R = 4
edges = sorted({round(x * FPS) for a, b in W["doc"] for x in (a, b)})
total = round(W["dur"] * FPS)
need = sorted({n for e in edges for n in range(e - R, e + R + 1) if 0 <= n < total}); lum = {}
for k in range(0, len(need), 60):
    part = need[k:k + 60]; sel = "+".join(f"eq(n\\,{n})" for n in part)
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", base, "-vf", f"select='{sel}',crop=iw*0.40:ih:0:0,scale=64:64,format=gray",
                          "-vsync", "0", "-f", "rawvideo", "-"], capture_output=True).stdout
    for n, fr in zip(part, np.frombuffer(raw, np.uint8).reshape(-1, 64 * 64)): lum[n] = float(fr.mean())
is_doc = lambda n: lum[n] > 160
fix = {}; moved = 0
for e in edges:
    ns = [n for n in range(e - R, e + R + 1) if n in lum]
    flips = [n for n in ns[1:] if n - 1 in lum and is_doc(n) != is_doc(n - 1)]
    if e <= 0 or e >= total: fix[e] = e; continue
    if len(flips) != 1: print(f"  ? switch near frame {e} ({e / FPS:.2f}s): {len(flips)} layout changes within {R} frames, left as predicted"); fix[e] = e; continue
    fix[e] = flips[0]; moved += flips[0] != e
t = lambda x: round(fix[round(x * FPS)] / FPS, 4)
for key in ("full", "doc"): W[key] = [[t(a) if round(a * FPS) in fix else a, t(b) if round(b * FPS) in fix else b] for a, b in W[key]]
W["short"] = [w for w in W["full"] if w[1] - w[0] < 2.0]; W["measured"] = True
json.dump(W, open(P, "w"), indent=1)
print(f"{slug}: {len(edges)} layout switches measured in the base video, {moved} moved by a frame or more")
