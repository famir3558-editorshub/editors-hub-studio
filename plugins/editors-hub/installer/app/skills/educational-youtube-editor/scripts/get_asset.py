#!/usr/bin/env python3
"""Bring a real-world asset into the project and record where it came from.
   get_asset.py <slug> file    "<path on the computer / drives>"     --as client-award --tier 1 --for "the client's award photo"
   get_asset.py <slug> url     "<direct image url>"                --as apple-store  --tier 3 --for "Apple Store, Regent St"
   get_asset.py <slug> site    "<page url>" [--tall 2400] [--width 1440] [--dark]   --as stripe-home --tier 2 --for "stripe.com homepage"
   get_asset.py <slug> ytthumb "<youtube url or video id>"         --as channel-1    --tier 1 --for "the thumbnail that is mentioned"
   get_asset.py <slug> list
Files land in <project>/assets/media/ and every one is logged in <project>/assets.json (file, source, tier, what it shows).
TIER = how real it is (references/asset-retrieval.md): 1 exact real-world example · 2 relevant screenshot · 3 authentic photograph ·
4 high-quality illustration · 5 custom graphic · 6 stock (only when nothing specific exists).
`site` uses headless Chrome: a public page, no login. For a logged-in page or a single post, screenshot it in the browser
tool and bring the saved file in with `file`. Open every fetched image with Read before using it."""
import json, os, re, shutil, subprocess, sys, urllib.request
from common import pj
slug, kind = sys.argv[1], sys.argv[2]; PJ = pj(slug); led = f"{PJ}/assets.json"
L = json.load(open(led)) if os.path.exists(led) else []
if kind == "list":
    for a in L: print(f"tier {a['tier']}  {a['file']:44s} {a['for']}   <- {a['source']}")
    sys.exit()
src = sys.argv[3]; opt = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
name = opt("--as") or sys.exit("--as <name> is required"); tier = int(opt("--tier", 0)) or sys.exit("--tier 1-6 is required"); what = opt("--for", "")
os.makedirs(f"{PJ}/assets/media", exist_ok=True); UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"}


def fetch(url, dst):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r, open(dst, "wb") as f: shutil.copyfileobj(r, f)


if kind == "file":
    src = os.path.expanduser(src); os.path.exists(src) or sys.exit(f"not found: {src}"); dst = f"{PJ}/assets/media/{name}{os.path.splitext(src)[1].lower()}"
    if os.path.getsize(src) > 60e6: os.path.lexists(dst) and os.remove(dst); os.symlink(src, dst)          # big clips stay where they are
    else: shutil.copy(src, dst)
elif kind == "url":
    ext = (re.search(r"\.(jpe?g|png|webp|gif|mp4)(?:\?|$)", src, re.I) or [None, "jpg"])[1].lower(); dst = f"{PJ}/assets/media/{name}.{ext}"; fetch(src, dst)
elif kind == "ytthumb":
    vid = (re.search(r"(?:v=|youtu\.be/|shorts/|vi/)([\w-]{11})", src) or re.match(r"([\w-]{11})$", src) or sys.exit("no video id found")).group(1); dst = f"{PJ}/assets/media/{name}.jpg"
    for q in ("maxresdefault", "sddefault", "hqdefault"):
        try:
            fetch(f"https://i.ytimg.com/vi/{vid}/{q}.jpg", dst)
            if os.path.getsize(dst) > 9000: break
        except Exception: pass
    src = f"https://www.youtube.com/watch?v={vid}"
elif kind == "site":
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"; os.path.exists(chrome) or sys.exit("Google Chrome not found")
    wd, tall = int(opt("--width", 1440)), int(opt("--tall", 900)); dst = f"{PJ}/assets/media/{name}.png"
    cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={wd},{tall}", "--force-device-scale-factor=1.5", "--virtual-time-budget=9000",
           f"--user-agent={UA['User-Agent']}", f"--screenshot={dst}", src]
    if "--dark" in sys.argv: cmd.insert(1, "--force-dark-mode")
    subprocess.run(cmd, capture_output=True, timeout=120)
else: sys.exit(__doc__)
os.path.exists(dst) and os.path.getsize(dst) > 2000 or sys.exit(f"nothing usable was saved for {src}. Try the browser tool, another source, or the next tier down.")
dim = ""
try:
    from PIL import Image; dim = "x".join(map(str, Image.open(dst).size))
except Exception: pass
rel = os.path.relpath(dst, PJ); L = [a for a in L if a["file"] != rel] + [{"file": rel, "source": src, "tier": tier, "for": what, "kind": kind}]
json.dump(L, open(led, "w"), indent=1)
print(f"saved {rel} {dim} (tier {tier}). LOOK at it with Read before using it: a cookie wall, a blank page or the wrong person is worse than no image.")
