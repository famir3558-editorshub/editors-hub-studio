#!/usr/bin/env python3
"""Clean the hiss and bring a finished clip to a normal listening level without clipping.
    05_loudness.py "<in.mp4>" "<out.mp4>" [-14] [--no-denoise]
Call recordings are very quiet (often around -30 LUFS). Two-pass EBU R128 loudness normalisation to
the target (default -14 LUFS, the level social platforms play at) with a true-peak ceiling of -1.5 dBTP, so nothing
peaks. Raising a quiet recording raises its room hiss by the same amount, so a light noise reduction runs first:
a 70 Hz high-pass and ffmpeg's afftdn at 14 dB with noise tracking. On a typical call that lowers the steady hiss
by about 9 dB and leaves the voice level almost unchanged (about 0.2 dB). Keep it light:
stronger settings start to sound processed. The picture is copied untouched; only the audio is re-encoded (AAC 320k, 48 kHz). Prints before and after."""
import json, re, subprocess, sys
args = [a for a in sys.argv[1:] if not a.startswith("--")]
src, dst = args[0], args[1]; I = float(args[2]) if len(args) > 2 else -14.0; TP, LRA = -1.5, 11
DN = "" if "--no-denoise" in sys.argv else "highpass=f=70,afftdn=nr=14:nf=-60:tn=1,"


def measure(path, pre=""):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-vn", "-af", f"{pre}loudnorm=I={I}:TP={TP}:LRA={LRA}:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    return json.loads(re.findall(r"\{[^{}]+\}", r.stderr)[-1])


m = measure(src, DN)
af = (DN + f"loudnorm=I={I}:TP={TP}:LRA={LRA}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
      f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-c:v", "copy", "-af", af, "-ar", "48000", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", dst], check=True)
o = measure(dst)
print(("denoised, " if DN else "") + f"{dst.split('/')[-1]}: {m['input_i']} LUFS, peak {m['input_tp']} dBTP  ->  {o['input_i']} LUFS, peak {o['input_tp']} dBTP")
if float(o["input_tp"]) > -1.0: print("WARNING peak is above -1 dBTP: lower the target and run again")
