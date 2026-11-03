#!/usr/bin/env python3
"""Word-level transcript of the raw recording, with the transcriber chosen at setup (ElevenLabs Scribe or local).
   01_transcribe.py <work_dir | slug>   -> <work>/el.json + el_words.json   (needs a48.wav there; a slug means @@WORK_ROOT@@/<slug>)
ElevenLabs is the recommended engine (most accurate word edges, which the tight cut depends on). The key is read from the
environment or the shell profile by stt.py and is never printed; never ask for it in chat."""
import os, sys, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stt
v = sys.argv[1]; d = v if os.path.isdir(v) else os.path.join(os.path.expanduser("@@WORK_ROOT@@"), v)
flac = f'{d}/a16.flac'
if not os.path.exists(flac):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{d}/a48.wav', '-ac', '1', '-ar', '16000', flac], check=True)
J = stt.transcribe(flac, diarize=False, events=True)
json.dump(J, open(f'{d}/el.json', 'w'))
W = [[w['text'], w['start'], w['end'], w.get('type')] for w in J['words'] if w.get('type') != 'spacing']
json.dump(W, open(f'{d}/el_words.json', 'w'))
print(v, J.get('_engine'), len(W), 'tokens')
