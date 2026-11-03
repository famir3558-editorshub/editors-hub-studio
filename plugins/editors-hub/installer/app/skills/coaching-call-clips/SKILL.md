---
name: coaching-call-clips
description: Turn a full recorded coaching call (30-90+ minutes, 16:9, typically with the camera off to the side while the coach looks at the client on screen) into a small number of high-quality social clips. Does the whole front half of the job - transcribes the entire call, reads all of it, finds and ranks the strongest standalone moments (insights, stories, analogies, frameworks, corrected misconceptions, a client question followed by a strong answer), tightens each into a 30-60 s story (up to ~90 s) with the strongest line the coach actually said moved to the front as the hook, and writes TWO production-ready editing prompts per clip - a 16:9 horizontal edit (graphics in the empty space beside the speaker, captions along the bottom) and a separately composed 9:16 vertical edit (full screen / split / full-screen animation) - then cuts each clip's source out of the call and builds the edits in HyperFrames with its own cut pipeline, engine and graphics kit. Use whenever the creator hands over a coaching call, client call, group call, Q&A call, Zoom or Fathom recording, or any long conversation and says "clip this call", "find the clips", "coaching clips", "pull the best moments", "turn this call into reels", "make content from this call", "what's worth posting from this call", or asks for horizontal and vertical versions of a call excerpt. Also for one part alone - only the clip list, only the prompts, re-ranking, or one more clip from a call already analysed. Not for a single scripted talking-head take (use a short-form reel skill), a published YouTube video (youtube-clips), or carousels.
---

# Coaching call clips

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/coaching-call-clips/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first. Do not start the task, and do
  not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if it exists,
  `~/.claude/creator-profile/notes/coaching-call-clips.md`. Rules under `## Style overrides` in that notes file win
  over the defaults written below.

"redo my setup" re-runs the interview at any time.

## Your setup

Filled in by setup. To change a line, change the answer (`setup/SETUP.md`), never this text.

| | |
|---|---|
| Creator | @@CREATOR_NAME@@ · @@BRAND_NAME@@ · @@HANDLE@@ |
| Colours | accent @@ACCENT@@ (@@ACCENT_NAME@@) · background @@BG@@ · text @@PAPER@@ · small labels @@GREY@@ |
| Fonts | main: @@FONT_MAIN_NAME@@ · emphasis: @@FONT_ACCENT_NAME@@ · captions: @@FONT_CAPTION_NAME@@ |
| Transcriber | @@TRANSCRIBER@@ |
| Folders | working files `@@WORK_ROOT@@` · HyperFrames projects `@@PROJECTS_ROOT@@` · real material (proof) `@@PROOF_DIR@@` |
| How calls are recorded | @@CALL_RECORDER@@ · camera @@CAMERA_ANGLE@@ · usually @@CALL_RESOLUTION@@ |
| People on the calls have agreed to be clipped | @@CLIP_CONSENT@@ |
| A client who is hard to hear | @@QUIET_CLIENT@@ |
| Swearing | kept in the audio; captions: @@SWEAR_CAPTIONS@@ |
| How many clips | every clip that clears the bar, @@MAX_CLIPS@@ at most |
| After the prompts are written | @@BUILD_RULE@@ |
| Ratios | @@RATIOS@@ |
| Music and sound effects | @@CLIP_SOUND@@ |
| Finished clips go to | @@FINALS_DIR@@ |
| Never clip | @@NEVER_CLIP@@ |

## What this skill does

A full coaching call goes in. What comes out, in this order:

1. **A clip list**: the few moments worth publishing, ranked, each with its hook and why it earns a post.
2. **Editing prompts per clip**: one for a 16:9 horizontal edit, one for a 9:16 vertical edit (only the ratios in
   "Your setup"). Same words, two different compositions.
3. **A source file per clip**, cut out of the call with the hook already in place.
4. When the creator says go: the edits themselves, built here with this skill's cut pipeline, engine and graphics kit.

The skill owns the listening, the choosing, the story edit and the build. Everything it needs is inside this folder.

`S=~/.claude/skills/coaching-call-clips/scripts` · cut pipeline `C=$S/cut` · work dir `W=@@WORK_ROOT@@/<slug>` (small
files) · outputs `"<call folder>/<call name> - Clips/"`, one sub-folder per clip (called `<out>` below). Video files
are large: big files stay beside the recording, on whichever drive holds it. Long steps run in the background, one
render at a time (two renders writing to the same external drive at once can fail).

Requirements: macOS, Node 22+, ffmpeg, HyperFrames (`npx hyperframes`), Python 3 with `numpy`, `soundfile`, `requests`
and `Pillow`. Face finding (`04_faces.py` + `face_boxes.swift`) uses Apple's Vision framework and the Swift compiler
that ships with the Xcode command line tools, so the build half of this skill runs on a Mac only.

## The sources of truth (read before planning, every session)

| For | Read | Notes |
|---|---|---|
| **Captions** (font, weight, emphasis, timing, rhythm) | `references/style.md` section 1 | One caption style for both versions of every clip. |
| **Vertical layout** (the three modes, cut alignment, where captions sit, opening hook) | `references/style.md` section 2, then `references/layouts.md` | What changes for call footage is in `layouts.md`. |
| **Graphics, motion, sound** | `references/style.md` sections 3-5 | A library to choose from, not a checklist. |
| **The tight cut and the caption file** | `references/cut.md` | The per-clip pipeline in `scripts/cut/`. |
| **Brand values** | "Your setup" above and `~/.claude/creator-profile/profile.json` | Colours and fonts are already filled into the engine. |
| **The creator's own rules** | `~/.claude/creator-profile/notes/coaching-call-clips.md` | `## Style overrides` there win over every default here. |

If the pack's `business-short-form-reels` skill is also installed, the vertical look (modes, hook, pills, glass,
motion) is shared with it. Its style notes file, `~/.claude/creator-profile/notes/business-short-form-reels.md`, is
where that look is kept in step: read it too, and when the creator changes a vertical rule there, apply it here.

Two points are settled so they are not re-argued:

- Captions here are one line of one to three words in the caption font with the emphasis word in the emphasis font
  and the accent colour, in both ratios. Only their *placement* in the vertical follows the three-mode layout.
- Captions may be made a little larger when that reads better. Still one line, never stacked.

Do not combine every treatment in one clip. For each moment pick the single treatment that explains it best.

## What makes these different from a scripted reel

The coach is not talking to the camera. On most calls the camera is off to one side and they are looking at the
client on their monitor (setup says: camera @@CAMERA_ANGLE@@). Leave it that way. The appeal is that the viewer has
been let into a private conversation where something unusually useful is being said; the edit removes friction and
makes the idea easier to follow, and stops there. So:

- No attempt to make it look like a direct-to-camera piece. The off-axis angle is the look: premium, documentary.
- The real room, the real voice, the real pauses for thought when they carry weight. No voice processing beyond
  cleaning the hiss and bringing the level up to normal (see Loudness).
- Graphics explain; they never decorate. A clip with two graphics that land is better than one with ten.

If the camera faces the speaker instead, the same rules hold; only the crop changes (see `references/layouts.md`).

## 1. Prepare and transcribe the whole call

```bash
python3 $S/01_call_prep.py "<call video>" <slug>     # audio, meta, two contact sheets of the whole call
python3 $S/02_call_transcribe.py <slug>              # the whole call, with speakers when the transcriber can
```

Act on the warnings (Zoom recordings are often variable frame rate).

**Transcription uses the transcriber chosen at setup: `@@TRANSCRIBER@@`.** Every script goes through
`scripts/stt.py`, so nothing else needs changing when the answer changes.

- `elevenlabs` (recommended): the most accurate words and timings, and speaker labels, at roughly $0.22 per hour of
  audio. The key is read from the environment or the shell profile, never printed, and **never asked for in chat**.
  If it is missing the script says so: tell the creator to add the export line themselves (`setup/SHARED-SETUP.md`,
  section A5).
- `local`: runs on this computer through HyperFrames. Free and private, but **there are no speaker labels**: every
  word comes back as `S0`. On a call with more than one person, say so plainly at the top of the clip list and work
  out who is speaking from what is said (who asks, who answers, who is named). Word edges are also a little looser,
  so read the tight cut's verify output closely.
- Never use the ElevenLabs connector's transcribe tool as a substitute (it costs far more for the same model), and
  do not swap in a Zoom, Fathom or other ready-made transcript even when one exists for the call: their timings are
  not word-accurate, and every cut downstream depends on word timings.

**Speaker labels drift on group calls.** Even with labels, a three-client call can come back with people swapped
several times and with a video played on screen credited to the coach. Treat `S0/S1/...` as a hint: decide who is
speaking from what is said, and check any segment that matters by listening or by a still.

Open both contact sheets. Note which side of the frame the speaker sits on, which way they face, where the empty
space is, and whether the set-up changes during the call (they move, the light changes, a screen share appears).
That decides where graphics can go in step 5.

## 2. Read all of it, then map it

Read `W/transcript.txt` from the first line to the last (it is long: read it in pages until the end; do not sample,
do not stop when you have enough clips). The best moment is often an hour in, and a line only makes sense as a hook
once you know what the call was about.

Work out who each speaker is from what they say. Then, before choosing anything, write yourself a short map of the
call: the topics in order with their times, each question the client asked, each story, each framework or analogy,
and where each one resolves. Give the creator the map in four or five lines at the top of the clip list so they can
see the whole call was covered.

## 3. Find, rank and choose

Read `references/selection-and-story.md` (what to look for, the scoring, the story edit, the hook rules).

In short: list every candidate, score each on the eight criteria, and keep **every clip that is strong enough to
post and can actually be cut cleanly**. No target and no minimum: three is a fine answer, so is seven.
**@@MAX_CLIPS@@ is the ceiling**; if more clear the bar, keep the strongest and name the rest under "next in line".
Do not trim a good clip to keep the list short, and do not pad it to look productive. Make a judgment: every clip on
the list is one you would publish, mapped out in `clips.json`, with its source cut and its prompts written. Say
plainly how many cleared the bar and how many were borderline.

Leave out anything on the creator's never-clip list (**@@NEVER_CLIP@@**), and apply the consent rule under "Rules
that protect people" before a candidate goes on the list, not after.

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
segments is a join someone has to hide, and a piece under about half a second (a three-word answer lifted on its
own) rarely cuts cleanly out of a live conversation where people talk over each other.

Read each printed clip as if you had never heard the call. Fix and re-run until each one has a beginning, a
development and a payoff, runs 30-60 s (up to about 90 s only when the idea truly needs it), and every `!` line has
been dealt with. The estimate is within a few seconds of the final cut.

## 5. Write the clip list and the prompts

Read `references/layouts.md` (how each ratio is composed for this footage) and `references/prompt-format.md` (the
exact format). Look at a still from each clip's time range (`ffmpeg -ss <t> -i <call> -frames:v 1 still.jpg`) so
the framing notes describe the real picture, not a guess.

- `"<out>/Clip list.md"`: the call map, then the ranked clips.
- `"<out>/<id>/<id> - 16x9 prompt.md"` and `"<out>/<id>/<id> - 9x16 prompt.md"` for every clip (only the ratios in
  "Your setup": @@RATIOS@@).

For each graphic, find the real thing first: the website, post, profile, document or person the speaker names. Look
in the proof folder (`@@PROOF_DIR@@`), then elsewhere on the creator's computer and drives, then the web, and record
in the prompt where each asset is, or that it still has to be found. A graphic field left as "none: stay on the
speaker" is a correct answer; do not fill a field because the template has one.

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

Then build the ratios from that one cut with this skill's engine (`engine/coach_engine.py`) and graphics kit
(`engine/coach_kit.py`):

```bash
python3 $S/06_new_project.py <clip slug> "<Title>"   # @@PROJECTS_ROOT@@/<clip slug>: engine, kit, fonts, cut, captions, faces.json
cd @@PROJECTS_ROOT@@/<clip slug> && python3 build.py 16x9       # then 9x16; write build.py first (start from the nearest example)
```

`examples/` holds three worked builds written with the kit, kept as structure references only (never reuse their
wording or figures): `example-figure-maths-calendar-build.py` (a figure card, a sum with ticking results, a calendar
of slots), `example-phone-mockup-build.py` (one graphic carried across several 9:16 mode switches) and
`example-bars-and-pill-stack-build.py` (growing bars, a pill stack joined by drawn lines). In a kit build each
graphic is a function that returns its HTML on the 680x540 stage plus a function that returns its timeline, and
`K.build(ratio, shots, stages, hook=, scrim=)` places every stage for you: in 16:9 against the open side of the
frame at the largest scale that clears the speaker's head, in 9:16 centred in the top half (`split`) or the frame
(`anim`). A graphic that continues across a 9:16 mode switch is a second instance with its earlier state pre-set
(`gsap.set`), not one stage spanning the switch.

**Which side the graphics go.** Run `06_new_project.py`, look at `faces.jpg`: if the speaker sits right of centre
use `side` / `sidep` (they move right, graphics on the left; `K.build(..., side="left")`); if they sit left of centre
use `rside` / `rsidep` (they move left, graphics on the right; the default).

**Keep the look consistent.** The default style in `references/style.md` and the example builds is one system:
editing rhythm, visual style, motion graphics and captions. Do not restyle clip by clip; build the next clip the same
way, and change a rule only when the creator asks (then write it into their notes file under `## Style overrides`).

**16:9: the speaker's face is a protected zone.** No graphic, image or text may cover or touch their face or head.
This is enforced, not eyeballed:

1. `python3 $S/04_faces.py "<cut video>" <project dir>` (run for you by `06_new_project.py`) finds the face every
   quarter second with Apple Vision and writes `faces.json`; open `faces.jpg` to check the yellow face boxes and red
   head boxes. macOS only.
2. While a graphic is beside the speaker, use the `side` / `sidep` shots (or `rside` / `rsidep`): the picture is
   enlarged (1.2x / 1.34x) and anchored to one edge, so the speaker moves across and the other side of the frame
   opens up. Alternate the two on the joins.
3. Size each stage with `E.fit(a, b, x, content_w)` (or let `K.build` do it): the largest scale that keeps the
   graphic clear of the head box for the whole time it is up. Pass the stage its real content box (`box=`).
4. The build prints `WARN FACE: ...` if any stage reaches into the head zone. Never render with that warning.
5. When several joins fall close together while someone off camera is talking, go `full` (the graphic alone on the
   brand background) for that stretch rather than flicking between framings.

If the head leaves little room, make the text inside the graphic larger rather than the graphic wider.

- The engine uses ONE video element and re-frames it per shot, so no pre-cropped camera files are needed.
  `E.init(ROOT, ratio, face=(cx, cy))` takes the face centre in the engine's 1920x1080 layout space (`04_faces.py`
  prints it; for a source of any other size `06_new_project.py` finds faces on a 1080p proxy so the numbers match).
- `E.shots([...])`: 16:9 uses `wide` / `punch` (112% about the face) / `side` / `sidep` / `rside` / `rsidep` /
  `full`; 9:16 uses `him` (the speaker full screen) / `him2` (the same, tighter, to cover a join between two
  full-screen blocks) / `split` / `anim`. The shot names are the engine's API; they say nothing about the speaker.
  The build warns when a big jump cut is left visible on the speaker. A join that came from `source.json` (minutes
  of the call removed) can be listed as a *small* cut by the tight-cut script, or not listed at all when no silence
  was trimmed at it: treat every `source.json` join as big and work out its cut-timeline time from the words either
  side.
- **A client who is hard to hear** (setup answer: **@@QUIET_CLIENT@@**). Clients usually come through the coach's
  speakers, so their audio is thin. Under the default (`cut their lines`): remove the client's lines and let the
  clip run on the coach's words alone, which also flows better. Keep a client line only when it is clearly audible
  on a phone speaker AND the clip does not make sense without it AND the consent rule allows it; then mark its
  captions `"other": true` (shown in a paler colour) and cover it with `anim` / `full`. When two transcripts of a
  client line disagree, that is the sign it is too unclear to keep.
- Graphics are drawn once on a 680x540 `E.stage` and placed per ratio: beside the speaker in 16:9 at the scale
  `E.fit` allows (with `E.scrim` darkening that side while they are up); at 1.45x in the top half or centre of the
  9:16 frame. Same components, different timing where the modes differ.
- 9:16 follows the three-mode structure in `references/style.md` (text hook on frame 1, three modes, every switch on
  a cut). A 1080p call gives a 1.78x enlargement when the speaker is full screen: it is the widest crop there is,
  they fill the frame, and it is a little soft (setup says calls are usually @@CALL_RESOLUTION@@). Say so in the
  report.
- **Swearing** stays in the audio. Captions follow the setup answer (**@@SWEAR_CAPTIONS@@**): `06_new_project.py`
  stars the common words when it is `starred`.
- No pill or label that repeats the caption word.
- Anything on screen that belongs to a client (a profile, a handle, a face) is built as a generic stand-in with a
  default avatar unless the creator says to show the real one.
- `npx hyperframes lint`, `npx hyperframes snapshot --at <each moment a graphic lands> --no-end`, read the
  snapshots, then `npx hyperframes render -o "<out>/<id>/<id> - <ratio>.mp4" --fps <source fps> --quality high`, one
  render at a time.

Every join listed in `source.json` and every BIG cut from the tight cut is hidden: on a mode switch or under a
full-screen graphic in the vertical; on a punch-in/out or under a large graphic in the horizontal.

**Hiss and loudness (every final).** Call recordings are very quiet (about -28 to -32 LUFS), and raising them raises
the room hiss. Finish every clip with `python3 $S/05_loudness.py "<render>" "<final>"`: a light noise reduction
first (70 Hz high-pass, afftdn 14 dB with noise tracking: about 9 dB less hiss, voice unchanged), then about
-14 LUFS with a -1.5 dBTP ceiling, so it plays at a normal level and never peaks. Picture untouched. Check the
before/after line it prints. Keep the denoise light.

**Music and sound effects** (setup answer: **@@CLIP_SOUND@@**). `none` means the clip carries the call's own sound
and nothing else. Anything else: follow `references/style.md` section 5, add the sound after the render and before
the loudness pass, and never guess a music track: use the creator's music folder and favourites from the profile.

**Where finals go** (setup answer: **@@FINALS_DIR@@**). Loudness-corrected finals are plainly named
("<Title> - 16x9.mp4", "<Title> - 9x16.mp4"). `beside the recording` means `"<out>/Finals/"`; a folder means that
folder (make a dated sub-folder only if the creator asked for one; if the drive is not connected, say so and keep
the finals in `"<out>/Finals/"` meanwhile). Working files stay beside the call recording.

**Review every render** with the checklist in `references/style.md` section 6. For a copy small enough to send in
chat (`SendUserFile`, 30 MB limit):

```bash
ffmpeg -i "<final>" -c:v libx264 -preset slow -crf 26 -c:a aac -b:a 160k -movflags +faststart "<final> (phone).mp4"
```

Report: clip lengths, what was cut that the creator might want back, what was moved to the front, each graphic and
its asset, every clip that carries someone else's voice or name, anything invented or chosen without asking.

Changing a finished clip: copy `build.py` to `build_vN.py` first, edit, render with a new suffix, so versions can be
compared.

## Rules that protect people

- **Only the speaker's words, and only their meaning.** Moving a line they said to the front is allowed when the
  clip then delivers exactly what that line promises. Never splice words into a sentence they did not say, never cut
  a qualifier ("for most people", "in your case") so a claim sounds bigger, never open on a line whose meaning
  depends on context the clip drops. If the reorder makes the clip more exciting than what was actually argued, it
  is wrong.
- **Consent decides whose voice can be used** (setup answer: **@@CLIP_CONSENT@@**).
  - `yes`: the people on the calls have agreed to be clipped, so a client's voice and question can be used as
    recorded. Two things still hold. Anything sensitive that is theirs rather than the coach's (health, money
    trouble, family, a named third party, exact private figures) is cut or left off the list, because agreeing to be
    clipped is not agreeing to have that broadcast. And every clip that carries a client's voice or name is flagged
    in the clip list (`03_clips.py` marks other speakers) so the creator can see it at a glance.
  - `no`: **only the creator's own voice is clipped.** Every line spoken by anyone else is cut. A client's name,
    business, face and screen never appear: cover a screen share with `full` / `anim`, and use a written question
    card in the creator's words where the answer needs its question. A moment that cannot stand without the other
    person's words is not made; list it under "Needs a yes first" in the clip list so the creator can ask that
    person. `03_clips.py` prints `NOT CLEARED` on any segment that still contains another speaker.
  - `ask each call`: ask once, at the start of each call, who on it has agreed, then apply `yes` or `no` person by
    person.
  If a call looks like a different kind of session from the usual (a sales call, a guest, a group with people who
  may not have agreed), ask once whatever the setup answer says.
- **Prefer clips that work without the client's voice.** They are easier to hear, easier to cut and safer to post.
- **Advice given to one person can mislead a stranger.** If the answer only holds for this client's situation,
  either keep the sentence that says so or do not make the clip.
- **Other people's material shown on screen** (a creator's post, a website): show it as the real thing, uncropped
  and credited by its own visible name or handle. Permissions are the creator's to manage; list each one in the
  report.
- **The never-clip list** (@@NEVER_CLIP@@) is absolute: those topics and names stay out of clips, captions and
  graphics.

## Defaults of this style (each is a setup answer or a style rule; change when the creator says)

Every clip that clears the bar, up to the ceiling in "Your setup" · what happens after the prompts follows the
setup answer · 16:9 captions bottom-centre at about 68 px · 16:9 graphics in the empty side of the frame on glass
cards · a punch-in of about 12% to hide joins in 16:9 · no text hook in 16:9, a two-line text hook in 9:16 ·
swearing kept in the audio, captions per the setup answer · a client's own voice kept only when the answer needs it,
it is clearly audible and consent allows it · music and sound effects per the setup answer.

New rules the creator gives while working ("never do X", "always Y") go straight into
`~/.claude/creator-profile/notes/coaching-call-clips.md` under `## Style overrides`, dated, the moment they say them.

## Related

`youtube-clips` (the same system for published long-form videos) · `business-short-form-reels` (shares the vertical
look, if installed) · `hyperframes` (the framework that builds and renders every edit).
