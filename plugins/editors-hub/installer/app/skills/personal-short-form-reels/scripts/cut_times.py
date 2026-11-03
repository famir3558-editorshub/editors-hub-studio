#!/usr/bin/env python3
"""Edit cuts of the tight cut, how visible each jump is, and the exact switch time to use.   cut_times.py <work>/edl.json <hf-media>/cam_full.mp4
Every mode switch between two camera modes (face <-> split) must sit on one of these. A jump under ~7 is a small head shift that may stay
visible inside a block; anything bigger must be a switch or be hidden under a full-screen animation.
Use the printed `switch` value (frame / fps - 0.002): a time rounded UP to the millisecond lands the switch one frame late."""
import json, subprocess, sys, numpy as np
E = json.load(open(sys.argv[1])); F = E["fps"]; acc = 0; C = []
for s, e in E["keeps"]: acc += e - s; C.append(acc)
C = C[:-1]; W, H = 135, 240
a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", sys.argv[2], "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout, np.uint8).reshape(-1, H, W).astype(np.float32)
d = np.abs(a[1:] - a[:-1]).mean((1, 2)); prev = 0
for c in C:
    print(f"frame {c:5d}  t={c / F:7.3f}  switch={c / F - 0.002:8.4f}  jump={d[c - 1]:5.1f}  ({'small' if d[c - 1] < 7.5 else 'MUST switch or hide'})  block since last cut {(c - prev) / F:4.1f}s"); prev = c
