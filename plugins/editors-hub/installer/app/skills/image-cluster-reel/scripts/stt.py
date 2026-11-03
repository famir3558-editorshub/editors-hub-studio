#!/usr/bin/env python3
"""One transcription door for every script in this pack.

    from stt import transcribe, el_key
    J = transcribe("audio.flac", diarize=False, keyterms=None)     # -> {"words": [{"text", "start", "end", "type": "word", "speaker_id"}], "_engine": ...}

    python3 stt.py <audio or video file> [out.json] [--diarize]    # command-line use

The result always has the ElevenLabs Scribe shape, whichever engine ran, so nothing downstream changes.

Engine = the "transcriber" answer in ~/.claude/creator-profile/profile.json (or $STT_ENGINE):
  elevenlabs  (recommended) ElevenLabs Scribe through the API. Most accurate words AND word edges, speaker labels,
              about $0.22 per hour of audio. Needs ELEVENLABS_API_KEY in the environment or the shell profile.
  local       Runs on this computer through HyperFrames (`npx hyperframes transcribe`: Parakeet if installed, else
              whisper.cpp). Free and private. Word edges are a little looser, so the tight cut needs a closer look,
              and there are NO speaker labels (long calls with several people are harder to read).
The key is never printed and never asked for in chat: the creator adds the export line to their shell profile themselves.
"""
import json, os, re, subprocess, sys, tempfile

HOME = os.path.expanduser("~")
PROFILE = os.path.expanduser(os.environ.get("CREATOR_PROFILE_DIR", "~/.claude/creator-profile")) + "/profile.json"
RC = (".zshrc", ".zprofile", ".zshenv", ".bashrc", ".bash_profile", ".profile")


def profile():
    return json.load(open(PROFILE)) if os.path.exists(PROFILE) else {}


def engine():
    return (os.environ.get("STT_ENGINE") or profile().get("transcriber") or "elevenlabs").lower()


def el_key(required=True):
    """ElevenLabs key from the environment or an `export ELEVENLABS_API_KEY=` line in the shell profile. Never printed."""
    k = os.environ.get("ELEVENLABS_API_KEY")
    if not k:
        for rc in RC:
            p = f"{HOME}/{rc}"
            if os.path.exists(p):
                for line in open(p, errors="ignore"):
                    m = re.match(r"\s*(?:export\s+)?ELEVENLABS_API_KEY=(.*)", line)
                    if m:
                        k = m.group(1).strip().strip("\"'")
    if not k and required:
        sys.exit("ELEVENLABS_API_KEY not found (environment or shell profile). Ask the creator to add\n"
                 "  export ELEVENLABS_API_KEY=\"...\"\nto ~/.zshrc themselves (never ask for the key in chat), "
                 "or switch to local transcription: python3 setup/apply_profile.py --set transcriber=local")
    return k


def _elevenlabs(audio, diarize, keyterms, language, events, speakers=None):
    import requests
    key = el_key()
    data = {"timestamps_granularity": "word",
            "tag_audio_events": "true" if events else "false", "diarize": "true" if diarize else "false"}
    if language:
        data["language_code"] = language                                # None = let ElevenLabs detect the language
    if speakers:
        data["num_speakers"] = str(int(speakers))
    r = None
    for model in ("scribe_v2", "scribe_v1"):
        d = dict(data, model_id=model)
        fields = list(d.items()) + ([("keyterms", k) for k in keyterms] if keyterms and model == "scribe_v2" else [])
        r = requests.post("https://api.elevenlabs.io/v1/speech-to-text", headers={"xi-api-key": key}, data=fields,
                          files={"file": open(audio, "rb")}, timeout=3600)
        if r.ok:
            J = r.json()
            J["_engine"] = "elevenlabs/" + model
            return J
        print(model, r.status_code, r.text[:300])
        if r.status_code in (401, 403):                                 # a bad or under-permissioned key fails the same way on every model
            sys.exit("ElevenLabs rejected the key. Ask the creator to check the key in their shell profile has Speech to Text access.")
    r.raise_for_status()


def _local(audio, language):
    """HyperFrames' local transcriber. Writes transcript.json ([{text, start, end}]) into a temp dir."""
    with tempfile.TemporaryDirectory() as d:
        cmd = ["npx", "-y", "hyperframes", "transcribe", os.path.abspath(audio), "--json", "-d", d]
        if language and language != "en":
            cmd += ["--language", language, "--model", "small"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        tp = f"{d}/transcript.json"
        if r.returncode != 0 or not os.path.exists(tp):
            sys.exit("local transcription failed:\n" + (r.stderr or r.stdout)[-1200:] +
                     "\nCheck `npx hyperframes doctor`, or use ElevenLabs.")
        meta = {}
        try:
            meta = json.loads(r.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            pass
        W = json.load(open(tp))
    words = [{"text": w["text"].strip(), "start": float(w["start"]), "end": float(w["end"]), "type": "word", "speaker_id": "speaker_0"}
             for w in W if w.get("text", "").strip()]
    for a, b in zip(words, words[1:]):                                   # whisper can give a word a zero or negative length
        if a["end"] <= a["start"]:
            a["end"] = min(a["start"] + 0.12, b["start"]) if b["start"] > a["start"] else a["start"] + 0.08
    return {"words": words, "text": " ".join(w["text"] for w in words),
            "_engine": "local/" + str(meta.get("engine", "whisper")) + "/" + str(meta.get("model", ""))}


def transcribe(audio, diarize=False, keyterms=None, language="en", events=True, speakers=None):
    """language=None lets ElevenLabs detect it. speakers = a known number of people (ElevenLabs only)."""
    e = engine()
    if e.startswith("eleven"):
        return _elevenlabs(audio, diarize, keyterms, language, events, speakers)
    if diarize:
        print("NOTE local transcription has no speaker labels: every word is marked speaker_0. Work out who is speaking from what is said.")
    print("NOTE local transcription: word edges are looser than ElevenLabs. Check the tight cut for clipped words before rendering.")
    return _local(audio, language)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    src = args[0]
    tmp = None
    if not src.lower().endswith((".wav", ".flac", ".mp3", ".m4a")):
        tmp = tempfile.mktemp(suffix=".flac")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000", tmp], check=True)
    J = transcribe(tmp or src, diarize="--diarize" in sys.argv)
    out = args[1] if len(args) > 1 else os.path.splitext(src)[0] + ".words.json"
    json.dump(J, open(out, "w"))
    print(J["_engine"], len(J["words"]), "words ->", out)
    if tmp:
        os.remove(tmp)
