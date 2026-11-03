#!/bin/zsh
# final.sh <project_dir> <voice_file> "<out.mp4>"     ONLY after the creator approves the preview. Full-quality render + their voice (about -16 LUFS).
# Music and sound effects are not added here: follow the creator's music rule, then use business-short-form-reels/engine/mix.py on this file.
set -e; P=$1; V=$2; OUT=$3; cd "$P"; python3 build.py
D=$(python3 -c "import re;print(re.search(r'data-duration=\"([\d.]+)\"', open('index.html').read()).group(1))")
npx --yes hyperframes@0.8.140 render -o work/_final_v.mp4 --fps $(cat fps.txt) --quality looks 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | grep -E "rendered in|✗" || true
AF="loudnorm=I=${LUFS:--16}:TP=-1.5:LRA=11"; [ -n "$VOICE_RAW" ] && AF="anull"
ffmpeg -v error -y -i work/_final_v.mp4 -i "$V" -map 0:v -map 1:a -c:v copy -af "$AF" -ar 48000 -c:a aac -b:a 320k -t $D -movflags +faststart "$OUT"
echo "final: $OUT"
