"""Slice-listening: hear the voice in short overlapping windows, so nothing is smoothed away.

A transcript of the whole file hides false starts, "ahh"s, throat noises and repeated takes: Whisper tidies them up.
This re-transcribes the voice in short windows (1.6 s long, starting every 1 s), each on its own, and lists what each
window really says, then flags what to listen to: filler sounds, a word said twice, a broken-off word, non-speech noises,
a line said again a few seconds later (the same 4 words), places Whisper couldn't read cleanly (a glitch, a doubled take
or noise), and every pause over 0.4 s. Run it on the RAW voice to pick takes, and on the cut (the voice alone, without
music) before every render, and again after any late voice edit. Check each flag by ear.

    python slice_listen.py VOICE.wav|VIDEO.mp4 [-o slices.txt] [--from 0] [--to 0] [--window 1.6] [--step 1.0]
                           [--gap 0.4] [--gap-db -35]

Runs Whisper on the NVIDIA graphics card when PyTorch can use one (about 4x faster), on the processor otherwise.
The GTX 16xx cards can't do half precision properly, so it always uses full precision.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

RATE = 16000
FILLERS = re.compile(r"\b(u+h+m*|u+m+|a+h+m*|a+hem|e+r+m*|h+m+|m+h*m+|o+h+)\b", re.I)
NOISE = re.compile(r"[\[(][^\])]*[\])]|\*[^*]+\*")
PROMPT = "Umm, uh, ahh, hmm."
REPEAT_GAP = (2.0, 20.0)  # seconds between the two takes of a repeated line
GLITCH_JOIN = 2.5  # garbled windows closer than this are one place to listen to


def stamp(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def device():
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def load_audio(path, start, end):
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-ss", str(start)] + (["-to", str(end)] if end else []) + \
          ["-i", str(path), "-map", "0:a:0", "-ac", "1", "-ar", str(RATE), "-f", "s16le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True, stdin=subprocess.DEVNULL).stdout
    import numpy as np
    return np.frombuffer(raw, np.int16).astype("float32") / 32768.0


def pauses(path, start, end, gap, db):
    """Every pause longer than `gap` seconds, as (start, length)."""
    cmd = ["ffmpeg", "-nostdin", "-v", "info", "-ss", str(start)] + (["-to", str(end)] if end else []) + \
          ["-i", str(path), "-map", "0:a:0", "-af", f"silencedetect=noise={db}dB:d={gap}", "-f", "null", "-"]
    err = subprocess.run(cmd, capture_output=True, text=True, errors="replace", stdin=subprocess.DEVNULL).stderr
    out, began = [], None
    for line in err.splitlines():
        m = re.search(r"silence_start: (-?[\d.]+)", line)
        if m:
            began = float(m.group(1))
        m = re.search(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", line)
        if m and began is not None:
            out.append((start + max(0.0, began), float(m.group(2))))
            began = None
    return out


def garbled(text, window):
    """Whisper looped (the same 3 words three times) or heard far more words than the window can hold."""
    w = re.findall(r"[a-z0-9']+", text.lower())
    grams = [" ".join(w[k:k + 3]) for k in range(len(w) - 2)]
    return len(w) > 8 * window + 2 or any(grams.count(g) >= 3 for g in set(grams))


def flags_for(text):
    found = []
    if FILLERS.search(text):
        found.append("filler")
    if NOISE.search(text):
        found.append("noise")
    words = re.findall(r"[a-z']+", text.lower())
    if any(a == b and (len(a) > 1 or a == "i") for a, b in zip(words, words[1:])):
        found.append("said twice")
    if re.search(r"\b[a-z']+-\s+[a-z']", text.lower()):  # a broken-off word, then more speech: "way mo- way more"
        found.append("false start")
    return found


def when(line):
    m = re.match(r"(\d+):([\d.]+)", line)
    return int(m.group(1)) * 60 + float(m.group(2)) if m else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("input")
    ap.add_argument("-o", "--output", default="")
    ap.add_argument("--from", dest="start", type=float, default=0.0)
    ap.add_argument("--to", dest="end", type=float, default=0.0)
    ap.add_argument("--window", type=float, default=1.6)
    ap.add_argument("--step", type=float, default=1.0)
    ap.add_argument("--gap", type=float, default=0.4, help="list every pause longer than this (seconds); 0 skips it")
    ap.add_argument("--gap-db", type=float, default=-35.0, help="how quiet counts as a pause (dB)")
    ap.add_argument("--model", default="", help="Whisper model; default small.en on the card, base.en on the processor")
    ap.add_argument("--cpu", action="store_true")
    a = ap.parse_args()
    try:
        import whisper
    except ImportError:
        sys.exit("Slice-listening needs Whisper: Editors.Hub's setup step 'Graphics card and checks' installs it.")
    dev = "cpu" if a.cpu else device()
    name = a.model or ("small.en" if dev == "cuda" else "base.en")
    try:
        model = whisper.load_model(name, device=dev)
    except Exception as e:  # the card's memory is busy, or the driver is too old
        print(f"The graphics card couldn't load Whisper ({str(e)[:160]}); using the processor.", file=sys.stderr)
        dev, name = "cpu", a.model or "base.en"
        model = whisper.load_model(name, device="cpu")
    audio = load_audio(a.input, a.start, a.end)
    length = len(audio) / RATE
    print(f"Slice-listening {stamp(length)} on the {'GRAPHICS CARD' if dev == 'cuda' else 'PROCESSOR'} ({name}), "
          f"{a.window:g} s windows every {a.step:g} s ...", file=sys.stderr)
    def hear(t, prompt=PROMPT):
        piece = audio[int(t * RATE):int((t + a.window) * RATE)]
        r = model.transcribe(piece, language="en", fp16=False, temperature=0.0, condition_on_previous_text=False,
                             initial_prompt=prompt, no_speech_threshold=0.6, word_timestamps=False)
        return " ".join(s["text"].strip() for s in r["segments"]).strip()

    raw, t = [], 0.0
    while t < length - 0.2:
        text = hear(t)
        if garbled(text, a.window):
            # Whisper often invents a loop on a short window, most of all after the filler prompt. Listen again without
            # it, and a little later; only a window that stays garbled every time is worth a listen.
            again = [hear(t, None), hear(min(t + 0.3, max(0.0, length - a.window)), None)]
            clean = next((x for x in again if not garbled(x, a.window)), None)
            if clean is not None:
                text = clean
        if text.strip(" .") and text.strip() != PROMPT:
            raw.append((a.start + t, text, flags_for(text)))
        t += a.step

    lines, flagged, glitches = [], [], []
    alone = {"filler", "noise"}  # a short sound on its own may fall in one window only
    for i, (at, text, marks) in enumerate(raw):
        if garbled(text, a.window):
            lines.append(f"{stamp(at)}-{stamp(at + a.window)}  [garbled] {text[:120]}   <-- glitch?")
            if glitches and at - glitches[-1][1] <= GLITCH_JOIN:
                glitches[-1][1] = at
            else:
                glitches.append([at, at])
            continue
        near = [m for j, (b, _, m) in enumerate(raw) if j != i and abs(b - at) < a.window]
        short = len(re.findall(r"[a-z']+", text.lower())) <= 3
        sure = [k for k in marks if (k in alone and short) or any(k in m for m in near)]  # else an overlapping window must agree
        lines.append(f"{stamp(at)}-{stamp(at + a.window)}  {text}" + (f"   <-- {', '.join(sure)}" if sure else ""))
        if sure:
            flagged.append(f"{stamp(at)}  {', '.join(sure)}: {text}")
    for s, e in glitches:
        span = stamp(s) if e == s else f"{stamp(s)}-{stamp(e + a.window)}"
        flagged.append(f"{span}  glitch? the voice here couldn't be read cleanly (a cut, a doubled take or noise)")

    # a line said twice: the same 4 words heard again a little later (not just the next, overlapping window)
    seen, pairs = {}, set()
    for at, text, _ in raw:
        if garbled(text, a.window):
            continue
        w = re.findall(r"[a-z0-9']+", text.lower())
        for k in range(len(w) - 3):
            gram = " ".join(w[k:k + 4])
            first = seen.get(gram)
            if first is not None and REPEAT_GAP[0] <= at - first <= REPEAT_GAP[1]:
                if not any(abs(first - f) <= 3 and abs(at - s) <= 3 for f, s in pairs):  # one flag per repeated line
                    flagged.append(f"{stamp(first)} and {stamp(at)}  line said twice: \"{gram}...\"")
                    pairs.add((first, at))
                seen[gram] = None
            elif first is None and gram not in seen:
                seen[gram] = at
    flagged.sort(key=when)

    gaps = pauses(a.input, a.start, a.end, a.gap, a.gap_db) if a.gap > 0 else []
    report = ["SLICES (each window on its own):", *lines, "", f"LISTEN TO THESE ({len(flagged)}):", *flagged]
    if a.gap > 0:
        report += ["", f"PAUSES OVER {a.gap:g} s ({len(gaps)}; listen to each: a breath, or a cut that left a hole?):",
                   *[f"{stamp(s)}  pause {d:.2f} s" for s, d in gaps]]
    out = "\n".join(report) + "\n"
    if a.output:
        Path(a.output).write_text(out, encoding="utf-8")
        print(f"{len(lines)} windows, {len(flagged)} to listen to, {len(gaps)} pauses -> {a.output}")
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    main()
