#!/usr/bin/env python3
"""Step 6 - frame the presenter for the lower half of the frame and cut them out of their background.
   06_cutout.py <slug> --preview <t> [<t> ...]     stills of the framing on the black + accent backdrop, nothing rendered (do this first)
   06_cutout.py <slug> [--no-matte]               render cam.mp4 (their crop, carries the sound) and the cut-out cam_fg.webm

Reads <work>/layout.json, which you write after looking at frames.py stills:
  {"face": {"cx": 1980, "top": 520, "chin": 1010},   SOURCE pixels: centre of the face, top of the head (hair/hat), chin
   "head_y": 1000,     optional: where the top of the head sits in the 1920 frame (default: the "head_y" setup answer, 1000 = they fill the lower ~48%)
   "head": 320,        optional: height of the head (top to chin) in output pixels (default: the "head_px" setup answer, 320, about 17% of the frame)
   "dx": 0,            optional: nudge the presenter left/right in OUTPUT pixels
   "fade": 0}          optional: fade the bottom N px of the cut-out into the backdrop (hides a desk edge the cut-out kept)

Geometry (1080x1920): top of the head 45-50% down the frame, head about 16-18% of the frame
height, shoulders run off the bottom edge, about 300 px of clear room kept above the head for raised hands.
If the source ends before the bottom of the frame (the presenter is cut off by the edge of the shot) they are enlarged until it
reaches, up to a head of 430 px; past that the last 140 px of the cut-out fade into the backdrop.
Writes <out>/hf-media/{cam.mp4, cam_fg.webm, cutout.json}."""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter
from common import work, load, save, grab, brand, num

W = work(sys.argv[1]); M = load(W, "meta.json"); L = load(W, "layout.json") or sys.exit(f"write {W}/layout.json first (see this script's header)")
SW, SH = M["w"], M["h"]; F = L["face"]; fh = F["chin"] - F["top"]
HEAD_Y = int(L.get("head_y", num("head_y", 1000))); HEAD = int(L.get("head", num("head_px", 320))); ROOM = 300; MAXUP = 1.3; MAXHEAD = 430

s = HEAD / fh
need = (1920 - HEAD_Y) / (SH - F["top"])                 # scale at which the source's bottom edge reaches the frame's
fade = 0
if need > s:
    s = min(need, MAXHEAD / fh)
    if s < need - 1e-6: fade = 140
s = min(s, MAXUP); fade = L.get("fade", fade)
head_in = round(min(ROOM, F["top"] * s))                 # clear room above the head inside the cut-out
cw = min(SW, 1080 / s); out_w = round(cw * s) // 2 * 2
cx0 = max(0, min(SW - cw, F["cx"] - cw / 2 - L.get("dx", 0) / s)); cy0 = F["top"] - head_in / s
ch = min(SH - cy0, (1920 - (HEAD_Y - head_in)) / s); out_h = round(ch * s) // 2 * 2
C = {"crop": [round(v) // 2 * 2 for v in (cw, ch, cx0, cy0)], "scale": round(s, 4),
     "me": {"x": (1080 - out_w) // 2, "y": HEAD_Y - head_in, "w": out_w, "h": out_h, "head_y": HEAD_Y, "head_in": head_in, "head": round(fh * s), "fade": fade},
     "cap": {"y": HEAD_Y - 46, "size": int(num("caption_size", 54))}}
m = C["me"]
print(f"cut-out: crop {C['crop']} scale {s:.3f} -> {out_w}x{out_h} at ({m['x']}, {m['y']}); head {m['head']} px tall with its top at y {HEAD_Y}; "
      f"bottom edge at y {m['y'] + out_h}{' (fades into the backdrop)' if fade else ''}; caption centre y {C['cap']['y']}")
if s > 1.05: print(f"NOTE the source is enlarged {s:.2f}x: they will be a little soft. A closer / larger source avoids this.")
if out_w < 1080: print(f"NOTE the source is only {out_w} px wide at this scale: the shoulders stop short of the frame edges (fine for a cut-out).")
if m["y"] + out_h < 1918 and not fade: print("NOTE the cut-out stops above the bottom of the frame: raise \"head\" or \"head_y\" in layout.json.")


def preview(t):
    p = tempfile.mktemp(suffix=".jpg"); grab(M.get("cut") or M["src"], t, p); im = Image.open(p).convert("RGB"); os.remove(p)
    x, y = C["crop"][2], C["crop"][3]; pc = im.crop((x, y, x + C["crop"][0], y + C["crop"][1])).resize((out_w, out_h))
    o = brand(W)["accent"]; rgb = tuple(int(o[i:i + 2], 16) for i in (1, 3, 5))
    bg = Image.new("RGB", (1080, 1920), (8, 7, 6)); g = Image.new("L", (1080, 1920), 0)
    ImageDraw.Draw(g).ellipse((-600, 1150, 1680, 2650), fill=150); g = g.filter(ImageFilter.GaussianBlur(170))
    bg.paste(Image.new("RGB", (1080, 1920), rgb), (0, 0), g)
    left = bg.copy(); left.paste(pc.point(lambda v: v * 0.55), (m["x"], m["y"]))        # the whole crop, dimmed: only the presenter will remain after the cut-out
    d = ImageDraw.Draw(left)
    d.rectangle((65, 200, 1015, 1060), outline=(255, 255, 255), width=2); d.text((80, 210), "evidence wall (its lower part tucks behind the head)", fill=(255, 255, 255))
    d.line([(0, 270), (1080, 270)], fill=(120, 120, 120), width=2); d.text((80, 240), "nothing to be read above this line", fill=(160, 160, 160))
    d.line([(200, C["cap"]["y"]), (880, C["cap"]["y"])], fill=rgb, width=4); d.text((210, C["cap"]["y"] - 30), "caption centre line", fill=rgb)
    d.line([(0, HEAD_Y), (1080, HEAD_Y)], fill=(90, 200, 120), width=2); d.text((80, HEAD_Y + 6), "top of the head", fill=(90, 200, 120))
    return left.resize((540, 960))


if "--preview" in sys.argv:
    os.makedirs(f"{W}/frames", exist_ok=True)
    for t in map(float, sys.argv[sys.argv.index("--preview") + 1:]):
        o = f"{W}/frames/cutout_{t:07.2f}.jpg"; preview(t).save(o, quality=88); print(o)
    print("Check several moments, including one where they lean or raise a hand: the green line touches the top of the head, the whole head and both "
          "shoulders are inside the crop, a raised hand is not chopped by the top of the crop, and the presenter is centred. Nudge with head_y / head / dx.")
    sys.exit()

cut = M.get("cut") or sys.exit("render the cut first (05_render_cut.py)")
O = f"{M['out']}/hf-media"; os.makedirs(O, exist_ok=True)
enc = ["-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", "-g", "24", "-keyint_min", "24", "-movflags", "+faststart"]      # a keyframe every second: the renderer seeks these files
w, h, x, y = C["crop"]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", cut, "-vf", f"crop={w}:{h}:{x}:{y},scale={out_w}:{out_h}:flags=lanczos,setsar=1", *enc, "-c:a", "aac", "-b:a", "320k", f"{O}/cam.mp4"], check=True)
if "--no-matte" not in sys.argv:                          # about 0.1 s per frame
    r = subprocess.run(["npx", "hyperframes", "remove-background", f"{O}/cam.mp4", "-o", f"{O}/cam_fg.webm", "--quality", "best"], capture_output=True, text=True)
    if r.returncode: print("CUT-OUT FAILED (fix and re-run; without cam_fg.webm the build shows them in a rounded panel with their real background):\n", (r.stdout + r.stderr)[-600:])
json.dump(C, open(f"{O}/cutout.json", "w"), indent=1); save(W, "cutout.json", C)
print("wrote", O, sorted(os.listdir(O)))
print("Next: check the cut-out edge BEFORE building. Three full-size stills (hair, a raised hand, a fast gesture):\n"
      f"  ffmpeg -v error -y -ss <t> -c:v libvpx-vp9 -i \"{O}/cam_fg.webm\" -frames:v 1 -vf \"format=rgba\" <still>.png")
