#!/usr/bin/env python3
"""Step 8 - render the whole video in chunks, join them, put their untouched audio back, add the quiet sound effects.
   08_render.py <slug> [--draft] [--tag v2] [--only 0,3] [--no-sfx] [--music "<file>" [--music-start <s>]] [--workers N]
Each chunk (a few minutes, split where nothing is on screen) is its own HyperFrames render, saved in "<out>/hf-parts".
A chunk is only re-rendered when its page changed, so fixing one scene re-renders one chunk, not the video.
Final : "<out>/<name> - YouTube Edit[ tag].mp4"  (the voice + sound effects)  and  "... (no SFX).mp4".
The master is 1080p, or 4K (the same page rendered at 2x) when the creator's setup asks for it; drafts are always 1080p.
Sound effects are played by role from the creator's own pack (sfx_map.json, made at setup). No map = no sound effects.
--draft  fast low-quality pass for review (written to the project's renders/ folder).
--music  ONLY when the creator has said yes and named the track: also writes "... (with music).mp4" (bed about 11 dB under the voice).
The voice is never processed: it is the cut's own audio track, copied across. One render at a time when the output is on an external drive."""
import hashlib, json, os, re, subprocess, sys
import numpy as np, soundfile as sf
from common import pj, load_sfx, sfx_role, master_4k
slug = sys.argv[1]; PJ = pj(slug); P = json.load(open(f"{PJ}/project.json")); draft = "--draft" in sys.argv
opt = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
tag = (" " + opt("--tag")) if "--tag" in sys.argv else ""; music = opt("--music"); mstart = float(opt("--music-start", 0)); only = opt("--only")
r = subprocess.run([sys.executable, "build.py", "--list"], cwd=PJ, capture_output=True, text=True); print(r.stdout, r.stderr[-2000:])
r.returncode == 0 or sys.exit("build.py failed")
R = json.load(open(f"{PJ}/render.json")); A = json.load(open(f"{PJ}/audit.json")); CH = R["chunks"]
parts = f"{PJ}/renders/draft-parts" if draft else f"{P['out']}/hf-parts"; os.makedirs(parts, exist_ok=True); os.makedirs(f"{PJ}/renders", exist_ok=True)
fps = P["fps_str"] if "/" in P["fps_str"] and not P["fps_str"].endswith("/1") else str(round(P["fps"]))
todo = [int(x) for x in only.split(",")] if only else range(len(CH)); files = []
for i, (a0, a1) in enumerate(CH):
    out = f"{parts}/part-{i:03d}.mp4"; files.append(out)
    if i not in todo: continue
    subprocess.run([sys.executable, "build.py", "--chunk", str(i)], cwd=PJ, check=True, capture_output=True)
    h = hashlib.sha1(open(f"{PJ}/index.html", "rb").read() + (b"d" if draft else b"f4" if (P.get("master") == "4k" or master_4k()) else b"f")).hexdigest()
    if os.path.exists(out) and os.path.exists(out + ".sha") and open(out + ".sha").read() == h: print(f"chunk {i}: unchanged, kept"); continue
    print(f"chunk {i + 1}/{len(CH)}: {a0:.1f}s -> {a1:.1f}s ...", flush=True)
    cmd = ["npx", "hyperframes", "render", "-o", out, "--fps", fps, "--quality", "draft" if draft else "high", "--quiet"]
    if opt("--workers"): cmd += ["--workers", opt("--workers")]
    if not draft and (P.get("master") == "4k" or master_4k()): cmd += ["--resolution", "landscape-4k"]
    subprocess.run(cmd, cwd=PJ, check=True); open(out + ".sha", "w").write(h)
    got = float(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "csv=p=0", out]).split()[0])
    if abs(got - (a1 - a0)) > 0.06: print(f"  WARNING chunk {i} is {got:.3f}s, expected {a1 - a0:.3f}s: sync will drift after it. Stop and look.")
missing = [f for f in files if not os.path.exists(f)]
if missing: sys.exit(f"{len(missing)} chunk(s) not rendered yet (e.g. {os.path.basename(missing[0])}); run without --only to finish")
lst = f"{parts}/list.txt"; open(lst, "w").write("".join("file '" + f.replace("'", "'\\''") + "'\n" for f in files))
final = f"{PJ}/renders/draft.mp4" if draft else f"{P['out']}/{P['stem']} - YouTube Edit{tag}.mp4"; dry = final[:-4] + " (no SFX).mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", P["cut"], "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy", "-movflags", "+faststart", dry], check=True)

# ---- sound effects: one quiet track built here, then laid under the voice. TRIM keeps whooshes near -29.5 dBFS (a voice peaks near -3).
TRIM = -8.5; MUSIC_MEAN = float(os.environ.get("MUSIC_MEAN", -39.0))
S = {} if "--no-sfx" in sys.argv else load_sfx(PJ)   # role: (file, measured peak dB, seconds used)
SR = 48000; D = P["dur"]; cues = []
for t, name, lv in R["sfx"]:
    r_ = sfx_role(S, name)
    if r_: cues.append((t, r_, lv))
kept, last = [], -9.0
for t, name, lv in cues:                         # key moments only: never two effects within 0.35 s
    if t - last >= 0.35: kept.append((t, name, lv)); last = t
trk = np.zeros((int((D + 2) * SR), 2), np.float32); cache = {}
for t, name, lv in kept:
    if name not in cache:
        tmpw = f"{PJ}/renders/_sfx_{name}.wav"          # any format in, 48 kHz stereo out
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", S[name][0], "-t", str(S[name][2] + 0.2), "-ar", str(SR), "-ac", "2", "-c:a", "pcm_f32le", tmpw], check=True)
        x, sr = sf.read(tmpw, always_2d=True, dtype="float32"); os.remove(tmpw)
        n = max(1, min(len(x), int(S[name][2] * SR))); x = x[:n].copy(); f = min(n, int(0.12 * SR)); x[-f:] *= np.linspace(1, 0, f)[:, None]; cache[name] = x
    x = cache[name] * 10 ** ((lv - S[name][1] + TRIM) / 20); i0 = max(0, int(t * SR)); trk[i0:i0 + len(x)] += x[:len(trk) - i0]
sfxwav = f"{PJ}/renders/sfx.wav"; sf.write(sfxwav, trk, SR, subtype="PCM_16")


def mix(out, bed=None):
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", dry, "-i", sfxwav]; fc = ["[0:a]aresample=48000,aformat=channel_layouts=stereo[v0]"]; labs = "[v0][1:a]"; n = 2
    if bed:
        info = subprocess.run(["ffmpeg", "-v", "info", "-ss", str(mstart), "-t", str(min(D, 120)), "-i", bed, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
        g = MUSIC_MEAN - float(re.search(r"mean_volume: (-?[\d.]+)", info).group(1)); cmd += ["-stream_loop", "-1", "-ss", str(mstart), "-i", bed]
        fc.append(f"[2:a]atrim=0:{D},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume={g:.1f}dB,afade=t=in:st=0:d=0.4,afade=t=out:st={D - 1.5:.2f}:d=1.5[m]"); labs += "[m]"; n = 3
    fc.append(f"{labs}amix=inputs={n}:normalize=0:duration=first[a]")
    subprocess.run(cmd + ["-filter_complex", ";".join(fc), "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", out], check=True)


if kept: mix(final)
else: subprocess.run(["cp", dry, final], check=True)
print(f"wrote {final}  ({len(CH)} chunks, {len(kept)} quiet sound effects = {len(kept) / (D / 60):.1f} per minute)\n      {dry}")
if music: mix(final[:-4] + " (with music).mp4", bed=music); print("wrote", final[:-4] + " (with music).mp4", "(deliver BOTH: with and without music)")
if draft: os.remove(dry)
print("\nAUDIT ", A["summary"]); [print("  ! " + x) for x in A["warnings"]]
print(f"\nnext: python3 {os.path.dirname(os.path.abspath(__file__))}/09_review.py {slug} \"{final}\"")
