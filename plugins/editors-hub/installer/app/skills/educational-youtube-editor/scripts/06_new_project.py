#!/usr/bin/env python3
"""Step 6 - scaffold the HyperFrames project.   06_new_project.py <slug> "<Title>" [--no-cut] [--face X,Y] [--refresh]
Creates <projects root>/<slug>-yt with the engine + kit, fonts, the creator's logo / wordmark / profile picture when they gave
them at setup, the working copy of the cut (1080p, or 2160p for a 4K master from a 4K source; on the output drive, linked in),
the cut's words and joins, and starter build.py / content_map.json / edit_plan.json.
--no-cut   the video is already edited: use it as it is (steps 3-5 skipped; words come straight from the transcript)
--face     where their face centre is in the 1920x1080 frame. Open <project>/face-check.jpg (it has a labelled grid),
           read the position, and re-run with --refresh --face X,Y. Split screens centre them using this.
--refresh  update words / engine / face without touching build.py, content_map.json or edit_plan.json."""
import json, os, shutil, subprocess, sys
from fractions import Fraction
from common import work, load, save, brand, brand_files, font_report, master_4k, grab, label_font, pj, SKILL, PROJECTS_ROOT
slug = sys.argv[1]; W = work(slug); M = load(W, "meta.json") or sys.exit("run 01_prep.py first"); refresh = "--refresh" in sys.argv
title = next((a for a in sys.argv[2:] if not a.startswith("--") and "," not in a), M["stem"]); PJ = pj(slug)
if "--no-cut" in sys.argv:
    words = load(W, "words.json") or sys.exit("run 02_transcribe.py first")
    M["cut"] = M["src"]; M["cut_dur"] = M["dur"]; save(W, "meta.json", M)
    save(W, "cut_words.json", [[t, s, e, i] for i, (t, s, e) in enumerate(words)]); save(W, "cuts.json", [])
M.get("cut") and os.path.exists(M["cut"]) or sys.exit("no cut yet: run 03-05, or pass --no-cut for an already-edited video")
if not os.path.exists(PJ):
    os.makedirs(PROJECTS_ROOT, exist_ok=True)
    subprocess.run(["npx", "-y", "hyperframes@latest", "init", f"{slug}-yt", "--non-interactive", "--example=blank", "--skip-transcribe", "--skill=talking-head-recut"], cwd=PROJECTS_ROOT, check=True, capture_output=True)
elif not refresh: sys.exit(f"{PJ} exists. Use --refresh to update words / engine / face without touching build.py.")
for d in ("assets/fonts", "assets/media", "review"): os.makedirs(f"{PJ}/{d}", exist_ok=True)
for f in os.listdir(f"{SKILL}/assets/fonts"): shutil.copy(f"{SKILL}/assets/fonts/{f}", f"{PJ}/assets/fonts/{f}")
shutil.copy(f"{SKILL}/assets/gsap.min.js", f"{PJ}/assets/gsap.min.js")
BF = brand_files()                                # optional: logo.png, wordmark.png, avatar.jpg (E.brand_asset("logo") finds them in a build)
for f, p in BF.items(): shutil.copy(p, f"{PJ}/assets/{f}")
if os.path.exists(f"{SKILL}/assets/sfx_map.json") and not os.path.exists(f"{PJ}/sfx_map.json"): shutil.copy(f"{SKILL}/assets/sfx_map.json", f"{PJ}/sfx_map.json")
for f in ("yt_engine.py", "yt_kit.py"): shutil.copy(f"{SKILL}/engine/{f}", f"{PJ}/{f}")
media = f"{M['out']}/hf-media"; os.makedirs(media, exist_ok=True); cam = f"{media}/cam.mp4"; fps = M["fps"]
if not os.path.exists(cam) or os.path.getmtime(cam) < os.path.getmtime(M["cut"]):
    big = master_4k() and max(M["w"], M["h"]) >= 3000; cw, ch = (3840, 2160) if big else (1920, 1080)   # the page is always 1920x1080; a 4K master renders it at 2x
    print(f"making the {ch}p working copy (dense keyframes so the renderer can seek anywhere) ...")
    if master_4k() and not big: print("NOTE a 4K master was asked for but the source is not 4K: the footage will be upscaled. A 1080p master is the honest choice for this video.")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", M["cut"], "-an", "-vf", f"scale={cw}:{ch}:force_original_aspect_ratio=increase,crop={cw}:{ch},setsar=1", "-r", fps,
                    "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-g", "12", "-pix_fmt", "yuv420p", "-movflags", "+faststart", cam], check=True)
if os.path.lexists(f"{PJ}/assets/cam.mp4"): os.remove(f"{PJ}/assets/cam.mp4")
os.symlink(cam, f"{PJ}/assets/cam.mp4")
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", cam]))
for f in ("cut_words.json", "cuts.json"): shutil.copy(f"{W}/{f}", f"{PJ}/{f}")
old = json.load(open(f"{PJ}/project.json")) if os.path.exists(f"{PJ}/project.json") else {}
face = [int(x) for x in sys.argv[sys.argv.index("--face") + 1].split(",")] if "--face" in sys.argv else old.get("face", [960, 400])
B = brand(W)
json.dump({"title": title, "slug": slug, "work": W, "out": M["out"], "stem": M["stem"], "cut": M["cut"], "dur": round(dur, 4), "fps": float(Fraction(fps)), "fps_str": fps,
           "face": face, "skill": SKILL, "accent": B["accent"], "master": "4k" if master_4k() else "1080p", "chunk": old.get("chunk", 240)}, open(f"{PJ}/project.json", "w"), indent=1)
from PIL import Image, ImageDraw
tmp = f"{PJ}/review/_f.jpg"; grab(cam, dur * 0.12, tmp); im = Image.open(tmp).convert("RGB"); d = ImageDraw.Draw(im); f = label_font(22)
for x in range(0, 1920, 160): d.line([(x, 0), (x, 1080)], fill=(255, 255, 255), width=1); d.text((x + 4, 4), str(x), fill=(255, 220, 0), font=f)
for y in range(0, 1080, 135): d.line([(0, y), (1920, y)], fill=(255, 255, 255), width=1); d.text((4, y + 4), str(y), fill=(255, 220, 0), font=f)
d.ellipse([face[0] - 14, face[1] - 14, face[0] + 14, face[1] + 14], outline=(255, 80, 0), width=5); im.save(f"{PJ}/face-check.jpg", quality=85); os.remove(tmp)
for name in ("build.py", "content_map.json", "edit_plan.json"):
    if not os.path.exists(f"{PJ}/{name}"): open(f"{PJ}/{name}", "w").write(open(f"{SKILL}/templates/{name}").read().replace("__TITLE__", title))
if not os.path.exists(f"{PJ}/assets.json"): json.dump([], open(f"{PJ}/assets.json", "w"))
print(f"project {PJ} | {dur / 60:.1f} min at {fps} fps | face {face} (check {PJ}/face-check.jpg: the ring should sit on the nose)")
print("brand images:", ", ".join(BF) if BF else "none given at setup (fine: nothing needs them)")
print("\n".join(font_report()) or "fonts: none named in the profile yet")
