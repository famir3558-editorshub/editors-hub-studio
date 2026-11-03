"""Shared helpers for the broll-stacked-text-edit skill: work folders, the creator's settings (filled in by setup),
probing, fonts, the B-roll library location, and the one door to transcription (stt.py)."""
import glob, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import stt  # noqa: E402

HOME = os.path.expanduser("~")
NAME = "broll-stacked-text-edit"
PDIR = os.path.dirname(stt.PROFILE)                         # the creator profile folder (shared by every skill in the pack)
WORK_ROOT = os.path.expanduser("@@WORK_ROOT@@")             # small working files, one folder per slug
ACCENT = "@@ACCENT@@"                                       # the brand accent colour (the key word in a stack)
# the creator's answers for this skill (setup/SETUP.md). Change the answer and re-run setup/apply_profile.py, never this text.
SET = {"caption_size": "@@CAPTION_SIZE@@", "stack_size": "@@STACK_SIZE@@", "source_framing": "@@SOURCE_FRAMING@@",
       "broll_max_share": "@@BROLL_MAX_SHARE@@"}
VIDEO_EXT = (".mp4", ".mov", ".m4v", ".mxf", ".mkv", ".avi", ".webm")
if "@" * 2 in WORK_ROOT + ACCENT + "".join(SET.values()):
    sys.exit("This skill has not been set up yet. Run the setup interview (setup/SETUP.md), then python3 setup/apply_profile.py")


def num(key, default):
    """A numeric setting; the default when the answer is not a number."""
    try:
        return float(SET[key])
    except (ValueError, TypeError):
        return default


def skill_answers():
    """This skill's own answers from the creator profile (setup/questions.json, scope skill)."""
    return stt.profile().get("skills", {}).get(NAME, {})


def output_rule():
    """Where finished videos go (setup answer `output_rule`): a folder, or text such as "beside the raw file"."""
    return str(stt.profile().get("output_rule") or "").strip()


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
    {"words": [{"text", "start", "end", "type": "word", "speaker_id"}], "_engine": ...}. The key is never printed or asked for."""
    return stt.transcribe(audio_path, diarize=diarize, events=events)


def el_words(J):
    return [[w["text"], w["start"], w["end"]] for w in J["words"]
            if w.get("type") == "word" and any(c.isalnum() for c in w["text"])]


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def find_font(names, extra_dirs=()):
    """Locate a font file by PostScript or full name (system folders, font collections, and Adobe Fonts' hidden activation folder)."""
    try:
        from fontTools.ttLib import TTFont, TTCollection
    except ImportError:
        return None
    dirs = [f"{HOME}/Library/Application Support/Adobe/CoreSync/plugins/livetype/.*/.*",
            f"{HOME}/Library/Fonts/*", "/Library/Fonts/*", "/System/Library/Fonts/*", "/System/Library/Fonts/Supplemental/*", *extra_dirs]
    for d in dirs:
        for p in glob.glob(d):
            if not p.lower().endswith((".otf", ".ttf", ".ttc")):
                continue
            try:
                fonts = [f["name"] for f in TTCollection(p, lazy=True).fonts] if p.lower().endswith(".ttc") else [TTFont(p, lazy=True)["name"]]
                if any(nm.getDebugName(6) in names or nm.getDebugName(4) in names for nm in fonts):
                    return p
            except Exception:
                pass
    return None


def font_face(spec, label):
    """A font saved in the creator profile ({"file": "X.ttf"} or {"local": ["Full Name", "PostScript-Name"]}, or a bare file name)
    -> (CSS src value, description, found). Files are looked for in this skill's assets/fonts, then the profile's assets/fonts;
    a local font is located on disk (Adobe Fonts included) so headless Chrome can load it by path."""
    if not spec:
        return None, f"{label}: nothing saved in the profile", False
    if isinstance(spec, str):
        spec = {"file": spec}
    for n in ([os.path.basename(spec["file"])] if spec.get("file") else []):
        for d in (f"{SKILL}/assets/fonts", f"{PDIR}/assets/fonts"):
            if os.path.exists(f"{d}/{n}"):
                return f'url("file://{d}/{n}")', f"{label}: {n}", True
    names = spec.get("local", [])
    if names:
        p = find_font(names)
        if p:
            return f'url("file://{p}")', f"{label}: {names[0]}", True
        return ", ".join(f'local("{n}")' for n in names), f"{label}: {names[0]} (NOT FOUND on this computer)", False
    return None, f"{label}: {spec.get('file')} is not in assets/fonts", False


def label_font(size):
    from PIL import ImageFont
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except Exception:
        return ImageFont.load_default()


def grab(path, t, out, box=None):
    """One frame at t seconds (fast seek)."""
    vf = ["-vf", f"scale={box[0]}:{box[1]}:force_original_aspect_ratio=decrease"] if box else []
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, t):.3f}", "-i", path, "-frames:v", "1", *vf, "-q:v", "3", out], check=True)


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
    """How the main video sits in the 9:16 frame. Default: the creator's `source_framing` answer (fill: portrait sources as they are, 16:9 cropped around the speaker)."""
    f = (plan or {}).get("frame") or {}
    default = SET["source_framing"] if SET["source_framing"] in ("fill", "fit") else "fill"
    return f.get("mode", default), tuple(f.get("focus", (0.5, 0.5)))


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


def broll_dirs():
    """The creator's standing B-roll folders (setup answer `broll_dirs`, a list). Every clip in them is catalogued once in a
    shared library. When the creator has indexed their footage with personal-broll-library, its footage folder is the fallback."""
    a = skill_answers().get("broll_dirs") or stt.profile().get("skills", {}).get("personal-broll-library", {}).get("footage_dir") or []
    a = [a] if isinstance(a, str) else list(a)
    return [os.path.abspath(os.path.expanduser(x)) for x in a if x]


LIB = f"{WORK_ROOT}/broll-library"


def library():
    return load(LIB, "library.json", []) if os.path.isdir(LIB) else []
