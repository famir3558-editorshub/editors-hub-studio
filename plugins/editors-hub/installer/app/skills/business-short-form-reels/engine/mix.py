#!/usr/bin/env python3
"""Sound for a reel built with kit.py.   python3 mix.py "<OUT dir>" "<Title>" "<suffix stem, e.g. Final Style v1>" [music file] [music start s]
Reads sfx.json (written by kit.flush(): glide-in times + accents). Key moments only, quiet (TRIM -8.5 dB; whooshes peak ~-29.5 dBFS).
Writes, for the master and the phone copy: "... - no music" (sound effects only) and, if a music file is given, "... - with music"
(bed at MUSIC_MEAN, 0.4 s fade in, 1.5 s fade out, started at the given second so the beat is in from frame 1)."""
import subprocess, os, sys, json, re
# Sounds are played by ROLE from sfx_map.json (made at setup with scripts/sfx_probe.py from the creator's own sound-effects folder).
# Looked for in: the project folder, then ~/.claude/creator-profile/assets/. No map = the reel is delivered without sound effects.
FALLBACK = {"swish": "woosh", "swoosh": "woosh", "slide": "woosh", "swirl": "woosh", "bigwhoosh": "woosh", "whip": "woosh", "pops": "pop", "shine": "pop",
            "shine2": "shine", "accept": "pop", "access": "pop", "dtext": "pop", "data": "pop"}
def load_sfx():
    for p in ("sfx_map.json", os.path.expanduser(os.environ.get("CREATOR_PROFILE_DIR", "~/.claude/creator-profile")) + "/assets/sfx_map.json"):
        if os.path.exists(p):
            M = json.load(open(p)); root = os.path.expanduser(M.get("dir", "")); S = {}
            for name, v in M.get("sounds", {}).items():
                f = v["file"] if os.path.isabs(v["file"]) else os.path.join(root, v["file"])
                if os.path.exists(f): S[name] = (f, float(v.get("peak", 0.0)), float(v.get("max", 0.6)))
                else: print("sfx_map: missing file for", name, "->", f)
            return S
    print("NOTE no sfx_map.json: no sound effects will be added (run scripts/sfx_probe.py on a sound-effects folder to make one).")
    return {}
S = load_sfx()   # role: (path, measured peak dB, max seconds)
def role(n):
    seen = set()
    while n not in S and n in FALLBACK and n not in seen: seen.add(n); n = FALLBACK[n]
    return n if n in S else None
TRIM = -8.5; MUSIC_MEAN = float(os.environ.get("MUSIC_MEAN", -39.0))
OUT, TITLE, STEM = sys.argv[1:4]; MUSIC = sys.argv[4] if len(sys.argv) > 4 else None; MSTART = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
J = json.load(open("sfx.json")); DUR = J["dur"]
EV = [(t, ["woosh", "swish", "swoosh"][i % 3], -21) for i, t in enumerate(J["glides"]) if t > 0.05] + [tuple(x) for x in J["accents"]]
def mix(src, events, out):
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", src]; fc = []; labs = ["[0:a]"]
    events = [(t, role(n), lv) for t, n, lv in sorted(events) if role(n)]
    if not events: subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-c", "copy", "-movflags", "+faststart", out], check=True); print("0 sounds ->", out); return
    for k, (t, n, lv) in enumerate(events):
        path, peak, mx = S[n]; cmd += ["-i", path]; ms = int(round(t * 1000))
        fc.append(f"[{k + 1}:a]atrim=0:{mx},afade=t=out:st={max(0, mx - 0.12):.2f}:d=0.12,aresample=48000,aformat=channel_layouts=stereo,volume={lv - peak + TRIM:.1f}dB,adelay={ms}|{ms}[s{k}]"); labs.append(f"[s{k}]")
    fc.append("".join(labs) + f"amix=inputs={len(labs)}:normalize=0:duration=first[a]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True); print(len(events), "sounds ->", out)
def bed(src, out):
    r = subprocess.run(["ffmpeg", "-v", "info", "-ss", str(MSTART), "-t", str(DUR), "-i", MUSIC, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
    g = MUSIC_MEAN - float(re.search(r"mean_volume: (-?[\d.]+)", r).group(1))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", MUSIC, "-filter_complex",
        f"[1:a]atrim={MSTART}:{MSTART + DUR},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume={g:.1f}dB,afade=t=in:st=0:d=0.4,afade=t=out:st={DUR - 1.5}:d=1.5[m];[0:a][m]amix=inputs=2:normalize=0:duration=first[a]",
        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", out], check=True)
os.makedirs("renders", exist_ok=True)
for src, dst in ((f"{OUT}/{TITLE} - 9x16 Reel ({STEM} - no SFX).mp4", f"{OUT}/{TITLE} - 9x16 Reel ({STEM} - %s).mp4"), (f"renders/{TITLE} ({STEM} - no SFX) (phone).mp4", f"renders/{TITLE} ({STEM} - %s) (phone).mp4")):
    mix(src, EV, dst % "no music")
    if MUSIC: tmp = "renders/_bed.mp4"; bed(src, tmp); mix(tmp, EV, dst % "with music")
