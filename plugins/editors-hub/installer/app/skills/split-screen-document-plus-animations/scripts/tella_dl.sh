#!/bin/bash
# tella_dl.sh "<signed output.m3u8 url from the Tella connector's list_sources>" "<out.mp4>"
# Tella's raw sources are signed HLS: every sub-playlist and segment needs the same query string. Segments are fMP4, so
# they are joined as they are and remuxed (no re-encode). Never run this inside sh -c '...': titles contain apostrophes.
u="$1"; out="$2"; q="${u#*\?}"; base="${u%/output.m3u8*}"
W="$(dirname "$out")/.dl_$$"; mkdir -p "$W"
curl -s "$u" > "$W/master.m3u8"
vpl=$(grep -v '^#' "$W/master.m3u8" | head -1)
apl=$(grep -o 'URI="[^"]*"' "$W/master.m3u8" | head -1 | sed 's/URI="//;s/"//')
for kind in v a; do
  pl=$vpl; [ $kind = a ] && pl=$apl
  [ -z "$pl" ] && continue
  curl -s "$base/$pl?$q" > "$W/$kind.m3u8"
  { grep -o 'MAP:URI="[^"]*"' "$W/$kind.m3u8" | sed 's/MAP:URI="//;s/"//'; grep -v '^#' "$W/$kind.m3u8"; } > "$W/$kind.list"
  mkdir -p "$W/$kind"; export W kind base q
  cat "$W/$kind.list" | xargs -P 8 -n 1 sh -c '[ -s "$W/$kind/$0" ] || curl -s --retry 5 -f -o "$W/$kind/$0" "$base/$0?$q" || echo FAIL $0'
  n=$(wc -l < "$W/$kind.list"); have=$(ls "$W/$kind" | wc -l)
  echo "$kind: $have/$n segments"
  [ "$have" -ne "$n" ] && { echo "INCOMPLETE ($kind): re-run, finished segments are kept"; exit 1; }
  while read f; do cat "$W/$kind/$f"; done < "$W/$kind.list" > "$W/$kind.mp4"
done
if [ -s "$W/a.mp4" ]; then ffmpeg -nostdin -v error -y -i "$W/v.mp4" -i "$W/a.mp4" -map 0:v -map 1:a -c copy -movflags +faststart "$out"
else ffmpeg -nostdin -v error -y -i "$W/v.mp4" -c copy -movflags +faststart "$out"; fi && rm -rf "$W" && echo "DONE $(ls -lh "$out" | awk '{print $5}') $out"
