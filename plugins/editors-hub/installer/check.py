#!/usr/bin/env python3
"""Editors.Hub plugin: put the studio app in ~/editors-hub (or update it), never touching that computer's own data.

    check.py            quiet: install or update if needed, then say in a line or two where things stand
                        (runs when a Claude session starts)
    check.py --install  install or update now and say so

Kept on each computer and never overwritten: data/ (accounts, sign-ins, settings, email login), library/ (styles and
videos) and profile/ once that computer has one (its brand). API keys live outside the folder altogether.

It also turns on Claude Code's auto-update for this plugin's marketplace and points it at the public releases, and
starts the app's own updater (updater.py), which needs no GitHub account. "autoUpdate": false in that computer's
settings is left alone, so a computer can opt out. The app's version can be ahead of this plugin's copy: it's never
put back.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
APP = HERE / "app"
DEST = Path(os.environ.get("EDITORS_HUB_HOME") or Path.home() / "editors-hub")
KEEP = {"data", "library"}
PY = "py" if os.name == "nt" else "python3"
MARKETPLACE = "editors-hub"
MARKETPLACE_SOURCE = {"source": "github", "repo": "famir3558-editorshub/editors-hub-studio"}
OLD_SOURCE = {"source": "github", "repo": "famir3558-editorshub/editors-hub"}  # private: needs a GitHub login


def version(folder):
    try:
        return (folder / "VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        return None


def is_newer(a, b):
    def parts(text):
        try:
            return tuple(int(x) for x in str(text).strip().split("."))
        except ValueError:
            return ()
    return bool(parts(a)) and parts(a) > parts(b)


def install():
    DEST.mkdir(parents=True, exist_ok=True)
    for item in APP.iterdir():
        target = DEST / item.name
        if item.name in KEEP or (item.name == "profile" and target.exists()):
            continue
        if item.is_dir():
            # laid over what's there, so skills the owner packed in on this computer stay
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)
    for launcher in ("Editors.Hub.command",):
        p = DEST / launcher
        if p.exists():
            p.chmod(0o755)


def enable_auto_update():
    """Sets autoUpdate on this marketplace in the user's Claude settings. Returns True if it changed anything.
    Anything unexpected in the file means leaving it exactly as it is."""
    settings = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / "settings.json"
    try:
        data = json.loads(settings.read_text(encoding="utf-8")) if settings.exists() else {}
    except (OSError, ValueError):
        return False
    known = data.setdefault("extraKnownMarketplaces", {}) if isinstance(data, dict) else None
    if not isinstance(known, dict):
        return False
    entry = known.setdefault(MARKETPLACE, {"source": MARKETPLACE_SOURCE})
    if not isinstance(entry, dict):
        return False
    moved = entry.get("source") == OLD_SOURCE
    if moved:
        entry["source"] = MARKETPLACE_SOURCE
    if "autoUpdate" in entry and not moved:
        return False
    newly_on = "autoUpdate" not in entry
    entry.setdefault("autoUpdate", True)
    settings.parent.mkdir(parents=True, exist_ok=True)
    tmp = settings.with_name(f"{settings.name}.editors-hub-tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, settings)
    return newly_on


def start_updater():
    """In the background: a session never waits for it, and it's quiet whatever happens."""
    updater = DEST / "updater.py"
    if not updater.exists() or os.environ.get("EDITORS_HUB_NO_UPDATES"):
        return
    kwargs = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL, "cwd": str(DEST)}
    if os.name == "nt":
        kwargs["creationflags"] = 0x00000008 | 0x00000200 | 0x08000000  # detached, own group, no window
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen([sys.executable, str(updater)], **kwargs)


def main():
    loud = "--install" in sys.argv
    try:
        if enable_auto_update():
            print("Editors.Hub will now update itself on this computer (Claude Code's auto-update for its plugin).")
    except OSError as e:
        print(f"Editors.Hub couldn't turn on its auto-update: {e}")
    bundled, here = version(APP), version(DEST)
    if not (DEST / "studio.py").exists():
        install()
        print(f"Editors.Hub {bundled} was just installed in {DEST}. To start it, use the editors-hub-setup skill: "
              f"`{PY} \"{DEST.as_posix()}/studio.py\" open` prints Home's address for the Claude app's built-in browser; "
              "the owner signs up there and the setup page installs the rest.")
    elif is_newer(bundled, here):
        install()
        print(f"Editors.Hub was updated from {here or 'an older version'} to {bundled} ({DEST}). Its accounts, "
              "settings and videos are unchanged.")
    elif loud:
        print(f"Editors.Hub {here} is already installed in {DEST}.")
    start_updater()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # a session start must never fail over this
        print(f"Editors.Hub couldn't be installed or updated: {e}")
