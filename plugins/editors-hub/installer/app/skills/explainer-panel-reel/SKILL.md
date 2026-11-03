---
name: explainer-panel-reel
description: Edit one raw talking-head video into a polished 9:16 explainer reel in the "panel" style - the video alternates between full-frame close-ups of the speaker and a black frame where their video sits in a rounded panel at the bottom (original background kept) while animations above them explain what they are saying (headings, numbered sections, cards, screenshots, diagrams, connecting lines, progressive reveals). Does the whole job from the raw file - transcript checked against the audio, tight cut (dead space, mistakes, false starts, repeats, set-up and ending footage removed), captions on every word (tight tracking, emphasis words in the creator's emphasis font and accent colour, never stacked), animation build, export and a final visual and audio review. Use whenever the creator hands over a raw talking-head video and says "panel edit", "explainer reel", "the panel style", "me at the bottom with animations on top", "like the reference videos", or asks for a re-render / new version of one. Also for one part alone - only the cut, only the captions, only the animations. Not for half-and-half split reels with glass cards (business-short-form-reels), B-roll edits (broll-stacked-text-edit), whiteboard long-forms or 16:9 YouTube edits (educational-youtube-editor).
---

# Explainer panel reel

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/explainer-panel-reel/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first. Do not start the task, and do
  not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if it exists,
  `~/.claude/creator-profile/notes/explainer-panel-reel.md`. Rules under `## Style overrides` in that notes file win
  over the defaults written below.

"redo my setup" re-runs the interview at any time.

## Your setup

Filled in by setup. To change a line, change the answer (`setup/SETUP.md`), never this text.

| | |
|---|---|
| Creator | @@CREATOR_NAME@@ · @@BRAND_NAME@@ · @@HANDLE@@ on @@PLATFORM@@ |
| What they teach, and to whom | @@NICHE@@ |
| Accent colour | @@ACCENT@@ (@@ACCENT_NAME@@) · panel / card background @@BG@@ |
| Fonts | main: @@FONT_MAIN_NAME@@ · captions: @@FONT_CAPTION_NAME@@ · emphasis: @@FONT_ACCENT_NAME@@ (set @@EMPHASIS_SCALE@@x the caption size) |
| Heading line 2 | @@HEADING_BLOCK@@ (on a block of the accent colour, or plain with an underline) |
| Head above the panel edge | @@POPOUT@@ · slow zoom on close-ups: @@CLOSE_UP_ZOOM@@ |
| Handle watermark | @@WATERMARK@@ |
| Transcriber | @@TRANSCRIBER@@ |
| Finished videos go | @@OUTPUT_RULE@@ (raw footage drive: @@MEDIA_DRIVE@@) |
| Folders | working files `@@WORK_ROOT@@` · HyperFrames projects `@@PROJECTS_ROOT@@` |
| Real material (proof) | @@PROOF_DIR@@ · also search: @@ASSET_DIRS@@ |
| Music | @@MUSIC_RULE@@ (this skill adds no music or sound effects unless asked) |
| How to work | @@WORK_RULE@@ |

One raw talking-head file goes in. A 1080x1920 video comes out that alternates between two layouts:

- **Full frame**: a close-up of the speaker filling the screen, caption under their chin.
- **Panel**: black frame with a faint dot grid; their video in a rounded panel at the bottom with their real
  background visible in it (head and raised hands may rise above the panel's top edge); a heading at the top;
  animations in the space between that build and clear in time with what they say; the caption just above their head.

The look comes from a study of two reference reels. Read `references/reference-study.md` before the first build of a
session: it holds the measurements for layout, pacing and motion. Nothing from those reels is reused (no accent
colour, logos, handles or examples). Everything on screen is the creator's content in the creator's brand.

`S=~/.claude/skills/explainer-panel-reel/scripts` · work dir `W=@@WORK_ROOT@@/<slug>` (small files) · HyperFrames
project `@@PROJECTS_ROOT@@/<slug>-panel` · outputs per the output rule (`@@OUTPUT_RULE@@`; the scripts default to
`"<video folder>/<video name> - Edit/"`, and `01_prep.py` takes another folder as its third argument). Video files are
large: keep the cut, crops and renders beside the source, and render one video at a time. Long steps run in the
background. Every script prints its own usage.

## 1. Inputs

| Input | Required | Notes |
|---|---|---|
| Raw video | yes | One talking-head file, any resolution, 16:9 or 9:16, constant frame rate. If the creator gives a folder and two files could be it, ask once. |
| Supporting footage / images | no | Screenshots, clips, photos, documents they want shown. Copy into the project's `assets/media/`. A screenshot dragged in is meant to be animated in, but ask where it goes. |
| Brand values | yes, set at setup | The accent colour, fonts, emphasis size and heading style are in "Your setup" and are written into every project's `assets/brand.json` by `08_new_project.py`. If one video needs different values (a client's video), write `W/brand.json` with the values **read from the client's brand files** (never eyeball a colour: take the hex from the token file or sample the logo). It overrides the setup for that video. |
| Handle | optional | Drawn as a small watermark only when the creator chose that at setup (`@@WATERMARK@@`). Never guess a handle. |
| Logo | optional | The engine does not draw a logo by itself. If the creator wants one on screen, drop the file into `assets/media/` and place it with `s.img(...)` where a graphic calls for it. |

Real assets beat invented ones. When the speaker mentions a person, a post, a page or a number, look for the real thing
(the proof folder `@@PROOF_DIR@@`, the other asset folders `@@ASSET_DIRS@@`, what the creator supplied) before drawing
a stand-in. Where something had to be invented (a name in a mock-up, a sample line of text), list it in the report.

`python3 $S/01_prep.py "<video>" <slug>` and act on its warnings (variable frame rate needs a constant-rate copy first).

## 2. Transcribe, then check it against the audio

`python3 $S/02_transcribe.py <slug>`: runs the transcriber chosen at setup (`@@TRANSCRIBER@@`) through `scripts/stt.py`.
With ElevenLabs the key is read from the environment or the shell profile, never printed and never asked for in chat.
Do not use any connector's transcribe tool (it costs many times more). Read the whole printed script and
`W/words.txt`. With local transcription the word edges are looser: expect to look harder at the cut in step 3.

The transcript is checked against the audio twice: `04_verify.py` (step 3) transcribes the *edited* audio again and
compares it word for word with what the cut was meant to keep, and you read it yourself: any word that looks wrong for
what the speaker is talking about (a name, a brand, a number) gets confirmed from context or asked about, then fixed
in the captions with `{heard|Shown}`.

## 3. The tight cut

Write `W/drops.json`: `{"words": [[i, j], ...], "secs": [[a, b], ...]}` (word-index ranges from `words.txt`; `secs`
for things that are not words).

Remove:
- **Recording set-up and ending footage**: anything before the speaker starts the piece and after they finish it
  (checking the camera, "okay", reaching to stop the recording).
- **False starts and repeated takes**: when a line is said more than once, keep the LAST complete take and drop every
  earlier attempt in full, including the half-sentence that led into it.
- **Mistakes**: stumbles, a wrong word followed by the right one, "um / uh", restarts, throat clears, asides.
- **Dead space**: the script removes pauses, breaths, the head and the tail itself. Never list them.

Keep:
- **The meaning.** Every sentence must still be a sentence and the argument must still follow. If unsure whether a
  repeat is a mistake or emphasis, keep it. Never reorder, never splice words into a sentence the speaker did not say.
- **Natural pacing.** Default gap between words is 0.12 s. If the result feels breathless, `--gap 0.2`; a pause
  clearly left for effect before a punchline stays (put nothing in `drops` and raise `--gap`, or accept one PAUSE line).
- A mid-video call to action and the end one (drop a CTA only when it is another take of the same slot).

`python3 $S/03_cut.py <slug>` then `python3 $S/04_verify.py <slug>`. Read the EDIT as a script and every MISSING /
EXTRA / CHANGED / PAUSE / REPEAT line; fix `drops.json` and repeat until clean. **The video starts on the first
spoken word and ends right after the last**: head and tail under ~0.25 s. If the last word sounds clipped, re-run with
`--pad-out 0.06` (or more) until its sound has died away. Then `python3 $S/05_render_cut.py <slug>` (background).

From here on every time is **cut-timeline seconds**: `W/edit.txt` (script plus every word's time), `W/cuts.json`
(every join), `python3 $S/cut_times.py <slug>` (the joins with the words either side; `BIG` = a jump a viewer sees).

## 4. Frame the speaker for both layouts

1. `python3 $S/frames.py <slug> <t> <t> ...`: gridded stills at several moments (include one where they lean or
   gesture high). Read off, in source pixels, the centre of the face, the top of the head (hair or hat) and the chin.
2. Write `W/layout.json`: `{"face": {"cx": .., "top": .., "chin": ..}, "popout": true}` (`popout` defaults to the setup
   answer, `@@POPOUT@@`).
3. `python3 $S/06_crops.py <slug> --preview <t> <t> ...` and open each still. Left = close-up, right = panel.
   Check: the caption line sits under the chin on the left and clears the head on the right; the whole head is in
   view; nothing important is cut by the panel's sides. Nudge with `full_dx`, `panel_dx`, `panel_dy`, or the scales.
   Never reframe the footage to make a graphic fit: if the framing is bad, tell the creator and push the graphics.
4. `python3 $S/06_crops.py <slug>` (background; the cut-out takes about 0.1 s per frame).

`popout: true` is the reference look (the head rises above the panel edge). It needs a clean cut-out: if the matte in
the draft shows a halo, flicker or missing fingers, set `"popout": false` (the head then sits inside the panel) and
re-run rather than shipping a bad edge.

## 5. Captions (the whole video, including under graphics)

`python3 $S/07_captions.py <slug>` drafts `W/phrases.txt`; edit it and run again.

- **Every spoken word is on screen once, in order, timed to the speech.** The script refuses a phrases file that
  does not match the verified cut word for word, so captions cannot drift from what is said.
- **One short line, 1-3 words** (the reference reels average about two), changing on the word. Break at the natural
  phrase; never split a number from its unit or a first name from a surname.
- **Type**: the caption font (`@@FONT_CAPTION_NAME@@`), bold, tracking -50 (`letter-spacing: -0.05em`), white, soft
  shadow.
- **Emphasis**: mark the word `*like this*`. It switches to the **emphasis font in the accent colour**
  (`@@FONT_ACCENT_NAME@@`, `@@ACCENT@@`), on the same line, same baseline, inside the normal caption, set
  `@@EMPHASIS_SCALE@@x` larger so it reads the same size. Nothing else about the caption changes. A figure
  (`*400,000*`) stays in the caption font and takes the accent colour: the emphasis font is only for whole words. Use
  it for the word that carries the point: about 3-6 a minute, never two captions running.
- **No stacked captions.** One line only: no multi-line blocks, no enlarged word, no line-by-line reveals. If a
  phrase is too long for one line, split it into two captions.
- **Position.** Full frame: under the chin, on the upper chest (computed from the chin in step 4; never on the face).
  Panel: centred in the gap just above the head, close to the speaker and clear of the graphics. Both are in
  `crops.json` -> `cap`; if the framing changes mid-video, check the caption sheet and adjust.
- Fix mis-heard words with `{heard|Shown}`; capitals and punctuation can be edited directly. Read `W/captions.txt`
  in full after every run and clear every LONG / SHORT line.

## 6. Plan the edit

`python3 $S/08_new_project.py <slug> "<Title>"`, then plan in three passes over `W/edit.txt`:

**a. Modes.** Mark the full-frame windows; everything else is panel.
- Open in panel with the heading writing on and the first graphic arriving in the first second, unless the hook is
  stronger said straight to camera.
- Full frame is for the lines with no graphic to show: a direct statement, a punchline, a transition, the call to
  action. Reference pacing: full frame is 20-30% of the runtime, close-ups last about 1-8 s, panel stretches about
  2-20 s, and there is a close-up at least every ~20 s.
- **Put every switch on an edit cut**, and every BIG cut on a switch (the change of framing hides the jump). A BIG
  cut inside a close-up is an error; small cuts inside a panel stretch are fine. A switch with no cut nearby is
  allowed: the punch-in reads as a cut.

**b. Points.** Break the script into its points. Each gets a heading (`E.heading`) or, when the speaker counts things
off, a numbered section bar (`E.section`). The heading names the point in 4-8 words, title case, and changes when the
point changes.

**c. Graphics.** For each sentence in a panel stretch, decide what would make it clearer to *see*: the thing named
(a screenshot, a post, a profile, a document), the relation described (two boxes and a line), the list about to be
walked through (numbered list, items blurred until reached), the number said (a counter), the quote read (typed into a
card). One idea per scene; each element lands on the word that names it; when the speaker moves on, it goes. Show,
do not repeat: graphics illustrate (a mock-up of the thing, a real interface, a real post) rather than restating the
spoken sentence as text.

Working rule at setup: `@@WORK_RULE@@`. When the rule is to show the plan, give it as a short table (time, mode,
heading, graphic, assets needed) and ask the open questions with `AskUserQuestion` before building: which assets to
use, any wording in headings, and music (never assume a track).

## 7. Build (`build.py` in the project; never edit `index.html`)

`examples/smoke-test-build.py` is a small working example (structure and API only); `engine/panel_engine.py`
documents every call.

```python
E.full([[5.82, 8.06]])                                   # close-up windows (snapped to frames)
E.heading(0.0, 5.7, "Show Them What", "You've *Already Done*")
E.section(10.82, DUR, "02", "Why This?")
with E.scene(0.0, 5.8) as s:                             # everything left fades just before the end
    n = s.node(540, 480, t=1.2, icon="A")
    a = s.box("Strategist", 250, 760, t=2.1)
    s.link((540, 545), (250, 760), t=1.9)                # line drawn from p1 to p2, accent end marker
    s.count(540, 930, 0, 400000, t=4.2)
    s.hot(a, 3.6); s.out(n, 5.0)
```

Elements: `box` (outlined label), `chip` (accent tag), `term` (accent pill), `text`, `node` (glowing circle),
`img` (screenshot / photo / clip card), `grid` (thumbnails one by one), `link` (solid or dashed connector), `path`
(any drawn curve or chart line), `list` (numbered, blurred until reached), `typed` (document card being typed),
`count`, `raw` (your own HTML for a one-off). Changes: `out`, `move`, `hot`, `dim`.

Animation rules:
- **Sync to speech.** `t` is the start time of the word that names the element, from `cut_words.json`. Entrances
  begin 0.15 s early so the element has landed on the word. Never earlier than it is mentioned, never late.
- **Build progressively.** Parts arrive one at a time in the order they are said; a diagram grows, it does not
  appear whole. In a panel stretch something new should arrive at least every ~3-4 s (the build warns at 4 s).
- **Remove with the narration.** When the speaker leaves an idea, its graphic fades (0.25 s) or is replaced; nothing
  stale stays on screen. To make room, `move` or `dim` what is there rather than piling up.
- **Motion vocabulary**: focus pull in (blur and 92% scale to sharp, 0.45 s), lines draw, headings write on from
  the left, numbers tick, text types, the active item lights in the accent colour (`hot`) or takes the list bar. Hard
  cuts between the two layouts. No bounces, no spins, no slides across the frame, no 3D.
- **Layout**: heading at y 190; graphics between y 380 and 1190, x 65-1015, centred on x 540; text inside
  graphics 30-46 px; one accent focal element per moment, the rest white on black. Positive = green `#2FA65A`,
  negative = red `#B3261E` when the speaker contrasts good and bad; otherwise only white and the accent colour.
- **Safe zone**: on a phone the platform's own interface covers the top and bottom of the frame. Keep animations
  inside y 270-1500 (the graphics area, y 380-1190, already is).
- **Headings**: the caption font, bold, tracking -50. Line 2 sits on a block of the accent colour (or carries a thin
  accent underline, per the setup answer `@@HEADING_BLOCK@@`); when it holds an emphasised word (`*word*`), the word is
  in the emphasis font and the line gets the underline instead (an accent word cannot sit on an accent block; the
  engine switches automatically).
- **Figures and money are always set in the main font**, never in the emphasis font.
- **Never crop a person** in a picture: size the card to the asset's shape. Show documents and interfaces as the
  real thing or a simple honest mock-up.
- The caption always carries the spoken words: do not repeat the sentence as on-screen text. Text in graphics is labels.

`python3 build.py` and read every WARN; `npx hyperframes lint`; `npx hyperframes snapshot --at <t,t,...>` at each
change of picture while designing, and open the contact sheet. (Two lint warnings are expected:
`timeline_track_too_dense` for the caption track and `gsap_repeated_fromto_without_baseline` when both a counter and
typed text are used.)

## 8. Export

Preview first. `python3 $S/09_render.py <slug> --draft` renders a fast, low-quality draft; run the review (step 9) on
it and show it before the final render, applying the creator's notes and re-previewing as often as needed, unless the
working rule says to run to the end. Then `python3 $S/09_render.py <slug> [--tag v2]`.

| Setting | Value |
|---|---|
| Frame | 1080x1920 (9:16), square pixels |
| Frame rate | the source's (23.976 / 25 / 29.97 / 30), constant |
| Video | H.264 MP4, HyperFrames `--quality high`, SDR Rec.709 |
| Audio | the original sound from the verified cut, AAC 320 kb/s in the camera file; no processing, no music or effects unless asked |
| Master | `"<out>/<name> - 9x16[ tag].mp4"` |
| Phone copy | `"... (phone).mp4"`, two-pass H.264 under 30 MB, AAC 160k, faststart: the one to hand over for a quick look |

Music, if the creator asks for it, is a separate step after the render: pick the track per the music rule
(`@@MUSIC_RULE@@`), mix it well under the voice (the voice stays untouched), and keep the version without music.

## 9. Final visual and audio review (every render, draft and final)

`python3 $S/10_review.py <slug> ["<render>"]`. Every line must be PASS; then open **every** sheet in
`<project>/review/` and check:

Visual
- `ends`: the first frame is already the speaker talking with the layout in place; the last frame is not a blink, a
  reach for the camera or a half-faded graphic.
- `switches`: each pair shows a clean hard cut between layouts; no single-frame flash of the other layout, no
  graphic showing through, caption in the right place for each side.
- `captions` (one tile per caption): every line of `captions.txt` is there and spelled right; one line only;
  readable at phone size; under the chin in close-ups and never on the face; in the panel layout between the graphics
  and the head, touching neither; emphasis words are in the emphasis font and accent colour (figures in the caption
  font, accent coloured); nothing clipped at the frame edge.
- `beats`: every heading and graphic has landed, is spelled right, sits inside the frame and the graphics area,
  overlaps nothing, and matches what is being said at that moment; nothing stale remains from the previous idea; the
  accent is the creator's accent colour everywhere (no stray colours); fonts are right (no fallback).
- `cuts`: no BIG jump visible inside a close-up; no sliver of a dropped take.
- The cut-out edge in the panel layout: look at full size at three moments (`ffmpeg -ss <t> -i <render> -frames:v 1`):
  no halo, no missing hand, no flicker between neighbouring frames.
- Then watch the draft through once at normal speed if a browser or player is available; otherwise read a 2-fps
  contact sheet of the whole thing for rhythm: something changes every few seconds, no dead stretch.

Audio
- Starts on the first word and ends after the last, with the last word's sound complete (the script checks both).
- In sync: offset to the verified cut is 0 ms (the script reports it); no drift at the end.
- No clipping; loudness reported. If it is far from -14 LUFS, tell the creator; do not change their sound without asking.
- Listen to `W/edit.wav` around any join that the verify step or the `cuts` sheet made doubtful.

Fix, re-render, review again until a pass is clean. Then give the creator the phone copy and the master's path, and
report briefly: length before and after; what was cut that they might want back; each heading and what each graphic
shows; caption fixes and the emphasised words; anything invented or chosen without asking; any warning left.

For notes after review: copy `build.py` to `build_vN.py`, edit, re-render with `--tag vN`, so versions can be compared.

## Default style choices (change when the creator asks)

Panel at x 70-1010, top y 1407, radius 36, running off the bottom · head pops out above the panel edge (setup:
`@@POPOUT@@`) · caption 62 px, panel caption just above the head, close-up caption 150 px under the chin · heading at
y 190, 54 px · line 2 of a heading per the setup answer (`@@HEADING_BLOCK@@`; `block=False` gives the underline for
one heading) · emphasis words `@@EMPHASIS_SCALE@@x` larger than the caption font so they read the same size · slow
zoom on close-ups: `@@CLOSE_UP_ZOOM@@` (`E.ZOOM_FULL = 1.04` turns it on for one video) · no watermark unless the
creator chose it · no music, no sound effects.

Defaults this style avoids: stacked or enlarged captions, 3D, bounces and slides across the frame, an accent fill
behind an emphasised word, the emphasis font for figures.

## Gotchas
- ffmpeg here has no drawtext/subtitles filters: all text is HTML in the composition.
- A font saved at setup as an installed or Adobe font is loaded with `local()`. If `08_new_project.py` reports it NOT
  FOUND (Creative Cloud not running, font deactivated), tell the creator; never ship the fallback face.
- The shipped open-licence emphasis font (Playfair Display Italic) sits in `assets/fonts`; the creator's own font files
  are copied there by `setup/apply_profile.py`.
- GSAP resets CSS `translate`: elements are positioned by a wrapper, and only the inner element is animated. In
  `raw()` HTML do the same.
- The renderer rounds `strokeDashoffset`: drawn lines use `pathLength="1000"` (the helpers do).
- Graphics keep running underneath a close-up; a scene that ends under one is cut, not faded.
- After changing captions, crops or setup answers: `08_new_project.py <slug> --refresh` (never touches `build.py`).
- A switch time rounded up lands one frame late and shows: `E.full` snaps to the frame for you; use `E.fr(t)` for
  anything else that must hit a cut.

## Related
`hyperframes`, `hyperframes-cli`, `hyperframes-animation` (framework rules) · `broll-stacked-text-edit` (same cut
pipeline) · `business-short-form-reels` (the other animated reel style) · `educational-youtube-editor` (16:9
long-form).
