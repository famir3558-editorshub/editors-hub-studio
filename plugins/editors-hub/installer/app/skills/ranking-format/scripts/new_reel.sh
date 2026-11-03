#!/bin/zsh
# new_reel.sh <project_dir> <cam_full.mp4> <cut_words.json> [fps]
# Scaffold a ranking-format project. cam_full.mp4 = the 9:16 TIGHT CUT of the presenter (1080x1920); words.json = [[start, end, word], ...] of that cut.
# Media is linked, not copied: keep the project on the same drive as the cut. Fonts saved as local fonts need no file copy.
set -e; P=$1; M=$2; W=$3; FPS=${4:-30000/1001}; K=~/.claude/skills/ranking-format
[ -f "$M" ] || { echo "no cam_full at $M"; exit 1; }
mkdir -p "$P/assets/fonts" "$P/assets/items" "$P/review" "$P/work"; N=$(basename "$P")
cp $K/assets/fonts/* "$P/assets/fonts/" 2>/dev/null || true; cp $K/assets/hyperframes.json "$P/"; cp $K/engine/rank_engine.py "$P/"; cp "$W" "$P/words.json"; echo -n $FPS > "$P/fps.txt"
ln -sf "$M" "$P/assets/cam_full.mp4"
echo "{\"id\":\"$N\",\"name\":\"$N\",\"createdAt\":\"$(date -u +%Y-%m-%dT%H:%M:%S.000Z)\"}" > "$P/meta.json"
echo "{ \"name\": \"$N\", \"private\": true, \"type\": \"module\" }" > "$P/package.json"
[ -f "$P/plan.json" ] || cp $K/examples/plan.example.json "$P/plan.json"
echo "project: $P  -> fill plan.json, put item images in assets/items/, then: python3 $K/scripts/layout.py $P"
