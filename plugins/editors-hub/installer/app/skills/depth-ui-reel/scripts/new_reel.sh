#!/bin/zsh
# new_reel.sh <project_dir> <media_dir> <cut_words.json> [fps]
# Scaffold a depth UI reel project. media_dir must hold cam_full.mp4 (the 9:16 tight cut of the creator, silent) and cam_fg.webm (the creator
# cut out, same timing). Both come from the business-short-form-reels skill (its 07_crops.sh), or from any 9:16 tight cut plus
#   npx hyperframes remove-background cam_full.mp4 -o cam_fg.webm --quality best
# Media is linked, not copied. Keep the project on the internal drive (it has symlinks); renders may go anywhere.
# Also copies in, when setup saved them: the creator's profile picture (assets/real/avatar.jpg) and reel covers (assets/reels/).
set -e; P=$1; M=$2; W=$3; FPS=${4:-30000/1001}; K=~/.claude/skills/depth-ui-reel
[ -f "$M/cam_full.mp4" ] || { echo "no cam_full.mp4 in $M"; exit 1; }
[ -f "$M/cam_fg.webm" ] || { echo "no cam_fg.webm in $M - run: npx hyperframes remove-background \"$M/cam_full.mp4\" -o \"$M/cam_fg.webm\" --quality best"; exit 1; }
mkdir -p "$P/assets/fonts" "$P/assets/real" "$P/assets/yt" "$P/assets/reels" "$P/review" "$P/work"; N=$(basename "$P")
cp $K/assets/fonts/* "$P/assets/fonts/"; cp $K/assets/hyperframes.json "$P/"; cp $K/engine/depth_engine.py "$P/"; cp "$W" "$P/words.json"; echo -n $FPS > "$P/fps.txt"
[ -f "$K/assets/avatar.jpg" ] && cp "$K/assets/avatar.jpg" "$P/assets/real/avatar.jpg" || echo "note: no profile picture saved at setup - channel cards will show a letter tile"
[ -d "$K/assets/reels" ] && cp -n "$K"/assets/reels/* "$P/assets/reels/" 2>/dev/null || true
ln -sf "$M/cam_full.mp4" "$P/assets/cam_full.mp4"; ln -sf "$M/cam_fg.webm" "$P/assets/cam_fg.webm"
echo "{\"id\":\"$N\",\"name\":\"$N\",\"createdAt\":\"$(date -u +%Y-%m-%dT%H:%M:%S.000Z)\"}" > "$P/meta.json"
cat > "$P/package.json" <<JSON
{ "name": "$N", "private": true, "type": "module",
  "scripts": { "check": "npx --yes hyperframes@0.8.140 check", "render": "npx --yes hyperframes@0.8.140 render" } }
JSON
[ -f "$P/build.py" ] || cp $K/examples/worked-example/build.py "$P/build.py"
echo "project: $P  (edit build.py: DUR, emph, camera blocks, beats; put real thumbnails in assets/yt, covers in assets/reels)"
