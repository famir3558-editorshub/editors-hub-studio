#!/bin/zsh
# Render every scene panel of a split reel to <out_dir>/Animations/"NN - Name.mp4".
#   render_scenes.sh <kit src folder, e.g. myReel> <PREFIX> [scene ids...]
# Reads src/<folder>/reel.json in the kit; comps are registered as <PREFIX>-<scene id>.
set -e
source ~/.claude/skills/split-reel/scripts/kit_env.sh
DIR=$1; PREFIX=$2; shift 2
REEL=$KIT/src/$DIR/reel.json
OUT=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['out_dir'])" "$REEL")/Animations
mkdir -p "$OUT"
IDS=(${@:-$(python3 -c "import json,sys;print(' '.join(s['id'] for s in json.load(open(sys.argv[1]))['scenes']))" "$REEL")})
cd "$KIT" && npx remotion bundle src/index.ts --out-dir "$WORK/bundle" >"$WORK/bundle.log" 2>&1 || { echo "bundle failed:"; tail -30 "$WORK/bundle.log"; exit 1; }
for id in ${=IDS}; do
  f="$OUT/${id/-/ - }.mp4"
  npx remotion render "$WORK/bundle" "${PREFIX}-${id}" "$f" --codec=h264 --crf=14 --concurrency=4 >"$WORK/render-$id.log" 2>&1 && echo "ok  $f" || { echo "FAIL $id (see $WORK/render-$id.log)"; exit 1; }
done
