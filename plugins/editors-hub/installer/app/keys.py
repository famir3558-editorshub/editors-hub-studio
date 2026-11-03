"""Editors.Hub API keys: the services the skills can use, which keys are added, and a safe place for them.

Keys are kept per computer and never inside the studio's folder, so copying or sharing the studio never carries them:
    Mac      ~/.config/editors-hub/keys.env, loaded by a two-line block in ~/.zshrc and ~/.bash_profile
    Windows  %APPDATA%\\editors-hub\\keys.env, and each key is also set as a user environment variable
A key that is already in the environment (added some other way) shows as added and is left alone.
Nothing here ever returns a key's value: only whether it's there and its last four characters.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

WINDOWS = os.name == "nt"
CONFIG = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "editors-hub" if WINDOWS else \
    Path.home() / ".config" / "editors-hub"
KEYS_FILE = CONFIG / "keys.env"
BLOCK_START = "# >>> Editors.Hub keys >>>"
BLOCK_END = "# <<< Editors.Hub keys <<<"
NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,63}$")

# What the packed skills actually use, and what each costs. "needed" is decided from the creator profile.
SERVICES = [
    {"env": "ELEVENLABS_API_KEY", "service": "ElevenLabs", "group": "Editing",
     "for": "Transcripts for cuts and captions (the most accurate), voice clean-up and voice-overs.",
     "cost": "Free plan, then paid", "url": "https://elevenlabs.io/app/settings/api-keys"},
    {"env": "PIXABAY_API_KEY", "service": "Pixabay", "group": "Editing",
     "for": "Free stock B-roll, including true 9:16 clips, when an edit needs new footage.",
     "cost": "Free", "url": "https://pixabay.com/api/docs/"},
    {"env": "GEMINI_API_KEY", "service": "Google Gemini", "group": "Watching videos",
     "for": "Lets Claude watch a video (reference edits, links) and say what happens in it.",
     "cost": "Free tier", "url": "https://aistudio.google.com/apikey"},
    {"env": "GROQ_API_KEY", "service": "Groq", "group": "Watching videos",
     "for": "Fast transcripts of reference videos that have no captions (the watch skill).",
     "cost": "Free tier", "url": "https://console.groq.com/keys"},
    {"env": "OPENAI_API_KEY", "service": "OpenAI", "group": "Generating",
     "for": "Images with GPT Image, and a backup for transcripts.", "cost": "Paid, per use",
     "url": "https://platform.openai.com/api-keys"},
    {"env": "HEYGEN_API_KEY", "service": "HeyGen", "group": "Generating",
     "for": "AI avatars and voice-overs (the media-use skill).", "cost": "Paid credits",
     "url": "https://app.heygen.com/settings?nav=API"},
]


def _read_file():
    out = {}
    try:
        for line in KEYS_FILE.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^(?:export\s+)?([A-Z][A-Z0-9_]*)=(.*)$", line.strip())
            if m:
                v = m.group(2).strip()
                if len(v) >= 2 and v[0] == v[-1] == "'":
                    v = v[1:-1].replace("'\\''", "'")
                out[m.group(1)] = v
    except FileNotFoundError:
        pass
    return out


def _write_file(values):
    CONFIG.mkdir(parents=True, exist_ok=True)
    tmp = KEYS_FILE.with_name("keys.env.tmp")
    lines = ["# Editors.Hub API keys for this computer. Managed from Settings > API keys."]
    for k, v in sorted(values.items()):
        quoted = "'" + v.replace("'", "'\\''") + "'"
        lines.append(f"export {k}={quoted}")
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    os.replace(tmp, KEYS_FILE)


def load_into_environment():
    """Make the saved keys visible to this process (and the tools it starts)."""
    for k, v in _read_file().items():
        os.environ.setdefault(k, v)


def _shell_hook():
    """Mac/Linux: load keys.env from the shell profiles, once, in a marked block."""
    if WINDOWS:
        return
    block = f'{BLOCK_START}\n[ -f "{KEYS_FILE}" ] && . "{KEYS_FILE}"\n{BLOCK_END}\n'
    for name in (".zshrc", ".bash_profile"):
        rc = Path.home() / name
        if name == ".bash_profile" and not rc.exists():
            continue
        text = rc.read_text(encoding="utf-8") if rc.exists() else ""
        if BLOCK_START in text:
            continue
        rc.write_text(text + ("" if text.endswith("\n") or not text else "\n") + "\n" + block, encoding="utf-8")


def status(needed=()):
    saved = _read_file()
    out = []
    for s in SERVICES:
        value = saved.get(s["env"]) or os.environ.get(s["env"], "")
        where = "Editors.Hub" if s["env"] in saved else ("this computer" if value else "")
        out.append({**s, "added": bool(value), "where": where, "ends": value[-4:] if len(value) >= 8 else "",
                    "needed": s["env"] in needed})
    return out


def save(env, value):
    if not NAME_RE.match(env or "") or env not in {s["env"] for s in SERVICES}:
        raise ValueError("unknown key")
    value = (value or "").strip()
    if not value or "\n" in value or len(value) > 500:
        raise ValueError("Paste the key on its own: one line, no spaces around it.")
    values = _read_file()
    values[env] = value
    _write_file(values)
    os.environ[env] = value
    if WINDOWS:
        subprocess.run(["setx", env, value], capture_output=True)
    else:
        _shell_hook()


def remove(env):
    values = _read_file()
    if env not in values:
        raise ValueError("That key was added outside Editors.Hub, so remove it where it was added.")
    del values[env]
    _write_file(values)
    os.environ.pop(env, None)
    if WINDOWS:
        subprocess.run(["reg", "delete", r"HKCU\Environment", "/v", env, "/f"], capture_output=True)


if __name__ == "__main__":
    for row in status():
        print(f"{row['service']:<14} {'added' if row['added'] else '-':<6} {row['where']}", file=sys.stdout)
