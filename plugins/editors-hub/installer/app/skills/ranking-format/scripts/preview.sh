#!/bin/zsh
# preview.sh <project_dir> <voice_file> ["<label>"]
# Build, render a draft, scale to 720p, put the CUT's voice on it (raised to about -16 LUFS, nothing else; VOICE_RAW=1 skips that),
# make a one-frame-per-second contact sheet. The creator watches review/preview_720.mp4 and approves (or sends notes) BEFORE final.sh runs.
# review/original_720.mp4 is the uncut-by-graphics camera version for side-by-side comparison.
# If you keep an external review tool, set REVIEW_HOOK to an executable that is called as: $REVIEW_HOOK <label> <preview> <events.json> <words.json>
set -e; P=$1; V=$2; LABEL=${3:-$(basename "$P")}; cd "$P"; python3 rank_engine.py
D=$(python3 -c "import json;print(json.load(open('plan.json'))['duration'])")
npx --yes hyperframes@0.8.140 render -o review/_v.mp4 --fps $(cat fps.txt) -q draft 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | grep -E "rendered in|✗" || true
AF="loudnorm=I=-16:TP=-1.5:LRA=11,"; [ -n "$VOICE_RAW" ] && AF=""
ffmpeg -v error -y -i review/_v.mp4 -i "$V" -map 0:v -map 1:a -vf scale=720:1280 -c:v libx264 -preset medium -b:v 3M -af "${AF}afade=t=out:st=$((D-0.15)):d=0.15" -ar 48000 -c:a aac -b:a 128k -t $D -movflags +faststart review/preview_720.mp4
[ -f review/original_720.mp4 ] || ffmpeg -v error -y -i assets/cam_full.mp4 -i "$V" -map 0:v -map 1:a -t $D -vf scale=720:1280 -c:v libx264 -b:v 3M -c:a aac -b:a 128k review/original_720.mp4
ffmpeg -v error -y -i review/preview_720.mp4 -vf "fps=1,scale=240:426,tile=8x$(python3 -c "import math;print(math.ceil($D/8))")" -frames:v 1 work/sheet.jpg
if [ -n "$REVIEW_HOOK" ] && [ -x "$REVIEW_HOOK" ]; then "$REVIEW_HOOK" "$LABEL" review/preview_720.mp4 review_events.json review_words.json | tail -1; fi
echo "preview: $P/review/preview_720.mp4   ($LABEL)"
echo "look at work/sheet.jpg (1 frame per second) before handing over"
