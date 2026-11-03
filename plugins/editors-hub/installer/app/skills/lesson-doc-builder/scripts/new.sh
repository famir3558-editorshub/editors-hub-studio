#!/usr/bin/env bash
# Usage: new.sh <slug>   e.g. new.sh ep03-topic-name  ->  <docs folder>/ep03-topic-name/doc.html
# Also refreshes doc.css, doc.js and fonts/ in an existing doc folder (use after a colour or font change).
set -e
SK="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$SK/.configured" ] || { echo "Setup has not been run for this skill yet: read setup/SETUP.md first."; exit 1; }
[ -n "$1" ] || { echo "usage: new.sh <slug>"; exit 1; }
ROOT="@@DOCS_ROOT@@"; ROOT="${ROOT/#\~/$HOME}"; D="$ROOT/$1"
mkdir -p "$D/assets" "$D/fonts"; cp "$SK/assets/doc.css" "$SK/assets/doc.js" "$D/"
cp "$SK"/assets/fonts/* "$D/fonts/" 2>/dev/null || true
[ -f "$D/doc.html" ] || cp "$SK/assets/starter.html" "$D/doc.html"
echo "$D/doc.html"
