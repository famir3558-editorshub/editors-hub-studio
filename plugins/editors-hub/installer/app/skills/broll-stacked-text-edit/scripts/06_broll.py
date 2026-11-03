#!/usr/bin/env python3
"""Step 6 - the B-roll library.
  06_broll.py ["<folder>" ...]        catalogue every clip in the folders (default: the creator's standing B-roll folders,
                                      the `broll_dirs` answer from setup). Only new or changed files are processed.
  06_broll.py --todo                  list the clips that have no notes yet (sheet path for each)
  06_broll.py --note <id> "<notes>"   save the notes for one clip
  06_broll.py --find <word> [...]     search the notes

The library lives in <work root>/broll-library (library.json + one labelled contact sheet per clip) and is shared by
every edit, so each clip is only reviewed once. LOOK AT THE SHEET of every clip before writing its notes: what happens,
where it is, how the speaker is framed, the usable seconds, and what idea it could illustrate. A clip with no notes has not been
reviewed and must not be skipped when choosing B-roll."""
import os, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from common import probe, save, grab, sheet, library, LIB, broll_dirs, VIDEO_EXT
os.makedirs(f"{LIB}/sheets", exist_ok=True); lib = library(); a = sys.argv[1:]
if a[:1] == ["--todo"]:
    todo = [c for c in lib if not c["notes"]]
    print("\n".join(f"{c['id']:4d}  {c['dur']:6.1f}s  {c['clip']}  ->  {c['sheet']}" for c in todo)); print(f"{len(todo)} of {len(lib)} clips still need notes"); sys.exit()
if a[:1] == ["--note"]:
    c = next(c for c in lib if c["id"] == int(a[1])); c["notes"] = a[2]; save(LIB, "library.json", lib); print("saved", c["clip"]); sys.exit()
if a[:1] == ["--find"]:
    for c in lib:
        if all(w.lower() in (c["notes"] + " " + c["clip"]).lower() for w in a[1:]):
            print(f"{c['id']:4d}  {c['dur']:6.1f}s  {c['w']}x{c['h']}  {c['clip']}\n      {c['notes']}")
    sys.exit()
folders = [os.path.abspath(os.path.expanduser(f)) for f in a] or broll_dirs()
folders or sys.exit("no B-roll folder: pass one on the command line, or save broll_dirs (python3 setup/apply_profile.py --set-skill 'broll_dirs=[\"/path/to/folder\"]')")
for f in folders:
    os.path.isdir(f) or sys.exit(f"folder not found (is the footage drive connected?): {f}")
known = {c["file"]: c for c in lib}; nid = max([c["id"] for c in lib], default=0); tmp = tempfile.mkdtemp(); new = 0
files = sorted((os.path.join(r, f), root) for root in folders for r, _, fs in os.walk(root) for f in fs
               if f.lower().endswith(VIDEO_EXT) and not f.startswith("."))
for n, (f, root) in enumerate(files, 1):
    size = os.path.getsize(f); old = known.get(f)
    if old and old.get("size") == size and os.path.exists(old["sheet"]):
        continue
    try:
        P = probe(f)
    except Exception as e:
        print(f"SKIP {f}: {str(e)[:80]}"); continue
    k = max(4, min(24 if P["dur"] > 60 else 18, round(P["dur"]))); ts = [P["dur"] * (i + 0.5) / k for i in range(k)]
    def one(it):
        i, t = it; p = f"{tmp}/{n}_{i}.jpg"
        try:
            grab(f, t, p, (300, 300)); return Image.open(p).convert("RGB"), f"{t:.1f}s"
        except Exception:
            return None
    with ThreadPoolExecutor(4) as ex:
        tiles = [x for x in ex.map(one, enumerate(ts)) if x]
    if not tiles:
        print(f"SKIP {f}: no frames"); continue
    cid = old["id"] if old else (nid := nid + 1); sh = f"{LIB}/sheets/{cid:04d}.jpg"
    sheet(tiles, sh, 6 if P["w"] >= P["h"] else 8, tiles[0][0].width)
    [os.remove(f"{tmp}/{n}_{i}.jpg") for i in range(k) if os.path.exists(f"{tmp}/{n}_{i}.jpg")]
    e = {"id": cid, "clip": os.path.join(os.path.basename(root), os.path.relpath(f, root)), "file": f, "size": size, "dur": round(P["dur"], 2),
         "w": P["w"], "h": P["h"], "fps": P["fps"], "hdr": "arib" in P["transfer"] or "smpte2084" in P["transfer"], "sheet": sh,
         "notes": old["notes"] if old else ""}
    if old:
        lib[lib.index(old)] = e
    else:
        lib.append(e)
    known[f] = e; new += 1
    print(f"{cid:4d}  {e['clip']}  {e['dur']:.1f}s  {e['w']}x{e['h']} {e['fps']}{' HDR' if e['hdr'] else ''}", flush=True)
    if new % 10 == 0:
        save(LIB, "library.json", lib)
save(LIB, "library.json", lib)
print(f"\n{len(files)} clips in the folders, {new} catalogued now, {sum(1 for c in lib if not c['notes'])} without notes (06_broll.py --todo).")
