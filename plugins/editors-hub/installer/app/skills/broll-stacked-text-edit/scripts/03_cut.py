#!/usr/bin/env python3
"""Step 3 - the tight cut.   03_cut.py <slug> [--gap 0.12] [--pad-out 0.035] [--pad-in 0.025]

Reads words.json, a48.wav, a16.wav and the decision file you write, drops.json (optional):
  {"words": [[i, j], ...],     inclusive word-index ranges from words.txt to remove
                               (false starts, repeated takes, fillers, mistakes; keep the LAST complete take)
   "secs":  [[a, b], ...]}     raw-second ranges to remove that are not words (coughs, off-camera chat, a long look away)
Writes edl.json {keeps: source frame ranges}, cut_words.json [[text, start, end, raw_index]] on the CUT timeline,
cuts.json (every join on the cut timeline) and edit.txt (the edit as a script with cut-timeline times).

What it removes: everything in drops.json, every pause longer than --gap between two kept words, breaths, and
the head and tail (tight to the first and last kept word). Word edges come from audio energy and are never allowed
to cut into a kept word's ElevenLabs span. ALWAYS run 04_verify.py next."""
import sys, wave
from fractions import Fraction
import numpy as np
from common import work, load, save

W = work(sys.argv[1])
arg = lambda k, d: float(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
GAP, PO, PI = arg("--gap", 0.12), arg("--pad-out", 0.035), arg("--pad-in", 0.025)
M = load(W, "meta.json"); FPS = float(Fraction(M["fps"]))
words = load(W, "words.json"); D = load(W, "drops.json", {}) or {}
w = wave.open(f"{W}/a48.wav"); n = w.getnframes(); a = np.frombuffer(w.readframes(n), np.int16).astype(np.float32) / 32768
DUR = n / 48000; h = 480; m = len(a) // h
rms = 20 * np.log10(np.sqrt((a[: m * h].reshape(m, h) ** 2).mean(1)) + 1e-9); rms = np.convolve(rms, np.ones(3) / 3, "same")

dropped = set()
for i, j in D.get("words", []):
    dropped.update(range(i, j + 1))
SECS = [tuple(x) for x in D.get("secs", [])]
for i, (t, s, e) in enumerate(words):
    if any(a_ <= (s + e) / 2 < b_ for a_, b_ in SECS):
        dropped.add(i)
kept = [i for i in range(len(words)) if i not in dropped]
kept or sys.exit("nothing kept")
above = lambda t: rms[min(len(rms) - 1, max(0, int(t * 100)))] > -46


def word_end(i):
    """Where word i's sound really ends: (time, found_silence). Never past the next word's start."""
    lim = min(words[i][2] + 1.0, words[i + 1][1] if i + 1 < len(words) else DUR)
    t = words[i][2]; q = 0
    while t < lim:
        q = 0 if above(t) else q + 1
        if q >= 10:
            return max(words[i][2], t - 0.09), True
        t += 0.01
    return max(words[i][2], lim), False


def word_start(i):
    lim = max(words[i][1] - 1.0, words[i - 1][2] if i else 0)
    t = words[i][1]; q = 0
    while t > lim:
        q = 0 if above(t) else q + 1
        if q >= 10:
            return min(words[i][1], t + 0.09), True
        t -= 0.01
    return min(words[i][1], lim), False


cuts = [[a_, b_, "drop"] for a_, b_ in SECS]
for p, nx in zip(kept, kept[1:]):
    (e, es), (s, ss) = word_end(p), word_start(nx)
    if nx != p + 1:                                   # words were dropped in between: always cut
        A, B = e + (PO if es else 0), s - (PI if ss else 0)
        if B - A > 0.02:
            cuts.append([A, B, "drop"])
    elif s - e > GAP:
        A, B = e + PO, s - PI
        seg = rms[int(A * 100): int(B * 100)] > -40; run = mx = 0
        for x in seg:
            run = run + 1 if x else 0; mx = max(mx, run)
        if B - A > 0.04 and not (B - A < 0.4 and mx >= 6):   # short gap with sustained sound = part of a word
            cuts.append([A, B, "gap"])
cuts.append([0, max(0, word_start(kept[0])[0] - 0.08), "head"])
cuts.append([min(DUR, word_end(kept[-1])[0] + 0.12), DUR, "tail"])


def keeps_from(cuts):
    cuts = sorted(c for c in cuts if c[1] > c[0]); Mg = []
    for A, B, t in cuts:
        if Mg and A <= Mg[-1][1] + 0.02:
            Mg[-1][1] = max(Mg[-1][1], B)
        else:
            Mg.append([A, B, t])
    K, cur = [], 0.0
    for A, B, t in Mg:
        if A > cur:
            K.append([cur, A])
        cur = max(cur, B)
    if cur < DUR:
        K.append([cur, DUR])
    return K


# breaths / air between words: unvoiced AND quiet for >= 0.18 s
K = keeps_from(cuts)
w16 = wave.open(f"{W}/a16.wav"); b = np.frombuffer(w16.readframes(w16.getnframes()), np.int16).astype(np.float32) / 32768
hop, win = 160, 640; nn = (len(b) - win) // hop; vo = np.zeros(nn, np.float32)
for s0 in range(0, nn, 20000):
    idx = np.arange(s0, min(nn, s0 + 20000)); fr = np.lib.stride_tricks.sliding_window_view(b, win)[idx * hop]
    fr = fr - fr.mean(1, keepdims=True); X = np.fft.rfft(fr, n=2 * win, axis=1); ac = np.fft.irfft(np.abs(X) ** 2, axis=1)[:, :win]
    vo[idx] = (ac / (ac[:, :1] + 1e-9))[:, 53:229].max(1)
mm = min(len(rms), len(vo)); quiet = (vo[:mm] < 0.45) & (rms[:mm] < -30); breaths = []
for ks, ke in K:
    run = 0; hi = min(int(ke * 100), mm)
    for i in range(int(ks * 100), hi + 1):
        if i < hi and quiet[i]:
            run += 1
            continue
        if run >= 18:
            t0, t1 = (i - run) / 100, i / 100
            if not [x for x in words if t0 + 0.06 < x[1] < t1 - 0.06] and t0 > ks + 0.05 and t1 < ke - 0.05:
                breaths.append([t0 + 0.05, t1 - 0.04, "breath"])
        run = 0

# guard: no cut may eat into a kept word
spans = [(words[i][1], words[i][2]) for i in kept]; safe = []
for A, B, kind in cuts + breaths:
    segs = [[A, B]]
    for s, e in spans:
        if e <= A or s >= B:
            continue
        segs = [g for x, y in segs for g in ([[x, y]] if e <= x or s >= y else [[x, s], [e, y]]) if g[1] - g[0] > 0]
    safe += [[x, y, kind] for x, y in segs if y - x >= 0.06 or kind in ("head", "tail")]
K = keeps_from(safe)
keeps = [[round(s * FPS), round(e * FPS)] for s, e in K]; keeps = [k for k in keeps if k[1] - k[0] >= 2]

# map onto the cut timeline
starts, acc = [], 0
for s, e in keeps:
    starts.append(acc); acc += e - s
total = acc / FPS


def cut_t(t):
    f = t * FPS
    for (s, e), st in zip(keeps, starts):
        if f < s:
            return st / FPS
        if f <= e:
            return (st + f - s) / FPS
    return total


cw = [[words[i][0], round(cut_t(words[i][1]), 3), round(cut_t(words[i][2]), 3), i] for i in kept]
joins = []
for k in range(len(keeps) - 1):
    A, B = keeps[k][1] / FPS, keeps[k + 1][0] / FPS
    kind = max((min(B, c[1]) - max(A, c[0]), c[2]) for c in safe)[1]
    joins.append({"t": round((starts[k + 1]) / FPS, 3), "removed": round(B - A, 2), "kind": kind,
                  "big": bool(kind == "drop" or B - A > 0.6)})
save(W, "edl.json", {"keeps": keeps, "dur": DUR, "fps": FPS}); save(W, "cut_words.json", cw); save(W, "cuts.json", joins)
short = [k for k in keeps if (k[1] - k[0]) / FPS < 0.2]
print(f"raw {DUR:.1f}s -> cut {total:.1f}s | {len(keeps)} keeps, {len(joins)} joins ({sum(j['big'] for j in joins)} big), "
      f"{len(breaths)} breath cuts, {len(dropped)} words dropped")
if short:
    print(f"WARNING {len(short)} keeps shorter than 0.2s (a sliver between two cuts): raw frames {short[:6]}; check drops.json around them")
marks = {next((x[3] for x in cw if x[1] >= j["t"] - 0.02), None) for j in joins if j["big"]}
lines, start = [], 0
for i, x in enumerate(cw):
    if i == len(cw) - 1 or x[0][-1] in ".?!":
        txt = ""
        for y in cw[start:i + 1]:
            txt += ("|| " if y[3] in marks else "") + y[0] + " "
        lines.append(f"[{cw[start][1]:7.2f}] {txt.strip()}"); start = i + 1
open(f"{W}/edit.txt", "w").write("\n".join(lines) + "\n\nWORDS (cut-timeline start, end, word)\n" +
                                 "\n".join(f"{x[1]:8.2f} {x[2]:8.2f}  {x[0]}" for x in cw) + "\n")
print("\nEDIT ( || = a big jump cut lands just before this word):\n" + "\n".join(lines))
