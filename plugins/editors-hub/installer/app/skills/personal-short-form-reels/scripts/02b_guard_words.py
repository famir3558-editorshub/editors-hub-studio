#!/usr/bin/env python3
"""guard.py <work>  — after 02_cut.py: never let a silence/breath cut eat into a kept word's transcript span."""
import json, sys
W = sys.argv[1]; E = json.load(open(f"{W}/edl.json")); F = E["fps"]; D = E["dur"]
FL = json.load(open(f"{W}/flubs.json"))
EL = [(s, e) for t, s, e, ty in json.load(open(f"{W}/el_words.json")) if ty == "word" and any(c.isalnum() for c in t)
      and not any(a <= (s + e) / 2 < b for a, b in FL)]
K = [(s / F, e / F) for s, e in E["keeps"]]; cuts = []; cur = 0
for s, e in K:
    if s > cur: cuts.append([cur, s])
    cur = e
if cur < D: cuts.append([cur, D])
out = []; n = 0
for a, b in cuts:
    segs = [[a, b]]
    for s, e in EL:
        if e <= a or s >= b: continue
        nx = []
        for x, y in segs:
            if e <= x or s >= y: nx.append([x, y]); continue
            if s - x > 0: nx.append([x, s])
            if y - e > 0: nx.append([e, y])
            n += 1
        segs = nx
    out += [g for g in segs if g[1] - g[0] >= 0.06]
keeps = []; cur = 0
for a, b in sorted(out):
    fa, fb = round(a * F), round(b * F)
    if fa - cur >= 2: keeps.append([cur, fa])
    cur = max(cur, fb)
if round(D * F) - cur >= 2: keeps.append([cur, round(D * F)])     # the recording ends on a kept word (no trailing silence): keep the tail
tot = sum(e - s for s, e in keeps) / F
print(f"{n} trims; cut {tot:.1f}s, {len(keeps)} keeps")
json.dump({"keeps": keeps, "dur": D, "fps": F}, open(f"{W}/edl.json", "w"))
