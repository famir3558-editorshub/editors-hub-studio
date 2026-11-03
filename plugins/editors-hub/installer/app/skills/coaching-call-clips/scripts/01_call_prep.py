#!/usr/bin/env python3
"""Step 1 - prepare a coaching call.   01_call_prep.py "<call video>" <slug> ["<output dir>"]
Probes the recording, writes mono audio for transcription, and makes contact sheets of the whole call so the framing
(which side the speaker sits, where they look, where the empty space is, any change of set-up) can be read before
planning. Work dir: <work root>/<slug> (small files only). Output dir: "<video folder>/<video name> - Clips" unless given."""
import os, subprocess, sys
from callcommon import work, probe, save, run, grab, mmss
src = os.path.abspath(os.path.expanduser(sys.argv[1])); W = work(sys.argv[2])
os.path.exists(src) or sys.exit(f"not found: {src}")
P = probe(src); P["audio"] or sys.exit("the recording has no audio track")
stem = os.path.splitext(os.path.basename(src))[0]
out = os.path.expanduser(sys.argv[3]) if len(sys.argv) > 3 else f"{os.path.dirname(src)}/{stem} - Clips"
os.makedirs(out, exist_ok=True)
run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000", f"{W}/a16.flac"])
save(W, "meta.json", {"src": src, "stem": stem, "out": out, **P})

# 48 frames spread over the call, 24 per sheet, each labelled by its position in the file name list printed below
N, per = 48, 24
os.makedirs(f"{W}/sheet", exist_ok=True)
times = [P["dur"] * (i + 0.5) / N for i in range(N)]
for i, t in enumerate(times):
    grab(src, t, f"{W}/sheet/f{i:02d}.jpg", box=(640, 360))
for s in range(N // per):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-start_number", str(s * per), "-i", f"{W}/sheet/f%02d.jpg",
                    "-frames:v", "1", "-vf", f"scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2,tile=6x4",
                    "-q:v", "4", f"{W}/call-sheet-{s + 1}.jpg"], check=True)
print(f"{stem}: {P['w']}x{P['h']} {P['fps']} fps, {mmss(P['dur'])} ({P['dur'] / 60:.0f} min) -> work {W} | out {out}")
print(f"contact sheets: {W}/call-sheet-1.jpg, call-sheet-2.jpg (6x4, left to right, top to bottom). Tile times:")
print("  " + "  ".join(f"{i + 1}:{mmss(t)}" for i, t in enumerate(times)))
if P["w"] < P["h"]:
    print("NOTE the recording is vertical. The 16:9 version needs a horizontal source: ask the creator before planning one.")
if P["fps"] != P["avg_fps"]:
    print(f"WARNING variable frame rate ({P['avg_fps']} avg vs {P['fps']}): common for Zoom / screen recordings. Make a constant-rate copy first:\n"
          f'  ffmpeg -i "<video>" -fps_mode cfr -r 30 -c:v hevc_videotoolbox -b:v 40M -tag:v hvc1 -c:a copy "<cfr copy>"  and run this on that.')
if "arib" in P["transfer"] or "smpte2084" in P["transfer"]:
    print("NOTE the recording is HDR; screenshots and graphics are SDR. Tell the creator before rendering.")
