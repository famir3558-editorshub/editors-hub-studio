"""Slice-listening: hear the voice in short overlapping windows, so nothing is smoothed away.

A transcript of the whole file hides false starts, "ahh"s, throat noises and repeated takes: Whisper tidies them up.
This re-transcribes the voice in short windows (1.6 s long, starting every 1 s), each on its own, and lists what each
window really says, then flags the windows to listen to: filler sounds, a word said twice, a half word, and
non-speech noises. Run it on the cut (or the mixed voice) before every render, and check each flag by ear.

    python slice_listen.py VOICE.wav|VIDEO.mp4 [-o slices.txt] [--from 0] [--to 0] [--window 1.6] [--step 1.0]

Runs Whisper on the NVIDIA graphics card when PyTorch can use one (about 4x faster), on the processor otherwise.
The GTX 16xx cards can't do half precision properly, so it always uses full precision.
"""
import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RATE = 16000
FILLERS = re.compile(r"\b(u+h+m*|u+m+|a+h+|e+r+m*|h+m+|m+h*m+|o+h+)\b", re.I)
NOISE = re.compile(r"[\[(][^\])]*[\])]|\*[^*]+\*")
PROMPT = "Umm, uh, ahh. So, so I, I think... like, you know, hmm. (clears throat)"


def stamp(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def device():
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def load_audio(path, start, end):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start)] + (["-to", str(end)] if end else []) + \
          ["-i", str(path), "-map", "0:a:0", "-ac", "1", "-ar", str(RATE), "-f", "s16le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    import numpy as np
    return np.frombuffer(raw, np.int16).astype("float32") / 32768.0


def flags_for(text, before):
    found = []
    if FILLERS.search(text):
        found.append("filler")
    if NOISE.search(text):
        found.append("noise")
    words = re.findall(r"[a-z']+", text.lower())
    if any(a == b for a, b in zip(words, words[1:])):
        found.append("said twice")
    if re.search(r"\b\w+-(\s|$)|\.\.\.|—\s*$", text):
        found.append("cut-off word")
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("input")
    ap.add_argument("-o", "--output", default="")
    ap.add_argument("--from", dest="start", type=float, default=0.0)
    ap.add_argument("--to", dest="end", type=float, default=0.0)
    ap.add_argument("--window", type=float, default=1.6)
    ap.add_argument("--step", type=float, default=1.0)
    ap.add_argument("--model", default="", help="Whisper model; default small.en on the card, base.en on the processor")
    ap.add_argument("--cpu", action="store_true")
    a = ap.parse_args()
    try:
        import whisper
    except ImportError:
        sys.exit("Slice-listening needs Whisper: python -m pip install --user openai-whisper")
    dev = "cpu" if a.cpu else device()
    name = a.model or ("small.en" if dev == "cuda" else "base.en")
    try:
        model = whisper.load_model(name, device=dev)
    except Exception as e:  # the card's memory is busy, or the driver is too old
        print(f"The graphics card couldn't load Whisper ({str(e)[:160]}); using the processor.", file=sys.stderr)
        dev, model = "cpu", whisper.load_model(a.model or "base.en", device="cpu")
    audio = load_audio(a.input, a.start, a.end)
    length = len(audio) / RATE
    print(f"Slice-listening {stamp(length)} on the {'GRAPHICS CARD' if dev == 'cuda' else 'PROCESSOR'} ({name}), "
          f"{a.window:g} s windows every {a.step:g} s ...", file=sys.stderr)
    lines, flagged, before, t = [], [], "", 0.0
    while t < length - 0.2:
        piece = audio[int(t * RATE):int((t + a.window) * RATE)]
        r = model.transcribe(piece, language="en", fp16=False, temperature=0.0, condition_on_previous_text=False,
                             initial_prompt=PROMPT, no_speech_threshold=0.6, word_timestamps=False)
        text = " ".join(s["text"].strip() for s in r["segments"]).strip()
        if text.strip(" .") and text.strip() != PROMPT:
            at = a.start + t
            marks = flags_for(text, before)
            lines.append(f"{stamp(at)}-{stamp(at + a.window)}  {text}" + (f"   <-- {', '.join(marks)}" if marks else ""))
            if marks:
                flagged.append(f"{stamp(at)}  {', '.join(marks)}: {text}")
            before = text
        t += a.step
    report = ["SLICES (each window on its own):", *lines, "", f"LISTEN TO THESE ({len(flagged)}):", *flagged]
    out = "\n".join(report) + "\n"
    if a.output:
        Path(a.output).write_text(out, encoding="utf-8")
        print(f"{len(lines)} windows, {len(flagged)} to listen to -> {a.output}")
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    main()
