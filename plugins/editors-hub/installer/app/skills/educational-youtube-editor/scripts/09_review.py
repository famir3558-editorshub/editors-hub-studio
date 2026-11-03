#!/usr/bin/env python3
"""Step 9 - review the RENDERED file, not the previews.   09_review.py <slug> ["<rendered file>"] [--intro 45]
Writes into <project>/review/:
  intro-*.jpg    one frame per second of the intro (does it look premium from the first frame? is the promise on screen?)
  scenes-*.jpg   three frames of every scene from the finished file (in / middle / out), labelled with state and component
  rhythm.jpg     the whole video as one strip, a frame every ~10 s (the waves: where it is dense, where it breathes)
  joins.jpg      a frame either side of every chunk join (must look continuous)
  crops-*.jpg    every image used, with the part that is SHOWN boxed in green (red = a face is cut) and each detected face in yellow.
                 Detection misses faces that are small, turned away or covered: look at every crop yourself.
Then prints the audit and the final quality checklist to answer. READ every sheet."""
import json, os, sys
from PIL import Image
from common import SKILL, grab, sheet, pj
slug = sys.argv[1]; PJ = pj(slug); P = json.load(open(f"{PJ}/project.json")); A = json.load(open(f"{PJ}/audit.json")); R = json.load(open(f"{PJ}/render.json"))
arg = [a for a in sys.argv[2:] if not a.startswith("--")]; f = arg[0] if arg else f"{PJ}/renders/draft.mp4"; os.path.exists(f) or sys.exit(f"not found: {f}")
intro = int(sys.argv[sys.argv.index("--intro") + 1]) if "--intro" in sys.argv else 45; D = P["dur"]; rv = f"{PJ}/review"; os.makedirs(rv, exist_ok=True); tmp = f"{rv}/_t.jpg"
for old in os.listdir(rv):
    if old.startswith(("intro-", "scenes-", "rhythm", "joins", "crops")): os.remove(f"{rv}/{old}")


def tile(t, lab):
    grab(f, min(max(0, t), D - 0.1), tmp, (960, 540)); return Image.open(tmp).convert("RGB"), lab


def sheets(tiles, name, cols, w, per):
    for k in range(0, len(tiles), per):
        p = f"{rv}/{name}{'-%d' % (k // per + 1) if len(tiles) > per else ''}.jpg"; sheet(tiles[k:k + per], p, cols, w); print("sheet", p)


sheets([tile(t + 0.5, f"{t + 0.5:.1f}s") for t in range(0, min(intro, int(D)))], "intro", 5, 384, 30)
sc = []
for s in A["scenes"]:
    d = s["b"] - s["a"]; sc += [tile(s["a"] + min(0.9, d * 0.3), f"{s['id']} in @{s['a']:.0f}s"), tile(s["a"] + d * 0.6, f"{s['kind']}/{s['comp']}/{s['variant']}"), tile(s["b"] - 0.45, f"{s['why']} score {s['score']}")]
sheets(sc, "scenes", 3, 640, 18)
step = max(5, D / 96); sheets([tile(k * step, f"{k * step / 60:.1f}m") for k in range(int(D / step))], "rhythm", 12, 160, 144)
cr = []
for u in A.get("crops", []):
    try:
        from PIL import ImageDraw
        im = Image.open(f"{PJ}/{u['src']}").convert("RGB"); im.thumbnail((900, 900)); d = ImageDraw.Draw(im); iw, ih = im.size
        F = json.load(open(f"{PJ}/faces.json")).get(u["src"], {}).get("faces", []); x0, y0, vw, vh = u["window"]
        d.rectangle([x0 * iw, y0 * ih, (x0 + vw) * iw - 1, (y0 + vh) * ih - 1], outline=(0, 230, 90) if u["ok"] else (255, 40, 40), width=6)
        for a_, b_, c_, d_ in F: d.rectangle([a_ * iw, b_ * ih, (a_ + c_) * iw, (b_ + d_) * ih], outline=(255, 210, 0), width=3)
        cr.append((im.resize((480, 360)) if False else im, f"{u['scene']}: {u['mode']}{'' if u['ok'] else '  FACE CUT'} ({u['faces']} face{'s' if u['faces'] != 1 else ''})"))
    except Exception as e: print("crop sheet skipped for", u["src"], e)
if cr:
    W_ = 420; cr = [(im.resize((W_, int(im.height * W_ / im.width))).crop((0, 0, W_, 420)) if im.height * W_ / im.width > 420 else im, lab) for im, lab in cr]
    sheets(cr, "crops", 4, 420, 16)
bad = [u for u in A.get("crops", []) if not u["ok"]]
js = [x for a0, a1 in R["chunks"][:-1] for x in (tile(a1 - 0.06, f"before join {a1:.2f}"), tile(a1 + 0.06, f"after join {a1:.2f}"))]
if js: sheets(js, "joins", 4, 480, 24)
os.path.exists(tmp) and os.remove(tmp)
print("\nAUDIT ", A["summary"]); [print("  ! " + x) for x in A["warnings"]]
print(f"CROPS  {len(A.get('crops', []))} image uses, {sum(1 for u in A.get('crops', []) if u['faces'])} with people, {len(bad)} cutting a face" + ("".join(f"\n  ! {u['scene']}: {u['src']}" for u in bad)))
print("\n" + open(f"{SKILL}/references/quality-check.md").read().split("## The checklist")[1].split("\n## ")[0].strip())
