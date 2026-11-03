#!/usr/bin/env python3
"""Cut B-roll and screen-recording pieces for a reel: video only, 23.976 fps, exact frame counts.   cut_clips.py "<out dir>" <spec.json>
spec.json = [{"name": "b1", "src": "c_76ce9615d3f5" | "/path/file.mp4", "in": 140.0, "frames": 21, "fit": "auto", "speed": 1.0}, ...]
  src    : a personal-B-roll-library clip id (looked up with broll.py) or a file path. The source is only READ, never changed.
  in     : seconds into the source where the piece starts (inside a usable segment / the best section; for a recording, the moment the creator is describing)
  frames : frames it is on screen (2 spare frames are added at the tail as a safety margin)
  fit    : "auto"   = B-roll for a FULL window, 1080x1920: vertical footage fills the frame, horizontal footage is LETTERBOXED (kept horizontal with black
                      bars - the rule: never crop a horizontal clip to fill)
           "screen" = a screen recording for a SPLIT window: scaled to 1920 px wide (1080 wide if it is a phone recording), no bars, aspect kept
           "fill"   = crop to fill 1080x1920 (only when the creator asks)
  speed  : 2.0 plays the source twice as fast (useful for a long scroll or a loading wait in a recording)
Prints each file's size and frame count. Symlink the out dir into the project's assets/ (new_project.sh does this for broll/ and screen/)."""
import json, os, subprocess, sys
out, spec = sys.argv[1], json.load(open(sys.argv[2])); os.makedirs(out, exist_ok=True)
BROLL = os.path.expanduser("~/.claude/skills/personal-broll-library/scripts/broll.py")
for c in spec:
    src = c["src"]
    if not os.path.exists(src):
        r = json.loads(subprocess.run(["python3", BROLL, "show", src], capture_output=True, text=True).stdout or "{}")
        src = (r.get("clips") or [{}])[0].get("abs_path") or sys.exit(f"{c['name']}: {c['src']} is neither a file nor a library clip id")
        if not os.path.exists(src): sys.exit(f"{c['name']}: {src} is not reachable (is the drive plugged in?)")
    s = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:stream_side_data=rotation", "-of", "json", src]))["streams"][0]
    w, h = s["width"], s["height"]; rot = abs(int(float((s.get("side_data_list") or [{}])[0].get("rotation", 0) or 0)))
    if rot in (90, 270): w, h = h, w
    fit = c.get("fit", "auto"); sp = float(c.get("speed", 1.0)); pre = f"setpts=PTS/{sp}," if sp != 1.0 else ""
    if fit == "screen":
        tw = 1080 if h > w else 1920; vf = f"{pre}scale={tw}:-2:flags=lanczos,setsar=1"
    elif fit == "fill" or h >= w:
        vf = f"{pre}scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1"
    else:
        vf = f"{pre}scale=1080:-2:flags=lanczos,pad=1080:1920:0:(oh-ih)/2:black,setsar=1"
    dst = f"{out}/{c['name']}.mp4"; n = int(c["frames"]) + 2
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(c["in"]), "-i", src, "-an", "-vf", vf, "-r", "24000/1001", "-frames:v", str(n), "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-g", "12", "-pix_fmt", "yuv420p", "-movflags", "+faststart", dst], capture_output=True, text=True)
    info = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=width,height,nb_read_frames", "-of", "csv=p=0", dst], capture_output=True, text=True).stdout.strip()
    print(f"{c['name']:8s} {info:18s} {'letterboxed' if (fit == 'auto' and w > h) else fit:11s} <- {os.path.basename(src)} @ {c['in']}s", "" if int(info.split(",")[-1] or 0) >= int(c["frames"]) else "  SHORT: the source ran out, pick an earlier in-point")
