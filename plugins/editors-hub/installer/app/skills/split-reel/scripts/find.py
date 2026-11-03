#!/usr/bin/env python3
"""Phrase -> time on the cut.   find.py <work_dir/words.json> "from phrase" ["to phrase"]
Prints start of the first phrase and end of the second (or of the first), for fullscreen windows
and animation cues ("full screen from 'if you do this' to 'ever'"). Matching ignores case/punctuation."""
import json, re, sys
W = json.load(open(sys.argv[1])); norm = lambda s: re.sub(r"[^a-z0-9']", "", s.lower().replace("-", ""))
T = [norm(w[2]) for w in W]
def find(ph, after=0):
    p = "".join(norm(x) for x in ph.split())
    for i in range(len(W)):
        if W[i][0] < after: continue
        s, j = "", i
        while j < len(W) and len(s) < len(p): s += T[j]; j += 1
        if s == p: return W[i][0], W[j - 1][1]
    sys.exit(f"not found: {ph!r}")
a = find(sys.argv[2]); b = find(sys.argv[3], a[0]) if len(sys.argv) > 3 else a
print(f"{a[0]:.2f} {b[1]:.2f}")
