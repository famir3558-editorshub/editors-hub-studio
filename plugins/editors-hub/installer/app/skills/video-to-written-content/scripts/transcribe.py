#!/usr/bin/env python3
"""
Transcribe a YouTube video or local video/audio file, word by word, through the pack's one transcription door
(scripts/stt.py): ElevenLabs Speech-to-Text (Scribe) or the free local transcriber, whichever was chosen at setup.

Usage:
  python transcribe.py <youtube-url-or-file-path> [--out <project-folder>] [--keyterms "Brand Name,Guest Name"] [--speakers 2]

What it does:
  1. Downloads audio from a YouTube URL (yt-dlp) or extracts audio from a local file (ffmpeg).
  2. Sends the full audio to stt.transcribe(): the engine is the "transcriber" answer in the creator profile
     (elevenlabs = most accurate, speaker labels; local = free, on this computer, no speaker labels).
  3. Writes:
       <out>/_source/transcript.raw.json   full result in the ElevenLabs shape (words, timestamps, speakers)
       <out>/_source/transcript.raw.md     readable transcript, paragraphed, with [mm:ss] markers
       <out>/_source/video-meta.json       title, url, duration (when available), engine used

From the creator profile (skills -> video-to-written-content), when setup has been run:
  keyterms     names, brands and terms to spell correctly: always passed, merged with --keyterms
  output_dir   parent folder for the project folders (default ./video-content)

Needs: ffmpeg, yt-dlp (for URLs). ElevenLabs engine: ELEVENLABS_API_KEY in the environment or shell profile and
`pip install requests`. Local engine: `npx hyperframes` (Node 22).
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stt  # noqa: E402  (scripts/stt.py: the shared transcription door)

SKILL_NAME = Path(__file__).resolve().parent.parent.name


def skill_answers():
    """This skill's setup answers from the creator profile. Empty when setup has not been run."""
    try:
        return (stt.profile().get("skills") or {}).get(SKILL_NAME) or {}
    except (OSError, ValueError):
        return {}


def as_terms(v):
    """Setup answers may be a JSON list or a comma-separated string. 'none' means no terms."""
    if isinstance(v, str):
        v = v.split(",")
    return [t for t in (str(x).strip() for x in (v or [])) if t and t.lower() != "none"]


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def need(binary, hint):
    if shutil.which(binary) is None:
        die(f"'{binary}' is not installed. {hint}")


def is_url(s):
    return bool(re.match(r"^https?://", s.strip()))


def slugify(text, max_len=60):
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:max_len].strip("-") or "video"


def fetch_youtube_audio(url, workdir):
    need("yt-dlp", "Install with: pip install yt-dlp  (or brew install yt-dlp)")
    need("ffmpeg", "Install with: brew install ffmpeg")
    meta = {}
    try:
        info = subprocess.run(
            ["yt-dlp", "--dump-single-json", "--no-playlist", url],
            capture_output=True, text=True, check=True,
        )
        j = json.loads(info.stdout)
        meta = {"title": j.get("title"), "url": url, "duration_s": j.get("duration"),
                "channel": j.get("channel"), "upload_date": j.get("upload_date")}
    except Exception as e:
        print(f"Warning: could not read video metadata ({e})", file=sys.stderr)
        meta = {"title": None, "url": url}

    out_tmpl = str(Path(workdir) / "audio.%(ext)s")
    subprocess.run(
        ["yt-dlp", "--no-playlist", "-f", "bestaudio/best", "-x", "--audio-format", "mp3",
         "--audio-quality", "0", "-o", out_tmpl, url],
        check=True,
    )
    audio = next(Path(workdir).glob("audio.*"), None)
    if not audio:
        die("yt-dlp finished but no audio file was produced.")
    return audio, meta


def extract_local_audio(path, workdir):
    p = Path(path).expanduser()
    if not p.exists():
        die(f"File not found: {p}")
    need("ffmpeg", "Install with: brew install ffmpeg")
    audio = Path(workdir) / "audio.mp3"
    # Mono, 44.1kHz, high bitrate: small upload, no loss of speech clarity.
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(p), "-vn", "-ac", "1", "-ar", "44100", "-b:a", "192k", str(audio)],
        check=True, capture_output=True,
    )
    return audio, {"title": p.stem, "source_file": str(p)}


def run_transcription(audio_path, keyterms, speakers, language):
    """Transcribe through stt.py. Returns the ElevenLabs-shaped result ({"words": [...], "text": ..., "_engine": ...})."""
    engine = stt.engine()
    if engine.startswith("eleven"):
        try:
            import requests  # noqa: F401
        except ImportError:
            die("Python package 'requests' missing. Run: pip3 install requests")
        stt.el_key()   # stops with the how-to-fix message when no key is set; never prints the key
    elif speakers and speakers > 1:
        print("Note: local transcription has no speaker labels. Work out who is speaking from what is said.",
              file=sys.stderr)
    try:
        return stt.transcribe(str(audio_path), diarize=True, keyterms=keyterms or None,
                              language=language or None, events=False, speakers=speakers or None)
    except Exception as e:   # network / HTTP errors from the API
        msg = str(e)
        if "401" in msg:
            die("ElevenLabs rejected the API key (401). Check ELEVENLABS_API_KEY in your shell profile.")
        die(f"Transcription failed: {msg[:500]}")


def to_paragraphs(words):
    """Group word-level output into readable paragraphs with [mm:ss] markers.
    New paragraph on speaker change, a pause over 1.5s, or ~90 words ending on a sentence."""
    paras, cur, start, speaker, last_end = [], [], None, None, None
    count = 0

    def flush():
        nonlocal cur, start, count
        if cur:
            text = "".join(cur).strip()
            text = re.sub(r"\s+", " ", text)
            paras.append((start, speaker, text))
        cur, start, count = [], None, 0

    # ElevenLabs sends the spaces between words as their own "spacing" items; the local engine sends words only.
    add_space = not any(w.get("type") == "spacing" for w in words)

    for w in words:
        wtype = w.get("type", "word")
        if wtype == "audio_event":
            continue
        sp = w.get("speaker_id")
        st = w.get("start")
        if cur and ((sp is not None and sp != speaker)
                    or (st is not None and last_end is not None and st - last_end > 1.5 and count > 25)
                    or (count > 90 and "".join(cur).rstrip().endswith((".", "?", "!")))):
            flush()
        if start is None and st is not None:
            start = st
        speaker = sp if sp is not None else speaker
        cur.append(w.get("text", "") + (" " if add_space else ""))
        if wtype == "word":
            count += 1
        if w.get("end") is not None:
            last_end = w["end"]
    flush()
    return paras


def fmt_ts(sec):
    if sec is None:
        return "--:--"
    sec = int(sec)
    h, m, s = sec // 3600, (sec % 3600) // 60, sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="YouTube URL or path to a video/audio file")
    ap.add_argument("--out", help="Project folder. Default: <output_dir from setup, else ./video-content>/<video-name>")
    ap.add_argument("--keyterms", default="", help="Comma-separated names/terms to bias spelling (added to the ones saved at setup)")
    ap.add_argument("--speakers", type=int, default=0, help="Number of speakers if known")
    ap.add_argument("--language", default="", help="ISO language code, e.g. en. Blank = auto-detect")
    args = ap.parse_args()

    answers = skill_answers()
    keyterms = []
    for k in as_terms(answers.get("keyterms")) + as_terms(args.keyterms):   # setup terms first, then this run's
        if k.lower() not in {x.lower() for x in keyterms}:
            keyterms.append(k)
    parent = str(answers.get("output_dir") or "").strip() or "video-content"

    with tempfile.TemporaryDirectory() as tmp:
        if is_url(args.source):
            audio, meta = fetch_youtube_audio(args.source, tmp)
        else:
            audio, meta = extract_local_audio(args.source, tmp)

        name = slugify(meta.get("title") or "video")
        out = Path(args.out).expanduser() if args.out else (Path.cwd() / Path(parent).expanduser() / name)
        (out / "_source").mkdir(parents=True, exist_ok=True)

        print(f"Transcribing ({stt.engine()})... this can take a few minutes for long videos.")
        if keyterms:
            print("Key terms: " + ", ".join(keyterms))
        result = run_transcription(audio, keyterms, args.speakers, args.language)
        meta["model"] = result.get("_engine", stt.engine())
        if keyterms:
            meta["keyterms"] = keyterms

    (out / "_source" / "transcript.raw.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
    (out / "_source" / "video-meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))

    words = result.get("words") or []
    speakers_seen = {w.get("speaker_id") for w in words if w.get("speaker_id") is not None}
    multi = len(speakers_seen) > 1
    lines = [f"# Raw transcript: {meta.get('title') or name}", ""]
    if meta.get("url"):
        lines += [f"Source: {meta['url']}", ""]
    if words:
        for st, sp, text in to_paragraphs(words):
            label = f" **{sp}:**" if multi and sp else ""
            lines.append(f"[{fmt_ts(st)}]{label} {text}")
            lines.append("")
    else:
        lines.append(result.get("text", ""))
    (out / "_source" / "transcript.raw.md").write_text("\n".join(lines))

    wc = len((result.get("text") or "").split()) or sum(1 for w in words if w.get("type", "word") == "word")
    print(f"DONE\nproject_folder={out}\nengine={meta['model']}\nwords={wc}\nspeakers={len(speakers_seen) or 1}")


if __name__ == "__main__":
    main()
