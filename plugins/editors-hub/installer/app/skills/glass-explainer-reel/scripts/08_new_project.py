#!/usr/bin/env python3
"""Step 8 - scaffold the HyperFrames project.   08_new_project.py <slug> "<Title>"
Creates <projects folder>/<slug>-glass with the engine + kit, the fonts, the creator's profile picture (a neutral grey
one when none was supplied), the creator's reel covers and brand images when they gave any, the brand values
(assets/brand.json), the pre-cropped camera files (links), captions and a starter build.py.
Re-run with --refresh after changing captions or crops (never overwrites build.py)."""
import json, os, shutil, subprocess, sys
from fractions import Fraction
from common import work, load, brand, brand_files, avatar_path, font_report, SKILL, PDIR, PROJECTS_ROOT
slug = sys.argv[1]; W = work(slug); M = load(W, "meta.json"); C = load(W, "crops.json") or sys.exit("run 06_crops.py first")
PJ = f"{PROJECTS_ROOT}/{slug}-glass"; refresh = "--refresh" in sys.argv
title = next((a for a in sys.argv[2:] if not a.startswith("--")), M["stem"]); media = f"{M['out']}/hf-media"
if not os.path.exists(PJ):
    os.makedirs(PROJECTS_ROOT, exist_ok=True)
    subprocess.run(["npx", "-y", "hyperframes@latest", "init", f"{slug}-glass", "--non-interactive", "--example=blank", "--skill=general-video"], cwd=PROJECTS_ROOT, check=True, capture_output=True)
elif not refresh: sys.exit(f"{PJ} exists. Use --refresh to update captions / crops / engine without touching build.py.")
os.makedirs(f"{PJ}/assets/fonts", exist_ok=True); os.makedirs(f"{PJ}/assets/media", exist_ok=True)
for f in os.listdir(f"{SKILL}/assets/fonts"): shutil.copy(f"{SKILL}/assets/fonts/{f}", f"{PJ}/assets/fonts/{f}")
for f, src in brand_files().items(): shutil.copy(src, f"{PJ}/assets/{f}")
for f in ("glass_engine.py", "glass_kit.py"): shutil.copy(f"{SKILL}/engine/{f}", f"{PJ}/{f}")

# the creator's profile picture: shown on "me" nodes and as the sender of a notification. None supplied = a neutral grey one, listed as a mock-up.
os.makedirs(f"{PJ}/assets/proof", exist_ok=True); av = avatar_path(); avatar = "profile"
if av: shutil.copy(av, f"{PJ}/assets/proof/avatar.jpg")
else:
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (400, 400), (58, 58, 60)); d = ImageDraw.Draw(im)
    d.ellipse((140, 70, 260, 190), fill=(142, 142, 147)); d.ellipse((60, 230, 340, 520), fill=(142, 142, 147))
    im.save(f"{PJ}/assets/proof/avatar.jpg", quality=92); avatar = "placeholder"

# the creator's own reel covers (optional): copied in at setup into <profile>/assets/reels, linked file by file
for src in (f"{SKILL}/assets/reels", f"{PDIR}/assets/reels"):
    if os.path.isdir(src):
        os.makedirs(f"{PJ}/assets/reels", exist_ok=True)
        for f in os.listdir(src):
            d = f"{PJ}/assets/reels/{f}"
            if not os.path.lexists(d): os.symlink(os.path.join(src, f), d)
        break
B = brand(W); json.dump(B, open(f"{PJ}/assets/brand.json", "w"), indent=1)
for f in ("cam_full.mp4", "cam_panel.mp4", "cam_panel_fg.webm"):
    d = f"{PJ}/assets/{f}"
    if os.path.lexists(d): os.remove(d)
    if os.path.exists(f"{media}/{f}"): os.symlink(f"{media}/{f}", d)
for f in ("captions.json", "cut_words.json", "cuts.json"):
    if os.path.exists(f"{W}/{f}"): shutil.copy(f"{W}/{f}", f"{PJ}/{f}")
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{media}/cam_full.mp4"]))
json.dump({"title": title, "slug": slug, "work": W, "out": M["out"], "stem": M["stem"], "dur": round(dur, 3), "fps": float(Fraction(M["fps"])), "fps_str": M["fps"],
           "panel": C["pn"], "cap": C["cap"], "popout": C["popout"], "avatar": avatar}, open(f"{PJ}/project.json", "w"), indent=1)
if not os.path.exists(f"{PJ}/build.py"):
    open(f"{PJ}/build.py", "w").write(open(f"{SKILL}/templates/build.py").read().replace("__TITLE__", title))
print(f"project {PJ} | {dur:.2f}s at {M['fps']} fps | accent {B['accent']} | watermark {B.get('handle') or 'off'} | profile picture: {avatar}")
if avatar == "placeholder": print("NOTE no profile picture on file: a neutral grey one is used and listed as a mock-up. Put avatar.jpg in the creator profile assets folder and run setup/apply_profile.py, then --refresh.")
for l in font_report(): print(l)
if not os.path.exists(f"{PJ}/captions.json"): print("WARNING no captions.json yet: run 07_captions.py then 08_new_project.py --refresh")
