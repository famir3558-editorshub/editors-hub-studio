#!/usr/bin/env python3
"""Step 6 — captions.   06_captions.py <cut_work>/words.json <phrases.txt> <project>/captions.json
phrases.txt: the whole script hand-phrased, ONE CAPTION PER LINE, 2-4 words each, every spoken word in order.
  Fix ASR slips in the phrase text and map them with  shown=heard  aliases on lines starting with '#alias',
  e.g.   #alias Notion=notion grow=or their=there Claude=clause
Each caption starts on its first word and holds until the next caption (max 0.5s past its last word).
Fails loudly at the first word that does not line up, so nothing drifts silently."""
import json, re, sys
W = json.load(open(sys.argv[1])); words = []
for s, e, w, *_ in W:
    if w.startswith(",") and words: words[-1][2] += w; words[-1][1] = e; continue      # "13" + ",000"
    words.append([s, e, w])
norm = lambda x: re.sub(r"[^a-z0-9']", "", x.lower().replace("’", "'"))
alias, phrases = {}, []
for ln in open(sys.argv[2]).read().splitlines():
    ln = ln.strip()
    if not ln: continue
    if ln.startswith("#alias"):
        for kv in ln.split()[1:]: k, v = kv.split("="); alias[norm(k)] = norm(v)
    elif not ln.startswith("#"): phrases.append(ln)
caps, k = [], 0
for ph in phrases:
    st = None
    for x in ph.split():
        if k >= len(words): sys.exit(f"ran out of words at {ph!r}")
        n, got = norm(x), norm(words[k][2])
        if got != n and got != alias.get(n, "#"): sys.exit(f"mismatch in {ph!r}: caption word {x!r} vs heard {words[k][2]!r} @ {words[k][0]:.2f}s")
        if st is None: st = words[k][0]
        en = words[k][1]; k += 1
    caps.append({"text": ph, "start": round(st, 3), "wend": round(en, 3)})
if k != len(words): sys.exit(f"{len(words) - k} spoken words left uncaptioned from {words[k][2]!r} @ {words[k][0]:.2f}s")
for i, c in enumerate(caps):
    nx = caps[i + 1]["start"] if i + 1 < len(caps) else c["wend"] + 0.4
    c["end"] = round(min(nx, c["wend"] + 0.5), 3)
caps[0]["start"] = 0
json.dump(caps, open(sys.argv[3], "w"), indent=0)
L = [len(c["text"].split()) for c in caps]
print(len(caps), "captions; words per caption min/max", min(L), max(L), "| over 4:", [c["text"] for c in caps if len(c["text"].split()) > 4], "| singles:", [c["text"] for c in caps if len(c["text"].split()) == 1])
