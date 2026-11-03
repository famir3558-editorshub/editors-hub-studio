---
name: split-screen-document-plus-animations
description: Split Screen Document Plus Animations - edit a long-form YouTube lesson recorded with a camera plus a notes document on a tablet or screen (usually in Tella) into a document-left, creator-right video. Does the whole job - pulls the raw camera and screen tracks, builds the split screen (document on the left, the creator on the right, full screen whenever they look up at the camera to make a point, app chrome cropped off the document), makes the dialogue cut (flubs, false starts, silences), then adds illustration-style animations ONLY in the full-screen sections (platform interfaces, notifications, playlists, dashboards, real channel cards and client proof, never the creator's words restated as text), renders at 1080p, frame-checks every layout switch, and fixes quiet audio when the creator approves it. Use whenever the creator says "split screen document plus animations", "document on the left, me on the right", "edit the Tella video", "do this one like the last lesson", "I recorded a YouTube video with the document", or hands over a camera file plus a tablet / notes screen recording for a long YouTube video. Also for one part alone - only the split screen, only the cut, only the graphics pass, only the audio fix, a re-render after notes. Not for videos without a document on screen (educational-youtube-editor), 9:16 reels, coaching-call clips, or building the notes document itself (lesson-doc-builder).
---

# Split Screen Document Plus Animations

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/split-screen-document-plus-animations/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first. Do not start the task, and do
  not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if it exists,
  `~/.claude/creator-profile/notes/split-screen-document-plus-animations.md`. Rules under `## Style overrides` in that
  notes file win over the defaults written below.

"redo my setup" re-runs the interview at any time.

This skill is built on top of `educational-youtube-editor` (its cut, render and review scripts and its engine are used
as they are). That skill must be installed and set up as well: `python3 ~/.claude/skills/educational-youtube-editor/setup/apply_profile.py --status`.
If it says `"configured": false`, set it up first (or run `creator-setup`), because its scripts hold the creator's folders and cut settings.

## Your setup

Filled in by setup. To change a line, change the answer (`setup/SETUP.md`), never this text.

| | |
|---|---|
| Creator | @@CREATOR_NAME@@ · @@BRAND_NAME@@ · @@HANDLE@@ |
| What they teach, and to whom | @@NICHE@@ |
| Colours | accent @@ACCENT@@ (@@ACCENT_NAME@@) · background @@BG@@ · text @@PAPER@@ · small labels @@GREY@@ |
| Fonts | main: @@FONT_MAIN_NAME@@ · emphasis: @@FONT_ACCENT_NAME@@ |
| Recorder | @@RECORDER@@ |
| Document page colour | @@DOC_PAGE_COLOR@@ |
| Shortest full-screen moment | @@MIN_FULL_SECONDS@@ s |
| Transcriber | @@TRANSCRIBER@@ |
| Raw lesson recordings live in | @@RAW_DIR@@ |
| Footage drive | @@MEDIA_DRIVE@@ |
| Finished videos go | @@OUTPUT_RULE@@ |
| Folders | working files `@@WORK_ROOT@@` · HyperFrames projects `@@PROJECTS_ROOT@@` |
| Real material (proof) | @@PROOF_DIR@@ |
| Other folders to search for real assets | @@ASSET_DIRS@@ |
| Real assets from the web | @@WEB_ASSETS@@ |
| Never show | @@NEVER_SHOW@@ |
| Sound effects | @@SFX_DIR@@ · copy without sound effects: @@NO_SFX_COPY@@ |
| Quiet recordings | @@QUIET_AUDIO_FIX@@ · target @@VOICE_TARGET_LUFS@@ LUFS · de-noise @@VOICE_DENOISE_DB@@ dB |
| Punch-in strength | @@PUNCH_PERCENT@@% |
| Depth and 3D in graphics | @@DEPTH_3D@@ |
| How far to go alone | @@WORK_RULE@@ |

## What this skill is for

A lesson format: the creator teaches from a notes document on a tablet or screen, recorded as a camera track plus a
screen track. The finished video is the **document on the left and the creator on the right** for most of the running
time, cutting to **the creator full screen** when they look up to make a point. It is in those full-screen moments, and
only there, that the animations go. The document sections are the visual and are left exactly alone.

The notes document itself is built by `lesson-doc-builder`. Long-form talking-head work that has no document on
screen belongs to `educational-youtube-editor`. Read that skill's `references/dialogue-edit.md` before cutting and
`references/asset-retrieval.md` before hunting assets.

## The rules of this format

1. **The split:** document on the left, creator on the right. Crop everything that is not the document: app tabs, toolbar, floating pen palette, undo button, page borders.
2. **Full screen whenever the creator is looking at the camera and making the point.** Split whenever they are going through the document, which is most of the video.
3. **Graphics only in the full-screen sections.** The document sections are left exactly alone: the document is the visual.
4. **Illustrate, do not repeat.** Every graphic is a thing: an interface, an object, a diagram, a real asset (an Instagram profile whose bio is being described, a channel card, a notification landing). Words appear only as labels inside that thing. A card that is just the creator's sentence as text is the one thing this format does not do. If nothing illustrates a line, use a punch-in or leave the creator alone. See `references/illustration-patterns.md`.
5. **Dialogue cut on the whole video:** silences, flubs, false starts, repeated takes, housekeeping asides ("where is my highlighter"). Banter and the creator's natural voice stay; they are the personality.
6. **1080p, no music** by default. Quiet sound effects on the graphics, well under the voice, plus a copy with no sound effects when setup says so.
7. **Edit from the camera-switched file**, not the raw tracks: the split-screen base is made first and everything else is done on top of it.
8. **No early reveal:** a "N rules" preview shows N hidden cards, never the rules.

### Preview first

Do not render the full-quality final first. Render a fast 720p preview (a 720p proxy of the source), give the creator the
file path, and wait for approval and timestamped notes before the final. Apply the notes, re-preview, then render the final
once approved. For a batch of lessons, gate the first video and apply its notes to the rest.

## How to work with the creator

How far to go without asking is a setup answer: see "How far to go alone" in **Your setup**.

- **`show the plan as a short table, then run to the end and report` (the pack default).** Show the plan for the graphics as a short table (time, what the creator says, what is shown) and carry on building. At the end, list what was cut and why, what is real and what is mocked, invented figures, and slips left in.
- **`stop and ask at each stage`.** Stop and wait for a yes after the split-screen base (a frame of each layout), after the dialogue cut, after the graphics plan, and after the preview.
- **Two things are always asked:** anything the creator drags in as a screenshot or file (where it goes), and the quiet-audio fix (see step 9).
- **Real over drawn.** A named channel, client or person is shown with the real avatar, plaque or testimonial. Nothing on the "Never show" line ever appears.
- Anything the creator says while working ("never do X", "always Y") goes into `~/.claude/creator-profile/notes/split-screen-document-plus-animations.md` under `## Style overrides`, dated, the moment they say it.

## Who does what

Delegate work that is mechanical or that a script or your own eyes check afterwards. Anything that decides what the viewer sees or hears stays with the main session.

| Work | Who |
|---|---|
| Transcript, first-pass `drops.json` with a reason on every entry, the cut/verify loop | A subagent |
| Reading the cut as a script for meaning; every editorial cut (duplicate takes, asides) | Main session |
| Asset hunt from an exact shot list (the creator's folders first, then the web, if allowed) | A subagent; you open every image before using it |
| The plan, every graphic, the intro | Main session (nearly every graphic is custom) |
| Frame check, review sheets | Scripts; you read the results |

Brief each subagent with the file paths, the references to read, what to leave for you to decide, and what to report. Tell the cut agent to stop before `05_render_cut.py`.

## Workflow

`S=~/.claude/skills/split-screen-document-plus-animations/scripts` · `ED=~/.claude/skills/educational-youtube-editor/scripts` · work `@@WORK_ROOT@@/<slug>` · project `@@PROJECTS_ROOT@@/<slug>-yt` · finished videos: the output folder (`@@OUTPUT_RULE@@`). Run long steps with the Bash tool's background mode. One render at a time when writing to an external drive.

### 1. Get the raw tracks and organise them
- With Tella (the supported recorder): the Tella connector's `list_videos` (newest first), `list_clips`, then `list_sources` gives two signed HLS URLs per video, a camera track (`CameraMic`, 3840x2160, the creator's mic) and a `Screen` track (the document, portrait or landscape). `"$S/tella_dl.sh" "<url>" "<out.mp4>"` for each.
- Any other recorder: you need two files of the same length and already in sync, a 4K camera file and a screen recording. Name them `camera.mp4` and `screen.mp4` in one folder.
- Keep each lesson in its own folder, `<raw folder>/Raw/{camera.mp4,screen.mp4}`, with working files and versions beside it in `Edit/`. If "Raw lesson recordings live in" in **Your setup** names a folder, look there first.
- Titles may contain apostrophes ("You're"): always pass paths as double-quoted arguments, never inside `sh -c '...'`.

### 2. Check the audio level now
`python3 $S/louder.py --measure "<Raw>/camera.mp4"`. A dynamic microphone into a screen recorder often comes in at about -37 LUFS, far too quiet. The fix (step 9) is only for quiet recordings. What happens next follows the setup answer (`@@QUIET_AUDIO_FIX@@`):

- `ask` (default): tell the creator the number and, if it is borderline or you are unsure, cut a 40-second sample both ways before deciding. A recording already near -20 LUFS or louder is left alone.
- `auto`: apply the fix when the measurement says quiet, and report the before and after numbers.
- `never`: leave the audio exactly as recorded and say in the report that it measured quiet.

### 3. The split-screen base
`python3 $S/01_split.py "<Raw folder>" <slug> "<Edit>/<Title> - Split Screen Edit v1.mp4"` (add `--plan-only` first to see the section list). It tracks the creator's gaze, finds the document inside the screen recording, decides the sections, and renders the 4K base in chunks.
- **Look at a frame of each layout** before the full render: document flush left with no app chrome, the creator framed on the right. If app chrome is still in the document, pass `--crop W:H:X:Y` (or edit `<work>/<slug>/split/crop.txt`).
- Expect roughly 25 to 40% full screen. If the switching feels busy, `--min-full 7`.
- If a creator who plainly looks to camera is never detected, lower `--pupil` and `--eye-open` a little; if too much goes full screen, raise them. `--force-full a-b` forces a stretch to full screen (the opening hook is always full screen: check the first section).
- The document's page colour is read from the recording (or set at setup) and fills the margin of a landscape document.

### 4. The dialogue cut
Educational editor scripts on the **base file**: `$ED/01_prep.py "<base>" <slug> "<Edit folder>"`, `$ED/02_transcribe.py`, `drops.json`, `$ED/03_cut.py`, `$ED/04_verify.py` (a subagent), then you read `edit.txt` end to end, make the editorial calls, re-verify, and `$ED/05_render_cut.py`.
- One cut removes the same moments from the creator and the document, because the base already contains both.
- Things that come up on lesson recordings: several abandoned takes of the intro, a point announced twice with a long gap between (keep the clean take), highlighter / laser asides, a blooper after the last line, 15 to 30 s dead gaps.
- Flag, do not fix, slips that cannot be cut cleanly (a wrong word, a mid-sentence self-correction). Tell the creator.
- Set `meta.json`'s `stem` to the clean title so outputs are not named "... Split Screen Edit v1 - YouTube Edit".

### 5. The graphics project
`python3 $S/02_project.py <slug> "<Title>"`. It scaffolds the project through the educational editor's `06_new_project.py`, installs this skill's engine (the document guard) and `doc_kit.py`, sets the creator's face position from the gaze data, maps the full-screen windows through the cut, and **measures every layout switch from the base video itself** (the prediction is a frame out about half the time). It needs the base video's document page to be light: switch detection reads the left 40% of the frame as a white page.

### 6. Plan, then build
- Print what the creator says inside each full-screen window (from `cut_words.json` and `windows.json`). Plan one illustration per window that deserves one; windows under about 6 s usually get nothing.
- Show the plan as a short table (time, what the creator says, what is shown) and carry on (or stop, if the setup answer says so).
- Write `build.py` with the engine (E), the kit (K) and `doc_kit` (D). `a, b = D.win(t)` gives the window a time sits in; time everything from the words with `E.w("exact words", a)`. `examples/lesson-build/build.py` is a structure reference.
- The engine **refuses** any scene that overlaps a document section, and a split or panel that touches one must be `cut=True`. Camera drift and punch-ins reset on the exact frame the layout switches.
- Splits inside a full-screen window put the graphic on the **left** and the creator on the **right**, so they never jump sides against the document layout.
- Snapshot every scene (`$ED/snap.py <slug> --all`) and read the sheets. Fix anything too small to read: interface text needs to be about 28 px or more at 1080p.
- What to show for what is being described, and the kit's pieces: `references/illustration-patterns.md`.

Figures inside illustrations are invented for the picture; real people and channels get real numbers. Report which is which.

### 7. Render and frame-check
`python3 $ED/08_render.py <slug> --tag v2` (preview first, see above), then, from the project folder:
`python3 $S/check_doc_frames.py "<final.mp4>" <project>/assets/cam.mp4`.
- It compares the final with the base on the first and last two frames of every document section and every 2.5 s inside. **Zero mismatches is the bar.** A mismatch near 100 is a one-frame flash of the wrong layout; one near 15 is a document section left zoomed.
- The final's video frame count must equal the cut's. One extra means a chunk gained a frame.
- Then `$ED/09_review.py` and read the intro strip, the scene sheets and the joins.

### 8. Deliver
- Say plainly what you checked (frames, sheets) and what you did not (watching end to end, listening).
- List: what was cut and why, what is real and what is mocked, invented figures, slips left in.
- Finished files go to the output folder (`@@OUTPUT_RULE@@`) as `<Title>.mp4` and, when setup says so, `<Title> (no SFX).mp4`. If copies are already there, replace them when the edit changes.

### 9. The quiet-audio fix (only when needed, and per the setup answer)
`python3 $S/louder.py "<Edit folder>" "<Title>" <project folder>`
The default recipe, chosen by ear from nine variants:
- the voice is raised to about **-19.8 LUFS** (the setup answer sets the target), with a **light de-noise** (6 dB by default) for the hiss the boost brings up, and a **limiter at -6 dB**;
- **nothing else**: no EQ, compressor, de-esser or expander. A full chain was compared against the creator's untouched voice and the untouched voice was preferred. Stronger de-noise and a louder, harder-limited version are available with `--denoise` and `--target` if the creator asks;
- sound effects are mixed back at their original level, never through the gain or limiter. After the fix they sit about 30 dB under the voice, which is the designed level.
On a stereo meter each channel peaks near -8 dB (a mono voice at -5 spread over two channels). It rewrites the final and the "(no SFX)" copy in place; the untouched voice stays in `renders/voice-raw.wav` so it can be redone.
The real fix is at the source: more mic gain in the recorder, peaking around -12 to -6 dB.

## Gotchas (each one cost a render)

- **Chunk length.** A chunk whose length rounds a hair over a whole number of frames gains a frame and everything after it slips. The engine sets a whole number of frames, a hair under.
- **First frame of later chunks.** A 4-decimal media start can land just before the frame and show the previous one. The engine adds a third of a frame.
- **Lazy tweens.** With GSAP's default lazy rendering, a page that first renders mid-video applies a queued tween after a later zero-length set, leaving a document section zoomed for seconds. The engine sets `lazy:false`. This is why the frame check samples inside sections, not only at their edges.
- **Drift into a document section.** The slow zoom must end before the reset; the engine ends it 0.1 s early at a document edge. A move already under way when a chunk starts runs only its remaining time.
- **Snapshots do not reproduce render-order bugs.** Only the frame check on the rendered file does.
- **Layout switches are measured, not calculated** (`snap_windows.py`).
- **The audit's density warnings** ("long stretches with nothing", "only N scenes in the intro") count the document sections as empty. Expected here; ignore those lines, act on the others.
- **Do not delete with a relative glob after `cd`**: a safety check can block it. Leave temp files or name them absolutely.
- Some ffmpeg builds have no `drawtext`. zsh does not word-split `$VAR`.
- **The base step is built for a 3840x2160 camera at about 29.97 fps** and for macOS (Apple Vision face landmarks, VideoToolbox encoding). On another size it stops and tells you; do not force it.
- Detection thresholds (pupil height, eye openness) and the document crop are tuned on one setup. Always look at a frame of each layout and at the section list before the full render.

## What is in the box

- `scripts/tella_dl.sh` raw download · `01_split.py` the split-screen base · `gaze.swift` (compiled on first use) · `windows.py` + `snap_windows.py` full-screen windows on the cut timeline · `02_project.py` project setup · `check_doc_frames.py` the frame check · `louder.py` audio measure and fix.
- `engine/yt_engine.py` the educational editor's engine plus the document guard and the render fixes above · `engine/doc_kit.py` the interface pieces (`views_card`, `ig_card`, `chan`, `vrow`, `note`, `playlist`, icons, `win`).
- `references/illustration-patterns.md` what to show for what is being described, the kit API and the readability rules.
- `examples/lesson-build/build.py` a structure reference: a hook, a preview of hidden cards, a climbing number, a channel card, a search choice, a step chain, notifications, an in-window split, a playlist and a punch-in. Never reuse its wording.
- `setup/` the first-run interview and the script that fills in the answers.

## Status

- The split-screen base, the dialogue cut and the graphics pass were refined on real lesson recordings; the steps were then packaged as scripts.
- `01_split.py`'s section planning reproduced a hand-built edit's sections; its render path and `02_project.py` have not been run end to end on a new creator's footage yet. Check their output on the first real use, and treat the landscape crop and the gaze thresholds as things to verify, not trust.
- Defaults still unconfirmed with the creator: the shortest full-screen section (5 s), and leaving the sound effects at the designed level after the audio fix.

## Related

`educational-youtube-editor` (cut scripts, kit, render, review; the long-form rules) · `lesson-doc-builder` (builds the notes document that is scrolled on screen).
