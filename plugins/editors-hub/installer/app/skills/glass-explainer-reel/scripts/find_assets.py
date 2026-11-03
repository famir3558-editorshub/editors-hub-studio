#!/usr/bin/env python3
"""Find a real asset on the creator's computer and drives BEFORE asking them or drawing a stand-in.
   find_assets.py <term> [<term> ...] [--video] [--image]        e.g.  find_assets.py guest name   |   find_assets.py client testimonial --image
Searches, in this order: this skill's folder (assets/), the creator's proof folder, the other folders they listed at setup,
earlier reel projects (<projects folder>/*/assets), their Desktop / Downloads / Pictures, then Spotlight (file names)
across the whole machine and every mounted drive. A file matches when EVERY term is in its path (case-insensitive).
Prints newest first with size and, for media, dimensions. Open the candidates with Read before choosing one.
If nothing suitable turns up: search Google Images and the person's public profile / page in the browser, save the
file into <project>/assets/media/, and record its URL with E.asset(path, url)."""
import glob, os, subprocess, sys
from common import PROJECTS_ROOT
IMG = (".jpg", ".jpeg", ".png", ".heic", ".webp", ".gif"); VID = (".mp4", ".mov", ".m4v", ".webm")
terms = [a.lower() for a in sys.argv[1:] if not a.startswith("--")]; terms or sys.exit(__doc__)
ext = (VID if "--video" in sys.argv else ()) + (IMG if "--image" in sys.argv else ()) or IMG + VID + (".pdf",)
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); H = os.path.expanduser("~")
# the proof folder and any other asset folders the creator named at setup (comma-separated, filled in by setup/apply_profile.py)
CREATOR_DIRS = [os.path.expanduser(d.strip()) for d in r"@@PROOF_DIR@@,@@ASSET_DIRS@@".split(",") if d.strip() and d.strip().lower() not in ("none", "none yet", "not set")]
ROOTS = [f"{SKILL}/assets", *CREATOR_DIRS, f"{PROJECTS_ROOT}/*/assets", f"{H}/Desktop", f"{H}/Downloads", f"{H}/Pictures"]
hits, seen = [], set()


def add(p, where):
    rp = os.path.realpath(p)
    if rp in seen or not p.lower().endswith(ext) or os.path.basename(p).startswith("._"): return
    if all(t in p.lower() for t in terms): seen.add(rp); hits.append((os.path.getmtime(p), p, where))


for r in ROOTS:
    for root in glob.glob(r):
        depth = root.count(os.sep)
        for d, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = [x for x in dirs if not x.startswith(".") and x not in ("node_modules", "renders", "snapshots", ".transcode-cache")]
            if d.count(os.sep) - depth > 6: dirs[:] = []
            for f in files: add(os.path.join(d, f), "known folder")
try:                                                    # Spotlight: file-name match on every term, anywhere (including mounted drives)
    q = " && ".join(f'kMDItemFSName == "*{t}*"cd' for t in terms)
    for p in subprocess.run(["mdfind", q], capture_output=True, text=True, timeout=40).stdout.splitlines():
        if os.path.exists(p) and "/Library/" not in p: add(p, "spotlight")
except Exception as e: print("spotlight search skipped:", e)
if not hits: sys.exit(f"nothing on disk for {terms}. Next: Google Images and the public profile / page (browser), then a simple mock-up as the last resort.")
for m, p, where in sorted(hits, reverse=True)[:40]:
    dim = ""
    try:
        if p.lower().endswith(VID): dim = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration", "-of", "csv=p=0", p], timeout=8).decode().replace("\n", " ").strip()
        elif p.lower().endswith(IMG[:3]):
            from PIL import Image; dim = "x".join(map(str, Image.open(p).size))
    except Exception: pass
    print(f"{os.path.getsize(p) / 1e6:8.1f} MB  {dim:22s} {p}   [{where}]")
print(f"\n{len(hits)} match(es), newest first (40 shown). Copy the chosen file into <project>/assets/media/ and record it: E.asset(\"assets/media/<file>\", \"<the path above>\").")
