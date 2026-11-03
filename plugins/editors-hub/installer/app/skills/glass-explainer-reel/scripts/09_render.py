#!/usr/bin/env python3
"""Step 9 - build, check, render, then mix the quiet sound effects under the voice.
   09_render.py <slug> [--draft] [--tag v2] [--no-sfx] [--music "<file>" [--music-start <s>]]
--draft: fast low-quality render into the project's renders/ folder for the review pass (sound effects included).
Final : "<out>/<name> - 9x16[ tag].mp4" (master: H.264 high bitrate, the speaker's voice + sound effects, AAC 320k), the same
        without effects as "... (no SFX).mp4", and a phone copy under 30 MB.
--music: ONLY when the creator has said yes and named the track. Also writes "... (with music).mp4": the bed sits about 11 dB
        under the voice (-39 dB mean), starts at --music-start (where the beat drops), 0.4 s fade in, 1.5 s fade out.
Sound cues come from <project>/sfx.json (written by build.py); the sound files are the creator's own pack, played by role from sfx_map.json (made at setup with scripts/sfx_probe.py).
One render at a time when the output is on an external drive."""
import json, os, re, subprocess, sys
from common import PROJECTS_ROOT, load_sfx, sfx_role
slug = sys.argv[1]; PJ = f"{PROJECTS_ROOT}/{slug}-glass"; P = json.load(open(f"{PJ}/project.json")); draft = "--draft" in sys.argv
opt = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
tag = (" " + opt("--tag")) if "--tag" in sys.argv else ""; music = opt("--music"); mstart = float(opt("--music-start", 0))
r = subprocess.run([sys.executable, "build.py"], cwd=PJ, capture_output=True, text=True); print(r.stdout, r.stderr)
r.returncode == 0 or sys.exit("build.py failed")
if "WARN no captions" in r.stdout: sys.exit("refusing to render without captions")
chk = subprocess.run(["npx", "hyperframes", "check"], cwd=PJ, capture_output=True, text=True)
print("\n".join(l for l in (chk.stdout + chk.stderr).splitlines() if any(s in l for s in ("✗", "error", "Error", "warn", "Check")))[:3000])
os.makedirs(f"{PJ}/renders", exist_ok=True)
final = f"{PJ}/renders/draft.mp4" if draft else f"{P['out']}/{P['stem']} - 9x16{tag}.mp4"
dry = final[:-4] + " (no SFX).mp4"
fps = P["fps_str"] if "/" in P["fps_str"] and not P["fps_str"].endswith("/1") else str(round(P["fps"]))
subprocess.run(["npx", "hyperframes", "render", "-o", dry, "--fps", fps, "--quality", "draft" if draft else "high", "--skill", "general-video"], cwd=PJ, check=True)

# ---- sound: quiet, key moments only. TRIM keeps whooshes near -29.5 dBFS and pops near -32.5 (the voice peaks near -3).
# Sounds come from the creator's own pack by ROLE (sfx_map.json, made at setup). A role the pack lacks falls back to the nearest one it
# has (shine2 -> shine -> pop; swish / swoosh -> woosh; accept / dtext / data -> pop). No map at all = delivered without effects.
TRIM = -8.5; MUSIC_MEAN = -39.0
S = {} if "--no-sfx" in sys.argv else load_sfx(PJ)             # role: (file, measured peak dB, seconds used)
J = json.load(open(f"{PJ}/sfx.json")) if os.path.exists(f"{PJ}/sfx.json") else {"cues": [], "dur": P["dur"]}
cues = []
for t, name, lv in J["cues"]:
    r_ = sfx_role(S, name)
    if r_: cues.append((t, r_, lv))
if not S and "--no-sfx" not in sys.argv: print("NOTE no sound pack set up: this render has no sound effects (the master and the no-SFX copy are the same).")


def mix(src, out, bed=None):
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", src]; fc = []; labs = ["[0:a]"]; n = 1
    if bed:
        info = subprocess.run(["ffmpeg", "-v", "info", "-ss", str(mstart), "-t", str(J["dur"]), "-i", bed, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
        g = MUSIC_MEAN - float(re.search(r"mean_volume: (-?[\d.]+)", info).group(1)); cmd += ["-i", bed]
        fc.append(f"[{n}:a]atrim={mstart}:{mstart + J['dur']},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume={g:.1f}dB,afade=t=in:st=0:d=0.4,afade=t=out:st={J['dur'] - 1.5:.2f}:d=1.5[m]"); labs.append("[m]"); n += 1
    for k, (t, name, lv) in enumerate(cues):
        f_, peak, mx = S[name]; cmd += ["-i", f_]; ms = int(round(t * 1000))
        fc.append(f"[{n}:a]atrim=0:{mx},afade=t=out:st={max(0, mx - 0.12):.2f}:d=0.12,aresample=48000,aformat=channel_layouts=stereo,volume={lv - peak + TRIM:.1f}dB,adelay={ms}|{ms}[s{k}]"); labs.append(f"[s{k}]"); n += 1
    if len(labs) == 1: subprocess.run(["cp", src, out], check=True); return
    fc.append("[0:a]aresample=48000,aformat=channel_layouts=stereo[v0]"); labs[0] = "[v0]"
    fc.append("".join(labs) + f"amix=inputs={len(labs)}:normalize=0:duration=first[a]")
    subprocess.run(cmd + ["-filter_complex", ";".join(fc), "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", out], check=True)


mix(dry, final); print(f"wrote {final} ({len(cues)} quiet sound effects under the voice) and {dry}")
outs = [final]
if music:
    wm = final[:-4] + " (with music).mp4"; mix(dry, wm, bed=music); outs.append(wm); print("wrote", wm, "(deliver BOTH: with and without music)")
if draft: os.remove(dry)
else:
    D = P["dur"]; br = int(min(6000, 26 * 8000 / D - 170)); log = f"{PJ}/renders/pass"
    for o in outs:
        ph = o[:-4] + " (phone).mp4"
        for n_, extra in ((1, ["-an", "-f", "mp4", "/dev/null"]), (2, ["-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", ph])):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", o, "-c:v", "libx264", "-preset", "slow", "-b:v", f"{br}k", "-maxrate", f"{br * 5 // 4}k", "-bufsize", "8000k",
                            "-pass", str(n_), "-passlogfile", log, *extra], check=True)
        print("phone copy", ph)
print(f"next: python3 {os.path.dirname(os.path.abspath(__file__))}/10_review.py {slug} \"{final}\"")
