#!/usr/bin/env python3
"""windows.py <slug> [<segs.json>]
Maps the layout sections of the split-screen base (<work root>/<slug>/split/segs.json, raw timeline) through the
dialogue cut (<work root>/<slug>/edl.json) and writes <work root>/<slug>/windows.json:
  {"full": [[a, b], ...], "doc": [[a, b], ...], "short": [...]}   seconds on the CUT timeline, on the frame grid.
This is a PREDICTION. Always run snap_windows.py next: the real switch in the base video sits a frame either side."""
import json, math, os, sys
slug = sys.argv[1]; W = f"{os.path.expanduser('@@WORK_ROOT@@')}/{slug}"       # the educational-youtube-editor work folder for this video
E = json.load(open(f"{W}/edl.json")); FPS = E["fps"]; keeps = E["keeps"]
segs = json.load(open(os.path.expanduser(sys.argv[2]) if len(sys.argv) > 2 else f"{W}/split/segs.json"))
starts = []; t = 0
for s, e in keeps: starts.append(t); t += e - s
total = t / FPS
def spans(a, b):
    out = []; A, B = a * FPS, b * FPS
    for (s, e), st in zip(keeps, starts):
        lo, hi = max(s, A), min(e, B)
        if hi > lo: out.append([(st + lo - s) / FPS, (st + hi - s) / FPS])
    return out
snap = lambda x: round(math.ceil(x * FPS - 1e-6) / FPS, 4); res = {"full": [], "doc": []}
for g in segs:
    sp = spans(g["start"], g["end"])
    if sp: res["full" if g["mode"] == "full" else "doc"].append([snap(sp[0][0]), snap(sp[-1][1])])
res["short"] = [w for w in res["full"] if w[1] - w[0] < 2.0]; res["dur"] = round(total, 3)
json.dump(res, open(f"{W}/windows.json", "w"), indent=1)
print(f"{slug}: cut {total:.1f}s | {len(res['full'])} full-screen windows = {sum(b - a for a, b in res['full']):.1f}s | {len(res['doc'])} document sections | {len(res['short'])} under 2 s (look at these)")
for a, b in res["full"]: print(f"  full {a:8.2f} - {b:8.2f}  ({b - a:.1f}s)")
