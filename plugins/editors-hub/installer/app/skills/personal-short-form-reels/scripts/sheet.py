#!/usr/bin/env python3
"""Look at a video without playing it.
  sheet.py every "<video>" <seconds> [out.jpg] [t0 t1]   contact sheet, one frame every N seconds with its time burned in (use on a SCREEN RECORDING to find
                                                         the moments the creator is describing, on B-roll candidates, on a finished render for rhythm)
  sheet.py frames "<render>" f f f ... [out.jpg]         the frame before, on and after each frame number (use on the RENDER at every mode switch and every
                                                         B-roll-to-B-roll change: the change must be ON the frame, with no black frame and no flash)
Needs Pillow for the time labels (falls back to unlabelled tiles)."""
import subprocess, sys, os, tempfile
mode, vid = sys.argv[1], sys.argv[2]; rest = sys.argv[3:]
out = next((x for x in rest if x.endswith(".jpg")), os.path.splitext(vid)[0] + f".{mode}.jpg"); rest = [x for x in rest if not x.endswith(".jpg")]
tmp = tempfile.mkdtemp(); tiles = []
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", vid]).decode().strip())
if mode == "every":
    step = float(rest[0]); t0, t1 = (float(rest[1]), float(rest[2])) if len(rest) > 2 else (0, dur); t = t0
    while t < t1 - 0.05: tiles.append((f"{t:.1f}s", ["-ss", f"{t:.3f}", "-i", vid, "-frames:v", "1"])); t += step
else:
    for f in [int(x) for x in rest]:
        for d in (-1, 0, 1): tiles.append((f"f{f + d}", ["-i", vid, "-vf", f"select='eq(n,{f + d})'", "-frames:v", "1", "-vsync", "0"]))
paths = []
for i, (lab, args) in enumerate(tiles):
    p = f"{tmp}/{i:04d}.jpg"; a = list(args)
    if "-vf" in a: a[a.index("-vf") + 1] += ",scale=-2:360"
    else: a += ["-vf", "scale=-2:360"]
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + a + [p]); paths.append((lab, p))
try:
    from PIL import Image, ImageDraw
    ims = [(l, Image.open(p)) for l, p in paths if os.path.exists(p)]; w, h = ims[0][1].size; cols = 9 if mode == "frames" else max(1, min(8, 1800 // w)); rows = -(-len(ims) // cols)
    S = Image.new("RGB", (cols * w, rows * h), "black"); D = ImageDraw.Draw(S)
    for k, (l, im) in enumerate(ims):
        x, y = (k % cols) * w, (k // cols) * h; S.paste(im, (x, y)); D.rectangle([x, y, x + 8 * len(l) + 8, y + 18], fill="black"); D.text((x + 4, y + 3), l, fill="yellow")
    S.save(out, quality=88)
except ImportError:
    n = len(paths); cols = 9 if mode == "frames" else 6; cmd = ["ffmpeg", "-v", "error", "-y"]
    for _, p in paths: cmd += ["-i", p]
    subprocess.run(cmd + ["-filter_complex", "".join(f"[{i}:v]" for i in range(n)) + f"xstack=inputs={n}:layout=" + "|".join(f"{(k % cols)}*w0_{(k // cols)}*h0" for k in range(n)), out])
print(len(paths), "tiles ->", out)
