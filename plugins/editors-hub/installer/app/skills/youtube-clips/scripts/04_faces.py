#!/usr/bin/env python3
"""Find the speaker's face through a cut, so graphics can be kept off it.   macOS only (Apple Vision).
      04_faces.py "<cut video>" "<project dir>" [step 0.25]
Samples the cut every `step` seconds, detects the largest face with Apple's Vision framework (face_boxes.swift, compiled with swiftc) and writes
<project>/faces.json: [{"t", "x", "y", "w", "h"}] in SOURCE pixels. The engine widens each face box into a head box
(hair, chin) and refuses to place a 16:9 graphic over it. Open <project>/faces.jpg to check the boxes by eye."""
import json, os, subprocess, sys, tempfile
cut, pj = sys.argv[1], sys.argv[2]; step = float(sys.argv[3]) if len(sys.argv) > 3 else 0.25
here = os.path.dirname(os.path.abspath(__file__)); tmp = tempfile.mkdtemp()
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", cut]))
subprocess.run(["ffmpeg", "-v", "error", "-i", cut, "-vf", f"fps={1 / step}", "-q:v", "3", f"{tmp}/f%04d.jpg"], check=True)
files = sorted(f for f in os.listdir(tmp) if f.endswith(".jpg"))
exe = f"{tmp}/fb"
subprocess.run(["swiftc", "-O", f"{here}/face_boxes.swift", "-o", exe], check=True, stderr=subprocess.DEVNULL)
out = subprocess.check_output([exe] + [f"{tmp}/{f}" for f in files], text=True)
faces = []
for k, line in enumerate(out.strip().splitlines()):
    p = line.rsplit(" ", 4)
    if p[-1] != "none" and len(p) == 5:
        faces.append({"t": round(k * step, 3), "x": int(p[1]), "y": int(p[2]), "w": int(p[3]), "h": int(p[4])})
json.dump(faces, open(f"{pj}/faces.json", "w"))
miss = len(files) - len(faces)
faces or sys.exit(f"no face found in {len(files)} samples: check the cut, or write faces.json by hand from gridded stills (cut/frames.py)")
xs = [f["x"] for f in faces]; print(f"{len(faces)} faces in {len(files)} samples over {dur:.1f}s ({miss} missed). Face left edge ranges x {min(xs)}-{max(xs)}, centre about ({sum(f['x'] + f['w'] / 2 for f in faces) / len(faces):.0f}, {sum(f['y'] + f['h'] / 2 for f in faces) / len(faces):.0f})")
if miss > len(files) * 0.2: print("WARNING many samples have no face (profile turned away, hand over face): check faces.jpg and add boxes by hand if needed")
# check sheet: 12 samples with the face box and the widened head box drawn
pick = faces[:: max(1, len(faces) // 12)][:12]
for n, f in enumerate(pick):
    hx, hy, hw, hh = f["x"] - 0.5 * f["w"], f["y"] - 0.65 * f["h"], 2.0 * f["w"], 1.95 * f["h"]
    src = f"{tmp}/f{int(round(f['t'] / step)) + 1:04d}.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"drawbox={f['x']}:{f['y']}:{f['w']}:{f['h']}:yellow:4,drawbox={hx:.0f}:{hy:.0f}:{hw:.0f}:{hh:.0f}:red:4,scale=640:-1", f"{tmp}/s{n:02d}.jpg"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{tmp}/s%02d.jpg", "-frames:v", "1", "-vf", "tile=4x3", "-q:v", "4", f"{pj}/faces.jpg"], check=True)
print(f"check sheet: {pj}/faces.jpg (yellow = detected face, red = protected head box)")
