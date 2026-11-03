#!/usr/bin/env python3
"""Word-level transcript of the creator's cut.   transcribe.py <cut.mp4> <work_dir>
Writes work_dir/words.json  [[start, end, word, prob], ...]  (seconds on the cut = panel timeline)
and   work_dir/readable.txt (lines with start-end, gaps > 0.6s marked, low-confidence words with '?').
Uses the transcriber chosen at setup through stt.py (ElevenLabs Scribe, or local through HyperFrames).
Word times are good to about +-0.1 s, which is what animation cues need. `prob` is 1.0 when the engine gives no
confidence score; words the engine scored low are marked '?' in readable.txt so you read them twice.
"""
import json, math, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stt

src, wd = sys.argv[1], sys.argv[2]
os.makedirs(wd, exist_ok=True)
audio = os.path.join(wd, "a16k.flac")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000", audio], check=True)
J = stt.transcribe(audio, diarize=False)
print("transcribed with", J.get("_engine", "?"))
W = []
for w in J["words"]:
    if w.get("type", "word") != "word" or not w.get("text", "").strip():
        continue
    lp = w.get("logprob")
    prob = round(math.exp(lp), 3) if isinstance(lp, (int, float)) and lp <= 0 else 1.0
    W.append((round(float(w["start"]), 3), round(float(w["end"]), 3), w["text"].strip(), prob))
if not W:
    sys.exit("no words found: is there speech in this file?")
json.dump(W, open(os.path.join(wd, "words.json"), "w"))
out, line, st, prev = [], "", W[0][0], W[0][1]
for s, e, w, p in W:
    if s - prev > 0.6 or len(line) > 90:
        out.append(f"{st:7.2f}-{prev:7.2f} {line}"); line, st = "", s
        if s - prev > 0.6: out.append(f"        [gap {s - prev:.2f}]")
    line += " " + w + ("?" if p < 0.5 else ""); prev = e
out.append(f"{st:7.2f}-{prev:7.2f} {line}")
open(os.path.join(wd, "readable.txt"), "w").write("\n".join(out) + "\n")
print("\n".join(out))
