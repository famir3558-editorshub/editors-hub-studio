#!/bin/zsh
# Contact sheet of panel stills:  qa_stills.sh <folder> <PREFIX> <out.jpg> "01-Hook:85" "04-Part:120" ...
# (frame numbers are within each scene; pick the end of each beat). Look at every tile.
set -e
source ~/.claude/skills/split-reel/scripts/kit_env.sh
DIR=$1; PREFIX=$2; OUTJ=$3; shift 3
Q=$(mktemp -d "$WORK/qa.XXXX")
cd "$KIT" && npx remotion bundle src/index.ts --out-dir "$WORK/bundle" >"$WORK/bundle.log" 2>&1 || { echo "bundle failed:"; tail -30 "$WORK/bundle.log"; exit 1; }
for spec in "$@"; do id=${spec%%:*}; f=${spec##*:}; npx remotion still "$WORK/bundle" "${PREFIX}-${id}" "$Q/${id}_$(printf %04d $f).png" --frame=$f >/dev/null 2>&1 & done; wait
ffmpeg -v error -y -pattern_type glob -i "$Q/*.png" -vf "scale=540:480,tile=4x4:padding=6:color=gray" "$OUTJ" && echo "$OUTJ"
