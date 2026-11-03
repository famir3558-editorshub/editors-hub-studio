#!/usr/bin/env python3
"""Captions as a separate file (never burned in).   make_srt.py <slug>
Writes "<out>/<name> - YouTube Edit.srt" from the cut's own word timings (cut_words.json), so it lines up with the
finished edit. Upload it to YouTube as the caption track. Lines break on sentence ends and pauses, at most 42
characters a line and two lines a caption. Only run when the creator's setup asks for a caption file
(`captions` = `srt`); the pack default is no captions at all. Read the file once: it is the transcript, so a
misheard name or term needs correcting by hand."""
import sys
from common import work, load
W = work(sys.argv[1]); M = load(W, "meta.json"); cw = load(W, "cut_words.json") or sys.exit("no cut_words.json: run 03_cut.py (or 06_new_project.py --no-cut) first")
MAXC, MAXL, MAXD = 42, 2, 6.0
caps, cur = [], []


def flush():
    if cur: caps.append(list(cur)); cur.clear()


for i, (t, s, e, *_r) in enumerate(cw):
    cur.append((t, s, e))
    text = " ".join(x[0] for x in cur); nxt = cw[i + 1] if i + 1 < len(cw) else None
    if (nxt is None or t[-1] in ".?!" or nxt[1] - e > 0.6 or len(text) + 1 + len(nxt[0]) > MAXC * MAXL or nxt[2] - cur[0][1] > MAXD): flush()
flush()


def stamp(x):
    ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def wrap(words):
    text = " ".join(words)
    if len(text) <= MAXC: return text
    best = min(range(1, len(words)), key=lambda k: abs(len(" ".join(words[:k])) - len(" ".join(words[k:]))))
    return " ".join(words[:best]) + "\n" + " ".join(words[best:])


out = f"{M['out']}/{M['stem']} - YouTube Edit.srt"
with open(out, "w", encoding="utf-8") as f:
    for n, c in enumerate(caps, 1):
        end = min(c[-1][2] + 0.15, caps[n][0][1] - 0.02) if n < len(caps) else c[-1][2] + 0.15
        f.write(f"{n}\n{stamp(c[0][1])} --> {stamp(max(end, c[0][1] + 0.3))}\n{wrap([x[0] for x in c])}\n\n")
print(f"wrote {out} ({len(caps)} captions). Read it once for misheard names and terms.")
