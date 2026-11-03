#!/bin/zsh
# Safe-zone check on the RENDERED reel.   safe_check.sh "<reel.mp4>" <out.jpg> <t1> <t2> ...
# Lays assets/safe-zone.png over frames at the given seconds and tiles them. Red bands = Instagram/TikTok interface
# (top 270 px, bottom 420 px; the orange strip y 1500-1585 is the ~20% overrun is allowed at the bottom); yellow box = button rail; dashed yellow line (y 1250) = captions must end above it.
# Nothing the creator needs the viewer to read or watch may sit in red; no caption may cross the dashed line.
set -e; F=$1; O=$2; shift 2; G=${0:A:h:h}/assets/safe-zone.png; T=$(mktemp -d)
i=0; for t in "$@"; do i=$((i+1)); ffmpeg -v error -y -ss $t -i "$F" -i "$G" -filter_complex "[0:v]scale=1080:1920[v];[v][1:v]overlay,scale=432:-1" -frames:v 1 -update 1 "$T/$(printf %03d $i).jpg"; done
python3 - "$T" "$O" <<'P'
import sys, glob
from PIL import Image
fs = sorted(glob.glob(sys.argv[1] + "/*.jpg")); ims = [Image.open(f) for f in fs]; n = len(ims); cols = min(n, 6); rows = -(-n // cols)
w, h = ims[0].size; s = Image.new("RGB", (w * cols, h * rows))
for k, im in enumerate(ims): s.paste(im, ((k % cols) * w, (k // cols) * h))
s.save(sys.argv[2], quality=88); print(sys.argv[2], s.size)
P
