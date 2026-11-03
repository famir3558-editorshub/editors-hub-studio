#!/usr/bin/env python3
"""Step 7 - captions for the whole video.   07_captions.py <slug>
First run: drafts <work>/phrases.txt from the verified cut (one caption per line, 1-3 words) and stops.
Edit phrases.txt, then run again to time it:
  - one caption per line, every spoken word, in order (the script refuses anything else);
  - regroup freely by moving line breaks (keep 1-3 words, never split a name or a number from its unit);
  - *word* = emphasis: that word is set in the emphasis font, accent colour, INSIDE the normal caption line
    (a figure stays in the main font, accent colour). Never a stacked or enlarged treatment;
  - {heard|Shown} fixes a mis-heard or mis-spelled word on screen ({acme|ACME}); capitals and punctuation can be
    changed directly.
Writes captions.json [{start, end, parts:[{t, em}]}] and captions.txt (read it in full)."""
import os, re, sys
from common import work, load, save, norm
W = work(sys.argv[1]); cw = load(W, "cut_words.json") or sys.exit("no cut_words.json: run 03_cut.py and 04_verify.py first")
M = load(W, "meta.json"); DUR = M.get("cut_dur", cw[-1][2]); P = f"{W}/phrases.txt"
if not os.path.exists(P):
    lines, cur = [], []
    for i, (t, s, e, _) in enumerate(cw):
        cur.append(t); last = i == len(cw) - 1
        gap = 0 if last else cw[i + 1][1] - e; chars = sum(len(x) for x in cur) + len(cur) - 1
        nxt = 0 if last else len(cw[i + 1][0])
        if last or t[-1] in ".,?!;:" or gap > 0.28 or len(cur) >= 3 or chars + 1 + nxt > 14:
            lines.append(" ".join(cur)); cur = []
    open(P, "w").write("\n".join(lines) + "\n")
    sys.exit(f"drafted {P} ({len(lines)} captions). Edit it (grouping, *emphasis*, {{heard|Shown}} fixes) and run again.")

caps, k, bad = [], 0, 0
for ln, line in enumerate(open(P).read().splitlines(), 1):
    if not line.strip(): continue
    parts, first = [], k
    for tok in line.split():
        em = tok.count("*") >= 2 or (tok.startswith("*") or tok.endswith("*")); raw = tok.replace("*", "")
        m = re.fullmatch(r"(\W*)\{([^|}]+)\|([^}]+)\}(\W*)", raw); heard, shown = (m.group(2), m.group(1) + m.group(3) + m.group(4)) if m else (raw, raw)
        if not norm(heard): parts.append({"t": shown, "em": False}); continue
        if k >= len(cw) or norm(cw[k][0]) != norm(heard):
            ctx = " ".join(x[0] for x in cw[max(0, k - 3):k + 4]); sys.exit(f"phrases.txt line {ln}: \"{heard}\" does not match the cut at word {k} (\"{cw[k][0] if k < len(cw) else 'END'}\"). Spoken there: ...{ctx}...")
        parts.append({"t": shown.replace("'", "\u2019"), "em": em}); k += 1
    if k == first: continue
    caps.append({"start": cw[first][1], "end": cw[k - 1][2], "parts": parts, "n": k - first})
k == len(cw) or sys.exit(f"phrases.txt stops at word {k} of {len(cw)}: the words from \"{' '.join(x[0] for x in cw[k:k + 5])}\" on have no caption")
for i, c in enumerate(caps):                      # each caption stays up until the next one, unless the speaker pauses
    nxt = caps[i + 1]["start"] if i + 1 < len(caps) else DUR
    c["end"] = round(nxt if nxt - c["end"] < 0.6 else c["end"] + 0.3, 3)
out = []
for c in caps:                                     # merge adjacent words that share emphasis; join with spaces
    ps = []
    for p in c["parts"]:
        if ps and ps[-1]["em"] == p["em"]: ps[-1]["t"] += " " + p["t"]
        else: ps.append({"t": (" " if ps else "") + p["t"], "em": p["em"]})
    for j in range(len(ps) - 1):
        if not ps[j + 1]["t"].startswith(" "): ps[j + 1]["t"] = " " + ps[j + 1]["t"]
    out.append({"start": c["start"], "end": c["end"], "parts": ps})
save(W, "captions.json", out)
with open(f"{W}/captions.txt", "w") as f:
    for c, o in zip(caps, out):
        txt = "".join(("[" + p["t"].strip() + "]" if p["em"] else p["t"]) for p in o["parts"]).strip()
        f.write(f"{o['start']:7.2f} {o['end']:7.2f}  {txt}\n")
        chars = len(txt.replace("[", "").replace("]", ""))
        if c["n"] > 3 or chars > 20: bad += 1; print(f"LONG   {o['start']:7.2f}  \"{txt}\"  ({c['n']} words, {chars} characters): split it; captions are one short line")
        if o["end"] - o["start"] < 0.16: bad += 1; print(f"SHORT  {o['start']:7.2f}  \"{txt}\" is on screen {o['end'] - o['start']:.2f}s: join it to a neighbour")
ne = sum(1 for o in out for p in o["parts"] if p["em"])
print(f"{len(out)} captions over {DUR:.1f}s, {ne} emphasised ({ne / DUR * 60:.1f} a minute; the style uses about 3-6 a minute). {bad} to fix. Read {W}/captions.txt ([word] = emphasis).")
if ne / DUR * 60 > 9: print("WARNING too many emphasised words: emphasis only works when it is rare")
