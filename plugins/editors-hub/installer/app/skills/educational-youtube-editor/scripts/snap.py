#!/usr/bin/env python3
"""Look at frames without rendering.   snap.py <slug> <t> [<t> ...]  |  snap.py <slug> --scene <id> [<id> ...]  |  snap.py <slug> --all
Times are on the cut timeline (whole video). The right chunk is built and HyperFrames snapshots those instants; the
PNGs land in <project>/snapshots and one labelled contact sheet per call in <project>/review/snap-*.jpg. READ the sheet.
--scene  three frames of each named scene (just in, middle, just before it leaves)
--all    the same for every scene (several sheets)."""
import glob, json, os, subprocess, sys, time
from common import sheet, pj
slug = sys.argv[1]; PJ = pj(slug); args = sys.argv[2:]
subprocess.run([sys.executable, "build.py", "--list"], cwd=PJ, check=True, capture_output=True)
R = json.load(open(f"{PJ}/render.json")); A = json.load(open(f"{PJ}/audit.json")); want = []
if args and args[0] in ("--scene", "--all"):
    for s in A["scenes"]:
        if args[0] == "--all" or s["id"] in args[1:]:
            d = s["b"] - s["a"]; want += [(s["a"] + min(0.9, d * 0.3), f"{s['id']} in"), (s["a"] + d * 0.6, f"{s['id']} {s['kind']}/{s['comp']}"), (s["b"] - 0.45, f"{s['id']} out")]
else: want = [(float(t), f"{float(t):.2f}s") for t in args]
want or sys.exit(__doc__)
from PIL import Image
tiles = []
for ci, (a0, a1) in enumerate(R["chunks"]):
    mine = [(t, lab) for t, lab in want if a0 <= t < a1 or (ci == len(R["chunks"]) - 1 and t >= a1)]
    if not mine: continue
    subprocess.run([sys.executable, "build.py", "--chunk", str(ci)], cwd=PJ, check=True, capture_output=True)
    out = f"{PJ}/snapshots/c{ci}"; subprocess.run(["rm", "-rf", out]); os.makedirs(out)
    r = subprocess.run(["npx", "hyperframes", "snapshot", "--no-end", "--at", ",".join(f"{t - a0:.3f}" for t, _ in mine), "-o", out], cwd=PJ, capture_output=True, text=True)
    files = sorted(glob.glob(f"{out}/*.png"), key=os.path.getmtime)
    if len(files) != len(mine): print(r.stdout[-1500:], r.stderr[-1500:]); sys.exit(f"snapshot gave {len(files)} frames for {len(mine)} times")
    files = sorted(files, key=lambda p: float(os.path.basename(p).split("-")[-1].replace("s.png", "").replace(".png", "")) if os.path.basename(p).split("-")[-1][0].isdigit() else os.path.getmtime(p))
    tiles += [(Image.open(f).convert("RGB"), f"{lab}  @{t:.1f}s") for f, (t, lab) in zip(files, sorted(mine))]
os.makedirs(f"{PJ}/review", exist_ok=True); stamp = time.strftime("%H%M%S")
for k in range(0, len(tiles), 12):
    p = f"{PJ}/review/snap-{stamp}-{k // 12 + 1}.jpg"; sheet(tiles[k:k + 12], p, 3, 640); print("sheet", p)
