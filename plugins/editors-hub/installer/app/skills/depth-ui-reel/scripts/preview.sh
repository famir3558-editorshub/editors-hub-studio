#!/bin/zsh
# preview.sh <project_dir> <voice_file> [seconds]
# Build, check, render a draft, scale to 720p and put the creator's voice on it: review/preview_720.mp4. voice_file = any file carrying the
# CUT's audio (the "<Title> - CUT 16x9.mp4"); it is raised to about -16 LUFS (LUFS=-17 to change), nothing else. VOICE_RAW=1 if already levelled.
# Give the creator the preview and wait for approval before final.sh. Also writes work/sheet.jpg (2 frames per second) to look at first.
set -e; P=$1; V=$2; cd "$P"; python3 build.py
D=${3:-$(python3 -c "import re;print(re.search(r'data-duration=\"([\d.]+)\"', open('index.html').read()).group(1))")}
npx --yes hyperframes@0.8.140 check 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | grep -E "✗|error\(s\)" | grep -v text_occluded || true   # text_occluded = graphics behind the head, intended
npx --yes hyperframes@0.8.140 render -o review/_v.mp4 --fps $(cat fps.txt) -q draft 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | grep -E "rendered in|✗" || true
AF="loudnorm=I=${LUFS:--16}:TP=-1.5:LRA=11,"; [ -n "$VOICE_RAW" ] && AF=""
ffmpeg -v error -y -i review/_v.mp4 -i "$V" -map 0:v -map 1:a -vf scale=720:1280 -c:v libx264 -preset medium -b:v 3M -af "${AF}afade=t=out:st=$(python3 -c "print($D-0.15)"):d=0.15" -ar 48000 -c:a aac -b:a 128k -t $D -movflags +faststart review/preview_720.mp4
ffmpeg -v error -y -i review/preview_720.mp4 -vf "fps=2,scale=240:426,tile=8x$(python3 -c "import math;print(math.ceil($D*2/8))")" -frames:v 1 work/sheet.jpg
echo "preview: $P/review/preview_720.mp4   contact sheet: $P/work/sheet.jpg  (look at it before handing over; wait for approval before final.sh)"
[ -s placeholders.txt ] && echo "placeholders (no real image found, say so in the hand-over):" && cat placeholders.txt || true
