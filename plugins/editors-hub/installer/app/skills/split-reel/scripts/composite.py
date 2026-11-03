#!/usr/bin/env python3
"""Split-screen 9:16 reel compositor.   python3 composite.py <reel.json> [--out-dir DIR] [--preview]
  --preview   fast 720x1280 draft ("<title> - 9x16 Reel - PREVIEW.mp4", veryfast, CRF 23) for the approval step

Reads the same reel.json the Remotion scenes import:
  title       "My Reel"                     -> "<title> - 9x16 Reel.mp4"
  source      the creator's cut (16:9); its audio is used as-is, untouched
  out_dir     panels are read from <out_dir>/Animations/"01 - Hook.mp4" (scene id "01-Hook")
  fps         source frame rate, e.g. "24000/1001"
  top_crop    [w,h,x,y] 9:8 crop of the source -> 1080x960 top half
  fs_crop     [w,h,x,y] 9:16 crop of the source -> 1080x1920 for full-screen windows
  scenes      [{id,start,end}] seconds on the cut
  fullscreen  [[a,b],...] seconds: just the creator, no graphics; hard cuts in and out
The lower half is black wherever no scene is playing.
"""
import json, os, subprocess, sys
from fractions import Fraction

c = json.load(open(sys.argv[1]))
out_dir = sys.argv[sys.argv.index("--out-dir") + 1] if "--out-dir" in sys.argv else c["out_dir"]
anim_dir = os.path.join(c["out_dir"], "Animations")
fps = Fraction(c.get("fps", "24000/1001"))
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", c["source"]]).decode())
snap = lambda t: round(round(t * fps) / fps, 4)  # frame-accurate
name = lambda sid: sid.replace("-", " - ", 1)    # "01-Hook" -> "01 - Hook"

tw, th, tx, ty = c["top_crop"]
fw, fh, fx, fy = c.get("fs_crop", [0, 0, 0, 0])
fs = [(snap(a), snap(b)) for a, b in c.get("fullscreen", [])]
scenes = [dict(s, file=s.get("file") or os.path.join(anim_dir, name(s["id"]) + ".mp4")) for s in c.get("scenes", [])]
for s in scenes:
    if not os.path.exists(s["file"]): sys.exit(f"missing panel: {s['file']} (run render_scenes.sh first)")
preview = "--preview" in sys.argv
out = os.path.join(out_dir, f"{c['title']} - 9x16 Reel{' - PREVIEW' if preview else ''}.mp4")

args = ["ffmpeg", "-v", "error", "-y", "-i", c["source"]]
for s in scenes: args += ["-i", s["file"]]
g = ["[0:v]split=2[srcA][srcB]",
     f"[srcA]crop={tw}:{th}:{tx}:{ty},scale=1080:960:flags=lanczos,setsar=1[top]",
     f"color=c=black:s=1080x960:r={fps}:d={dur:.3f}[b0]"]
cur = "b0"
for i, s in enumerate(scenes, 1):
    g.append(f"[{i}:v]fps={fps},setsar=1,setpts=PTS-STARTPTS+{snap(s['start'])}/TB[s{i}]")
    g.append(f"[{cur}][s{i}]overlay=eof_action=pass:repeatlast=0[b{i}]")
    cur = f"b{i}"
g.append(f"[top][{cur}]vstack=shortest=1[split]")
if fs:
    en = "+".join(f"between(t,{a},{b - 0.0001})" for a, b in fs)
    g.append(f"[srcB]crop={fw}:{fh}:{fx}:{fy},scale=1080:1920:flags=lanczos,setsar=1[full]")
    g.append(f"[split][full]overlay=0:0:enable='{en}',format=yuv420p[vf]")
else:
    g += ["[srcB]nullsink", "[split]format=yuv420p[vf]"]
g.append("[vf]scale=720:1280:flags=bicubic[v]" if preview else "[vf]null[v]")
args += ["-filter_complex", ";".join(g), "-map", "[v]", "-map", "0:a", "-r", str(fps),
         "-c:v", "libx264", "-preset", "veryfast" if preview else "slow", "-crf", "23" if preview else "16",
         "-c:a", "aac", "-b:a", "192k" if preview else "320k",
         "-movflags", "+faststart", "-t", f"{dur:.3f}", out]
print(f"{len(scenes)} panels, {len(fs)} full-screen windows, {dur:.2f}s -> {out}", flush=True)
subprocess.run(args, check=True)
print("done")
