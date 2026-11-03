#!/bin/zsh
# Strip of stills from a finished reel:  reel_sheet.sh <reel.mp4> <out.jpg> 2 8 20 ...  (seconds)
set -e; source ~/.claude/skills/split-reel/scripts/kit_env.sh
V=$1; O=$2; shift 2; T=$(mktemp -d "$WORK/sheet.XXXX"); ins=(); n=0
for t in "$@"; do ffmpeg -v error -y -ss $t -i "$V" -frames:v 1 -vf scale=270:480 "$T/$n.jpg"; ins+=(-i "$T/$n.jpg"); n=$((n+1)); done
ffmpeg -v error -y "${ins[@]}" -filter_complex "hstack=$n" "$O" && echo "$O"
