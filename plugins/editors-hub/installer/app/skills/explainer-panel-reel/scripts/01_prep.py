#!/usr/bin/env python3
"""Step 1 - prepare.   01_prep.py "<video>" <slug> ["<output dir>"]
Probes the video, writes mono audio for analysis and upload, and records where outputs go.
Work dir: <work root>/<slug> (small files only; the work root is set at setup). Output dir: the creator's output rule
(by default "<video folder>/<video name> - Edit") unless given."""
import os, sys
from common import work, probe, save, run, WORK_ROOT
src = os.path.abspath(os.path.expanduser(sys.argv[1])); W = work(sys.argv[2])
os.path.exists(src) or sys.exit(f"not found: {src}")
P = probe(src); P["audio"] or sys.exit("the video has no audio track")
stem = os.path.splitext(os.path.basename(src))[0]
out = os.path.expanduser(sys.argv[3]) if len(sys.argv) > 3 else f"{os.path.dirname(src)}/{stem} - Edit"
os.makedirs(out, exist_ok=True)
run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "48000", f"{W}/a48.wav"])
run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/a48.wav", "-ar", "16000", f"{W}/a16.wav"])
run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/a16.wav", f"{W}/a16.flac"])
save(W, "meta.json", {"src": src, "stem": stem, "out": out, **P})
print(f"{stem}: {P['w']}x{P['h']} {P['fps']} fps, {P['dur']:.1f}s -> work {W} | out {out}")
if P["fps"] != P["avg_fps"]:
    print(f"WARNING variable frame rate ({P['avg_fps']} avg vs {P['fps']}). Make a constant-frame-rate copy first:\n"
          f'  ffmpeg -i "<video>" -vsync cfr -r 30 -c:v hevc_videotoolbox -b:v 40M -tag:v hvc1 -c:a copy "<cfr copy>"  and run 01_prep.py on that.')
if "arib" in P["transfer"] or "smpte2084" in P["transfer"]:
    print("NOTE the video is HDR; screenshots and graphics are SDR. Tell the creator before rendering.")
