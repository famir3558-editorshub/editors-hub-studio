# The tight cut and the caption file (one clip at a time)

The scripts are in `scripts/cut/`. They work on ONE clip's `<id> - source.mov` (written by `03_clips.py --extract`),
under the clip's own slug: work dir `@@WORK_ROOT@@/<clip slug>`. The reordering was already done when the source was
cut, so nothing here ever reorders.

```bash
C=~/.claude/skills/<this skill>/scripts/cut
python3 $C/01_prep.py "<out>/<id>/<id> - source.mov" <clip slug> "<out>/<id>"
python3 $C/02_transcribe.py <clip slug>
python3 $C/03_cut.py <clip slug> [--gap 0.12] [--pad-out 0.035] [--pad-in 0.025]
python3 $C/04_verify.py <clip slug>
python3 $C/05_render_cut.py <clip slug>
python3 $C/06_captions.py <clip slug>          # run twice: draft, then time
python3 $C/cut_times.py <clip slug>
python3 $C/frames.py <clip slug> <t> [<t> ...]  # gridded stills, when a position has to be read by hand
```

Python needs `numpy`, `soundfile`, `requests` (ElevenLabs only) and `Pillow` (`frames.py` only).

## 1. Prepare

`01_prep.py` probes the file, writes the analysis audio and records where outputs go. Pass the clip's own folder as
the third argument so the cut is written beside its source. Act on its warnings (variable frame rate, HDR).

## 2. Transcribe, then check it against the audio

`02_transcribe.py` uses the transcriber chosen at setup (`scripts/stt.py`). Read the whole printed script and
`words.txt` (one numbered word per line).

The transcript is checked against the audio twice: `04_verify.py` transcribes the *edited* audio again and compares
it word for word with what the cut was meant to keep; and you read for sense: any word that looks wrong for the
subject (a name, a brand, a number) is confirmed from context or asked about, then fixed in the captions with
`{heard|Shown}`.

With local transcription the word edges are looser and two passes can disagree on small words: read every MISSING /
EXTRA / CHANGED line, and listen to `edit.wav` at any join you are unsure of before rendering.

## 3. The decision file: `drops.json`

Write `@@WORK_ROOT@@/<clip slug>/drops.json`:

```json
{"words": [[i, j], ...], "secs": [[a, b], ...]}
```

`words` are inclusive word-index ranges from `words.txt`; `secs` are raw-second ranges for things that are not
words. Start by pasting the `secs` list from `<id> - source.json` (the small bits removed inside the clip that are
still in the file), then add anything else.

Remove:
- **False starts and repeated takes**: when a line is said more than once, keep the LAST complete take and drop
  every earlier attempt in full, including the half-sentence that led into it.
- **Mistakes**: stumbles, a wrong word followed by the right one, "um / uh", restarts, throat clears, asides.
- **Lines that are not the main speaker's**, when the skill's rules say they go (hard to hear, not cleared).
- **Dead space** is removed by the script itself (pauses, breaths, the head and the tail). Never list it.

Keep:
- **The meaning.** Every sentence must still be a sentence and the argument must still follow. If unsure whether a
  repeat is a mistake or emphasis, keep it. Never splice words into a sentence that was not said.
- **Natural pacing.** The default gap between words is 0.12 s. If the result feels breathless, `--gap 0.2`. A pause
  clearly left for effect before a punchline stays (raise `--gap`, or accept one PAUSE line in the verify).

## 4. Cut and verify

`03_cut.py` then `04_verify.py`. Read the EDIT as a script and every MISSING / EXTRA / CHANGED / PAUSE / REPEAT
line; fix `drops.json` and repeat until it is clean. **The clip starts on the first spoken word and ends right after
the last**: head and tail under about 0.25 s. If the last word sounds clipped, re-run with `--pad-out 0.06` (or
more) until its sound has died away. The verified cut must read exactly as the script in the clip's prompt.

Then `05_render_cut.py` (background for long or 4K sources): frame-accurate, 8 ms audio fades at every join,
written as `"<out>/<id>/<id> - source - CUT.mp4"` at the source resolution.

From here on every time is **cut-timeline seconds**: `edit.txt` (the script plus every word's time), `cuts.json`
(every join), and `cut_times.py` (the joins with the words either side; `BIG` = a jump a viewer sees).

A join listed in `<id> - source.json` (minutes of the recording removed between two pieces) is always a big jump,
even when the tight cut lists it as small or does not list it at all because no silence was trimmed there. Work out
its cut-timeline time from the words either side of it in `edit.txt` and put a shot change on it.

## 5. Captions

`06_captions.py <clip slug>` drafts `phrases.txt` from the verified cut and stops. Edit it, then run again:

- one caption per line, every spoken word, in order (the script refuses anything else);
- regroup freely by moving line breaks (1-3 words; never split a name or a number from its unit);
- `*word*` marks emphasis: that word is set in the emphasis font and the accent colour inside the normal caption
  line (a figure stays in the caption font and takes the accent colour);
- `{heard|Shown}` fixes a mis-heard or mis-spelled word on screen; capitals and punctuation can be changed directly.

It writes `captions.json` (`[{start, end, parts: [{t, em}]}]`) and `captions.txt`. Read `captions.txt` in full and
clear every LONG / SHORT line. The style rules are in `style.md` section 1.

To show a line in the paler "someone else is speaking" colour, add `"other": true` to that caption in the project's
`captions.json` after the project is made.

## 6. Hand over to the build

The project script (`06_new_project.py` or `06_project.py`, in `scripts/`) copies `captions.json`, `cuts.json` and
`cut_words.json` into the HyperFrames project, links the cut as `assets/cam.mp4` and finds the face. After changing
captions, run it again: it refreshes those files and never touches `build.py`.
