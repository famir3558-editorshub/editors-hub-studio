"""Shared helpers for the explainer-panel-reel skill (cut pipeline shared with broll-stacked-text-edit): work folders,
the creator's settings (filled in by setup), probing, stills, brand values, and the one door to transcription (stt.py)."""
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
SET = {"handle": "@@HANDLE@@", "platform": "@@PLATFORM@@", "watermark": "@@WATERMARK@@", "emphasis_scale": "@@EMPHASIS_SCALE@@",
       "heading_block": "@@HEADING_BLOCK@@", "popout": "@@POPOUT@@", "close_up_zoom": "@@CLOSE_UP_ZOOM@@",
       "proof_dir": r"@@PROOF_DIR@@", "asset_dirs": r"@@ASSET_DIRS@@"}
VIDEO_EXT = (".mp4", ".mov", ".m4v", ".mxf", ".mkv", ".avi", ".webm")
if "@" * 2 in "\n".join([WORK_ROOT, PROJECTS_ROOT, ACCENT, *SET.values()]):
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


def scribe(audio_path, diarize=False, events=True):
    """Transcribe with the engine chosen at setup (stt.py). The result always has the ElevenLabs Scribe shape:
    {"words": [{"text", "start", "end", "type", "speaker_id"}], "_engine": ...}."""
    return stt.transcribe(audio_path, diarize=diarize, events=events)


def el_words(J):
    return [[w["text"], w["start"], w["end"]] for w in J["words"]
            if w.get("type") == "word" and any(c.isalnum() for c in w["text"])]


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def find_font(postscript_names, extra_dirs=()):
    """Locate a font file by PostScript name or full name (the names given to `local()`), including Adobe Fonts' hidden activation folder."""
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
                n = TTFont(p, lazy=True)["name"]
                if n.getDebugName(6) in postscript_names or n.getDebugName(4) in postscript_names:
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
    """How the main video sits in the 9:16 frame. Default: fill (portrait sources as they are, 16:9 cropped around the speaker)."""
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


def popout_default():
    """The creator's setup answer for letting the head rise above the panel edge (06_crops.py: layout.json overrides it per video)."""
    return SET["popout"].strip().lower() not in ("off", "no", "false", "inside")


def folders(value):
    """A setup answer that names one or more folders -> the ones that exist ("none yet" and the like give nothing)."""
    out = []
    for x in re.split(r";|\n|,\s*(?=[~/])", value or ""):
        x = os.path.expanduser(x.strip().strip('"'))
        if x.startswith("/") and os.path.isdir(x):
            out.append(x)
    return out


def brand(W=None):
    """Brand values for a build, from the creator's setup (filled into this file) and optionally <work>/brand.json when ONE
    video needs different values (for example a client's video): {"accent": "#RRGGBB", "handle": "@name", ...}."""
    watermark = SET["watermark"].strip().lower() in ("yes", "true", "on", "1")
    handle = SET["handle"].strip()
    b = {"accent": ACCENT, "platform": SET["platform"].strip().lower() or "instagram",
         "handle": handle if watermark and handle and handle.lower() != "not set" else None,
         "heading_block": "underline" if SET["heading_block"].strip().lower().startswith("under") else "block"}
    try:
        b["emphasis_scale"] = float(SET["emphasis_scale"])
    except ValueError:
        b["emphasis_scale"] = 1.12
    b["zoom_full"] = 1.04 if SET["close_up_zoom"].strip().lower() in ("on", "yes", "true") else 1.0
    if W and os.path.exists(f"{W}/brand.json"):
        b.update(json.load(open(f"{W}/brand.json")))
    re.fullmatch(r"#[0-9A-Fa-f]{6}", b.get("accent", "")) or sys.exit("brand: 'accent' must be a #RRGGBB value (profile answer `accent`, or <work>/brand.json)")
    return b


def font_report():
    """Check that every font named in the profile can really be loaded, so a fallback never ships unnoticed."""
    P = stt.profile(); lines = []
    for key, role in (("font_main_bold", "main font (bold)"), ("font_caption", "caption font"), ("font_accent", "emphasis font")):
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
