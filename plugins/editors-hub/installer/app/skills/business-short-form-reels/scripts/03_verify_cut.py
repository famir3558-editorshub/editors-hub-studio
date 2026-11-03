#!/usr/bin/env python3
"""Step 3 — verify the cut BEFORE rendering.   03_verify_cut.py <work_dir>
1. Transcribes every removed gap that contains sustained sound and is not a declared flub
   -> hidden retakes / real words whisper's first pass missed show up here (GAP lines). Read them all.
2. Transcribes the edited audio end to end -> read it as a script: no repeats, no clipped words, no half sentences.
If a GAP line is real content: add a protect.json span or adjust flubs.json, re-run 02_cut.py, verify again."""
import json, sys, wave, numpy as np, subprocess, os
W = sys.argv[1]; E = json.load(open(f"{W}/edl.json")); FPS = E["fps"]
w = wave.open(f"{W}/a16.wav"); a = np.frombuffer(w.readframes(w.getnframes()), np.int16); r = np.load(f"{W}/rms.npy")
MODEL = os.path.expanduser("~/.cache/hyperframes/whisper/models/ggml-small.bin")
def wr(p, x):
    o = wave.open(p, "wb"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(16000); o.writeframes(x.astype(np.int16).tobytes()); o.close()
import shutil; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
def tx(p):
    """Quick local read of a short piece: whisper-cli with the model HyperFrames caches, else the transcriber chosen at setup."""
    if shutil.which("whisper-cli") and os.path.exists(MODEL):
        return subprocess.run(["whisper-cli", "-m", MODEL, "-f", p, "-l", "en", "-nt", "-np"], capture_output=True, text=True).stdout.strip().replace("\n", " ")
    import stt
    return " ".join(w["text"] for w in stt.transcribe(p, events=False)["words"] if w.get("type", "word") == "word")
FL = json.load(open(f"{W}/flubs.json")) if os.path.exists(f"{W}/flubs.json") else []
os.makedirs(f"{W}/gaps", exist_ok=True); prev = 0; pad = np.zeros(8000, np.int16)
for s, e in E["keeps"]:
    A, B = prev / FPS, s / FPS; prev = e
    if B - A < 0.3 or (r[int(A * 100): int(B * 100)] > -40).sum() < 25: continue
    if sum(max(0, min(B, fb) - max(A, fa)) for fa, fb in FL) > 0.8 * (B - A): continue
    p = f"{W}/gaps/g_{A:.2f}_{B:.2f}.wav"; wr(p, np.concatenate([pad, a[int(A * 16000): int(B * 16000)], pad]))
    print(f"GAP {A:.2f}-{B:.2f} ({B - A:.1f}s): {tx(p)}")
wr(f"{W}/edit16.wav", np.concatenate([a[int(s / FPS * 16000): int(e / FPS * 16000)] for s, e in E["keeps"]]))
print("\nEDIT:", tx(f"{W}/edit16.wav"))
