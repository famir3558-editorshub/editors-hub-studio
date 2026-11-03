---
name: youtube-clips
description: Turn a full long-form YouTube video (the creator's own, 5-90+ minutes, 16:9, given as a local file or a YouTube link) into a small number of high-quality social clips. Does the whole front half of the job - finds the cleanest file or downloads the video if it is a link, transcribes all of it, reads all of it, finds and ranks the strongest standalone moments (insights, stories, analogies, frameworks, corrected misconceptions, strong opinions), tightens each into a 30-60 s story (up to ~90 s) with the strongest line actually said moved to the front as the hook, and writes TWO production-ready editing prompts per clip - a 16:9 horizontal edit (graphics beside the speaker, captions along the bottom) and a separately composed 9:16 vertical edit (full screen / split / full-screen animation) - then cuts each clip's source out of the video and builds the edits in HyperFrames with its own cut pipeline, engine and graphics kit. Use whenever the creator hands over a YouTube video, a YouTube link, a long-form episode, lesson, podcast-style solo video or VSL and says "clip this video", "YouTube clips", "find the clips", "pull the best moments", "turn this video into reels / shorts", "make shorts from this", "what's worth posting from this video", or asks for horizontal and vertical versions of an excerpt. Also for one part alone - only the clip list, only the prompts, re-ranking, or one more clip from a video already analysed. Not for coaching or client calls (coaching-call-clips), editing the long-form video itself, a single scripted short take (use a short-form reel skill), or carousels.
---

# YouTube clips

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/youtube-clips/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first. Do not start the task, and do
  not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if it exists,
  `~/.claude/creator-profile/notes/youtube-clips.md`. Rules under `## Style overrides` in that notes file win over
  the defaults written below.

"redo my setup" re-runs the interview at any time.

## Your setup

Filled in by setup. To change a line, change the answer (`setup/SETUP.md`), never this text.

| | |
|---|---|
| Creator | @@CREATOR_NAME@@ · @@BRAND_NAME@@ · @@HANDLE@@ |
| Channel | @@CHANNEL@@ |
| Colours | accent @@ACCENT@@ (@@ACCENT_NAME@@) · background @@BG@@ · text @@PAPER@@ · small labels @@GREY@@ |
| Fonts | main: @@FONT_MAIN_NAME@@ · emphasis: @@FONT_ACCENT_NAME@@ · captions: @@FONT_CAPTION_NAME@@ |
| Transcriber | @@TRANSCRIBER@@ |
| Folders | working files `@@WORK_ROOT@@` · HyperFrames projects `@@PROJECTS_ROOT@@` · real material (proof) `@@PROOF_DIR@@` |
| Raw recordings and clean cuts live in | @@RAW_DIR@@ |
| Published videos have captions / music burned in | @@PUBLISHED_LOOK@@ |
| Downloads go to | `@@DOWNLOADS_DIR@@` |
| Swearing | kept in the audio; captions: @@SWEAR_CAPTIONS@@ |
| How many clips | every clip that clears the bar, @@MAX_CLIPS@@ at most |
| After the prompts are written | @@BUILD_RULE@@ |
| Ratios | @@RATIOS@@ |
| Music and sound effects | @@CLIP_SOUND@@ |
| Pointing back to the full video | @@FULL_VIDEO_TAG@@ |
| Finished clips go to | @@FINALS_DIR@@ |
| Other people's videos | @@OTHER_CREATORS@@ |
| Never clip | @@NEVER_CLIP@@ |

## What this skill does

A full YouTube video goes in (a file, or a YouTube link). What comes out, in this order:

1. **A clip list**: the few moments worth publishing, ranked, each with its hook and why it earns a post.
2. **Editing prompts per clip**: one for a 16:9 horizontal edit, one for a 9:16 vertical edit (only the ratios in
   "Your setup"). Same words, two different compositions.
3. **A source file per clip**, cut out of the video with the hook already in place.
4. When the creator says go: the edits themselves, built here with this skill's cut pipeline, engine and graphics kit.

The skill owns the listening, the choosing, the story edit and the build. Everything it needs is inside this folder.

`S=~/.claude/skills/youtube-clips/scripts` · cut pipeline `C=$S/cut` · work dir `W=@@WORK_ROOT@@/<slug>` (small
files) · outputs `"<video folder>/<video name> - Clips/"`, one sub-folder per clip (called `<out>` below). Video
files are large: big files (downloads included) stay on the drive that holds the video. Long steps run in the
background, one render at a time (two renders writing to the same external drive at once can fail).

Requirements: macOS, Node 22+, ffmpeg, HyperFrames (`npx hyperframes`), `yt-dlp` for links
(`brew install yt-dlp`), Python 3 with `numpy`, `soundfile`, `requests` and `Pillow`. Face finding (`04_faces.py` +
`face_boxes.swift`) uses Apple's Vision framework and the Swift compiler that ships with the Xcode command line
tools, so the build half of this skill runs on a Mac only.

## The sources of truth (read before planning, every session)

| For | Read | Notes |
|---|---|---|
| **Captions** (font, weight, emphasis, timing, rhythm) | `references/style.md` section 1 | One caption style for both versions of every clip. |
| **Vertical layout** (the three modes, cut alignment, where captions sit, opening hook) | `references/style.md` section 2, then `references/layouts.md` | What to check for YouTube footage is in `layouts.md`. |
| **Graphics, motion, sound** | `references/style.md` sections 3-5 | A library to choose from, not a checklist. |
| **The tight cut and the caption file** | `references/cut.md` | The per-clip pipeline in `scripts/cut/`. |
| **Brand values** | "Your setup" above and `~/.claude/creator-profile/profile.json` | Colours and fonts are already filled into the engine. |
| **The creator's own rules** | `~/.claude/creator-profile/notes/youtube-clips.md` | `## Style overrides` there win over every default here. |

If the pack's `business-short-form-reels` skill is also installed, the vertical look (modes, hook, pills, glass,
motion) is shared with it. Its style notes file, `~/.claude/creator-profile/notes/business-short-form-reels.md`, is
where that look is kept in step: read it too, and when the creator changes a vertical rule there, apply it here. If
`coaching-call-clips` is installed, the two skills share one engine design and one style: keep them in step.

Two points are settled so they are not re-argued:

- Captions here are one line of one to three words in the caption font with the emphasis word in the emphasis font
  and the accent colour, in both ratios. Only their *placement* in the vertical follows the three-mode layout.
- Captions may be made a little larger when that reads better. Still one line, never stacked.

Do not combine every treatment in one clip. For each moment pick the single treatment that explains it best.

## What is different about a published video

- **The speaker is talking to the camera**, usually centred, one speaker. The clip should feel like the sharpest
  minute of a video the viewer now wants to watch in full. The real voice and the real pauses for thought stay.
- **The video was made to be watched from the start.** Lines lean on what came before ("like I said", "this second
  one", "as you can see here"). Standalone clarity is the gate that removes most candidates.
- **The picture may already be edited.** A published video can carry burned-in captions, graphics, B-roll, zooms, a
  screen layout (a face in a card beside a document, a tablet or a whiteboard) and music. See "Which file to work
  from" below.
- **Guests and played clips.** Rules about other voices are rules about guests, interviewers, clips played on
  screen and other people's material.
- **Graphics explain; they never decorate.** A clip with two graphics that land is better than one with ten.

## Which file to work from

Ask for, or find, the cleanest picture of the same recording, in this order:

1. **The raw or the clean cut** (no captions, no graphics, no music). Look before asking, and before downloading
   anything: the folder from setup (`@@RAW_DIR@@`), then next to any file the creator has given you. Best for
   everything.
2. **The finished export** from the creator's own drive. Fine when the stretch being clipped is plain talking head.
3. **A download of the published video** (a YouTube link): what the prep script fetches. Lower bitrate than the
   creator's own file; say so in the report.

Setup says the published videos carry burned-in captions or music: **@@PUBLISHED_LOOK@@**. Whatever it says, check
the contact sheets of this video. When the only picture has things burned in:

- Never put captions over burned-in captions, or a graphic over a burned-in graphic. Either choose a stretch where
  the picture is clean, cover that stretch with a full-screen graphic (`full` / `anim`), or tell the creator the
  clip needs the raw.
- A screen layout (the face in a card beside a document or a tablet) is a valid 16:9 picture as it stands. For the
  9:16, the face has to be cropped out of its card, which is small: check a still, and if it is too soft, the
  vertical is built as split / animation with the speaker in the lower half only, or it needs the raw.
- Music under the published video cannot be removed, and a join across it is audible. Keep each clip to one
  continuous stretch, or get the raw.
- Existing cuts and zooms in the published picture count as joins: note them from the contact sheet.

**Someone else's video** (not the channel in "Your setup": @@CHANNEL@@). The setup answer is
**@@OTHER_CREATORS@@**. Under the default (`ask each time`), stop and ask once before doing anything past the clip
list: whose words may be clipped and published is the creator's decision, and every rule below about the speaker's
words then applies to that speaker.

## 1. Prepare and transcribe the whole video

```bash
python3 $S/01_video_prep.py "<video file or YouTube URL>" <slug>     # download if a link, audio, meta, two contact sheets
python3 $S/02_video_transcribe.py <slug>                             # the whole video
```

For a link the script downloads with `yt-dlp` (best quality, to `@@DOWNLOADS_DIR@@`, or beside the output folder
when you pass one) and prints the title, channel, chapters and the "most replayed" points. Chapters help the map;
most-replayed is a hint about what viewers re-watched, not a ranking. Act on the warnings (variable frame rate,
under 1080p, HDR, downloads folder not available).

**Transcription uses the transcriber chosen at setup: `@@TRANSCRIBER@@`.** Every script goes through
`scripts/stt.py`, so nothing else needs changing when the answer changes.

- `elevenlabs` (recommended): the most accurate words and timings, and speaker labels, at roughly $0.22 per hour of
  audio. The key is read from the environment or the shell profile, never printed, and **never asked for in chat**.
  If it is missing the script says so: tell the creator to add the export line themselves (`setup/SHARED-SETUP.md`,
  section A5).
- `local`: runs on this computer through HyperFrames. Free and private, but **there are no speaker labels**: every
  word comes back as `S0`. For a solo video that costs nothing. When the video has a guest, an interviewer or
  played clips, say so plainly at the top of the clip list and work out who is speaking from what is said. Word
  edges are also a little looser, so read the tight cut's verify output closely.
- Never use the ElevenLabs connector's transcribe tool as a substitute (it costs far more for the same model), and
  do not swap in YouTube's auto-captions or another ready-made transcript even when one exists: their timings are
  not word-accurate, and every cut downstream depends on word timings.

Speaker labels: a solo video should come back as one speaker. More than one means a guest, an interviewer, or a clip
played on screen; a played clip is sometimes credited to the main speaker. Treat `S0/S1/...` as a hint and check any
segment that matters by listening or by a still.

Open both contact sheets. Note where the speaker sits, whether they are looking at the camera, where the empty space
is, and every change of picture during the video (B-roll, screen share, a layout, burned-in graphics or captions, a
second camera). That decides which file to work from and where graphics can go in step 5.

## 2. Read all of it, then map it

Read `W/transcript.txt` from the first line to the last (read it in pages until the end; do not sample, do not stop
when you have enough clips). The best moment is often deep in the video, and a line only makes sense as a hook once
you know what the video was about.

Before choosing anything, write yourself a short map: the promise made in the intro, the sections in order with
their times (use the chapters when there are any), each story, each framework or analogy, each example, and where
each one resolves. Mark the parts that are not content: the cold open that previews later lines, the "subscribe"
ask, sponsor reads, the outro. Give the creator the map in four or five lines at the top of the clip list so they
can see the whole video was covered.

## 3. Find, rank and choose

Read `references/selection-and-story.md` (what to look for, the scoring, the story edit, the hook rules).

In short: list every candidate, score each on the eight criteria, and keep **every clip that is strong enough to
post and can actually be cut cleanly**. No target and no minimum: three is a fine answer, so is seven.
**@@MAX_CLIPS@@ is the ceiling**; if more clear the bar, keep the strongest and name the rest under "next in line".
Do not trim a good clip to keep the list short, and do not pad it to look productive. Make a judgment: every clip on
the list is one you would publish, mapped out in `clips.json`, with its source cut and its prompts written. Say
plainly how many cleared the bar and how many were borderline.

Leave out anything on the creator's never-clip list (**@@NEVER_CLIP@@**).

## 4. Edit each clip as a story

For each chosen clip write an entry in `W/clips.json`:

```json
{"clips": [{"id": "01-price-is-a-story", "title": "Price Is a Story", "segments": [[4210, 4236], [3980, 4105], [4120, 4209]]}]}
```

Segments are inclusive word-index ranges from `transcript.txt` (`w1234`), in **play order**. Leave words out to
remove them; put a later segment first to open on it. Then:

```bash
python3 $S/03_clips.py <slug>          # every clip printed as a script with estimated timings and warnings
```

The opening segment may be used a second time later in the clip (a hook that is then heard again in its natural
place as the last line); nothing else may repeat. Prefer a few long segments to many short ones: every gap between
segments is a join someone has to hide.

Read each printed clip as if you had never seen the video. Fix and re-run until each one has a beginning, a
development and a payoff, runs 30-60 s (up to about 90 s only when the idea truly needs it), and every `!` line has
been dealt with. The estimate is within a few seconds of the final cut.

## 5. Write the clip list and the prompts

Read `references/layouts.md` (how each ratio is composed for this footage) and `references/prompt-format.md` (the
exact format). Look at a still from each clip's time range (`ffmpeg -ss <t> -i <video> -frames:v 1 still.jpg`) so
the framing notes describe the real picture, not a guess.

- `"<out>/Clip list.md"`: the video map, then the ranked clips.
- `"<out>/<id>/<id> - 16x9 prompt.md"` and `"<out>/<id>/<id> - 9x16 prompt.md"` for every clip (only the ratios in
  "Your setup": @@RATIOS@@).

For each graphic, find the real thing first: the website, post, profile, document or person the speaker names. If
the full video already showed it on screen, that is the first place to look (the project folder for that video, then
the proof folder `@@PROOF_DIR@@`, the creator's drives, then the web). Record in the prompt where each asset is, or
that it still has to be found. A graphic field left as "none: stay on the speaker" is a correct answer; do not fill
a field because the template has one.

Then show the creator the clip list in chat (short) and link the prompt files. What happens next is the setup answer
"after the prompts are written": **@@BUILD_RULE@@**.

- `ask`: stop here and ask the open questions in one go with `AskUserQuestion` (which clips to build, anything
  flagged, sound if the setup answer is "ask each time").
- `build`: carry on to steps 6 and 7 for every clip on the list, then report.

## 6. Cut each clip's source

```bash
python3 $S/03_clips.py <slug> --extract all      # or one id; background, one at a time
```

Writes `"<out>/<id>/<id> - source.mov"` (full resolution, audio untouched) and `<id> - source.json`: where each piece
came from, the time of every join, and `secs` ranges for the small removed bits that are still in the file. From here
the clip is an ordinary raw recording: the reordering is already done, so the tight cut never reorders anything.

## 7. Build

Both versions start the same way: the tight cut of `<id> - source.mov`, made with this skill's own pipeline.
`references/cut.md` has the rules for each step; in short:

```bash
SRC="<out>/<id>/<id> - source.mov"
python3 $C/01_prep.py "$SRC" <clip slug> "<out>/<id>"   # the clip's own slug and its own folder
python3 $C/02_transcribe.py <clip slug>                 # transcriber from setup
#   write @@WORK_ROOT@@/<clip slug>/drops.json: paste the "secs" from source.json, then add anything else to remove
python3 $C/03_cut.py <clip slug> && python3 $C/04_verify.py <clip slug>     # repeat until the verify is clean
python3 $C/05_render_cut.py <clip slug>                 # "<out>/<id>/<id> - source - CUT.mp4" (background)
python3 $C/06_captions.py <clip slug>                   # drafts phrases.txt; edit it; run again
python3 $C/cut_times.py <clip slug>                     # every join on the cut timeline, BIG ones marked
```

The verified cut must read exactly as the script in the prompt.

Then build the ratios from that one cut with this skill's engine (`engine/clip_engine.py`) and kit
(`engine/ytkit.py`). One HyperFrames project per clip:

```bash
python3 $S/06_project.py <clip slug> "<Title>"     # @@PROJECTS_ROOT@@/<clip slug>
cd @@PROJECTS_ROOT@@/<clip slug> && python3 build.py 16x9       # then 9x16; write build.py first (start from the nearest example)
```

`06_project.py` makes the project: init, engine, kit, fonts, the full-resolution cut linked as `assets/cam.mp4`, a
1080p proxy, `faces.json`, captions (swear words starred if setup says so), `project.json`. It prints the face
centre, every cut, and where each `source.json` join falls on the cut timeline. Write `build.py` with the kit:
`K.start(ROOT, RATIO, face=...)` sets a centred direct-to-camera framing (centred, lowered, captions under the
chin), `K.hook(...)`, `K.show(a, b, html, js, box=...)` places one stage of graphics for whichever ratio is being
built, `K.finish()` adds the 16:9 scrim and builds. The 9:16 shot `himd` is a full-screen shot for a stretch where
the speaker is looking down (at notes, a tablet, the desk): the caption sits lower so it is not on the face. Before
rendering, check each full-screen shot's face drift and chin; end the clip before the speaker looks down to write
if the last line allows it.

`examples/` holds three worked builds written with the kit, kept as structure references only (never reuse their
wording or figures): `example-grid-and-list-build.py` (a grid of avatars, then a list of pills),
`example-graph-and-status-cards-build.py` (a drawn graph, cards whose status tag flips) and
`example-nodes-and-lists-build.py` (nodes joined by a drawn line, two lists).

**Keep the look consistent.** The default style in `references/style.md` and the example builds is one system:
editing rhythm, visual style, motion graphics and captions. Do not restyle clip by clip. On the creator's first
video, build ONE clip, show it, and write what they say into their notes file before building the rest.

Things the engine needs set per video:

- **4K raws:** leave `src` at its 1920x1080 default. That is the engine's layout space, and the video is sized by
  CSS, so linking the 4K cut as `assets/cam.mp4` just makes the 9:16 crop sharp. `06_project.py` makes a 1080p proxy
  of the cut and runs `04_faces.py` on it, so `faces.json` and `face=(cx, cy)` are in the same 1920x1080 space.
- **Head height.** If the speaker sits high in the frame, lower them in 9:16 so the hook clears the head
  (`for k in ("him", "him2"): E.V[k]["Y"] = 1110`; `K.start` does this), and check frame 0.
- **9:16 captions sit just under the chin.** Set `E.CAP["9x16"]["him"]` and `["him2"]` after `init` so the caption
  centre is about 140-170 px below the chin (`K.start` sets 1240 and 1380 as a starting point), then check a still
  of each: never on the jaw or a beard. Split and animation captions stay where they are.
- A join from `source.json` may not appear in `cuts.json` at all. Use the time `06_project.py` prints for it and put
  a shot change on it.
- **9:16 face placement.** The engine default puts the face right of centre (`X: 640`) to leave looking room. When
  the speaker is looking at the camera, centre them after `init`: `for m in E.V.values(): m["X"] = 540` (`K.start`
  does this).

**16:9: the speaker's face is a protected zone.** No graphic, image or text may cover or touch their face or head.
This is enforced, not eyeballed:

1. `python3 $S/04_faces.py "<cut video>" <project dir>` (run for you by `06_project.py`) finds the face every
   quarter second with Apple Vision and writes `faces.json`; open `faces.jpg` to check the yellow face boxes and red
   head boxes. macOS only.
2. While a graphic is beside the speaker, use the `side` / `sidep` shots: the picture is enlarged (1.2x / 1.34x) and
   anchored to the left edge, so the speaker moves right and the left of the frame opens up. Alternate the two on
   the joins. (This engine only opens the left. If the speaker sits in the left third of the frame, use `full` for
   graphics, or say so and plan around it; do not mirror the picture.)
3. Size each stage with `E.fit(a, b, x, content_w)` (`K.show` does it): the largest scale that keeps the graphic's
   right edge clear of the head box for the whole time it is up. Pass the stage its real content box (`box=`).
4. The build prints `WARN FACE: ...` if any stage reaches into the head zone. Never render with that warning.
5. When several joins fall close together, go `full` (the graphic alone on the brand background) for that stretch
   rather than flicking between framings.

If the head leaves little room, make the text inside the graphic larger rather than the graphic wider.

- The engine uses ONE video element and re-frames it per shot, so no pre-cropped camera files are needed.
- `E.shots([...])`: 16:9 uses `wide` / `punch` (112% about the face) / `side` / `sidep` / `full`; 9:16 uses `him`
  (the speaker full screen) / `him2` (the same, tighter, to cover a join between two full-screen blocks) / `himd` /
  `split` / `anim`. The shot names are the engine's API; they say nothing about the speaker. The build warns when a
  big jump cut is left visible on the speaker. Treat every `source.json` join as big.
- **Lines that are not the creator's** (a guest, an interviewer, a clip played on screen): keep one only when it is
  clearly audible on a phone speaker AND the clip does not make sense without it; then mark its captions
  `"other": true` (shown in a paler colour) and cover it with `anim` / `full`. Otherwise cut it and let the clip run
  on the creator's words.
- Graphics are drawn once on a 680x540 `E.stage` and placed per ratio: beside the speaker in 16:9 at the scale
  `E.fit` allows (left edge x 40-50, with `E.scrim` darkening that side while they are up); at 1.45x in the top half
  or centre of the 9:16 frame. Same components, different timing where the modes differ.
- 9:16 follows the three-mode structure in `references/style.md` (text hook on frame 1, three modes, every switch on
  a cut). A 1080p source gives a 1.78x enlargement when the speaker is full screen and is a little soft; a 4K raw is
  not. Say which it was in the report.
- **Swearing** stays in the audio. Captions follow the setup answer (**@@SWEAR_CAPTIONS@@**): `06_project.py` stars
  the common words when it is `starred`.
- **Pointing back to the full video** (setup answer: **@@FULL_VIDEO_TAG@@**). `no tag` means no title tag and no end
  card. Anything else: a small tag with the full video's title, lower left, for the first 3 s, or the end card the
  creator described.
- No pill or label that repeats the caption word.
- `npx hyperframes lint`, `npx hyperframes snapshot --at <each moment a graphic lands> --no-end`, read the
  snapshots, then `npx hyperframes render -o "<out>/<id>/<id> - <ratio>.mp4" --fps <source fps> --quality high`, one
  render at a time.

Every join listed in `source.json` and every BIG cut from the tight cut is hidden: on a mode switch or under a
full-screen graphic in the vertical; on a punch-in/out or under a large graphic in the horizontal.

**Loudness (every final).** Finish every clip with `python3 $S/05_loudness.py "<render>" "<final>"`: about -14 LUFS
with a -1.5 dBTP ceiling, so it plays at a normal level and never peaks. Picture untouched. Check the before/after
line it prints (a published video is usually close already; a raw is not).

**Music and sound effects** (setup answer: **@@CLIP_SOUND@@**). `none` means the clip carries the video's own sound
and nothing else. Anything else: follow `references/style.md` section 5, add the sound after the render and before
the loudness pass, and never guess a music track: use the creator's music folder and favourites from the profile.

**Where finals go** (setup answer: **@@FINALS_DIR@@**). Loudness-corrected finals are plainly named
("<Title> - 16x9.mp4", "<Title> - 9x16.mp4"). `beside the video` means `"<out>/Finals/"`; a folder means that folder
(if the drive is not connected, say so and keep the finals in `"<out>/Finals/"` meanwhile). Working files stay
beside the video.

**Review every render** with the checklist in `references/style.md` section 6. For a copy small enough to send in
chat (`SendUserFile`, 30 MB limit):

```bash
ffmpeg -i "<final>" -c:v libx264 -preset slow -crf 26 -c:a aac -b:a 160k -movflags +faststart "<final> (phone).mp4"
```

Report: clip lengths, which file was used (raw, export or download), what was cut that the creator might want back,
what was moved to the front, each graphic and its asset, every clip that carries someone else's voice or name,
anything invented or chosen without asking.

Changing a finished clip: copy `build.py` to `build_vN.py` first, edit, render with a new suffix, so versions can be
compared.

## Rules that protect people

- **Only the speaker's words, and only their meaning.** Moving a line they said to the front is allowed when the
  clip then delivers exactly what that line promises. Never splice words into a sentence they did not say, never cut
  a qualifier ("for most people", "in your case") so a claim sounds bigger, never open on a line whose meaning
  depends on context the clip drops. If the reorder makes the clip more exciting than what was actually argued, it
  is wrong.
- **A clip must not promise what only the full video delivers.** If the payoff is ten minutes later, either it is in
  the clip or the clip is not made. (A deliberate teaser that points to the full video is a different product: ask.)
- **Guests and other voices.** A guest agreed to be in the video, which normally covers clips of it; still flag
  every clip that carries someone else's voice or name in the clip list (`03_clips.py` marks other speakers), and
  leave out anything sensitive that is theirs rather than the creator's (health, money trouble, family, a named
  third party).
- **Sponsor reads, affiliate mentions and dated offers** ("this week only", a launch date) are left out of clips
  unless the creator asks for them.
- **Other people's material shown on screen** (a creator's post, a website, a clip played in the video): show it as
  the real thing, uncropped and credited by its own visible name or handle. Permissions are the creator's to manage;
  list each one in the report.
- **Someone else's video** is handled as the setup answer says (@@OTHER_CREATORS@@); under the default it is never
  clipped past the clip list without asking first.
- **The never-clip list** (@@NEVER_CLIP@@) is absolute: those topics and names stay out of clips, captions and
  graphics.

## Defaults of this style (each is a setup answer or a style rule; change when the creator says)

The creator's own videos only unless setup says otherwise · every clip that clears the bar, up to the ceiling in
"Your setup" · what happens after the prompts follows the setup answer · 16:9 captions bottom-centre at about
68 px · 16:9 graphics beside the speaker on glass cards · a punch-in of about 12% to hide joins in 16:9 · no text
hook in 16:9, a two-line text hook in 9:16 · face centred in 9:16 when the speaker looks at the camera, captions
just under the chin · no "watch the full video" tag or end card unless setup says so · swearing kept in the audio,
captions per the setup answer · music and sound effects per the setup answer.

New rules the creator gives while working ("never do X", "always Y") go straight into
`~/.claude/creator-profile/notes/youtube-clips.md` under `## Style overrides`, dated, the moment they say them.

## Related

`coaching-call-clips` (the same system for recorded calls: keep the two in step) · `business-short-form-reels`
(shares the vertical look, if installed) · `hyperframes` (the framework that builds and renders every edit).
