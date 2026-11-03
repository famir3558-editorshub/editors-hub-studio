---
name: personal-broll-library
description: A personal B-roll library and editing assistant for a creator's own footage. Use when the creator wants to index or organise their own B-roll footage folder, add new footage to the library, search their footage ("find b-roll of me working", "do I have clips of me on my phone", "b-roll for procrastination"), match their own B-roll to a script, transcript, voiceover or video they are editing, or add personal B-roll to an edit in Premiere Pro, DaVinci Resolve, Final Cut or CapCut. Also use for "set up my b-roll library" and "redo my setup". Not for sourcing stock, meme or internet footage.
---

# Personal B-Roll Library

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/personal-broll-library/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first. Do not start the task, and do
  not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if it exists,
  `~/.claude/creator-profile/notes/personal-broll-library.md`. Rules under `## Style overrides` in that notes file
  win over the defaults written below.

"redo my setup" re-runs the interview at any time.

## Your setup

Filled in by the setup interview. If a line still shows a placeholder in double at-signs, setup has not finished.

| | |
|---|---|
| Creator | @@CREATOR_NAME@@ (the person in the footage unless clearly someone else) |
| What they do | @@NICHE@@ |
| Footage folder (first folder to scan) | `@@FOOTAGE_DIR@@` |
| Footage is stored on | @@FOOTAGE_DRIVE@@ |
| Library index | `@@LIBRARY_DIR@@` |
| Editing app | @@EDITING_APP@@ |
| Sequence frame rate | @@SEQUENCE_FPS@@ |
| Sequence shape | @@SEQUENCE_FORMAT@@ |
| The footage mostly shows | @@FOOTAGE_SHOWS@@ |
| Their videos are about | @@VIDEO_TOPICS@@ |
| Never use or show | @@NEVER_SHOW@@ |

## What this is

A semantic database of the creator's own footage: what each clip shows, what ideas it can stand
for, which seconds are usable, and when to use it in an edit. Footage is analysed **once**;
afterwards every search, script match and export reuses the stored metadata.

Everything runs through one CLI, `scripts/broll.py` (Python 3.9+, ffmpeg/ffprobe; Pillow optional).
All commands print JSON. Below, `broll` means:

```bash
python3 ~/.claude/skills/personal-broll-library/scripts/broll.py     # add --library <path> to override
```

The library (SQLite index, contact sheets, plans, exports) lives in `@@LIBRARY_DIR@@`. The CLI reads
that folder from the setup answer `library_dir` (or `$BROLL_LIBRARY`, or `~/BrollLibrary` when neither
is set). It sits on the internal disk on purpose: search and planning work even when the footage drive
is unplugged. Only frame extraction and importing into the editing app need the drive connected.

## Rules that never bend

1. **Never modify the footage.** No moving, renaming, deleting, transcoding, compressing or
   overwriting source media unless the creator explicitly asks in this conversation. The CLI only reads
   media; keep it that way with any ad-hoc command you run (no `mv`, `rm`, `ffmpeg -y` onto a
   source path).
2. **Look before you describe.** Never tag a clip from its filename. Every analysis is based on
   the contact sheets (and audio profile) of that clip.
3. **Reuse the index.** Never re-analyse a clip whose status is `analyzed` unless the file changed,
   the creator asks, or `status` reports `outdated_analysis`.
4. **Never pretend editing-app work happened.** Nothing touches Premiere Pro (or any other editing
   app) unless a working integration actually ran. Exports are files the creator imports or runs
   themselves; say so plainly.
5. **Non-destructive in the editing app.** The XML imports as a new sequence; the JSX script clones the
   sequence first. Never write anything that edits their existing sequence or project file.
6. **Respect the never-use list.** Anything matching "Never use or show" in the setup table above
   (people, places, private screens) is recorded in the clip's `issues` and `avoid_for` when it is
   analysed, is never offered in search answers without that warning, and is never put into a plan.
7. Never call a section of a script or video a "beat". Say part, section, moment or line.

## Workflow A: index or update a footage folder

When the creator does not name a folder, use the footage folder from the setup table
(`@@FOOTAGE_DIR@@`). If it is on an external drive and the folder is not there, ask them to plug the
drive in; do not scan somewhere else instead.

1. `broll scan "<folder>"` - walks the folder (sub-folders included) and classifies every video:
   - `new` - needs analysis
   - `changed` - same path, different content (re-recorded/overwritten) - needs re-analysis
   - `moved` - renamed or moved, recognised by content hash; analysis kept, nothing to do
   - `duplicate` - identical copy of an existing clip; linked, never analysed twice, hidden from search
   - `missing` - no longer found; kept in the index and restored automatically if it reappears
   - `unsupported` - BRAW/R3D etc. that ffmpeg cannot decode; ask the creator for a proxy/H.264 export
   Unchanged files are skipped by size+mtime without hashing, so rescans of big folders are fast.
2. `broll extract --pending --limit 10` - for each pending clip: grabs 6-24 frames spread across
   the whole clip, builds labelled contact sheets (timestamps burned in), reads loudness/activity,
   and writes an analysis template to `<library>/pending/<clip_id>.json`.
3. For each clip: **Read every sheet image**, then fill its template following
   `references/analysis-guide.md` (read that guide before the first clip of a session). Pay most
   attention to `segments` and `best_section`: they decide which seconds get used in edits.
4. `broll ingest --dir <library>/pending` - validates and stores. Fix anything listed under
   `failed` and ingest again. Unfilled templates are skipped, not stored.
5. Repeat 2-4 until `pending_remaining` is 0. Report: how many clips were added, moved,
   duplicated, missing, and anything unsupported.

Large backlogs (50+ clips): process in batches of 10, and use the Agent tool to analyse batches in
parallel, giving each subagent the clip ids, the sheet paths, the template paths,
`references/analysis-guide.md` and the never-use list. You run `ingest` yourself afterwards and
spot-check a few.

If the drive moved (new mount point or folder renamed): `broll roots` then
`broll relink --from "<old>" --to "<new>"`. No re-analysis needed.

## Workflow B: search the library

For "find b-roll of me working", "do I have footage of my phone", "something for making money
online":

1. Translate the request into **what would literally be on screen**. "Making money online" ->
   laptop, phone notification, payment, typing, dashboard. "Procrastination" -> phone scrolling,
   lying on the couch, staring, TV. Use what you know about their footage and topics from the setup
   table to choose terms that are likely to exist in this library.
2. `broll search "<request>" --expand "term,term,term"` (add `--orientation vertical` for vertical
   videos, `--min-quality 3` when quality matters, `--fresh` to down-rank clips they use a lot).
   The library's `concepts.json` adds standard expansions automatically, including any niche concepts
   added at setup. When a topic of theirs keeps needing the same hand-written `--expand`, offer to
   add it to `<library>/concepts.json` so it happens automatically.
3. The CLI is keyword-ranked. **You** are the semantic layer: read each candidate's description,
   uses and avoid list and rerank by meaning. Drop clips that only match a tag technically.
4. If there are few or weak hits, try a second search with different visual terms. For a library
   under ~300 clips you may run `broll dump` and judge every clip directly.
5. Answer with the best 3-6 clips: filename, best section (e.g. 3.0-9.0s), one line on why it fits,
   and quality. If nothing fits, say so and say what to film.

## Workflow C: match B-roll to a script, transcript or video

1. Get timed text:
   - SRT/VTT/Whisper/ElevenLabs/Deepgram JSON/CSV -> `broll transcript <file> --group 6 -o seg.json`
   - A video they are editing -> the quickest route is captions exported from the editing app as SRT
     (Premiere Pro: Text panel > Captions > Export to SRT file; DaVinci Resolve: Timeline > Create
     Subtitles from Audio, then export the subtitle track as SRT; CapCut and Final Cut: export the
     auto captions as SRT). Or transcribe it here:
     `python3 ~/.claude/skills/personal-broll-library/scripts/stt.py "<video>" words.json`, then
     `broll transcript words.json --group 6 -o seg.json`. That uses the transcription choice saved in
     the profile (`transcriber`: ElevenLabs is the accurate paid option, `local` is free and runs on
     this computer). If that choice was skipped at setup, run section A5 of `setup/SHARED-SETUP.md`
     now, before transcribing. Never ask for an API key in chat.
   - A plain script -> `broll transcript script.txt` gives estimated times (flagged). Fine for
     planning; get the real SRT before exporting to the editing app.
2. Read `references/matching-guide.md`, then go through the segments and pick the moments where
   personal B-roll genuinely strengthens the point. Not every line needs it.
3. For each moment run a search (Workflow B) and choose the strongest clip and section. Pass the ids
   you have already used with `--exclude` so the video does not repeat itself.
4. Write the plan JSON to `<library>/plans/<project>.json` (format in `references/schema.md`),
   including `gaps` for moments that need B-roll they do not have yet.
5. `broll plan-check <plan>` - fix every error; review the warnings (setup moments, reused
   frames, overlong cuts, no shot variety).
6. Present the plan as a table: time, what is said, clip + section, length, why. Then list the gaps.

## Workflow D: put it into the edit

The creator finishes in: **@@EDITING_APP@@**. Usual sequence: @@SEQUENCE_FPS@@ fps, @@SEQUENCE_FORMAT@@.

`broll export <plan> --to all` writes three files to `<library>/exports/`. Always pass
`--fps/--width/--height` matching the real sequence: 1920x1080 for horizontal, 1080x1920 for
vertical. If the frame rate in the setup table is "match the main video", or you are unsure, read it
from the main video with `ffprobe` rather than assuming. If the creator works in both shapes, ask
which one this edit is.

What gets written:

- **`.xml`** - an FCP7 XML timeline (xmeml). It arrives as a *new* sequence: main video on V1/A1
  (when the plan has `main_video`), B-roll on V2 trimmed to the chosen sections with **no B-roll
  audio**, a marker on every placement and on every gap. Existing sequences are untouched; the
  creator copies V2 into the real edit or carries on in the new sequence.
- **`.jsx`** - Premiere Pro only, experimental. ExtendScript that clones the active sequence, imports
  the clips into a "Personal B-roll (auto)" bin, makes video-only subclips and overwrites them onto V2
  of the clone. It must be run by the creator inside Premiere (e.g. VS Code ExtendScript Debugger).
  It has not been tested against their Premiere version; say so, and check `references/premiere.md`.
- **`.csv`** - human-readable placement sheet (timeline in/out, clip, source in/out, what is said,
  why, file path). Works with every editing app.

Which file to hand over depends on the editing app. Be honest about what each one can do:

| Editing app | What to send | What to tell them |
|---|---|---|
| **Premiere Pro** | `.xml` (recommended, reliable). `.jsx` only if they ask for it. | File > Import the `.xml`. A new sequence appears; copy V2 into the real edit. |
| **DaVinci Resolve** | `.xml` plus the `.csv` as a backstop | File > Import > Timeline, choose the `.xml`. Resolve reads FCP7 XML, but this skill's file was built and checked against Premiere, so treat the first import as a test: check the clips sit at the right times and relink media if Resolve asks. Markers may not all come across. |
| **Final Cut Pro** | `.csv`, and the `.xml` only if they have a converter | Final Cut Pro reads its own FCPXML format, not FCP7 XML, so the `.xml` will not import directly. Two routes: convert it (a converter app such as SendToX, or import it into the free DaVinci Resolve and export an FCPXML from there), or place the clips by hand from the `.csv`. Say which route you are suggesting and that the conversion is untested here. |
| **CapCut** | `.csv` only | CapCut cannot import an XML timeline. The `.csv` lists each clip, the exact section to use and where it goes; they place the clips by hand. Offer to read the list out in order as they work. |
| **None / something else** | `.csv` | Same as CapCut, or offer the `.xml` if their app lists "Final Cut Pro 7 XML" among its import formats. |

Send the files. Tell them exactly what to import and where to click. Never say B-roll "has been
added" to their timeline. If an automation tool for their editing app becomes available in a session
(for Premiere, see `references/premiere.md`), drive it from the same plan JSON and follow the
non-destructive steps there.

After they confirm they used a plan: `broll used <plan>` so future searches with `--fresh` avoid
overusing the same clips across videos.

## Other commands

`broll status` (counts, roots online/offline, pending), `broll show <id>` (full record + usage
history), `broll backup` (whole library to one JSON), `broll init`.

## References

- `references/analysis-guide.md` - how to watch a clip and fill every field, with examples
- `references/matching-guide.md` - selection rules for scripts and edits
- `references/schema.md` - analysis record, plan format, database layout, status lifecycle
- `references/premiere.md` - importing into Premiere Pro and other editing apps, the JSX script, and the automation roadmap
- `setup/SETUP.md` - the first-run questions; `setup/SHARED-SETUP.md` - the questions shared by every skill in the pack
