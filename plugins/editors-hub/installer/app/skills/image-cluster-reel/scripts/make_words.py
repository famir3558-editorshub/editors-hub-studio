#!/usr/bin/env python3
"""Word timings for a clip, in the shape cluster_reel.py reads.

  make_words.py clip.mp4 words.json

Pulls the audio with ffmpeg, transcribes it through stt.py (ElevenLabs or this computer, whichever the creator chose in setup)
and writes [[start, end, "word"], ...]. Run it on the EDITED clip (the one the reel is built on), so the times match."""
import json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stt

if len(sys.argv) < 3:
    sys.exit(__doc__)
clip, out = sys.argv[1], sys.argv[2]
with tempfile.TemporaryDirectory() as d:
    wav = os.path.join(d, "a.flac")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", clip, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
    J = stt.transcribe(wav)
words = [[round(float(w["start"]), 3), round(float(w["end"]), 3), w["text"]]
         for w in J.get("words", []) if w.get("type", "word") == "word"]
json.dump(words, open(out, "w"))
print(f"{len(words)} words -> {out}  (engine: {J.get('_engine', 'unknown')})")
