#!/bin/zsh
# Step 7 — pre-crop the camera for the reel (keeps preview + render fast).
#   07_crops.sh "<CUT 16x9.mp4>" "<out_dir>/hf-media" [top: w h x y] [full: w h x y]
# cam_top.mp4  = 9:8 crop  -> 1080x960, CARRIES THE AUDIO (top half in split mode)
# cam_full.mp4 = 9:16 crop -> 1080x1920, muted (full-screen face windows)
# cam_fg.webm  = the same crop with the background removed (for graphics behind the creator's head)
# Defaults are the crops saved at setup for the creator's usual camera set-up (source pixels). Check with a still first; shift x so the face is centred.
set -e; C=$1; O=$2; mkdir -p "$O"
DT=(@@CROP_TOP@@); DF=(@@CROP_FULL@@)
TW=${3:-$DT[1]} TH=${4:-$DT[2]} TX=${5:-$DT[3]} TY=${6:-$DT[4]}; FW=${7:-$DF[1]} FH=${8:-$DF[2]} FX=${9:-$DF[3]} FY=${10:-$DF[4]}
ffmpeg -v error -y -i "$C" -vf "crop=$TW:$TH:$TX:$TY,scale=1080:960:flags=lanczos" -c:v libx264 -crf 15 -preset medium -pix_fmt yuv420p -c:a aac -b:a 320k -movflags +faststart "$O/cam_top.mp4"
ffmpeg -v error -y -i "$C" -an -vf "crop=$FW:$FH:$FX:$FY,scale=1080:1920:flags=lanczos" -c:v libx264 -crf 15 -preset medium -pix_fmt yuv420p -movflags +faststart "$O/cam_full.mp4"
# cam_fg.webm = the creator cut out of cam_full (transparent). Lets FACE-window graphics sit BEHIND the head.
# ~0.13 s per frame (a 60 s reel takes ~3 min). Skip with NO_MATTE=1 when the reel has no behind-the-head graphics.
if [ -z "$NO_MATTE" ]; then npx hyperframes remove-background "$O/cam_full.mp4" -o "$O/cam_fg.webm" --quality best > "$O/matte.log" 2>&1 || echo "matte failed - see $O/matte.log"; fi
ls -la "$O"
