#!/usr/bin/env python3
"""louder.py "<edit folder>" "<stem>" <project dir> [--target -19.8] [--ceiling -6] [--denoise 6] [--suffix " - YouTube Edit v2"]
        louder.py --measure "<any video or audio file>"
The audio fix for QUIET recordings: the creator's voice is raised to the target loudness (setup answer, default about
-19.8 LUFS), given a LIGHT de-noise for the mic hiss the boost brings up (setup answer, default 6 dB), and limited at
-6 dB. Nothing else: no EQ, no compressor, no de-esser, no gate. The voice stays natural. Sound effects are mixed back
underneath at their original level, never through the gain or the limiter.
Only needed when the recording is quiet (a dynamic microphone into a screen recorder often comes in at about -37 LUFS).
Measure first (--measure) and check with the creator before applying: this is a setup answer (`quiet_audio_fix`,
default `ask`). --denoise 0 turns the de-noise off.
Rewrites "<stem><suffix>.mp4" and "<stem><suffix> (no SFX).mp4" in place: video copied, audio replaced. The untouched voice is
kept as <project>/renders/voice-raw.wav so this can be re-run with other settings."""
import os, re, subprocess, sys
opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
def lufs(p):
    r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-i", p, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1]), float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)[-1])
if "--measure" in sys.argv:                      # louder.py --measure "<any video or audio file>"
    I, pk = lufs(sys.argv[sys.argv.index("--measure") + 1])
    print(f"loudness {I:.1f} LUFS, peak {pk:.1f} dB. " + ("QUIET: the fix is likely needed, check with the creator." if I < -24 else "Normal level: leave the audio alone." if I > -20 else "Borderline: play the creator a sample."))
    sys.exit()
E, stem, PJ = sys.argv[1], sys.argv[2], os.path.expanduser(sys.argv[3])
def _num(v, d):
    try: return float(v)
    except ValueError: return d     # the setup answer was not a number: the default stands
TARGET = float(opt("--target", _num("@@VOICE_TARGET_LUFS@@", -19.8))); CEIL = float(opt("--ceiling", -6.0)); NR = float(opt("--denoise", _num("@@VOICE_DENOISE_DB@@", 6))); SUF = opt("--suffix", " - YouTube Edit v2")
final = f"{E}/{stem}{SUF}.mp4"; dry = f"{E}/{stem}{SUF} (no SFX).mp4"; W = f"{PJ}/renders"; raw = f"{W}/voice-raw.wav"
if not os.path.exists(raw):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", dry, "-vn", "-c:a", "pcm_s24le", raw], check=True)
I0, _ = lufs(raw); g = TARGET - I0; up = f"{W}/voice-up.wav"; lim = 10 ** (CEIL / 20)
floor = float(re.findall(r"Noise floor dB: (-?[\d.]+)", subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", raw, "-af", "astats=measure_perchannel=none", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
for _ in range(4):
    nf = min(-20, max(-80, floor + g + 0.5))    # the hiss sits at the recording's noise floor plus the boost
    dn = f"afftdn=nr={NR:g}:nf={nf:.1f}:tn=1," if NR > 0 else ""
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", raw, "-af", f"volume={g:.2f}dB,{dn}alimiter=limit={lim:.4f}:attack=5:release=60:level=false", "-c:a", "pcm_s24le", up], check=True)
    I1, pk = lufs(up)
    if abs(I1 - TARGET) < 0.15: break
    g += TARGET - I1
print(f"{stem}: voice {I0:.1f} -> {I1:.1f} LUFS (boost {g:.1f} dB, peak {pk:.1f} dB, de-noise {NR:g} dB at floor {nf:.0f} dB)")
tmp = f"{E}/.louder-tmp.mp4"
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", dry, "-i", up, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", tmp], check=True)
os.replace(tmp, dry)
if os.path.exists(f"{W}/sfx.wav"):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", dry, "-i", up, "-i", f"{W}/sfx.wav", "-filter_complex",
                    "[1:a]aformat=channel_layouts=stereo[v0];[v0][2:a]amix=inputs=2:normalize=0:duration=first[a]", "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, final)
else: subprocess.run(["cp", dry, final], check=True)
I2, pk2 = lufs(final); print(f"  final {I2:.1f} LUFS, peak {pk2:.1f} dB | {final}")
