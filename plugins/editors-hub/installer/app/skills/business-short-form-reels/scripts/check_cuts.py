#!/usr/bin/env python3
"""Verify cut alignment on the RENDERED reel.   check_cuts.py "<reel.mp4>" "<hf-media dir>" <work>/edl.json [allowed small-cut frames, comma separated]
Works out the mode of every frame by comparing it with cam_top.mp4 (split = the creator's camera in the bottom half), then reports any split on/off
switch that is not on an edit cut and any edit cut sitting inside a split block. (Face windows are zoomed and carry overlays, so they are
checked through the split windows either side of them.)"""
import json, subprocess, sys, numpy as np
reel, media, edl = sys.argv[1:4]; allow = {int(x) for x in sys.argv[4].split(",")} if len(sys.argv) > 4 else set()
E = json.load(open(edl)); F = E["fps"]; acc = 0; C = []
for s, e in E["keeps"]: acc += e - s; C.append(acc)
C = C[:-1]
def load(p, w, h): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vf", f"scale={w}:{h},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout, np.uint8).reshape(-1, h, w).astype(np.float32)
R = load(reel, 90, 160); T = load(media + "/cam_top.mp4", 90, 80); n = min(len(R), len(T))
S = [np.abs(R[i][80:160] - T[i]).mean() < 8 for i in range(n)]; sw = [i for i in range(1, n) if S[i] != S[i - 1]]
print("split switches:", len(sw)); print("split switches NOT on an edit cut:", [round(i / F, 3) for i in sw if i not in C])
print("edit cuts inside a split block (not in the allowed list):", [round(c / F, 3) for c in C if c < n and S[c] and S[c - 1] and c not in allow])
