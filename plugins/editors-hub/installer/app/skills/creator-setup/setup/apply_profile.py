#!/usr/bin/env python3
"""Fill this skill's @@PLACEHOLDERS@@ from the creator profile.

    python3 setup/apply_profile.py            fill every placeholder, copy fonts / profile picture in, mark the skill configured
    python3 setup/apply_profile.py --status   say whether setup has been done and what is still missing (changes nothing)
    python3 setup/apply_profile.py --set key=value [key=value ...]            save shared answers to the profile, then stop
    python3 setup/apply_profile.py --set-skill key=value [key=value ...]      save answers that belong to this skill only

The profile is ONE file shared by every skill in this pack: ~/.claude/creator-profile/profile.json
(override the folder with $CREATOR_PROFILE_DIR). Shared answers (name, brand, colours, fonts, transcription) are asked
once and reused; each skill keeps its own answers under "skills" -> "<skill name>".

How filling works: the first run snapshots every file that contains a placeholder into setup/.pristine/. Every run
re-renders from that snapshot, so changing an answer and running this again updates the skill ("redo my setup").
Placeholders are written @@UPPER_SNAKE@@ and map to the lower-case profile key (@@ACCENT@@ <- "accent").
"""
import datetime, hashlib, json, os, re, shutil, sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = os.path.basename(SKILL)
PDIR = os.path.expanduser(os.environ.get("CREATOR_PROFILE_DIR", "~/.claude/creator-profile"))
PFILE = f"{PDIR}/profile.json"
PRISTINE = f"{SKILL}/setup/.pristine"
TOKEN = re.compile(r"@@([A-Z][A-Z0-9_]*)@@")
TEXT_EXT = (".md", ".py", ".sh", ".css", ".json", ".txt", ".swift", ".html", ".js", ".cjs")
DEFAULTS = {"bg": "#050505", "paper": "#F2F0EC", "grey": "#9A928A", "accent_name": "accent colour",
            "work_root": "~/reel-work", "projects_root": "~/videos", "transcriber": "elevenlabs"}
FONT_KEYS = ("font_main_bold", "font_main_regular", "font_accent", "font_caption", "font_title")


def load():
    return json.load(open(PFILE)) if os.path.exists(PFILE) else {}


def save(p):
    os.makedirs(PDIR, exist_ok=True)
    json.dump(p, open(PFILE, "w"), indent=1, ensure_ascii=False)


def parse(v):
    v = v.strip()
    if v[:1] in "[{" or v in ("true", "false", "null") or re.fullmatch(r"-?\d+(\.\d+)?", v):
        try:
            return json.loads(v)
        except ValueError:
            pass
    return v


def rgb(hexv):
    h = hexv.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hexs(t):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(c))) for c in t)


def lum(t):
    f = lambda c: c / 3294.6 if c <= 10.31475 else ((c / 255 + 0.055) / 1.055) ** 2.4
    r, g, b = (f(c) for c in t)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def font_src(spec, prefix):
    """{"file": "X.ttf"} -> url("<prefix>X.ttf") ; {"local": ["Full Name", "PostScript-Name"]} -> local(...), local(...)
    Both may be given: local() first, the file as the fallback."""
    if isinstance(spec, str):
        spec = {"file": spec}
    parts = ['local("%s")' % n for n in spec.get("local", [])]
    if spec.get("file"):
        parts.append('url("%s%s")' % (prefix, os.path.basename(spec["file"])))
    return ", ".join(parts)


def qdefaults():
    q = f"{SKILL}/setup/questions.json"
    if not os.path.exists(q):
        return {}
    return {x["key"]: x["default"] for x in json.load(open(q)).get("questions", [])
            if not x.get("required") and x.get("default") not in (None, "")}


def tokens(p):
    t = dict(DEFAULTS)
    t.update(qdefaults())
    t.update({k: v for k, v in p.items() if k != "skills" and v not in (None, "")})
    t.update({k: v for k, v in p.get("skills", {}).get(NAME, {}).items() if v not in (None, "")})
    t.setdefault("font_main_regular", t.get("font_main_bold"))
    t.setdefault("font_caption", t.get("font_main_bold"))
    t.setdefault("font_caption_name", t.get("font_main_name"))
    t.setdefault("font_title", t.get("font_main_bold"))                  # big document titles (the document skills)
    t.setdefault("font_title_name", t.get("font_main_name"))
    t.setdefault("creator_first_name", (t.get("creator_name") or "").split(" ")[0] or None)
    out = {}
    for k, v in t.items():
        if v is None:
            continue
        if k in FONT_KEYS:
            out[k.upper() + "_SRC"] = font_src(v, "assets/fonts/")      # used by the engines (page at the project root)
            out[k.upper() + "_SRC_CSS"] = font_src(v, "fonts/")         # used by assets/brand.css
        elif isinstance(v, (str, int, float)):
            out[k.upper()] = str(v)
        elif isinstance(v, list):
            out[k.upper()] = ", ".join(str(x) for x in v)
    if "ACCENT" in out:
        a = rgb(out["ACCENT"])
        out["ACCENT"] = hexs(a)
        out["ACCENT_RGB"] = "%d,%d,%d" % a
        out["ACCENT_LIGHT"] = hexs(tuple(c + (255 - c) * 0.42 for c in a))
        out["ON_ACCENT"] = "#120C08" if lum(a) > 0.18 else "#FFFFFF"     # text that sits ON the accent colour
        d = tuple(c * 0.82 for c in a)                                   # light pages: small accent text and labels
        out["ACCENT_DARK"] = hexs(d)
        out["ON_ACCENT_DARK"] = "#120C08" if lum(d) > 0.18 else "#FFFFFF"
        out["ACCENT_TINT"] = hexs(tuple(c + (255 - c) * 0.88 for c in a))  # pale highlight behind open items
    if "BG" in out:
        out["BG_RGB"] = "%d,%d,%d" % rgb(out["BG"])
    return out


def text_files(root):
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in (".pristine", "__pycache__", "node_modules", ".git")]
        if os.path.abspath(d) == os.path.abspath(f"{SKILL}/setup"):
            continue                                                     # setup files talk ABOUT placeholders; never fill them
        for f in files:
            if f.endswith(TEXT_EXT):
                yield os.path.join(d, f)


def snapshot():
    """Copy every file that still holds a placeholder into setup/.pristine (once per file)."""
    for p in text_files(SKILL):
        rel = os.path.relpath(p, SKILL)
        q = f"{PRISTINE}/{rel}"
        if os.path.exists(q):
            continue
        try:
            s = open(p, encoding="utf-8").read()
        except UnicodeDecodeError:
            continue
        if TOKEN.search(s):
            os.makedirs(os.path.dirname(q), exist_ok=True)
            shutil.copy2(p, q)


def required():
    q = f"{SKILL}/setup/questions.json"
    if not os.path.exists(q):
        return []
    return [x["key"] for x in json.load(open(q)).get("questions", []) if x.get("required")]


def status(p):
    sk = p.get("skills", {}).get(NAME, {})
    asked = {k: v for k, v in DEFAULTS.items() if k != "transcriber"}      # the transcriber is always asked, never assumed
    flat = {**asked, **qdefaults(), **{k: v for k, v in p.items() if k != "skills"}, **sk}
    missing = [k for k in required() if flat.get(k) in (None, "", [], {})]
    return {"skill": NAME, "profile": PFILE, "profile_exists": os.path.exists(PFILE),
            "configured": os.path.exists(f"{SKILL}/.configured") and not missing, "missing_answers": missing}


def main():
    a = sys.argv[1:]
    p = load()
    if a[:1] == ["--status"]:
        print(json.dumps(status(p), indent=1))
        return
    if a[:1] in (["--set"], ["--set-skill"]):
        target = p if a[0] == "--set" else p.setdefault("skills", {}).setdefault(NAME, {})
        for kv in a[1:]:
            k, _, v = kv.partition("=")
            target[k.strip()] = parse(v)
        save(p)
        print("saved", ", ".join(kv.split("=")[0] for kv in a[1:]), "->", PFILE)
        return

    t = tokens(p)
    snapshot()
    left = {}
    n = 0
    for d, _, files in os.walk(PRISTINE):
        for f in files:
            src = os.path.join(d, f)
            rel = os.path.relpath(src, PRISTINE)
            s = open(src, encoding="utf-8").read()
            out = TOKEN.sub(lambda m: t.get(m.group(1), m.group(0)), s)
            for m in TOKEN.finditer(out):
                left.setdefault(m.group(1), set()).add(rel)
            dst = f"{SKILL}/{rel}"
            open(dst, "w", encoding="utf-8").write(out)
            shutil.copymode(src, dst)
            n += 1

    # shared files the skills expect inside their own folder
    copied = []
    if os.path.isdir(f"{SKILL}/assets"):
        if os.path.isdir(f"{PDIR}/assets/fonts"):
            os.makedirs(f"{SKILL}/assets/fonts", exist_ok=True)
            for f in os.listdir(f"{PDIR}/assets/fonts"):
                shutil.copy2(f"{PDIR}/assets/fonts/{f}", f"{SKILL}/assets/fonts/{f}")
                copied.append("fonts/" + f)
        for f in ("avatar.jpg", "sfx_map.json", "music.json"):
            if os.path.exists(f"{PDIR}/assets/{f}"):
                shutil.copy2(f"{PDIR}/assets/{f}", f"{SKILL}/assets/{f}")
                copied.append(f)
        if os.path.isdir(f"{PDIR}/assets/reels"):                        # reel covers for opening graphics
            shutil.copytree(f"{PDIR}/assets/reels", f"{SKILL}/assets/reels", dirs_exist_ok=True)
            copied.append("reels/")
    for k in FONT_KEYS:                                                  # a font given as a file must actually be there
        spec = p.get(k)
        fn = spec if isinstance(spec, str) else (spec or {}).get("file")
        if fn and os.path.isdir(f"{SKILL}/assets") and not os.path.exists(f"{SKILL}/assets/fonts/{os.path.basename(fn)}"):
            print(f"WARNING {k}: {os.path.basename(fn)} is not in {PDIR}/assets/fonts - copy the font file there and run this again")

    st = status(p)
    print(f"{NAME}: filled {n} files from {PFILE}" + (f"; copied {', '.join(copied)}" if copied else ""))
    if left or st["missing_answers"]:
        if st["missing_answers"]:
            print("STILL TO ASK:", ", ".join(st["missing_answers"]))
        for k, files in sorted(left.items()):
            print(f"UNFILLED @@{k}@@ in: {', '.join(sorted(files))}")
        if os.path.exists(f"{SKILL}/.configured"):
            os.remove(f"{SKILL}/.configured")
        sys.exit(1)
    p.setdefault("skills", {}).setdefault(NAME, {})["configured"] = datetime.date.today().isoformat()
    save(p)
    h = hashlib.sha1(json.dumps(t, sort_keys=True).encode()).hexdigest()[:10]
    open(f"{SKILL}/.configured", "w").write(f"Configured {datetime.date.today().isoformat()} from {PFILE} ({h}).\n"
                                            "Delete this file, or say 'redo my setup', to run the setup questions again.\n")
    print("configured: every placeholder is filled.")


if __name__ == "__main__":
    main()
