#!/usr/bin/env python3
"""Step 8 - scaffold the HyperFrames project.   08_new_project.py <slug> "<Title>"
Creates <projects root>/<slug>-essay with the engine, fonts, film grain, brand.json, the presenter crop + cut-out (links), captions and a
starter build.py. Re-run with --refresh after changing captions, the cut-out, the brand or the engine (never overwrites build.py)."""
import json, os, shutil, subprocess, sys
from fractions import Fraction
from common import work, load, brand, font_report, pj, SKILL, PROJECTS_ROOT
slug = sys.argv[1]; W = work(slug); M = load(W, "meta.json"); C = load(W, "cutout.json") or sys.exit("run 06_cutout.py first")
PJ = pj(slug); refresh = "--refresh" in sys.argv
title = next((a for a in sys.argv[2:] if not a.startswith("--")), M["stem"]); media = f"{M['out']}/hf-media"
if not os.path.exists(PJ):
    os.makedirs(PROJECTS_ROOT, exist_ok=True)
    subprocess.run(["npx", "-y", "hyperframes@latest", "init", f"{slug}-essay", "--non-interactive", "--example=blank", "--skill=general-video"], cwd=PROJECTS_ROOT, check=True, capture_output=True)
elif not refresh: sys.exit(f"{PJ} exists. Use --refresh to update captions / cut-out / brand / engine without touching build.py.")
os.makedirs(f"{PJ}/assets/fonts", exist_ok=True); os.makedirs(f"{PJ}/assets/media", exist_ok=True)
for f in (os.listdir(f"{SKILL}/assets/fonts") if os.path.isdir(f"{SKILL}/assets/fonts") else []): shutil.copy(f"{SKILL}/assets/fonts/{f}", f"{PJ}/assets/fonts/{f}")
for f in os.listdir(f"{SKILL}/assets"):
    if f.endswith(".png"): shutil.copy(f"{SKILL}/assets/{f}", f"{PJ}/assets/{f}")
shutil.copy(f"{SKILL}/engine/essay_engine.py", f"{PJ}/essay_engine.py")
B = brand(W); json.dump(B, open(f"{PJ}/assets/brand.json", "w"), indent=1)
if os.path.exists(f"{SKILL}/assets/sfx_map.json") and not os.path.exists(f"{PJ}/sfx_map.json"): shutil.copy(f"{SKILL}/assets/sfx_map.json", f"{PJ}/sfx_map.json")
for f in ("cam.mp4", "cam_fg.webm"):
    d = f"{PJ}/assets/{f}"
    if os.path.lexists(d): os.remove(d)
    if os.path.exists(f"{media}/{f}"): os.symlink(f"{media}/{f}", d)
for f in ("captions.json", "cut_words.json", "cuts.json"):
    if os.path.exists(f"{W}/{f}"): shutil.copy(f"{W}/{f}", f"{PJ}/{f}")
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{media}/cam.mp4"]))
json.dump({"title": title, "slug": slug, "work": W, "out": M["out"], "stem": M["stem"], "dur": round(dur, 3), "fps": float(Fraction(M["fps"])), "fps_str": M["fps"],
           "me": C["me"], "cap": C["cap"]}, open(f"{PJ}/project.json", "w"), indent=1)
if not os.path.exists(f"{PJ}/build.py"):
    open(f"{PJ}/build.py", "w").write(open(f"{SKILL}/templates/build.py").read().replace("__TITLE__", title))
print(f"project {PJ} | {dur:.2f}s at {M['fps']} fps | accent {B['accent']} | cut-out {'ready' if os.path.exists(f'{media}/cam_fg.webm') else 'MISSING (panel fallback)'}")
for line in font_report(): print("font check:", line)
if not os.path.exists(f"{PJ}/captions.json"): print("WARNING no captions.json yet: run 07_captions.py then 08_new_project.py --refresh")
