#!/bin/zsh
# Scaffold a split reel:  new.sh <folder> <PREFIX> "<Title>" <cut.mp4> <out_dir>
#   new.sh --refresh   only refreshes the kit's brand file, kit.tsx, register.tsx and fonts (after a setup change)
#   folder  camelCase src folder, e.g. myReel          PREFIX  short caps id, e.g. MR
# First run creates the Remotion project (the kit) from the skill's kit/ folder and installs it; every run refreshes the
# kit's brand file, kit.tsx and register.tsx from the skill, then creates src/<folder>/{reel.json,<PREFIX>.tsx} with
# crops worked out from the cut's size, and registers <PREFIX>-<scene id> in src/Root.tsx.
set -e
source ~/.claude/skills/split-reel/scripts/kit_env.sh
F=$1; P=$2; TITLE=$3; SRC=$4; OUT=$5
if [ "$1" != "--refresh" ]; then
[ -n "$F" ] && [ -n "$P" ] && [ -n "$TITLE" ] && [ -f "$SRC" ] && [ -n "$OUT" ] || { echo 'usage: new.sh <folder> <PREFIX> "<Title>" <cut.mp4> <out_dir>   |   new.sh --refresh'; exit 1; }
[[ "$P" =~ ^[A-Za-z][A-Za-z0-9]*$ ]] || { echo "PREFIX must be letters and digits only"; exit 1; }
[[ "$F" =~ ^[A-Za-z][A-Za-z0-9]*$ ]] || { echo "folder must be letters and digits only"; exit 1; }
fi
grep -q '@@' "$SK/kit/src/brand.js" && { echo "This skill has not been set up yet: run the setup interview (setup/SETUP.md), then python3 $SK/setup/apply_profile.py"; exit 1; }

if [ ! -f "$KIT/package.json" ]; then
  mkdir -p "$KIT"; cp -R "$SK/kit/." "$KIT/"
else
  cp "$SK/kit/src/brand.js" "$SK/kit/src/brand.d.ts" "$KIT/src/"
  cp "$SK/kit/src/splitReel/"* "$KIT/src/splitReel/"
fi
mkdir -p "$KIT/public/fonts"
cp "$SK/assets/fonts/"* "$KIT/public/fonts/" 2>/dev/null || true
if [ ! -d "$KIT/node_modules" ]; then
  echo "installing the Remotion project in $KIT (first time only, a few minutes) ..."
  (cd "$KIT" && npm install --no-audit --no-fund)
fi
[ "$1" = "--refresh" ] && { echo "kit refreshed in $KIT (brand file, kit.tsx, register.tsx, fonts)"; exit 0; }

[ -e "$KIT/src/$F" ] && { echo "src/$F already exists in the kit"; exit 1; }
mkdir -p "$KIT/src/$F" "$OUT/Animations"
FPS=$(ffprobe -v error -select_streams v -show_entries stream=r_frame_rate -of csv=p=0 "$SRC")
DIMS=$(ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0:s=x "$SRC")
python3 - "$KIT/src/$F/reel.json" "$TITLE" "$SRC" "$OUT" "$FPS" "$DIMS" <<'PY'
import json, sys
p, title, src, out, fps, dims = sys.argv[1:]
W, H = (int(x) for x in dims.split("x"))
# 9:16 full-screen crop: full height, centred.  9:8 top-half crop: about 47% of the width, upper part of the frame.
fw = (round(H * 9 / 16) // 2) * 2; fx = ((W - fw) // 2 // 2) * 2
tw = min(W, (round(W * 0.47) // 8) * 8); th = tw * 8 // 9
tx = ((W - tw) // 2 // 2) * 2; ty = min(round(H * 0.09), H - th)
json.dump({"title": title, "source": src, "out_dir": out, "fps": fps,
           "top_crop": [tw, th, tx, max(ty, 0)], "fs_crop": [fw, H, fx, 0],
           "fullscreen": [], "scenes": [{"id": "01-Hook", "start": 0, "end": 3}]}, open(p, "w"), indent=1)
PY
python3 - "$SK/templates/Reel.tsx" "$KIT/src/$F/$P.tsx" "$TITLE" "$P" <<'PY'
import sys
src, dst, title, prefix = sys.argv[1:]
open(dst, "w").write(open(src).read().replace("__TITLE__", title).replace("__PREFIX__", prefix))
PY
python3 - "$KIT/src/Root.tsx" "$F" "$P" <<'PY'
import sys
p, f, P = sys.argv[1:]; r = open(p).read()
imp = f'import {{ {P}_COMPS }} from "./{f}/{P}";\nimport {f}Reel from "./{f}/reel.json";\n'
r = r.replace("// <split-reel:imports>", imp + "// <split-reel:imports>", 1)
r = r.replace("{/* <split-reel:comps> */}", f'<SplitReelComps prefix="{P}" reel={{{f}Reel}} comps={{{P}_COMPS}} />\n    {{/* <split-reel:comps> */}}', 1)
open(p, "w").write(r)
PY
echo "created $KIT/src/$F/{reel.json,$P.tsx}; registered $P-* in Root.tsx"
echo "next: check the crops with stills.sh, then write the scenes in reel.json and $P.tsx"
