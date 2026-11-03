#!/bin/zsh
# Scaffold the HyperFrames project for a personal short-form reel.   new_project.sh <slug> "<Title>" "<out dir>"
#   needs <out dir>/hf-media/cam_full.mp4 + cam_top.mp4 (prep_cams.py). Creates @@PROJECTS_ROOT@@/<slug>-psf with:
#   assets/{brand.css, fonts, proof/avatar.jpg, cam_*.mp4 -> out dir, broll/ screen/ -> out dir, logos/},
#   reel_engine.py, kit.py, psf.py, mix.py, sfx_map.json, build.py (starter), words.json if <work>/cut/words.json is passed as a 4th argument.
set -e; SK=${0:A:h:h}; SLUG=$1; TITLE=$2; OUT=$3; PR="@@PROJECTS_ROOT@@"; PR="${PR/#\~/$HOME}"; P="$PR/$SLUG-psf"
[ -e "$P" ] && { echo "$P already exists"; exit 1; }
[ -f "$OUT/hf-media/cam_top.mp4" ] || { echo "missing $OUT/hf-media/cam_top.mp4 - run prep_cams.py first"; exit 1; }
mkdir -p "$PR" && cd "$PR" && npx -y hyperframes@latest init "$SLUG-psf" --non-interactive --example=blank --skill=general-video >/dev/null
cd "$P"; mkdir -p assets/proof assets/logos compositions "$OUT/hf-media/broll" "$OUT/hf-media/screen"
cp "$SK/assets/brand.css" assets/; cp -R "$SK/assets/fonts" assets/; [ -f "$SK/assets/avatar.jpg" ] && cp "$SK/assets/avatar.jpg" assets/proof/avatar.jpg; [ -f "$SK/assets/sfx_map.json" ] && cp "$SK/assets/sfx_map.json" .
ln -sf "$OUT/hf-media/cam_top.mp4" assets/cam_top.mp4; ln -sf "$OUT/hf-media/cam_full.mp4" assets/cam_full.mp4
ln -sfn "$OUT/hf-media/broll" assets/broll; ln -sfn "$OUT/hf-media/screen" assets/screen
cp "$SK/engine/reel_engine.py" "$SK/engine/kit.py" "$SK/engine/psf.py" "$SK/engine/mix.py" .
[ -n "$4" ] && cp "$4" words.json
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/hf-media/cam_full.mp4")
sed -e "s/__TITLE__/$TITLE/" -e "s/__DUR__/$DUR/" "$SK/assets/build_template.py" > build.py
echo "created $P (DUR $DUR). Next: plan the windows from cut_times.py, cut the B-roll / recording pieces into $OUT/hf-media/{broll,screen}, write build.py."
