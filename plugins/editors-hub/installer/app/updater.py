#!/usr/bin/env python3
"""Keeps Editors.Hub up to date by itself, with no GitHub account: the releases are in a public repository.

    updater.py            check for a newer version and put it in place (quiet; notes go in data/update.log)
    updater.py --restart  restart Home, so it runs the new version

Everything is downloaded and checked against the release's list of files before anything here changes, and the
version is written last, so an update that stops part way is simply done again. Never touches data/ (accounts,
settings, the email login), library/ (styles and videos) or profile/ (that computer's brand). API keys live outside
this folder altogether. To turn it off on a computer, set "auto_update": false in data/settings.json.
"""
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
REPO = "famir3558-editorshub/editors-hub-studio"
APP_PATH = "plugins/editors-hub/installer/app"
VERSION_URL = f"https://raw.githubusercontent.com/{REPO}/main/{APP_PATH}/VERSION"
ZIP_URL = f"https://codeload.github.com/{REPO}/zip/refs/heads/main"
MANIFEST = "update-manifest.json"
KEEP = {"data", "library", "profile"}
CHECK_EVERY = 3600  # a session can start any number of times: look at most once an hour
MAX_DOWNLOAD = 300_000_000


class UpdateError(Exception):
    pass


def version_tuple(text):
    try:
        return tuple(int(x) for x in str(text).strip().split("."))
    except ValueError:
        return ()


def newer(a, b):
    """Is version a newer than version b? Something unreadable is never newer."""
    return bool(version_tuple(a)) and version_tuple(a) > version_tuple(b)


def file_hash(data):
    """Line endings don't count: git can store a text file differently from how it was built on Windows."""
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def fetch(url, limit, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "Editors.Hub-updater", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read(limit + 1)
    if len(data) > limit:
        raise UpdateError("the download is bigger than a release should be")
    return data


def safe_rel(rel):
    path = PurePosixPath(rel)
    if path.is_absolute() or ".." in path.parts or not path.parts or ":" in rel or "\\" in rel or path.parts[0] in KEEP:
        raise UpdateError(f"the release has a file it shouldn't: {rel}")
    return path


def unpack(zip_path, dest):
    """Takes just the app out of the repository's .zip. Returns (app folder, the files marked executable)."""
    executable = set()
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            parts = PurePosixPath(info.filename).parts
            marker = tuple(APP_PATH.split("/"))
            if info.is_dir() or len(parts) <= len(marker) + 1 or parts[1:len(marker) + 1] != marker:
                continue
            rel = "/".join(parts[len(marker) + 1:])
            if ".." in rel.split("/") or "\\" in rel or ":" in rel:
                raise UpdateError(f"the release has a file outside its folder: {info.filename}")
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as fi, open(target, "wb") as fo:
                shutil.copyfileobj(fi, fo)
            if (info.external_attr >> 16) & 0o111:
                executable.add(rel)
    return dest, executable


def verify(app, expected_version):
    """Every file on the release's list has to be there, and be exactly what the list says."""
    try:
        manifest = json.loads((app / MANIFEST).read_text(encoding="utf-8"))
        files = manifest["files"]
    except (OSError, ValueError, KeyError) as e:
        raise UpdateError(f"the release's list of files can't be read: {e}")
    if manifest.get("version") != expected_version or not files or "VERSION" not in files or "studio.py" not in files:
        raise UpdateError("the release's list of files doesn't match its version")
    for rel, digest in files.items():
        safe_rel(rel)
        path = app / rel
        if not path.is_file() or file_hash(path.read_bytes()) != digest:
            raise UpdateError(f"{rel} is missing or damaged in the download")
    return manifest


def apply(app, manifest, root, executable=()):
    previous = {}
    try:
        previous = json.loads((root / MANIFEST).read_text(encoding="utf-8")).get("files", {})
    except (OSError, ValueError):
        pass
    names = [rel for rel in manifest["files"] if rel != "VERSION"]
    for rel in [*names, MANIFEST, "VERSION"]:  # the version last: stopping part way means it's done again next time
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(f"{target.name}.updating")
        shutil.copy2(app / rel, tmp)
        if os.name != "nt" and (rel in executable or rel.endswith((".sh", ".command"))):
            tmp.chmod(tmp.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        os.replace(tmp, target)
    for rel in previous:  # files a release dropped go; anything else in the folder was put there by someone, so it stays
        if rel not in manifest["files"] and safe_rel(rel):
            (root / rel).unlink(missing_ok=True)


def settings_of(root):
    try:
        return json.loads((root / "data" / "settings.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def update(root=ROOT, version_url=VERSION_URL, zip_url=ZIP_URL, force=False):
    """Returns what happened, in a few words. Trouble is raised; a computer with no internet is just no news."""
    root = Path(root)
    if os.environ.get("EDITORS_HUB_NO_UPDATES") or settings_of(root).get("auto_update") is False:
        return "turned off"
    data = root / "data"
    data.mkdir(exist_ok=True)
    stamp = data / "update-check.json"
    try:
        last = json.loads(stamp.read_text(encoding="utf-8")).get("at", 0)
    except (OSError, ValueError):
        last = 0
    if not force and time.time() - last < CHECK_EVERY:
        return "checked recently"
    lock = data / ".update.lock"
    try:
        if time.time() - lock.stat().st_mtime > 1800:  # left behind by a process that died
            lock.unlink()
    except FileNotFoundError:
        pass
    try:
        os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except FileExistsError:
        return "another update is running"
    try:
        here = (root / "VERSION").read_text(encoding="utf-8").strip() if (root / "VERSION").exists() else ""
        latest = fetch(version_url, 100, timeout=20).decode("ascii", "replace").strip()
        stamp.write_text(json.dumps({"at": time.time(), "latest": latest}), encoding="utf-8")
        if not newer(latest, here):
            return f"up to date ({here})"
        with tempfile.TemporaryDirectory(dir=data, prefix=".update-") as tmp:
            zip_path = Path(tmp) / "release.zip"
            zip_path.write_bytes(fetch(zip_url, MAX_DOWNLOAD, timeout=300))
            app, executable = unpack(zip_path, Path(tmp) / "app")
            manifest = verify(app, latest)
            apply(app, manifest, root, executable)
        return f"updated from {here} to {latest}"
    finally:
        lock.unlink(missing_ok=True)


def restart(root=ROOT):
    """Home's watcher asks for this when no job or upload is running. `open` also installs the skills that changed."""
    studio = str(Path(root) / "studio.py")
    subprocess.run([sys.executable, studio, "stop"], capture_output=True, timeout=60)
    time.sleep(1)
    subprocess.run([sys.executable, studio, "open"], capture_output=True, timeout=120)


def main():
    if "--restart" in sys.argv:
        restart()
        return
    log = ROOT / "data" / "update.log"
    try:
        result = update(force="--force" in sys.argv)
    except Exception as e:  # never in the way: the studio carries on as it is, and tries again later
        result = f"couldn't update: {type(e).__name__}: {e}"
    if result not in ("checked recently", "turned off"):
        log.parent.mkdir(exist_ok=True)
        with open(log, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {result}\n")
    if "--force" in sys.argv:
        print(result)


if __name__ == "__main__":
    main()
