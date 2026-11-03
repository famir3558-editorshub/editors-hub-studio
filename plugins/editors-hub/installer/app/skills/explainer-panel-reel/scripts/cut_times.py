#!/usr/bin/env python3
"""Where the mode switches can go.   cut_times.py <slug>
Lists every join in the tight cut on the cut timeline with the words either side. `BIG` joins (a dropped take or a long
removal) are the jumps a viewer sees: put a full-frame <-> panel switch exactly on each of them where possible."""
import sys
from common import work, load
W = work(sys.argv[1]); cuts = load(W, "cuts.json"); cw = load(W, "cut_words.json"); M = load(W, "meta.json")
print(f"cut length {M.get('cut_dur', cw[-1][2]):.2f}s, {len(cuts)} joins. Use the time as printed in E.full([...]); the engine snaps it to the frame.\n")
for c in cuts:
    k = next((i for i, x in enumerate(cw) if x[1] >= c["t"] - 0.02), len(cw) - 1)
    print(f"{c['t']:8.3f}  {'BIG  ' if c['big'] else 'small'} removed {c['removed']:5.2f}s   ...{' '.join(x[0] for x in cw[max(0, k - 3):k])} | {' '.join(x[0] for x in cw[k:k + 3])}...")
