#!/usr/bin/env python3
"""Bring a finished clip to a normal listening level without clipping.   05_loudness.py "<in.mp4>" "<out.mp4>" [-14]
Raw recordings and downloads vary in level. Two-pass EBU R128 loudness normalisation to
the target (default -14 LUFS, the level social platforms play at) with a true-peak ceiling of -1.5 dBTP, so nothing
peaks. The picture is copied untouched; only the audio is re-encoded (AAC 320k, 48 kHz). Prints before and after."""
import json, re, subprocess, sys
src, dst = sys.argv[1], sys.argv[2]; I = float(sys.argv[3]) if len(sys.argv) > 3 else -14.0; TP, LRA = -1.5, 11


def measure(path, extra=""):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-vn", "-af", f"loudnorm=I={I}:TP={TP}:LRA={LRA}{extra}:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    return json.loads(re.findall(r"\{[^{}]+\}", r.stderr)[-1])


m = measure(src)
af = (f"loudnorm=I={I}:TP={TP}:LRA={LRA}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
      f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-c:v", "copy", "-af", af, "-ar", "48000", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", dst], check=True)
o = measure(dst)
print(f"{dst.split('/')[-1]}: {m['input_i']} LUFS, peak {m['input_tp']} dBTP  ->  {o['input_i']} LUFS, peak {o['input_tp']} dBTP")
if float(o["input_tp"]) > -1.0: print("WARNING peak is above -1 dBTP: lower the target and run again")
