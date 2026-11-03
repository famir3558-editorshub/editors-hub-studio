#!/usr/bin/env python3
"""Step 2 — the tight cut.   02_cut.py <work_dir> [--fps 24000/1001] [--gap 0.12] [--pad-out 0.035] [--pad-in 0.025]

Reads   work/tx.json, a48.wav, a16.wav  and the hand-written decision files (all optional):
  flubs.json    [[start,end],...]  RAW seconds to remove: failed takes, repeats, off-script chat.
                Keep the LAST complete take. A range runs from the first bad word to just before the good take.
  protect.json  [[start,end],...]  spans where whisper lost/collapsed words — cut on energy only there.
  fix.json      [[old_time,new_time],...]  move one mis-timed word.
Writes  work/words.json, rms.npy, edl.json {keeps:[[f0,f1],...] source frames, dur}.

The standard: "sharp fast cuts that leave no gaps at the end or start of my sentences".
  - every pause > --gap between two kept words is cut, leaving pad-out after the word and pad-in before the next
  - breaths/air between words (unvoiced + quiet >= 0.18s) are cut too
  - word edges come from full-band RMS (boundary = >=100ms below -46 dBFS), not from whisper's times
ALWAYS run 03_verify_cut.py afterwards and read the result."""
import numpy as np, json, sys, wave, os
from fractions import Fraction
W = sys.argv[1]
arg = lambda k, d: (sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d)
FPS = float(Fraction(arg("--fps", "24000/1001"))); GAP = float(arg("--gap", 0.12)); PO = float(arg("--pad-out", 0.035)); PI = float(arg("--pad-in", 0.025))
J = json.load(open(f"{W}/tx.json"))
w = wave.open(f"{W}/a48.wav"); n = w.getnframes(); a = np.frombuffer(w.readframes(n), np.int16).astype(np.float32) / 32768
DUR = n / 48000; h = 480; m = len(a) // h
rms = 20 * np.log10(np.sqrt((a[: m * h].reshape(m, h) ** 2).mean(1)) + 1e-9); rms = np.convolve(rms, np.ones(3) / 3, "same"); np.save(f"{W}/rms.npy", rms)
words = []
for seg in J["transcription"]:
    for t in seg["tokens"]:
        tx = t["text"]
        if tx.startswith("[_"): continue
        d = t.get("t_dtw", -1) / 100
        if d < 0: d = t["offsets"]["from"] / 1000
        s = tx.strip()
        if not s or all(not c.isalnum() for c in s):
            if words and s: words[-1][0] += s
            continue
        if tx.startswith(" ") or not words: words.append([s, d, d])
        else: words[-1][0] += s; words[-1][2] = d
rd = lambda f, d: json.load(open(f"{W}/{f}")) if os.path.exists(f"{W}/{f}") else d
for old, new in rd("fix.json", []):
    for x in words:
        if abs(x[1] - old) < 0.005: x[1] = x[2] = new
FL = [tuple(x) for x in rd("flubs.json", [])]
for pa, pb in rd("protect.json", []):          # replace whisper words by energy bursts
    words = [x for x in words if not (pa <= x[1] < pb)]
    seg = rms[int(pa * 100): int(pb * 100)] > -46; st = None; q = 0
    for i, x in enumerate(seg):
        t = pa + i / 100
        if x:
            if st is None: st = t
            q = 0; en = t
        elif st is not None:
            q += 1
            if q >= 10: words.append(["~", st, en]); st = None
    if st is not None: words.append(["~", st, en])
words.sort(key=lambda x: x[1]); json.dump(words, open(f"{W}/words.json", "w"))
infl = lambda t: any(a_ <= t < b_ for a_, b_ in FL)
kw = [x for x in words if not infl((x[1] + x[2]) / 2)]
above = lambda t: rms[min(len(rms) - 1, int(t * 100))] > -46
def word_end(x):
    t = x[2]; lim = x[2] + 1.0; q = 0
    while t < lim:
        if above(t): q = 0
        else:
            q += 1
            if q >= 10: return t - 0.09
        t += 0.01
    return lim
def word_start(x):
    t = x[1]; lim = max(0, x[1] - 1.0); q = 0
    while t > lim:
        if above(t): q = 0
        else:
            q += 1
            if q >= 10: return t + 0.09
        t -= 0.01
    return lim
cuts = [[a_, b_, "flub"] for a_, b_ in FL]
for p, nx in zip(kw, kw[1:]):
    e = word_end(p); s = word_start(nx)
    if s - e > GAP:
        A, B = e + PO, s - PI
        seg = rms[int(A * 100): int(B * 100)] > -40; run = mx = 0
        for x in seg: run = run + 1 if x else 0; mx = max(mx, run)
        if B - A > 0.04 and not (B - A < 0.4 and mx >= 6): cuts.append([A, B, "gap"])   # short gap with sustained sound = part of a word
cuts.append([0, max(0, word_start(kw[0]) - 0.1), "head"]); cuts.append([word_end(kw[-1]) + 0.12, DUR, "tail"])
def keeps_from(cuts):
    cuts.sort(); M = []
    for A, B, t in cuts:
        if M and A <= M[-1][1] + 0.02: M[-1][1] = max(M[-1][1], B)
        else: M.append([A, B, t])
    K, cur = [], 0.0
    for A, B, t in M:
        if A > cur: K.append([cur, A])
        cur = max(cur, B)
    if cur < DUR: K.append([cur, DUR])
    return K
K = keeps_from(cuts)
# breaths / air between words: unvoiced AND quiet for >= 0.18s
w16 = wave.open(f"{W}/a16.wav"); b = np.frombuffer(w16.readframes(w16.getnframes()), np.int16).astype(np.float32) / 32768
hop, win = 160, 640; nn = (len(b) - win) // hop; vo = np.zeros(nn, np.float32)
for s0 in range(0, nn, 20000):
    idx = np.arange(s0, min(nn, s0 + 20000)); fr = np.lib.stride_tricks.sliding_window_view(b, win)[idx * hop]
    fr = fr - fr.mean(1, keepdims=True); X = np.fft.rfft(fr, n=2 * win, axis=1); ac = np.fft.irfft(np.abs(X) ** 2, axis=1)[:, :win]
    vo[idx] = (ac / (ac[:, :1] + 1e-9))[:, 53:229].max(1)
mm = min(len(rms), len(vo)); quiet = (vo[:mm] < 0.45) & (rms[:mm] < -30); extra = []
for ks, ke in K:
    run = 0
    for i in range(int(ks * 100), min(int(ke * 100), mm) + 1):
        qv = quiet[i] if i < min(int(ke * 100), mm) else False
        if qv: run += 1
        else:
            if run >= 18:
                t0, t1 = (i - run) / 100, i / 100
                if not [x for x in words if t0 + 0.06 < x[1] < t1 - 0.06] and t0 > ks + 0.05 and t1 < ke - 0.05: extra.append([t0 + 0.05, t1 - 0.04, "breath"])
            run = 0
K = keeps_from(cuts + extra)
keeps = [[round(s * FPS), round(e * FPS)] for s, e in K]; keeps = [k for k in keeps if k[1] - k[0] >= 2]
tot = sum(e - s for s, e in keeps) / FPS
print(f"raw {DUR:.1f}s -> cut {tot:.1f}s, {len(keeps)} keeps ({len(extra)} breath cuts, {len(FL)} flub ranges)")
json.dump({"keeps": keeps, "dur": DUR, "fps": FPS}, open(f"{W}/edl.json", "w"))
