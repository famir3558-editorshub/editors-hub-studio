#!/usr/bin/env python3
"""ElevenLabs words -> the tx.json that 02_cut.py reads.   01b_el_to_tx.py <work_dir>   (needs <work>/el_words.json from 01_transcribe_elevenlabs.py)
Each word becomes two tokens (its start and its end) so the cut script knows both edges. Also prints the script with times, pauses marked."""
import json, sys
W = sys.argv[1]; EL = json.load(open(f"{W}/el_words.json")); toks = []; line = []; prev = None
for t, s, e, ty in EL:
    t = t.strip()
    if prev is not None and s - prev > 0.6: print(" ".join(line)); print(f"   --- {s - prev:.1f}s pause"); line = []
    line.append(f"{t}@{s:.2f}" if ty == "word" else f"[{t}@{s:.2f}-{e:.2f}]"); prev = e
    if t[-1:] in ".?!": print(" ".join(line)); line = []
    if ty != "word" or not any(c.isalnum() for c in t): continue
    a, b = s + 0.02, max(s + 0.02, e - 0.02)
    if len(t.rstrip('.,?!"')) > 1:
        toks.append({"text": " " + t[:-1], "t_dtw": round(a * 100), "offsets": {"from": int(s * 1000)}}); toks.append({"text": t[-1], "t_dtw": round(b * 100), "offsets": {"from": int(e * 1000)}})
    else: toks.append({"text": " " + t, "t_dtw": round((a + b) / 2 * 100), "offsets": {"from": int(s * 1000)}})
print(" ".join(line)); json.dump({"transcription": [{"tokens": toks}]}, open(f"{W}/tx.json", "w"))
