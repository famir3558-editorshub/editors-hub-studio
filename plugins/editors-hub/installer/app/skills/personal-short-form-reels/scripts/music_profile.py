#!/usr/bin/env python3
"""Where should a track start under a short reel?   music_profile.py "<track>" [reel seconds, default 16]
Prints the loudness of every 2 seconds and the loudest stretches of the reel's length. Claude cannot HEAR music: choose tracks from what is known about
the piece plus this profile, start where the music is already playing properly (not in a quiet intro, unless a sparse intro is the point), and let the creator audition."""
import subprocess, sys, numpy as np
p = sys.argv[1]; L = float(sys.argv[2]) if len(sys.argv) > 2 else 16.0
a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vn", "-ac", "1", "-ar", "8000", "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
e = [20 * np.log10(np.sqrt((a[i:i + 16000] ** 2).mean()) + 1e-9) for i in range(0, len(a) - 16000, 16000)]
print(f"{len(a) / 8000:.0f}s  |  dB per 2 s:"); print(" ".join(f"{2 * i}:{v:.0f}" for i, v in enumerate(e)))
n = max(1, int(L // 2)); w = sorted(((float(np.mean(e[i:i + n])), 2 * i) for i in range(len(e) - n)), reverse=True)
seen = []
for m, s in w:
    if all(abs(s - x) > L for x in seen): seen.append(s); print(f"  strong {L:.0f}s stretch from {s}s (mean {m:.0f} dB)")
    if len(seen) == 4: break
