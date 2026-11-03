---
name: glass-explainer-reel
description: Edit one raw talking-head video into a 9:16 "glass explainer" reel - the explainer panel edit (full-frame close-ups alternating on hard cuts with a black dot-grid frame where the speaker's video sits in a rounded panel at the bottom, their cut-out rising above it, heading on top, one-line word-timed captions) with the business-reel style graphics built into the panel's graphic area - a distinct visual metaphor per reel, real people / reel covers / Instagram notifications / saved Reels / Google Docs, drawn lines and graphs, ticking counters, light sweeps, on rectangular cards with a restrained Liquid Glass finish, plus quiet sound effects on key reveals. Does the whole job from the raw file - transcript, tight cut, verification, captions, asset hunt (the creator's computer and drives first, then the web), build, export with sound, review. Use whenever the creator says "glass explainer", "glass explainer reel", "the panel edit with the business graphics", "explainer reel with glass", "panel style with real examples", or asks for a new version of one. Not for the plain panel style (explainer-panel-reel), the three-mode split reels (business-short-form-reels) or B-roll edits (broll-stacked-text-edit).
---

# Glass explainer reel

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/glass-explainer-reel/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first. Do not start the task, and do
  not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if it exists,
  `~/.claude/creator-profile/notes/glass-explainer-reel.md`. Rules under `## Style overrides` in that notes file
  win over the defaults written below.

"redo my setup" re-runs the interview at any time.

## Your setup

Filled in by setup. To change a line, change the answer (`setup/SETUP.md`), never this text.

| | |
|---|---|
| Creator | @@CREATOR_NAME@@ · @@BRAND_NAME@@ · @@HANDLE@@ (@@PLATFORM@@) |
| What they do, and for whom | @@NICHE@@ |
| Accent colour | @@ACCENT@@ (@@ACCENT_NAME@@) · background @@BG@@ |
| Fonts | main: @@FONT_MAIN_NAME@@ · emphasis: @@FONT_ACCENT_NAME@@ · captions: @@FONT_CAPTION_NAME@@ |
| Watermark | @@WATERMARK@@ (handle on the video) |
| Glass finish | @@GLASS_LOOK@@ (full / soft / off) |
| Sound effects | @@SOUND_EFFECTS@@ · sound pack folder: @@SFX_DIR@@ |
| Music | @@MUSIC_RULE@@ · music folder: @@MUSIC_DIR@@ |
| Transcriber | @@TRANSCRIBER@@ |
| Finished reels go | @@OUTPUT_RULE@@ |
| Footage drive | @@MEDIA_DRIVE@@ |
| Folders | working files `@@WORK_ROOT@@` · HyperFrames projects `@@PROJECTS_ROOT@@` |
| Real material (proof) | @@PROOF_DIR@@ |
| Other folders to search for real assets | @@ASSET_DIRS@@ |
| Real assets from the web | @@WEB_ASSETS@@ |
| Never show | @@NEVER_SHOW@@ |
| How far to go alone | @@WORK_RULE@@ |

## What it makes

One raw talking-head file goes in. A 1080x1920 video comes out that alternates between two layouts on hard cuts:

- **Full frame**: a close-up of the speaker filling the screen, caption under the chin.
- **Panel**: black frame with a faint dot grid; the speaker's video in a rounded panel at the bottom with their real
  background (their head and raised hands may rise above the panel's top edge); a heading at the top; graphics in the
  space between that build and clear in time with what is said; the caption just above the head.

Two styles were merged to make this one. **The edit is the explainer panel reel; the graphics are the business
reel's, redesigned to live inside the panel's graphic area.** When the two disagree, the panel edit wins.
`references/merge-rules.md` lists exactly what came from where and what was left out; read it, and
`references/reference-study.md` (the layout and pacing numbers), before the first build of a session.
`examples/validation/*.py` are structure references only.

`S=~/.claude/skills/glass-explainer-reel/scripts` · work dir `W=@@WORK_ROOT@@/<slug>` (small files) · HyperFrames
project `@@PROJECTS_ROOT@@/<slug>-glass` · outputs `"<video folder>/<video name> - Edit/"` (the output rule above).
Big files stay beside the source, on the drive that holds it. Long steps run in the background, one render at a time
when the output is on an external drive. Every script prints its own usage.

## How to work on this skill

The creator's working rule is in the setup table (**How far to go alone**). The default, `finish the best version,
then report`:

**Do not stop to ask for an asset or for final wording.** Find the best real asset yourself (section 6), write the
best heading and label wording you can, finish the reel, and then tell the creator what you used, where each thing
came from, and what to check or replace. They sort out final copy and asset choices afterwards. If the rule is
`stop and ask at each stage`, stop after the cut, after the plan and after the draft instead.

Always a stop, whatever the rule: two files could be the raw video; **music** (never assume a track: follow the
music rule, ask whether they want one and which, separately from the build, and deliver the reel without it in the
meantime); anything that would publish or send something on their behalf.

**Draft first.** Never render the full-quality final first. Render a fast draft (`09_render.py <slug> --draft`),
review it yourself (section 10), show it to the creator, and render the final only once they are happy with it.
Apply their timestamped notes as a new version (`build_vN.py`, `--tag vN`). With several reels in a batch: draft the
first, apply its notes, then carry the same notes into the rest.

## 1. Inputs

| Input | Required | Notes |
|---|---|---|
| Raw video | yes | One talking-head file, any resolution, 16:9 or 9:16, constant frame rate. |
| Supporting footage / images | no | Anything the creator supplies goes in the project's `assets/media/` and is used ahead of anything you find. |
| Brand | on file | Accent colour, brand name and the optional watermark handle come from the creator's profile (see the setup table). A different accent for one video (a client's video) = `W/brand.json` with `{"accent": "#RRGGBB"}` read **from that client's files** (never eyeball a colour). |
| Handle | optional | Drawn as a small watermark only when the watermark answer is on and a handle is set. Do not guess a handle. |
| Profile picture | optional | `avatar.jpg` in the creator profile's assets folder: shown on "me" nodes and as the sender of a notification. Without one a neutral grey picture is drawn and listed as a mock-up. |

`python3 $S/01_prep.py "<video>" <slug>` and act on its warnings (variable frame rate needs a constant-rate copy first).

## 2. Transcribe, then check it against the audio

`python3 $S/02_transcribe.py <slug>`: uses the transcriber chosen at setup (`scripts/stt.py`; ElevenLabs Scribe by
default, or the free local engine). The key is read from the shell profile, never printed, never asked for in chat.
Do not use the ElevenLabs connector's transcribe tool (about 30x the cost). Read the whole printed script and
`W/words.txt`. Any word that looks wrong for the subject (a name, a brand, a number) is confirmed from context and
fixed in the captions with `{heard|Shown}`. With the local transcriber, word edges are looser: the verify step in
section 3 matters more, and clipped words need a closer listen.

## 3. The tight cut

Write `W/drops.json`: `{"words": [[i, j], ...], "secs": [[a, b], ...]}` (word-index ranges from `words.txt`; `secs`
for things that are not words).

Remove: recording set-up and ending footage · false starts and repeated takes (keep the LAST complete take, drop
every earlier attempt in full) · mistakes, fillers, throat clears, asides · dead space (the script removes pauses,
breaths, head and tail itself: never list them).

Keep: **the speaker's meaning** (every sentence still a sentence; if unsure whether a repeat is emphasis, keep it;
never reorder, never splice) · **natural pacing** (default gap 0.12 s; `--gap 0.2` if breathless; a pause left for
effect stays) · a mid-video call to action and the end one.

`python3 $S/03_cut.py <slug>` then `python3 $S/04_verify.py <slug>`. Read the EDIT as a script and every MISSING /
EXTRA / CHANGED / PAUSE / REPEAT line; fix `drops.json` and repeat until clean. **The video starts on the first
spoken word and ends right after the last** (head and tail under ~0.25 s; `--pad-out 0.06` if the last word is
clipped). Then `python3 $S/05_render_cut.py <slug>` (background).

From here every time is **cut-timeline seconds**: `W/edit.txt`, `W/cuts.json`, `python3 $S/cut_times.py <slug>`
(`BIG` = a jump a viewer sees).

## 4. Frame the speaker for both layouts

1. `python3 $S/frames.py <slug> <t> <t> ...`: gridded stills (include one where they lean or gesture high). Read
   off, in source pixels, the centre of the face, the top of the head and the chin.
2. Write `W/layout.json`: `{"face": {"cx": .., "top": .., "chin": ..}, "popout": true}`.
3. `python3 $S/06_crops.py <slug> --preview <t> ...` and open each still (left = close-up, right = panel). The
   caption line sits under the chin on the left and clears the head on the right; the whole head is in view. Nudge
   with `full_dx`, `panel_dx`, `panel_dy` or the scales.
4. `python3 $S/06_crops.py <slug>` (background; the cut-out takes about 0.1 s per frame).

`popout: true` (the head rises above the panel edge) needs a clean cut-out: a halo, flicker or missing fingers in
the draft means `"popout": false` and a re-run, not a bad edge. **The panel, its position, its rounded top and the
real background inside it are fixed: glass is never applied to it.**

## 5. Captions (the whole video, including under graphics)

`python3 $S/07_captions.py <slug>` drafts `W/phrases.txt`; edit it and run again.

- **Every spoken word on screen once, in order, timed to the speech** (the script refuses anything else).
- **One short line, 1-3 words**, changing on the word. Never split a number from its unit or a name.
- **Type**: the caption font, tracking -50, white, soft shadow.
- **Emphasis** `*like this*`: the emphasis font in the accent colour, same line, same baseline. A figure
  (`*400,000*`) stays in the main font and turns the accent colour. About 3-6 a minute, never two captions running.
- **No stacked captions, no one-word mode, no other caption fonts.** Too long for one line = two captions.
- **Position**: close-up = under the chin on the upper chest; panel = in the gap just above the head, clear of the
  graphics. Read `W/captions.txt` in full after every run and clear every LONG / SHORT line.

## 6. Find the assets (before planning the graphics)

For every person, post, page, document, number or result the script mentions, get the real thing, in this order:

1. **What the creator supplied** for this video.
2. **Their computer and drives**: `python3 $S/find_assets.py <term> [<term> ...] [--image|--video]` searches this
   skill's `assets/` folder, the proof folder and other asset folders named at setup, earlier reel projects, the
   Desktop / Downloads / Pictures folders and Spotlight across every mounted drive. Try several terms (first name,
   handle, "testimonial", "screenshot", the number). Open the candidates with Read before choosing.
3. **The web** (when the setup answer allows it): Google Images and the person's public profile or page, in the
   browser (their real profile picture, channel page, post cover). Save the file into `<project>/assets/media/`.
4. **A mock-up, last**: simple and plainly a stand-in (default grey profile picture, a generic account name such
   as "viewer", grey bars instead of invented body copy). Never a made-up name that could pass for a real person.

Anything on the "never show" list is not used, whatever the script says.

Copy the chosen file into the project's `assets/media/` and **record where it came from in `build.py`**:
`E.asset("assets/media/x.jpg", "<the path or URL it came from>", "<note>")`. Kit interfaces record themselves as
mock-ups. The build prints every mock-up and unrecorded asset and writes the full list to `review.json`: that list
is the asset part of the final report.

Rules for real assets: **never crop a person** (`K.person` sizes the card to the asset's own shape) · a clip with
burned-in captions or music is still usable (it plays muted) but say so in the report · other creators' reel covers
are fine (the creator handles copyright) · the creator's real profile picture goes on anything shown as coming from
them.

## 7. Plan the edit

`python3 $S/08_new_project.py <slug> "<Title>"`, then plan in three passes over `W/edit.txt`. Show the creator the
plan as a short table (time, mode, heading, graphic, asset) **in the same message as you carry on building** (unless
the working rule says to stop).

**a. Modes** (unchanged from the panel edit). Mark the full-frame windows; everything else is panel.
- Open in panel with the heading writing on and the first graphic arriving in the first second, unless the hook is
  stronger said straight to camera. No opening text hook over the face.
- Full frame is for lines with no graphic to show: a direct statement, a punchline, a transition, the call to
  action. Full frame is 20-30% of the runtime; close-ups last about 1-8 s; panel stretches about 2-20 s; a close-up
  at least every ~20 s.
- **Every switch on an edit cut, every BIG cut on a switch.** A BIG cut inside a close-up is an error; small cuts
  inside a panel stretch are fine; a switch with no cut nearby is allowed (the punch-in reads as a cut).
- Two layouts only. No split-screen halves, no full-screen animation sections.

**b. Points.** Each point gets a heading (`E.heading`, 4-8 words, title case) or, when the speaker counts things
off, a numbered section bar (`E.section`). It changes when the point changes.

**c. Graphics** (this is where the business reel comes in).
- **One signature metaphor for the reel's core idea**, different every reel (a bridge between two things, a rope,
  a retention line, a lens on a crowd). Build it in parts, each part arriving as it is named, and bring it back
  when the speaker returns to the idea.
- **Show, don't label.** Prefer a demonstration (a drawn connection, a graph, a counter, a before/after, the
  active item lighting up) to a row of text boxes. Labels are short and modest; **never repeat the spoken caption
  as graphic text**.
- **A real-world example whenever the script calls for one**: the real person (`K.person`), their real channel
  (`K.ytchannel`), real reel covers (`s.grid`, `s.img`), comments or DMs as Instagram notifications (`K.notifs`),
  "save this" as a Reel being saved (`K.saved`), a document as a Google Doc (`K.gdoc`), anything quoted typed into
  a card (`s.typed`).
- **A graphic too big for the area** (y 380-1190, 810 px tall) is redesigned smaller or **spread over successive
  panel scenes** (part one, close-up on its cut, part two). It never takes over the full frame and never moves a
  switch.
- One idea per scene; when the speaker moves on, it goes.

## 8. Build (`build.py` in the project; never edit `index.html`)

`examples/validation/build.py` is a worked reel (a real-world example scene, an explainer scene, a numbered
section); `examples/validation/build_gallery.py` shows every kit component. They are structure and API references
only: never reuse their wording, names or assets. `engine/glass_engine.py` and `engine/glass_kit.py` document every
call.

```python
import glass_engine as E, glass_kit as K
E.full([[5.82, 8.06]])                                   # close-up windows (snapped to frames)
E.heading(0.0, 5.7, "Show Them What", "You've *Already Done*")
with E.scene(0.0, 5.8) as s:                             # everything left fades just before the end
    me = s.node(540, 462, t=1.3, r=66, img=K.ME)         # the creator's picture, on "me"
    s.chip("Strategist", 540, 548, t=2.1)
    s.link((540, 600), (300, 690), t=2.72, dot=False)    # a line drawn to the next part
    K.ytchannel(s, "Channel Name", "@channelhandle", 300, 690, t=2.88, avatar="assets/media/channel.jpg", count=(0, 400000, 3.7, 1.3))
    K.person(s, "assets/media/guest.mp4", 790, 690, 430, t=5.14, tag="Guest name", origin="a clip the creator supplied")
```

Engine elements (all rectangular): `box` (glass label card), `chip` (accent tag), `term`, `text`, `node` (glowing
circle, takes a picture), `img`, `grid` (thumbnails one by one), `link` (solid / dashed connector), `path` (any
drawn curve), `list` (numbered, blurred until reached), `typed` (glass card being typed), `count`, `raw`. Changes:
`out`, `move`, `hot` (accent colour + light sweep), `sweep`, `dim`.
Kit: `K.card`, `K.person`, `K.ytchannel`, `K.notifs`, `K.gdoc`, `K.saved`, `K.graph`, `K.versus`.

**Timing and motion (the panel edit's rules; the business reel's earlier entrances are NOT used)**
- **Sync to speech.** `t` is the start of the word that names the element (`cut_words.json`). Entrances begin
  0.15 s early so the element has landed on the word. Never earlier than it is mentioned, never late.
- **Build progressively.** Parts arrive one at a time in the order they are said. In a panel stretch something new
  arrives at least every ~3-4 s (the build warns at 4 s).
- **Remove with the narration.** When the speaker leaves an idea its graphic fades (0.25 s) or is replaced. To make
  room, `move` or `dim` rather than piling up.
- **Motion vocabulary**: focus pull in (blur and 92% scale to sharp, 0.45 s); lines and graphs draw (a dot rides
  the front of a graph line); headings write on from the left; numbers tick as a plain counter and take the accent
  colour on landing; text types; the active item lights in the accent colour and a band of light sweeps across it;
  soft blurred fade out. Hard cuts between the two layouts. No bounces, no spins, no slides across the frame, no 3D.

**Layout and colour**
- Heading at y 190; graphics between y 380 and 1190, x 65-1015, centred on x 540 (the build warns outside it).
- Text inside graphics 30-46 px; small tags 22-30; a hero number about 110-120. The caption stays the biggest text.
- **One accent-coloured focal point per moment.** When a new element becomes the point, take the colour off the old
  one (`s.hot(old, t, on=False)`). Positive = green `#2FA65A`, negative = red `#B3261E` only when the speaker
  contrasts good and bad (`K.versus`, `K.graph(col=K.GREEN)`, `s.count(color=K.GREEN)`). Text that sits on an
  accent fill (chips, the heading block, the filled box) uses a dark or white colour chosen for contrast.
- **Headings**: the main font, bold; line 2 on an accent block, or, when it holds an `*emphasised*` word, plain with
  a thin accent underline and the word in the emphasis font (automatic).

**Liquid Glass (restrained, and only on the graphics; the setup answer above sets full, soft or off)**
- Cards stay **rectangular** (corner radius 6-10 px): label boxes, typed cards, chart frames, comparison cards,
  the channel card, the active list row. Glass = a translucent layer that blurs the soft light behind it, a bright
  top edge, a faint inner glow, a drop shadow for depth, and the light sweep when a card becomes active.
- Each scene carries two very faint drifting light orbs behind its graphics (that is what the glass refracts);
  the frame must still read as the dark background with the dot grid. `E.LIGHT = 0.6` tones it down (the `soft`
  answer), `E.scene(a, b, light=False)` removes it, `E.GLASS = False` returns the plain hairline look (the `off` answer).
- **Never glass**: the speaker's video panel, the heading, the section bar, the caption, the accent chips, photos
  and footage (they get a thin edge highlight only).
- **No stacked oval pills.** Only real interfaces keep their own rounded shape (an iOS notification, a phone,
  a Subscribe button), because the real thing is that shape.

**Sound (quiet effects on key reveals; mixed under the voice by the render script)**
- The build writes the cues to `sfx.json`: one soft whoosh for the first graphic of each scene, plus accents that
  components add themselves (a counter's tick and landing, a notification after the first, the tap on a saved
  Reel, typing). `s.hot(i, t, sound=True)` adds a shine for THE key moment of a scene; `E.sfx(t, name)` adds one
  by hand; `E.scene(a, b, sound=False)` silences a scene; `E.SOUND = False` silences the reel.
- **Not a sound on every element**: about 40 per 90 s (the build prints the rate and warns above ~45). Cues under
  a close-up, crowded within 0.3 s, or in the last 0.8 s are dropped automatically.
- **The sounds are the creator's own pack**, played by role from `sfx_map.json` (made at setup with
  `scripts/sfx_probe.py`). The roles are `woosh`, `swish`, `swoosh`, `pop`, `shine`, `shine2`, `accept`, `dtext`,
  `data`; only `woosh` and `pop` are needed, a missing role falls back to the nearest one the pack has. **No pack =
  the reel is delivered with the speaker's voice only**: say so in the report; do not invent sounds.
- Levels: every role is trimmed from its measured peak so whooshes land about -29.5 dBFS and pops about -32.5; the
  speaker's voice peaks near -3.
- **Music is a separate question.** Never assume a track. If the creator says yes and names one:
  `09_render.py <slug> --music "<file>" --music-start <s>` writes a "with music" version as well (bed about 11 dB
  under the voice, 0.4 s fade in, 1.5 s out); deliver both.

`python3 build.py` and read every WARN and REVIEW line; `npx hyperframes lint`; `npx hyperframes snapshot --at
<t,t,...> --no-end --describe false` at each key moment while designing, and open the contact sheet. (Expected lint
warnings: `timeline_track_too_dense` for the caption track and `gsap_repeated_fromto_without_baseline` for
counters, typed text and sweeps.)

## 9. Export

`python3 $S/09_render.py <slug> --draft` for review, then `python3 $S/09_render.py <slug> [--tag v2]`.

| Setting | Value |
|---|---|
| Frame | 1080x1920 (9:16), square pixels |
| Frame rate | the source's (23.976 / 25 / 29.97 / 30), constant |
| Video | H.264 MP4, HyperFrames `--quality high`, SDR Rec.709 |
| Audio | the speaker's original sound from the verified cut, unprocessed, plus the quiet sound effects; AAC 320 kb/s |
| Master | `"<out>/<name> - 9x16[ tag].mp4"`; the same without effects as `"… (no SFX).mp4"` |
| Phone copy | `"… (phone).mp4"`, two-pass H.264 under 30 MB, AAC 160k, faststart: the one to send for a quick look |

## 10. Final visual and audio review (every render, draft and final)

`python3 $S/10_review.py <slug> ["<render>"]`. Every line must be PASS; then open **every** sheet in
`<project>/review/` and check:

Visual
- `ends`: the first frame is already the speaker speaking with the layout in place; the last is not a blink, a
  reach for the camera or a half-faded graphic.
- `switches`: each pair is a clean hard cut; no single-frame flash of the other layout, no graphic showing
  through, caption in the right place for each side.
- `captions` (one tile per caption): every line present and spelled right; one line only; readable at phone size;
  under the chin in close-ups and never on the face; in the panel layout between the graphics and the head,
  touching neither; emphasis in the emphasis font and accent colour (figures in the accent colour, main font);
  nothing clipped.
- `beats` (every heading and graphic just after it lands): each has landed, is spelled right, sits inside the
  graphics area, overlaps nothing and matches what is being said at that moment; nothing stale; one accent focal
  point; glass reads as glass without greying the frame; real photos uncropped; interfaces look like the real
  thing; fonts right (no fallback).
- `cuts`: no BIG jump inside a close-up; no sliver of a dropped take.
- The cut-out edge at full size at three moments (`ffmpeg -ss <t> -i <render> -frames:v 1`): no halo, no missing
  hand, no flicker.
- Watch the draft once at normal speed if a player is available; otherwise read a 2-fps sheet for rhythm.

Audio
- Starts on the first word, ends after the last with the sound complete; offset to the verified cut is 0 ms.
- No clipping; loudness reported (far from -14 LUFS: tell the creator, do not change their sound).
- Sound effects sit well under the voice and land on their reveals; none on a close-up; none masking a word.
- Listen to `W/edit.wav` around any join the verify step or the `cuts` sheet made doubtful.

Fix, re-render, review again until clean. Then give the master's path and the phone copy, and report:
1. length before and after, and what was cut that the creator might want back;
2. each heading and what each graphic shows;
3. **every asset used and where it came from** (from `review.json`), with mock-ups called out;
4. **every piece of wording you wrote** (headings, labels, mock-up text) for the creator to confirm or replace;
5. caption fixes and the emphasised words; the sounds used (or that there was no pack); any warning left;
6. the music question, if not yet answered. Then ask for their notes.

For notes after review: copy `build.py` to `build_vN.py`, edit, re-render with `--tag vN`. The creator compares versions.

## Defaults that are the pack's choices (change when the creator says)
Glass strength and the faint light behind it (`E.LIGHT = 1.0`) · card corner radius 6-10 px · notification size
(880x150, up to 4) · sound on by default with one whoosh per scene · panel geometry, caption sizes and heading
style inherited unchanged from explainer-panel-reel · a neutral grey profile picture until a real one is supplied ·
no watermark · no music.

## Gotchas
- ffmpeg here has no drawtext/subtitles filters: all text is HTML in the composition.
- A font saved as `local` (for example an Adobe Font) only renders while Creative Cloud is running.
  `08_new_project.py` prints a font report: if it says NOT FOUND, tell the creator; never ship the fallback.
- GSAP resets CSS `translate`: elements are positioned by a wrapper and only the inner element is animated. In
  `raw()` HTML do the same.
- The renderer rounds `strokeDashoffset`: drawn lines use `pathLength="1000"` (the helpers do).
- Glass needs something behind it: with `light=False` a glass card on a plain dark background looks like a flat grey box.
- Graphics keep running underneath a close-up; a scene that ends under one is cut, not faded. End a scene (and its
  heading) about 0.15 s before the next one starts, so the outgoing fade and incoming focus pull do not overlap.
- After changing captions, crops, the engine or the profile picture: `08_new_project.py <slug> --refresh` (never
  touches `build.py`).
- A switch time rounded up lands one frame late and shows: `E.full` snaps for you; use `E.fr(t)` for anything else
  that must hit a cut.
- Kit CSS is global to the page: keep class names in `raw()` HTML unique.
- Face finding and the cut-out use macOS tools; the scripts are written for a Mac.

## Dependencies (everything else is inside this skill folder)
`ffmpeg`, `python3` with Pillow, numpy, soundfile, requests, fontTools · `npx hyperframes` (rendering, snapshots,
`remove-background` for the cut-out) · an ElevenLabs key in the shell profile when the transcriber is ElevenLabs.
Not read at run time: explainer-panel-reel or business-short-form-reels (the scripts and engine were copied here).

## Related
`explainer-panel-reel` (the plain panel style) · `business-short-form-reels` (the three-mode split reels) ·
`hyperframes`, `hyperframes-cli`, `hyperframes-animation` (framework rules).
