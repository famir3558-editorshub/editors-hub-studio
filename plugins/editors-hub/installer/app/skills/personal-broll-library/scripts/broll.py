#!/usr/bin/env python3
"""
broll.py - Personal B-Roll Library CLI (part of the personal-broll-library skill)

Builds and queries a semantic index of personal B-roll footage. The footage is
NEVER modified: this tool only reads media files (ffprobe / ffmpeg frame grabs)
and writes to its own library folder.

Requires: Python 3.9+, ffmpeg + ffprobe on PATH. Pillow is optional (labelled
contact sheets); without it, sheets are built by ffmpeg without timestamp labels.

Every command prints JSON to stdout so Claude can read the result.

Commands
  init                         create the library folder
  scan <folder>                find new / changed / moved / duplicate / missing clips
  status                       counts, roots, what still needs analysing
  extract [--id ID|--pending]  grab frames + contact sheets + analysis template
  ingest <file|--dir DIR>      validate a filled analysis JSON and store it
  show <id>                    full record for one clip
  search "<query>"             ranked candidates (Claude reranks semantically)
  dump                         compact listing of every analysed clip
  transcript <file>            SRT/VTT/JSON/CSV/TXT -> timed segments JSON
  plan-check <plan.json>       validate a B-roll placement plan
  export <plan.json>           FCP7 XML (Premiere, Resolve) / Premiere ExtendScript / CSV sheet
  used <plan.json>             record that a plan's clips were used in a video
  roots | relink               manage footage folders (e.g. external drive moved)
  backup                       write the whole library to one JSON file
"""
import argparse
import csv
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

VERSION = "1.0.0"
SCHEMA_VERSION = 1
ANALYSIS_VERSION = 1  # bump if analysis-guide.md changes enough to warrant re-analysis

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".mkv", ".avi", ".mts", ".m2ts", ".mxf",
              ".webm", ".3gp", ".hevc", ".mpg", ".mpeg", ".wmv", ".dv"}
UNSUPPORTED_RAW = {".braw", ".r3d", ".ari", ".crm"}
CHUNK = 1 << 20
SKILL_DIR = Path(__file__).resolve().parent.parent


def _profile():
    """The creator profile written by this skill's setup (setup/apply_profile.py). Empty if setup has not run."""
    f = Path(os.environ.get("CREATOR_PROFILE_DIR", "~/.claude/creator-profile")).expanduser() / "profile.json"
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


PROFILE = _profile()
SKILL_ANSWERS = (PROFILE.get("skills") or {}).get(SKILL_DIR.name) or {}
# Library folder: $BROLL_LIBRARY, else the setup answer "library_dir", else ~/BrollLibrary.
DEFAULT_LIBRARY = (os.environ.get("BROLL_LIBRARY") or str(SKILL_ANSWERS.get("library_dir") or "").strip()
                   or str(Path.home() / "BrollLibrary"))

SHOT_TYPES = ["extreme wide", "wide", "medium wide", "medium", "medium close-up", "close-up",
              "extreme close-up", "insert", "pov", "over-the-shoulder", "top-down", "screen recording"]
SPEAKING = ["none", "talking to camera", "talking off camera", "on a call", "background voices"]

STOP = set("""a an the of to and or for in on at with by from is are be been was were it its this that
these those as about into over under my me i im i'm you your we our some any all clips clip footage
broll b-roll b roll find show give do have got where which what when who how can could would should of
section sections part video videos shot shots me him his her hers them their something represent represents
representing work-for that's""".split())
# "b-roll of Sam working" should search for "working", not for the creator's own first name (from the profile).
STOP |= {w for w in re.findall(r"[a-z0-9']+", str(PROFILE.get("creator_name") or "").lower().split(" ")[0]) if w}


# --------------------------------------------------------------------------- utils
def now():
    return _dt.datetime.now().isoformat(timespec="seconds")


def out(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


def die(msg, **extra):
    out({"ok": False, "error": msg, **extra})
    sys.exit(1)


def run(cmd, timeout=None):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                          encoding="utf-8", errors="replace")


def need(*tools):
    missing = [t for t in tools if not shutil.which(t)]
    if missing:
        die(f"Missing tool(s): {', '.join(missing)}. On macOS install with: brew install ffmpeg")


def lib_paths(lib):
    root = Path(lib).expanduser().resolve()
    return {
        "root": root, "db": root / "library.db", "frames": root / "frames",
        "pending": root / "pending", "plans": root / "plans", "exports": root / "exports",
        "concepts": root / "concepts.json", "backups": root / "backups",
    }


DDL = """
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS roots(id INTEGER PRIMARY KEY, path TEXT UNIQUE, label TEXT, added_at TEXT, last_scan TEXT);
CREATE TABLE IF NOT EXISTS clips(
  id TEXT PRIMARY KEY,
  root_id INTEGER, rel_path TEXT, abs_path TEXT, filename TEXT,
  size INTEGER, mtime REAL, quick_hash TEXT,
  duration REAL, width INTEGER, height INTEGER, fps REAL, codec TEXT,
  has_audio INTEGER, audio_channels INTEGER, rotation INTEGER, orientation TEXT, creation_time TEXT,
  audio_profile TEXT,
  status TEXT,             -- pending | analyzed | missing | duplicate | error
  duplicate_of TEXT, error TEXT,
  analysis TEXT, analysis_version INTEGER,
  first_seen TEXT, last_seen TEXT, analyzed_at TEXT, updated_at TEXT,
  use_count INTEGER DEFAULT 0, last_used TEXT
);
CREATE INDEX IF NOT EXISTS clips_hash ON clips(quick_hash);
CREATE INDEX IF NOT EXISTS clips_path ON clips(abs_path);
CREATE VIRTUAL TABLE IF NOT EXISTS clips_fts USING fts5(
  id UNINDEXED, summary, description, activity, tags_literal, tags_conceptual, uses,
  objects, environment, mood, shot, filename, tokenize='porter unicode61');
CREATE TABLE IF NOT EXISTS usage(id INTEGER PRIMARY KEY, clip_id TEXT, project TEXT,
  used_at TEXT, src_in REAL, src_out REAL, at REAL);
"""


def connect(lib):
    p = lib_paths(lib)
    for k in ("root", "frames", "pending", "plans", "exports", "backups"):
        p[k].mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(p["db"])
    con.row_factory = sqlite3.Row
    con.executescript(DDL)
    con.execute("INSERT OR IGNORE INTO meta VALUES('schema_version', ?)", (str(SCHEMA_VERSION),))
    con.execute("INSERT OR IGNORE INTO meta VALUES('created_at', ?)", (now(),))
    if not p["concepts"].exists():
        seed = SKILL_DIR / "assets" / "concepts.json"
        if seed.exists():
            shutil.copy(seed, p["concepts"])
        else:
            p["concepts"].write_text("{}\n")
    con.commit()
    return con, p


def orientation(w, h):
    if not w or not h:
        return None
    if abs(w - h) / max(w, h) < 0.05:
        return "square"
    return "horizontal" if w > h else "vertical"


def quick_hash(path, size):
    h = hashlib.sha256()
    h.update(str(size).encode())
    with open(path, "rb") as f:
        if size <= 3 * CHUNK:
            h.update(f.read())
        else:
            for off in (0, size // 2 - CHUNK // 2, size - CHUNK):
                f.seek(off)
                h.update(f.read(CHUNK))
    return h.hexdigest()


def probe(path):
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
            timeout=180)
    if r.returncode != 0:
        return None, (r.stderr.strip() or "ffprobe failed")[:300]
    d = json.loads(r.stdout or "{}")
    fmt, streams = d.get("format", {}), d.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video"
              and not s.get("disposition", {}).get("attached_pic")), None)
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if not v:
        return None, "no video stream"

    def rate(s):
        for k in ("avg_frame_rate", "r_frame_rate"):
            try:
                n, dn = (float(x) for x in s.get(k, "0/0").split("/"))
                if n and dn:
                    return round(n / dn, 3)
            except (ValueError, ZeroDivisionError):
                pass
        return None

    dur = float(fmt.get("duration") or v.get("duration") or 0)
    rot = 0
    try:
        rot = int(float(v.get("tags", {}).get("rotate", 0) or 0))
    except ValueError:
        pass
    for sd in v.get("side_data_list") or []:
        if "rotation" in sd:
            try:
                rot = int(float(sd["rotation"]))
            except ValueError:
                pass
    w, h = v.get("width"), v.get("height")
    if w and h and abs(rot) % 180 == 90:
        w, h = h, w
    return {
        "duration": round(dur, 3), "width": w, "height": h, "fps": rate(v),
        "codec": v.get("codec_name"), "has_audio": 1 if a else 0,
        "audio_channels": (a or {}).get("channels"), "rotation": rot,
        "orientation": orientation(w, h),
        "creation_time": (fmt.get("tags") or {}).get("creation_time"),
    }, None


def audio_profile(path, dur):
    """Cheap loudness / activity read. Claude confirms speech visually."""
    window = min(dur or 300, 300)
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-t", "300", "-i", str(path), "-vn",
             "-af", "silencedetect=n=-38dB:d=0.5,volumedetect", "-f", "null", "-"], timeout=400)
    err = r.stderr
    mean = re.search(r"mean_volume:\s*(-?[\d.]+|-inf)", err)
    peak = re.search(r"max_volume:\s*(-?[\d.]+|-inf)", err)
    silent, open_start = 0.0, None
    for line in err.splitlines():
        m = re.search(r"silence_start:\s*(-?[\d.]+)", line)
        if m:
            open_start = max(0.0, float(m.group(1)))
        m = re.search(r"silence_duration:\s*([\d.]+)", line)
        if m:
            silent += float(m.group(1))
            open_start = None
    if open_start is not None:
        silent += max(0.0, window - open_start)
    fmean = float(mean.group(1)) if mean and mean.group(1) != "-inf" else None
    active = max(0.0, min(1.0, 1 - silent / window)) if window else 0.0
    if fmean is None or fmean < -55 or active < 0.1:
        level = "silent"
    elif active < 0.5 or fmean < -35:
        level = "ambient"
    else:
        level = "active"
    return {"mean_db": fmean, "peak_db": float(peak.group(1)) if peak and peak.group(1) != "-inf" else None,
            "active_ratio": round(active, 2), "level": level,
            "note": "level=active means sound most of the time (possible speech) - confirm visually"}


def row_dict(r):
    d = dict(r)
    for k in ("analysis", "audio_profile"):
        if d.get(k):
            try:
                d[k] = json.loads(d[k])
            except ValueError:
                pass
    return d


def load_concepts(p):
    try:
        return json.loads(p["concepts"].read_text())
    except (OSError, ValueError):
        return {}


# --------------------------------------------------------------------------- scan
def iter_videos(folder, library_root):
    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")
                       and not d.endswith((".prproj", "Adobe Premiere Pro Auto-Save"))
                       and Path(dirpath, d).resolve() != library_root]
        for fn in filenames:
            if fn.startswith(".") or fn.startswith("._"):
                continue
            ext = Path(fn).suffix.lower()
            if ext in VIDEO_EXTS or ext in UNSUPPORTED_RAW:
                yield Path(dirpath, fn)


def cmd_scan(a):
    need("ffprobe", "ffmpeg")
    con, p = connect(a.library)
    folder = Path(a.folder).expanduser().resolve()
    if not folder.is_dir():
        die(f"Not a folder: {folder}")
    con.execute("INSERT OR IGNORE INTO roots(path,label,added_at) VALUES(?,?,?)",
                (str(folder), a.label or folder.name, now()))
    root_id = con.execute("SELECT id FROM roots WHERE path=?", (str(folder),)).fetchone()["id"]
    by_path = {r["abs_path"]: r for r in con.execute("SELECT * FROM clips WHERE root_id=?", (root_id,))}
    seen, report = set(), {k: [] for k in
                           ("new", "changed", "moved", "duplicate", "unchanged", "missing", "error", "unsupported")}
    ts = now()
    for f in iter_videos(folder, p["root"]):
        path = str(f.resolve())
        seen.add(path)
        rel = os.path.relpath(path, folder)
        if f.suffix.lower() in UNSUPPORTED_RAW:
            report["unsupported"].append(rel)
            continue
        try:
            st = f.stat()
        except OSError as e:
            report["error"].append({"file": rel, "error": str(e)})
            continue
        row = by_path.get(path)
        if row and row["size"] == st.st_size and abs((row["mtime"] or 0) - st.st_mtime) < 1:
            con.execute("UPDATE clips SET last_seen=? WHERE id=?", (ts, row["id"]))
            report["unchanged"].append(row["id"])
            continue
        qh = quick_hash(path, st.st_size)
        if row:
            if row["quick_hash"] == qh:  # touched only
                con.execute("UPDATE clips SET mtime=?, last_seen=? WHERE id=?", (st.st_mtime, ts, row["id"]))
                report["unchanged"].append(row["id"])
                continue
            meta, err = probe(path)  # same path, new content -> re-analyse
            con.execute("""UPDATE clips SET size=?, mtime=?, quick_hash=?, status=?, error=?, analysis=NULL,
                           analysis_version=NULL, audio_profile=NULL, last_seen=?, updated_at=? WHERE id=?""",
                        (st.st_size, st.st_mtime, qh, "error" if err else "pending", err, ts, ts, row["id"]))
            if meta:
                con.execute("""UPDATE clips SET duration=:duration,width=:width,height=:height,fps=:fps,codec=:codec,
                               has_audio=:has_audio,audio_channels=:audio_channels,rotation=:rotation,
                               orientation=:orientation,creation_time=:creation_time WHERE id=:id""",
                            {**meta, "id": row["id"]})
            con.execute("DELETE FROM clips_fts WHERE id=?", (row["id"],))
            report["changed"].append({"id": row["id"], "file": rel})
            continue
        twins = con.execute("SELECT * FROM clips WHERE quick_hash=? AND status!='duplicate'", (qh,)).fetchall()
        gone = [t for t in twins if not os.path.exists(t["abs_path"])]
        if gone:  # renamed / moved / drive remounted -> keep analysis
            t = gone[0]
            new_status = "analyzed" if t["analysis"] else ("pending" if t["status"] in ("missing", "pending") else t["status"])
            con.execute("""UPDATE clips SET root_id=?, rel_path=?, abs_path=?, filename=?, mtime=?, status=?,
                           last_seen=?, updated_at=? WHERE id=?""",
                        (root_id, rel, path, f.name, st.st_mtime, new_status, ts, ts, t["id"]))
            by_path.pop(t["abs_path"], None)
            report["moved"].append({"id": t["id"], "from": t["rel_path"], "to": rel})
            continue
        if twins:  # identical copy of an existing clip
            orig = twins[0]
            cid = f"c_{qh[:12]}_{hashlib.sha1(path.encode()).hexdigest()[:4]}"
            con.execute("""INSERT OR REPLACE INTO clips(id,root_id,rel_path,abs_path,filename,size,mtime,quick_hash,
                           duration,width,height,fps,codec,has_audio,orientation,status,duplicate_of,first_seen,last_seen,updated_at)
                           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'duplicate',?,?,?,?)""",
                        (cid, root_id, rel, path, f.name, st.st_size, st.st_mtime, qh, orig["duration"], orig["width"],
                         orig["height"], orig["fps"], orig["codec"], orig["has_audio"], orig["orientation"],
                         orig["id"], ts, ts, ts))
            report["duplicate"].append({"id": cid, "file": rel, "duplicate_of": orig["id"], "original": orig["rel_path"]})
            continue
        meta, err = probe(path)
        cid = f"c_{qh[:12]}"
        if con.execute("SELECT 1 FROM clips WHERE id=?", (cid,)).fetchone():
            cid = f"c_{qh[:12]}_{hashlib.sha1(path.encode()).hexdigest()[:4]}"
        con.execute("""INSERT INTO clips(id,root_id,rel_path,abs_path,filename,size,mtime,quick_hash,status,error,
                       first_seen,last_seen,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (cid, root_id, rel, path, f.name, st.st_size, st.st_mtime, qh,
                     "error" if err else "pending", err, ts, ts, ts))
        if meta:
            con.execute("""UPDATE clips SET duration=:duration,width=:width,height=:height,fps=:fps,codec=:codec,
                           has_audio=:has_audio,audio_channels=:audio_channels,rotation=:rotation,
                           orientation=:orientation,creation_time=:creation_time WHERE id=:id""", {**meta, "id": cid})
            report["new"].append({"id": cid, "file": rel, "duration": meta["duration"]})
        else:
            report["error"].append({"id": cid, "file": rel, "error": err})
    for path, row in by_path.items():
        if path not in seen and row["status"] != "missing" and not os.path.exists(path):
            con.execute("UPDATE clips SET status='missing', updated_at=? WHERE id=?", (ts, row["id"]))
            report["missing"].append({"id": row["id"], "file": row["rel_path"]})
    con.execute("UPDATE roots SET last_scan=? WHERE id=?", (ts, root_id))
    con.commit()
    pending = con.execute("SELECT COUNT(*) n FROM clips WHERE status='pending'").fetchone()["n"]
    summary = {k: len(v) for k, v in report.items()}
    out({"ok": True, "root": str(folder), "summary": summary, "pending_analysis_total": pending,
         "details": {k: v for k, v in report.items() if k != "unchanged"},
         "next": "Run: broll.py extract --pending --limit 10  (then analyse each contact sheet)" if pending else
         "Library is up to date."})


# --------------------------------------------------------------------------- status / roots
def cmd_status(a):
    con, p = connect(a.library)
    counts = {r["status"]: r["n"] for r in con.execute("SELECT status, COUNT(*) n FROM clips GROUP BY status")}
    stale = con.execute("SELECT COUNT(*) n FROM clips WHERE status='analyzed' AND analysis_version<?",
                        (ANALYSIS_VERSION,)).fetchone()["n"]
    roots = [dict(r) for r in con.execute("SELECT * FROM roots")]
    for r in roots:
        r["online"] = os.path.isdir(r["path"])
    pend = [dict(r) for r in con.execute(
        "SELECT id, rel_path, duration FROM clips WHERE status='pending' ORDER BY first_seen LIMIT ?", (a.limit,))]
    hours = con.execute("SELECT COALESCE(SUM(duration),0) s FROM clips WHERE status='analyzed'").fetchone()["s"] / 3600
    out({"ok": True, "library": str(p["root"]), "counts": counts, "analyzed_hours": round(hours, 2),
         "outdated_analysis": stale, "roots": roots, "pending_sample": pend})


def cmd_roots(a):
    con, _ = connect(a.library)
    rows = [dict(r) for r in con.execute(
        "SELECT r.*, (SELECT COUNT(*) FROM clips c WHERE c.root_id=r.id) clips FROM roots r")]
    for r in rows:
        r["online"] = os.path.isdir(r["path"])
    out({"ok": True, "roots": rows})


def cmd_relink(a):
    con, _ = connect(a.library)
    old = str(Path(a.old).expanduser())
    new = str(Path(a.new).expanduser().resolve())
    r = con.execute("SELECT * FROM roots WHERE path=?", (old.rstrip("/"),)).fetchone()
    if not r:
        die(f"No root registered at {old}. See: broll.py roots")
    if not os.path.isdir(new):
        die(f"New folder not found: {new}")
    if con.execute("SELECT 1 FROM roots WHERE path=?", (new,)).fetchone():
        die("That new folder is already a registered root; just run scan on it instead.")
    con.execute("UPDATE roots SET path=? WHERE id=?", (new, r["id"]))
    fixed, still_missing = 0, []
    for c in con.execute("SELECT id, rel_path, status, analysis FROM clips WHERE root_id=?", (r["id"],)).fetchall():
        np_ = str(Path(new, c["rel_path"]))
        st = c["status"]
        if os.path.exists(np_):
            fixed += 1
            if st == "missing":
                st = "analyzed" if c["analysis"] else "pending"
        else:
            still_missing.append(c["rel_path"])
        con.execute("UPDATE clips SET abs_path=?, status=? WHERE id=?", (np_, st, c["id"]))
    con.commit()
    out({"ok": True, "relinked": fixed, "not_found": still_missing[:50],
         "next": "Run scan on the new folder to pick up any new or changed files."})


# --------------------------------------------------------------------------- extract
def pick_times(dur, n=None):
    if not dur or dur <= 0:
        return [0.0]
    if n is None:
        n = max(6, min(24, round(dur / 2.0)))
    if dur < 1.5:
        n = min(n, 3)
    lo, hi = min(0.25, dur * 0.1), max(dur - 0.25, dur * 0.9)
    if n == 1:
        return [round(dur / 2, 2)]
    return [round(lo + (hi - lo) * i / (n - 1), 2) for i in range(n)]


def grab_frame(src, t, dest):
    vf = "scale=640:640:force_original_aspect_ratio=decrease,scale=trunc(iw/2)*2:trunc(ih/2)*2"
    r = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", str(src),
             "-frames:v", "1", "-vf", vf, "-q:v", "4", str(dest)], timeout=120)
    return r.returncode == 0 and dest.exists() and dest.stat().st_size > 0


def build_sheets(frames, clip, outdir, per_sheet=12):
    """frames: list of (t, path). Returns list of sheet paths."""
    sheets = []
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        Image = None
    vertical = clip.get("orientation") == "vertical"
    cols = 6 if vertical else 4
    for si in range(0, len(frames), per_sheet):
        chunk = frames[si:si + per_sheet]
        dest = outdir / f"sheet_{si // per_sheet + 1:02d}.jpg"
        if Image:
            cell_w = 300 if vertical else 420
            thumbs = []
            for t, fp in chunk:
                im = Image.open(fp).convert("RGB")
                im.thumbnail((cell_w, cell_w * 2))
                thumbs.append((t, im))
            cell_h = max(im.height for _, im in thumbs)
            rows = (len(thumbs) + cols - 1) // cols
            header = 44
            sheet = Image.new("RGB", (cols * cell_w + (cols + 1) * 6, header + rows * (cell_h + 6) + 6), (20, 20, 20))
            d = ImageDraw.Draw(sheet)
            try:
                font = ImageFont.truetype("DejaVuSans-Bold.ttf", 18)
                small = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
            except OSError:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 18)
                    small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 16)
                except OSError:
                    font = small = ImageFont.load_default()
            title = (f"{clip['id']}  |  {clip['rel_path']}  |  {clip.get('duration') or 0:.1f}s  |  "
                     f"{clip.get('width')}x{clip.get('height')}  |  sheet {si // per_sheet + 1}")
            d.text((8, 12), title[:150], fill=(255, 255, 255), font=font)
            for i, (t, im) in enumerate(thumbs):
                x = 6 + (i % cols) * (cell_w + 6)
                y = header + 6 + (i // cols) * (cell_h + 6)
                sheet.paste(im, (x + (cell_w - im.width) // 2, y))
                label = f"{t:.1f}s"
                d.rectangle([x, y, x + 74, y + 24], fill=(0, 0, 0))
                d.text((x + 5, y + 3), label, fill=(255, 220, 0), font=small)
            sheet.save(dest, quality=82)
        else:
            lst = outdir / "_list.txt"
            lst.write_text("".join(f"file '{fp}'\n" for _, fp in chunk))
            rows = (len(chunk) + cols - 1) // cols
            run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                 "-vf", f"scale=420:-2,tile={cols}x{rows}:padding=6", "-frames:v", "1", str(dest)])
            lst.unlink(missing_ok=True)
        if dest.exists():
            sheets.append(str(dest))
    return sheets


TEMPLATE_FIELDS = {
    "summary": "", "description": "", "people": [], "speaking": "none",
    "location": "", "environment": "", "time_of_day": "", "setting_details": "",
    "objects": [], "devices": [], "activity": "", "actions": [],
    "shot_type": "", "camera_angle": "", "camera_movement": "", "subject_movement": "",
    "lighting": "", "colour": "", "mood": [],
    "tags_literal": [], "tags_conceptual": [], "editorial_uses": [], "avoid_for": [],
    "segments": [], "best_section": {"start": None, "end": None, "why": ""},
    "quality": None, "usefulness": None, "issues": [], "notes": "",
}


def cmd_extract(a):
    need("ffmpeg")
    con, p = connect(a.library)
    if a.id:
        rows = con.execute("SELECT * FROM clips WHERE id IN (%s)" % ",".join("?" * len(a.id)), a.id).fetchall()
    elif a.pending:
        rows = con.execute("""SELECT * FROM clips WHERE status='pending' ORDER BY first_seen LIMIT ?""",
                           (a.limit,)).fetchall()
    else:
        die("Use --id <clip_id> [...] or --pending")
    results = []
    for r in rows:
        c = dict(r)
        if c["status"] in ("missing", "duplicate"):
            results.append({"id": c["id"], "skipped": c["status"]})
            continue
        if not os.path.exists(c["abs_path"]):
            results.append({"id": c["id"], "skipped": "file not reachable (drive unplugged?)"})
            continue
        fdir = p["frames"] / c["id"]
        if fdir.exists():
            shutil.rmtree(fdir)
        fdir.mkdir(parents=True)
        frames = []
        for i, t in enumerate(pick_times(c["duration"], a.frames)):
            dest = fdir / f"f_{i:03d}_{t:07.2f}.jpg"
            if grab_frame(c["abs_path"], t, dest):
                frames.append((t, str(dest)))
        if not frames:
            con.execute("UPDATE clips SET status='error', error='frame extraction failed' WHERE id=?", (c["id"],))
            con.commit()
            results.append({"id": c["id"], "error": "frame extraction failed"})
            continue
        sheets = build_sheets(frames, c, fdir)
        ap = None
        if c["has_audio"]:
            ap = audio_profile(c["abs_path"], c["duration"])
            con.execute("UPDATE clips SET audio_profile=? WHERE id=?", (json.dumps(ap), c["id"]))
            con.commit()
        tpl = {"clip_id": c["id"], "filename": c["filename"], "duration": c["duration"],
               "orientation": c["orientation"], **TEMPLATE_FIELDS}
        tpl_path = p["pending"] / f"{c['id']}.json"
        if not tpl_path.exists():
            tpl_path.write_text(json.dumps(tpl, indent=2))
        results.append({
            "id": c["id"], "file": c["rel_path"], "duration": c["duration"],
            "resolution": f"{c['width']}x{c['height']}", "fps": c["fps"], "orientation": c["orientation"],
            "audio": ap if ap else "no audio track", "sheets": sheets,
            "frame_times": [t for t, _ in frames], "analysis_file": str(tpl_path),
        })
    out({"ok": True, "clips": results,
         "next": "Read each sheet image, fill the analysis_file per references/analysis-guide.md, then: "
                 "broll.py ingest --dir <library>/pending"})


# --------------------------------------------------------------------------- ingest
def _norm_list(v):
    if v is None:
        return []
    if isinstance(v, str):
        v = [x for x in re.split(r"[,;\n]", v)]
    seen, outl = set(), []
    for x in v:
        if isinstance(x, (dict, list)):
            outl.append(x)
            continue
        s = re.sub(r"\s+", " ", str(x)).strip()
        if s and s.lower() not in seen:
            seen.add(s.lower())
            outl.append(s)
    return outl


def validate_analysis(an, clip):
    errs, warns = [], []
    dur = clip["duration"] or 0
    for k in ("summary", "description", "activity", "shot_type", "camera_movement", "speaking"):
        if not isinstance(an.get(k), str) or not an.get(k).strip():
            errs.append(f"'{k}' must be a non-empty string")
    for k in ("tags_literal", "tags_conceptual", "editorial_uses"):
        an[k] = _norm_list(an.get(k))
    an["tags_literal"] = [t.lower() for t in an["tags_literal"]]
    an["tags_conceptual"] = [t.lower() for t in an["tags_conceptual"]]
    if len(an["tags_literal"]) < 5:
        errs.append("tags_literal needs at least 5 tags")
    if len(an["tags_conceptual"]) < 5:
        errs.append("tags_conceptual needs at least 5 tags")
    if len(an["editorial_uses"]) < 2:
        errs.append("editorial_uses needs at least 2 entries")
    for k in ("objects", "devices", "actions", "mood", "avoid_for", "issues", "people"):
        an[k] = _norm_list(an.get(k))
    for k in ("quality", "usefulness"):
        try:
            v = int(an.get(k))
            if not 1 <= v <= 5:
                raise ValueError
            an[k] = v
        except (TypeError, ValueError):
            errs.append(f"'{k}' must be an integer 1-5")
    segs = an.get("segments") or []
    if not isinstance(segs, list) or not segs:
        errs.append("segments must list at least one {start,end,description,usable,quality}")
        segs = []
    for i, s in enumerate(segs):
        try:
            s["start"], s["end"] = float(s["start"]), float(s["end"])
        except (KeyError, TypeError, ValueError):
            errs.append(f"segment {i} needs numeric start/end")
            continue
        if s["start"] < 0 or s["end"] <= s["start"] or s["end"] > dur + 0.6:
            errs.append(f"segment {i} ({s['start']}-{s['end']}) outside clip 0-{dur}")
        s.setdefault("usable", True)
        if not s.get("description"):
            warns.append(f"segment {i} has no description")
    bs = an.get("best_section") or {}
    try:
        bs["start"], bs["end"] = float(bs["start"]), float(bs["end"])
        if bs["start"] < 0 or bs["end"] <= bs["start"] or bs["end"] > dur + 0.6:
            errs.append(f"best_section {bs['start']}-{bs['end']} outside clip 0-{dur}")
    except (KeyError, TypeError, ValueError):
        errs.append("best_section needs numeric start/end")
    an["best_section"] = bs
    blob = json.dumps(an).lower()
    if "todo" in blob or "lorem" in blob:
        errs.append("analysis still contains placeholder text (TODO/lorem)")
    if an.get("speaking") not in SPEAKING:
        warns.append(f"speaking '{an.get('speaking')}' not one of {SPEAKING}")
    if not any(st in (an.get("shot_type") or "").lower() for st in SHOT_TYPES):
        warns.append(f"shot_type '{an.get('shot_type')}' not in standard list {SHOT_TYPES}")
    return errs, warns


def fts_row(cid, filename, an):
    j = lambda v: " | ".join(x if isinstance(x, str) else json.dumps(x) for x in (v or []))
    return (cid, an.get("summary", ""), an.get("description", ""),
            f"{an.get('activity', '')} | {j(an.get('actions'))}",
            j(an.get("tags_literal")), j(an.get("tags_conceptual")), j(an.get("editorial_uses")),
            f"{j(an.get('objects'))} | {j(an.get('devices'))}",
            f"{an.get('location', '')} | {an.get('environment', '')} | {an.get('setting_details', '')} | {an.get('time_of_day', '')}",
            f"{j(an.get('mood'))} | {an.get('lighting', '')} | {an.get('colour', '')}",
            f"{an.get('shot_type', '')} | {an.get('camera_angle', '')} | {an.get('camera_movement', '')} | {an.get('speaking', '')}",
            re.sub(r"[_\-.]+", " ", filename or ""))


def cmd_ingest(a):
    con, p = connect(a.library)
    files = []
    if a.dir:
        files = sorted(Path(a.dir).expanduser().glob("*.json"))
    files += [Path(f).expanduser() for f in a.files]
    if not files:
        die("Nothing to ingest. Pass analysis JSON files or --dir.")
    done, failed, skipped = [], [], []
    for f in files:
        try:
            an = json.loads(f.read_text())
        except (OSError, ValueError) as e:
            failed.append({"file": str(f), "errors": [f"unreadable JSON: {e}"]})
            continue
        cid = an.get("clip_id")
        r = con.execute("SELECT * FROM clips WHERE id=?", (cid,)).fetchone()
        if not r:
            failed.append({"file": str(f), "errors": [f"unknown clip_id {cid}"]})
            continue
        if not (an.get("summary") or "").strip() and a.dir:
            skipped.append(cid)  # untouched template
            continue
        errs, warns = validate_analysis(an, dict(r))
        if errs:
            failed.append({"file": str(f), "clip_id": cid, "errors": errs, "warnings": warns})
            continue
        for k in ("filename", "duration", "orientation"):
            an.pop(k, None)
        ts = now()
        con.execute("""UPDATE clips SET analysis=?, analysis_version=?, status='analyzed', analyzed_at=?, updated_at=?,
                       error=NULL WHERE id=?""", (json.dumps(an, ensure_ascii=False), ANALYSIS_VERSION, ts, ts, cid))
        con.execute("DELETE FROM clips_fts WHERE id=?", (cid,))
        con.execute("INSERT INTO clips_fts VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", fts_row(cid, r["filename"], an))
        con.commit()
        if f.parent.resolve() == p["pending"].resolve():
            f.unlink()
        done.append({"id": cid, "warnings": warns} if warns else cid)
    remaining = con.execute("SELECT COUNT(*) n FROM clips WHERE status='pending'").fetchone()["n"]
    out({"ok": not failed, "ingested": done, "failed": failed, "skipped_unfilled": skipped,
         "pending_remaining": remaining})


# --------------------------------------------------------------------------- show / dump / search
def cmd_show(a):
    con, _ = connect(a.library)
    rows = [row_dict(r) for r in con.execute(
        "SELECT * FROM clips WHERE id IN (%s)" % ",".join("?" * len(a.ids)), a.ids)]
    for r in rows:
        r["usage"] = [dict(u) for u in con.execute(
            "SELECT project, used_at, at, src_in, src_out FROM usage WHERE clip_id=? ORDER BY used_at DESC", (r["id"],))]
    out({"ok": True, "clips": rows})


def compact(r, an):
    return {
        "id": r["id"], "file": r["rel_path"], "dur": r["duration"], "orient": r["orientation"],
        "online": os.path.exists(r["abs_path"]) if r["abs_path"] else False,
        "summary": an.get("summary"), "shot": an.get("shot_type"), "move": an.get("camera_movement"),
        "speaking": an.get("speaking"), "location": an.get("location"),
        "literal": an.get("tags_literal", [])[:14], "concepts": an.get("tags_conceptual", [])[:14],
        "uses": an.get("editorial_uses", [])[:5], "avoid": an.get("avoid_for", [])[:3],
        "best": [an.get("best_section", {}).get("start"), an.get("best_section", {}).get("end")],
        "q": an.get("quality"), "u": an.get("usefulness"), "used": r["use_count"],
    }


def cmd_dump(a):
    con, _ = connect(a.library)
    rows = con.execute("SELECT * FROM clips WHERE status='analyzed' ORDER BY rel_path").fetchall()
    clips = [compact(r, json.loads(r["analysis"])) for r in rows]
    if a.full:
        clips = [row_dict(r) for r in rows]
    out({"ok": True, "count": len(clips), "clips": clips})


def build_terms(query, expand, concepts):
    q = query.lower()
    terms, hit_concepts = [], []
    for k, vals in concepts.items():
        if k.startswith("_"):
            continue
        if re.search(r"\b" + re.escape(k.lower()) + r"\b", q):
            hit_concepts.append(k)
            terms.append(k.lower())
            terms += [v.lower() for v in vals]
    terms += [w for w in re.findall(r"[a-z0-9']+", q) if w not in STOP and len(w) > 1]
    if expand:
        terms += [e.strip().lower() for e in expand.split(",") if e.strip()]
    seen, res = set(), []
    for t in terms:
        if t not in seen:
            seen.add(t)
            res.append(t)
    return res, hit_concepts


def fts_expr(terms):
    parts = []
    for t in terms:
        toks = [x for x in re.findall(r"[a-z0-9]+", t.lower())]
        if not toks:
            continue
        parts.append('"' + " ".join(toks) + '"')
        if len(toks) > 1:
            parts += ['"' + x + '"' for x in toks if x not in STOP and len(x) > 2]
    seen, res = set(), []
    for x in parts:
        if x not in seen:
            seen.add(x)
            res.append(x)
    return " OR ".join(res)


def cmd_search(a):
    con, p = connect(a.library)
    terms, concepts_hit = build_terms(a.query, a.expand, load_concepts(p))
    expr = fts_expr(terms)
    if not expr:
        die("Query has no searchable words. Add --expand with visual terms.")
    rows = con.execute(
        """SELECT c.*, bm25(clips_fts, 0, 2.0, 1.5, 3.0, 3.0, 3.0, 2.5, 2.0, 1.0, 1.0, 0.6, 0.3) AS r
           FROM clips_fts JOIN clips c ON c.id = clips_fts.id
           WHERE clips_fts MATCH ? AND c.status='analyzed' ORDER BY r LIMIT 300""", (expr,)).fetchall()
    excl = set((a.exclude or "").split(",")) - {""}
    best = max((-r["r"] for r in rows), default=1) or 1
    results = []
    for r in rows:
        an = json.loads(r["analysis"])
        if r["id"] in excl:
            continue
        if a.orientation and r["orientation"] != a.orientation:
            continue
        if a.min_quality and (an.get("quality") or 0) < a.min_quality:
            continue
        if a.speaking and (an.get("speaking") or "") != a.speaking:
            continue
        if a.shot and a.shot.lower() not in (an.get("shot_type") or "").lower():
            continue
        if a.min_duration and (r["duration"] or 0) < a.min_duration:
            continue
        text = " ".join(str(x) for x in fts_row("", r["filename"], an)).lower()
        matched = [t for t in terms if re.search(r"\b" + re.escape(t) + r"", text)]
        rel = (-r["r"]) / best
        score = 0.75 * rel + 0.25 * ((an.get("quality") or 3) + (an.get("usefulness") or 3)) / 10
        if a.fresh:
            score -= min(0.2, 0.04 * (r["use_count"] or 0))
        c = compact(r, an)
        c.update(score=round(score, 3), matched=matched[:12], description=an.get("description"))
        results.append(c)
    results.sort(key=lambda x: -x["score"])
    total = con.execute("SELECT COUNT(*) n FROM clips WHERE status='analyzed'").fetchone()["n"]
    out({"ok": True, "query": a.query, "concepts_matched": concepts_hit, "terms_used": terms,
         "candidates": results[:a.limit], "candidate_pool": len(results), "library_size": total,
         "note": "Candidates are keyword-ranked. Rerank by meaning using description/uses/avoid before answering."
                 + (" Few hits: try --expand with more visual synonyms, or `dump` to review all clips."
                    if len(results) < 3 else "")})


# --------------------------------------------------------------------------- transcript
def parse_time(s):
    s = s.strip().replace(",", ".")
    secs = 0.0
    for part in s.split(":"):
        secs = secs * 60 + float(part)
    return secs


def _clean(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>|\{[^}]+\}", "", t)).strip()


def parse_cues(text):
    segs = []
    for block in re.split(r"\n\s*\n", text.replace("\r", "")):
        lines = [l for l in block.strip().split("\n") if l.strip()]
        idx = next((i for i, l in enumerate(lines) if "-->" in l), None)
        if idx is None:
            continue
        a_, b_ = lines[idx].split("-->")
        try:
            st, en = parse_time(a_), parse_time(b_.strip().split()[0])
        except ValueError:
            continue
        txt = _clean(" ".join(lines[idx + 1:]))
        if txt:
            segs.append({"start": round(st, 3), "end": round(en, 3), "text": txt})
    return segs


def words_to_segments(words, max_len=12.0, gap=0.7):
    segs, cur = [], None
    for w in words:
        t = (w.get("punctuated_word") or w.get("word") or w.get("text") or "").strip()
        if not t or w.get("type") in ("spacing", "audio_event"):
            continue
        st, en = float(w.get("start", 0)), float(w.get("end", w.get("start", 0)))
        if cur and (st - cur["end"] > gap or en - cur["start"] > max_len or re.search(r"[.!?]$", cur["text"])):
            segs.append(cur)
            cur = None
        if cur is None:
            cur = {"start": st, "end": en, "text": t}
        else:
            cur["end"], cur["text"] = en, cur["text"] + " " + t
    if cur:
        segs.append(cur)
    return [{"start": round(s["start"], 3), "end": round(s["end"], 3), "text": s["text"]} for s in segs]


def parse_json_transcript(d):
    if isinstance(d, dict) and isinstance(d.get("segments"), list):
        return [{"start": float(s["start"]), "end": float(s["end"]), "text": _clean(s.get("text", ""))}
                for s in d["segments"]]
    if isinstance(d, dict) and "results" in d:
        res = d["results"]
        if res.get("utterances"):
            return [{"start": u["start"], "end": u["end"], "text": u["transcript"]} for u in res["utterances"]]
        alt = res["channels"][0]["alternatives"][0]
        return words_to_segments(alt.get("words", []))
    if isinstance(d, dict) and isinstance(d.get("words"), list):
        return words_to_segments(d["words"])
    if isinstance(d, list) and d and "start" in d[0]:
        if "text" in d[0] and len(str(d[0]["text"]).split()) > 1:
            return [{"start": float(s["start"]), "end": float(s["end"]), "text": _clean(s["text"])} for s in d]
        return words_to_segments(d)
    raise ValueError("Unrecognised JSON transcript shape")


def estimate_segments(text, wpm):
    text = re.sub(r"\s+", " ", text).strip()
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    segs, t = [], 0.0
    for s in sents:
        d = max(1.0, len(s.split()) / wpm * 60)
        segs.append({"start": round(t, 2), "end": round(t + d, 2), "text": s})
        t += d
    return segs


def group_segments(segs, target):
    if not target:
        return segs
    out_, cur = [], None
    for s in segs:
        if cur is None:
            cur = dict(s)
            continue
        span = cur["end"] - cur["start"]
        if span >= target and re.search(r"[.!?\"']$", cur["text"]) or span >= target * 2:
            out_.append(cur)
            cur = dict(s)
        else:
            cur["end"], cur["text"] = s["end"], cur["text"] + " " + s["text"]
    if cur:
        out_.append(cur)
    return out_


def cmd_transcript(a):
    f = Path(a.file).expanduser()
    if not f.exists():
        die(f"Not found: {f}")
    ext = f.suffix.lower()
    if ext in VIDEO_EXTS or ext in {".wav", ".mp3", ".m4a", ".aac"}:
        die("That is a media file. Get a transcript first: export captions as SRT from your editing app "
            "(Premiere: Text panel > Captions > Export to SRT), or transcribe it with "
            "`python3 scripts/stt.py <file> words.json`, then pass the .srt or .json here.")
    raw = f.read_text(encoding="utf-8-sig", errors="replace")
    timed = True
    if ext in (".srt", ".vtt"):
        segs = parse_cues(raw)
    elif ext == ".json":
        segs = parse_json_transcript(json.loads(raw))
    elif ext in (".csv", ".tsv"):
        rd = csv.DictReader(raw.splitlines(), delimiter="\t" if ext == ".tsv" else ",")
        segs = []
        for row in rd:
            row = {k.lower().strip(): v for k, v in row.items() if k}
            segs.append({"start": parse_time(row.get("start") or row.get("in") or "0"),
                         "end": parse_time(row.get("end") or row.get("out") or "0"),
                         "text": _clean(row.get("text") or row.get("transcript") or "")})
    else:
        segs, timed = estimate_segments(raw, a.wpm), False
    segs = [s for s in segs if s["text"]]
    if not segs:
        die("No transcript text found in file.")
    segs = group_segments(segs, a.group)
    for i, s in enumerate(segs, 1):
        s["i"] = i
    res = {"ok": True, "source": str(f), "timed": timed, "count": len(segs),
           "duration": segs[-1]["end"], "segments": segs}
    if not timed:
        res["warning"] = f"Script has no timecodes; times are estimated at {a.wpm} wpm. Re-run on the real SRT before exporting to your editing app."
    if a.output:
        Path(a.output).expanduser().write_text(json.dumps(res, indent=2, ensure_ascii=False))
        out({k: v for k, v in res.items() if k != "segments"} | {"written": a.output})
    else:
        out(res)


# --------------------------------------------------------------------------- plan
def load_plan(path):
    try:
        plan = json.loads(Path(path).expanduser().read_text())
    except (OSError, ValueError) as e:
        die(f"Cannot read plan: {e}")
    if not isinstance(plan.get("placements"), list):
        die("Plan needs a 'placements' list (see references/schema.md)")
    return plan


def check_plan(con, plan, edge=0.4):
    errors, warnings, info = [], [], []
    clips = {}
    main_dur = None
    if plan.get("main_video"):
        mv = Path(plan["main_video"]).expanduser()
        if mv.exists():
            meta, _ = probe(mv) if shutil.which("ffprobe") else (None, None)
            main_dur = meta["duration"] if meta else None
        else:
            warnings.append(f"main_video not found: {mv}")
    pl = sorted(plan["placements"], key=lambda x: float(x.get("at", 0)))
    used_ranges = {}
    prev_shot = None
    for i, x in enumerate(pl):
        tag = f"#{x.get('n', i + 1)} @ {x.get('at')}s"
        try:
            at, dur, si = float(x["at"]), float(x["duration"]), float(x.get("src_in", 0))
        except (KeyError, TypeError, ValueError):
            errors.append(f"{tag}: needs numeric at, duration, src_in")
            continue
        r = con.execute("SELECT * FROM clips WHERE id=?", (x.get("clip_id"),)).fetchone()
        if not r:
            errors.append(f"{tag}: unknown clip_id {x.get('clip_id')}")
            continue
        clips[r["id"]] = r
        an = json.loads(r["analysis"]) if r["analysis"] else {}
        if r["status"] != "analyzed":
            errors.append(f"{tag}: clip {r['id']} status is {r['status']}")
        if not os.path.exists(r["abs_path"]):
            warnings.append(f"{tag}: source file not reachable right now ({r['rel_path']}) - plug in the drive before importing")
        cd = r["duration"] or 0
        if si < 0 or si + dur > cd + 0.05:
            errors.append(f"{tag}: source {si:.2f}-{si + dur:.2f}s exceeds clip length {cd:.2f}s")
        if si < edge:
            warnings.append(f"{tag}: starts {si:.2f}s into the recording - first moments are often camera setup")
        if cd - (si + dur) < edge:
            warnings.append(f"{tag}: runs to the very end of the recording - check for the reach-to-stop moment")
        for s in an.get("segments", []):
            if s.get("usable") is False and s["start"] < si + dur and s["end"] > si:
                warnings.append(f"{tag}: overlaps unusable part {s['start']}-{s['end']}s ({s.get('description', '')})")
        if dur < 1.0:
            warnings.append(f"{tag}: {dur:.1f}s is very short (flash cut) - intended?")
        if dur > 8.0:
            warnings.append(f"{tag}: {dur:.1f}s is long for B-roll over talking - consider splitting")
        if main_dur and at + dur > main_dur + 0.05:
            errors.append(f"{tag}: ends after the main video ({main_dur:.1f}s)")
        rng = used_ranges.setdefault(r["id"], [])
        for (o_in, o_out, o_tag) in rng:
            if si < o_out and si + dur > o_in:
                warnings.append(f"{tag}: re-uses the same frames of {r['id']} as {o_tag}")
                break
        else:
            if rng:
                info.append(f"{tag}: {r['id']} already used at {rng[0][2]} (different section)")
        rng.append((si, si + dur, tag))
        shot = (an.get("shot_type") or "").lower()
        if prev_shot and shot and shot == prev_shot[0] and abs(at - prev_shot[1]) < 6:
            info.append(f"{tag}: same shot type ({shot}) as the previous B-roll - consider variety")
        prev_shot = (shot, at + dur)
    tracks = {}
    for x in pl:
        try:
            tracks.setdefault(int(x.get("track", 2)), []).append((float(x["at"]), float(x["at"]) + float(x["duration"]), x))
        except (KeyError, TypeError, ValueError):
            pass
    for t, items in tracks.items():
        items.sort(key=lambda z: z[0])
        for (a1, b1, x1), (a2, b2, x2) in zip(items, items[1:]):
            if a2 < b1 - 0.01:
                errors.append(f"V{t}: placement #{x2.get('n')} at {a2}s overlaps #{x1.get('n')} (ends {b1:.2f}s)")
    return {"errors": errors, "warnings": warnings, "info": info, "placements": len(pl),
            "distinct_clips": len(clips), "main_duration": main_dur}, clips


def cmd_plan_check(a):
    con, _ = connect(a.library)
    plan = load_plan(a.plan)
    res, _ = check_plan(con, plan)
    out({"ok": not res["errors"], **res})


# --------------------------------------------------------------------------- export
NTSC = {23.976: 24, 23.98: 24, 29.97: 30, 59.94: 60, 47.952: 48, 119.88: 120}


def rate_el(parent, fps):
    tb, ntsc = (NTSC[fps], True) if fps in NTSC else (int(round(fps)), False)
    r = ET.SubElement(parent, "rate")
    ET.SubElement(r, "timebase").text = str(tb)
    ET.SubElement(r, "ntsc").text = "TRUE" if ntsc else "FALSE"
    return r


def fr(sec, fps):
    return int(round(float(sec) * fps))


def pathurl(p):
    return "file://localhost" + urllib.parse.quote(str(Path(p).resolve()).replace("\\", "/"))


def sub(parent, tag, text=None):
    e = ET.SubElement(parent, tag)
    if text is not None:
        e.text = str(text)
    return e


def file_el(parent, fid, path, dur_s, fps, w, h, has_audio, channels, emitted):
    if fid in emitted:
        ET.SubElement(parent, "file", id=fid)
        return
    emitted.add(fid)
    f = ET.SubElement(parent, "file", id=fid)
    sub(f, "name", Path(path).name)
    sub(f, "pathurl", pathurl(path))
    rate_el(f, fps)
    sub(f, "duration", fr(dur_s, fps))
    tc = sub(f, "timecode")
    rate_el(tc, fps)
    sub(tc, "string", "00:00:00:00")
    sub(tc, "frame", 0)
    sub(tc, "displayformat", "NDF")
    media = sub(f, "media")
    v = sub(sub(media, "video"), "samplecharacteristics")
    rate_el(v, fps)
    if w:
        sub(v, "width", w)
    if h:
        sub(v, "height", h)
    if has_audio:
        au = sub(media, "audio")
        sc = sub(au, "samplecharacteristics")
        sub(sc, "depth", 16)
        sub(sc, "samplerate", 48000)
        sub(au, "channelcount", channels or 2)


def clipitem(track, cid, name, fid, path, src_dur, fps, start, end, cin, cout, meta, emitted,
             audio=False, src_track=1, comment=None):
    ci = ET.SubElement(track, "clipitem", id=cid)
    sub(ci, "name", name)
    sub(ci, "enabled", "TRUE")
    sub(ci, "duration", fr(src_dur, fps))
    rate_el(ci, fps)
    sub(ci, "start", start)
    sub(ci, "end", end)
    sub(ci, "in", cin)
    sub(ci, "out", cout)
    file_el(ci, fid, path, src_dur, fps, meta.get("width"), meta.get("height"),
            meta.get("has_audio"), meta.get("audio_channels"), emitted)
    if audio:
        st = sub(ci, "sourcetrack")
        sub(st, "mediatype", "audio")
        sub(st, "trackindex", src_track)
    if comment:
        mk = sub(ci, "marker")
        sub(mk, "name", "B-roll")
        sub(mk, "comment", comment[:500])
        sub(mk, "in", cin)
        sub(mk, "out", -1)
    return ci


def build_xml(plan, clips, fps, w, h):
    root = ET.Element("xmeml", version="4")
    seq = sub(root, "sequence", None)
    seq.set("id", "sequence-1")
    name = f"{plan.get('project', 'Video')} - Personal B-roll"
    sub(seq, "name", name)
    pl = sorted(plan["placements"], key=lambda x: float(x["at"]))
    main = plan.get("main_video")
    main_meta = None
    if main and Path(main).expanduser().exists():
        main_meta, _ = probe(Path(main).expanduser())
    end_s = max([float(x["at"]) + float(x["duration"]) for x in pl] + [main_meta["duration"] if main_meta else 0])
    sub(seq, "duration", fr(end_s, fps))
    rate_el(seq, fps)
    tc = sub(seq, "timecode")
    rate_el(tc, fps)
    sub(tc, "string", "00:00:00:00")
    sub(tc, "frame", 0)
    sub(tc, "displayformat", "NDF")
    media = sub(seq, "media")
    video = sub(media, "video")
    fmt = sub(sub(video, "format"), "samplecharacteristics")
    rate_el(fmt, fps)
    sub(fmt, "width", w)
    sub(fmt, "height", h)
    sub(fmt, "pixelaspectratio", "square")
    emitted = set()
    v1 = sub(video, "track")
    audio = sub(media, "audio")
    if main_meta:
        md = main_meta["duration"]
        clipitem(v1, "clipitem-main-v", Path(main).name, "file-main", Path(main).expanduser(), md, fps,
                 0, fr(md, fps), 0, fr(md, fps), main_meta, emitted)
        for ch in range(1, min(main_meta.get("audio_channels") or 0, 2) + 1 if main_meta.get("has_audio") else 1):
            at = sub(audio, "track")
            clipitem(at, f"clipitem-main-a{ch}", Path(main).name, "file-main", Path(main).expanduser(), md, fps,
                     0, fr(md, fps), 0, fr(md, fps), main_meta, emitted, audio=True, src_track=ch)
    v2 = sub(video, "track")
    for i, x in enumerate(pl, 1):
        r = clips[x["clip_id"]]
        meta = dict(r)
        st = fr(x["at"], fps)
        en = st + max(1, fr(x["duration"], fps))
        cin = fr(x.get("src_in", 0), fps)
        cout = cin + (en - st)
        note = f"{x.get('says', '')} || why: {x.get('why', '')}".strip(" |")
        clipitem(v2, f"clipitem-broll-{i}", r["filename"], f"file-{r['id']}", r["abs_path"], r["duration"], fps,
                 st, en, cin, cout, meta, emitted, comment=note)
    for i, x in enumerate(pl, 1):
        mk = sub(seq, "marker")
        sub(mk, "name", f"B-roll {i}: {clips[x['clip_id']]['filename']}")
        sub(mk, "comment", (x.get("says") or "")[:300])
        sub(mk, "in", fr(x["at"], fps))
        sub(mk, "out", -1)
    for g in plan.get("gaps", []):
        mk = sub(seq, "marker")
        sub(mk, "name", "B-roll gap (no personal clip)")
        sub(mk, "comment", f"{g.get('says', '')} || idea: {g.get('visual_idea', '')}"[:300])
        sub(mk, "in", fr(g.get("at", 0), fps))
        sub(mk, "out", -1)
    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n' + ET.tostring(root, encoding="unicode") + "\n"


JSX_TEMPLATE = r"""/*
  Personal B-roll placer - generated by personal-broll-library (broll.py export --to jsx)
  EXPERIMENTAL. Runs inside Premiere Pro as ExtendScript (e.g. via the VS Code
  "ExtendScript Debugger" extension, target: Premiere Pro).

  Safety: it never edits your open sequence. It clones the active sequence,
  works on the clone (named "<name> + B-roll"), imports the B-roll files into a
  bin called "Personal B-roll (auto)", makes VIDEO-ONLY subclips of the chosen
  sections and overwrites them onto the target video track of the clone.
  Your dialogue audio is untouched because the subclips carry no audio.
*/
(function () {
  var PLAN = __PLAN__;
  var BIN_NAME = "Personal B-roll (auto)";
  function log(s) { $.writeln(s); }
  if (!app.project || !app.project.activeSequence) { alert("Open the sequence you want B-roll added to, then run again."); return; }
  var original = app.project.activeSequence;
  var originalName = original.name;
  if (!original.clone()) { alert("Could not clone the sequence - nothing was changed."); return; }
  var clone = null;
  for (var s = app.project.sequences.numSequences - 1; s >= 0; s--) {
    var cand = app.project.sequences[s];
    if (cand.name === originalName + " Copy" || cand.name === originalName + " copy") { clone = cand; break; }
  }
  if (!clone) { alert("Clone created but not found by name - stopping. Your original sequence is unchanged."); return; }
  clone.name = originalName + " + B-roll";
  app.project.openSequence(clone.sequenceID);
  var seq = app.project.activeSequence;

  function findBin(name) {
    var root = app.project.rootItem;
    for (var i = 0; i < root.children.numItems; i++) {
      var c = root.children[i];
      if (c.type === ProjectItemType.BIN && c.name === name) return c;
    }
    return root.createBin(name);
  }
  var bin = findBin(BIN_NAME);
  function findItem(item, path) {
    for (var i = 0; i < item.children.numItems; i++) {
      var c = item.children[i];
      if (c.type === ProjectItemType.BIN) { var r = findItem(c, path); if (r) return r; }
      else if (c.getMediaPath && c.getMediaPath() === path) return c;
    }
    return null;
  }
  function getItem(path) {
    var it = findItem(app.project.rootItem, path);
    if (it) return it;
    if (!new File(path).exists) return null;
    app.project.importFiles([path], true, bin, false);
    return findItem(bin, path);
  }
  var placed = 0, skipped = [];
  for (var k = 0; k < PLAN.placements.length; k++) {
    var p = PLAN.placements[k];
    var trackIndex = (p.track || 2) - 1;
    if (seq.videoTracks.numTracks <= trackIndex) { skipped.push("#" + p.n + ": sequence has no V" + (trackIndex + 1) + " - add a video track and rerun"); continue; }
    var item = getItem(p.path);
    if (!item) { skipped.push("#" + p.n + ": file not found " + p.path); continue; }
    var tIn = new Time(); tIn.seconds = p.src_in;
    var tOut = new Time(); tOut.seconds = p.src_in + p.duration;
    var sub = item.createSubClip("BR" + p.n + " " + item.name, tIn.ticks, tOut.ticks, 0, 1, 0);
    if (!sub) { skipped.push("#" + p.n + ": could not create subclip"); continue; }
    sub.moveBin(bin);
    var at = new Time(); at.seconds = p.at;
    seq.videoTracks[trackIndex].overwriteClip(sub, at.seconds);
    placed++;
    log("Placed #" + p.n + " at " + p.at + "s");
  }
  alert("B-roll placed: " + placed + " of " + PLAN.placements.length + " on sequence \"" + seq.name + "\"." +
        (skipped.length ? "\nSkipped:\n" + skipped.join("\n") : "") +
        "\nYour original sequence \"" + originalName + "\" was not changed.");
})();
"""


def cmd_export(a):
    con, p = connect(a.library)
    plan = load_plan(a.plan)
    res, clips = check_plan(con, plan)
    if res["errors"] and not a.force:
        die("Plan has errors - fix them (or pass --force).", errors=res["errors"])
    fps = float(a.fps or plan.get("fps") or 25)
    fps = min(NTSC, key=lambda k: abs(k - fps)) if any(abs(k - fps) < 0.02 for k in NTSC) else fps
    w, h = int(a.width or plan.get("width") or 1920), int(a.height or plan.get("height") or 1080)
    outdir = Path(a.output).expanduser() if a.output else p["exports"]
    outdir.mkdir(parents=True, exist_ok=True)
    stem = re.sub(r"[^A-Za-z0-9 _-]+", "", plan.get("project", "video")).strip().replace(" ", "_") or "video"
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M")
    written = []
    kinds = {"xml", "jsx", "csv"} if a.to == "all" else {a.to}
    pl = sorted(plan["placements"], key=lambda x: float(x["at"]))
    if "xml" in kinds:
        f = outdir / f"{stem}_broll_{stamp}.xml"
        f.write_text(build_xml(plan, clips, fps, w, h), encoding="utf-8")
        written.append(str(f))
    if "jsx" in kinds:
        data = {"placements": [{"n": x.get("n", i), "at": float(x["at"]), "duration": float(x["duration"]),
                                "src_in": float(x.get("src_in", 0)), "track": int(x.get("track", 2)),
                                "path": clips[x["clip_id"]]["abs_path"]} for i, x in enumerate(pl, 1)]}
        f = outdir / f"{stem}_place_broll_{stamp}.jsx"
        f.write_text(JSX_TEMPLATE.replace("__PLAN__", json.dumps(data, indent=2)), encoding="utf-8")
        written.append(str(f))
    if "csv" in kinds:
        f = outdir / f"{stem}_broll_sheet_{stamp}.csv"
        with open(f, "w", newline="", encoding="utf-8") as fh:
            wr = csv.writer(fh)
            wr.writerow(["#", "timeline_in", "timeline_out", "duration_s", "clip", "source_in", "source_out",
                         "what_is_said", "why_this_clip", "file_path"])
            for i, x in enumerate(pl, 1):
                r = clips[x["clip_id"]]
                fpi = int(round(fps))

                def tc(s):
                    n = fr(s, fps)
                    return f"{n // (fpi * 3600):02d}:{n // (fpi * 60) % 60:02d}:{n // fpi % 60:02d}:{n % fpi:02d}"
                at, d, si = float(x["at"]), float(x["duration"]), float(x.get("src_in", 0))
                wr.writerow([x.get("n", i), tc(at), tc(at + d), round(d, 2), r["filename"], round(si, 2),
                             round(si + d, 2), x.get("says", ""), x.get("why", ""), r["abs_path"]])
        written.append(str(f))
    out({"ok": True, "written": written, "fps": fps, "frame_size": f"{w}x{h}",
         "warnings": res["warnings"], "info": res["info"],
         "how_to_use": {
             "xml": "FCP7 XML (xmeml). Premiere Pro: File > Import the .xml. DaVinci Resolve: File > Import > "
                    "Timeline. It opens as a NEW sequence / timeline (main video on V1/A1 if main_video was set, "
                    "B-roll on V2 with no audio, markers on every placement). Your existing sequences are "
                    "untouched; copy V2 into your real edit or finish in the new sequence. Final Cut Pro needs "
                    "the file converted to FCPXML first; CapCut cannot import it (use the .csv).",
             "jsx": "Premiere Pro only, experimental ExtendScript: clones your active sequence and places "
                    "video-only B-roll on the clone.",
             "csv": "Human-readable placement sheet. Works with every editing app: place the clips by hand from it."}})


def cmd_used(a):
    con, _ = connect(a.library)
    plan = load_plan(a.plan)
    proj = a.project or plan.get("project", "untitled")
    ts = now()
    n = 0
    for x in plan["placements"]:
        if con.execute("SELECT 1 FROM clips WHERE id=?", (x.get("clip_id"),)).fetchone():
            con.execute("INSERT INTO usage(clip_id,project,used_at,src_in,src_out,at) VALUES(?,?,?,?,?,?)",
                        (x["clip_id"], proj, ts, x.get("src_in"), float(x.get("src_in", 0)) + float(x["duration"]), x["at"]))
            con.execute("UPDATE clips SET use_count=use_count+1, last_used=? WHERE id=?", (ts, x["clip_id"]))
            n += 1
    con.commit()
    out({"ok": True, "recorded": n, "project": proj})


def cmd_backup(a):
    con, p = connect(a.library)
    data = {"version": VERSION, "schema_version": SCHEMA_VERSION, "exported_at": now(),
            "roots": [dict(r) for r in con.execute("SELECT * FROM roots")],
            "clips": [row_dict(r) for r in con.execute("SELECT * FROM clips ORDER BY rel_path")],
            "usage": [dict(r) for r in con.execute("SELECT * FROM usage")]}
    f = Path(a.output).expanduser() if a.output else p["backups"] / f"library_{_dt.datetime.now():%Y%m%d-%H%M}.json"
    f.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    out({"ok": True, "written": str(f), "clips": len(data["clips"])})


def cmd_init(a):
    con, p = connect(a.library)
    out({"ok": True, "library": str(p["root"]), "db": str(p["db"]), "concepts": str(p["concepts"]),
         "version": VERSION})


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Personal B-Roll Library")
    ap.add_argument("--library", default=DEFAULT_LIBRARY, help=f"library folder (default {DEFAULT_LIBRARY}, or $BROLL_LIBRARY)")
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("init").set_defaults(fn=cmd_init)
    s = sp.add_parser("scan"); s.add_argument("folder"); s.add_argument("--label"); s.set_defaults(fn=cmd_scan)
    s = sp.add_parser("status"); s.add_argument("--limit", type=int, default=20); s.set_defaults(fn=cmd_status)
    sp.add_parser("roots").set_defaults(fn=cmd_roots)
    s = sp.add_parser("relink"); s.add_argument("--from", dest="old", required=True); s.add_argument("--to", dest="new", required=True); s.set_defaults(fn=cmd_relink)
    s = sp.add_parser("extract"); s.add_argument("--id", nargs="+"); s.add_argument("--pending", action="store_true")
    s.add_argument("--limit", type=int, default=10); s.add_argument("--frames", type=int); s.set_defaults(fn=cmd_extract)
    s = sp.add_parser("ingest"); s.add_argument("files", nargs="*"); s.add_argument("--dir"); s.set_defaults(fn=cmd_ingest)
    s = sp.add_parser("show"); s.add_argument("ids", nargs="+"); s.set_defaults(fn=cmd_show)
    s = sp.add_parser("dump"); s.add_argument("--full", action="store_true"); s.set_defaults(fn=cmd_dump)
    s = sp.add_parser("search"); s.add_argument("query"); s.add_argument("--expand", help="comma-separated extra visual terms")
    s.add_argument("--limit", type=int, default=12); s.add_argument("--orientation", choices=["horizontal", "vertical", "square"])
    s.add_argument("--min-quality", type=int); s.add_argument("--speaking", choices=SPEAKING); s.add_argument("--shot")
    s.add_argument("--min-duration", type=float); s.add_argument("--exclude", help="comma-separated clip ids")
    s.add_argument("--fresh", action="store_true", help="down-rank clips used often in past videos"); s.set_defaults(fn=cmd_search)
    s = sp.add_parser("transcript"); s.add_argument("file"); s.add_argument("--wpm", type=float, default=150)
    s.add_argument("--group", type=float, default=0, help="merge segments to about N seconds"); s.add_argument("-o", "--output"); s.set_defaults(fn=cmd_transcript)
    s = sp.add_parser("plan-check"); s.add_argument("plan"); s.set_defaults(fn=cmd_plan_check)
    s = sp.add_parser("export"); s.add_argument("plan"); s.add_argument("--to", choices=["xml", "jsx", "csv", "all"], default="all")
    s.add_argument("--fps", type=float); s.add_argument("--width", type=int); s.add_argument("--height", type=int)
    s.add_argument("-o", "--output"); s.add_argument("--force", action="store_true"); s.set_defaults(fn=cmd_export)
    s = sp.add_parser("used"); s.add_argument("plan"); s.add_argument("--project"); s.set_defaults(fn=cmd_used)
    s = sp.add_parser("backup"); s.add_argument("-o", "--output"); s.set_defaults(fn=cmd_backup)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
