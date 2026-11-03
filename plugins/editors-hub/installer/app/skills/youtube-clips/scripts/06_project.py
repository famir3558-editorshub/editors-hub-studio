#!/usr/bin/env python3
"""Set up the HyperFrames project for one clip, after the tight cut is verified, rendered and captioned.
    06_project.py <clip slug> "<Title>" [<project dir>]
<clip slug> is the work dir (<work root>/<clip slug>) of this skill's cut pipeline (scripts/cut), holding meta.json (with
the rendered CUT), captions.json, cuts.json, cut_words.json, edl.json. Makes <projects root>/<clip slug> (or the dir
given): hyperframes init, the engine and ytkit, the fonts from this skill's assets/fonts, assets/cam.mp4 linked to the
full-resolution cut, a 1080p proxy for face detection (so faces.json is in the engine's 1920x1080 layout space),
faces.json / faces.jpg, project.json. Prints the face centre for K.start / E.init and where each source.json join falls
on the cut timeline (joins are often missing from cuts.json). Never touches an existing build.py. Swear words in
captions follow the setup answer (the audio always keeps them)."""
import glob, json, os, re, shutil, subprocess, sys
from ytcommon import WORK_ROOT, PROJECTS_ROOT, SKILL as skill
slug, title = sys.argv[1], sys.argv[2]
W = f"{WORK_ROOT}/{slug}"; PJ = os.path.expanduser(sys.argv[3]) if len(sys.argv) > 3 else f"{PROJECTS_ROOT}/{slug}"
here = os.path.dirname(os.path.abspath(__file__))
os.path.exists(f"{skill}/.configured") or sys.exit("This skill has not been set up yet: run the setup interview (setup/SETUP.md) first.")
M = json.load(open(f"{W}/meta.json"))
cut = M.get("cut") or next(iter(glob.glob(f"{M['out']}/*- CUT.mp4")), None) or sys.exit("no rendered cut: run cut/05_render_cut.py first")
if not os.path.exists(f"{PJ}/hyperframes.json"):
    os.makedirs(os.path.dirname(PJ), exist_ok=True)
    subprocess.run(["npx", "-y", "hyperframes@latest", "init", os.path.basename(PJ), "--example", "blank", "--non-interactive"], cwd=os.path.dirname(PJ), check=True, stdout=subprocess.DEVNULL)
for f in ("clip_engine.py", "ytkit.py"): shutil.copy(f"{skill}/engine/{f}", PJ)
os.makedirs(f"{PJ}/assets/fonts", exist_ok=True)
for f in glob.glob(f"{skill}/assets/fonts/*"):
    shutil.copy(f, f"{PJ}/assets/fonts")
if os.path.lexists(f"{PJ}/assets/cam.mp4"): os.remove(f"{PJ}/assets/cam.mp4")
os.symlink(cut, f"{PJ}/assets/cam.mp4")
for f in ("cuts.json", "cut_words.json"):
    shutil.copy(f"{W}/{f}", PJ)
STAR = "@@SWEAR_CAPTIONS@@".strip().lower().startswith("star")     # setup answer: starred | as spoken
SWEAR = {"fuck": "f***", "fucking": "f***ing", "fucked": "f***ed", "shit": "s***", "bullshit": "bulls***"}
caps = json.load(open(f"{W}/captions.json"))
if STAR:
    for c in caps:
        for p in c["parts"]:
            p["t"] = re.sub(r"[A-Za-z]+", lambda m: (SWEAR[m.group(0).lower()].capitalize() if m.group(0)[0].isupper() else SWEAR[m.group(0).lower()]) if m.group(0).lower() in SWEAR else m.group(0), p["t"])
json.dump(caps, open(f"{PJ}/captions.json", "w"))
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", cut]))
E = json.load(open(f"{W}/edl.json")); fps = E["fps"]
json.dump({"title": title, "dur": round(dur, 3), "fps": fps, "fps_str": M.get("fps", str(fps)), "out": M["out"], "stem": M["stem"].replace(" - source", "")}, open(f"{PJ}/project.json", "w"))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", cut, "-vf", "scale=1920:1080", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-an", f"{W}/proxy1080.mp4"], check=True)
subprocess.run([sys.executable, f"{here}/04_faces.py", f"{W}/proxy1080.mp4", PJ], check=True)
sj = next(iter(glob.glob(f"{M['out']}/*- source.json")), None)
if sj:
    for j in json.load(open(sj))["joins"]:
        fr = round(j["t"] * fps); kept = 0; t = None
        for a, b in E["keeps"]:
            if fr <= a: t = kept / fps; break
            if a < fr <= b: t = (kept + fr - a) / fps; break
            kept += b - a
        print(f"JOIN \"{j['before']}\" | \"{j['after']}\": cut timeline {t:.3f}s" if t is not None else f"JOIN at source {j['t']}: after the last kept frame")
print("cuts:", " ".join(f"{c['t']}{'*' if c['big'] else ''}" for c in json.load(open(f"{PJ}/cuts.json"))), "  (* = big)")
print(f"project {PJ}, {dur:.2f}s at {fps} fps, {len(caps)} captions" + (" (swear words starred)" if STAR else ""))
