#!/usr/bin/env python3
"""Editors.Hub: your own local Home page and review page for video edits. Runs on Mac and Windows.

Everything is plain Python (3.9+, no packages to install). ffmpeg is optional (used for thumbnails).

    studio.py open [<video>] [--browser]        start Home if needed, print its (or a review page's) address
    studio.py serve [--port N]                  run Home in this window (Ctrl+C stops it)
    studio.py stop                              stop a Home started by `open`
    studio.py status [--json]                   styles and videos, and where each one stands
    studio.py new-project "<client>" [--contact "..."] [--website "..."] [--about "..."] [--brand "..."]
    studio.py project-add <project> <file> [--section brandbook|logos|fonts|files]   add a client's brand file
    studio.py new-style "<name>" [--format short|long] [--link <url>]... [--notes "..."]   a reusable editing look, with no client in it
    studio.py new-video <style> "<name>" --project <project> [--raw <file>]... [--brief "..."]
    studio.py new-video <style> "<name>" --training [--raw <file>]...   a video to train the style, for no client
    studio.py context <video>                   the files to read before editing: the client's brand, then the style
    studio.py export-project <project> <folder>  copy a client, with their brand files and videos, into <folder>
    studio.py import-project <folder or .zip>   bring a saved client into this studio
    studio.py export-style <style> <folder>     copy a style into <folder> (a drive, a cloud folder) to take elsewhere
    studio.py import-style <folder or .zip> [--shared]   bring an exported style into this studio
    studio.py rename-style <style> "<new name>" / duplicate-style <style> / delete-style <style>
    studio.py deleted-styles / restore-style <name from deleted-styles>   (deleting only moves to Recently deleted)
    studio.py online-styles                     what's in the online Shared folder (a private GitHub repo)
    studio.py upload-style <style>              put a style in the online Shared folder (or update it there)
    studio.py download-style <tag> [--shared]   bring a style from the online Shared folder into this studio
    studio.py share-style <style>               move a style to the Shared folder: everyone signed in sees it
    studio.py unshare-style <style>             back to its maker's private styles
    studio.py update <video> "<plain words>" [--snapshot <image or video>] [--at S]   show progress in the Live tab
    studio.py ask-render <video> [--note "..."] [--size WxH] [--fps N] [--duration S]   open the render popup, wait for the choice
    studio.py finish-render <video> <file> [--note "..."]   encode with the chosen settings and add it as the next draft
    studio.py broll-ask <video>                 when an edit or next draft starts: opens the b-roll popup if needed, waits, says what to do
    studio.py broll-plan <video> <plan.json> [--change]   opens the picker with 3 or 4 options per part, waits for the picks
    studio.py broll-record <video> <plan.json> [--change]   notes the clips you chose by yourself, so they can be changed later
    studio.py broll-status <video>              what's picked for each part, with the files
    studio.py set-style <video> <style>         a client's video follows another style from its next draft
    studio.py add-draft <video> <file> [--note "..."]      a new version for review (v1, v2, ...)
    studio.py notes <video> [--all]             the review notes on the latest draft, in time order
    studio.py done <video> <note-id>...         mark notes fixed
    studio.py set-status <video> <status>       editing | in review | changes | approved | delivered
    studio.py wait <video> [--timeout S]        listen for "Submit feedback to Claude" on the review page (the page
                                                shows Claude as listening); prints the notes sent, then stops
    studio.py reply <video> <note-id> "<what you did>" [--not-fixed] [--lesson "<editing rule>"] [--client-lesson "<brand rule>"]
                                                answer a note on the page (and mark it fixed); --lesson also adds an
                                                editing rule to the style's STYLE.md, --client-lesson a rule about
                                                this client to the project's BRAND.md ("Saved to <name>")
    studio.py live <video> [--project <dir>] [--stop]    the HyperFrames live preview shown on the review page
    studio.py skills [list]                     the Claude skills packed in Editors.Hub, and their state here
    studio.py skills install [<name>...]        install missing skills into Claude now (Home also does it on start)
    studio.py skills skip <name>...             don't install these on this computer
    studio.py skills add <folder>...            pack more skills in (a skill folder, or a folder of skills)
    studio.py skills remove <name>              take a skill out of the pack (it stays installed on this computer)
    studio.py profile [status]                  the creator-setup profile packed in the studio, and the one here
    studio.py profile pack                      pack this computer's creator-setup profile (brand, fonts, notes)
    studio.py profile restore [--replace]       put the packed profile in place here and fill the skills from it
    studio.py codes                             sign-up / sign-in codes waiting (they also go to the owner's email)
    studio.py users                             the accounts: owner, editors, reviewers
    studio.py user-role <email> <editor|reviewer>    change someone's role
    studio.py user-remove <email>               remove an account (signs them out everywhere)
    studio.py rename-user <email> <new username>   change a username everywhere it shows
    studio.py setup [--check]                   check the tools the skills need and install what's missing
                                                (Home also does this every time it starts)

On Mac run it as `python3 studio.py ...`, on Windows as `py studio.py ...`.
"""
import argparse
import contextlib
import hashlib
import json
import mimetypes
import os
import re
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
import zipfile
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import auth
import hubsetup
import keys

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
DATA = ROOT / "data"
SETTINGS = DATA / "settings.json"
PIDFILE = DATA / "server.pid"
DEFAULT_PORT = 48100
STATUSES = ["editing", "in review", "changes", "approved", "delivered"]
WINDOWS = os.name == "nt"
LOCK = threading.RLock()
OWNER_EMAIL = ""  # the owner, the only account that can do admin things, is whoever sets up this computer's studio first
# a studio from before that named its owner in the code; while that account doesn't exist here, it's still open to claim
OLD_DEFAULT_OWNER = "f02e69672afef314c6fb7041a0d7e06cc440a8ab5d5073a27c8b951756fe8516"
APP_VERSION = (Path(__file__).resolve().parent / "VERSION").read_text(encoding="utf-8").strip()
import approval  # noqa: E402

# The skills packed in Editors.Hub (skills/<name>/SKILL.md) and where Claude Code reads skills on any computer.
SKILLS = ROOT / "skills"
CLAUDE_SKILLS = Path(os.environ.get("EDITORS_HUB_SKILLS_DIR") or Path.home() / ".claude" / "skills")
DEVICE = CLAUDE_SKILLS.parent / "editors-hub-device.json"  # this computer only: skills not to install here
# creator-setup's shared answers (brand, fonts, notes): packed in the studio, put in place on a computer that has none.
PROFILE_PACK = ROOT / "profile"
PROFILE_DIR = CLAUDE_SKILLS.parent / "creator-profile"
SKILL_MARKER = ".editors-hub.json"
SKILL_JUNK = {".DS_Store", "Thumbs.db", "desktop.ini", "__pycache__", SKILL_MARKER}
HUB_DIR_TOKEN = "@@EDITORS_HUB_DIR@@"

# Browsers play H.264 .mov/.m4v files when they are labelled as mp4.
MEDIA_TYPES = {".mp4": "video/mp4", ".mov": "video/mp4", ".m4v": "video/mp4", ".webm": "video/webm",
               ".mkv": "video/x-matroska", ".jpg": "image/jpeg", ".png": "image/png",
               ".wav": "audio/wav", ".mp3": "audio/mpeg", ".m4a": "audio/mp4"}


class StudioError(Exception):
    status = 400


class NotFound(StudioError):
    status = 404


# ---------------------------------------------------------------- files and settings

def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:60].strip("-") or "untitled"


def safe_filename(name):
    """A file name that is valid on both Mac and Windows."""
    name = re.split(r"[\\/]", name)[-1]
    name = re.sub(r'[<>:"|?*\x00-\x1f]+', "_", name).strip(" .")
    stem = name.split(".")[0].upper()
    if stem in {"CON", "PRN", "AUX", "NUL"} or re.fullmatch(r"(COM|LPT)\d", stem):
        name = "_" + name
    return name[:180] or "file"


def unique_path(folder, name):
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    stem, ext, n = path.stem, path.suffix, 2
    while path.exists():
        path = folder / f"{stem} ({n}){ext}"
        n += 1
    return path


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    for attempt in range(20):  # Windows refuses the swap while another process is reading the file
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            time.sleep(0.05)
    os.replace(tmp, path)


def settings():
    with LOCK:
        s = read_json(SETTINGS, {}) or {}
        defaults = {"studio_name": "Editors.Hub", "your_name": "", "library": str(ROOT / "library"),
                    "port": DEFAULT_PORT, "owner_email": OWNER_EMAIL, "lan": False}
        if any(k not in s for k in defaults) or not s.get("token"):
            s = {**defaults, **s, "token": s.get("token") or secrets.token_urlsafe(24)}
            write_json(SETTINGS, s)
        return s


def wifi_on():
    return bool(settings().get("lan")) and approval.open_to_others(DATA)


def update_settings(changes):
    with LOCK:
        s = settings()
        if "lan" in changes:
            if changes["lan"] and not approval.open_to_others(DATA):
                raise StudioError(auth.ALONE)
            s["lan"] = bool(changes["lan"])
        if "library_confirmed" in changes:
            s["library_confirmed"] = bool(changes["library_confirmed"])
        for key in ("studio_name", "your_name", "library"):
            if key not in changes:
                continue
            value = str(changes[key]).strip()
            if key == "library":
                if not value:
                    raise StudioError("the library folder can't be empty")
                value = str(Path(value).expanduser().resolve())
                try:
                    for sub in (SHARED, PRIVATE):
                        Path(value, sub).mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    raise StudioError(f"can't use that folder: {e}")
            if key == "studio_name" and not value:
                value = "Editors.Hub"
            s[key] = value
        write_json(SETTINGS, s)
        return s


# The library keeps each person's styles private until they share them:
#   shared/<style>/              everyone signed in sees it (and the older styles/<style>/ layout counts as shared)
#   private/<username>/<style>/  only the person who made it
SHARED, PRIVATE, OLD_STYLES = "shared", "private", "styles"


def library():
    lib = Path(settings()["library"]).expanduser()
    for sub in (SHARED, PRIVATE):
        (lib / sub).mkdir(parents=True, exist_ok=True)
    return lib


def reveal(path):
    """Open a folder in Finder (Mac) or File Explorer (Windows)."""
    path = str(path)
    if WINDOWS:
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def make_thumb(video, out):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return
    for seek in ("1", "0"):
        try:
            subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-ss", seek, "-i", str(video), "-frames:v", "1",
                            "-vf", "scale=640:-2", str(out)], timeout=60, capture_output=True)
        except (OSError, subprocess.TimeoutExpired):
            return
        if Path(out).exists():
            return


# ---------------------------------------------------------------- styles

def style_dirs():
    lib = library()
    out = {}
    for d in [*lib.glob(f"{SHARED}/*"), *lib.glob(f"{OLD_STYLES}/*"), *lib.glob(f"{PRIVATE}/*/*")]:
        # a hidden folder is a style still being copied, imported or renamed: not a style yet
        if not d.name.startswith(".") and not d.parent.name.startswith(".") and (d / "style.json").exists():
            out.setdefault(d.name, d)
    return out


def style_meta(d):
    meta = read_json(d / "style.json", {}) or {}
    shared = not (d.parent.parent.name == PRIVATE and d.parent.parent.parent == library())
    return {**meta, "id": d.name, "folder": str(d), "shared": shared}


def can_see(meta, user):
    """None is this computer itself (Claude's commands): it sees everything. A person sees shared styles and their own."""
    return user is None or meta["shared"] or meta.get("maker") == user["email"]


def style_dir(style_id, user=None):
    d = style_dirs().get(style_id)
    if not d or not can_see(style_meta(d), user):
        names = ", ".join(s["id"] for s in list_styles(user)) or "none yet"
        raise NotFound(f"no style '{style_id}' (styles: {names})")
    return d


def list_styles(user=None):
    out = [style_meta(d) for d in style_dirs().values()]
    return sorted((m for m in out if can_see(m, user)), key=lambda m: m["name"].lower())


def _maker(user):
    if user:
        return user["email"], user["username"]
    owner = accounts().users().get(settings()["owner_email"])  # Claude's commands make styles for the owner
    return settings()["owner_email"], owner["username"] if owner else "owner"


STYLE_FORMATS = {"short": "Short-form", "long": "Long-form"}


def check_style_format(value):
    value = str(value or "").strip()
    if value and value not in STYLE_FORMATS:
        raise StudioError("A style's format is short or long.")
    return value


def create_style(name, client="", notes="", user=None, format="", links=()):
    name = name.strip()
    if not name:
        raise StudioError("a style needs a name")
    format = check_style_format(format)
    links = [str(x).strip() for x in links if str(x).strip()]
    for link in links:
        if not re.match(r"^https?://\S+$", link):
            raise StudioError(f"A reference link has to start with http:// or https://: {link[:80]}")
    email, username = _maker(user)
    with LOCK:
        taken = style_dirs()
        base = sid = slugify(name)
        n = 2
        while sid in taken:
            sid, n = f"{base}-{n}", n + 1
        d = library() / PRIVATE / username / sid
        for sub in ("videos", "brief", *(folders[0] for _, _, folders in SECTIONS)):
            (d / sub).mkdir(parents=True, exist_ok=True)
        write_json(d / "style.json", {"name": name, "client": client.strip(), "notes": notes.strip(), "format": format,
                                      "created": now(), "maker": email, "maker_name": username})
        rules = notes.strip() or "(The rules of this style: fonts, colours, captions, pacing, B-roll, music, sound.)"
        client_line = f"Client: {client.strip()}\n\n" if client.strip() else ""
        format_line = f"Format: {STYLE_FORMATS[format]}\n\n" if format else ""
        link_lines = "".join(f"- {link}\n" for link in links)
        (d / "STYLE.md").write_text(f"# {name}\n\n{client_line}{format_line}## How this style looks\n\n"
                                    f"{rules}\n\n## References\n\nPut reference videos, fonts, LUTs and project "
                                    f"files in references/.\n{chr(10) + link_lines if links else ''}", encoding="utf-8")
    return {"id": sid, "name": name, "folder": str(d), "shared": False}


def share_style(style_id, share=True, user=None):
    """Move a style into the Shared folder (everyone sees it) or back to its maker's private styles."""
    with LOCK:
        d = style_dir(style_id, user)
        meta = style_meta(d)
        owner = user is None or user["role"] == "owner"
        mine = user is None or meta.get("maker") == user["email"]
        if share and not mine:
            raise auth.Forbidden("Only the person who made a style can share it.")
        if not share and not (mine or owner):
            raise auth.Forbidden("Only the person who made it, or the owner, can unshare a style.")
        if meta["shared"] == share:
            return meta
        maker_name = meta.get("maker_name") or _maker(None)[1]
        dest = library() / SHARED / style_id if share else library() / PRIVATE / maker_name / style_id
        if dest.exists():
            raise StudioError(f"{dest} is already there")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(d), str(dest))
        data = read_json(dest / "style.json", {}) or {}
        data.update(shared_at=now() if share else None, shared_by=(user or {}).get("username", maker_name) if share else None)
        if not data.get("maker"):  # a style from before sharing existed belongs to the owner
            data["maker"], data["maker_name"] = _maker(None)
        write_json(dest / "style.json", data)
    return style_meta(dest)


# ---------------------------------------------------------------- renaming, duplicating, deleting a style

TRASH = ".trash"  # library/.trash/<when>-<style>: deleted styles wait here, with their videos, until restored


def can_manage(meta, user):
    return user is None or user["role"] == "owner" or meta.get("maker") == user["email"]


def rename_style(style_id, name, user=None):
    name = str(name or "").strip()
    if not name:
        raise StudioError("A style needs a name.")
    sdir = style_dir(style_id, user)
    if not can_manage(style_meta(sdir), user):
        raise auth.Forbidden("Only the person who made this style, or the owner, can rename it.")
    with LOCK:
        data = read_json(sdir / "style.json", {}) or {}
        data["name"] = name[:120]
        write_json(sdir / "style.json", data)
    return style_meta(sdir)


def duplicate_style(style_id, user=None):
    """A private copy for the person asking, with everything in it (on an APFS drive the copy shares space)."""
    sdir = can_take_style(style_id, user)
    meta = style_meta(sdir)
    email, username = _maker(user)
    with LOCK:
        taken = style_dirs()
        n = 2
        sid = f"{style_id}-copy"
        while sid in taken:
            sid, n = f"{style_id}-copy-{n}", n + 1
        dest = library() / PRIVATE / username / sid
        dest.parent.mkdir(parents=True, exist_ok=True)
    files = transfer_files(sdir)

    def work(job):
        job["total_bytes"] = sum(f.stat().st_size for _, f in files)
        job["stage"] = "Copying the style and its videos"
        tmp = dest.with_name(f".{sid}.copying")
        if tmp.exists():
            shutil.rmtree(tmp)
        try:
            if sys.platform == "darwin" and subprocess.run(["cp", "-cR", str(sdir), str(tmp)], capture_output=True).returncode == 0:
                for junk in [*tmp.rglob(".video.lock"), *tmp.rglob(".claude-wait.json")]:
                    junk.unlink(missing_ok=True)
                job["done_bytes"] = job["total_bytes"]
            else:
                copy_files(files, tmp, job)
            check_stop(job)
        except BaseException:
            shutil.rmtree(tmp, ignore_errors=True)
            raise
        with LOCK:
            taken_videos = set(video_dirs())
            for vdir in sorted((tmp / "videos").glob("*")) if (tmp / "videos").is_dir() else []:
                new, k = f"{vdir.name}-copy", 2
                while new in taken_videos:
                    new, k = f"{vdir.name}-copy-{k}", k + 1
                os.replace(vdir, vdir.with_name(new))
                taken_videos.add(new)
            data = read_json(tmp / "style.json", {}) or {}
            data.update(name=f"{meta['name']} (copy)", maker=email, maker_name=username, created=now(),
                        copied_from=style_id, shared_at=None, shared_by=None)
            write_json(tmp / "style.json", data)
            os.replace(tmp, dest)
        return {"id": sid, "name": data["name"]}
    return start_job("duplicate", f"Duplicating {meta['name']}", user, work, style=style_id)


def delete_style(style_id, user=None):
    """Moves the style, with its videos, into Recently deleted. Nothing is erased; it can be restored."""
    sdir = style_dir(style_id, user)
    meta = style_meta(sdir)
    if not can_manage(meta, user):
        raise auth.Forbidden("Only the person who made this style, or the owner, can delete it.")
    for vdir in sdir.glob("videos/*"):
        if (vdir / "video.json").exists() and claude_status(vdir)["listening"]:
            raise StudioError("Claude is working on a video in this style right now. Try again when it's done.")
        stop_live(vdir.name) if (read_json(vdir / "video.json", {}) or {}).get("live") else None
    with LOCK:
        trash = library() / TRASH
        trash.mkdir(exist_ok=True)
        dest = trash / f"{time.strftime('%Y%m%d-%H%M%S')}-{style_id}"
        shutil.move(str(sdir), str(dest))
        write_json(dest / ".deleted.json", {"id": style_id, "name": meta["name"], "shared": meta["shared"],
                                            "maker": meta.get("maker"), "maker_name": meta.get("maker_name"),
                                            "deleted_by": (user or {}).get("email") or settings()["owner_email"],
                                            "deleted": now()})
    return {"id": style_id, "name": meta["name"], "trash": dest.name}


def list_trash(user=None):
    out = []
    trash = library() / TRASH
    for d in sorted(trash.glob("*"), reverse=True) if trash.is_dir() else []:
        info = read_json(d / ".deleted.json")
        if not info:
            continue
        if user is not None and user["role"] != "owner" and user["email"] not in (info.get("maker"), info.get("deleted_by")):
            continue
        videos = len(list(d.glob("videos/*/video.json")))
        out.append({**info, "trash": d.name, "videos": videos})
    return out


def erase_deleted(trash_name, user=None):
    """Delete forever: only for something already in Recently deleted, and only by the person's own click on the page.
    The note saying what it is goes last, so anything that can't be erased stays listed and can be tried again."""
    root = library() / TRASH
    d = root / str(trash_name)
    info = read_json(d / ".deleted.json") if d.parent == root and d.name not in ("", ".", "..") and d.is_dir() else None
    if not info or (user is not None and user["role"] != "owner" and user["email"] not in (info.get("maker"), info.get("deleted_by"))):
        raise NotFound("That isn't in Recently deleted.")
    with LOCK:
        try:
            for item in d.iterdir():
                if item.name != ".deleted.json":
                    shutil.rmtree(item) if item.is_dir() else item.unlink()
            shutil.rmtree(d)
        except OSError as e:
            raise StudioError(f"Some of {info['name']} couldn't be erased, because a file is in use or protected: {getattr(e, 'filename', '') or e}. Close it and try again.")
    return {"name": info["name"]}


def restore_style(trash_name, user=None):
    d = (library() / TRASH / trash_name)
    info = read_json(d / ".deleted.json") if d.parent == library() / TRASH and d.is_dir() else None
    if not info or (user is not None and user["role"] != "owner" and user["email"] not in (info.get("maker"), info.get("deleted_by"))):
        raise NotFound("That isn't in Recently deleted.")
    is_project = info.get("kind") == "project"
    with LOCK:
        sid, n = info["id"], 2
        taken = project_dirs() if is_project else style_dirs()
        while sid in taken:
            sid, n = f"{info['id']}-{n}", n + 1
        dest = library() / PROJECTS / sid if is_project else library() / SHARED / sid if info.get("shared") else \
            library() / PRIVATE / (info.get("maker_name") or _maker(None)[1]) / sid
        dest.parent.mkdir(parents=True, exist_ok=True)
        taken_videos = set(video_dirs())
        for vdir in sorted((d / "videos").glob("*")):  # a video made since with the same name keeps its own
            if vdir.name in taken_videos:
                os.replace(vdir, vdir.with_name(f"{vdir.name}-restored"))
        (d / ".deleted.json").unlink()
        shutil.move(str(d), str(dest))
    return {**project_meta(dest), "kind": "project"} if is_project else style_meta(dest)


# ---------------------------------------------------------------- projects: one client each, kept apart from styles

# library/projects/<project>/ holds a client's details (project.json), brand guidelines (BRAND.md), brand files and
# videos. Everyone who makes videos sees every project; only the person who made one, or the owner, can change it.
PROJECTS = "projects"
PROJECT_SECTIONS = [
    ("brandbook", "Brandbook"),
    ("logos", "Logos"),
    ("fonts", "Fonts"),
    ("files", "Other files"),
]
PROJECT_INFO = ("contact", "website", "about")
SORT_PROJECT_FILE = [  # where a client's file goes when no section is chosen
    ({".ttf", ".otf", ".woff", ".woff2"}, "fonts"),
    ({".pdf", ".ppt", ".pptx", ".key", ".doc", ".docx"}, "brandbook"),
    ({".svg", ".ai", ".eps", ".png", ".jpg", ".jpeg", ".gif", ".webp"}, "logos"),
]


def project_dirs():
    root = library() / PROJECTS
    if not root.is_dir():
        return {}
    return {d.name: d for d in root.iterdir() if not d.name.startswith(".") and (d / "project.json").exists()}


def project_meta(d):
    return {**(read_json(d / "project.json", {}) or {}), "id": d.name, "folder": str(d)}


def project_dir(project_id):
    d = project_dirs().get(project_id)
    if not d:
        names = ", ".join(sorted(project_dirs())) or "none yet"
        raise NotFound(f"no project '{project_id}' (projects: {names})")
    return d


def list_projects():
    return sorted((project_meta(d) for d in project_dirs().values()), key=lambda m: m["name"].lower())


def create_project(name, contact="", website="", about="", brand="", user=None):
    name = str(name or "").strip()
    if not name:
        raise StudioError("A project needs a client's name.")
    email, username = _maker(user)
    with LOCK:
        taken = project_dirs()
        base = pid = slugify(name)
        n = 2
        while pid in taken:
            pid, n = f"{base}-{n}", n + 1
        d = library() / PROJECTS / pid
        for sub in ("videos", *(sec for sec, _ in PROJECT_SECTIONS)):
            (d / sub).mkdir(parents=True, exist_ok=True)
        write_json(d / "project.json", {"name": name[:120], "contact": str(contact).strip(), "website": str(website).strip(),
                                        "about": str(about).strip(), "created": now(), "maker": email, "maker_name": username})
        body = str(brand).strip() or "(Colours, fonts, logo use, tone of voice, and anything the client never wants.)"
        (d / "BRAND.md").write_text(f"# {name} brand guidelines\n\n{body}\n", encoding="utf-8")
    return project_meta(d)


def can_edit_project(meta, user):
    return user is None or user["role"] == "owner" or meta.get("maker") == user["email"]


def project_files(d, section):
    if section not in {sec for sec, _ in PROJECT_SECTIONS}:
        raise NotFound("no such section")
    folder = d / section
    items = []
    for f in sorted(folder.rglob("*"), key=lambda f: f.name.lower()) if folder.is_dir() else []:
        if f.is_file() and not f.name.startswith("."):
            items.append({"name": f.name, "file": f.relative_to(d).as_posix(), "kind": kind_of(f.name),
                          "size": f.stat().st_size, "modified": f.stat().st_mtime})
    return items


def project_page(project_id, user=None):
    d = project_dir(project_id)
    meta = project_meta(d)
    videos = []
    dirs, styles, projects = video_dirs(user), style_dirs(), project_dirs()
    for vid, vdir in dirs.items():
        if vdir.parent.parent == d:
            try:
                videos.append(video_summary(load_video(vid, dirs), styles, projects))
            except StudioError:
                pass
    videos.sort(key=lambda v: v["updated"], reverse=True)
    guide = d / "BRAND.md"
    return {**meta, "videos": videos, "brand": guide.read_text(encoding="utf-8", errors="replace") if guide.exists() else "",
            "rules": learned_rules_of(d, "BRAND.md"),
            "counts": {sec: len(project_files(d, sec)) for sec, _ in PROJECT_SECTIONS},
            "sections": [{"id": sec, "label": label} for sec, label in PROJECT_SECTIONS],
            "can_edit": can_edit_project(meta, user),
            "claude_prompt": (f'In Editors.Hub, work for the client "{meta["name"]}" (project id {project_id}). Read their '
                              f'brand guidelines and brand files first: {guide}. Their brand decides colours, fonts and '
                              f'logos; the style I pick for each video decides the editing.')}


def save_project(project_id, changes, user=None):
    d = project_dir(project_id)
    meta = project_meta(d)
    if not can_edit_project(meta, user):
        raise auth.Forbidden("Only the person who made this project, or the owner, can change it.")
    with LOCK:
        data = read_json(d / "project.json", {}) or {}
        if "name" in changes:
            name = str(changes["name"]).strip()
            if not name:
                raise StudioError("A project needs a client's name.")
            data["name"] = name[:120]
        for k in PROJECT_INFO:
            if k in changes:
                data[k] = str(changes[k]).strip()
        write_json(d / "project.json", data)
        if "brand" in changes:
            (d / "BRAND.md").write_text(str(changes["brand"]), encoding="utf-8")
    return project_page(project_id, user)


def project_section_for(name, section="auto"):
    if section == "auto":
        ext = Path(name).suffix.lower()
        return next((sec for exts, sec in SORT_PROJECT_FILE if ext in exts), "files")
    if section not in {sec for sec, _ in PROJECT_SECTIONS}:
        raise StudioError("unknown section")
    return section


def add_project_file(project_id, src, section="auto"):
    src = Path(src)
    if not src.is_file():
        raise StudioError(f"no file at {src}")
    d = project_dir(project_id)
    section = project_section_for(src.name, section)
    (d / section).mkdir(exist_ok=True)
    dest = unique_path(d / section, safe_filename(src.name))
    shutil.copy2(src, dest)
    return section, dest


def delete_project(project_id, user=None):
    """Moves the client, with their brand files and videos, into Recently deleted. Nothing is erased."""
    d = project_dir(project_id)
    meta = project_meta(d)
    if not can_edit_project(meta, user):
        raise auth.Forbidden("Only the person who made this project, or the owner, can delete it.")
    for vdir in d.glob("videos/*"):
        if (vdir / "video.json").exists() and claude_status(vdir)["listening"]:
            raise StudioError("Claude is working on a video for this client right now. Try again when it's done.")
        stop_live(vdir.name) if (read_json(vdir / "video.json", {}) or {}).get("live") else None
    with LOCK:
        trash = library() / TRASH
        trash.mkdir(exist_ok=True)
        dest = trash / f"{time.strftime('%Y%m%d-%H%M%S')}-{project_id}"
        shutil.move(str(d), str(dest))
        write_json(dest / ".deleted.json", {"kind": "project", "id": project_id, "name": meta["name"], "shared": False,
                                            "maker": meta.get("maker"), "maker_name": meta.get("maker_name"),
                                            "deleted_by": (user or {}).get("email") or settings()["owner_email"],
                                            "deleted": now()})
    return {"id": project_id, "name": meta["name"], "trash": dest.name}


# ---------------------------------------------------------------- the style page: its sections and files

# Each section of a style and the folders it reads (the first is where new files go when none exists yet;
# library/... is where older imported styles keep them).
SECTIONS = [
    ("references", "References", ["references", "library/references"]),
    ("broll", "B-roll", ["broll", "library/broll"]),
    ("graphics", "Graphics", ["graphics", "library/graphics", "library/screens"]),
    ("effects", "Effects", ["effects", "library/effects"]),
    ("transitions", "Transitions", ["transitions", "library/transitions"]),
    ("grades", "Colour grading", ["grades", "library/grades"]),
    ("sfx", "Sound effects", ["sfx", "library/sfx"]),
    ("music", "Music", ["music", "library/music"]),
    ("projects", "Editing files", ["projects", "library/projects"]),
]
KINDS = {"video": {".mp4", ".mov", ".m4v", ".webm", ".mkv"}, "image": {".png", ".jpg", ".jpeg", ".gif", ".webp"},
         "audio": {".wav", ".mp3", ".m4a", ".aac", ".aif", ".aiff", ".flac", ".ogg"}}
SORT_BY_TYPE = [  # where a file dropped on the overview goes
    ({".cube", ".3dl", ".look", ".lut"}, "grades"),
    ({".prproj", ".aep", ".aepx", ".fcpxml", ".xml", ".drp", ".drt", ".mogrt", ".aegraphic", ".ffx", ".capcut"}, "projects"),
    (KINDS["audio"], "music"),
    (KINDS["video"], "broll"),
    (KINDS["image"], "graphics"),
]


def kind_of(name):
    ext = Path(name).suffix.lower()
    return next((k for k, exts in KINDS.items() if ext in exts), "file")


def section_items(sdir, section):
    """A section's items: a clip and its still preview (name.poster.jpg / name.jpg) count as one."""
    folders = next(f for sid, _, f in SECTIONS if sid == section)
    groups = {}
    for rel in folders:
        root = sdir / rel
        if not root.is_dir():
            continue
        for f in root.rglob("*"):
            if not f.is_file() or f.name.startswith(".") or f.suffix.lower() in (".json", ".bak", ".md"):
                continue
            key = str(f.relative_to(sdir).with_suffix("")).removesuffix(".poster")
            groups.setdefault(key, []).append(f)
    items = []
    for files in groups.values():
        files.sort(key=lambda f: ("video", "audio", "image", "file").index(kind_of(f.name)))
        main, rest = files[0], files[1:]
        poster = next((f for f in rest if kind_of(f.name) == "image"), None)
        st = main.stat()
        items.append({"name": main.name, "file": main.relative_to(sdir).as_posix(), "kind": kind_of(main.name),
                      "size": st.st_size, "modified": st.st_mtime,
                      "poster": poster.relative_to(sdir).as_posix() if poster else None,
                      "folder": main.parent.relative_to(sdir).as_posix()})
    return sorted(items, key=lambda i: i["file"].lower())


def section_target(sdir, section):
    folders = next(f for sid, _, f in SECTIONS if sid == section)
    for rel in folders:
        if (sdir / rel).is_dir():
            return sdir / rel
    return sdir / folders[0]


def learned_rules_of(sdir, guide="STYLE.md"):
    try:
        text = (sdir / guide).read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    m = re.search(r"^## Lessons from reviews\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return [line[2:].strip() for line in (m.group(1) if m else "").splitlines() if line.startswith("- ")]


def style_page(style_id, user=None):
    sdir = style_dir(style_id, user)
    meta = style_meta(sdir)
    videos = []
    client_videos = 0  # clients' videos live in their projects; a style's own page shows the videos that train it
    dirs, styles, projects = video_dirs(user), style_dirs(), project_dirs()
    for vid in dirs:
        try:
            v = load_video(vid, dirs)
        except StudioError:
            continue
        if v.get("style") == style_id:
            if v.get("project"):
                client_videos += 1
            else:
                videos.append(video_summary(v, styles, projects))
    videos.sort(key=lambda v: v["updated"], reverse=True)
    finished = []
    for v in videos:
        if v["status"] in ("approved", "delivered"):
            approved = load_video(v["id"]).get("approved") or {}
            finished.append({**v, "at": approved.get("at") or v["updated"]})
    finished.sort(key=lambda v: v["at"], reverse=True)
    brief = ""
    for name in ("brief/BRIEF.md", "BRIEF.md"):
        if (sdir / name).is_file():
            brief = (sdir / name).read_text(encoding="utf-8", errors="replace")
            break
    guide = (sdir / "STYLE.md").read_text(encoding="utf-8", errors="replace") if (sdir / "STYLE.md").exists() else ""
    is_owner = user is None or user["role"] == "owner"
    return {**meta, "videos": videos, "client_videos": client_videos, "rules": learned_rules_of(sdir), "guide": guide, "brief": brief,
            "counts": {sid: len(section_items(sdir, sid)) for sid, _, _ in SECTIONS},
            "sections": [{"id": sid, "label": label} for sid, label, _ in SECTIONS],
            "last_finished": finished[0] if finished else None,
            "can_edit": is_owner or meta.get("maker") == (user or {}).get("email"),
            "mine": user is not None and meta.get("maker") == user["email"],
            "claude_prompt": (f'In Editors.Hub, work in the "{meta["name"]}" style (style id {style_id}). Read its '
                              f'STYLE.md first: {sdir / "STYLE.md"}')}


def browse_style(style_id, rel="", user=None):
    """The Files tab: one folder of the style at a time."""
    sdir = style_dir(style_id, user).resolve()
    target = (sdir / rel).resolve()
    if target != sdir and sdir not in target.parents:
        raise NotFound("no such folder")
    if not target.is_dir():
        raise NotFound("no such folder")
    entries = []
    for f in sorted(target.iterdir(), key=lambda f: (f.is_file(), f.name.lower())):
        if f.name.startswith("."):
            continue
        st = f.stat()
        entries.append({"name": f.name, "path": f.relative_to(sdir).as_posix(), "dir": f.is_dir(),
                        "kind": "folder" if f.is_dir() else kind_of(f.name), "size": 0 if f.is_dir() else st.st_size,
                        "modified": st.st_mtime})
    return {"path": "" if target == sdir else target.relative_to(sdir).as_posix(), "entries": entries[:2000]}


def save_style_text(style_id, changes, user=None):
    sdir = style_dir(style_id, user)
    page = style_page(style_id, user)
    if not page["can_edit"]:
        raise auth.Forbidden("Only the person who made this style, or the owner, can change it.")
    with LOCK:
        if "guide" in changes:
            (sdir / "STYLE.md").write_text(str(changes["guide"]), encoding="utf-8")
        if "brief" in changes:
            target = sdir / "brief" / "BRIEF.md"
            target.parent.mkdir(exist_ok=True)
            target.write_text(str(changes["brief"]), encoding="utf-8")
        if "notes" in changes or "client" in changes or "format" in changes:
            data = read_json(sdir / "style.json", {}) or {}
            if "format" in changes:
                data["format"] = check_style_format(changes["format"])
            for k in ("notes", "client"):
                if k in changes:
                    data[k] = str(changes[k]).strip()
            write_json(sdir / "style.json", data)
    return style_page(style_id, user)


# ---------------------------------------------------------------- videos

def video_dirs(user=None):
    """Videos this person can see: in any project, or kept in their own or shared styles; a reviewer (a client) sees
    only the videos they were invited to review."""
    out = {}
    reviewer = user is not None and user["role"] == "reviewer"
    homes = [*project_dirs().values()]
    for sdir in style_dirs().values():
        if user is None or reviewer or can_see(style_meta(sdir), user):
            homes.append(sdir)
    for home in homes:
        for d in home.glob("videos/*"):
            if not (d / "video.json").exists():
                continue
            if reviewer and user["email"] not in (read_json(d / "video.json", {}) or {}).get("reviewers", []):
                continue
            out[d.name] = d
    return out


def set_reviewer(vid, email, add=True):
    email = (email or "").strip().lower()
    if not auth.EMAIL_RE.match(email):
        raise StudioError("That email doesn't look right.")
    with vlock(vid):
        v = load_video(vid)
        people = [e for e in v.get("reviewers", []) if e != email]
        if add:
            people.append(email)
        v["reviewers"] = people
        save_video(v)
    return people


def can_see_video(vid, user):
    if vid not in video_dirs(user):
        raise NotFound(f"no video '{vid}'")


def load_video(vid, dirs=None):
    d = (video_dirs() if dirs is None else dirs).get(vid)
    if not d:
        raise NotFound(f"no video '{vid}'")
    v = read_json(d / "video.json")
    if v is None:
        raise StudioError(f"{d / 'video.json'} can't be read")
    if not v.get("project"):  # a style video belongs to the style holding it, even after a copy or an import
        v["style"] = d.parent.parent.name
    return {**v, "id": vid, "folder": str(d)}


def save_video(v):
    v["updated"] = now()
    write_json(Path(v["folder"]) / "video.json", {k: x for k, x in v.items() if k not in ("id", "folder")})


_held = threading.local()


@contextlib.contextmanager
def vlock(vid):
    """One writer at a time for a video: the page and Claude's commands (another process) both change video.json."""
    held = getattr(_held, "vids", None)
    if held is None:
        held = _held.vids = set()
    if vid in held:
        yield
        return
    with LOCK:
        d = video_dirs().get(vid)
        if not d:
            raise NotFound(f"no video '{vid}'")
        lock = d / ".video.lock"
        deadline = time.time() + 15
        while True:
            try:
                os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
                break
            except FileExistsError:
                try:
                    if time.time() - lock.stat().st_mtime > 30:  # left behind by a process that died
                        lock.unlink()
                        continue
                except FileNotFoundError:
                    continue
                if time.time() > deadline:
                    raise StudioError("the video is busy; try again")
                time.sleep(0.05)
        held.add(vid)
        try:
            yield
        finally:
            held.discard(vid)
            try:
                lock.unlink()
            except FileNotFoundError:
                pass


def latest_version(v):
    return v["drafts"][-1]["version"] if v["drafts"] else None


def video_summary(v, styles=None, projects=None):
    latest = latest_version(v)
    sdir = (style_dirs() if styles is None else styles).get(v["style"])
    style = read_json(sdir / "style.json", {}) or {} if sdir else {}
    pdir = (project_dirs() if projects is None else projects).get(v.get("project", ""))
    project = read_json(pdir / "project.json", {}) or {} if pdir else {}
    return {"id": v["id"], "name": v["name"], "style": v["style"],
            "style_name": style.get("name") or f"{v['style']} (style not in this studio)",
            "project": v.get("project", ""), "project_name": project.get("name", ""),
            "status": v["status"], "created": v["created"], "updated": v.get("updated", v["created"]),
            "draft_count": len(v["drafts"]), "latest": latest,
            "open_notes": sum(1 for n in v["notes"] if not n["done"] and n["version"] == latest),
            "thumb": (Path(v["folder"]) / "thumb.jpg").exists(), "style_shared": style_meta(sdir)["shared"] if sdir else False,
            "render_waiting": (v.get("render_request") or {}).get("status") == "waiting",
            "broll_waiting": (v.get("broll") or {}).get("stage") in BROLL_ASKING}


def video_view(v):
    d = Path(v["folder"])

    def files(sub):
        folder = d / sub
        if not folder.is_dir():
            return []
        return [{"name": p.name, "size": p.stat().st_size} for p in sorted(folder.iterdir())
                if p.is_file() and not p.name.startswith(".")]

    live = v.get("live")
    return {**v, **video_summary(v), "raw": files("raw"), "exports": files("exports"), "statuses": STATUSES,
            "updates": v.get("updates", [])[-200:], "render_options": RENDER_OPTIONS,
            "claude": claude_status(d), "live": {**live, "running": live_ok(live["url"])} if live else None}


def create_video(style_id, name, brief="", raw=(), user=None, project="", training=False):
    """A client's video lives in their project; a video made to train a style (training) lives in the style."""
    name = name.strip()
    if not name:
        raise StudioError("a video needs a name")
    if project and training:
        raise StudioError("a video is either for a client or to train a style, not both")
    if not project and not training:
        names = ", ".join(sorted(project_dirs())) or "none yet: make one with new-project"
        raise StudioError(f"a video needs a project, the client it's for (projects: {names}), or --training to train the style")
    sdir = style_dir(style_id, user)
    pdir = project_dir(project) if project else None
    with LOCK:
        taken = video_dirs()
        base = vid = slugify(name)
        n = 2
        while vid in taken:
            vid, n = f"{base}-{n}", n + 1
        d = (pdir or sdir) / "videos" / vid
        for sub in ("raw", "drafts", "exports"):
            (d / sub).mkdir(parents=True)
        v = {"name": name, "style": style_id, "project": project, "status": "editing", "created": now(),
             "brief": brief.strip(), "drafts": [], "notes": [], "next_note": 1, "approved": None, "id": vid, "folder": str(d)}
        save_video(v)
        about = f"Client: {project_meta(pdir)['name']} (project {project}; brand in ../../BRAND.md)\n" if pdir else \
            "Made to train this style, for no client. What it teaches goes in ../../STYLE.md\n"
        (d / "VIDEO.md").write_text(f"# {name}\n\n{about}"
                                    f"Style: {style_id} (`studio.py context {vid}` gives its folder)\n\n## Brief\n\n"
                                    f"{brief.strip() or '-'}\n\n## Folders\n\nraw/ footage, drafts/ versions for "
                                    f"review (added with add-draft), exports/ final files.\n", encoding="utf-8")
    for f in raw:
        add_raw(vid, f)
    return v


def set_video_style(vid, style_id, user=None):
    """Later drafts of a client's video follow this style. A style video stays with the style it trains."""
    name = style_meta(style_dir(style_id, user))["name"]
    with vlock(vid):
        v = load_video(vid)
        if not v.get("project"):
            raise StudioError("This video trains its style, so it stays with that style.")
        if v["style"] == style_id:
            return v
        v["style"] = style_id
        save_video(v)
        md = Path(v["folder"]) / "VIDEO.md"
        if md.exists():
            md.write_text(re.sub(r"^Style: \S+", lambda _: f"Style: {style_id}", md.read_text(encoding="utf-8"), count=1, flags=re.M),
                          encoding="utf-8")
    post_update(vid, f"The style for this video is now {name}. The next draft follows it.")
    return load_video(vid)


def video_context(vid):
    """What to read before editing a video: the client's brand decides how it's branded, the style how it's cut."""
    v = load_video(vid)
    lines = [f"Video: {v['name']} [{vid}]", f"Folder: {v['folder']}", f"Brief: {Path(v['folder']) / 'VIDEO.md'}"]
    pdir = project_dirs().get(v.get("project", ""))
    if pdir:
        lines += [f"\nClient: {project_meta(pdir)['name']} [{pdir.name}]  decides colours, fonts, logos, tone and client rules",
                  f"  Details: {pdir / 'project.json'}", f"  Guidelines and client rules: {pdir / 'BRAND.md'}"]
        lines += [f"  {label}: {pdir / sec} ({len(project_files(pdir, sec))} files)" for sec, label in PROJECT_SECTIONS]
    else:
        lines.append("\nClient: none. This video trains its style: what it teaches goes in the style's STYLE.md")
    sdir = style_dirs().get(v["style"])
    if sdir:
        meta = style_meta(sdir)
        lines += [f"\nStyle: {meta['name']} [{sdir.name}]  decides pacing, captions, motion, transitions and sound"]
        if meta.get("format"):
            lines.append(f"  Format: {STYLE_FORMATS[meta['format']]}")
        lines += [f"  Rules and lessons: {sdir / 'STYLE.md'}", f"  References: {section_target(sdir, 'references')}",
                  f"  Editing project files (XML and others): {section_target(sdir, 'projects')}", f"  Folder: {sdir}"]
    else:
        lines.append(f"\nStyle: '{v['style']}' isn't in this studio (deleted, or still on another computer). Ask which style to use.")
    return "\n".join(lines)


def add_raw(vid, src, name=None, move=False):
    src = Path(src)
    if not src.is_file():
        raise StudioError(f"no file at {src}")
    v = load_video(vid)
    dest = unique_path(Path(v["folder"]) / "raw", safe_filename(name or src.name))
    (shutil.move if move else shutil.copy2)(str(src), str(dest))
    with vlock(vid):
        v = load_video(vid)
        save_video(v)
    if not (Path(v["folder"]) / "thumb.jpg").exists():
        make_thumb(dest, Path(v["folder"]) / "thumb.jpg")
    return dest.name


def add_draft(vid, src, note="", move=False, original=None, render=None):
    src = Path(src)
    if not src.is_file():
        raise StudioError(f"no file at {src}")
    with vlock(vid):
        v = load_video(vid)
        version = (latest_version(v) or 0) + 1
        rel = f"drafts/v{version}{src.suffix.lower() or '.mp4'}"
        dest = Path(v["folder"]) / rel
        (shutil.move if move else shutil.copy2)(str(src), str(dest))
        draft = {"version": version, "file": rel, "added": now(), "note": note.strip(),
                 "original": original or src.name}
        if render:
            draft["render"] = render
        for n in v["notes"]:  # notes Claude fixed since the last draft show as "changed in this draft"
            if n.get("done") and n.get("reply") and not n.get("fixed_in"):
                n["fixed_in"] = version
        for b in v.get("feedback", []):
            if b.get("picked_up_ts") and not b.get("answered_in"):
                b["answered_in"] = version
                draft["worked_for"] = int(time.time() - b["picked_up_ts"])
        v["drafts"].append(draft)
        v["status"], v["approved"] = "in review", None
        save_video(v)
    make_thumb(dest, Path(v["folder"]) / "thumb.jpg")
    return version


def find_note(v, nid):
    for n in v["notes"]:
        if n["id"] == int(nid):
            return n
    raise NotFound(f"no note #{nid}")


def clean_attachments(folder, items):
    out = []
    for a in (items or [])[:10]:
        if a.get("kind") == "link":
            url = str(a.get("url", "")).strip()
            if not re.match(r"^https?://\S+$", url):
                raise StudioError("links have to start with http:// or https://")
            out.append({"kind": "link", "url": url[:2000]})
        elif a.get("kind") == "file":
            rel = str(a.get("file", ""))
            target = (Path(folder) / rel).resolve()
            if not rel.startswith("notes-files/") or Path(folder).resolve() not in target.parents or not target.is_file():
                raise StudioError("that attachment isn't there any more; add it again")
            out.append({"kind": "file", "file": rel, "name": str(a.get("name") or target.name)[:200],
                        "image": target.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".webp")})
    return out


def add_note(vid, version, t, text, author="", author_email="", attachments=None):
    text = str(text).strip()
    if not text and not attachments:
        raise StudioError("the note is empty")
    with vlock(vid):
        v = load_video(vid)
        if not any(d["version"] == int(version) for d in v["drafts"]):
            raise StudioError(f"there is no v{version}")
        nid = v.get("next_note", 1)
        note = {"id": nid, "version": int(version), "t": round(max(0.0, float(t)), 2), "text": text,
                "author": author or settings()["your_name"], "author_email": author_email, "done": False,
                "created": now(), "attachments": clean_attachments(v["folder"], attachments)}
        v["notes"].append(note)
        v["next_note"] = nid + 1
        save_video(v)
    return note


def update_note(vid, nid, changes):
    with vlock(vid):
        v = load_video(vid)
        note = find_note(v, nid)
        if "done" in changes:
            note["done"] = bool(changes["done"])
        if "text" in changes and str(changes["text"]).strip():
            note["text"] = str(changes["text"]).strip()
        save_video(v)
    return note


def delete_note(vid, nid):
    with vlock(vid):
        v = load_video(vid)
        v["notes"].remove(find_note(v, nid))
        save_video(v)


# ---------------------------------------------------------------- the review loop with Claude

WAIT_FILE = ".claude-wait.json"


def claude_status(folder):
    hb = read_json(Path(folder) / WAIT_FILE)
    if hb and time.time() - hb.get("beat", 0) < 20:
        return {"listening": True, "since": hb.get("since")}
    return {"listening": False}


def submit_feedback(vid, by=""):
    """Send every note not yet sent to Claude as one batch; a waiting `studio.py wait` picks it up."""
    with vlock(vid):
        v = load_video(vid)
        fresh = [n for n in v["notes"] if not n.get("batch") and not n.get("done")]
        if not fresh:
            raise StudioError("There are no new notes to send.")
        batches = v.setdefault("feedback", [])
        bid = len(batches) + 1
        for n in fresh:
            n["batch"] = bid
        batches.append({"id": bid, "at": now(), "by": by, "notes": [n["id"] for n in fresh],
                        "draft": latest_version(v)})
        v["status"] = "changes"
        save_video(v)
    return batches[-1]


def describe_notes(v, notes):
    folder = Path(v["folder"])
    lines = []
    for n in notes:
        lines.append(f"  #{n['id']}  v{n['version']} at {fmt_time(n['t'])}  ({n.get('author') or '-'}): {n['text']}")
        for a in n.get("attachments", []):
            lines.append(f"        {'link' if a['kind'] == 'link' else 'file'}: "
                         f"{a['url'] if a['kind'] == 'link' else folder / a['file']}")
    return lines


def wait_for_feedback(vid, timeout=0):
    """Listen for the page's "Submit feedback to Claude"; returns the batch and its notes, or None on timeout."""
    folder = Path(load_video(vid)["folder"])
    hb = folder / WAIT_FILE
    since, start = now(), time.time()
    try:
        while True:
            write_json(hb, {"pid": os.getpid(), "since": since, "beat": time.time()})
            with vlock(vid):
                v = load_video(vid)
                batch = next((b for b in v.get("feedback", []) if not b.get("picked_up")), None)
                if batch:
                    batch["picked_up"], batch["picked_up_ts"] = now(), time.time()
                    save_video(v)
                    return batch, v, [n for n in v["notes"] if n["id"] in batch["notes"]]
            if timeout and time.time() - start > timeout:
                return None
            time.sleep(2)
    finally:
        try:
            hb.unlink()
        except FileNotFoundError:
            pass


def add_lesson(md, title, lesson, v, nid):
    text_md = md.read_text(encoding="utf-8") if md.exists() else f"# {title}\n"
    if "## Lessons from reviews" not in text_md:
        text_md = text_md.rstrip("\n") + "\n\n## Lessons from reviews\n"
    text_md = text_md.rstrip("\n") + f"\n- {time.strftime('%Y-%m-%d')}: {lesson.strip()} ({v['name']}, note #{nid})\n"
    md.write_text(text_md, encoding="utf-8")


def reply_note(vid, nid, text, fixed=True, lesson="", client_lesson=""):
    """lesson is an editing rule (it goes to the style); client_lesson is about this client (it goes to their project)."""
    with vlock(vid):
        v = load_video(vid)
        note = find_note(v, nid)
        saved = []
        if client_lesson.strip():
            if not v.get("project"):
                raise StudioError("This video trains a style, so there's no client to save that to. Use --lesson.")
            pdir = project_dir(v["project"])
            client = project_meta(pdir)["name"]
            add_lesson(pdir / "BRAND.md", f"{client} brand guidelines", client_lesson, v, nid)
            saved.append(client)
        if lesson.strip():
            sdir = style_dir(v["style"])
            style = read_json(sdir / "style.json", {}) or {}
            add_lesson(sdir / "STYLE.md", style.get("name", v["style"]), lesson, v, nid)
            saved.append(style.get("name", v["style"]))
        note["reply"] = {"text": str(text).strip(), "at": now()}
        if fixed:
            note["done"] = True
        if saved:
            note["saved_to"] = " and ".join(saved)
        save_video(v)
    return note


# ---------------------------------------------------------------- the Live tab: what Claude is doing, in plain words

def take_snapshot(folder, src, at=None):
    """Copies an image, or grabs one frame of a video, into the video's updates/ folder. Returns its path in the folder."""
    src = Path(src)
    if not src.is_file():
        raise StudioError(f"no file at {src}")
    out = Path(folder) / "updates"
    out.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(2)
    if kind_of(src.name) == "image":
        dest = out / f"{stamp}{src.suffix.lower()}"
        shutil.copy2(src, dest)
    elif kind_of(src.name) == "video":
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise StudioError("A snapshot from a video needs FFmpeg.")
        dest = out / f"{stamp}.jpg"
        subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-ss", str(at or 0), "-i", str(src), "-frames:v", "1",
                        "-vf", "scale=960:-2", str(dest)], capture_output=True, timeout=120)
        if not dest.exists():
            raise StudioError(f"Couldn't take a snapshot from {src.name}.")
    else:
        raise StudioError("A snapshot has to be an image or a video.")
    return dest.relative_to(folder).as_posix()


def post_update(vid, text, snapshot=None, at=None, draft=None):
    text = str(text or "").strip()
    if not text and not snapshot:
        raise StudioError("An update needs some words or a snapshot.")
    image = take_snapshot(load_video(vid)["folder"], snapshot, at) if snapshot else None
    with vlock(vid):
        v = load_video(vid)
        items = v.setdefault("updates", [])
        item = {"id": (items[-1]["id"] + 1) if items else 1, "at": now(), "text": text[:4000], "image": image,
                "draft": draft or (latest_version(v) or 0) + 1}
        items.append(item)
        save_video(v)
    return item


# ---------------------------------------------------------------- the render popup: the owner picks, then Claude renders

RENDER_OPTIONS = {
    "resolution": [["same", "Same as the edit"], ["720", "720p"], ["1080", "1080p (Full HD)"], ["1440", "1440p (2K)"], ["2160", "2160p (4K)"]],
    "fps": [["same", "Same as the edit"], ["24", "24 fps"], ["25", "25 fps"], ["30", "30 fps"], ["50", "50 fps"], ["60", "60 fps"]],
    "bitrate": [["low", "Low"], ["medium", "Medium"], ["high", "High"], ["higher", "Higher"]],
    "format": [["h264", "MP4, H.264 (plays everywhere)"], ["h265", "MP4, H.265 (smaller, some browsers can't play it)"],
               ["prores", "MOV, ProRes (very large, for other editors; browsers can't play it)"]],
    "audio": [["128", "128 kbps"], ["192", "192 kbps"], ["320", "320 kbps"]],
}
RENDER_DEFAULTS = {"resolution": "same", "fps": "same", "bitrate": "medium", "format": "h264", "audio": "192"}
RENDER_MBPS = {"low": 4, "medium": 8, "high": 16, "higher": 30}  # H.264 at 1080p 30 fps; web/review.js works this out too


def probe_media(path):
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return {}
    try:
        r = subprocess.run([ffprobe, "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=width,height,r_frame_rate:format=duration", "-of", "json", str(path)],
                           capture_output=True, text=True, timeout=60)
        data = json.loads(r.stdout)
        stream = data["streams"][0]
        top, bottom = stream["r_frame_rate"].split("/")
        return {"width": int(stream["width"]), "height": int(stream["height"]),
                "fps": round(int(top) / (int(bottom) or 1), 3), "duration": float(data.get("format", {}).get("duration") or 0)}
    except (OSError, ValueError, KeyError, IndexError, subprocess.TimeoutExpired):
        return {}


def render_size(width, height, resolution):
    if resolution == "same":
        return width - width % 2, height - height % 2
    scale = int(resolution) / min(width, height)
    return round(width * scale / 2) * 2, round(height * scale / 2) * 2


def render_mbps(choice, width, height, fps):
    if choice["format"] == "prores":
        return None
    amount = RENDER_MBPS[choice["bitrate"]] * ((width * height * fps) / (1920 * 1080 * 30)) ** 0.75
    return max(0.5, round(amount * (0.7 if choice["format"] == "h265" else 1), 1))


def describe_choice(choice):
    label = lambda key: dict(RENDER_OPTIONS[key])[choice[key]]
    return (f"resolution {label('resolution')}, frame rate {label('fps')}, bitrate {label('bitrate')}, "
            f"format {label('format')}, audio {label('audio')}")


def ask_render(vid, note="", size="", fps=None, duration=None):
    """Opens the render popup on the review page. Asking again before it's answered or used keeps the same request."""
    source = {}
    if size:
        m = re.fullmatch(r"(\d+)[xX](\d+)", size.strip())
        if not m:
            raise StudioError("--size looks like 1080x1920")
        source = {"width": int(m.group(1)), "height": int(m.group(2))}
    v = load_video(vid)
    if not source:
        raw = sorted(p for p in (Path(v["folder"]) / "raw").glob("*") if kind_of(p.name) == "video")
        source = probe_media(raw[0]) if raw else {}
    if fps:
        source["fps"] = fps
    if duration:
        source["duration"] = duration
    with vlock(vid):
        v = load_video(vid)
        req = v.get("render_request")
        if not req or req.get("status") not in ("waiting", "chosen"):
            req = {"id": len(v.get("drafts", [])) + 1, "status": "waiting", "asked": now(), "draft": (latest_version(v) or 0) + 1,
                   "defaults": v.get("last_render_choice") or RENDER_DEFAULTS}
        req.update(note=str(note).strip(), source=source)
        v["render_request"] = req
        save_video(v)
    return req


def wait_for_render_choice(vid, timeout=0):
    folder = Path(load_video(vid)["folder"])
    hb = folder / WAIT_FILE
    since, start = now(), time.time()
    try:
        while True:
            write_json(hb, {"pid": os.getpid(), "since": since, "beat": time.time()})
            req = load_video(vid).get("render_request") or {}
            if req.get("status") == "chosen":
                return req
            if timeout and time.time() - start > timeout:
                return None
            time.sleep(2)
    finally:
        try:
            hb.unlink()
        except FileNotFoundError:
            pass


def set_render_choice(vid, choice, by=""):
    picked = {}
    for key, options in RENDER_OPTIONS.items():
        value = str((choice or {}).get(key, ""))
        if value not in dict(options):
            raise StudioError(f"Choose a {key}.")
        picked[key] = value
    with vlock(vid):
        v = load_video(vid)
        req = v.get("render_request")
        if not req or req.get("status") != "waiting":
            raise StudioError("Nothing is waiting for render settings right now.")
        req.update(status="chosen", choice=picked, chosen=now(), by=by)
        v["last_render_choice"] = picked
        save_video(v)
    post_update(vid, f"You chose the render settings: {describe_choice(picked)}.")
    return req


def finish_render(vid, master, note=""):
    """Encodes the edit with the settings chosen in the popup, and adds it as the next draft."""
    master = Path(master)
    if not master.is_file():
        raise StudioError(f"no file at {master}")
    v = load_video(vid)
    req = v.get("render_request") or {}
    if req.get("status") != "chosen":
        raise StudioError("No render settings have been chosen for this draft. Run: studio.py ask-render " + vid)
    ffmpeg = shutil.which("ffmpeg")
    info = probe_media(master)
    if not ffmpeg or not info:
        raise StudioError("Rendering needs FFmpeg and a readable video file.")
    choice = req["choice"]
    width, height = render_size(info["width"], info["height"], choice["resolution"])
    fps = info["fps"] if choice["fps"] == "same" else int(choice["fps"])
    mbps = render_mbps(choice, width, height, fps)
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-i", str(master), "-vf", f"scale={width}:{height}:flags=lanczos"]
    if choice["fps"] != "same":
        cmd += ["-r", str(fps)]
    if choice["format"] == "prores":
        cmd += ["-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le", "-c:a", "pcm_s16le"]
        suffix = ".mov"
    else:
        codec = ["-c:v", "libx265", "-tag:v", "hvc1"] if choice["format"] == "h265" else ["-c:v", "libx264"]
        cmd += [*codec, "-preset", "medium", "-b:v", f"{mbps}M", "-maxrate", f"{round(mbps * 1.5, 1)}M",
                "-bufsize", f"{round(mbps * 2, 1)}M", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                "-c:a", "aac", "-b:a", f"{choice['audio']}k"]
        suffix = ".mp4"
    out = Path(v["folder"]) / f".render-{secrets.token_hex(3)}{suffix}"
    post_update(vid, f"Rendering now: {width} × {height}, {fps:g} fps" + (f", about {mbps} Mbps." if mbps else ", ProRes."))
    try:
        r = subprocess.run([*cmd, str(out)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode or not out.exists():
            raise StudioError("The render failed: " + (r.stderr or "").strip()[-400:])
        made = probe_media(out)
        size_mb = out.stat().st_size / 1e6
        render = {**choice, "width": made.get("width", width), "height": made.get("height", height),
                  "fps": made.get("fps", fps), "mbps": mbps, "size_mb": round(size_mb, 1)}
        version = add_draft(vid, out, note, move=True, original=master.name, render=render)
    finally:
        out.unlink(missing_ok=True)
    with vlock(vid):
        v = load_video(vid)
        v["render_request"].update(status="used", used_in=version)
        save_video(v)
    final = Path(v["folder"]) / v["drafts"][-1]["file"]
    post_update(vid, f"Draft {version} is ready to review: {render['width']} × {render['height']}, {render['fps']:g} fps, "
                     f"{size_mb:.1f} MB.", final, (made.get("duration") or 0) / 2, version)
    return version, render


# ---------------------------------------------------------------- the b-roll picker: who picks, then what, then is it good

# video.json "broll": mode (manual or auto), settled (the owner said it's all good), stage (what the page is asking:
# mode, picking, review or idle), decision (the last answer, for the waiting command), parts (each place b-roll goes).
BROLL_NOTE = re.compile(r"\bb[\s-]?rolls?\b", re.I)
BROLL_ASKING = ("mode", "picking", "review")
BROLL_MAX_PARTS = 40


def broll_of(v):
    return v.setdefault("broll", {"mode": None, "settled": False, "stage": "idle", "decision": None, "parts": [], "round": None, "ask": 0})


def broll_notes(v):
    return [n for n in v["notes"] if not n["done"] and BROLL_NOTE.search(n.get("text") or "")]


def broll_begin(vid):
    """Called when an edit or a next draft starts. Says what to do, and opens a popup if the owner has to answer."""
    with vlock(vid):
        v = load_video(vid)
        b = broll_of(v)
        notes = broll_notes(v)
        if notes:  # the owner brought it up, so it's open again, whatever was said before
            b.update(settled=False, stage="idle", decision=None)
            save_video(v)
            return {"action": "notes", "notes": notes, "broll": b}
        if b["settled"]:
            return {"action": "skip", "broll": b}
        if b["stage"] in BROLL_ASKING:
            return {"action": "waiting", "broll": b}
        latest = latest_version(v) or 0
        if not b["mode"]:
            stage = "mode"
        elif any(p.get("picked") for p in b["parts"]) and latest >= (b["round"] or 1):
            stage = "review"
        else:
            return {"action": "ready", "broll": b}
        b.update(stage=stage, decision=None, ask=b["ask"] + 1)
        save_video(v)
        return {"action": "waiting", "broll": b}


def broll_wait(vid, timeout=0):
    """Waits for the owner's answer on the page, showing them Claude is listening. Returns it, or None on timeout."""
    folder = Path(load_video(vid)["folder"])
    hb = folder / WAIT_FILE
    since, start = now(), time.time()
    try:
        while True:
            write_json(hb, {"pid": os.getpid(), "since": since, "beat": time.time()})
            b = broll_of(load_video(vid))
            if b["stage"] not in BROLL_ASKING and b["decision"]:
                return b["decision"]
            if timeout and time.time() - start > timeout:
                return None
            time.sleep(2)
    finally:
        try:
            hb.unlink()
        except FileNotFoundError:
            pass


def _broll_number(value, what):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise StudioError(f"{what} has to be a time in seconds.")
    return round(float(value), 2)


def _broll_read_plan(plan, one_option):
    """Checks a whole plan before anything is copied, so a bad one changes nothing."""
    parts = plan.get("parts") if isinstance(plan, dict) else None
    if not isinstance(parts, list) or not parts:
        raise StudioError('A b-roll plan needs "parts", a list of the places b-roll goes.')
    if len(parts) > BROLL_MAX_PARTS:
        raise StudioError(f"That's {len(parts)} parts. A plan can have {BROLL_MAX_PARTS}.")
    for i, part in enumerate(parts, 1):
        where = f"Part {i}"
        if not isinstance(part, dict):
            raise StudioError(f"{where} has to be an object.")
        start, end = _broll_number(part.get("start"), f"{where}'s start"), _broll_number(part.get("end"), f"{where}'s end")
        if end <= start:
            raise StudioError(f"{where} ends before it starts.")
        if not str(part.get("why") or "").strip():
            raise StudioError(f'{where} needs "why": the reason b-roll goes here, in plain words.')
        options = part.get("options")
        count = len(options) if isinstance(options, list) else 0
        if one_option and count != 1:
            raise StudioError(f"{where} needs the 1 clip you chose.")
        if not one_option and count not in (3, 4):
            raise StudioError(f"{where} has {count} options. Give 3 or 4 for each part.")
        for option in options:
            src = Path(str(option.get("file") or "")) if isinstance(option, dict) else None
            if not src or not src.is_file():
                raise StudioError(f"{where} has an option with no file: {option}")
            if kind_of(src.name) not in ("video", "image"):
                raise StudioError(f"{src.name} has to be a video or an image.")
            if not one_option and not str(option.get("label") or "").strip():
                raise StudioError(f'{where} has an option with no "label".')
    return parts


def _broll_build_part(folder, pid, part, one_option):
    out = {"id": pid, "start": round(float(part["start"]), 2), "end": round(float(part["end"]), 2),
           "says": str(part.get("says") or "").strip()[:600], "why": str(part["why"]).strip()[:600], "options": [], "needs_pick": not one_option}
    if part.get("frame"):
        out["frame"] = take_snapshot(folder, part["frame"], part.get("frame_at"))
    stamp = f"{time.strftime('%Y%m%d-%H%M%S')}-{secrets.token_hex(2)}"
    for n, option in enumerate(part["options"], 1):
        src = Path(option["file"])
        dest = folder / "broll-options" / f"part-{pid}-{stamp}"
        dest.mkdir(parents=True, exist_ok=True)
        target = dest / f"{n}-{safe_filename(src.name)}"
        shutil.copy2(src, target)
        item = {"id": n, "label": str(option.get("label") or src.stem).strip()[:160], "why": str(option.get("why") or "").strip()[:400],
                "source": str(option.get("source") or "").strip()[:160], "kind": kind_of(src.name), "file": target.relative_to(folder).as_posix()}
        if item["kind"] == "video":
            poster = target.with_suffix(".poster.jpg")
            make_thumb(target, poster)
            if poster.exists():
                item["poster"] = poster.relative_to(folder).as_posix()
        out["options"].append(item)
    if one_option:
        out["picked"] = 1
    return out


def _broll_apply_plan(vid, plan, one_option, only_changed):
    parts = _broll_read_plan(plan, one_option)
    folder = Path(load_video(vid)["folder"])
    if only_changed:
        known = {p["id"] for p in broll_of(load_video(vid))["parts"]}
        for part in parts:
            if part.get("id") not in known:
                raise StudioError(f"There's no part {part.get('id')} to change. Parts here: {sorted(known)}")
    start_id = 1 + max([p["id"] for p in broll_of(load_video(vid))["parts"]] or [0])
    built = [_broll_build_part(folder, part["id"] if only_changed else start_id + i, part, one_option) for i, part in enumerate(parts)]
    with vlock(vid):
        v = load_video(vid)
        b = broll_of(v)
        if only_changed:
            by_id = {p["id"]: p for p in built}
            for i, old in enumerate(b["parts"]):
                if old["id"] in by_id:
                    new = by_id[old["id"]]
                    new["replaced"] = old.get("replaced", []) + [{k: old.get(k) for k in ("picked", "options")}]
                    b["parts"][i] = new
        else:
            b["parts"] = built
        b.update(settled=False, decision=None, change=[], round=(latest_version(v) or 0) + 1)
        if one_option:
            b.update(mode=b["mode"] or "auto", stage="idle")
        else:
            b.update(mode=b["mode"] or "manual", stage="picking", ask=b["ask"] + 1)
        save_video(v)
    return built


def broll_plan(vid, plan, only_changed=False):
    """Opens the picker: 3 or 4 options for each part, or just the parts being changed."""
    return _broll_apply_plan(vid, plan, False, only_changed)


def broll_record(vid, plan, only_changed=False):
    """The clips Claude chose by itself, so the next draft can offer them for changing."""
    return _broll_apply_plan(vid, plan, True, only_changed)


def set_broll_mode(vid, mode):
    if mode not in ("manual", "auto"):
        raise StudioError("Choose manual or automatic.")
    with vlock(vid):
        v = load_video(vid)
        b = broll_of(v)
        if b["stage"] != "mode":
            raise StudioError("This isn't asking how to pick the b-roll right now.")
        b.update(mode=mode, stage="idle", decision={"type": "mode", "mode": mode, "at": now()})
        save_video(v)
    post_update(vid, "You'll pick the b-roll. I'm watching the video to find where it can go." if mode == "manual"
                else "I'll choose the b-roll for this video myself.")
    return b


def set_broll_picks(vid, picks):
    if not isinstance(picks, dict):
        raise StudioError("Those picks can't be read.")
    with vlock(vid):
        v = load_video(vid)
        b = broll_of(v)
        if b["stage"] != "picking":
            raise StudioError("There's nothing to pick right now.")
        pending = [p for p in b["parts"] if p.get("needs_pick")]
        for part in pending:
            choice = picks.get(str(part["id"]))
            if choice != "none" and choice not in [o["id"] for o in part["options"]]:
                raise StudioError("Pick one option for every part before you submit.")
        for part in pending:
            part.update(picked=picks[str(part["id"])], needs_pick=False)
        b.update(stage="idle", decision={"type": "picks", "at": now()}, round=(latest_version(v) or 0) + 1)
        save_video(v)
    post_update(vid, f"You picked the b-roll for {len(pending)} part{'' if len(pending) == 1 else 's'}. I'm putting it into the edit now.")
    return b


def set_broll_review(vid, change):
    """After a draft: nothing to change means it's all good, and the popup stays away until a note brings b-roll up."""
    if not isinstance(change, list):
        raise StudioError("That answer can't be read.")
    with vlock(vid):
        v = load_video(vid)
        b = broll_of(v)
        if b["stage"] != "review":
            raise StudioError("This isn't asking about the b-roll right now.")
        known = {p["id"] for p in b["parts"]}
        if not set(change) <= known:
            raise StudioError("Choose parts of this video.")
        if change:
            b.update(stage="idle", change=sorted(set(change)), decision={"type": "change", "parts": sorted(set(change)), "at": now()})
        else:
            b.update(stage="idle", settled=True, change=[], decision={"type": "good", "at": now()})
        save_video(v)
    post_update(vid, "You said the b-roll is good. I won't ask again unless a note brings it up." if not change
                else f"You want to change {len(change)} b-roll part{'' if len(change) == 1 else 's'}. I'm finding new options.")
    return b


def describe_broll(v):
    folder = Path(v["folder"])
    b = broll_of(v)
    lines = [f"B-roll: {b['mode'] or 'not chosen yet'}" + (", settled" if b["settled"] else "")]
    for part in b["parts"]:
        picked = next((o for o in part["options"] if o["id"] == part.get("picked")), None)
        what = f"{picked['label']}: {folder / picked['file']}" if picked else "no b-roll here" if part.get("picked") == "none" else "not picked yet"
        lines.append(f"  part {part['id']}  {fmt_time(part['start'])}-{fmt_time(part['end'])}  {what}" + (f"\n      says: {part['says']}" if part["says"] else ""))
    return "\n".join(lines)


def broll_say(vid, decision):
    v = load_video(vid)
    if decision["type"] == "mode":
        if decision["mode"] == "auto":
            return ("AUTOMATIC: choose the b-roll yourself and edit. Then record what you used so it can be changed later: "
                    f"studio.py broll-record {vid} <plan.json>")
        return ("MANUAL: watch the whole video, find every place b-roll can go, gather 3 or 4 real options for each, then open the picker: "
                f"studio.py broll-plan {vid} <plan.json>")
    if decision["type"] == "picks":
        return "PICKED. Use exactly these, then carry on with the edit:\n" + describe_broll(v)
    if decision["type"] == "good":
        return "ALL GOOD: leave the b-roll as it is, and don't ask again unless a note brings it up."
    return (f"CHANGE parts {decision['parts']}: gather 3 or 4 NEW options for just these, then: "
            f"studio.py broll-plan {vid} <plan.json> --change\n" + describe_broll(v))


def live_ok(url):
    try:
        with urllib.request.urlopen(url, timeout=0.6):
            return True
    except Exception as e:
        return getattr(e, "code", None) is not None  # it answered, even if not with 200


def start_live(vid, project=None):
    """Start HyperFrames' live preview of the video's project, for the review page's Live preview tab."""
    v = load_video(vid)
    project = Path(project or Path(v["folder"]) / "project").expanduser().resolve()
    if not project.is_dir():
        raise StudioError(f"no HyperFrames project at {project} (pass --project <folder>)")
    stop_live(vid)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    npx = shutil.which("npx")
    if not npx:
        raise StudioError("Node isn't installed (run studio.py setup)")
    log = open(Path(v["folder"]) / ".live.log", "a")
    kwargs = {"stdout": log, "stderr": log, "stdin": subprocess.DEVNULL, "cwd": str(Path.home())}
    if WINDOWS:
        kwargs["creationflags"] = 0x00000008 | 0x00000200 | 0x08000000
    else:
        kwargs["start_new_session"] = True
    proc = subprocess.Popen([npx, "--yes", "hyperframes", "preview", str(project), f"--port={port}", "--no-open",
                             "--foreground", "--force-new"], **kwargs)
    url = f"http://127.0.0.1:{port}/"
    with vlock(vid):
        v = load_video(vid)
        v["live"] = {"url": url, "project": str(project), "pid": proc.pid, "started": now()}
        save_video(v)
    for _ in range(60):
        if live_ok(url):
            break
        time.sleep(0.5)
    return url


def stop_live(vid):
    with vlock(vid):
        v = load_video(vid)
        live = v.pop("live", None)
        save_video(v)
    if live and live.get("pid"):
        try:
            if WINDOWS:
                subprocess.run(["taskkill", "/PID", str(live["pid"]), "/T", "/F"], capture_output=True)
            else:
                os.killpg(os.getpgid(live["pid"]), signal.SIGTERM)
        except (ProcessLookupError, PermissionError, OSError):
            pass
    return live


def set_status(vid, status):
    if status not in STATUSES:
        raise StudioError(f"status must be one of: {', '.join(STATUSES)}")
    with vlock(vid):
        v = load_video(vid)
        v["status"] = status
        if status not in ("approved", "delivered"):
            v["approved"] = None
        save_video(v)
    return v


def approve(vid, version):
    with vlock(vid):
        v = load_video(vid)
        if not any(d["version"] == int(version) for d in v["drafts"]):
            raise StudioError(f"there is no v{version}")
        v["status"], v["approved"] = "approved", {"version": int(version), "at": now()}
        save_video(v)
    return v


_ACCOUNTS = None


def accounts():
    global _ACCOUNTS
    if _ACCOUNTS is None:
        s = settings()
        open_to_claim = not s["owner_email"] or s.get("owner_claimed") or \
            hashlib.sha256(s["owner_email"].encode()).hexdigest() == OLD_DEFAULT_OWNER
        _ACCOUNTS = auth.Auth(DATA, s["owner_email"], log=lambda line: print(line, flush=True), claim=claim_owner if open_to_claim else None,
                              open_to_others=lambda: approval.open_to_others(DATA))
    return _ACCOUNTS


def claim_owner(email):
    write_json(SETTINGS, {**settings(), "owner_email": email, "owner_claimed": True})


def rename_account(email, username):
    """A new username everywhere it shows: the account, the private styles folder, "made by" and note authors."""
    acc = accounts()
    old = acc.rename(email, username)
    new = acc.users()[email]["username"]
    if old == new:
        return new
    with LOCK:
        lib = library()
        old_dir, new_dir = lib / PRIVATE / old, lib / PRIVATE / new
        if old_dir.is_dir():
            if new_dir.exists() and old.lower() != new.lower():
                for d in old_dir.iterdir():  # someone's folder already there: move the styles in one by one
                    shutil.move(str(d), str(unique_path(new_dir, d.name)))
                old_dir.rmdir()
            else:
                tmp = lib / PRIVATE / f".renaming-{secrets.token_hex(3)}"  # two steps: Mac and Windows ignore case
                os.replace(old_dir, tmp)
                os.replace(tmp, new_dir)
        for sdir in style_dirs().values():
            data = read_json(sdir / "style.json", {}) or {}
            if data.get("maker") == email or (not data.get("maker") and data.get("maker_name") == old):
                data["maker_name"] = new
                if data.get("shared_by") == old:
                    data["shared_by"] = new
                write_json(sdir / "style.json", data)
        for vid in video_dirs():
            with vlock(vid):
                v = load_video(vid)
                changed = False
                for n in v.get("notes", []):
                    if n.get("author_email") == email or (not n.get("author_email") and n.get("author") == old):
                        n["author"], changed = new, True
                for b in v.get("feedback", []):
                    if b.get("by") == old:
                        b["by"], changed = new, True
                if changed:
                    save_video(v)
    return new


def lan_addresses(port):
    """This computer's addresses on the local network, for people on the same Wi-Fi."""
    out = set()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("192.168.0.1", 9))  # picks the outgoing interface; nothing is sent
            out.add(sock.getsockname()[0])
    except OSError:
        pass
    return [f"http://{ip}:{port}" for ip in sorted(out) if not ip.startswith("127.")]


def fmt_time(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


# ---------------------------------------------------------------- Claude skills packed in Editors.Hub
#
# A skill is installed into ~/.claude/skills only when it isn't there, and later replaced only when the copy there
# is still exactly what Editors.Hub put in (the marker file records its hash). A skill that came from somewhere
# else, or that was set up or edited since (creator-setup fills in the brand), is never touched.

def skill_files(folder):
    for p in sorted(folder.rglob("*")):
        rel = p.relative_to(folder)
        if p.is_file() and not any(part in SKILL_JUNK for part in rel.parts):
            yield rel, p


def tree_hash(folder):
    h = hashlib.sha256()
    for rel, p in skill_files(folder):
        h.update(rel.as_posix().encode() + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest()


def skill_description(folder):
    text = (folder / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^description:\s*[>|]?\s*(.*?)\s*$", text, re.M)
    desc = (m.group(1) if m else "").strip().strip("\"'")
    if not desc and m:  # folded description on the following lines
        rest = text[m.end():].split("\n---", 1)[0]
        desc = " ".join(line.strip() for line in rest.splitlines() if line.startswith(" "))
    return desc[:220] + ("…" if len(desc) > 220 else "")


def bundled_skills():
    if not SKILLS.is_dir():
        return []
    return [d for d in sorted(SKILLS.iterdir()) if d.is_dir() and (d / "SKILL.md").exists()]


def skipped_here():
    return set((read_json(DEVICE, {}) or {}).get("skip_skills", []))


def set_skipped(names, skip):
    data = read_json(DEVICE, {}) or {}
    current = set(data.get("skip_skills", []))
    data["skip_skills"] = sorted(current | set(names) if skip else current - set(names))
    write_json(DEVICE, data)


def skill_state(src):
    dest = CLAUDE_SKILLS / src.name
    if not dest.exists() and not dest.is_symlink():
        return "skipped here" if src.name in skipped_here() else "missing"
    marker = read_json(dest / SKILL_MARKER) if dest.is_dir() and not dest.is_symlink() else None
    if not marker:
        return "already there"  # installed another way: left alone
    if tree_hash(dest) != marker.get("installed_hash"):
        return "set up"  # filled in or edited on this computer: left alone
    if tree_hash(src) != marker.get("bundle_hash"):
        return "skipped here" if src.name in skipped_here() else "update"
    return "installed"


def list_skills():
    return [{"name": d.name, "description": skill_description(d), "state": skill_state(d)} for d in bundled_skills()]


def install_skill(src):
    """Copy one packed skill into Claude's skills folder (replacing only a copy Editors.Hub put there)."""
    dest = CLAUDE_SKILLS / src.name
    tmp = CLAUDE_SKILLS / f".{src.name}.editors-hub-tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(src, tmp, ignore=shutil.ignore_patterns(*SKILL_JUNK))
    for p in tmp.rglob("*.md"):  # the Editors.Hub skill needs to know where this copy of the studio lives
        text = p.read_text(encoding="utf-8", errors="replace")
        if HUB_DIR_TOKEN in text:
            p.write_text(text.replace(HUB_DIR_TOKEN, ROOT.as_posix()), encoding="utf-8")
    write_json(tmp / SKILL_MARKER, {"installed_by": "Editors.Hub", "at": now(), "bundle_hash": tree_hash(src),
                                    "installed_hash": tree_hash(tmp)})
    if dest.exists():
        shutil.rmtree(dest)
    os.replace(tmp, dest)


def install_skills(names=None):
    """Install what's missing and update untouched copies; with names, only those (and stop skipping them here)."""
    CLAUDE_SKILLS.mkdir(parents=True, exist_ok=True)
    if names:
        unknown = set(names) - {s.name for s in bundled_skills()}
        if unknown:
            raise NotFound(f"not packed in Editors.Hub: {', '.join(sorted(unknown))}")
        set_skipped(names, False)
    done = {"installed": [], "updated": [], "failed": []}
    for src in bundled_skills():
        state = skill_state(src)
        if state not in ("missing", "update") or (names and src.name not in names):
            continue
        try:
            install_skill(src)
            done["installed" if state == "missing" else "updated"].append(src.name)
        except OSError as e:
            done["failed"].append(f"{src.name}: {e}")
    return done


def add_skills(paths):
    found = []
    for path in map(lambda p: Path(p).expanduser(), paths):
        if (path / "SKILL.md").exists():
            found.append(path)
        elif path.is_dir():
            found += [d for d in sorted(path.iterdir()) if d.is_dir() and (d / "SKILL.md").exists()]
        else:
            raise StudioError(f"no skill at {path} (a skill is a folder with a SKILL.md)")
    if not found:
        raise StudioError("no skills found there (a skill is a folder with a SKILL.md)")
    SKILLS.mkdir(exist_ok=True)
    for src in found:
        dest = SKILLS / src.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest, ignore=shutil.ignore_patterns(*SKILL_JUNK))
    return [s.name for s in found]


def remove_skill(name):
    dest = SKILLS / name
    if not (dest / "SKILL.md").exists():
        raise NotFound(f"no packed skill '{name}'")
    shutil.rmtree(dest)


def profile_summary(folder):
    p = read_json(Path(folder) / "profile.json")
    if p is None:
        return None
    fonts = sorted(f.name for f in (Path(folder) / "assets" / "fonts").glob("*") if f.is_file())
    return {"creator": p.get("creator_name", ""), "brand": p.get("brand_name", ""), "accent": p.get("accent", ""),
            "fonts": fonts, "folder": str(folder)}


def profile_fingerprint():
    """What the skills are filled from: the answers (not creator-setup's own 'configured' dates) and the asset files."""
    p = read_json(PROFILE_DIR / "profile.json", {}) or {}
    answers = {k: {a: b for a, b in v.items() if a != "configured"} for k, v in p.get("skills", {}).items()}
    p = {**p, "skills": {k: v for k, v in answers.items() if v}}
    assets = PROFILE_DIR / "assets"
    files = [(rel.as_posix(), f.stat().st_size) for rel, f in skill_files(assets)] if assets.is_dir() else []
    return hashlib.sha256(json.dumps([p, files], sort_keys=True).encode()).hexdigest()


def pack_profile():
    if not (PROFILE_DIR / "profile.json").exists():
        raise StudioError(f"no creator-setup profile on this computer ({PROFILE_DIR}); run creator-setup first")
    found = [k for k in (read_json(PROFILE_DIR / "profile.json", {}) or {})
             if re.search(r"api.?key|secret|token|password", k, re.I)]
    if found:
        raise StudioError(f"the profile holds what looks like a key ({', '.join(found)}); keys don't belong in it")
    tmp = ROOT / ".profile-tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(PROFILE_DIR, tmp, ignore=shutil.ignore_patterns(*SKILL_JUNK))
    if PROFILE_PACK.exists():
        shutil.rmtree(PROFILE_PACK)
    os.replace(tmp, PROFILE_PACK)
    return profile_summary(PROFILE_PACK)


def restore_profile(replace=False):
    """Put the packed profile in place. Never over this computer's own profile unless asked (that one is kept aside)."""
    if not (PROFILE_PACK / "profile.json").exists():
        return None
    if (PROFILE_DIR / "profile.json").exists():
        if not replace:
            return None
        backup = PROFILE_DIR.with_name(f"creator-profile.before-{time.strftime('%Y%m%d-%H%M%S')}")
        os.replace(PROFILE_DIR, backup)
    elif PROFILE_DIR.exists():
        shutil.rmtree(PROFILE_DIR)
    shutil.copytree(PROFILE_PACK, PROFILE_DIR)
    return profile_summary(PROFILE_DIR)


def fill_skills():
    """Fill the placeholders of the skills Editors.Hub installed (and nobody changed) from this computer's profile."""
    if not (PROFILE_DIR / "profile.json").exists():
        return []
    fingerprint = profile_fingerprint()
    filled = []
    for src in bundled_skills():
        dest = CLAUDE_SKILLS / src.name
        script = dest / "setup" / "apply_profile.py"
        if src.name == "creator-setup" or not script.exists() or skill_state(src) != "installed":
            continue
        marker = read_json(dest / SKILL_MARKER)
        if marker.get("profile") == fingerprint:
            continue
        try:
            r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=300,
                               encoding="utf-8", errors="replace",
                               cwd=str(Path.home()), env={**os.environ, "CREATOR_PROFILE_DIR": str(PROFILE_DIR)})
        except (OSError, subprocess.TimeoutExpired) as e:
            filled.append(f"{src.name} (failed: {e})")
            continue
        ready = r.returncode == 0
        # what the fill changed is still Editors.Hub's copy: record it, so a newer pack version can replace and refill it
        write_json(dest / SKILL_MARKER, {**marker, "profile": fingerprint, "filled": now(), "ready": ready,
                                         "installed_hash": tree_hash(dest)})
        filled.append(src.name if ready else f"{src.name} (asks a few questions of its own on first use)")
    return filled


# ---------------------------------------------------------------- what setup needs from the studio

CLAUDE_MD = CLAUDE_SKILLS.parent / "CLAUDE.md"
NOTE_START = "<!-- editors-hub:start (written by Editors.Hub; delete from here to editors-hub:end to remove) -->"
NOTE_END = "<!-- editors-hub:end -->"


def claude_note():
    run = f'python3 "{ROOT.as_posix()}/studio.py"' if not WINDOWS else f'py "{ROOT.as_posix()}/studio.py"'
    scope = ("For ANY video-editing request (a raw clip, an edit, a reel, captions, B-roll, a client's video, review "
             "notes), use the `editors-hub` skill first: it puts the work in the right client project, with the right style.")
    return (f"{NOTE_START}\n## Editors.Hub\nThis computer has Editors.Hub, the owner's own video studio "
            f"(`{run} status`). {scope} Show its pages in the Claude app's built-in browser "
            f"(`{run} open` prints the address). Never hand anyone a sign-in code except the owner.\n{NOTE_END}\n")


def claude_note_ok():
    try:
        text = CLAUDE_MD.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False
    return NOTE_START in text and claude_note() in text


def write_claude_note():
    text = CLAUDE_MD.read_text(encoding="utf-8") if CLAUDE_MD.exists() else ""
    if NOTE_START in text and NOTE_END in text:
        before, rest = text.split(NOTE_START, 1)
        text = before + rest.split(NOTE_END, 1)[1].lstrip("\n")
    text = (text.rstrip("\n") + "\n\n" if text.strip() else "") + claude_note()
    CLAUDE_MD.parent.mkdir(parents=True, exist_ok=True)
    CLAUDE_MD.write_text(text, encoding="utf-8")


def transcriber():
    return (read_json(PROFILE_DIR / "profile.json", {}) or {}).get("transcriber", "local")


def needed_keys():
    return {"ELEVENLABS_API_KEY"} if transcriber() == "elevenlabs" else set()


def setup_workdir():
    s = settings()
    return (True, s["library"]) if s.get("library_confirmed") else (False, "Pick where your styles and videos go.")


def setup_skills():
    todo = [x["name"] for x in list_skills() if x["state"] in ("missing", "update")]
    if todo:
        return False, f"{len(todo)} to install"
    if not claude_note_ok():
        return False, "Claude's note isn't written yet"
    return True, f"{len(bundled_skills())} skills ready, and Claude knows the studio"


def setup_install_skills():
    with LOCK:
        restore_profile()
        done = install_skills()
        fill_skills()
        write_claude_note()
    return f"installed {len(done['installed'])}" if done["installed"] else ""


def setup_keys():
    rows = keys.status(needed_keys())
    missing = [r["service"] for r in rows if r["needed"] and not r["added"]]
    if missing:
        return False, f"Add: {', '.join(missing)} (Settings > API keys)"
    added = sum(r["added"] for r in rows)
    return True, f"{added} of {len(rows)} added; none more needed for how you work"


# ---------------------------------------------------------------- moving a style between computers
#
# Export copies a style into one folder (or a .zip) with editors-hub-style.json beside it: what's inside, file by file,
# so an import can check that everything arrived. Works the same on Mac and Windows.

STYLE_MANIFEST = "editors-hub-style.json"
ZIP_SUFFIX = ".editors-hub-style.zip"
PROJECT_MANIFEST = "editors-hub-project.json"
PROJECT_ZIP_SUFFIX = ".editors-hub-project.zip"
TRANSFER_JUNK = {".video.lock", ".claude-wait.json", ".live.log", ".DS_Store", "Thumbs.db", "desktop.ini", STYLE_MANIFEST, PROJECT_MANIFEST}
JOBS = {}


def transfer_files(sdir):
    out = []
    for f in sorted(sdir.rglob("*")):
        rel = f.relative_to(sdir)
        if f.is_file() and not any(part in TRANSFER_JUNK or part.startswith((".upload-", ".render-")) for part in rel.parts):
            out.append((rel.as_posix(), f))
    return out


def style_manifest(sdir, files):
    meta = style_meta(sdir)
    sizes = {rel: f.stat().st_size for rel, f in files}
    return {"format": "editors-hub-style", "version": 1, "id": sdir.name, "name": meta["name"],
            "client": meta.get("client", ""), "exported": now(), "maker": meta.get("maker"),
            "maker_name": meta.get("maker_name"), "studio_version": (ROOT / "VERSION").read_text().strip(),
            "bytes": sum(sizes.values()), "files": sizes}


def can_take_style(style_id, user):
    """Anyone who makes videos can take a shared style; a private one only its maker (style_dir hides it otherwise)."""
    if user is not None and user["role"] == "reviewer":
        raise auth.Forbidden("Your account can't do that. Ask the owner.")
    return style_dir(style_id, user)


class JobStopped(Exception):
    pass


def check_stop(job):
    """Long loops call this; a Stop on the page makes the work end here and clean up after itself."""
    if job is not None and job.get("stop"):
        raise JobStopped()


def stop_job(jid, user=None):
    job = JOBS.get(jid)
    if not job or (user is not None and user["role"] != "owner" and job["by"] != user["email"]):
        raise NotFound("no such job")
    if job["state"] == "running":
        job["stop"] = True
        job["stage"] = "Stopping and cleaning up"
    return job


def start_job(kind, title, user, work, style=None):
    """Work that takes a while, in the background. The page's activity panel shows its stage and progress."""
    jid = secrets.token_hex(6)
    job = {"id": jid, "kind": kind, "title": title, "state": "running", "done_bytes": 0, "total_bytes": 0,
           "stage": "Starting", "message": "", "result": None, "by": (user or {}).get("email"), "style": style,
           "started": now(), "started_ts": time.time(), "finished_ts": None}
    JOBS[jid] = job

    def run():
        try:
            job["result"] = work(job)
            job["state"], job["stage"] = "done", "Done"
        except JobStopped:
            job["state"], job["stage"] = "stopped", "Stopped"
            job["message"] = "Stopped. Nothing was left half done."
        except Exception as e:
            job["state"], job["message"] = "failed", str(e) if isinstance(e, (StudioError, auth.AuthError)) else f"{type(e).__name__}: {e}"
        job["finished_ts"] = time.time()
    threading.Thread(target=run, daemon=True).start()
    return job


def recent_jobs(user):
    """What the activity panel shows: running jobs, and ones that finished in the last 15 minutes."""
    out = [j for j in JOBS.values() if (user is None or user["role"] == "owner" or j["by"] == user["email"])
           and (j["state"] == "running" or time.time() - (j["finished_ts"] or 0) < 900)]
    return sorted(out, key=lambda j: j["started_ts"], reverse=True)[:12]


def copy_files(files, dest_root, job):
    for rel, src in files:
        target = dest_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(src, "rb") as fi, open(target, "wb") as fo:
            while True:
                check_stop(job)
                chunk = fi.read(8 << 20)
                if not chunk:
                    break
                fo.write(chunk)
                job["done_bytes"] += len(chunk)
        shutil.copystat(src, target)


def export_style_to(style_id, dest_parent, user=None):
    sdir = can_take_style(style_id, user)
    dest_parent = Path(str(dest_parent or "").strip()).expanduser()
    if not dest_parent.is_dir():
        raise StudioError(f"{dest_parent} isn't a folder that exists")
    files = transfer_files(sdir)
    manifest = style_manifest(sdir, files)
    if shutil.disk_usage(dest_parent).free < manifest["bytes"] * 1.02 + 50_000_000:
        raise StudioError(f"Not enough space there: the style needs {manifest['bytes'] / 1e9:.1f} GB.")
    out = unique_path(dest_parent, safe_filename(f"{manifest['name']} - EditorsHub style"))

    def work(job):
        job["total_bytes"] = manifest["bytes"]
        job["stage"] = f"Copying to {dest_parent.name or dest_parent}"
        tmp = out.with_name(out.name + " (copying)")
        try:
            copy_files(files, tmp, job)
            write_json(tmp / STYLE_MANIFEST, manifest)
            os.replace(tmp, out)
        except BaseException:
            shutil.rmtree(tmp, ignore_errors=True)  # stopped or failed: no half copy left on the drive
            raise
        return {"path": str(out), "name": manifest["name"], "bytes": manifest["bytes"]}
    return start_job("export", f"Saving {manifest['name']}", user, work, style=style_id)


def place_style(src, manifest, where, user, job, move=False):
    """Check the files against the manifest, then put the style in this studio (My styles or Shared)."""
    bad = [rel for rel, size in manifest["files"].items()
           if not (src / rel).is_file() or (src / rel).stat().st_size != size]
    if bad:
        raise StudioError(f"{len(bad)} file{'s are' if len(bad) > 1 else ' is'} missing or incomplete, like {bad[0]}. "
                          f"Export the style again.")
    email, username = _maker(user)
    with LOCK:
        taken = style_dirs()
        base = sid = slugify(manifest.get("id") or manifest["name"])
        n = 2
        while sid in taken:
            sid, n = f"{base}-{n}", n + 1
        dest = library() / SHARED / sid if where == "shared" else library() / PRIVATE / username / sid
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_name(f".{sid}.importing")
        if tmp.exists():
            shutil.rmtree(tmp)
    try:
        if move:
            os.replace(src, tmp)
        else:
            job["total_bytes"] = manifest["bytes"]
            copy_files([(rel, src / rel) for rel in manifest["files"]], tmp, job)
        check_stop(job)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)  # stopped or failed: the half-copied style goes
        raise
    (tmp / STYLE_MANIFEST).unlink(missing_ok=True)
    with LOCK:
        taken_videos = set(video_dirs())
        for vdir in sorted((tmp / "videos").glob("*")) if (tmp / "videos").is_dir() else []:
            if vdir.name in taken_videos:  # a video with the same name lives in another style here
                new, n = f"{vdir.name}-2", 3
                while new in taken_videos:
                    new, n = f"{vdir.name}-{n}", n + 1
                os.replace(vdir, vdir.with_name(new))
        data = read_json(tmp / "style.json", {}) or {}
        data.update(maker=email, maker_name=username, original_maker=manifest.get("maker"),
                    imported={"from": manifest.get("source", ""), "at": now(), "exported": manifest.get("exported")})
        if sid != base:
            data["name"] = f"{manifest['name']} ({sid.rsplit('-', 1)[-1]})"
        data.pop("shared_at", None)
        if where == "shared":
            data.update(shared_at=now(), shared_by=username)
        write_json(tmp / "style.json", data)
        os.replace(tmp, dest)
    return {"id": sid, "name": data.get("name", manifest["name"]), "shared": where == "shared",
            "videos": len(list((dest / "videos").glob("*/video.json"))), "bytes": manifest["bytes"]}


def read_export(path):
    """An exported style: a folder with editors-hub-style.json, or a .zip holding one. Returns (manifest, kind)."""
    path = Path(path)
    if path.is_dir():
        if (path / PROJECT_MANIFEST).is_file():
            raise StudioError("That's a saved client. Import it from Projects.")
        manifest = read_json(path / STYLE_MANIFEST)
        if manifest:
            return manifest, "folder"
        files = transfer_files(path)
        if not files:
            raise StudioError("That folder is empty.")
        if (path / "style.json").is_file():  # a style folder copied over by hand
            m = style_manifest(path, files)
            m["name"] = (read_json(path / "style.json", {}) or {}).get("name") or path.name
            return m, "folder"
        # any other folder: its files become a new style, each sorted into its section
        return {"name": path.name, "id": slugify(path.name), "bytes": sum(f.stat().st_size for _, f in files),
                "files": {rel: f.stat().st_size for rel, f in files}}, "plain"
    if path.is_file() and zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as zf:
            name = next((n for n in zf.namelist() if n.endswith("/" + STYLE_MANIFEST) and n.count("/") == 1), None)
            if not name:
                raise StudioError("That .zip isn't an exported Editors.Hub style.")
            return json.loads(zf.read(name)), "zip"
    raise StudioError(f"Nothing to import at {path}")


FONT_EXTS = {".ttf", ".otf", ".woff", ".woff2"}


def style_from_folder(folder, where, user, job):
    """Make a new style from a folder of material: footage to B-roll, LUTs to Colour grading, project files to
    Project files, audio to Music, images to Graphics, fonts to fonts/, anything else to files/ (paths kept)."""
    files = transfer_files(folder)
    job["total_bytes"] = sum(f.stat().st_size for _, f in files)
    made = create_style(folder.name, "", "", user)
    sdir = Path(made["folder"])
    sorted_into = {}
    try:
        _fill_from_folder(files, sdir, sorted_into, job)
    except BaseException:
        shutil.rmtree(sdir, ignore_errors=True)  # stopped or failed: the half-made style goes
        raise
    if where == "shared":
        share_style(made["id"], True, user)
    return {"id": made["id"], "name": made["name"], "shared": where == "shared", "videos": 0,
            "bytes": job["total_bytes"], "sorted": sorted_into}


def _fill_from_folder(files, sdir, sorted_into, job):
    for rel, src in files:
        ext = src.suffix.lower()
        section = next((sec for exts, sec in SORT_BY_TYPE if ext in exts), None)
        base = section_target(sdir, section) if section else sdir / ("fonts" if ext in FONT_EXTS else "files")
        dest = base / Path(rel)
        if dest.exists():
            dest = unique_path(dest.parent, dest.name)
        copy_files([(dest.relative_to(sdir).as_posix(), src)], sdir, job)
        label = next((lab for sid, lab, _ in SECTIONS if sid == section), "Fonts" if ext in FONT_EXTS else "Files")
        sorted_into[label] = sorted_into.get(label, 0) + 1


def import_style_from(path, where="mine", user=None, remove_after=False):
    path = Path(str(path or "").strip()).expanduser()
    manifest, kind = read_export(path)
    manifest["source"] = str(path)
    if where not in ("mine", "shared"):
        raise StudioError("where must be mine or shared")
    if shutil.disk_usage(library()).free < manifest.get("bytes", 0) * (1.02 if kind == "folder" else 2.05) + 50_000_000:
        raise StudioError(f"Not enough space in the library: the style needs {manifest.get('bytes', 0) / 1e9:.1f} GB.")

    def work(job):
        job["stage"] = "Copying and checking every file"
        try:
            if kind == "folder":
                return place_style(path, manifest, where, user, job)
            if kind == "plain":
                return style_from_folder(path, where, user, job)
            job["total_bytes"] = manifest.get("bytes", 0)
            unpack = library() / f".unpacking-{secrets.token_hex(4)}"
            try:
                with zipfile.ZipFile(path) as zf:
                    root = next(n.split("/")[0] for n in zf.namelist() if n.endswith("/" + STYLE_MANIFEST))
                    for info in zf.infolist():
                        if info.is_dir() or not info.filename.startswith(root + "/"):
                            continue
                        rel = info.filename[len(root) + 1:]
                        target = (unpack / rel).resolve()
                        if unpack.resolve() not in target.parents:  # a path in the zip trying to escape
                            raise StudioError("That .zip has a file outside its style folder.")
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(info) as fi, open(target, "wb") as fo:
                            while True:
                                check_stop(job)
                                chunk = fi.read(8 << 20)
                                if not chunk:
                                    break
                                fo.write(chunk)
                                job["done_bytes"] += len(chunk)
                return place_style(unpack, manifest, where, user, job, move=True)
            finally:
                if unpack.exists():
                    shutil.rmtree(unpack, ignore_errors=True)
        finally:
            if remove_after:
                path.unlink(missing_ok=True)
    return start_job("import", f"Bringing in {manifest.get('name', 'a style')}", user, work)


# ---------------------------------------------------------------- taking a client's project to a drive or another computer

def project_manifest(d, files):
    meta = project_meta(d)
    styles = {}
    for f in d.glob("videos/*/video.json"):
        style_id = (read_json(f, {}) or {}).get("style")
        if style_id:
            sdir = style_dirs().get(style_id)
            styles[style_id] = style_meta(sdir)["name"] if sdir else style_id
    sizes = {rel: f.stat().st_size for rel, f in files}
    return {"format": "editors-hub-project", "version": 1, "id": d.name, "name": meta["name"], "exported": now(),
            "maker": meta.get("maker"), "maker_name": meta.get("maker_name"), "styles": styles,
            "studio_version": (ROOT / "VERSION").read_text().strip(), "bytes": sum(sizes.values()), "files": sizes}


def export_project_to(project_id, dest_parent, user=None):
    d = project_dir(project_id)
    dest_parent = Path(str(dest_parent or "").strip()).expanduser()
    if not dest_parent.is_dir():
        raise StudioError(f"{dest_parent} isn't a folder that exists")
    files = transfer_files(d)
    manifest = project_manifest(d, files)
    if shutil.disk_usage(dest_parent).free < manifest["bytes"] * 1.02 + 50_000_000:
        raise StudioError(f"Not enough space there: this client needs {manifest['bytes'] / 1e9:.1f} GB.")
    out = unique_path(dest_parent, safe_filename(f"{manifest['name']} - EditorsHub project"))

    def work(job):
        job["total_bytes"] = manifest["bytes"]
        job["stage"] = f"Copying to {dest_parent.name or dest_parent}"
        tmp = out.with_name(out.name + " (copying)")
        try:
            copy_files(files, tmp, job)
            write_json(tmp / PROJECT_MANIFEST, manifest)
            os.replace(tmp, out)
        except BaseException:
            shutil.rmtree(tmp, ignore_errors=True)  # stopped or failed: no half copy left on the drive
            raise
        return {"path": str(out), "name": manifest["name"], "bytes": manifest["bytes"], "styles": list(manifest["styles"].values())}
    return start_job("export", f"Saving {manifest['name']}", user, work)


def read_project_export(path):
    """A saved client: a folder with editors-hub-project.json, or a .zip holding one. Returns (manifest, kind)."""
    path = Path(path)
    if path.is_dir():
        manifest, kind = read_json(path / PROJECT_MANIFEST), "folder"
        if not manifest:
            raise StudioError("That folder isn't a saved Editors.Hub project." +
                              (" It's a style: add it from My styles." if (path / STYLE_MANIFEST).is_file() else ""))
    elif path.is_file() and zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as zf:
            name = next((n for n in zf.namelist() if n.endswith("/" + PROJECT_MANIFEST) and n.count("/") == 1), None)
            if not name:
                raise StudioError("That .zip isn't a saved Editors.Hub project.")
            manifest, kind = json.loads(zf.read(name)), "zip"
    else:
        raise StudioError(f"Nothing to import at {path}")
    files = manifest.get("files")
    if manifest.get("format") != "editors-hub-project" or not manifest.get("name") or not isinstance(files, dict):
        raise StudioError("That saved project can't be read. Save it again.")
    for rel in files:  # what's saved has to stay inside the new project's folder
        if rel.startswith(("/", "\\")) or ":" in rel or ".." in rel.replace("\\", "/").split("/"):
            raise StudioError("That saved project has a file outside its folder.")
    return manifest, kind


def place_project(src, manifest, user, job, move=False):
    """Check the files against the list, then add the client to this studio. A client already here keeps theirs."""
    bad = [rel for rel, size in manifest["files"].items()
           if not (src / rel).is_file() or (src / rel).stat().st_size != size]
    if bad:
        raise StudioError(f"{len(bad)} file{'s are' if len(bad) > 1 else ' is'} missing or incomplete, like {bad[0]}. "
                          f"Save the project again.")
    email, username = _maker(user)
    with LOCK:
        taken = project_dirs()
        base = pid = slugify(manifest.get("id") or manifest["name"])
        n = 2
        while pid in taken:
            pid, n = f"{base}-{n}", n + 1
        dest = library() / PROJECTS / pid
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_name(f".{pid}.importing")
        if tmp.exists():
            shutil.rmtree(tmp)
    try:
        if move:
            os.replace(src, tmp)
        else:
            job["total_bytes"] = manifest["bytes"]
            copy_files([(rel, src / rel) for rel in manifest["files"]], tmp, job)
        check_stop(job)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)  # stopped or failed: the half-copied client goes
        raise
    (tmp / PROJECT_MANIFEST).unlink(missing_ok=True)
    for sub in ("videos", *(sec for sec, _ in PROJECT_SECTIONS)):  # empty folders aren't in the file list
        (tmp / sub).mkdir(exist_ok=True)
    with LOCK:
        taken_videos = set(video_dirs())
        for vdir in sorted((tmp / "videos").glob("*")):
            info = vdir / "video.json"
            if not info.exists():
                continue
            v = read_json(info, {}) or {}
            v["project"] = pid
            v.pop("live", None)  # a preview running on the other computer isn't running here
            write_json(info, v)
            if vdir.name in taken_videos:  # a video with the same name lives somewhere else here
                new, n = f"{vdir.name}-2", 3
                while new in taken_videos:
                    new, n = f"{vdir.name}-{n}", n + 1
                os.replace(vdir, vdir.with_name(new))
                taken_videos.add(new)
        data = read_json(tmp / "project.json", {}) or {}
        data.update(maker=email, maker_name=username, original_maker=manifest.get("maker"),
                    imported={"from": manifest.get("source", ""), "at": now(), "exported": manifest.get("exported")})
        if pid != base:
            data["name"] = f"{manifest['name']} ({pid.rsplit('-', 1)[-1]})"
        write_json(tmp / "project.json", data)
        os.replace(tmp, dest)
    here = style_dirs()
    return {"id": pid, "name": data.get("name", manifest["name"]), "videos": len(list((dest / "videos").glob("*/video.json"))),
            "bytes": manifest["bytes"], "missing_styles": [name for sid, name in (manifest.get("styles") or {}).items() if sid not in here]}


def import_project_from(path, user=None, remove_after=False):
    path = Path(str(path or "").strip()).expanduser()
    try:
        manifest, kind = read_project_export(path)
        manifest["source"] = str(path)
        if shutil.disk_usage(library()).free < manifest.get("bytes", 0) * (1.02 if kind == "folder" else 2.05) + 50_000_000:
            raise StudioError(f"Not enough space in the library: this client needs {manifest.get('bytes', 0) / 1e9:.1f} GB.")
    except Exception:
        if remove_after:
            path.unlink(missing_ok=True)
        raise

    def work(job):
        job["stage"] = "Copying and checking every file"
        try:
            if kind == "folder":
                return place_project(path, manifest, user, job)
            job["total_bytes"] = manifest.get("bytes", 0)
            unpack = library() / f".unpacking-{secrets.token_hex(4)}"
            try:
                with zipfile.ZipFile(path) as zf:
                    root = next(n.split("/")[0] for n in zf.namelist() if n.endswith("/" + PROJECT_MANIFEST))
                    for info in zf.infolist():
                        if info.is_dir() or not info.filename.startswith(root + "/"):
                            continue
                        target = (unpack / info.filename[len(root) + 1:]).resolve()
                        if unpack.resolve() not in target.parents:  # a path in the zip trying to escape
                            raise StudioError("That .zip has a file outside its project folder.")
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(info) as fi, open(target, "wb") as fo:
                            while True:
                                check_stop(job)
                                chunk = fi.read(8 << 20)
                                if not chunk:
                                    break
                                fo.write(chunk)
                                job["done_bytes"] += len(chunk)
                return place_project(unpack, manifest, user, job, move=True)
            finally:
                if unpack.exists():
                    shutil.rmtree(unpack, ignore_errors=True)
        finally:
            if remove_after:
                path.unlink(missing_ok=True)
    return start_job("project-import", f"Bringing in {manifest['name']}", user, work)


# ---------------------------------------------------------------- the online Shared folder
#
# Styles uploaded here can be downloaded into Editors.Hub on any computer signed in to the same GitHub account.
# It's a private GitHub repository (<you>/editors-hub-styles); each style is one release holding the style as a .zip
# in parts of at most 1.9 GB (GitHub's limit is 2 GB a file) and a short description to list it by.

ONLINE_PART = 1_900_000_000
ONLINE_MARK = "editors-hub-style:"
ONLINE_REPO_NAME = "editors-hub-styles"


def gh(*args, timeout=900, check=True):
    exe = shutil.which("gh")
    if not exe:
        raise StudioError("GitHub's tool (gh) isn't on this computer yet. Ask Claude to install it and sign you in to GitHub.")
    r = subprocess.run([exe, *args], capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=timeout, cwd=str(Path.home()), stdin=subprocess.DEVNULL)
    if check and r.returncode != 0:
        msg = first_line_of((r.stderr or r.stdout or "").strip()) or "GitHub didn't answer"
        if "auth login" in msg or "not logged" in msg.lower():
            msg = "This computer isn't signed in to GitHub. Ask Claude to sign you in with gh."
        raise StudioError(msg)
    return r


def first_line_of(text):
    return next((line.strip() for line in text.splitlines() if line.strip()), "")


def online_repo():
    if settings().get("online_repo"):
        return settings()["online_repo"]
    login = gh("api", "user", "--jq", ".login", timeout=30).stdout.strip()
    return f"{login}/{ONLINE_REPO_NAME}"


def online_styles():
    repo = online_repo()
    r = gh("api", f"repos/{repo}/releases?per_page=100", timeout=60, check=False)
    if r.returncode != 0:
        if "Not Found" in (r.stdout + r.stderr):
            return repo, []  # nothing uploaded yet: the folder is made with the first upload
        raise StudioError(first_line_of(r.stderr) or "GitHub didn't answer")
    out = []
    for rel in json.loads(r.stdout or "[]"):
        if not rel.get("tag_name", "").startswith("style-"):
            continue
        info = {}
        for line in (rel.get("body") or "").splitlines():
            if line.startswith(ONLINE_MARK):
                try:
                    info = json.loads(line[len(ONLINE_MARK):])
                except ValueError:
                    pass
        parts = [a for a in rel.get("assets", []) if ".zip." in a["name"]]
        complete = info.get("parts") == len(parts) and all(a.get("state", "uploaded") == "uploaded" for a in parts)
        out.append({**info, "tag": rel["tag_name"], "name": info.get("name") or rel.get("name") or rel["tag_name"],
                    "uploaded": rel.get("published_at"), "complete": complete, "release_id": rel.get("id"),
                    "size": sum(a["size"] for a in parts),
                    "assets": sorted(({"name": a["name"], "id": a["id"], "size": a["size"]} for a in parts), key=lambda a: a["name"])})
    return repo, sorted(out, key=lambda x: x.get("uploaded") or "", reverse=True)


class CountingReader:
    """Hands a file to an upload a bit at a time, counting every byte sent."""

    def __init__(self, f, job):
        self.f, self.job = f, job

    def read(self, n=-1):
        check_stop(self.job)
        data = self.f.read(1 << 20 if n is None or n < 0 else min(n, 1 << 20))
        self.job["done_bytes"] += len(data)
        return data


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def github_upload_part(repo, release_id, path, token, job):
    for attempt in range(3):
        before = job["done_bytes"]
        try:
            with open(path, "rb") as f:
                req = urllib.request.Request(
                    f"https://uploads.github.com/repos/{repo}/releases/{release_id}/assets?name={urllib.parse.quote(path.name)}",
                    data=CountingReader(f, job), method="POST",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream",
                             "Content-Length": str(path.stat().st_size), "Accept": "application/vnd.github+json"})
                with urllib.request.urlopen(req, timeout=900) as r:
                    return json.loads(r.read() or b"{}")
        except Exception as e:
            if job.get("stop"):
                raise JobStopped()
            job["done_bytes"] = before
            listing = gh("api", f"repos/{repo}/releases/{release_id}/assets", timeout=60, check=False)
            for a in json.loads(listing.stdout or "[]") if listing.returncode == 0 else []:
                if a.get("name") == path.name:  # a half-sent part blocks the name: clear it before trying again
                    gh("api", "-X", "DELETE", f"repos/{repo}/releases/assets/{a['id']}", timeout=60, check=False)
            if attempt == 2:
                raise StudioError(f"Uploading {path.name} kept failing ({e}). Check the internet and try again.")
            job["stage"] = f"Retrying {path.name} (the connection dropped)"
            time.sleep(5 * (attempt + 1))


def github_download_part(repo, asset, dest, token, job):
    for attempt in range(3):
        before = job["done_bytes"]
        try:
            req = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases/assets/{asset['id']}",
                                         headers={"Authorization": f"Bearer {token}", "Accept": "application/octet-stream"})
            try:
                resp = urllib.request.build_opener(_NoRedirect).open(req, timeout=120)
            except urllib.error.HTTPError as e:  # GitHub points to where the file is stored; go there without the key
                if e.code not in (301, 302, 303, 307, 308):
                    raise
                resp = urllib.request.urlopen(e.headers["Location"], timeout=900)
            with resp, open(dest, "wb") as out:
                while True:
                    check_stop(job)
                    chunk = resp.read(1 << 20)
                    if not chunk:
                        break
                    out.write(chunk)
                    job["done_bytes"] += len(chunk)
            if dest.stat().st_size != asset["size"]:
                raise StudioError("the download stopped part way")
            return
        except Exception as e:
            if job.get("stop"):
                raise JobStopped()
            job["done_bytes"] = before
            if attempt == 2:
                raise StudioError(f"Downloading {asset['name']} kept failing ({e}). Check the internet and try again.")
            job["stage"] = f"Retrying {asset['name']} (the connection dropped)"
            time.sleep(5 * (attempt + 1))


class PartWriter:
    """A file that rolls over to name.001, .002... every `size` bytes; zipfile writes into it as it would a stream."""

    def __init__(self, folder, stem, size, job):
        self.folder, self.stem, self.size, self.job = folder, stem, size, job
        self.parts, self.cur, self.left = [], None, 0

    def write(self, data):
        check_stop(self.job)
        view = memoryview(data)
        while view:
            if self.left == 0:
                if self.cur:
                    self.cur.close()
                path = self.folder / f"{self.stem}.{len(self.parts) + 1:03d}"
                self.parts.append(path)
                self.cur, self.left = open(path, "wb"), self.size
            take = min(len(view), self.left)
            self.cur.write(view[:take])
            self.left -= take
            self.job["done_bytes"] += take
            view = view[take:]
        return len(data)

    def flush(self):
        if self.cur:
            self.cur.flush()

    def close(self):
        if self.cur:
            self.cur.close()
            self.cur = None


def upload_style_online(style_id, user=None):
    sdir = style_dir(style_id, user)
    meta = style_meta(sdir)
    if not can_manage(meta, user):
        raise auth.Forbidden("Only the person who made this style, or the owner, can put it online.")
    repo = online_repo()
    files = transfer_files(sdir)
    manifest = style_manifest(sdir, files)
    if shutil.disk_usage(library()).free < manifest["bytes"] * 1.05 + 100_000_000:
        raise StudioError(f"Not enough space to pack it: uploading needs about {manifest['bytes'] / 1e9:.1f} GB free for a moment.")
    tag = f"style-{style_id}"

    def work(job):
        job["total_bytes"] = manifest["bytes"]  # first the packing; the bar then starts again for the upload itself
        job["stage"] = "Connecting to the online Shared folder"
        token = gh("auth", "token", timeout=30).stdout.strip()
        if gh("repo", "view", repo, "--json", "name", timeout=60, check=False).returncode != 0:
            gh("repo", "create", repo, "--private", "--add-readme", "--description",
               "Editors.Hub online Shared folder: styles to download into Editors.Hub on any computer.", timeout=120)
        tmp = library() / f".online-{secrets.token_hex(4)}"
        tmp.mkdir()
        try:
            job["stage"] = "Packing the style"
            writer = PartWriter(tmp, f"{style_id}{ZIP_SUFFIX}", ONLINE_PART, job)
            with zipfile.ZipFile(writer, "w", zipfile.ZIP_STORED, allowZip64=True) as zf:
                zf.writestr(f"{style_id}/{STYLE_MANIFEST}", json.dumps(manifest, indent=1))
                for rel, f in files:
                    zf.write(f, f"{style_id}/{rel}")
            writer.close()
            job["done_bytes"], job["total_bytes"] = 0, sum(p.stat().st_size for p in writer.parts)  # now: how much is uploaded
            maker_email, maker_name = meta.get("maker"), meta.get("maker_name")
            summary = {"id": style_id, "name": meta["name"], "client": meta.get("client", ""),
                       "notes": (meta.get("notes") or "")[:400], "palette": meta.get("palette", [])[:8],
                       "maker": maker_email, "maker_name": maker_name, "bytes": manifest["bytes"],
                       "videos": len(list(sdir.glob("videos/*/video.json"))), "parts": len(writer.parts),
                       "uploaded_by": (user or {}).get("username") or _maker(None)[1], "studio_version": manifest["studio_version"]}
            body = (f"{meta['name']}: a style for Editors.Hub. Download it from Add a style > From the online Shared "
                    f"folder.\n\n{ONLINE_MARK}{json.dumps(summary)}")
            check_stop(job)
            job["stage"] = "Getting the online folder ready"
            gh("release", "delete", tag, "--repo", repo, "--yes", "--cleanup-tag", timeout=120, check=False)
            made = gh("api", "-X", "POST", f"repos/{repo}/releases", "-f", f"tag_name={tag}", "-f", f"name={meta['name']}",
                      "-f", f"body={body}", timeout=120)
            release_id = json.loads(made.stdout)["id"]
            try:
                for n, part in enumerate(writer.parts, 1):
                    job["stage"] = f"Uploading part {n} of {len(writer.parts)}" if len(writer.parts) > 1 else "Uploading"
                    github_upload_part(repo, release_id, part, token, job)
            except BaseException:
                # nobody should download half a style: the unfinished online copy goes, and the style is no longer online
                job["stage"] = "Removing the unfinished online copy"
                gh("release", "delete", tag, "--repo", repo, "--yes", "--cleanup-tag", timeout=120, check=False)
                with LOCK:
                    data = read_json(sdir / "style.json", {}) or {}
                    if data.pop("online", None) is not None:
                        write_json(sdir / "style.json", data)
                raise
            with LOCK:
                data = read_json(sdir / "style.json", {}) or {}
                data["online"] = {"repo": repo, "tag": tag, "at": now()}
                write_json(sdir / "style.json", data)
            return {"name": meta["name"], "repo": repo, "bytes": manifest["bytes"], "parts": len(writer.parts)}
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return start_job("online-upload", f"Uploading {meta['name']}", user, work, style=style_id)


def download_online_style(tag, where="mine", user=None):
    if user is not None and user["role"] == "reviewer":
        raise auth.Forbidden("Your account can't do that. Ask the owner.")
    repo, items = online_styles()
    item = next((i for i in items if i["tag"] == tag), None)
    if not item:
        raise NotFound("That style isn't in the online Shared folder any more.")
    if not item["complete"]:
        raise StudioError("That style is still being uploaded (or its upload stopped). Try again later.")
    if shutil.disk_usage(library()).free < item["size"] * 2.1 + 100_000_000:
        raise StudioError(f"Not enough space: downloading needs about {item['size'] * 2 / 1e9:.1f} GB free for a moment.")

    def work(job):
        job["total_bytes"] = item["size"]  # first the download itself; the bar then starts again for unpacking
        job["stage"] = "Connecting to the online Shared folder"
        token = gh("auth", "token", timeout=30).stdout.strip()
        tmp = library() / f".online-{secrets.token_hex(4)}"
        tmp.mkdir()
        try:
            names = [a["name"] for a in item["assets"]]
            for n, asset in enumerate(item["assets"], 1):
                job["stage"] = f"Downloading part {n} of {len(names)}" if len(names) > 1 else "Downloading"
                github_download_part(repo, asset, tmp / asset["name"], token, job)
            job["stage"] = "Putting the parts together"
            whole = tmp / f"{item['id']}{ZIP_SUFFIX}"
            with open(whole, "wb") as out:
                for name in names:
                    with open(tmp / name, "rb") as part:
                        shutil.copyfileobj(part, out, 8 << 20)
                    (tmp / name).unlink()
            job["stage"] = "Unpacking and checking every file"
            job["done_bytes"] = 0
            inner = import_style_from(whole, where, user, remove_after=True)
            while inner["state"] == "running":
                if job.get("stop"):
                    inner["stop"] = True
                job["done_bytes"], job["total_bytes"] = inner["done_bytes"], inner["total_bytes"] or item["size"]
                time.sleep(0.3)
            if inner["state"] == "stopped":
                raise JobStopped()
            if inner["state"] != "done":
                raise StudioError(inner["message"])
            return {**inner["result"], "from": f"{repo} ({tag})"}
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return start_job("online-download", f"Downloading {item['name']}", user, work, style=item.get("id"))


def remove_online_style(tag, user=None):
    repo, items = online_styles()
    item = next((i for i in items if i["tag"] == tag), None)
    if not item:
        raise NotFound("That style isn't in the online Shared folder.")
    if user is not None and user["role"] != "owner" and item.get("maker") != user["email"]:
        raise auth.Forbidden("Only the person who made this style, or the owner, can take it out of the online folder.")
    gh("release", "delete", tag, "--repo", repo, "--yes", "--cleanup-tag", timeout=120)
    sdir = style_dirs().get(item.get("id", ""))
    if sdir:
        with LOCK:
            data = read_json(sdir / "style.json", {}) or {}
            if (data.get("online") or {}).get("tag") == tag:
                data.pop("online")
                write_json(sdir / "style.json", data)
    return {"removed": item["name"]}


def transfer_places():
    """Where a style can be saved or found: drives, cloud folders, Desktop and Downloads, on Mac and Windows."""
    home = Path.home()
    roots = [(home / "Desktop", "Desktop"), (home / "Downloads", "Downloads"), (home / "Documents", "Documents")]
    if WINDOWS:
        roots += [(p, p.name) for p in sorted(home.glob("OneDrive*")) if p.is_dir()]
        roots += [(Path(f"{d}:\\"), f"Drive {d}:") for d in "DEFGHIJKLMNOPQRSTUVWXYZ" if Path(f"{d}:\\").exists()]
    elif sys.platform == "darwin":
        roots += [(p, p.name.split("-")[0] if "-" in p.name else p.name) for p in sorted((home / "Library" / "CloudStorage").glob("*")) if p.is_dir()]
        roots += [(p, f"Drive {p.name}") for p in sorted(Path("/Volumes").glob("*")) if p.is_dir() and not p.is_symlink()]
    places = []
    for path, label in roots:
        try:
            places.append({"path": str(path), "label": label, "free": shutil.disk_usage(path).free})
        except OSError:
            continue
    return places


def find_exports(manifest_name=STYLE_MANIFEST, zip_suffix=ZIP_SUFFIX):
    found = []
    for place in transfer_places():
        root = Path(place["path"])
        try:
            level1 = [p for p in root.iterdir() if not p.name.startswith(".")][:400]
        except OSError:
            continue
        candidates = list(level1)
        for d in level1:
            if d.is_dir():
                try:
                    candidates += [p for p in d.iterdir() if not p.name.startswith(".")][:200]
                except OSError:
                    pass
        for c in candidates:
            try:
                if (c.is_dir() and (c / manifest_name).is_file()) or (c.is_file() and c.name.endswith(zip_suffix)):
                    m = read_json(c / manifest_name) if c.is_dir() else None
                    found.append({"path": str(c), "name": (m or {}).get("name") or c.name[:-len(zip_suffix)],
                                  "bytes": (m or {}).get("bytes") or c.stat().st_size, "where": place["label"],
                                  "kind": "folder" if c.is_dir() else "zip"})
            except OSError:
                continue
    return found


def folder_suggestions():
    out = [str(ROOT / "library")]
    home = Path.home()
    out.append(str(home / ("Videos" if WINDOWS else "Movies") / "Editors.Hub"))
    if sys.platform == "darwin":
        for vol in sorted(Path("/Volumes").glob("*")):
            if vol.is_dir() and not vol.is_symlink() and vol.name not in ("Macintosh HD", "Recovery"):
                out.append(str(vol / "Editors.Hub"))
    elif WINDOWS:
        for letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
            if Path(f"{letter}:\\").exists():
                out.append(f"{letter}:\\Editors.Hub")
    current = settings()["library"]
    return {"current": current, "confirmed": bool(settings().get("library_confirmed")),
            "suggestions": [current] + [x for x in out if x != current]}


hubsetup.configure(workdir=setup_workdir, skills=setup_skills, install_skills=setup_install_skills,
                   keys=setup_keys, transcriber=transcriber)


def auto_install_skills():
    try:
        restored = restore_profile()
        done = install_skills()
        filled = fill_skills()
    except Exception as e:  # never stop Home starting over a skill
        print(f"skills: couldn't install ({e})", flush=True)
        return
    if restored:
        print(f"creator profile put in place: {restored['brand']} ({restored['creator']})", flush=True)
    for key in ("installed", "updated", "failed"):
        if done[key]:
            print(f"skills {key}: {', '.join(done[key])}", flush=True)
    if filled:
        print(f"skills filled from the profile: {', '.join(filled)}", flush=True)


# ---------------------------------------------------------------- web server

class Handler(BaseHTTPRequestHandler):
    server_version = "EditorsHub/1.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        self.handle_any("GET")

    def do_HEAD(self):
        self.handle_any("HEAD")

    def do_POST(self):
        self.handle_any("POST")

    def do_PATCH(self):
        self.handle_any("PATCH")

    def do_PUT(self):
        UPLOADING[0] += 1
        try:
            self._do_put()
        finally:
            UPLOADING[0] -= 1

    def _do_put(self):
        self.handle_any("PUT")

    def do_DELETE(self):
        self.handle_any("DELETE")

    # -- replies

    def send_body(self, body, ctype, status=200, extra=()):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in extra:
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def send_json(self, data, status=200):
        self.send_body(json.dumps(data).encode(), "application/json", status)

    def send_file(self, path):
        size = path.stat().st_size
        ctype = MEDIA_TYPES.get(path.suffix.lower()) or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        start, end, status = 0, size - 1, 200
        m = re.fullmatch(r"bytes=(\d*)-(\d*)", (self.headers.get("Range") or "").strip())
        if m and size:
            a, b = m.groups()
            if a == "" and b:
                start = max(0, size - int(b))
            else:
                start = int(a or 0)
                end = min(size - 1, int(b)) if b else size - 1
            if start > end:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            status = 206
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1 if size else 0))
        self.send_header("Cache-Control", "no-cache")
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        if self.command == "HEAD" or not size:
            return
        try:
            with open(path, "rb") as f:
                f.seek(start)
                left = end - start + 1
                while left > 0:
                    chunk = f.read(min(1 << 20, left))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    left -= len(chunk)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def read_json_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length > 1_000_000:
            raise StudioError("request too large")
        raw = self.rfile.read(length) if length else b""
        try:
            return json.loads(raw or b"{}")
        except json.JSONDecodeError:
            raise StudioError("bad JSON")

    # -- access: signed-in accounts only; admin things for the owner only

    def host_ok(self):
        if wifi_on():
            return True
        port = self.server.server_port
        return self.headers.get("Host", "") in {f"127.0.0.1:{port}", f"localhost:{port}"}

    def local(self):
        return self.client_address[0] in ("127.0.0.1", "::1")

    def session_token(self):
        got = cookies.SimpleCookie(self.headers.get("Cookie", "")).get("ehsession")
        return got.value if got else ""

    def set_session(self, token, location=None, data=None):
        cookie = f"ehsession={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age={auth.SESSION_TTL if token else 0}"
        if location:
            self.send_response(303)
            self.send_header("Set-Cookie", cookie)
            self.send_header("Location", location)
            self.send_header("Content-Length", "0")
            self.end_headers()
        else:
            self.send_body(json.dumps(data or {}).encode(), "application/json", extra=[("Set-Cookie", cookie)])

    def need(self, *roles):
        if self.user["role"] not in roles:
            raise auth.Forbidden("Only the studio owner can do that." if roles == ("owner",) else
                                 "Your account can't do that. Ask the owner.")

    def handle_any(self, method):
        if not self.host_ok():
            return self.send_body(b"wrong address", "text/plain", 403)
        url = urllib.parse.urlsplit(self.path)
        path = urllib.parse.unquote(url.path)
        query = urllib.parse.parse_qs(url.query)
        parts = [p for p in path.split("/") if p]
        try:
            # the private link `studio.py open` prints signs the owner in, but only on this computer
            token = query.pop("t", [None])[0]
            if token is not None and method in ("GET", "HEAD"):
                rest = urllib.parse.urlencode(query, doseq=True)
                target = url.path + (f"?{rest}" if rest else "")
                if self.local() and secrets.compare_digest(token, settings()["token"]):
                    session = accounts().session_for_owner(self.headers.get("User-Agent", ""))
                    if session:
                        return self.set_session(session, target)
                return self.send_body(b"", "text/plain", 303, extra=[("Location", "/signin?next=" + urllib.parse.quote(target))])
            if parts[:1] == ["approve"] or parts[:2] == ["api", "approval"]:
                return self.approval_route(method, parts)
            if approval.status(DATA)["required"] and parts[:1] != ["static"]:  # nothing here until the owner has let this computer in
                if parts[:1] in (["api"], ["media"]):
                    return self.send_json({"error": "This computer needs approval from the studio's owner.", "approve": True}, 401)
                return self.send_body(b"", "text/plain", 303, extra=[("Location", "/approve")])
            if parts[:2] == ["api", "auth"] or parts[:1] in (["static"], ["signin"]):
                return self.public_route(method, parts, query)
            self.user = accounts().user_for(self.session_token())
            if not self.user:
                if parts[:1] == ["api"] or parts[:1] == ["media"]:
                    return self.send_json({"error": "Sign in first.", "signin": True}, 401)
                return self.send_body(b"", "text/plain", 303, extra=[("Location", "/signin?next=" + urllib.parse.quote(path))])
            self.route(method, path, query)
        except (StudioError, auth.AuthError) as e:
            self.send_json({"error": str(e)}, e.status)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass
        except Exception as e:  # keep Home up whatever one request does
            self.send_json({"error": f"{type(e).__name__}: {e}"}, 500)

    def approval_route(self, method, parts):
        if method in ("GET", "HEAD"):
            if parts == ["approve"]:
                return self.send_file(WEB / "approve.html")
            if parts == ["api", "approval", "status"]:
                return self.send_json(approval.status(DATA))
            raise NotFound("not found")
        if not self.local():
            raise auth.Forbidden("Approval is asked for on the studio's own computer.")
        body = self.read_json_body()
        email, username = str(body.get("email", "")).strip().lower(), str(body.get("username", "")).strip()
        try:
            if parts == ["api", "approval", "request"]:
                approval.request_code(email, username)
                return self.send_json({"ok": True})
            if parts == ["api", "approval", "verify"]:
                passed = approval.verify_code(DATA, email, body.get("code", ""))
                acc = accounts()
                agent = self.headers.get("User-Agent", "")
                if not acc.users():  # a new studio: they own the copy on their own computer
                    return self.set_session(acc.adopt_owner(passed["email"], passed.get("username") or username, agent), data={"ok": True, "next": "/"})
                if passed["email"] == acc.owner_email:
                    return self.set_session(acc.session_for_owner(agent), data={"ok": True, "next": "/"})
                return self.send_json({"ok": True, "next": "/signin"})
        except approval.ApprovalError as e:
            raise StudioError(str(e))
        raise NotFound("not found")

    def public_route(self, method, parts, query):
        acc = accounts()
        if method in ("GET", "HEAD"):
            if parts == ["signin"]:
                return self.send_file(WEB / "signin.html")
            if parts[0] == "static" and len(parts) == 2 and (WEB / parts[1]).is_file():
                return self.send_file(WEB / parts[1])
            if parts == ["api", "auth", "me"]:
                user = acc.user_for(self.session_token())
                return self.send_json({"user": acc.public(user), "owner_exists": acc.owner_exists(),
                                       "email_ready": acc.mail_status()["ready"]})
            raise NotFound("not found")
        body = self.read_json_body()
        agent = self.headers.get("User-Agent", "")
        if parts == ["api", "auth", "signup"]:
            return self.send_json(acc.request_code("signup", body.get("email"), body.get("username")))
        if parts == ["api", "auth", "signin"]:
            return self.send_json(acc.request_code("signin", body.get("login")))
        if parts == ["api", "auth", "connect-email"]:
            # the owner's first sign-in on a new computer: connect their Gmail right there, then email the waiting code
            email = (body.get("email") or "").strip().lower()
            if not self.local() or email != acc.owner_email:
                raise auth.Forbidden("Only the owner, on the studio's own computer, can connect the email.")
            if acc.mail_status()["ready"]:
                raise auth.AuthError("Email is already connected. The owner can change it on the Team page.")
            acc.set_mail(acc.owner_email, body.get("password"), test_email=False)
            return self.send_json(acc.resend_code(email))
        if parts == ["api", "auth", "verify"]:
            token, user = acc.verify(body.get("login"), body.get("code"), agent)
            return self.set_session(token, data={"user": acc.public(user)})
        if parts == ["api", "auth", "signout"]:
            acc.sign_out(self.session_token())
            return self.set_session("", data={"ok": True})
        raise NotFound("not found")

    def route(self, method, path, query):
        parts = [p for p in path.split("/") if p]
        q = lambda k, d="": query.get(k, [d])[0]
        acc = accounts()
        role = self.user["role"]
        # a video inside someone else's private style doesn't exist for this person
        if parts[:2] == ["api", "videos"] and len(parts) >= 3:
            can_see_video(parts[2], self.user)
        if parts[:1] == ["media"] and len(parts) >= 2:
            can_see_video(parts[1], self.user)

        if method in ("GET", "HEAD"):
            if not parts:
                return self.send_file(WEB / "home.html")
            if parts[0] == "review" and len(parts) == 2:
                return self.send_file(WEB / "review.html")
            if parts[0] == "style" and len(parts) == 2:
                self.need("owner", "editor")
                return self.send_file(WEB / "style.html")
            if parts[0] == "style-media" and len(parts) >= 3:
                self.need("owner", "editor")
                sdir = style_dir(parts[1], self.user).resolve()
                target = sdir.joinpath(*parts[2:]).resolve()
                if sdir not in target.parents or not target.is_file():
                    raise NotFound("no such file")
                return self.send_file(target)
            if parts[0] == "project" and len(parts) == 2:
                self.need("owner", "editor")
                return self.send_file(WEB / "project.html")
            if parts[0] == "project-media" and len(parts) >= 3:
                self.need("owner", "editor")
                pdir = project_dir(parts[1]).resolve()
                target = pdir.joinpath(*parts[2:]).resolve()
                if pdir not in target.parents or not target.is_file():
                    raise NotFound("no such file")
                return self.send_file(target)
            if parts[:2] == ["api", "projects"] and len(parts) >= 3:
                self.need("owner", "editor")
                if len(parts) == 3:
                    return self.send_json(project_page(parts[2], self.user))
                if parts[3:4] == ["section"] and len(parts) == 5:
                    return self.send_json({"items": project_files(project_dir(parts[2]), parts[4])})
                if parts[3:] == ["download"]:
                    return self.send_project_zip(parts[2])
            if parts == ["api", "online"]:
                self.need("owner", "editor")
                try:
                    repo, items = online_styles()
                    return self.send_json({"ready": True, "repo": repo, "styles": items})
                except StudioError as e:
                    return self.send_json({"ready": False, "message": str(e), "styles": []})
            if parts == ["api", "trash"]:
                self.need("owner", "editor")
                return self.send_json({"items": list_trash(self.user)})
            if parts == ["api", "transfer"]:
                self.need("owner", "editor")
                return self.send_json({"places": transfer_places(),
                                       "exports": find_exports(PROJECT_MANIFEST, PROJECT_ZIP_SUFFIX) if q("type") == "project" else find_exports(),
                                       "library_free": shutil.disk_usage(library()).free})
            if parts == ["api", "jobs"]:
                return self.send_json({"jobs": recent_jobs(self.user)})
            if parts[:2] == ["api", "jobs"] and len(parts) == 3:
                job = JOBS.get(parts[2])
                if not job or (job["by"] != self.user["email"] and role != "owner"):
                    raise NotFound("no such job")
                return self.send_json(job)
            if parts[:2] == ["api", "styles"] and parts[3:] == ["download"]:
                return self.send_style_zip(parts[2])
            if parts[:2] == ["api", "styles"] and len(parts) >= 3:
                self.need("owner", "editor")
                if len(parts) == 3:
                    return self.send_json(style_page(parts[2], self.user))
                if parts[3:4] == ["section"] and len(parts) == 5:
                    if parts[4] not in {sid for sid, _, _ in SECTIONS}:
                        raise NotFound("no such section")
                    return self.send_json({"items": section_items(style_dir(parts[2], self.user), parts[4])})
                if parts[3:] == ["browse"]:
                    return self.send_json(browse_style(parts[2], q("path"), self.user))
            if parts[0] == "media" and len(parts) >= 3:
                folder = Path(load_video(parts[1])["folder"]).resolve()
                target = folder.joinpath(*parts[2:]).resolve()
                if folder not in target.parents or not target.is_file():
                    raise NotFound("no such file")
                return self.send_file(target)
            if parts == ["api", "state"]:
                return self.send_json(self.state())
            if parts == ["api", "setup"]:
                return self.send_json(hubsetup.snapshot())
            if parts[:2] == ["api", "videos"] and len(parts) == 3:
                view = video_view(load_video(parts[2]))
                if role == "reviewer":
                    for private in ("reviewers", "updates", "render_request", "last_render_choice", "render_options", "broll"):
                        view.pop(private, None)
                return self.send_json(view)
            self.need("owner")
            if parts == ["api", "skills"]:
                return self.send_json({"skills": list_skills(), "folder": str(CLAUDE_SKILLS),
                                       "profile": profile_summary(PROFILE_PACK)})
            if parts == ["api", "team"]:
                return self.send_json(self.team())
            if parts == ["api", "keys"]:
                return self.send_json({"keys": keys.status(needed_keys()), "file": str(keys.KEYS_FILE)})
            if parts == ["api", "setup", "folders"]:
                return self.send_json(folder_suggestions())
            raise NotFound("not found")

        if method == "PUT" and parts == ["api", "import", "upload"]:
            self.need("owner", "editor")
            if not q("name").lower().endswith(".zip"):
                raise StudioError("Choose the style's .zip file.")
            incoming = self.receive(library() / ".incoming", q("name"))
            try:
                job = import_style_from(incoming, q("where", "mine"), self.user, remove_after=True)
            except Exception:
                incoming.unlink(missing_ok=True)
                raise
            return self.send_json(job)
        if method == "PUT" and parts[:2] == ["api", "styles"] and parts[3:] == ["upload"]:
            self.need("owner", "editor")
            return self.upload_to_style(parts[2], q("section", "auto"), q("name", "file"))
        if method == "PUT" and parts == ["api", "import-project", "upload"]:
            self.need("owner", "editor")
            if not q("name").lower().endswith(".zip"):
                raise StudioError("Choose the project's .zip file.")
            incoming = self.receive(library() / ".incoming", q("name"))
            return self.send_json(import_project_from(incoming, self.user, remove_after=True))
        if method == "PUT" and parts[:2] == ["api", "projects"] and parts[3:] == ["upload"]:
            self.need("owner", "editor")
            return self.upload_to_project(parts[2], q("section", "auto"), q("name", "file"))
        if method == "PUT" and parts[:2] == ["api", "videos"] and len(parts) == 4 and parts[3] == "upload":
            if q("kind") != "attach":  # anyone can attach a screenshot to a note; footage and drafts are for makers
                self.need("owner", "editor")
            return self.upload(parts[2], q("kind", "raw"), q("name", "upload.mp4"), q("note"))

        body = self.read_json_body()
        # everyone signed in: notes, approving, asking for changes
        if parts[:2] == ["api", "videos"] and len(parts) >= 4 and parts[3] == "notes":
            vid = parts[2]
            if method == "POST" and len(parts) == 4:
                return self.send_json(add_note(vid, body.get("version"), body.get("t", 0), body.get("text", ""),
                                               self.user["username"], self.user["email"], body.get("attachments")))
            if len(parts) == 5:
                note = find_note(load_video(vid), parts[4])
                if role == "reviewer" and note.get("author_email") != self.user["email"]:
                    raise auth.Forbidden("You can only change your own notes.")
                if method == "PATCH":
                    return self.send_json(update_note(vid, parts[4], body))
                if method == "DELETE":
                    delete_note(vid, parts[4])
                    return self.send_json({"ok": True})
        if method == "POST" and parts[:2] == ["api", "videos"] and len(parts) == 3:
            vid = parts[2]
            if "approve" in body:
                approve(vid, body["approve"])
            elif "status" in body:
                if role == "reviewer" and body["status"] != "changes":
                    raise auth.Forbidden("Reviewers can approve or ask for changes.")
                set_status(vid, body["status"])
            return self.send_json(video_view(load_video(vid)))

        if method == "POST" and parts == ["api", "me", "username"]:
            rename_account(self.user["email"], body.get("username"))
            return self.send_json({"user": acc.public(acc.users()[self.user["email"]])})
        # editors and the owner: making things, and sending notes to Claude
        self.need("owner", "editor")
        if method == "POST" and parts[:2] == ["api", "videos"] and parts[3:] == ["feedback"]:
            submit_feedback(parts[2], self.user["username"])
            return self.send_json(video_view(load_video(parts[2])))
        if method == "POST" and parts[:2] == ["api", "videos"] and parts[3:] == ["style"]:
            set_video_style(parts[2], body.get("style", ""), self.user)
            return self.send_json(video_view(load_video(parts[2])))
        if method == "POST" and parts[:2] == ["api", "videos"] and parts[3:] == ["broll"]:
            if "mode" in body:
                set_broll_mode(parts[2], body["mode"])
            elif "picks" in body:
                set_broll_picks(parts[2], body["picks"])
            elif "change" in body:
                set_broll_review(parts[2], body["change"])
            else:
                raise StudioError("That answer can't be read.")
            return self.send_json(video_view(load_video(parts[2])))
        if method == "POST" and parts[:2] == ["api", "videos"] and parts[3:] == ["render-choice"]:
            set_render_choice(parts[2], body, self.user["username"])
            return self.send_json(video_view(load_video(parts[2])))
        if method == "POST" and parts[:2] == ["api", "videos"] and parts[3:] == ["reviewers"]:
            set_reviewer(parts[2], body.get("email"), not body.get("remove"))
            return self.send_json(video_view(load_video(parts[2])))
        if method == "POST" and parts[:2] == ["api", "videos"] and parts[3:] == ["live"]:
            if body.get("stop"):
                stop_live(parts[2])
            else:
                start_live(parts[2], body.get("project") or None)
            return self.send_json(video_view(load_video(parts[2])))
        if method == "POST" and parts == ["api", "styles"]:
            links = body.get("links") or []
            if not isinstance(links, list):
                raise StudioError("links has to be a list")
            return self.send_json(create_style(body.get("name", ""), body.get("client", ""), body.get("notes", ""),
                                               self.user, body.get("format", ""), links))
        if method == "POST" and parts[:2] == ["api", "jobs"] and parts[3:] == ["stop"]:
            return self.send_json(stop_job(parts[2], self.user))
        if method == "POST" and parts[:2] == ["api", "styles"] and parts[3:] == ["online"]:
            return self.send_json(upload_style_online(parts[2], self.user))
        if method == "POST" and parts[:2] == ["api", "online"] and parts[3:] == ["download"]:
            return self.send_json(download_online_style(parts[2], body.get("where", "mine"), self.user))
        if method == "DELETE" and parts[:2] == ["api", "online"] and len(parts) == 3:
            return self.send_json(remove_online_style(parts[2], self.user))
        if method == "POST" and parts[:2] == ["api", "styles"] and parts[3:] == ["rename"]:
            return self.send_json(rename_style(parts[2], body.get("name"), self.user))
        if method == "POST" and parts[:2] == ["api", "styles"] and parts[3:] == ["duplicate"]:
            return self.send_json(duplicate_style(parts[2], self.user))
        if method == "DELETE" and parts[:2] == ["api", "styles"] and len(parts) == 3:
            return self.send_json(delete_style(parts[2], self.user))
        if method == "DELETE" and parts[:2] == ["api", "trash"] and len(parts) == 3:
            return self.send_json(erase_deleted(parts[2], self.user))
        if method == "POST" and parts[:2] == ["api", "trash"] and parts[3:] == ["restore"]:
            return self.send_json(restore_style(parts[2], self.user))
        if method == "POST" and parts[:2] == ["api", "styles"] and parts[3:] == ["export"]:
            return self.send_json(export_style_to(parts[2], body.get("dest"), self.user))
        if method == "POST" and parts == ["api", "import"]:
            return self.send_json(import_style_from(body.get("path"), body.get("where", "mine"), self.user))
        if method == "POST" and parts[:2] == ["api", "styles"] and len(parts) == 3:
            return self.send_json(save_style_text(parts[2], body, self.user))
        if method == "POST" and parts[:2] == ["api", "styles"] and parts[3:] == ["share"]:
            return self.send_json(share_style(parts[2], bool(body.get("share", True)), self.user))
        if method == "POST" and parts == ["api", "projects"]:
            return self.send_json(create_project(body.get("name", ""), body.get("contact", ""), body.get("website", ""),
                                                 body.get("about", ""), body.get("brand", ""), self.user))
        if method == "POST" and parts == ["api", "import-project"]:
            return self.send_json(import_project_from(body.get("path"), self.user))
        if method == "POST" and parts[:2] == ["api", "projects"] and parts[3:] == ["export"]:
            return self.send_json(export_project_to(parts[2], body.get("dest"), self.user))
        if method == "POST" and parts[:2] == ["api", "projects"] and len(parts) == 3:
            return self.send_json(save_project(parts[2], body, self.user))
        if method == "DELETE" and parts[:2] == ["api", "projects"] and len(parts) == 3:
            return self.send_json(delete_project(parts[2], self.user))
        if method == "POST" and parts == ["api", "videos"]:
            v = create_video(body.get("style", ""), body.get("name", ""), body.get("brief", ""), user=self.user,
                             project=body.get("project", ""), training=bool(body.get("training")))
            return self.send_json({"id": v["id"]})
        if method == "POST" and parts == ["api", "reveal"]:
            if not self.local():
                raise auth.Forbidden("Folders open on the studio's own computer only.")
            if body.get("video"):
                can_see_video(body["video"], self.user)
            reveal(load_video(body["video"])["folder"] if body.get("video") else
                   style_dir(body["style"], self.user) if body.get("style") else
                   project_dir(body["project"]) if body.get("project") else library())
            return self.send_json({"ok": True})

        # the owner only: admin
        self.need("owner")
        if method == "POST" and parts == ["api", "settings"]:
            update_settings(body)
            return self.send_json(self.state())
        if method == "POST" and parts == ["api", "setup", "run"]:
            hubsetup.start_background(only=body.get("only"), log=lambda line: print(line, flush=True))
            time.sleep(0.3)
            return self.send_json(hubsetup.snapshot())
        if method == "POST" and parts == ["api", "setup", "workdir"]:
            folder = str(body.get("folder", "")).strip()
            update_settings({"library": folder, "library_confirmed": True})
            hubsetup.start_background(log=lambda line: print(line, flush=True))
            time.sleep(0.3)
            return self.send_json(hubsetup.snapshot())
        if method == "POST" and parts == ["api", "keys"]:
            try:
                if body.get("remove"):
                    keys.remove(body.get("env"))
                else:
                    keys.save(body.get("env"), body.get("value"))
            except ValueError as e:
                raise StudioError(str(e))
            hubsetup.start_background(log=lambda line: print(line, flush=True))  # setup carries on by itself
            return self.send_json({"keys": keys.status(needed_keys()), "file": str(keys.KEYS_FILE)})
        if method == "POST" and parts == ["api", "skills", "install"]:
            with LOCK:
                restore_profile()
                done = install_skills()
                done["filled"] = fill_skills()
            return self.send_json({**done, "skills": list_skills(), "folder": str(CLAUDE_SKILLS),
                                   "profile": profile_summary(PROFILE_PACK)})
        if method == "POST" and parts == ["api", "mail"]:
            if body.get("clear"):
                acc.clear_mail()
            else:
                acc.set_mail(body.get("user"), body.get("password"), body.get("host"), body.get("port"))
            return self.send_json(self.team())
        if parts[:2] == ["api", "team"] and len(parts) == 3:
            email = parts[2].lower()
            if method == "POST" and "role" in body:
                acc.set_role(email, body["role"])
            elif method == "POST" and body.get("cancel_code"):
                acc.cancel_code(email)
            elif method == "DELETE":
                acc.remove(email)
            return self.send_json(self.team())
        raise NotFound("not found")

    def team(self):
        acc = accounts()
        port = self.server.server_port
        return {"members": acc.team(), "pending": acc.pending(), "mail": acc.mail_status(), "alone": not approval.open_to_others(DATA),
                "owner_email": acc.owner_email, "lan": wifi_on(),
                "lan_urls": lan_addresses(port), "lan_live": self.server.server_address[0] != "127.0.0.1"}

    def state(self):
        s = settings()
        videos = []
        dirs, style_folders, project_folders = video_dirs(self.user), style_dirs(), project_dirs()
        for vid in dirs:
            try:
                videos.append(video_summary(load_video(vid, dirs), style_folders, project_folders))
            except StudioError:
                pass
        videos.sort(key=lambda v: v["updated"], reverse=True)
        styles = [] if self.user["role"] == "reviewer" else [
            {**st, "videos": sum(1 for v in videos if v["style"] == st["id"] and not v["project"]),
             "client_videos": sum(1 for v in videos if v["style"] == st["id"] and v["project"]), "mine": st.get("maker") == self.user["email"],
             "can_manage": can_manage(st, self.user)}
            for st in list_styles(self.user)]
        projects = [] if self.user["role"] == "reviewer" else [
            {**p, "videos": sum(1 for v in videos if v["project"] == p["id"]),
             "brand_files": sum(len(project_files(Path(p["folder"]), sec)) for sec, _ in PROJECT_SECTIONS),
             "can_edit": can_edit_project(p, self.user)}
            for p in list_projects()]
        me = accounts().public(self.user)
        visible = ("studio_name", "your_name", "library") if me["role"] == "owner" else ("studio_name",)
        return {"me": me, "version": APP_VERSION, "approval": approval.status(DATA), "settings": {k: s[k] for k in visible},
                "projects": projects, "styles": styles, "videos": videos, "statuses": STATUSES,
                "platform": "windows" if WINDOWS else "mac" if sys.platform == "darwin" else "linux"}

    def receive(self, folder, name, limit=20_000_000_000):
        """Stream the request body into folder/name (a fresh name if it's taken); returns the saved path."""
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            raise StudioError("empty upload")
        if length > limit:
            raise StudioError("that file is too big")
        folder.mkdir(parents=True, exist_ok=True)
        tmp = folder / f".upload-{secrets.token_hex(4)}"
        try:
            with open(tmp, "wb") as f:
                left = length
                while left > 0:
                    chunk = self.rfile.read(min(1 << 20, left))
                    if not chunk:
                        raise StudioError("the upload stopped part way")
                    f.write(chunk)
                    left -= len(chunk)
            dest = unique_path(folder, safe_filename(name))
            os.replace(tmp, dest)
            return dest
        finally:
            if tmp.exists():
                tmp.unlink()

    def send_style_zip(self, style_id):
        """Download: the style as one .zip, written straight to the browser while it's read (no size limit)."""
        sdir = can_take_style(style_id, self.user)
        files = transfer_files(sdir)
        manifest = style_manifest(sdir, files)
        name = safe_filename(manifest["name"]) + ZIP_SUFFIX
        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Disposition", f"attachment; filename=\"{name}\"; filename*=UTF-8''{urllib.parse.quote(name)}")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True
        try:
            with zipfile.ZipFile(self.wfile, "w", zipfile.ZIP_STORED, allowZip64=True) as zf:
                zf.writestr(f"{sdir.name}/{STYLE_MANIFEST}", json.dumps(manifest, indent=1))
                for rel, f in files:  # videos and images are compressed already: stored as they are, fast
                    zf.write(f, f"{sdir.name}/{rel}")
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def send_project_zip(self, project_id):
        """Download: the client as one .zip, written straight to the browser while it's read (no size limit)."""
        d = project_dir(project_id)
        files = transfer_files(d)
        manifest = project_manifest(d, files)
        name = safe_filename(manifest["name"]) + PROJECT_ZIP_SUFFIX
        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Disposition", f"attachment; filename=\"{name}\"; filename*=UTF-8''{urllib.parse.quote(name)}")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True
        try:
            with zipfile.ZipFile(self.wfile, "w", zipfile.ZIP_STORED, allowZip64=True) as zf:
                zf.writestr(f"{d.name}/{PROJECT_MANIFEST}", json.dumps(manifest, indent=1))
                for rel, f in files:
                    zf.write(f, f"{d.name}/{rel}")
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def upload_to_style(self, style_id, section, name):
        sdir = style_dir(style_id, self.user)
        if not style_page(style_id, self.user)["can_edit"]:
            raise auth.Forbidden("Only the person who made this style, or the owner, can add files to it.")
        if section == "auto":  # dropped on the overview: sorted by what the file is
            ext = Path(name).suffix.lower()
            section = next((sec for exts, sec in SORT_BY_TYPE if ext in exts), None)
            if section is None:
                folder = sdir / ("library/fonts" if (sdir / "library/fonts").is_dir() else "fonts") \
                    if ext in (".ttf", ".otf", ".woff", ".woff2") else sdir / "files"
                dest = self.receive(folder, name)
                return self.send_json({"section": "files", "file": dest.relative_to(sdir).as_posix()})
        if section not in {sid for sid, _, _ in SECTIONS}:
            raise StudioError("unknown section")
        dest = self.receive(section_target(sdir, section), name)
        label = next(label for sid, label, _ in SECTIONS if sid == section)
        self.send_json({"section": section, "label": label, "file": dest.relative_to(sdir).as_posix()})

    def upload_to_project(self, project_id, section, name):
        d = project_dir(project_id)
        if not can_edit_project(project_meta(d), self.user):
            raise auth.Forbidden("Only the person who made this project, or the owner, can add files to it.")
        section = project_section_for(name, section)
        dest = self.receive(d / section, name)
        label = next(label for sec, label in PROJECT_SECTIONS if sec == section)
        self.send_json({"section": section, "label": label, "file": dest.relative_to(d).as_posix()})

    def upload(self, vid, kind, name, note):
        if kind not in ("raw", "draft", "attach"):
            raise StudioError("kind must be raw, draft or attach")
        folder = Path(load_video(vid)["folder"])
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            raise StudioError("empty upload")
        tmp = folder / f".upload-{secrets.token_hex(4)}{Path(safe_filename(name)).suffix}"
        try:
            with open(tmp, "wb") as f:
                left = length
                while left > 0:
                    chunk = self.rfile.read(min(1 << 20, left))
                    if not chunk:
                        raise StudioError("the upload stopped part way")
                    f.write(chunk)
                    left -= len(chunk)
            if kind == "attach":
                if length > 50_000_000:
                    raise StudioError("attachments can be up to 50 MB")
                dest = unique_path(folder / "notes-files", safe_filename(name))
                shutil.move(str(tmp), str(dest))
                result = {"kind": "file", "file": f"notes-files/{dest.name}", "name": dest.name,
                          "image": dest.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".webp")}
            elif kind == "draft":
                result = {"version": add_draft(vid, tmp, note, move=True, original=safe_filename(name))}
            else:
                result = {"file": add_raw(vid, tmp, name=name, move=True)}
        finally:
            if tmp.exists():
                tmp.unlink()
        self.send_json(result)


# ---------------------------------------------------------------- starting and stopping Home

def home_url(path="/"):
    s = settings()
    return f"http://127.0.0.1:{s['port']}{path}?t={s['token']}"


def running(port):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/static/app.css", timeout=1) as r:
            return r.headers.get("Server", "").startswith("EditorsHub")
    except Exception:
        return False


def port_free(port):
    with socket.socket() as sock:
        return sock.connect_ex(("127.0.0.1", port)) != 0


def ensure_running():
    port = settings()["port"]
    if running(port):
        return
    if not port_free(port):
        raise StudioError(f"port {port} is used by another program; change \"port\" in {SETTINGS}")
    DATA.mkdir(parents=True, exist_ok=True)
    log = open(DATA / "server.log", "a")
    kwargs = {"stdout": log, "stderr": log, "stdin": subprocess.DEVNULL, "cwd": str(ROOT)}
    if WINDOWS:
        kwargs["creationflags"] = 0x00000008 | 0x00000200 | 0x08000000  # detached, own group, no window
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "serve"], **kwargs)
    for _ in range(50):
        time.sleep(0.1)
        if running(port):
            return
    raise StudioError(f"Home didn't start; see {DATA / 'server.log'}")


UPLOADING = [0]  # uploads going on right now: Home doesn't restart for an update in the middle of one


def spawn_detached(*args):
    kwargs = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL, "cwd": str(ROOT)}
    if WINDOWS:
        kwargs["creationflags"] = 0x00000008 | 0x00000200 | 0x08000000  # detached, own group, no window
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen([sys.executable, *args], **kwargs)


def watch_for_updates():
    """Looks for a new version now and then, and restarts Home onto one once nothing is being copied or uploaded."""
    updater = str(ROOT / "updater.py")
    next_look = 0
    while True:
        if time.time() >= next_look:
            next_look = time.time() + 6 * 3600
            spawn_detached(updater)
        try:
            here = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        except OSError:
            here = APP_VERSION
        busy = UPLOADING[0] > 0 or any(j["state"] == "running" for j in JOBS.values())
        if here != APP_VERSION and not busy:
            spawn_detached(updater, "--restart")
            return
        time.sleep(30)


def serve(port):
    settings()
    library()
    try:
        # only this computer, unless the owner lets people on the same Wi-Fi in (Team page)
        httpd = ThreadingHTTPServer(("0.0.0.0" if wifi_on() else "127.0.0.1", port), Handler)
    except OSError as e:
        sys.exit(f"can't use port {port}: {e}")
    httpd.daemon_threads = True
    PIDFILE.write_text(str(os.getpid()))
    print(f"Editors.Hub is running: {home_url()}", flush=True)
    if wifi_on():
        print(f"On your Wi-Fi: {', '.join(lan_addresses(port)) or 'no network found'}", flush=True)
    keys.load_into_environment()

    def start_up():
        auto_install_skills()
        hubsetup.setup(install=True, log=lambda line: print(line, flush=True))
    threading.Thread(target=start_up, daemon=True).start()
    if not os.environ.get("EDITORS_HUB_NO_UPDATES"):
        threading.Thread(target=watch_for_updates, daemon=True).start()

    def keep_approval():  # once a day: renews this computer's pass, and notices if the owner has removed it
        while True:
            approval.renew(DATA)
            time.sleep(86400)
    threading.Thread(target=keep_approval, daemon=True).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if PIDFILE.exists() and PIDFILE.read_text().strip() == str(os.getpid()):
            PIDFILE.unlink()


def stop():
    pid = PIDFILE.read_text().strip() if PIDFILE.exists() else ""
    if not pid:
        print("Home isn't running")
        return
    try:
        if WINDOWS:
            subprocess.run(["taskkill", "/PID", pid, "/F"], capture_output=True)
        else:
            os.kill(int(pid), signal.SIGTERM)
        print("Home stopped")
    except (ProcessLookupError, ValueError):
        print("Home wasn't running")
    PIDFILE.unlink(missing_ok=True)


# ---------------------------------------------------------------- command line

def print_status(as_json):
    videos = []
    for vid in video_dirs():
        videos.append(video_summary(load_video(vid)))
    styles = list_styles()
    projects = list_projects()
    if as_json:
        print(json.dumps({"home": home_url() if running(settings()["port"]) else None, "library": str(library()),
                          "projects": projects, "styles": styles, "videos": videos}, indent=1))
        return
    port = settings()["port"]
    print(f"{settings()['studio_name']}  -  library: {library()}")
    print(f"Home: {'running, ' + home_url() if running(port) else 'not running (studio.py open starts it)'}\n")

    def video_lines(shown):
        for v in sorted(shown, key=lambda v: v["updated"], reverse=True):
            draft = f"v{v['latest']}" if v["latest"] else "no draft"
            notes = f", {v['open_notes']} open notes" if v["open_notes"] else ""
            print(f"    {v['id']:<32} {v['status']:<10} {draft}{notes}  (style: {v['style_name']})")

    print("PROJECTS (clients)")
    if not projects:
        print('  None yet. Make one: studio.py new-project "Client name"')
    for p in projects:
        print(f"{p['name']}  [{p['id']}]  {p['folder']}")
        video_lines(v for v in videos if v["project"] == p["id"])
        print()
    print("\nSTYLES (editing looks)")
    if not styles:
        print('  None yet. Make one: studio.py new-style "Look name"')
    for st in styles:
        where = "shared" if st["shared"] else f"private to {st.get('maker_name') or 'owner'}"
        print(f"{st['name']}  [{st['id']}]  ({where})  {st['folder']}")
        video_lines(v for v in videos if v["style"] == st["id"] and not v["project"])
        print()


def print_notes(vid, show_all):
    v = load_video(vid)
    latest = latest_version(v)
    if latest is None:
        print(f"{v['name']}: no drafts yet")
        return
    notes = [n for n in v["notes"] if show_all or not n["done"]]
    notes.sort(key=lambda n: (n["version"], n["t"]))
    approved = f", approved v{v['approved']['version']}" if v.get("approved") else ""
    print(f"{v['name']}  -  {v['status']}, latest v{latest}{approved}  -  {v['folder']}")
    if not notes:
        print("No open notes." if not show_all else "No notes.")
    batches = {b["id"]: b for b in v.get("feedback", [])}
    for n in notes:
        b = batches.get(n.get("batch"))
        state = "fixed" if n["done"] else "with Claude" if b and b.get("picked_up") else "sent" if b else "new"
        print(f"  #{n['id']:<3} v{n['version']}  {fmt_time(n['t']):>7}  [{state}] ({n.get('author') or '-'})  {n['text']}")
        for a in n.get("attachments", []):
            print(f"        {'link' if a['kind'] == 'link' else 'file'}: "
                  f"{a['url'] if a['kind'] == 'link' else Path(v['folder']) / a['file']}")
        if n.get("reply"):
            print(f"        reply: {n['reply']['text']}")


def skills_command(action, paths):
    if action == "add":
        if not paths:
            raise StudioError("say which folder: studio.py skills add <folder>")
        names = add_skills(paths)
        print(f"Packed into Editors.Hub: {', '.join(names)}")
        action, paths = "install", []
    elif action == "skip":
        set_skipped(paths, True)
        print(f"Won't install on this computer: {', '.join(paths)}")
        action = "list"
    elif action == "remove":
        for name in paths:
            remove_skill(name)
            print(f"Taken out of the pack: {name} (still installed on this computer)")
        return
    if action == "install":
        restore_profile()
        done = install_skills(paths)
        done["filled"] = fill_skills()
        for key in ("installed", "updated", "failed", "filled"):
            if done[key]:
                print(f"{'Filled from your profile' if key == 'filled' else key.capitalize()}: {', '.join(done[key])}")
        if not any(done.values()):
            print("Nothing to install: every packed skill is already in Claude.")
    skills = list_skills()
    print(f"\n{len(skills)} skills packed in Editors.Hub, Claude's skills folder: {CLAUDE_SKILLS}")
    for s in skills:
        print(f"  {s['name']:<40} {s['state']}")


def profile_command(action, replace):
    if action == "pack":
        s = pack_profile()
        print(f"Packed into Editors.Hub: {s['brand']} ({s['creator']}), accent {s['accent']}, fonts: {', '.join(s['fonts']) or 'none'}")
        print("New computers that have no creator profile get this one, and their skills come filled in.")
        return
    if action == "restore":
        s = restore_profile(replace)
        if not s:
            raise StudioError("nothing restored: no packed profile, or this computer has its own "
                              "(use --replace to swap it; the old one is kept beside it)")
        print(f"Profile put in place: {s['brand']} ({s['creator']})")
        filled = fill_skills()
        print(f"Filled: {', '.join(filled) or 'nothing needed filling'}")
        return
    packed, here = profile_summary(PROFILE_PACK), profile_summary(PROFILE_DIR)
    describe = lambda s: f"{s['brand'] or '-'} ({s['creator'] or '-'}), accent {s['accent'] or '-'}, fonts: {', '.join(s['fonts']) or 'none'}"
    print(f"Packed in Editors.Hub: {describe(packed) if packed else 'none (studio.py profile pack)'}")
    print(f"On this computer:      {describe(here) if here else 'none'}  [{PROFILE_DIR}]")


def main(argv=None):
    p = argparse.ArgumentParser(prog="studio.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("open")
    o.add_argument("video", nargs="?")
    o.add_argument("--browser", action="store_true", help="also open it in your web browser")
    sv = sub.add_parser("serve")
    sv.add_argument("--port", type=int)
    sub.add_parser("stop")
    st = sub.add_parser("status")
    st.add_argument("--json", action="store_true")
    ns = sub.add_parser("new-style")
    ns.add_argument("name")
    ns.add_argument("--client", default="")
    ns.add_argument("--notes", default="")
    ns.add_argument("--format", default="", choices=["", *STYLE_FORMATS])
    ns.add_argument("--link", action="append", default=[])
    np_ = sub.add_parser("new-project")
    np_.add_argument("name")
    np_.add_argument("--contact", default="")
    np_.add_argument("--website", default="")
    np_.add_argument("--about", default="")
    np_.add_argument("--brand", default="")
    pa = sub.add_parser("project-add")
    pa.add_argument("project")
    pa.add_argument("file")
    pa.add_argument("--section", default="auto", choices=["auto", *(sec for sec, _ in PROJECT_SECTIONS)])
    nv = sub.add_parser("new-video")
    nv.add_argument("style")
    nv.add_argument("name")
    nv.add_argument("--project", default="")
    nv.add_argument("--training", action="store_true")
    nv.add_argument("--raw", action="append", default=[])
    nv.add_argument("--brief", default="")
    ctx = sub.add_parser("context")
    ctx.add_argument("video")
    ad = sub.add_parser("add-draft")
    ad.add_argument("video")
    ad.add_argument("file")
    ad.add_argument("--note", default="")
    nt = sub.add_parser("notes")
    nt.add_argument("video")
    nt.add_argument("--all", action="store_true")
    dn = sub.add_parser("done")
    dn.add_argument("video")
    dn.add_argument("ids", nargs="+", type=int)
    sv_ = sub.add_parser("set-style")
    sv_.add_argument("video")
    sv_.add_argument("style")
    ba = sub.add_parser("broll-ask")
    ba.add_argument("video")
    ba.add_argument("--timeout", type=int, default=0, help="seconds; 0 waits until there's an answer")
    bp = sub.add_parser("broll-plan")
    bp.add_argument("video")
    bp.add_argument("plan")
    bp.add_argument("--change", action="store_true")
    bp.add_argument("--timeout", type=int, default=0, help="seconds; 0 waits until the picks are submitted")
    br = sub.add_parser("broll-record")
    br.add_argument("video")
    br.add_argument("plan")
    br.add_argument("--change", action="store_true")
    bs = sub.add_parser("broll-status")
    bs.add_argument("video")
    up = sub.add_parser("update")
    up.add_argument("video")
    up.add_argument("text", nargs="?", default="")
    up.add_argument("--snapshot", default=None)
    up.add_argument("--at", type=float, default=None)
    ar = sub.add_parser("ask-render")
    ar.add_argument("video")
    ar.add_argument("--note", default="")
    ar.add_argument("--size", default="")
    ar.add_argument("--fps", type=float, default=None)
    ar.add_argument("--duration", type=float, default=None)
    ar.add_argument("--timeout", type=int, default=0, help="seconds; 0 waits until the settings are chosen")
    fr = sub.add_parser("finish-render")
    fr.add_argument("video")
    fr.add_argument("file")
    fr.add_argument("--note", default="")
    ss = sub.add_parser("set-status")
    ss.add_argument("video")
    ss.add_argument("status")
    wt = sub.add_parser("wait")
    wt.add_argument("video")
    wt.add_argument("--timeout", type=int, default=0, help="seconds; 0 waits until feedback comes")
    rp = sub.add_parser("reply")
    rp.add_argument("video")
    rp.add_argument("id", type=int)
    rp.add_argument("text")
    rp.add_argument("--not-fixed", action="store_true")
    rp.add_argument("--lesson", default="")
    rp.add_argument("--client-lesson", default="")
    lv = sub.add_parser("live")
    lv.add_argument("video")
    lv.add_argument("--project")
    lv.add_argument("--stop", action="store_true")
    sk = sub.add_parser("skills")
    sk.add_argument("action", nargs="?", default="list", choices=["list", "install", "add", "skip", "remove"])
    sk.add_argument("paths", nargs="*")
    pr = sub.add_parser("profile")
    pr.add_argument("action", nargs="?", default="status", choices=["status", "pack", "restore"])
    pr.add_argument("--replace", action="store_true", help="restore over this computer's own profile (kept aside)")
    xp = sub.add_parser("export-project")
    xp.add_argument("project")
    xp.add_argument("dest")
    ip = sub.add_parser("import-project")
    ip.add_argument("path")
    ex = sub.add_parser("export-style")
    ex.add_argument("style")
    ex.add_argument("dest")
    im = sub.add_parser("import-style")
    im.add_argument("path")
    im.add_argument("--shared", action="store_true")
    rn = sub.add_parser("rename-style")
    rn.add_argument("style")
    rn.add_argument("name")
    sub.add_parser("duplicate-style").add_argument("style")
    sub.add_parser("delete-style").add_argument("style")
    sub.add_parser("deleted-styles")
    sub.add_parser("restore-style").add_argument("trash")
    sub.add_parser("online-styles")
    sub.add_parser("upload-style").add_argument("style")
    dl = sub.add_parser("download-style")
    dl.add_argument("tag")
    dl.add_argument("--shared", action="store_true")
    sh = sub.add_parser("share-style")
    sh.add_argument("style")
    us = sub.add_parser("unshare-style")
    us.add_argument("style")
    sub.add_parser("codes")
    sub.add_parser("users")
    ur = sub.add_parser("user-role")
    ur.add_argument("email")
    ur.add_argument("role", choices=list(auth.ROLES))
    ru = sub.add_parser("rename-user")
    ru.add_argument("email")
    ru.add_argument("username")
    rm = sub.add_parser("user-remove")
    rm.add_argument("email")
    su = sub.add_parser("setup")
    su.add_argument("--check", action="store_true", help="only check, install nothing")
    a = p.parse_args(argv)
    if a.cmd not in ("open", "serve", "stop", "setup", "skills", "profile") and approval.status(DATA)["required"]:
        sys.exit("error: this computer needs approval from the studio's owner. Open Home (studio.py open) and ask for a code.")

    try:
        if a.cmd == "serve":
            serve(a.port or settings()["port"])
        elif a.cmd == "stop":
            stop()
        elif a.cmd == "open":
            if a.video:
                load_video(a.video)
            ensure_running()
            url = home_url(f"/review/{a.video}" if a.video else "/")
            print(url)
            if a.browser:
                import webbrowser
                webbrowser.open(url)
        elif a.cmd == "status":
            print_status(a.json)
        elif a.cmd == "new-style":
            st = create_style(a.name, a.client, a.notes, format=a.format, links=a.link)
            print(f"Style '{st['name']}' [{st['id']}] made: {st['folder']}")
        elif a.cmd == "new-project":
            p = create_project(a.name, a.contact, a.website, a.about, a.brand)
            print(f"Project '{p['name']}' [{p['id']}] made: {p['folder']}")
        elif a.cmd == "project-add":
            section, dest = add_project_file(a.project, a.file, a.section)
            print(f"Added to {section}: {dest}")
        elif a.cmd == "new-video":
            v = create_video(a.style, a.name, a.brief, a.raw, project=a.project, training=a.training)
            print(f"Video '{v['name']}' [{v['id']}] made: {v['folder']}")
            print(f"Raw footage in raw/. Post progress with studio.py update, and ask before rendering: studio.py ask-render {v['id']}")
            print(f"Before editing, read what this prints: studio.py context {v['id']}")
        elif a.cmd == "context":
            print(video_context(a.video))
        elif a.cmd == "set-style":
            print(f"{a.video} now follows the style {set_video_style(a.video, a.style)['style']}.")
        elif a.cmd == "broll-ask":
            start = broll_begin(a.video)
            if start["action"] == "skip":
                print("SKIP: the owner said the b-roll is good. Don't ask, and leave it as it is.")
            elif start["action"] == "notes":
                print("NOTES ABOUT B-ROLL: do what they ask. If they want a clip changed, gather 3 or 4 NEW options for just that part, then "
                      f"studio.py broll-plan {a.video} <plan.json> --change")
                print("\n".join(describe_notes(load_video(a.video), start["notes"])))
                print(describe_broll(load_video(a.video)))
            elif start["action"] == "ready":
                mode = start["broll"]["mode"]
                print(f"READY ({mode}): nothing to ask yet. " + (f"Open the picker with studio.py broll-plan {a.video} <plan.json>" if mode == "manual" and not start["broll"]["parts"] else "Carry on with the edit."))
                print(describe_broll(load_video(a.video)))
            else:
                print(f"The b-roll popup is open: {home_url('/review/' + a.video)}\nWaiting for the answer...", flush=True)
                got = broll_wait(a.video, a.timeout)
                print(broll_say(a.video, got) if got else "No answer yet. The popup stays open; run broll-ask again to keep listening.")
        elif a.cmd in ("broll-plan", "broll-record"):
            try:
                plan = json.loads(Path(a.plan).read_text(encoding="utf-8-sig"))
            except (OSError, ValueError) as e:
                raise StudioError(f"That plan can't be read: {e}")
            if a.cmd == "broll-record":
                print(f"Recorded {len(broll_record(a.video, plan, a.change))} b-roll parts.")
            else:
                built = broll_plan(a.video, plan, a.change)
                print(f"The picker is open with {len(built)} parts: {home_url('/review/' + a.video)}\nWaiting for the picks...", flush=True)
                got = broll_wait(a.video, a.timeout)
                print(broll_say(a.video, got) if got else "No picks yet. The picker stays open; run studio.py broll-ask to keep listening.")
        elif a.cmd == "broll-status":
            print(describe_broll(load_video(a.video)))
        elif a.cmd == "update":
            post_update(a.video, a.text, a.snapshot, a.at)
            print("Posted to the Live tab.")
        elif a.cmd == "ask-render":
            req = ask_render(a.video, a.note, a.size, a.fps, a.duration)
            print(f"The render popup is open: {home_url('/review/' + a.video)}\nWaiting for the settings...", flush=True)
            req = wait_for_render_choice(a.video, a.timeout)
            if not req:
                print("No settings chosen yet. The popup stays waiting; run ask-render again to keep listening.")
                return
            print(f"RENDER SETTINGS: {describe_choice(req['choice'])}")
            if req["choice"]["fps"] != "same":
                print(f"Render the edit at {req['choice']['fps']} fps and full quality, then run: studio.py finish-render {a.video} <file> --note \"what changed\"")
            else:
                print(f"Render the edit at full quality, then run: studio.py finish-render {a.video} <file> --note \"what changed\"")
        elif a.cmd == "finish-render":
            version, r = finish_render(a.video, a.file, a.note)
            print(f"v{version} is up for review ({r['width']}x{r['height']}, {r['fps']:g} fps, {r['size_mb']} MB): {home_url('/review/' + a.video)}")
        elif a.cmd == "add-draft":
            n = add_draft(a.video, a.file, a.note)
            print(f"v{n} is up for review: {home_url('/review/' + a.video)}")
        elif a.cmd == "notes":
            print_notes(a.video, a.all)
        elif a.cmd == "done":
            for nid in a.ids:
                update_note(a.video, nid, {"done": True})
            print(f"Marked fixed: {', '.join('#' + str(i) for i in a.ids)}")
        elif a.cmd == "set-status":
            set_status(a.video, a.status)
            print(f"{a.video}: {a.status}")
        elif a.cmd == "wait":
            print(f"Listening for feedback on {a.video} (the review page shows Claude as listening)...", flush=True)
            got = wait_for_feedback(a.video, a.timeout)
            if not got:
                print("No feedback came in time.")
                return
            batch, v, notes = got
            print(f"FEEDBACK on {v['name']} (draft v{batch.get('draft')}), sent by {batch.get('by') or 'the owner'}:")
            print("\n".join(describe_notes(v, notes)))
            print(f"\nWhen a note is done: studio.py reply {a.video} <id> \"what you changed\" "
                  f"[--lesson \"an editing rule for the style\"] [--client-lesson \"a rule about this client\"]. Then ask-render, render and "
                  f"studio.py finish-render {a.video} <file> --note \"what changed\", and wait again.")
        elif a.cmd == "reply":
            n = reply_note(a.video, a.id, a.text, fixed=not a.not_fixed, lesson=a.lesson, client_lesson=a.client_lesson)
            print(f"#{a.id}: {'fixed' if n['done'] else 'answered'}" + (f", saved to {n['saved_to']}" if n.get("saved_to") else ""))
        elif a.cmd == "live":
            if a.stop:
                stop_live(a.video)
                print("Live preview stopped.")
            else:
                print(f"Live preview: {start_live(a.video, a.project)} (shown in the review page's Live preview tab)")
        elif a.cmd == "skills":
            skills_command(a.action, a.paths)
        elif a.cmd == "profile":
            profile_command(a.action, a.replace)
        elif a.cmd in ("export-project", "import-project"):
            job = export_project_to(a.project, a.dest) if a.cmd == "export-project" else import_project_from(a.path)
            while job["state"] == "running":
                time.sleep(0.5)
            if job["state"] != "done":
                raise StudioError(job["message"] or "It stopped.")
            r = job["result"]
            if a.cmd == "export-project":
                print(f"Saved {r['name']} ({r['bytes'] / 1e9:.2f} GB) to {r['path']}")
                if r["styles"]:
                    print(f"Its videos use these styles, which are saved separately: {', '.join(r['styles'])}")
            else:
                print(f"{r['name']} is in this studio, {r['videos']} videos.")
                if r["missing_styles"]:
                    print(f"Not in this studio yet, so bring them in too: {', '.join(r['missing_styles'])}")
        elif a.cmd in ("export-style", "import-style"):
            job = export_style_to(a.style, a.dest) if a.cmd == "export-style" else \
                import_style_from(a.path, "shared" if a.shared else "mine")
            last = -1
            while job["state"] == "running":
                pct = int(job["done_bytes"] * 100 / job["total_bytes"]) if job["total_bytes"] else 0
                if pct // 10 != last // 10:
                    print(f"  {job['title']}: {pct}%", flush=True)
                    last = pct
                time.sleep(1)
            if job["state"] == "failed":
                raise StudioError(job["message"])
            r = job["result"]
            print(f"Saved {r['name']} ({r['bytes'] / 1e9:.2f} GB) to {r['path']}" if a.cmd == "export-style" else
                  f"{r['name']} is in this studio ({'Shared' if r['shared'] else 'My styles'}), {r['videos']} videos.")
        elif a.cmd == "online-styles":
            repo, items = online_styles()
            print(f"Online Shared folder: {repo}")
            for i in items:
                print(f"  {i['tag']:<36} {i['name']:<30} {i['size'] / 1e9:6.2f} GB  by {i.get('uploaded_by') or '-'}"
                      + ("" if i["complete"] else "  (upload not finished)"))
            if not items:
                print("  nothing yet")
        elif a.cmd in ("upload-style", "download-style"):
            job = upload_style_online(a.style) if a.cmd == "upload-style" else \
                download_online_style(a.tag, "shared" if a.shared else "mine")
            last = -1
            while job["state"] == "running":
                pct = int(job["done_bytes"] * 100 / job["total_bytes"]) if job["total_bytes"] else 0
                if pct // 10 != last // 10:
                    print(f"  {job['title']}: {pct}%", flush=True)
                    last = pct
                time.sleep(1)
            if job["state"] == "failed":
                raise StudioError(job["message"])
            r = job["result"]
            print(f"{r['name']} is in the online Shared folder ({r['repo']})" if a.cmd == "upload-style" else
                  f"{r['name']} is in this studio ({'Shared' if r['shared'] else 'My styles'}), {r['videos']} videos.")
        elif a.cmd == "rename-style":
            print(f"Renamed: {rename_style(a.style, a.name)['name']}")
        elif a.cmd == "duplicate-style":
            job = duplicate_style(a.style)
            while job["state"] == "running":
                time.sleep(0.5)
            if job["state"] == "failed":
                raise StudioError(job["message"])
            print(f"Copied to {job['result']['name']} [{job['result']['id']}], private")
        elif a.cmd == "delete-style":
            r = delete_style(a.style)
            print(f"{r['name']} moved to Recently deleted ({r['trash']}); restore-style {r['trash']} brings it back")
        elif a.cmd == "deleted-styles":
            items = list_trash()
            print("\n".join(f"  {i['trash']:<50} {i['name']}  ({i['videos']} videos, deleted {i['deleted']})" for i in items) or "Nothing in Recently deleted.")
        elif a.cmd == "restore-style":
            print(f"Restored: {restore_style(a.trash)['name']}")
        elif a.cmd in ("share-style", "unshare-style"):
            st = share_style(a.style, a.cmd == "share-style")
            print(f"{st['name']} is now {'shared: everyone signed in sees it' if st['shared'] else 'private again'} ({st['folder']})")
        elif a.cmd == "codes":
            codes = accounts().all_codes()
            if not codes:
                print("No codes waiting.")
            for c in sorted(codes, key=lambda c: c["sent"]):
                who = "you (owner)" if c["email"] == accounts().owner_email else f"{c['username']} ({c['email']})"
                left = int(c["expires"] - time.time()) // 60
                print(f"  {c['code']}   {c['purpose']:<7} {who}   {left} min left")
        elif a.cmd == "users":
            for u in accounts().team():
                print(f"  {u['username']:<20} {u['email']:<32} {u['role']:<9} last seen {u.get('last_seen') or '-'}")
            if not accounts().owner_exists():
                print(f"No owner yet: open Home and create the owner account with {accounts().owner_email}.")
        elif a.cmd == "user-role":
            accounts().set_role(a.email.lower(), a.role)
            print(f"{a.email}: {a.role}")
        elif a.cmd == "rename-user":
            print(f"{a.email} is now {rename_account(a.email.lower(), a.username)}")
        elif a.cmd == "user-remove":
            accounts().remove(a.email.lower())
            print(f"Removed {a.email}")
        elif a.cmd == "setup":
            keys.load_into_environment()
            result = hubsetup.setup(install=not a.check, log=print)
            for it in result["items"]:
                print(f"  {it['title']:<40} {it['state']:<10} {it['detail']}")
            print("Ready." if result["ready"] else "Not ready yet: the steps above that aren't ok need doing.")
    except (StudioError, auth.AuthError) as e:
        sys.exit(f"error: {e}")


if __name__ == "__main__":
    main()
