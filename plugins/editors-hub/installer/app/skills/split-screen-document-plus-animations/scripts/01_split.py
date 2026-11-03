#!/usr/bin/env python3
"""Step 1 - the split-screen base edit.   01_split.py "<Raw folder with camera.mp4 + screen.mp4>" <slug> "<out.mp4>" [options]
Camera (4K, the creator's mic) + the document screen recording (iPad or other screen, same length, already in sync) ->
one 4K video: the document on the LEFT and the creator on the RIGHT, cutting to the creator FULL SCREEN whenever they look
up at the camera to make a point. No cuts, no audio change. Work files: <work root>/<slug>/split/.
  --plan-only        stop after the section list (segs.json) without rendering
  --min-full N       shortest full-screen section in seconds (default: the setup answer, normally 5; raise it if the switching feels busy)
  --force-full a-b[,c-d]  raw seconds to force full screen (the opening hook is always full screen: check the first section)
  --crop W:H:X:Y     where the document sits inside the screen recording, in screen pixels (default: worked out
                     automatically; the result is written to split/crop.txt, which can also be edited by hand)
  --pupil N          how high the pupils must sit in the eye to count as "looking at the camera" (default 0.03)
  --eye-open N       how open the eyes must be (default 0.17). Lower both a little if a creator who plainly looks to camera
                     is never detected; raise them if too much goes full screen.
How it decides: Apple Vision face landmarks at 5 fps. The creator is "looking at the camera" when their pupils sit high in
the eye and the eyes are open; a section goes full screen when that holds and the document is not being scrolled or
written on. Needs macOS (Vision, VideoToolbox) and the Xcode command line tools (swiftc)."""
import json, os, subprocess, sys
import numpy as np
raw, slug, out = os.path.abspath(os.path.expanduser(sys.argv[1])), sys.argv[2], os.path.abspath(os.path.expanduser(sys.argv[3]))
opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
WORK_ROOT = os.path.expanduser("@@WORK_ROOT@@")     # the same working folder the educational-youtube-editor scripts use
if "@" * 2 in WORK_ROOT: sys.exit("This skill has not been set up yet: run the setup interview (setup/SETUP.md), then python3 setup/apply_profile.py")
try: MINFULL = float(opt("--min-full", "@@MIN_FULL_SECONDS@@"))
except ValueError: MINFULL = 5.0
PUPIL = float(opt("--pupil", 0.03)); EYEOPEN = float(opt("--eye-open", 0.17)); HERE = os.path.dirname(os.path.abspath(__file__))
D = f"{WORK_ROOT}/{slug}/split"; os.makedirs(D, exist_ok=True); cam, scr = f"{raw}/camera.mp4", f"{raw}/screen.mp4"
for f in (cam, scr): os.path.exists(f) or sys.exit(f"missing {f}")
run = lambda c, **k: subprocess.run(c, check=True, **k)
probe = lambda p, e: subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", e, "-of", "csv=p=0", p], text=True).strip()
cw, ch = map(int, probe(cam, "stream=width,height").split(",")); sw, sh = map(int, probe(scr, "stream=width,height").split(","))
dc, ds = (float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p])) for p in (cam, scr))
(cw, ch) == (3840, 2160) or sys.exit(f"camera is {cw}x{ch}: this step is built for 3840x2160. Stop and tell the creator.")
LAND = sw > sh   # landscape screen: the document takes about 75% of the frame on its own page colour, the creator a column of about 25% on the right ("flush column"); small on-screen controls (an undo pill) are left in on purpose
abs(dc - ds) < 0.5 or sys.exit(f"camera ({dc:.1f}s) and screen ({ds:.1f}s) differ in length: they are not in sync. Stop and tell the creator.")

# ---- 1. proxies + gaze
if not os.path.exists(f"{D}/gaze.txt"):
    print("proxies and gaze tracking ...", flush=True)
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", cam, "-vf", "fps=5,scale=960:-2", "-an", "-c:v", "h264_videotoolbox", "-b:v", "3M", f"{D}/camp.mp4"])
    binp = f"{WORK_ROOT}/.bin/gaze"; os.makedirs(os.path.dirname(binp), exist_ok=True)
    if not os.path.exists(binp): run(["swiftc", "-O", f"{HERE}/gaze.swift", "-o", binp], stderr=subprocess.DEVNULL)
    open(f"{D}/gaze.txt", "w").write(subprocess.run([binp, f"{D}/camp.mp4"], capture_output=True, text=True).stdout)

# ---- 2. where the document is inside the screen recording (app tabs, toolbar, pen palette, undo pill and page edges cropped away)
if "--crop" in sys.argv: open(f"{D}/crop.txt", "w").write(opt("--crop", ""))      # an explicit crop always wins
if LAND and not os.path.exists(f"{D}/crop.txt"):
    left, top, right, bot = 4, round(sh * 98 / 1116), sw - 64, sh - 54      # app tabs + toolbar above, pen palette right, bottom bar below (measured on a 1116-high landscape tablet capture: other apps differ)
    open(f"{D}/crop.txt", "w").write(f"{(right - left) // 2 * 2}:{(bot - top) // 2 * 2}:{left}:{top}"); print("landscape document crop", open(f"{D}/crop.txt").read(), "LOOK at a frame before trusting it; correct it with --crop W:H:X:Y if app chrome is still in.")
if not os.path.exists(f"{D}/crop.txt"):
    p = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", scr, "-vf", "fps=1/10,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    fr = np.frombuffer(p, np.uint8).reshape(-1, sh, sw); L, R = [], []
    for f in fr:
        c = np.percentile(f[int(sh * .13):int(sh * .97)], 90, axis=0); w = np.where(c > 200)[0]
        if len(w): L.append(int(w.min())); R.append(int(w.max()))
    L and R or sys.exit("could not find the document page in the screen recording: pass --crop W:H:X:Y (the document's rectangle in screen pixels)")
    left = max(set(L), key=L.count) + 3; right = max(set(R), key=R.count) - 3; top = round(sh * 204 / 1896)       # 204 px clears a floating pen palette on a 1896-high portrait capture
    w_ = (right - left) // 2 * 2; h_ = round(w_ * 2160 / 1686) // 2 * 2
    if top + h_ > sh - 24: h_ = (sh - 24 - top) // 2 * 2; w_ = round(h_ * 1686 / 2160) // 2 * 2
    open(f"{D}/crop.txt", "w").write(f"{w_}:{h_}:{left}:{top}"); print(f"document crop {w_}:{h_}:{left}:{top} (of {sw}x{sh}). LOOK at a frame before trusting it.")
crop = open(f"{D}/crop.txt").read().strip(); cwid, chgt, cx0, cy0 = map(int, crop.split(":"))

# ---- 3. sections
rows = [l.split() for l in open(f"{D}/gaze.txt") if l.strip()]; T = np.array([float(r[0]) for r in rows]); n = len(T)
pup = np.array([float(r[8]) if len(r) > 2 else np.nan for r in rows]); eo = np.array([float(r[7]) if len(r) > 2 else np.nan for r in rows])
look = ((pup > PUPIL) & (eo > EYEOPEN)).astype(float); look[np.isnan(pup)] = 0; sm = np.convolve(look, np.ones(7) / 7, "same")
gw, gh = 166, round(166 * chgt / cwid)
p = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", scr, "-vf", f"crop={crop},fps=5,scale={gw}:{gh},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
S = np.frombuffer(p, np.uint8).reshape(-1, gh, gw); act = np.zeros(n)
for i in range(1, min(n, len(S))): act[i] = (np.abs(S[i].astype(int) - S[i - 1]) > 24).mean()
busy = np.convolve((act > 0.002).astype(float), np.ones(5), "same") > 0; state = (sm >= 0.6) & (~busy)
def runs(s):
    o = []; i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]: j += 1
        o.append((i, j, bool(s[i]))); i = j
    return o
def fill(s, val, mx):
    for a, b, v in runs(s):
        if v == val and b - a < mx and a > 0 and b < len(s): s[a:b] = not val
    return s
for ff in opt("--force-full", "").split(","):     # e.g. --force-full 0-13: a stretch they plainly deliver to camera but the tracker split (an animated page on the screen counts as 'busy')
    if ff: fa, fb = map(float, ff.split("-")); state[(T >= fa) & (T < fb)] = True
state = fill(state, False, 8); state = fill(state, True, int(MINFULL * 5)); state = fill(state, False, 15)   # look-aways under 1.6 s stay full; short fulls dropped; split slivers under 3 s merge
segs = [{"start": round(float(T[a]), 2), "end": round(float(T[b - 1] + 0.2), 2), "mode": "full" if v else "split"} for a, b, v in runs(state)]
json.dump(segs, open(f"{D}/segs.json", "w"), indent=0); full = sum(s["end"] - s["start"] for s in segs if s["mode"] == "full")
print(f"{len(segs)} sections | full screen {full:.0f}s of {T[-1]:.0f}s ({100 * full / T[-1]:.0f}%) | {sum(s['mode'] == 'full' for s in segs)} full-screen moments")
if "--plan-only" in sys.argv: sys.exit()

# ---- 4. render in 300.3 s chunks (one long ffmpeg run can be killed by the host; chunks also resume), then join with the camera's own audio
FPS = 30000 / 1001; CL = 9000 / FPS; nch = int(np.ceil(dc / CL)); face = [float(r[1]) for r in rows if len(r) > 2]; fx = float(np.median(face))
DW = 2880 if LAND else 1686; CW = 3840 - DW; x0 = int(min(max(fx * 3840 - CW / 2, 0), 3840 - CW)) // 2 * 2; os.makedirs(f"{D}/parts", exist_ok=True); parts = []
for k in range(nch):
    a = k * CL; pt = f"{D}/parts/p_{k:02d}.mp4"; parts.append(pt)
    if os.path.exists(pt): continue
    terms = [f"between(t,{max(s['start'] - a, 0):.3f},{s['end'] - a:.3f})" for s in segs if s["mode"] == "split" and s["end"] > a and s["start"] < a + CL]
    ov = f"[full][sp]overlay=0:0:enable='{'+'.join(terms) or '0'}':eof_action=pass,format=yuv420p[v]"
    if LAND:
        dh = round(DW * chgt / cwid) // 2 * 2
        pc = "@@DOC_PAGE_COLOR@@".strip().lstrip("#")
        if len(pc) != 6 or any(c not in "0123456789abcdefABCDEF" for c in pc):        # "auto": the page colour is read from the document itself
            px = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", "1", "-i", scr, "-frames:v", "1", "-vf", f"crop={crop},crop=8:8:0:0,scale=1:1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
            pc = "%02X%02X%02X" % tuple(px[:3]) if len(px) >= 3 else "FFFFFF"
        fc = (f"[0:v]split[full][c];[c]crop={CW}:2160:{x0}:0[right];color=c=0x{pc}:s={DW}x2160:r=30000/1001[bgc];[1:v]fps=30000/1001,crop={crop},scale={DW}:{dh}:flags=lanczos[dd];"
              f"[bgc][dd]overlay=0:{(2160 - dh) // 2}:shortest=1[left];[left][right]hstack=shortest=1[sp];" + ov)
    else:
        fc = (f"[0:v]split[full][c];[c]crop={CW}:2160:{x0}:0[right];[1:v]fps=30000/1001,crop={crop},scale={DW}:2160:flags=lanczos[left];"
              f"[left][right]hstack[sp];" + ov)
    open(f"{D}/parts/fc_{k}.txt", "w").write(fc); print(f"chunk {k + 1}/{nch} ...", flush=True)
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{a:.4f}", "-i", cam, "-ss", f"{a:.4f}", "-i", scr, "-filter_complex_script", f"{D}/parts/fc_{k}.txt",
         "-map", "[v]", "-an", "-frames:v", "9000", "-c:v", "hevc_videotoolbox", "-b:v", "28M", "-tag:v", "hvc1", pt + ".tmp.mp4"]); os.rename(pt + ".tmp.mp4", pt)
open(f"{D}/list.txt", "w").write("".join("file '" + p.replace("'", "'\\''") + "'\n" for p in parts)); os.makedirs(os.path.dirname(out), exist_ok=True)
run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{D}/list.txt", "-i", cam, "-map", "0:v", "-map", "1:a", "-c", "copy", "-tag:v", "hvc1", "-movflags", "+faststart", out])
print("wrote", out, "| the chunk files in", f"{D}/parts", "can be deleted once the video is checked")
