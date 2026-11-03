#!/usr/bin/env python3
"""Scaffold (or refresh) the HyperFrames project for one clip.   06_new_project.py <clip slug> "<Title>"
Needs this skill's cut pipeline (scripts/cut/01_prep ... 06_captions) to have run for <clip slug>: cut rendered,
captions.json written. Creates <projects root>/<clip slug> with the engine and the graphics kit, the fonts from this
skill's assets/fonts, the cut linked as assets/cam.mp4, captions, cuts, project.json and faces.json (04_faces.py).
Never touches an existing build.py. Swear words in captions follow the setup answer (the audio always keeps them)."""
import json, os, re, shutil, subprocess, sys
from callcommon import WORK_ROOT, PROJECTS_ROOT, SKILL as SK
slug, title = sys.argv[1], sys.argv[2]
W = f"{WORK_ROOT}/{slug}"; PJ = f"{PROJECTS_ROOT}/{slug}"
os.path.exists(f"{SK}/.configured") or sys.exit("This skill has not been set up yet: run the setup interview (setup/SETUP.md) first.")
M = json.load(open(f"{W}/meta.json"))
cut = M.get("cut") or f"{M['out']}/{M['stem']} - CUT.mp4"; os.path.exists(cut) or sys.exit(f"no cut at {cut}: run cut/05_render_cut.py")
if not os.path.exists(PJ):
    os.makedirs(PROJECTS_ROOT, exist_ok=True)
    subprocess.run(["npx", "-y", "hyperframes@latest", "init", slug, "--non-interactive", "--example=blank", "--skill=general-video"], cwd=PROJECTS_ROOT, check=True, capture_output=True)
os.makedirs(f"{PJ}/assets/fonts", exist_ok=True)
for f in os.listdir(f"{SK}/assets/fonts"): shutil.copy(f"{SK}/assets/fonts/{f}", f"{PJ}/assets/fonts/{f}")
if os.path.lexists(f"{PJ}/assets/cam.mp4"): os.remove(f"{PJ}/assets/cam.mp4")
os.symlink(cut, f"{PJ}/assets/cam.mp4")
for f in ("coach_engine.py", "coach_kit.py"): shutil.copy(f"{SK}/engine/{f}", f"{PJ}/{f}")
for f in ("cuts.json", "cut_words.json"): shutil.copy(f"{W}/{f}", f"{PJ}/{f}")
STAR = "@@SWEAR_CAPTIONS@@".strip().lower().startswith("star")     # setup answer: starred | as spoken
SWEAR = {"fuck": "f***", "fucking": "f***ing", "fucked": "f***ed", "shit": "s***", "bullshit": "bulls***"}
caps = json.load(open(f"{W}/captions.json"))
if STAR:
    for c in caps:
        for p in c["parts"]:
            p["t"] = re.sub(r"[A-Za-z]+", lambda m: (SWEAR[m.group(0).lower()].capitalize() if m.group(0)[0].isupper() else SWEAR[m.group(0).lower()]) if m.group(0).lower() in SWEAR else m.group(0), p["t"])
json.dump(caps, open(f"{PJ}/captions.json", "w"))
d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", cut]))
num, den = (M["fps"].split("/") + ["1"])[:2]
json.dump({"title": title, "dur": round(d, 3), "fps": float(num) / float(den), "fps_str": M["fps"], "out": M["out"], "stem": M["stem"].replace(" - source", "")}, open(f"{PJ}/project.json", "w"))
print(f"{PJ}: {d:.2f}s, {len(caps)} captions" + (" (swear words starred)" if STAR else ""))
# faces.json must be in the engine's 1920x1080 layout space: detect on a 1080p proxy when the cut is any other size
if (M["w"], M["h"]) != (1920, 1080):
    proxy = f"{W}/proxy1080.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", cut, "-vf", "scale=1920:1080", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-an", proxy], check=True)
    print(f"({M['w']}x{M['h']} source: faces found on a 1920x1080 proxy; leave E.init's src at its default)")
else:
    proxy = cut
subprocess.run([sys.executable, f"{SK}/scripts/04_faces.py", proxy, PJ], check=True)
