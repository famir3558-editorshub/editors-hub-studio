#!/usr/bin/env python3
"""Step 2 - transcribe the whole video, speakers labelled when the transcriber can.   02_video_transcribe.py <slug>
Uses the transcriber chosen at setup (scripts/stt.py): ElevenLabs gives speaker labels; local transcription does not,
so every word comes back as S0 and you work out who is speaking from what is said.
Writes el.json (raw), words.json [[text, start, end, speaker], ...] and transcript.txt: one line per sentence with the
index of its first word, its time in the video and who is speaking. Read transcript.txt from the first line to the last
before choosing anything. An API key is read from the environment or the shell profile and never printed."""
import collections, sys
from ytcommon import work, load, save, scribe, mmss
W = work(sys.argv[1])
J = load(W, "el.json")
if not J:
    J = scribe(f"{W}/a16.flac", diarize=True, events=False)
    save(W, "el.json", J)
else:
    print("(el.json already exists: reusing it. Delete it to transcribe again.)")
LOCAL = str(J.get("_engine", "")).startswith("local")
words = [[w["text"], w["start"], w["end"], (w.get("speaker_id") or "speaker_0").replace("speaker_", "S")]
         for w in J["words"] if w.get("type") == "word" and any(c.isalnum() for c in w["text"])]
save(W, "words.json", words)
n = 0
with open(f"{W}/transcript.txt", "w") as f:
    start = 0
    for i, (t, s, e, sp) in enumerate(words):
        last = i == len(words) - 1
        gap = 0 if last else words[i + 1][1] - e
        if last or t[-1] in ".?!" or gap > 0.7 or words[i + 1][3] != sp:
            f.write(f"[w{start:<6d} {mmss(words[start][1])}] {sp}: " + " ".join(w[0] for w in words[start:i + 1])
                    + (f"   ({gap:.0f}s pause)" if gap > 4 else "") + "\n")
            if not last and words[i + 1][3] != sp:
                f.write("\n")
            start = i + 1; n += 1
share = collections.Counter(w[3] for w in words)
print(f"{len(words)} words, {mmss(words[-1][2])}, {n} lines -> {W}/transcript.txt")
for sp, c in share.most_common():
    first = next(w for w in words if w[3] == sp)
    print(f"  {sp}: {c} words ({100 * c / len(words):.0f}%), first heard at {mmss(first[1])}")
if LOCAL:
    print("NOTE transcribed on this computer: there are NO speaker labels (everything is S0). Say so in the clip list, and "
          "work out who is speaking from what is said; check any line that matters by listening or by a still.")
else:
    print("Work out who each speaker is from what they say. One speaker only is normal for a solo video. "
          "More than one = a guest, an interviewer or a clip played on screen: flag every line that is not the creator's.")
