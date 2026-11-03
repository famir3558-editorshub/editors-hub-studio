"""Shared helpers for this skill's scripts: work folders, probing, stills, and the one door to transcription (stt.py).
The tight-cut pipeline in this folder (01_prep -> 06_captions) works on ONE clip's source file at a time."""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)                 # <skill>/scripts : holds stt.py
SKILL = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)
import stt  # noqa: E402

HOME = os.path.expanduser("~")
WORK_ROOT = os.path.expanduser("@@WORK_ROOT@@")           # small working files, one folder per slug
PROJECTS_ROOT = os.path.expanduser("@@PROJECTS_ROOT@@")   # HyperFrames projects, one folder per clip
VIDEO_EXT = (".mp4", ".mov", ".m4v", ".mxf", ".mkv", ".avi", ".webm")
if "@" * 2 in WORK_ROOT + PROJECTS_ROOT:
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


def el_key():
    """The ElevenLabs key, read by stt.py from the environment or the shell profile. Never printed, never asked for in chat."""
    return stt.el_key()


def scribe(audio_path, diarize=False, events=True):
    """Transcribe with the engine chosen at setup (stt.py). The result always has the ElevenLabs Scribe shape:
    {"words": [{"text", "start", "end", "type": "word", "speaker_id"}], "_engine": ...}."""
    return stt.transcribe(audio_path, diarize=diarize, events=events)


def el_words(J):
    return [[w["text"], w["start"], w["end"]] for w in J["words"]
            if w.get("type") == "word" and any(c.isalnum() for c in w["text"])]


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def label_font(size):
    """A plain system font for the labels on gridded stills (never used in a video)."""
    from PIL import ImageFont
    for p in ("/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf"):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


def grab(path, t, out, box=None):
    """One frame at t seconds (fast seek)."""
    vf = ["-vf", f"scale={box[0]}:{box[1]}:force_original_aspect_ratio=decrease"] if box else []
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, t):.3f}", "-i", path, "-frames:v", "1", *vf, "-pix_fmt", "yuvj420p", "-strict", "unofficial", "-q:v", "3", out], check=True)
