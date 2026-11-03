#!/bin/zsh
# Step 8 — scaffold the HyperFrames project.   08_new_reel.sh <slug> "<Title>" "<out_dir>"
#   e.g. 08_new_reel.sh pricing-story-hf "Pricing Story" ".../Pricing Story - Edit"
# Needs <out_dir>/hf-media/cam_top.mp4 + cam_full.mp4 (07_crops.sh). Creates @@PROJECTS_ROOT@@/<slug>:
#   assets/{brand.css, fonts, reels (if any), proof/avatar.jpg, cam_top.mp4, cam_full.mp4}, reel_engine.py, kit.py, mix.py, sfx_map.json, build.py (starter), BRIEF.md
set -e; SK=${0:A:h:h}; SLUG=$1; TITLE=$2; OUT=$3; PR="@@PROJECTS_ROOT@@"; PR="${PR/#\~/$HOME}"; P="$PR/$SLUG"
[ -e "$P" ] && { echo "$P already exists"; exit 1; }
[ -f "$OUT/hf-media/cam_top.mp4" ] || { echo "missing $OUT/hf-media/cam_top.mp4 — run 07_crops.sh first"; exit 1; }
mkdir -p "$PR" && cd "$PR" && npx -y hyperframes@latest init "$SLUG" --non-interactive --example=blank --skill=general-video >/dev/null
cd "$P"; mkdir -p assets/proof assets/clips compositions
cp "$SK/assets/brand.css" assets/; cp -R "$SK/assets/fonts" assets/; [ -d "$SK/assets/reels" ] && cp -R "$SK/assets/reels" assets/
[ -f "$SK/assets/avatar.jpg" ] && cp "$SK/assets/avatar.jpg" assets/proof/avatar.jpg; [ -f "$SK/assets/sfx_map.json" ] && cp "$SK/assets/sfx_map.json" .
ln -sf "$OUT/hf-media/cam_top.mp4" assets/cam_top.mp4; ln -sf "$OUT/hf-media/cam_full.mp4" assets/cam_full.mp4
[ -f "$OUT/hf-media/cam_fg.webm" ] && ln -sf "$OUT/hf-media/cam_fg.webm" assets/cam_fg.webm
cp "$SK/engine/reel_engine.py" "$SK/engine/kit.py" "$SK/engine/mix.py" .
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/hf-media/cam_top.mp4")
sed -e "s/__TITLE__/$TITLE/" -e "s/__DUR__/$DUR/" "$SK/templates/build.py" > build.py
cat > BRIEF.md <<B
---
workflow: general-video
flow: automation
storyboard: no
message: "$TITLE"
destination: Instagram Reels / TikTok
aspect: "9:16"
language: en
---
## Intent
Business short-form reel for @@CREATOR_NAME@@ (skill: business-short-form-reels). Split / full-face / full-animation rotation, captions under the chin.
## Notes
Output dir: $OUT
B
echo "created $P  (DUR $DUR). Next: write captions.json (06_captions.py), then the scenes in build.py."
