"""Editors.Hub setup: the steps a computer goes through before the studio is ready, in order.

Each step checks first and installs only what's missing. Mac installs with Homebrew, Windows with winget. Steps that
need the person (picking a folder, Apple's install window, Homebrew's password, adding a key) wait for them and carry
on by themselves on the next check. The studio passes in what only it knows (folder, skills, keys) with configure().
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

WINDOWS = os.name == "nt"
MAC = sys.platform == "darwin"
PY_PACKAGES = {"numpy": "numpy", "soundfile": "soundfile", "requests": "requests", "PIL": "pillow",
               "fontTools": "fonttools"}
TOOLS = [  # command, Homebrew formula, winget id, what it's for
    ("ffmpeg", "ffmpeg", "Gyan.FFmpeg", "FFmpeg"),
    ("node", "node", "OpenJS.NodeJS.LTS", "Node"),
    ("yt-dlp", "yt-dlp", "yt-dlp.yt-dlp", "yt-dlp"),
    ("uv", "uv", "astral-sh.uv", "uv"),
]
HOMEBREW_INSTALL = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
APP_INSTALLER = "ms-windows-store://pdp/?productid=9NBLGGH4NNS1"

HOOKS = {}
STATE = {"running": False, "step": "", "items": [], "checked": None, "ready": None}
_lock = threading.Lock()


def configure(**hooks):
    """workdir() -> (ok, detail); skills() -> (ok, detail); install_skills() -> detail; keys() -> (ok, detail);
    transcriber() -> 'local' | 'elevenlabs'."""
    HOOKS.update(hooks)


def add_tool_paths():
    """Apps started from Finder or a launcher don't always see where Homebrew / winget put tools."""
    extra = []
    if MAC:
        extra = ["/opt/homebrew/bin", "/usr/local/bin", str(Path.home() / ".local" / "bin")]
    elif WINDOWS:
        local = os.environ.get("LOCALAPPDATA", "")
        extra = [os.path.join(local, "Microsoft", "WinGet", "Links"),
                 os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "nodejs"),
                 os.path.join(os.environ.get("APPDATA", ""), "npm"), str(Path.home() / ".local" / "bin")]
    parts = os.environ.get("PATH", "").split(os.pathsep)
    for p in reversed(extra):
        if p and os.path.isdir(p) and p not in parts:
            parts.insert(0, p)
    os.environ["PATH"] = os.pathsep.join(parts)


def run(cmd, timeout=900):
    try:
        # from the home folder: tools that look at the current folder can stall on an external drive's
        # UTF-8 whatever the system's own text format (Windows defaults to cp1252, which HyperFrames' output breaks)
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, stdin=subprocess.DEVNULL,
                           cwd=os.path.expanduser("~"),
                           env={**os.environ, "NONINTERACTIVE": "1", "HOMEBREW_NO_ENV_HINTS": "1"})
        return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()
    except FileNotFoundError:
        return 127, f"{cmd[0]} not found"
    except subprocess.TimeoutExpired:
        return 124, f"{' '.join(cmd[:3])} took too long"


def first_line(text):
    return next((line.strip() for line in text.splitlines() if line.strip()), "")


def npx():
    return shutil.which("npx")


def hf(*args, timeout=900):
    exe = npx()
    if not exe:
        return 127, "Node isn't installed yet"
    return run([exe, "--yes", "hyperframes", *args], timeout=timeout)


def python():
    """The Python the skills' scripts run (`python3` on Mac, `python` / `py` on Windows)."""
    for name in (("python", "py") if WINDOWS else ("python3",)):
        exe = shutil.which(name)
        if exe:
            return exe
    return sys.executable


# ---------------------------------------------------------------- checks and installs, one per step

def check_devtools():
    code, out = run(["xcode-select", "-p"], timeout=20)
    return code == 0 and os.path.isdir(out.strip()), out.strip()


def install_devtools():
    run(["xcode-select", "--install"], timeout=30)
    return "needs you", "macOS opened an install window: finish it, then press Check everything again."


def check_manager():
    # only look for it: `brew --version` can stall when started from some app launchers
    exe = shutil.which("brew" if MAC else "winget" if WINDOWS else "")
    return bool(exe), exe or ""


def install_manager():
    if MAC:
        script = f'tell application "Terminal" to do script "{HOMEBREW_INSTALL.replace(chr(34), chr(92) + chr(34))}"'
        run(["osascript", "-e", script, "-e", 'tell application "Terminal" to activate'], timeout=30)
        return "needs you", "A Terminal window opened with Homebrew's installer: type your Mac password there and wait for it to finish."
    if WINDOWS:
        os.startfile(APP_INSTALLER)
        return "needs you", 'The Microsoft Store opened on "App Installer": install or update it, then press Check everything again.'
    return "needs you", "Install ffmpeg, node, yt-dlp and uv with your system's package manager."


def check_tools():
    missing, versions = [], []
    for cmd, _, _, label in TOOLS:
        exe = shutil.which(cmd)
        if not exe:
            missing.append(label)
            continue
        if cmd == "node":
            m = re.search(r"v(\d+)", run([exe, "--version"], 30)[1])
            if not m or int(m.group(1)) < 22:
                missing.append("Node 22 or newer")
                return
            versions.append(f"Node {m.group(0)}")
    if missing:
        return False, "missing " + ", ".join(missing)
    return True, "all four found" + (f" ({', '.join(versions)})" if versions else "")


def install_tools():
    failed = []
    for cmd, brew, winget, label in TOOLS:
        if shutil.which(cmd) and cmd != "node":
            continue
        if cmd == "node" and check_tools()[0]:
            continue
        if MAC:
            code, out = run(["brew", "install", brew], timeout=1800)
        elif WINDOWS:
            code, out = run(["winget", "install", "-e", "--id", winget, "--silent",
                             "--accept-package-agreements", "--accept-source-agreements"], timeout=1800)
        else:
            code, out = 1, "no installer"
        add_tool_paths()
        if code != 0 and not shutil.which(cmd):
            failed.append(f"{label}: {first_line(out[-300:])}")
    if failed:
        return "failed", "; ".join(failed)
    if WINDOWS and not check_tools()[0]:
        return "restart", "Installed: restart Editors.Hub (or the computer) so it can find them."
    return None, ""


def check_hyperframes():
    code, out = hf("--version", timeout=300)
    if code != 0:
        return False, "not installed yet"
    version = first_line(out)
    code, path = hf("browser", "path", timeout=120)
    if code != 0 or not path.strip():
        return False, f"HyperFrames {version}; its Chrome isn't downloaded yet"
    return True, f"HyperFrames {version} with its headless Chrome"


def install_hyperframes():
    exe = npx()
    if not exe:
        return "failed", "Node isn't installed yet"
    run([exe, "--yes", "hyperframes@latest", "--version"], timeout=900)
    code, out = hf("browser", "ensure", timeout=1800)
    return (None, "") if code == 0 else ("failed", first_line(out[-300:]))


def check_python():
    exe = python()
    missing = [pkg for mod, pkg in PY_PACKAGES.items() if run([exe, "-c", f"import {mod}"], 60)[0] != 0]
    if missing:
        return False, "missing " + ", ".join(missing)
    return True, f"Python {first_line(run([exe, '--version'], 30)[1]).split()[-1]}: {', '.join(PY_PACKAGES.values())}"


def install_python():
    exe = python()
    pkgs = [pkg for mod, pkg in PY_PACKAGES.items() if run([exe, "-c", f"import {mod}"], 30)[0] != 0]
    # ready-made wheels only: compiling numpy on a brand-new Python can take an hour and still fail
    cmd = [exe, "-m", "pip", "install", "--user", "--quiet", "--only-binary=:all:", *pkgs]
    code, out = run(cmd, timeout=1800)
    if code != 0 and "externally-managed" in out:  # Homebrew's Python: user installs still go to the user's folder
        code, out = run(cmd + ["--break-system-packages"], timeout=1800)
    return (None, "") if code == 0 else ("failed", first_line(out[-300:]))


def _bg_model_ready():
    folder = Path.home() / ".cache" / "hyperframes" / "background-removal"
    return folder.is_dir() and any(p.is_file() and p.stat().st_size > 1_000_000 for p in folder.rglob("*"))


def _parakeet_ready():
    code, out = hf("models", "list", "--json", timeout=120)
    try:
        data = json.loads(out[out.index("{"):out.rindex("}") + 1])
        return any(m.get("engine") == "parakeet" and m.get("installed") for m in data.get("models", []))
    except ValueError:
        return False


def check_models():
    local = HOOKS.get("transcriber", lambda: "local")() == "local"
    have = []
    missing = []
    (have if _bg_model_ready() else missing).append("cut-outs")
    if local:
        (have if _parakeet_ready() else missing).append("speech-to-text")
    if missing:
        return False, "to download: " + ", ".join(missing)
    return True, ", ".join(have) + (" (transcripts use ElevenLabs)" if not local else "")


def install_models():
    problems = []
    if not _bg_model_ready():
        ffmpeg = shutil.which("ffmpeg")
        with tempfile.TemporaryDirectory() as tmp:
            src, out = os.path.join(tmp, "in.png"), os.path.join(tmp, "out.png")
            if ffmpeg:
                run([ffmpeg, "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=size=128x128", "-frames:v", "1", src], 60)
            code, text = hf("remove-background", src, "-o", out, timeout=1800)  # first use downloads the model
            if not _bg_model_ready():
                problems.append("cut-out model: " + first_line(text[-200:]))
    if HOOKS.get("transcriber", lambda: "local")() == "local" and not _parakeet_ready():
        code, text = hf("models", "install", "parakeet", timeout=3600)
        if code != 0:
            problems.append("speech model: " + first_line(text[-200:]))
    return ("failed", "; ".join(problems)) if problems else (None, "")


def check_skills():
    return HOOKS["skills"]() if "skills" in HOOKS else (False, "")


def install_skills():
    detail = HOOKS["install_skills"]() if "install_skills" in HOOKS else ""
    return None, detail


STEPS = [
    {"id": "workdir", "title": "Where your work goes", "manual": "folder",
     "text": "The folder each new style and its videos go in: on this computer or on a drive. You can change it later in Settings.",
     "check": lambda: HOOKS["workdir"]() if "workdir" in HOOKS else (False, "")},
    {"id": "devtools", "title": "Apple's developer tools", "mac": True, "manual": "button", "button": "Install",
     "text": "Apple's command-line tools (compilers and git), which Homebrew needs. macOS installs them in its own window.",
     "check": check_devtools, "install": install_devtools, "after": []},
    {"id": "manager", "title": "Homebrew" if not WINDOWS else "winget (App Installer)", "manual": "button",
     "button": "Install",
     "text": ("The Mac's package manager, for the tools below. It asks for your Mac's password once, in a Terminal window."
              if not WINDOWS else "Windows' package manager, for the tools below. It comes with App Installer from the Microsoft Store."),
     "check": check_manager, "install": install_manager, "after": ["devtools"]},
    {"id": "tools", "title": "FFmpeg, Node, yt-dlp and uv",
     "text": "FFmpeg cuts and renders video, Node runs HyperFrames, yt-dlp downloads reference videos and uv runs Python tools.",
     "check": check_tools, "install": install_tools, "after": ["manager"]},
    {"id": "hyperframes", "title": "HyperFrames engine",
     "text": "HyperFrames, the engine that builds and renders every edit, and the headless Chrome it renders with.",
     "check": check_hyperframes, "install": install_hyperframes, "after": ["tools"]},
    {"id": "python", "title": "Python tools for editing",
     "text": "The Python packages the skills' scripts use: Pillow, NumPy, soundfile, requests and fonttools.",
     "check": check_python, "install": install_python, "after": []},
    {"id": "models", "title": "Editing models",
     "text": "Small AI models from HyperFrames, kept on this computer: cut-outs and, for free transcripts, the speech model (about 700 MB).",
     "check": check_models, "install": install_models, "after": ["hyperframes"]},
    {"id": "skills", "title": "Video skills and Claude's instructions",
     "text": "The video skills packed in Editors.Hub, filled in with your brand, and a short note that tells Claude how to use the studio.",
     "check": check_skills, "install": install_skills, "after": []},
    {"id": "keys", "title": "Your API keys", "manual": "keys",
     "text": "The keys your edits need. Add them in Settings, and setup carries on by itself.",
     "check": lambda: HOOKS["keys"]() if "keys" in HOOKS else (True, "")},
]


def steps():
    return [s for s in STEPS if not (s.get("mac") and not MAC)]


# ---------------------------------------------------------------- running it

def _set(**kw):
    with _lock:
        STATE.update(kw)


def _item(step_id, state, detail=""):
    with _lock:
        for it in STATE["items"]:
            if it["id"] == step_id:
                it.update(state=state, detail=detail)


def snapshot():
    with _lock:
        return {**STATE, "items": [dict(i) for i in STATE["items"]]}


def setup(install=True, only=None, log=print):
    """Check every step in order; with install, install what's missing once the steps it needs are done.
    `only` runs one step's install even if it's one that waits for the person (a button on the page)."""
    if STATE["running"]:
        return snapshot()
    add_tool_paths()
    _set(running=True, step="checking", ready=None,
         items=[{"id": s["id"], "title": s["title"], "text": s["text"], "manual": s.get("manual"),
                 "button": s.get("button"), "state": "checking", "detail": ""} for s in steps()])
    done = set()
    try:
        for s in steps():
            try:
                _run_step(s, done, install, only, log)
            except Exception as e:  # one step going wrong never stops the steps after it
                _item(s["id"], "failed", f"{type(e).__name__}: {e}")
                log(f"setup: {s['title']} failed: {e}")
    finally:
        _set(running=False, step="", checked=time.strftime("%Y-%m-%dT%H:%M:%S"),
             ready=all(i["state"] == "ok" for i in STATE["items"]))
    return snapshot()


def _run_step(s, done, install, only, log):
    """Check one step and, when it can be done now, install it."""
    _set(step=f"checking {s['title']}")
    ok, detail = s["check"]()
    if ok:
        done.add(s["id"])
        _item(s["id"], "ok", detail)
        return
    waiting = [a for a in s.get("after", []) if a not in done and any(x["id"] == a for x in steps())]
    manual = s.get("manual") and only != s["id"]
    if not install or "install" not in s or waiting or manual:
        state = "waiting" if waiting else "needs you" if s.get("manual") else "missing"
        _item(s["id"], state, detail if not waiting else f"after {', '.join(waiting)}")
        return
    _set(step=f"installing {s['title']}")
    _item(s["id"], "installing", "")
    log(f"setup: installing {s['title']}")
    state, note = s["install"]()
    add_tool_paths()
    ok, detail = s["check"]()
    if ok:
        done.add(s["id"])
        _item(s["id"], "ok", detail)
    else:
        _item(s["id"], state or "failed", note or detail or "didn't finish")
    log(f"setup: {s['title']}: {'ok' if ok else state or 'not ready'}")


def start_background(only=None, log=print):
    threading.Thread(target=setup, kwargs={"install": True, "only": only, "log": log}, daemon=True).start()
