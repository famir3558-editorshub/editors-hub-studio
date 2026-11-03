#!/bin/zsh
# Contact sheet of a rendered reel at given times (use ±0.04s around EVERY mode cut + a few mid-scene).
#   sheet.sh "<reel.mp4>" <out.jpg> t1 t2 ...
set -e; R=$1; O=$2; shift 2; T=$(dirname "$O")/.sheet_tmp; mkdir -p "$T"; rm -f "$T"/q_*.jpg(N); i=0
for t in "$@"; do i=$((i+1)); ffmpeg -v error -y -ss $t -i "$R" -frames:v 1 -vf scale=216:384 "$T/q_$(printf %03d $i).jpg"; done
ffmpeg -v error -y -pattern_type glob -i "$T/q_*.jpg" -vf "tile=10x$(( (i+9)/10 )):padding=4:color=gray" "$O" && echo "$O"
