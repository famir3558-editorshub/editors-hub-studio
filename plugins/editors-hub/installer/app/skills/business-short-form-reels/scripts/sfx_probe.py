#!/usr/bin/env python3
"""List a sound-effects folder with each file's length and peak level, and print a starter sfx_map.json.
    python3 sfx_probe.py "<folder>" [--write]      --write saves ~/.claude/creator-profile/assets/sfx_map.json

The mix (mix.py) plays sounds by ROLE. Roles used by the kits: woosh, swish, swoosh (a graphic coming in, rotated),
pop, pops (something landing), shine (a highlight), swirl (the opening), slide, accept, access, dtext, data, whip.
Only `woosh` and `pop` are needed: any role that is missing falls back to one of those. This script guesses roles from
file names; read the list, listen if you can, and correct the map by hand. "peak" is the file's measured peak in dB
(the mix uses it to play every sound at the same quiet level); "max" is how many seconds of the file are used."""
import json, os, re, subprocess, sys
ROLES = {"woosh": r"woosh|whoosh", "swish": r"swish", "swoosh": r"swoosh", "pop": r"\bpop\b|pop[ _-]?\d|click|tap", "pops": r"pops",
         "shine": r"shine|shimmer|sparkle", "swirl": r"swirl|riser|rise", "slide": r"slide", "accept": r"accept|success|confirm",
         "access": r"access|unlock", "dtext": r"text|type|typing|key", "data": r"data|load|digital", "whip": r"whip"}
MAXLEN = {"pop": 0.4, "pops": 0.5, "slide": 0.5, "accept": 0.5, "dtext": 0.4, "woosh": 0.6, "swish": 0.6, "swoosh": 0.6, "access": 0.7,
          "shine": 0.8, "data": 1.25, "swirl": 2.0, "whip": 2.0}
root = os.path.abspath(os.path.expanduser(sys.argv[1])); rows = []
for d, _, files in os.walk(root):
    for f in sorted(files):
        if not f.lower().endswith((".wav", ".mp3", ".aif", ".aiff", ".m4a", ".flac", ".ogg")): continue
        p = os.path.join(d, f)
        e = subprocess.run(["ffmpeg", "-v", "info", "-i", p, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
        pk = re.search(r"max_volume: (-?[\d.]+)", e); du = re.search(r"Duration: (\d+):(\d+):([\d.]+)", e)
        if not pk or not du: continue
        dur = int(du.group(1)) * 3600 + int(du.group(2)) * 60 + float(du.group(3))
        rows.append((os.path.relpath(p, root), round(dur, 2), float(pk.group(1))))
sounds = {}
for rel, dur, pk in rows:
    print(f"{dur:6.2f}s  peak {pk:6.1f} dB  {rel}")
    if dur > 4: continue
    for role, pat in ROLES.items():
        if role not in sounds and re.search(pat, os.path.basename(rel).lower()):
            sounds[role] = {"file": rel, "peak": pk, "max": min(dur, MAXLEN[role])}; break
M = {"dir": root, "sounds": sounds}
print("\nstarter map (correct it by hand):\n" + json.dumps(M, indent=1))
if "--write" in sys.argv:
    out = os.path.expanduser(os.environ.get("CREATOR_PROFILE_DIR", "~/.claude/creator-profile")) + "/assets"
    os.makedirs(out, exist_ok=True); json.dump(M, open(f"{out}/sfx_map.json", "w"), indent=1); print("wrote", f"{out}/sfx_map.json")
