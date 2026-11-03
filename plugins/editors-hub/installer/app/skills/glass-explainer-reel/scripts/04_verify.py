#!/usr/bin/env python3
"""Step 4 - verify the cut BEFORE rendering video.   04_verify.py <slug>
Builds the edited audio from edl.json, transcribes it again with the same transcriber, and compares it word for word
with what the cut was meant to keep. Read every line it prints:
  MISSING / EXTRA / CHANGED   a clipped word, a leftover fragment of a dropped take, or a word the first pass misheard
  PAUSE                       dead space still in the edit
  REPEAT                      the same word twice in a row (often a leftover false start)
Fix drops.json (or --gap), re-run 03_cut.py, and verify again until it is clean. Writes edit.wav for listening."""
import difflib, sys, wave
import numpy as np
from common import work, load, save, scribe, el_words, norm, run
W = work(sys.argv[1]); E = load(W, "edl.json"); FPS = E["fps"]; cw = load(W, "cut_words.json")
w = wave.open(f"{W}/a48.wav"); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
X = int(0.008 * 48000); r = np.linspace(0, 1, X); parts = []
for s, e in E["keeps"]:
    c = a[int(round(s / FPS * 48000)): int(round(e / FPS * 48000))].copy()
    if len(c) > 2 * X:
        c[:X] *= r; c[-X:] *= r[::-1]
    parts.append(c)
x = np.concatenate(parts).astype(np.int16)
o = wave.open(f"{W}/edit.wav", "wb"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(48000); o.writeframes(x.tobytes()); o.close()
run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/edit.wav", "-ar", "16000", f"{W}/edit16.flac"])
V = el_words(scribe(f"{W}/edit16.flac")); save(W, "verify_words.json", V)
A, B = [norm(x[0]) for x in cw], [norm(x[0]) for x in V]; issues = 0
ctx = lambda L, i, j: " ".join(y[0] for y in L[max(0, i - 3): j + 3])
for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
    if op == "equal":
        continue
    issues += 1; t = cw[min(i1, len(cw) - 1)][1]
    name = {"delete": "MISSING", "insert": "EXTRA", "replace": "CHANGED"}[op]
    print(f"{name:8s} at {t:7.2f}s  meant: \"{ctx(cw, i1, i2)}\"  |  heard: \"{ctx(V, j1, j2)}\"")
for p, q in zip(V, V[1:]):
    if q[1] - p[2] > 0.45:
        issues += 1; print(f"PAUSE    at {p[2]:7.2f}s  {q[1] - p[2]:.2f}s between \"{p[0]}\" and \"{q[0]}\"")
    if norm(p[0]) == norm(q[0]):
        print(f"REPEAT   at {p[1]:7.2f}s  \"{p[0]} {q[0]}\"  (fine if it was meant)")
dur = len(x) / 48000
print(f"\nhead {V[0][1]:.2f}s before the first word, tail {dur - V[-1][2]:.2f}s after the last (both should be under ~0.25s)")
print(f"{issues} issue(s); edit is {dur:.1f}s, {len(V)} words\n\nHEARD: " + " ".join(y[0] for y in V))
