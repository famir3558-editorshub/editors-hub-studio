#!/usr/bin/env python3
"""Step 8 - check the plan and render.   08_render.py <slug> --lint | --draft | --final [--tag v2]
  --lint    only check plan.json against the cut (run after every change to the plan)
  --draft   fast 720x1280 render of the whole edit for review: "<out>/<name> - DRAFT.mp4"
  --final   1080x1920 master "<name> - EDIT.mp4" plus "<name> - EDIT (phone).mp4" (under 30 MB, for sending)
The finished video is always 9:16 (1080x1920).

plan.json (all times are CUT-timeline seconds, from edit.txt / cuts.json):
  "frame": {"mode": "fill", "focus": [0.5, 0.5]}     how the MAIN video sits in the 9:16 frame.
           fill = it covers the frame (a 16:9 source is cropped around "focus": set focus x so the speaker is centred)
           fit  = the whole 16:9 picture sits inside the vertical frame with black above and below
  "broll": [{"at": 4.21, "dur": 2.6, "clip": 132, "in": 3.0,       where it goes, which clip (library id or name), where in the clip
             "mode": "fit", "focus": [0.5, 0.5], "speed": 1.0, "why": "typing = writing the hook"}]
           mode defaults to fit for a landscape clip (whole picture inside the frame) and fill for a portrait one.
           Use "fill" on a landscape clip only when its subject survives the 9:16 crop ("focus" chooses the part kept).
  "captions", "text": see 07_text.py (run it after every change; it builds the text layer this script overlays)
B-roll replaces the picture only; the speaker's voice always continues underneath. B-roll audio is never used."""
import hashlib, json, os, subprocess, sys
from fractions import Fraction
from common import work, load, save, library, frame_mode, vf_place, num, CW, CH

W = work(sys.argv[1]); M = load(W, "meta.json"); plan = load(W, "plan.json") or sys.exit("no plan.json")
mode = next((m for m in ("--lint", "--draft", "--final") if m in sys.argv), None) or sys.exit(__doc__)
tag = (" " + sys.argv[sys.argv.index("--tag") + 1]) if "--tag" in sys.argv else ""
"cut" in M or sys.exit("render the cut first (05_render_cut.py)")
FR = M["fps"]; FPS = float(Fraction(FR)); TOT = M["cut_dur"]; snap = lambda t: round(t * FPS) / FPS
cat = library(); cuts = load(W, "cuts.json", []); L = load(W, "layer.json"); cw = load(W, "cut_words.json")
sig = hashlib.md5(json.dumps([plan.get("text"), plan.get("captions"), plan.get("broll"), plan.get("frame"), plan.get("style"), cw], sort_keys=True).encode()).hexdigest()
B = sorted(plan.get("broll", []), key=lambda b: b["at"]); errors, warns = [], []


def clip_of(b):
    hit = [c for c in cat if str(c["id"]) == str(b["clip"])] or [c for c in cat if b["clip"] in (c["clip"], os.path.basename(c["clip"]))]
    return hit[0] if hit else None


for b in B:
    b["at"] = snap(b["at"]); b["end"] = snap(b["at"] + b["dur"]); c = clip_of(b); sp = b.get("speed", 1.0)
    if not c:
        errors.append(f"b-roll at {b['at']:.2f}: clip \"{b['clip']}\" is not in the B-roll library (use its id or clip name from library.json)"); continue
    b["file"] = c["file"]; b["w"], b["h"] = c["w"], c["h"]; b["mode"] = b.get("mode", "fit" if c["w"] > c["h"] else "fill")
    if not os.path.exists(c["file"]):
        errors.append(f"b-roll at {b['at']:.2f}: file missing (is the footage drive connected?): {c['file']}")
    if not c.get("notes"):
        warns.append(f"clip {c['id']} ({c['clip']}) has no notes in the library: it was placed without being reviewed")
    if b.get("in", 0) + b["dur"] * sp > c["dur"] + 0.01:
        errors.append(f"b-roll at {b['at']:.2f}: needs {b.get('in', 0) + b['dur'] * sp:.2f}s of \"{b['clip']}\" but it is {c['dur']:.2f}s long")
    if b["end"] > TOT + 0.02:
        errors.append(f"b-roll at {b['at']:.2f} runs past the end of the edit ({TOT:.2f}s)")
    if b["dur"] < 1.0:
        warns.append(f"b-roll at {b['at']:.2f} is {b['dur']:.2f}s: under 1s reads as a flash")
    if b["dur"] > 6:
        warns.append(f"b-roll at {b['at']:.2f} is {b['dur']:.1f}s: long; the speaker is off screen for all of it")
    if c.get("hdr"):
        warns.append(f"\"{b['clip']}\" is HDR; check its colour against the main video in the draft")
    for j in cuts:
        for edge, name in ((b["at"], "starts"), (b["end"], "ends")):
            if 0.02 < abs(edge - j["t"]) < 0.2:
                warns.append(f"b-roll at {b['at']:.2f} {name} {abs(edge - j['t']):.2f}s from the cut at {j['t']:.2f}: "
                             f"put the edge exactly on the cut, or at least 0.25s clear of it, so the jump is not seen for a few frames")
for p, q in zip(B, B[1:]):
    if q["at"] < p["end"] - 1e-6:
        errors.append(f"b-roll at {p['at']:.2f} and {q['at']:.2f} overlap")
    elif 0 < q["at"] - p["end"] < 0.8:
        warns.append(f"only {q['at'] - p['end']:.2f}s of the speaker between the b-roll ending {p['end']:.2f} and the next: join them or leave a real beat")
if not L or not os.path.exists(L["seq"] % 0):
    errors.append("the text layer has not been built: run 07_text.py")
elif L["sig"] != sig:
    errors.append("plan.json or the cut changed since the text layer was built: run 07_text.py again")
else:
    n = len(L["cards"]); words = sum(c["i1"] - c["i0"] + 1 for c in L["captions"]) + sum(c["i1"] - c["i0"] + 1 for c in L["cards"])
    print(f"text: {len(L['captions'])} captions + {n} stacks = {words} of {len(cw)} spoken words captioned")
    if words != len(cw):
        errors.append("not every spoken word is captioned")
    if n / TOT * 60 > 5:
        warns.append(f"{n / TOT * 60:.1f} stacks a minute: the stack is for the few phrases where emphasis helps; the rest stay plain captions")
    for c in L["cards"]:
        for j in cuts:
            if j["big"] and c["at"] + 0.05 < j["t"] < c["end"] - 0.05:
                warns.append(f"stack {c['id']} sits across the big jump cut at {j['t']:.2f}: check it against the speaker on both sides")
        for b in B:
            if c["at"] < b["at"] < c["end"] or c["at"] < b["end"] < c["end"]:
                warns.append(f"stack {c['id']} is on screen while the picture changes at a b-roll edge ({b['at']:.2f}-{b['end']:.2f}): move the b-roll edge or the stack")
covered = lambda t: any(b["at"] - 1e-3 <= t <= b["end"] + 1e-3 for b in B)
big = [j for j in cuts if j["big"]]; hid = [j for j in big if covered(j["t"])]; cov = sum(b["dur"] for b in B) / TOT * 100
print(f"edit {TOT:.1f}s {CW}x{CH} | {len(B)} b-roll ({cov:.0f}% of the runtime)")
print(f"big jump cuts: {len(hid)} of {len(big)} hidden under b-roll; still visible at: " + (", ".join(f"{j['t']:.2f}" for j in big if not covered(j["t"])) or "none"))
if B and B[0]["at"] < 1.5:
    warns.append("b-roll in the first 1.5s: the opening normally stays on the speaker so the viewer meets them")
if cov > num("broll_max_share", 35) + 10:      # the creator's share + 10 points
    warns.append(f"b-roll covers {cov:.0f}% of the edit: the speaker should stay the main picture")
for w_ in warns:
    print("WARN ", w_)
for e in errors:
    print("ERROR", e)
if errors:
    sys.exit(1)
if mode == "--lint":
    sys.exit(0)

fm, ff = frame_mode(M, plan); inp = ["-i", M["cut"]]; ch = [f"[0:v]{vf_place(M['w'], M['h'], fm, ff)}[v0]"]; cur, n = "v0", 0
for b in B:
    n += 1; sp = b.get("speed", 1.0)
    inp += ["-ss", f"{b.get('in', 0):.3f}", "-t", f"{b['dur'] * sp + 0.2:.3f}", "-i", b["file"]]
    ch.append(f"[{n}:v]setpts=(PTS-STARTPTS)/{sp},fps={FR},{vf_place(b['w'], b['h'], b['mode'], b.get('focus', [0.5, 0.5]))},setpts=PTS+{b['at']:.5f}/TB[b{n}]")
    ch.append(f"[{cur}][b{n}]overlay=enable='gte(t,{b['at'] - 0.002:.5f})*lt(t,{b['end'] - 0.002:.5f})':eof_action=pass[v{n}]"); cur = f"v{n}"
n += 1; inp += ["-framerate", FR, "-start_number", "0", "-i", L["seq"]]
ch.append(f"[{cur}][{n}:v]overlay=0:0:eof_action=pass:format=auto[v{n}]"); cur = f"v{n}"
out_dir, stem = M["out"], M["stem"]
if mode == "--draft":
    ch.append(f"[{cur}]scale=720:1280,format=yuv420p[vo]"); out = f"{out_dir}/{stem} - DRAFT{tag}.mp4"; enc = ["-c:v", "h264_videotoolbox", "-b:v", "5M"]
else:
    ch.append(f"[{cur}]format=yuv420p[vo]"); out = f"{out_dir}/{stem} - EDIT{tag}.mp4"; enc = ["-c:v", "hevc_videotoolbox", "-b:v", "20M", "-tag:v", "hvc1"]
subprocess.run(["ffmpeg", "-v", "error", "-stats", "-y", *inp, "-filter_complex", ";".join(ch), "-map", "[vo]", "-map", "0:a",
                *enc, "-r", FR, "-c:a", "copy", "-t", f"{TOT:.3f}", "-movflags", "+faststart", out], check=True)
M["last"] = out; print("wrote", out)
if mode == "--final":
    ph = f"{out_dir}/{stem} - EDIT{tag} (phone).mp4"; rate = int(min(8e6, 26e6 * 8 / TOT - 192e3))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out, "-c:v", "h264_videotoolbox", "-b:v", str(rate),
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", ph], check=True)
    M["phone"] = ph; print("wrote", ph)
save(W, "meta.json", M)
