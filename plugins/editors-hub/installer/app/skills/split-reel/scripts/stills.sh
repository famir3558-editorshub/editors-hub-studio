#!/bin/zsh
# Framing check: 4 source stills with the 9:8 (top half) and 9:16 (full screen) crop drawn on.
#   stills.sh <cut.mp4> <out.jpg> [reel.json | top w h x y [fs w h x y]]
# With a reel.json the crops are read from it; with numbers they are used as given; with neither, a centred default.
set -e; V=$1; O=$2
if [[ "$3" == *.json ]]; then
  read TW TH TX TY FW FH FX FY < <(python3 -c "import json,sys;c=json.load(open(sys.argv[1]));print(*c['top_crop'],*c['fs_crop'])" "$3")
else
  W=$(ffprobe -v error -select_streams v -show_entries stream=width -of csv=p=0 "$V"); H=$(ffprobe -v error -select_streams v -show_entries stream=height -of csv=p=0 "$V")
  read DTW DTH DTX DTY DFW DFH DFX DFY < <(python3 -c "
W,H=$W,$H
fw=H*9//16; tw=int(W*0.47)//8*8; th=tw*8//9
print(tw,th,(W-tw)//2,min(round(H*0.09),H-th),fw,H,(W-fw)//2,0)")
  TW=${3:-$DTW} TH=${4:-$DTH} TX=${5:-$DTX} TY=${6:-$DTY}; FW=${7:-$DFW} FH=${8:-$DFH} FX=${9:-$DFX} FY=${10:-$DFY}
fi
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V"); source ~/.claude/skills/split-reel/scripts/kit_env.sh
T=$(mktemp -d "$WORK/frame.XXXX"); ins=()
for k in 1 2 3 4; do t=$(python3 -c "print($D*$k/5)"); ffmpeg -v error -y -ss $t -i "$V" -frames:v 1 \
  -vf "drawbox=$TX:$TY:$TW:$TH:color=orange@0.9:t=12,drawbox=$FX:$FY:$FW:$FH:color=cyan@0.8:t=8,scale=960:-2" "$T/$k.jpg"; ins+=(-i "$T/$k.jpg"); done
ffmpeg -v error -y "${ins[@]}" -filter_complex "[0][1]hstack[a];[2][3]hstack[b];[a][b]vstack" "$O" && echo "$O  (orange = top half, cyan = full screen)"
