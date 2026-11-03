#!/usr/bin/env python3
"""layout.py <project_dir> [--choose A|B|C90|C80] [--from T --to T]
Where can the tier table go without covering the presenter's face?  Scans assets/cam_full.mp4 (one frame a second between --from/--to, default the
whole clip), finds the lowest the chin ever gets, and tests four placements IN THIS ORDER:
  A    full size, inside the safe zone (table y 1000-1500)
  B    full size, pushed DOWN into the bottom zone Instagram covers (as little as needed, bottom never past y 1720)
  C90  10% smaller, bottom at y 1720          C80  20% smaller, bottom at y 1720
The first one that clears the face (chin + caption line + margin) is recommended. Writes work/layout_options.jpg (every option drawn on the worst
frame, with the safe-zone lines) and layout.json. SHOW THE JPG TO THE USER and let them choose before building; --choose records their pick."""
import json, os, subprocess, sys, glob
from PIL import Image, ImageDraw, ImageFont
K = os.path.dirname(os.path.abspath(__file__)); P = os.path.abspath(sys.argv[1]); args = sys.argv[2:]
def opt(name, d=None): return args[args.index(name) + 1] if name in args else d
TW, TH, SAFE_T, SAFE_B, LOW = 760, 500, 270, 1500, 1720
try: CAPS_ON = json.load(open(os.path.join(P, "plan.json"))).get("captions", "@@CAPTIONS@@" != "off") not in (False, "off", "no")
except Exception: CAPS_ON = "@@CAPTIONS@@" != "off"
NEED = (78 if CAPS_ON else 0) + 26          # caption line above the table (when captions are on) + breathing room under the chin
W = os.path.join(P, "work"); F = os.path.join(W, "layout_frames"); os.makedirs(F, exist_ok=True)
for f in glob.glob(F + "/*.jpg"): os.remove(f)
cam = os.path.join(P, "assets", "cam_full.mp4"); rng = []
if opt("--from"): rng += ["-ss", opt("--from")]
if opt("--to"): rng += ["-to", opt("--to")]
subprocess.run(["ffmpeg", "-v", "error", "-y", *rng, "-i", cam, "-vf", "fps=1,scale=1080:1920", "-q:v", "3", F + "/f_%04d.jpg"], check=True)
frames = sorted(glob.glob(F + "/*.jpg"))
bin_ = os.path.join(W, "face_boxes")
if not os.path.exists(bin_): subprocess.run(["swiftc", "-O", os.path.join(K, "face_boxes.swift"), "-o", bin_], check=True)
out = subprocess.run([bin_, *frames], capture_output=True, text=True).stdout.strip().splitlines()
faces = []
for line in out:
    parts = line.rsplit(" ", 4)
    if len(parts) == 5: faces.append((parts[0], *[float(x) for x in parts[1:]]))
if not faces: sys.exit("no face found in any frame - check the crop")
# Vision's face box stops near the chin; add 6% of the face height so the whole chin is protected.
worst = max(faces, key=lambda f: f[2] + f[4] * 1.06); chin = worst[2] + worst[4] * 1.06; head_top = min(f[2] - f[4] * 0.35 for f in faces)
options = []
def add(key, name, scale, top):
    bottom = top + TH * scale; clear = top - NEED - chin
    options.append(dict(key=key, name=name, scale=scale, top=round(top), bottom=round(bottom), clears_face=clear >= 0, margin=round(clear),
                        below_safe=max(0, round(bottom - SAFE_B))))
add("A", "Full size, inside the safe zone", 1.0, SAFE_B - TH)
add("B", "Full size, lower (into the bottom zone)", 1.0, min(LOW - TH, max(SAFE_B - TH, chin + NEED)))
add("C90", "10% smaller, at the bottom limit", 0.9, LOW - TH * 0.9)
add("C80", "20% smaller, at the bottom limit", 0.8, LOW - TH * 0.8)
rec = next((o["key"] for o in options if o["clears_face"]), None)
choice = opt("--choose", rec or "C80"); chosen = next(o for o in options if o["key"] == choice)
warn = []
if rec is None: warn.append("NO option clears the face: the presenter is too large in frame. Re-crop wider / lower the crop so the chin sits higher, or accept C80 touching the neck.")
elif rec != "A": warn.append(f"The table does not fit inside the safe zone without covering the face (chin reaches y {chin:.0f}). Recommended: {rec} - {next(o['name'] for o in options if o['key'] == rec)}.")
if chosen["below_safe"]: warn.append(f"Option {choice} puts the bottom {chosen['below_safe']} px of the table under Instagram's caption / buttons area (below y {SAFE_B}). Lower tiers (E, F) may be partly hidden in the feed.")
if head_top < 286 + 70: warn.append(f"The top of the head reaches y {head_top:.0f}: the title at y 286 may touch the hair. Move it (plan.json title_y) or re-crop.")
json.dump(dict(scale=chosen["scale"], top=chosen["top"], choice=choice, recommended=rec, chin_y=round(chin), worst_frame=os.path.basename(worst[0]),
               options=options, warnings=warn), open(os.path.join(P, "layout.json"), "w"), indent=1)
# ---- picture: each option drawn on the worst frame
def font(sz):
    for f in ("/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(f): return ImageFont.truetype(f, sz)
    return ImageFont.load_default()
COL = ["#FF7F7E", "#FFBF7F", "#FFFF7F", "#7FFF7F", "#7FBFFF", "#807FFF", "#FF7FFE"]; tiles = []
for o in options:
    im = Image.open(worst[0]).convert("RGB"); d = ImageDraw.Draw(im, "RGBA"); s = o["scale"]; x0 = 540 - TW * s / 2; y0 = o["top"]
    d.rectangle([0, 0, 1080, SAFE_T], fill=(255, 0, 0, 46)); d.rectangle([0, SAFE_B, 1080, 1920], fill=(255, 0, 0, 46))
    for y in (SAFE_T, SAFE_B): d.line([0, y, 1080, y], fill=(255, 80, 80, 255), width=4)
    d.rectangle([x0 - 6, y0 - 6, x0 + TW * s + 6, y0 + TH * s + 6], fill=(0, 0, 0, 255))
    for i, c in enumerate(COL):
        ry = y0 + i * 72 * s; d.rectangle([x0, ry, x0 + TW * s, ry + 68 * s], fill=(27, 26, 29, 255)); d.rectangle([x0, ry, x0 + 72 * s, ry + 68 * s], fill=c)
        d.text((x0 + 36 * s, ry + 34 * s), "SABCDEF"[i], font=font(int(26 * s)), fill="#141414", anchor="mm")
    if CAPS_ON: d.text((540, y0 - 78 + 28), "caption line goes here", font=font(44), fill="white", anchor="mm", stroke_width=3, stroke_fill="black")
    fx, fy, fw, fh = worst[1:]; d.rectangle([fx, fy, fx + fw, fy + fh * 1.06], outline=(60, 255, 120, 255), width=5)
    ok = o["clears_face"]; tag = ("RECOMMENDED  " if o["key"] == rec else "") + ("CHOSEN  " if o["key"] == choice and choice != rec else "")
    d.rectangle([0, 0, 1080, 200], fill=(0, 0, 0, 215))
    d.text((40, 24), f"{o['key']}  {o['name']}", font=font(46), fill="white")
    d.text((40, 84), ("clears the face" if ok else "COVERS THE FACE / CAPTION") + (f"   |   {o['below_safe']} px below the safe zone" if o["below_safe"] else "   |   inside the safe zone"),
           font=font(36), fill="#7CFFA0" if ok else "#FF7B6B")
    if tag: d.text((40, 136), tag.strip(), font=font(40), fill="@@ACCENT@@")
    tiles.append(im.resize((540, 960)))
sheet = Image.new("RGB", (540 * 4 + 30, 960), "#111")
for i, t in enumerate(tiles): sheet.paste(t, (i * 550, 0))
sheet.save(os.path.join(W, "layout_options.jpg"), quality=88)
print(f"lowest chin y {chin:.0f} (frame {os.path.basename(worst[0])}); recommended {rec}; using {choice}: scale {chosen['scale']}, table y {chosen['top']}-{chosen['bottom']}")
for o in options: print(f"  {o['key']:<4} {'ok ' if o['clears_face'] else 'NO '} margin {o['margin']:>5} px, {o['below_safe']} px below safe zone")
for w_ in warn: print("WARNING:", w_)
print("show the user:", os.path.join(W, "layout_options.jpg"))
