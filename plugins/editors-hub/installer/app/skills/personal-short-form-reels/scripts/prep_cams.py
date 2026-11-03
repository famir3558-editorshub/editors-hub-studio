#!/usr/bin/env python3
"""Camera files for the reel, from the rendered tight cut.   prep_cams.py "<CUT.mp4>" "<out>/hf-media" [--full W H X Y] [--top W H X Y] [--top-y N]
  cam_full.mp4 = 1080x1920, muted  (the creator full screen)
  cam_top.mp4  = 1080x960, CARRIES THE AUDIO  (the creator on the bottom half in SPLIT windows; needed even when the reel has no split)
A VERTICAL source (phone clips are often stored as 3840x2160 with a rotation flag = really 2160x3840) is simply scaled; cam_top is a 1080x960 window of it
starting --top-y px down the 1080x1920 frame (default 330: the head near the top of the half, chin and chest below).
A HORIZONTAL 16:9 source needs crops in SOURCE pixels: --full (9:16 window) and --top (9:8 window). The defaults are the crops saved
at setup for the creator's usual camera set-up (@@CROP_FULL@@ and @@CROP_TOP@@). ALWAYS open the two stills this writes (cam_full.jpg, cam_top.jpg): the whole head in frame, face centred, head not cut."""
import subprocess, sys, json, os
a = sys.argv[1:]; cut, out = a[0], a[1]; os.makedirs(out, exist_ok=True)
def opt(k, n, d):
    return [int(x) for x in a[a.index(k) + 1:a.index(k) + 1 + n]] if k in a else d
s = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:stream_side_data=rotation", "-of", "json", cut]))["streams"][0]
w, h = s["width"], s["height"]
rot = abs(int(float((s.get("side_data_list") or [{}])[0].get("rotation", 0) or 0)))
if rot in (90, 270): w, h = h, w
V = ["-r", "24000/1001", "-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
if h > w:
    ty = opt("--top-y", 1, [330])[0]
    full = "scale=1080:1920:flags=lanczos,setsar=1"; top = f"scale=1080:1920:flags=lanczos,crop=1080:960:0:{ty},setsar=1"
    print(f"vertical source {w}x{h}: scaled; cam_top = y {ty}-{ty + 960} of the frame")
else:
    fw, fh, fx, fy = opt("--full", 4, [int(x) for x in "@@CROP_FULL@@".split()]); tw, th, tx, ty = opt("--top", 4, [int(x) for x in "@@CROP_TOP@@".split()])
    full = f"crop={fw}:{fh}:{fx}:{fy},scale=1080:1920:flags=lanczos,setsar=1"; top = f"crop={tw}:{th}:{tx}:{ty},scale=1080:960:flags=lanczos,setsar=1"
    print(f"horizontal source {w}x{h}: full crop {fw}x{fh}+{fx}+{fy}, top crop {tw}x{th}+{tx}+{ty}")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", cut, "-an", "-vf", full, "-crf", "15"] + V + [f"{out}/cam_full.mp4"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", cut, "-vf", top, "-crf", "18", "-c:a", "aac", "-b:a", "320k"] + V + [f"{out}/cam_top.mp4"], check=True)
for n in ("cam_full", "cam_top"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "2", "-i", f"{out}/{n}.mp4", "-frames:v", "1", f"{out}/{n}.jpg"], check=True)
    print(n, subprocess.check_output(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=width,height,nb_read_frames", "-of", "csv=p=0", f"{out}/{n}.mp4"]).decode().strip())
print("open", f"{out}/cam_full.jpg", "and cam_top.jpg and check the framing")
