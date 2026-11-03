#!/usr/bin/env python3
"""ElevenLabs word timings moved onto the CUT's clock.   05b_cut_words.py <work_dir>   -> <work>/cut/words.json  [[start, end, word], ...]
No second transcription needed: every kept word's raw time is mapped through edl.json. Prints the cut as a script with times.
Merge spoken numbers by hand afterwards if a caption should show digits (e.g. "four hundred thousand" -> "400,000")."""
import json, os, sys
W = sys.argv[1]; E = json.load(open(f"{W}/edl.json")); F = E["fps"]; K = [(s / F, e / F) for s, e in E["keeps"]]
def m(t):
    acc = 0
    for a, b in K:
        if t < a: return acc
        if t <= b: return acc + t - a
        acc += b - a
    return acc
out = []; line = []
for t, s, e, ty in json.load(open(f"{W}/el_words.json")):
    if ty != "word" or not any(c.isalnum() for c in t): continue
    if not any(a <= (s + e) / 2 <= b for a, b in K): continue
    out.append([round(m(s), 3), round(m(e), 3), t.strip()]); line.append(f"{t.strip()}@{m(s):.2f}")
    if t.strip()[-1] in ".?!": print(" ".join(line)); line = []
print(" ".join(line)); os.makedirs(f"{W}/cut", exist_ok=True); json.dump(out, open(f"{W}/cut/words.json", "w")); print(len(out), "words")
