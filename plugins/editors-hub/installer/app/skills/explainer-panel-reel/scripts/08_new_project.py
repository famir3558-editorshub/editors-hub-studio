#!/usr/bin/env python3
"""Step 8 - scaffold the HyperFrames project.   08_new_project.py <slug> "<Title>"
Creates <projects root>/<slug>-panel with the engine, fonts, brand.json (written from the creator's setup), the
pre-cropped camera files (links), captions and a starter build.py. Re-run with --refresh after changing captions, crops
or the creator's setup (never overwrites build.py)."""
import json, os, shutil, subprocess, sys
from fractions import Fraction
from common import work, load, brand, font_report, SKILL, PROJECTS_ROOT
slug = sys.argv[1]; W = work(slug); M = load(W, "meta.json"); C = load(W, "crops.json") or sys.exit("run 06_crops.py first")
PJ = f"{PROJECTS_ROOT}/{slug}-panel"; refresh = "--refresh" in sys.argv
title = next((a for a in sys.argv[2:] if not a.startswith("--")), M["stem"]); media = f"{M['out']}/hf-media"
if not os.path.exists(PJ):
    os.makedirs(PROJECTS_ROOT, exist_ok=True)
    subprocess.run(["npx", "-y", "hyperframes@latest", "init", f"{slug}-panel", "--non-interactive", "--example=blank", "--skill=general-video"], cwd=PROJECTS_ROOT, check=True, capture_output=True)
elif not refresh: sys.exit(f"{PJ} exists. Use --refresh to update captions / crops / engine without touching build.py.")
os.makedirs(f"{PJ}/assets/fonts", exist_ok=True); os.makedirs(f"{PJ}/assets/media", exist_ok=True)
for f in os.listdir(f"{SKILL}/assets/fonts"): shutil.copy(f"{SKILL}/assets/fonts/{f}", f"{PJ}/assets/fonts/{f}")
for f in os.listdir(f"{SKILL}/assets"):                       # the creator's own images, if setup copied any (logo, avatar): available to s.img()
    if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".svg")): shutil.copy(f"{SKILL}/assets/{f}", f"{PJ}/assets/{f}")
shutil.copy(f"{SKILL}/engine/panel_engine.py", f"{PJ}/panel_engine.py")
B = brand(W); json.dump(B, open(f"{PJ}/assets/brand.json", "w"), indent=1)
for f in ("cam_full.mp4", "cam_panel.mp4", "cam_panel_fg.webm"):
    d = f"{PJ}/assets/{f}"
    if os.path.lexists(d): os.remove(d)
    if os.path.exists(f"{media}/{f}"): os.symlink(f"{media}/{f}", d)
for f in ("captions.json", "cut_words.json", "cuts.json"):
    if os.path.exists(f"{W}/{f}"): shutil.copy(f"{W}/{f}", f"{PJ}/{f}")
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{media}/cam_full.mp4"]))
json.dump({"title": title, "slug": slug, "work": W, "out": M["out"], "stem": M["stem"], "dur": round(dur, 3), "fps": float(Fraction(M["fps"])), "fps_str": M["fps"],
           "panel": C["pn"], "cap": C["cap"], "popout": C["popout"]}, open(f"{PJ}/project.json", "w"), indent=1)
if not os.path.exists(f"{PJ}/build.py"):
    open(f"{PJ}/build.py", "w").write(open(f"{SKILL}/templates/build.py").read().replace("__TITLE__", title))
print(f"project {PJ} | {dur:.2f}s at {M['fps']} fps | accent {B['accent']} | emphasis size {B['emphasis_scale']}x | heading line 2: {B['heading_block']} | "
      f"handle watermark {B.get('handle') or 'off'}")
print("Fonts (the skill's assets/fonts, filled in at setup):")
for line in font_report(): print("  " + line)
print("A font marked NOT FOUND would silently fall back to another face: fix it (or tell the creator) before rendering.")
if not os.path.exists(f"{PJ}/captions.json"): print("WARNING no captions.json yet: run 07_captions.py then 08_new_project.py --refresh")
