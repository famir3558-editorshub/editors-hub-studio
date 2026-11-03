---
name: visual-essay-reel
description: Edit a raw talking-head video into a 9:16 "visual essay" reel in a BLACK + brand-accent look - the presenter is cut out of their room and sits in the lower half of a matte black frame lit by a controlled glow in the creator's accent colour, and the space above them is an evidence wall that shows exactly what they are talking about (the real post, person, article, study, website, product, statistic, before/after, comparison, B-roll), changing on hard cuts. Evidence-driven, not retention-driven - every visual has a reason. Does the whole job from the raw file - word-timed transcript, tight cut, cut-out, captions, asset hunt (the creator's own files first, then the web), build in HyperFrames, export, review. Use whenever the creator says "visual essay", "visual essay reel", "the black and accent edit", "the evidence edit", "show what I'm talking about", "cut me out and put the receipts above me", gives a reference reel in this style, or asks to analyse a talking-head video for what could be shown on screen. Also for one part alone - only the evidence plan, only the cut-out, only the backdrop, a re-render after notes. Not for the panel and glass explainer styles, the split reels (business-short-form-reels, split-reel) or B-roll edits (broll-stacked-text-edit).
---

# Visual essay reel (black + accent)

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/visual-essay-reel/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first. Do not start the task, and do
  not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if it exists,
  `~/.claude/creator-profile/notes/visual-essay-reel.md`. Rules under `## Style overrides` in that notes file win over
  the defaults written below.

"redo my setup" re-runs the interview at any time.

## Your setup

Filled in by setup. To change a line, change the answer (`setup/SETUP.md`), never this text.

| | |
|---|---|
| Creator | @@CREATOR_NAME@@ · @@BRAND_NAME@@ · @@HANDLE@@ |
| What they teach, and to whom | @@NICHE@@ |
| Accent colour | @@ACCENT@@ (@@ACCENT_NAME@@). Every colour of the look (the light, the near-black, the charcoal, the highlights) is derived from this one value |
| Fonts | main: @@FONT_MAIN_NAME@@ · caption: @@FONT_CAPTION_NAME@@ · emphasis: @@FONT_ACCENT_NAME@@ |
| Title font | @@TITLE_FONT@@ (first line of an opening title) |
| Caption size | @@CAPTION_SIZE@@ px |
| Presenter position | top of the head at y @@HEAD_Y@@, head @@HEAD_PX@@ px tall (frame 1080x1920) |
| Default light | from the @@GLOW_DEFAULT@@ |
| Pace of the cut | gap between sentences @@CUT_GAP@@ s |
| Transcriber | @@TRANSCRIBER@@ |
| Footage drive | @@MEDIA_DRIVE@@ |
| Finished videos go | @@OUTPUT_RULE@@ |
| Folders | working files `@@WORK_ROOT@@` · HyperFrames projects `@@PROJECTS_ROOT@@` |
| Real material (proof) | @@PROOF_DIR@@ |
| Other folders to search for real assets | @@ASSET_DIRS@@ |
| Real assets from the web | @@WEB_ASSETS@@ |
| Never show | @@NEVER_SHOW@@ |
| How far to go alone | @@WORK_RULE@@ |
| Music | @@MUSIC_RULE@@ · music folder: @@MUSIC_DIR@@ |
| Sound effects | @@SFX_DIR@@ |

One raw talking-head file goes in. A 1080x1920 video comes out in which:

- **the backdrop** is a matte black studio with a light in the accent colour entering it (never a flat gradient, never
  another hue);
- **the presenter** is cut out of their room and fills the lower ~48% of the frame, the fixed anchor of every shot;
- **the wall above them** shows the thing they are naming at that moment, and changes when they move on.

**The one principle: make the viewer SEE what is being talked about.** A visual goes up because the words at that
moment name it, prove it or need it explained, never because a few seconds have passed. If a line has nothing to show,
the wall stays empty and the presenter carries it.

Before the first build of a session read `references/reference-study.md` (what the reference style does, and what this
skill changes on purpose) and open `examples/validation/build.py` (a working build, structure only). The skill
recreates the reference's system (hierarchy, pacing, evidence, hard cuts), not its frames.

`S=~/.claude/skills/visual-essay-reel/scripts` · work dir `W=@@WORK_ROOT@@/<slug>` (small files) · HyperFrames project
`@@PROJECTS_ROOT@@/<slug>-essay` · outputs per the output rule (`@@OUTPUT_RULE@@`). Video files are large: the cut,
crops and renders go beside the source (or on the footage drive), one render at a time. Long steps run in the
background. Every script prints its own usage.

## How to work with the creator

How far to go without asking is a setup answer: see "How far to go alone" in **Your setup**.

- **`run to the end, then report` (the pack default).** Find the best real asset yourself, write the few words of
  on-screen text yourself, finish the reel, then report what you used and where each thing came from. Stop only for:
  two files that could be the raw video; **music** (never assume a track; ask separately and deliver without it
  meanwhile, as the setup answer says); anything that would publish or send on their behalf. Show the evidence plan
  (section 7) in the same message as you carry on building.
- **`stop and ask at each stage`.** Stop and wait for a yes after the tight cut (raw length against cut length and the
  notable removals), after the cut-out check (the three full-size stills), after the evidence plan (the table) and
  after the draft render (the review sheets). Within a stage, still do not ask about each asset or wording choice: list
  them at the stop.
- **Nothing on the "Never show" line ever appears**, in a card, a screenshot, a browser capture or the background of a
  photo. Check every fetched asset against it.
- Rights to third-party images and posts are the creator's to manage: they answered how far to go at setup ("Real
  assets from the web"), and every source is listed in the report so they can decide.
- Anything they tell you while working ("never do X", "always Y") goes into
  `~/.claude/creator-profile/notes/visual-essay-reel.md` under `## Style overrides`, dated, the moment they say it.

### Preview first (every render)

Never render the full-quality final first. Render the draft (`09_render.py <slug> --draft`, fast and low quality),
run the review (section 10), and give the creator the draft with the review sheets. Ask them to watch it and send
timestamped notes. Apply the notes (a new `build_vN.py`), re-draft, and render the final only once they approve. In a
batch, gate video 1, then apply its notes to the rest.

## 1-3. Prep, transcript, tight cut

1. `python3 $S/01_prep.py "<video>" <slug>`: act on its warnings (variable frame rate needs a constant-rate copy).
2. `python3 $S/02_transcribe.py <slug>`: transcribes with the transcriber chosen at setup (`scripts/stt.py`; the key,
   if any, is read from the shell profile, never printed, never asked for in chat). Read the whole script and
   `W/words.txt`; fix mis-heard names and numbers later in the captions with `{heard|Shown}`. With the local
   transcriber, word edges are looser: listen to the cut closely.
3. Write `W/drops.json`: `{"words": [[i, j], ...], "secs": [[a, b], ...]}`. Remove set-up and ending footage, false
   starts and repeated takes (keep the LAST complete take), mistakes, fillers and asides; the script removes pauses
   and breaths itself. Keep the meaning (never reorder, never splice), natural pacing (default gap: the setup answer,
   0.12 s) and any calls to action.
4. `python3 $S/03_cut.py <slug>` then `python3 $S/04_verify.py <slug>` until clean; the video starts on the first word
   and ends right after the last. Then `python3 $S/05_render_cut.py <slug>` (background).

From here every time is **cut-timeline seconds**: `W/edit.txt`, `W/cuts.json`, `python3 $S/cut_times.py <slug>`
(`BIG` = a jump a viewer sees).

## 4. Frame the presenter and cut them out

1. `python3 $S/frames.py <slug> <t> <t> ...` (include one where they lean or raise a hand). Read off, in source
   pixels, the centre of the face, the top of the head and the chin.
2. Write `W/layout.json`: `{"face": {"cx": .., "top": .., "chin": ..}}`. Optional: `head_y` (top of the head in the
   frame; default is the setup answer), `head` (head height in px; default is the setup answer), `dx`, `fade` (fade the
   bottom N px into the backdrop).
3. `python3 $S/06_cutout.py <slug> --preview <t> ...` and open each still: the green line touches the top of the
   head, both shoulders are inside the crop, a raised hand is not chopped, the presenter is centred.
4. `python3 $S/06_cutout.py <slug>` (background; about 0.1 s per frame).
5. **Check the cut-out before building** (the script prints the command): three full-size stills at the hair, a
   raised hand and a fast gesture. They must look like themselves in a studio, not like a sticker:
   - hair edges natural, no bright fringe of the old background, no flicker between frames;
   - fingers complete; skin tone unchanged (nothing in this skill grades the face);
   - **furniture the cut-out kept** (a chair back, a desk edge, a mic): a chair behind the shoulders is acceptable; a
     desk edge or a pale wedge at the bottom is not - hide it with `"fade": 150-200` or a higher `head_y`, re-run.
   - If the edge cannot be made clean, do not ship a bad cut-out: delete `cam_fg.webm` and the build shows the
     presenter in a rounded panel with their real background, the wall above. Tell the creator.

The presenter stays the same size and place by default. Change them only when the composition needs it (section 8).
If the source framing is poor (head cut off by the frame, very small in the shot), say so before building and let the
creator decide.

## 5. Captions

`python3 $S/07_captions.py <slug>` drafts `W/phrases.txt`; edit and run again.

- Every spoken word once, in order, timed to the speech; **one short line, 1-3 words**; never split a number from
  its unit or a name.
- Caption font, bold, tracking -50, white with a dark edge, at the caption size from setup (default 54 px):
  deliberately small, because here the evidence is the loudest thing on screen and text supports it.
- Emphasis `*like this*`: the emphasis font in the accent colour, same line. A figure stays in the caption font and
  turns the accent colour (figures are never set in a serif or script face). About 3-6 a minute.
- One fixed line just above the head (it follows the presenter automatically when they are moved or punched in).
  No stacks.

## 6. Find the evidence (before planning, and without asking)

Go through `W/edit.txt` line by line and mark every concrete thing mentioned. For each one get **the real thing**:

| Mentioned | Show |
|---|---|
| a claim | the proof: the screenshot, the result, the number on its real page |
| a person / creator | their photo, profile or a piece of their content |
| a company | its product, website or logo |
| a tweet, post, comment, DM, ad | that actual post or ad |
| a study, article, news story | the page itself, headline and publication visible |
| a statistic | the source page with the figure; a built statistic graphic only if no page exists |
| a website / tool | a screenshot or screen recording of it |
| a product | the product shot |
| a story, a place, a moment | B-roll behind the presenter |
| a comparison | the two things side by side |
| a transformation | before and after, labelled |
| a trend | several real examples at once |
| something abstract | a simple diagram or metaphor, only if it makes the idea easier to understand; otherwise nothing |

Sources, in this order: (1) what the creator supplied; (2) their computer and drives: `python3 $S/find_assets.py
<term> ... [--image|--video]` (searches this skill's assets, the proof folder and other asset folders from setup,
earlier projects, the footage drive, Desktop / Downloads / Pictures, then Spotlight); (3) the web, in the browser, when
"Real assets from the web" allows it: the real post, profile, article or page, captured as a clean screenshot at 2x so
its text stays sharp; (4) a plain stand-in, last, marked `mock=True`, never a made-up name or number that could pass
for real.

Specific beats generic: a real screenshot of the thing beats stock footage of the idea. Copy each file into
`<project>/assets/media/` and pass `origin=` (the path or URL it came from) when you place it: the build lists
anything unrecorded.

## 7. Plan the edit

`python3 $S/08_new_project.py <slug> "<Title>"`. Then write the plan as a table and show it while you build:

| Time | They say | Relation | On the wall | Layout | Asset (source) |
|---|---|---|---|---|---|
| 2.1 | "the channel that went from zero to 400,000" | claim -> proof | the channel's plaque clip + the count | hero+side | plaque clip (client folder) |

Rules for the plan:
- **Each row names its relation** (claim -> proof, person -> image, study -> article, comparison -> side by side...).
  A row whose only reason is "it has been a while" is deleted.
- **On the word.** A visual arrives on the start of the word that names it, never before the speaker gets there.
- **One idea on the wall at a time.** When they move on, it is cut, not left to linger.
- **Density follows the script.** The reference shows something new about every 2 s because its script names
  something every 2 s. A line with nothing to show is `E.solo` and the presenter carries it. The build warns after
  4.5 s without a change: answer the warning honestly (find the thing, or mark it solo), do not fill it.
- **Arrange, never scatter.** More than one asset = a named layout: `pair` (comparison, before/after), `trio`,
  `stack`, `grid`, `hero+side` (main proof + supporting detail), or an overlay (a reply laid over the post it answers).
- **Full attention** for footage that deserves it: `E.backdrop(mode="full")` with `E.me(t, "hidden")` or a corner pose.
- **Open on evidence.** The first frame already has the presenter speaking, the strongest visual up and, if the hook
  needs one, a title (2-4 words a line). A collage that opens the reel can close it too.
- **Jump cuts.** Put an evidence change, a move of the presenter or a punch-in on every `BIG` cut so it reads as
  intended.

## 8. Build (`build.py` in the project; never edit `index.html`)

`examples/validation/build.py` is a worked build (structure only); `engine/essay_engine.py` documents every call.

```python
import essay_engine as E
E.init(ROOT)
E.glow(0, "bottom")                                             # the accent light; change it per chapter, on a cut
E.title(0.0, 2.4, "Borrowed *Proof*", "No Results Yet")
with E.scene(2.4, 6.0) as s:                                    # one idea; everything in it is cut at the end
    a, b = E.slot("hero+side")
    s.card("assets/media/plaque.mp4", a, t=2.9, frame="white", source="Where the clip is from", origin="<path or URL>")
    s.stat("{}", "subscribers", b, t=4.2, count=(0, 400000), size=92)
E.backdrop("assets/media/street.mp4", 6.0, 8.5, mode="top", origin="B-roll library")
E.me(8.5, "close"); E.solo(8.5, 10.2)                           # a straight-to-camera line, wall empty on purpose
E.me(10.2, "center"); E.punch(12.0, 1.1, hold=1.4)
E.build()
```

**On the wall** (`with E.scene(a, b) as s`): `s.card` (THE evidence element: image or clip at its own shape, optional
white mat, `label=`, `source=`), `s.cutout` (transparent PNG, no card), `s.logo`, `s.stat`, `s.quote`, `s.tag`,
`s.text` (a key phrase, 1-4 words), `s.raw` (a one-off diagram); `s.out`, `s.move`, `s.dim`.
**Behind the presenter**: `E.backdrop` (top / full / bottom, optional accent `tint`), `E.collage`.
**In front of them**: `E.title`. **The presenter**: `E.me`, `E.punch`, `E.solo`. **Light**: `E.glow`. **Layouts**: `E.slot`.

### Layers
Backdrop -> evidence -> presenter. The presenter is always in front of the evidence, so the lower edge of a tall card
tucks behind the head: keep what must be read in the upper part of the card. The wall is x 65-1015, y 200-1060; nothing
to be read above y 270 or outside x 65-1015 (platform interface); captions stay above y 1250.

### Evidence treatment
- **Evidence keeps its own look.** A tweet looks like a tweet, an article like an article. The system adds only a
  soft shadow, a corner radius and, where it helps, a white mat (`frame="white"`: screen recordings, app footage,
  photos that would sink into the black) or a hairline (`frame="hair"`: dark screenshots).
- Never crop a person or the text of a screenshot (`fit="contain"` is the default; `cover` is for scenery).
- `source=` puts a small credit above the card when the viewer could not otherwise tell what it is.
- Dark-mode screenshots disappear on this backdrop: capture in light mode or use `frame="hair"`.

### Motion
- Entrances: `how="pop"` (0.18 s scale-in, the default), `"cut"` (instant; use it on an edit cut and for the first
  frame), `"rise"`. Exits are cuts. A card pushes in 3% while it is up (`E.DRIFT`), nothing more.
- No spins, bounces, slides across the frame, transition packs or 3D. The energy is the information changing.
- **The presenter**: `E.me(t, pose)` is a hard change on a cut, for a reason: `left` / `right` to clear a tall or
  centred asset, `corner-left` / `corner-right` over a full-bleed backdrop, `close` for a straight-to-camera line,
  `hidden` when footage deserves the whole frame, back to `center` after.
- **Punch-ins** (`E.punch`) only where the line earns it: a strong claim, a surprise, a punchline, a rhetorical
  question, a major turn, the conclusion. The build warns past about one per 7 s.

### The black + accent backdrop
- The frame reads as **black first**: near-black base with charcoal falloff, a bloom of the accent colour from one
  direction, film grain, a soft vignette. The accent is the light, never half the frame.
- `E.glow(t, where, strength)`: `bottom`, `low-left`, `low-right`, `left`, `right`, `behind`, `top`, `top-left`,
  `top-right`, `off`. The setup answer is where it starts when a build does not say. Change it when the script changes
  chapter, on a cut; `dur=` drifts it slowly instead.
- **Every colour comes from one value**, `accent` (the profile answer; for ONE video that needs a different accent,
  put `{"accent": "#RRGGBB"}` in `W/brand.json` and run `08_new_project.py <slug> --refresh`). The engine derives the
  darker accent, ember, lighter accent, highlight, the glow colour (saturation capped so it never turns neon),
  near-black and charcoal, and prints them at each build. To pin any of them by hand: `"palette": {"o_dark": "#...",
  "o_deep": ..., "o_light": ..., "o_hi": ..., "o_glow": ..., "nb": ..., "ch": ...}` in `brand.json`. A clearly
  saturated accent works best; a very pale or grey one gives a weak glow.
- Dials: `E.GLOW` (overall light, keep <= 1.2), `E.GRAIN` (0.34). Never a flat black, a bright accent field, a 50/50
  split, a visible gradient edge or an animated background.

### Type
Caption font bold (tracking -50) for captions, labels and phrases; the emphasis font for the opening title's first
line (unless setup chose the main font) and for emphasis words; figures always in the caption font, in the accent
colour. Small credits ("source") are the main regular weight at about 62% white. On-screen text is short (names,
numbers, labels, a quoted line, a key phrase) and never repeats the caption. One accent focal point at a time.

### Sound
The speaker's voice only, by default. `sound=True` on an element or `E.sfx(t, name)` adds one quiet cue for a key
reveal (mixed well under the voice by the render script, from the creator's own sound-effects folder; no folder = no
effects); never one per visual. Music is a separate question (see "How to work with the creator").

`python3 build.py` and read every WARN and REVIEW line; `npx hyperframes lint`; `npx hyperframes snapshot --at
<t,t,...> --no-end --describe false` at each change while designing, and open the contact sheet. (Expected lint
warning: `timeline_track_too_dense` for the caption track.)

## 9. Export

`python3 $S/09_render.py <slug> --draft` for review, then `python3 $S/09_render.py <slug> [--tag v2]`
(`--music "<file>" --music-start <s>` only once the creator has named a track; deliver both versions).

| Setting | Value |
|---|---|
| Frame | 1080x1920 (9:16), source frame rate, H.264 MP4, SDR Rec.709 |
| Audio | the original sound from the verified cut, unprocessed; AAC 320 kb/s |
| Master | `"<out>/<name> - 9x16[ tag].mp4"` |
| Phone copy | `"… (phone).mp4"`, under 30 MB: the one to send |

## 10. Review (every render)

`python3 $S/10_review.py <slug> ["<render>"]`: every line PASS, then open every sheet in `<project>/review/`.

- **The evidence test**: with the sound off, can you tell what is being talked about? Does each visual match the words
  at that moment, arrive on its word and leave when the speaker moves on? Is anything there only to fill time?
- **The presenter**: natural edge at full size at three moments (hair, hand, fast gesture), no halo or flicker, skin
  tone as shot, no furniture wedge; clearly the anchor and never smaller than the evidence needs.
- **Evidence**: readable at phone size; screenshots still look like the real thing; no person or text cropped; the
  part the head covers does not matter; nothing readable above y 270; layouts aligned, nothing scattered.
- **Backdrop**: black first, the accent as light; no banding, no visible gradient edge; grain present but quiet.
- **Captions** (`captions` sheet): every line present and spelled right, one line, above the head, readable over
  whatever card is behind it.
- **Cuts and moves** (`switches`, `cuts`): each move of the presenter lands on a cut with no one-frame flash; no
  bare BIG jump.
- **Audio**: starts on the first word, ends after the last, offset to the verified cut 0 ms, no clipping.

Fix, re-render, review again. Then send the phone copy and report: length before and after and what was cut; the
evidence table as built; **every asset and where it came from** (`review.json`), stand-ins called out; every piece of
wording you wrote; lines left bare because nothing real could be found (so the creator can supply something); the
palette used; the music question. For notes: copy `build.py` to `build_vN.py`, edit, re-render with `--tag vN`.

## Defaults of this style

Change only when the creator asks (or a setup answer says otherwise):

- The presenter fills the lower ~48% (head top at y 1000, head 320 px) · light from the bottom · grain 0.34.
- Caption 54 px with emphasis in the emphasis font and accent colour.
- 0.18 s scale-in rather than a pure hard cut · 3% card drift · white mat on footage and photos.
- No sound effects, no music, no watermark unless asked for.
- Typography beyond captions, titles, labels and figures is not specified: use the rules in "Type" above.

Defaults this style avoids: a flat or animated backdrop, a half-and-half split, 3D, spins or bounces, text that
repeats the captions, evidence that is cropped or restyled, a visual that is only there to fill time.

## Gotchas

- ffmpeg here has no drawtext/subtitles filters: all text is HTML in the composition.
- An emphasis font that comes from an Adobe Fonts activation needs Creative Cloud running. `08_new_project.py` prints
  a font check: if a font says NOT FOUND, tell the creator and never ship the fallback.
- The cut-out is 1080 px wide: poses above about 1.3x scale go soft. `close` is the limit.
- The sound rides on `assets/cam.mp4` (the uncut-out crop, invisible under the cut-out). Do not remove it.
- GSAP resets CSS `translate`: elements are positioned by a wrapper and the inner element is animated. In `raw()`
  HTML do the same, and keep class names unique.
- A hard change rounded up lands one frame late and shows: `E.me`, `scene` edges and `how="cut"` snap for you; use
  `E.fr(t)` for anything else that must hit a cut.
- After changing captions, the cut-out, the brand or the engine: `08_new_project.py <slug> --refresh`.

## Dependencies

`ffmpeg`, `python3` with Pillow, numpy, soundfile, requests, fontTools · `npx hyperframes` (render, snapshots,
`remove-background`) · a transcriber (ElevenLabs key in the shell profile, or the local engine; setup decides) · the
creator's fonts in `assets/fonts/` (copied in by setup). Other skills in this pack that share the cut and caption
pipeline: `glass-explainer-reel` and `business-short-form-reels`. Also `hyperframes`.
