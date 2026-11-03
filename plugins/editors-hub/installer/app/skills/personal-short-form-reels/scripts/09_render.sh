#!/bin/zsh
# Step 9 — check, render, make the phone copy.   09_render.sh <project_dir> "<out_dir>" "<Title>" [suffix]
set -e; P=$1; OUT=$2; TITLE=$3; SUF=${4:-}; cd "$P"
python3 build.py
npx hyperframes check 2>&1 | grep -E "✗|Check" | head -20
F="$OUT/$TITLE - 9x16 Reel$SUF.mp4"
npx hyperframes render -o "$F" --fps 24000/1001 --quality looks --skill general-video 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | grep -E "rendered in|MB ·|rror" | tail -3
# phone copy: SendUserFile caps at 30 MB -> two-pass ~23 MB for a 60s reel (scale -b:v for longer reels)
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$F"); BR=$(python3 -c "print(int(min(2900, 23*8000/$D - 160)))")
PH="$P/renders/$TITLE$SUF (phone).mp4"; mkdir -p "$P/renders"
ffmpeg -v error -y -i "$F" -c:v libx264 -preset slow -b:v ${BR}k -maxrate $((BR*5/4))k -bufsize 6000k -pass 1 -passlogfile "$P/renders/pass" -an -f mp4 /dev/null
ffmpeg -v error -y -i "$F" -c:v libx264 -preset slow -b:v ${BR}k -maxrate $((BR*5/4))k -bufsize 6000k -pass 2 -passlogfile "$P/renders/pass" -c:a aac -b:a 160k -movflags +faststart "$PH"
echo "master: $F"; echo "phone:  $PH"
