#!/usr/bin/env python3
"""Step 6 - frame the speaker for both layouts and pre-crop the camera.
   06_crops.py <slug> --preview <t> [<t> ...]     stills of both layouts, nothing rendered (do this first)
   06_crops.py <slug> [--no-matte]               render cam_full.mp4, cam_panel.mp4 and the cut-out cam_panel_fg.webm

Reads <work>/layout.json, which you write after looking at frames.py stills:
  {"face": {"cx": 1980, "top": 520, "chin": 1010},     SOURCE pixels: centre of the face, top of the head (hair/hat), chin
   "popout": true,            (default from setup) head and raised hands may rise above the panel's top edge (needs the matte)
   "full_scale": null,        optional: force the close-up scale (output px per source px)
   "panel_scale": null,       optional: force the panel scale
   "full_dx": 0, "panel_dx": 0, "panel_dy": 0}          optional nudges in OUTPUT pixels

Geometry (the style's defaults, on the 1080x1920 frame):
  close-up : top of head ~14% down, head (top to chin) ~42% of the frame height, caption just under the chin.
  panel    : x 70-1010, top edge y 1407, running off the bottom, top corners radius 36; the head ~270 px tall with its
             top ~65 px ABOVE the panel edge (popout) or 30 px inside it (no popout).
Writes <out>/hf-media/{cam_full.mp4 (1080x1920, audio), cam_panel.mp4, cam_panel_fg.webm, crops.json}."""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw
from common import work, load, save, grab, popout_default

W = work(sys.argv[1]); M = load(W, "meta.json"); L = load(W, "layout.json") or sys.exit(f"write {W}/layout.json first (see this script's header)")
SW, SH = M["w"], M["h"]; F = L["face"]; fh = F["chin"] - F["top"]; pop = L.get("popout", popout_default())
PN = {"x": 70, "y": 1407, "w": 940, "h": 513, "r": 36, "head": 150 if pop else 0}
MAXUP = 1.3      # never enlarge source pixels more than this (soft picture)


def clamp(v, lo, hi): return max(lo, min(hi, v))


# close-up: 9:16 window
fs = L.get("full_scale") or clamp(0.42 * 1920 / fh, max(1080 / SW, 1920 / SH), MAXUP)
fw, fhh = 1080 / fs, 1920 / fs
fx = clamp(F["cx"] - fw / 2 - L.get("full_dx", 0) / fs, 0, SW - fw); fy = clamp(F["top"] - 0.14 * fhh, 0, SH - fhh)
chin_out = (F["chin"] - fy) * fs; cap_full = round(clamp(chin_out + 150, 1000, 1330))
# panel: 940 x (513 + head) window
ph = PN["h"] + PN["head"]
ps = L.get("panel_scale") or clamp(270 / fh, max(PN["w"] / SW, ph / SH), MAXUP)
pw, phh = PN["w"] / ps, ph / ps
top_in = (PN["head"] - 65) if pop else 30
px = clamp(F["cx"] - pw / 2 - L.get("panel_dx", 0) / ps, 0, SW - pw); py = clamp(F["top"] - top_in / ps - L.get("panel_dy", 0) / ps, 0, SH - phh)
head_top_out = PN["y"] - PN["head"] + (F["top"] - py) * ps
cap_panel = round(min(1290, head_top_out - 52)) if pop else PN["y"] - 70
C = {"full": [round(v) // 2 * 2 for v in (fw, fhh, fx, fy)], "panel": [round(v) // 2 * 2 for v in (pw, phh, px, py)], "panel_px": [PN["w"], ph],
     "pn": PN, "popout": pop, "cap": {"panel_y": cap_panel, "full_y": cap_full, "size": 62}, "full_scale": round(fs, 3), "panel_scale": round(ps, 3)}
print(f"close-up: crop {C['full']} scale {fs:.2f} (chin lands at y {chin_out:.0f}, caption centre y {cap_full})")
print(f"panel   : crop {C['panel']} scale {ps:.2f} (top of head at y {head_top_out:.0f}, panel edge y {PN['y']}, caption centre y {cap_panel})")
if fs > 1.05: print(f"NOTE the close-up enlarges the source {fs:.2f}x: it will be a little softer than the panel. A larger/closer source avoids this.")
if 0.42 * 1920 / fh > MAXUP: print("NOTE the speaker is small in the source: the close-up is looser than the default so the picture stays sharp.")


def layout(t):
    p = tempfile.mktemp(suffix=".jpg"); grab(M.get("cut") or M["src"], t, p); im = Image.open(p).convert("RGB"); os.remove(p)
    a = im.crop((C["full"][2], C["full"][3], C["full"][2] + C["full"][0], C["full"][3] + C["full"][1])).resize((1080, 1920))
    b = Image.new("RGB", (1080, 1920)); pc = im.crop((C["panel"][2], C["panel"][3], C["panel"][2] + C["panel"][0], C["panel"][3] + C["panel"][1])).resize((PN["w"], ph))
    if PN["head"]:                                   # head-room strip: darkened here; in the render only the cut-out shows in it
        strip = pc.crop((0, 0, PN["w"], PN["head"])).point(lambda v: v * 0.45); b.paste(strip, (PN["x"], PN["y"] - PN["head"]))
    mask = Image.new("L", (PN["w"], PN["h"] + PN["r"]), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, PN["w"], PN["h"] + PN["r"] * 2), PN["r"], fill=255)
    b.paste(pc.crop((0, PN["head"], PN["w"], ph)), (PN["x"], PN["y"]), mask.crop((0, 0, PN["w"], PN["h"])))
    for img, y in ((a, cap_full), (b, cap_panel)):
        d = ImageDraw.Draw(img); d.line([(200, y), (880, y)], fill=(@@ACCENT_RGB@@), width=4); d.text((210, y - 34), "caption centre line", fill=(@@ACCENT_RGB@@))
    out = Image.new("RGB", (2200, 1920), (40, 40, 40)); out.paste(a, (0, 0)); out.paste(b, (1120, 0)); return out.resize((1100, 960))


if "--preview" in sys.argv:
    os.makedirs(f"{W}/frames", exist_ok=True)
    for t in map(float, sys.argv[sys.argv.index("--preview") + 1:]):
        o = f"{W}/frames/layout_{t:07.2f}.jpg"; layout(t).save(o, quality=88); print(o)
    print("Left = close-up, right = panel layout (the darker strip above the panel is where only the cut-out will show). Check: caption line under the chin on the left; "
          "on the right the whole head is in view and the caption line clears it. Check several moments, including one where the speaker leans or gestures.")
    sys.exit()

cut = M.get("cut") or sys.exit("render the cut first (05_render_cut.py)")
O = f"{M['out']}/hf-media"; os.makedirs(O, exist_ok=True); enc = ["-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", "-g", "24", "-keyint_min", "24", "-movflags", "+faststart"]      # a keyframe every second: the renderer seeks these files
w, h, x, y = C["full"]; subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", cut, "-vf", f"crop={w}:{h}:{x}:{y},scale=1080:1920:flags=lanczos,setsar=1", *enc, "-c:a", "aac", "-b:a", "320k", f"{O}/cam_full.mp4"], check=True)
w, h, x, y = C["panel"]; subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", cut, "-an", "-vf", f"crop={w}:{h}:{x}:{y},scale={PN['w']}:{ph // 2 * 2}:flags=lanczos,setsar=1", *enc, f"{O}/cam_panel.mp4"], check=True)
if pop and "--no-matte" not in sys.argv:            # the speaker's cut-out for the pop-out above the panel edge (~0.1 s per frame)
    r = subprocess.run(["npx", "hyperframes", "remove-background", f"{O}/cam_panel.mp4", "-o", f"{O}/cam_panel_fg.webm", "--quality", "best"], capture_output=True, text=True)
    if r.returncode: print("MATTE FAILED (set \"popout\": false in layout.json, or fix and re-run):\n", (r.stdout + r.stderr)[-600:])
json.dump(C, open(f"{O}/crops.json", "w"), indent=1); save(W, "crops.json", C)
print("wrote", O, os.listdir(O))
