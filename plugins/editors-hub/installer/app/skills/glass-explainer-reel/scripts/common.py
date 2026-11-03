"""Shared helpers for the glass-explainer-reel skill: work folders, the creator's brand values (filled in at setup),
probing, stills, sound effects, and the one door to transcription (stt.py). The cut pipeline is the explainer panel
reel's, copied here so this skill stands alone."""
import glob, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import stt  # noqa: E402

HOME = os.path.expanduser("~")
PDIR = os.path.dirname(stt.PROFILE)                         # the creator profile folder (shared by every skill in the pack)
WORK_ROOT = os.path.expanduser("@@WORK_ROOT@@")             # small working files, one folder per slug
PROJECTS_ROOT = os.path.expanduser("@@PROJECTS_ROOT@@")     # HyperFrames projects, one folder per video
ACCENT = "@@ACCENT@@"                                       # the brand accent colour
# the creator's answers for this skill (setup/SETUP.md). Change the answer and re-run setup/apply_profile.py, never this text.
SET = {"watermark": "@@WATERMARK@@", "handle": "@@HANDLE@@", "platform": "@@PLATFORM@@", "brand_name": "@@BRAND_NAME@@"}
VIDEO_EXT = (".mp4", ".mov", ".m4v", ".mxf", ".mkv", ".avi", ".webm")
if "@" * 2 in WORK_ROOT + PROJECTS_ROOT + ACCENT + "".join(SET.values()):
    sys.exit("This skill has not been set up yet. Run the setup interview (setup/SETUP.md), then python3 setup/apply_profile.py")


def work(arg):
    """A slug ('my-video') or a path -> the work directory."""
    d = arg if os.sep in arg else f"{WORK_ROOT}/{arg}"
    os.makedirs(d, exist_ok=True)
    return d


def load(W, name, default=None):
    p = f"{W}/{name}"
    return json.load(open(p)) if os.path.exists(p) else default


def save(W, name, obj):
    json.dump(obj, open(f"{W}/{name}", "w"), indent=1)


def run(cmd):
    subprocess.run(cmd, check=True)


def probe(path):
    j = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", path]))
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    rot = 0
    for sd in v.get("side_data_list", []):
        rot = sd.get("rotation", rot)
    w, h = v["width"], v["height"]
    if abs(int(rot)) % 180 == 90:
        w, h = h, w
    return {"w": w, "h": h, "fps": v["r_frame_rate"], "avg_fps": v["avg_frame_rate"],
            "dur": float(j["format"]["duration"]), "transfer": v.get("color_transfer", ""),
            "audio": any(s["codec_type"] == "audio" for s in j["streams"])}


def scribe(audio_path):
    """Transcribe with the engine chosen at setup (stt.py). The result always has the ElevenLabs Scribe shape:
    {"words": [{"text", "start", "end", "type"}]}, whichever engine ran."""
    return stt.transcribe(audio_path, diarize=False)


def el_words(J):
    return [[w["text"], w["start"], w["end"]] for w in J["words"]
            if w.get("type") == "word" and any(c.isalnum() for c in w["text"])]


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def find_font(postscript_names, extra_dirs=()):
    """Locate a font file by PostScript name, including Adobe Fonts' hidden activation folder."""
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        return None
    dirs = [f"{HOME}/Library/Application Support/Adobe/CoreSync/plugins/livetype/.*/.*",
            f"{HOME}/Library/Fonts/*", "/Library/Fonts/*", *extra_dirs]
    for d in dirs:
        for p in glob.glob(d):
            if not p.lower().endswith((".otf", ".ttf")):
                continue
            try:
                if TTFont(p, lazy=True)["name"].getDebugName(6) in postscript_names:
                    return p
            except Exception:
                pass
    return None


def label_font(size):
    from PIL import ImageFont
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except Exception:
        return ImageFont.load_default()


def grab(path, t, out, box=None):
    """One frame at t seconds (fast seek)."""
    vf = ["-vf", f"scale={box[0]}:{box[1]}:force_original_aspect_ratio=decrease"] if box else []
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, t):.3f}", "-i", path, "-frames:v", "1", *vf, "-pix_fmt", "yuvj420p", "-strict", "unofficial", "-q:v", "3", out], check=True)


CW, CH = 1080, 1920           # the finished video is always 9:16


def canvas(M=None, plan=None):
    return CW, CH


def placed(w, h, mode, focus=(0.5, 0.5)):
    """Where footage of size w x h sits in the 9:16 frame: (scaled w, scaled h, x, y). x/y negative = cropped.
    fill = covers the whole frame (cropped around focus); fit = the whole image inside the frame, black around it."""
    s = max(CW / w, CH / h) if mode == "fill" else min(CW / w, CH / h)
    sw, sh = round(w * s), round(h * s)
    if mode == "fill":
        return sw, sh, -round((sw - CW) * focus[0]), -round((sh - CH) * focus[1])
    return sw, sh, (CW - sw) // 2, (CH - sh) // 2


def frame_mode(M, plan):
    """How the main video sits in the 9:16 frame. Default: fill (portrait sources as they are, 16:9 cropped around him)."""
    f = (plan or {}).get("frame") or {}
    return f.get("mode", "fill"), tuple(f.get("focus", (0.5, 0.5)))


def vf_place(w, h, mode, focus=(0.5, 0.5)):
    """ffmpeg filter that puts footage into the 9:16 frame."""
    if mode == "fill":
        return (f"scale={CW}:{CH}:force_original_aspect_ratio=increase,"
                f"crop={CW}:{CH}:(iw-{CW})*{focus[0]}:(ih-{CH})*{focus[1]},setsar=1")
    return f"scale={CW}:{CH}:force_original_aspect_ratio=decrease,pad={CW}:{CH}:(ow-iw)/2:(oh-ih)/2:black,setsar=1"


def base_frame(M, plan, t):
    """The cut's frame at t as a PIL image in the 9:16 frame (same placement the render uses)."""
    from PIL import Image
    import tempfile
    p = tempfile.mktemp(suffix=".jpg"); grab(M["cut"], t, p)
    im = Image.open(p).convert("RGB"); os.remove(p)
    mode, focus = frame_mode(M, plan); sw, sh, x, y = placed(im.width, im.height, mode, focus)
    out = Image.new("RGB", (CW, CH)); out.paste(im.resize((sw, sh)), (x, y)); return out


def sheet(tiles, out, cols, tile_w):
    """tiles: [(PIL image, label)] -> one labelled contact sheet."""
    from PIL import Image, ImageDraw
    f = label_font(20); th = max(int(im.height * tile_w / im.width) for im, _ in tiles); rows = -(-len(tiles) // cols)
    S = Image.new("RGB", (cols * (tile_w + 8) + 8, rows * (th + 38) + 8), (24, 24, 24)); d = ImageDraw.Draw(S)
    for k, (im, lab) in enumerate(tiles):
        x, y = 8 + (k % cols) * (tile_w + 8), 8 + (k // cols) * (th + 38)
        S.paste(im.resize((tile_w, int(im.height * tile_w / im.width))), (x, y)); d.text((x + 2, y + th + 6), lab, fill=(235, 235, 235), font=f)
    S.save(out, quality=88)


def brand(W=None):
    """Brand values for a build, from the creator's setup (accent colour, brand name, optional watermark handle),
    overridden by <work>/brand.json when ONE video needs its own accent (for example a client's video):
    {"accent": "#RRGGBB", "handle": "@name"}. The watermark is drawn only when the creator turned it on AND a handle is set."""
    handle = SET["handle"].strip()
    on = SET["watermark"].strip().lower() in ("on", "yes", "true", "1")
    b = {"name": SET["brand_name"], "accent": ACCENT, "handle": handle if on and handle.lower() not in ("", "not set", "none") else None,
         "platform": SET["platform"].strip().lower()}
    if W and os.path.exists(f"{W}/brand.json"):
        b.update(json.load(open(f"{W}/brand.json")))
    re.fullmatch(r"#[0-9A-Fa-f]{6}", b.get("accent", "")) or sys.exit("brand: 'accent' must be a #RRGGBB value (profile answer `accent`, or <work>/brand.json)")
    return b


BRAND_FILES = ("logo.png", "wordmark.png")   # optional: square logo, wide wordmark (light, for dark backgrounds). Nothing in the engine needs them.


def brand_files():
    """{file name: path} for the optional brand images the creator gave at setup, from the skill's assets/ folder, then the profile's."""
    out = {}
    for f in BRAND_FILES:
        for d in (f"{SKILL}/assets", f"{PDIR}/assets"):
            if os.path.exists(f"{d}/{f}"):
                out[f] = f"{d}/{f}"; break
    return out


def avatar_path():
    """The creator's profile picture (assets/avatar.jpg in the skill, else in the profile), or None."""
    for d in (f"{SKILL}/assets", f"{PDIR}/assets"):
        if os.path.exists(f"{d}/avatar.jpg"):
            return f"{d}/avatar.jpg"
    return None


def font_report():
    """Check that every font named in the profile can really be loaded, so a fallback never ships unnoticed."""
    P = stt.profile(); lines = []
    for key, role in (("font_main_bold", "main font (bold)"), ("font_main_regular", "main font (regular)"), ("font_accent", "emphasis font"),
                      ("font_caption", "caption font")):
        spec = P.get(key) or ({"file": "PlayfairDisplay-Italic.ttf"} if key == "font_accent" else None)   # the shipped default emphasis font
        if spec is None:
            continue
        spec = {"file": spec} if isinstance(spec, str) else spec
        if spec.get("file"):
            ok = os.path.exists(f"{SKILL}/assets/fonts/{os.path.basename(spec['file'])}")
            lines.append(f"{role}: {os.path.basename(spec['file'])} {'found' if ok else 'NOT in assets/fonts: copy it to the profile assets/fonts folder and run setup/apply_profile.py again'}")
        elif spec.get("local"):
            ok = find_font(spec["local"])
            lines.append(f"{role}: {spec['local'][0]} " + ("installed" if ok else "NOT FOUND on this computer (an Adobe Font needs Creative Cloud running; fontTools is needed for this check). "
                                                                                 "It would fall back to another font: tell the creator, do not ship the fallback."))
    return lines


SFX_FALLBACK = {"swish": "woosh", "swoosh": "woosh", "slide": "woosh", "swirl": "woosh", "whip": "woosh", "pops": "pop", "shine": "pop",
                "shine2": "shine", "accept": "pop", "access": "pop", "dtext": "pop", "data": "pop"}


def load_sfx(project=None):
    """Sounds are played by ROLE from sfx_map.json, made at setup with scripts/sfx_probe.py from the creator's own
    sound-effects folder. Looked for in the project, the skill's assets/, then the creator profile's assets/.
    Returns {role: (path, measured peak dB, max seconds)}. No map = the video is delivered without sound effects."""
    for p in ([f"{project}/sfx_map.json"] if project else []) + [f"{SKILL}/assets/sfx_map.json", f"{PDIR}/assets/sfx_map.json"]:
        if os.path.exists(p):
            M = json.load(open(p)); root = os.path.expanduser(M.get("dir", "")); S = {}
            for name, v in M.get("sounds", {}).items():
                f = v["file"] if os.path.isabs(v["file"]) else os.path.join(root, v["file"])
                if os.path.exists(f):
                    S[name] = (f, float(v.get("peak", 0.0)), float(v.get("max", 0.6)))
                else:
                    print("sfx_map: missing file for", name, "->", f)
            return S
    print("NOTE no sfx_map.json: no sound effects will be added (run scripts/sfx_probe.py on a sound-effects folder to make one).")
    return {}


def sfx_role(S, n):
    """The role to play for a cue: itself if the map has it, else its nearest stand-in, else None."""
    seen = set()
    while n not in S and n in SFX_FALLBACK and n not in seen:
        seen.add(n); n = SFX_FALLBACK[n]
    return n if n in S else None
