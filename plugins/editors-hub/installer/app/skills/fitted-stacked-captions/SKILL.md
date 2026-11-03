---
name: fitted-stacked-captions
description: Fitted stacked captions - a 9:16 caption style where one emphasised word per caption is set big in the accent colour and the emphasis font, and the other words, in the caption font bold, are fitted tightly around its letter shapes (tucked into the gaps above and below it); captions with no good emphasis are one plain line of 3-5 words. Words pop on one at a time, just BEFORE they are spoken. No commas. Use whenever the creator says "fitted captions", "stacked captions", "the stacked caption style", "big word with small words fitted around it", "put those captions on this reel", or asks for this caption style on a reel, a cut or inside another edit skill. Does the captions only (plan, layout sheet, preview, final or a transparent overlay); the cut, B-roll, graphics and music belong to the edit skills. On first use it asks a short series of setup questions (accent colour, fonts) before doing anything.
---

# Fitted stacked captions

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/fitted-stacked-captions/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first. Do not start the task, and do
  not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if it exists,
  `~/.claude/creator-profile/notes/fitted-stacked-captions.md`. Rules under `## Style overrides` in that notes file
  win over the defaults written below.

"redo my setup" re-runs the interview at any time.

## Your setup

Filled in by setup. To change a line, change the answer (`setup/SETUP.md`), never this text.

| | |
|---|---|
| Creator | @@CREATOR_NAME@@ · @@BRAND_NAME@@ · @@HANDLE@@ |
| Anchor word colour | accent @@ACCENT@@ (@@ACCENT_NAME@@) |
| Anchor word font (emphasis font) | @@FONT_ACCENT_NAME@@ |
| Fitted words font (caption font, bold) | @@FONT_CAPTION_NAME@@ |
| Sizes on a 1080-wide frame | anchor @@ANCHOR_PX@@ px · fitted words @@SMALL_PX@@ px (plain captions +4 px) |
| Words appear | @@LEAD_SECONDS@@ s before they are spoken |
| Lowest line the captions may reach | y @@BOTTOM_LIMIT@@ on a 1920-tall frame |
| Review | @@REVIEW_RULE@@ |
| Transcriber | @@TRANSCRIBER@@ |
| Finished videos go | @@OUTPUT_RULE@@ |
| Folders | working files `@@WORK_ROOT@@` |

Script: `S=~/.claude/skills/fitted-stacked-captions/scripts/fit_captions.py`. Example plan: `examples/example.plan.json`
(structure only: never reuse its wording).

## What the style is

- **One anchor word per caption.** The word you would stress when saying the line (one word, two at most) is set in the
  **emphasis font, in the accent colour, at the anchor size** (195 px by default on a 1080-wide frame).
- **Everything else is fitted around it** in the **caption font, bold, at the small size** (48 px by default, tracking
  -0.05 em, white). Words before the anchor tuck into the dips of its top outline (a short word sits between two
  letters of the anchor, with the earlier words resting on top); words after it tuck under, around descenders. Lines
  sit about 5 px from the letters and may touch or overlap them. It always reads top to bottom, left to right.
- **Plain captions.** A caption with no anchor is ONE line of the caption font bold (small size + 4 px), **3 to 5
  words**, same position.
- **Word by word, early.** Each word pops on by itself (hard pop: no fade, slide or scale) the lead time before it is
  spoken, so the viewer reads just ahead of the voice. Words hold; the whole caption clears when the next caption's
  first word appears. Words never move once placed.
- Soft drop shadow only. No boxes, outlines or other colours.

## Rules of the style (all enforced or warned by the script)

1. **No commas, anywhere.** The script strips them. Full stops (and ? !) stay.
2. **Only stack where there is real emphasis.** Most captions in a reel may be plain; the anchor word must be worth it.
3. **If the anchor does not fit well, do not force it.** The bad case: several small lines piled up with the big word
   just sitting at the bottom. Make those words plain captions of 3-5 words instead. Judge this on the layout sheet:
   a good stack has at most two short lines on either side of the anchor.
4. **A caption never ends on the first word of the next sentence** (never "...failing. I"). Start the next caption
   with it.
5. **Plain captions are 3-5 words, one line, every time.**
6. Break captions at natural phrase ends; the anchor usually sits in the middle or at the end of its caption.
7. Figures and currency are never set in the emphasis font when it is a serif (a number cannot be the anchor: keep it in
   a plain caption); captions stay inside the reel safe zone (above the bottom limit in `## Your setup`, and below the
   speaker's chin).

## Steps

1. **Inputs.** The EDITED 9:16 video (after the tight cut) and word timings for that edit
   (`[[start, end, "word"], ...]`; a word list from the transcriber also works). If there is no transcript yet,
   transcribe the edit first: `python3 ~/.claude/skills/fitted-stacked-captions/scripts/stt.py edit.mp4 words.json`
   (uses the transcriber saved in the profile; the output has the ElevenLabs word-list shape the script reads).
   Transcribe the EDIT, not the raw file: the timings must match the cut.
2. **Position.** Grab a still and find the speaker's chin. Set `cy` (the vertical centre of the captions) about
   130-170 px under the chin and keep the block above the bottom limit. A caption can override with its own `"cy"`.
3. **Write `plan.json`** in the work folder:
   ```json
   {"cy": 1125, "captions": [
     {"id": "cap00", "pre": "The one thing that kept", "em": "clients", "post": "from signing up"},
     {"id": "cap01", "pre": "was a price they"},
     {"id": "cap02", "pre": "never really", "em": "understood"}
   ]}
   ```
   `pre` = words before the anchor, `em` = the anchor, `post` = words after. No `em` = plain caption. Every spoken
   word must appear exactly once, in order (the script checks the text against the transcript and stops at the first
   mismatch). Keep ids stable between re-renders so review notes stay attached. Guide: `pre` up to about 5 words,
   `post` up to about 3.
4. **Layout sheet first.** `python3 $S sheet --plan plan.json --words words.json --work W` then LOOK at `W/sheet.png`
   (more than 16 captions make `sheet2.png` and so on). Fix any `RULE:` lines it prints, and turn any awkward stack
   into plain captions (rule 3). Repeat until every tile is clean.
5. **Preview** (720p):
   `python3 $S preview --plan plan.json --words words.json --work W --video edit.mp4 --out W/review/preview_720.mp4`
   (`--audio voice.wav` if the video file has no sound). The script also writes `W/review_events.json`: one entry per
   caption (`id`, `t0`, `t1`, `text`) so notes can point at a caption by id.
6. **Final.** Follow the review setting in `## Your setup`. With "preview first, wait for approval" (the default):
   do NOT render the full-quality final first. Give the creator the preview, ask for timestamped notes, apply them
   (edit the plan, re-run `sheet` and `preview`), and render the final only once they approve. Otherwise render
   the final straight after the layout sheet is clean. Same command with `final`. Inside another edit skill use
   `overlay` instead (below).

## Using it with the reel skills

This skill is a caption layer. It never cuts, never adds B-roll or graphics, so it sits on top of an edit that already
exists.

- **On a finished 9:16 reel** (the creator hands over a cut or an export and wants this caption style): run steps 1 to
  6 as written, with the finished video as `--video`.
- **Inside another reel skill** (`business-short-form-reels`, `personal-short-form-reels`, `explainer-panel-reel`,
  `broll-stacked-text-edit`, `split-reel`): build the reel with that skill but leave its own captions out (its
  caption layer is the thing this skill replaces), transcribe the final tight cut, then run `overlay`:
  `python3 $S overlay --plan plan.json --words words.json --work W --out W/captions.mov`. The result is a transparent
  ProRes 4444 `.mov` the length of the video, at 30 fps unless `--video` is given (pass `--video` so the frame rate
  matches). Composite it as the topmost layer of the host skill's own render, or over its finished render with
  `ffmpeg -i reel.mp4 -i captions.mov -filter_complex "[0:v][1:v]overlay=0:0:eof_action=repeat" ...`.
- **Where the captions sit** depends on the host layout: read the host skill's caption position (under the chin on a
  full-frame close-up, just above the head in a panel layout) and set `cy` per caption. A stack is taller than a
  one-word caption (the anchor alone is about 150 px tall): keep the host's pills, cards and graphics off that block,
  or move the graphic.
- **Moments where another layer covers the speaker** (full-screen animation, a B-roll window): the captions can stay
  on top, but check the sheet against the actual frames there; the stack must not sit over the graphic's text.
- **Styles with their own small captions** (`image-cluster-reel`, `cutout-backdrop-reel`, `cutout-grid-reel`,
  `depth-ui-reel`) are built around a different caption size and spot. Use this skill on them only if the creator asks,
  and then plan `cy` and `small` for that layout.
- Never run two caption layers at once: switch the host's captions off.

## Tuning (plan.json keys)

`lead` (seconds early), `em` (anchor px; shrinks by itself only if the word is wider than the frame), `small`,
`gap` (px between the lines and the letters, 5), `maxBottom`, `accent` (a hex, for a one-off colour), `trackSmall` and
`trackAnchor` (letter-spacing in em: -0.05 and -0.03 suit bold sans and an italic serif; open them a little for a
looser font). The defaults come from the setup answers. The spacing and sizes above are the default
look: change them only when the creator asks, and write a lasting change under `## Style overrides` in the notes file.

## Notes

- **Fonts.** The anchor and the fitted words each load from the font source saved in the profile (a font file in the
  skill's `assets/fonts/`, or an installed font found by name; an Adobe font is found in the Creative Cloud sync
  folder, so Creative Cloud must be running). If a font fails to load the script stops before drawing anything and
  says which one: it never silently ships a fallback. The default emphasis font is the Playfair Display Italic that
  ships in `assets/fonts/`.
- **Layout** is done in headless Chrome on a canvas: the script measures the anchor word's outline and slides each
  fitted line to the deepest spot it fits. It tries every way of breaking the `pre` / `post` words into lines and
  keeps the most compact. It needs Google Chrome (or `CHROME=/path` set), ffmpeg and ffprobe.
- The video must be 9:16 for `preview` and `final`; the layout is always worked out on a 1080x1920 canvas.
- Assets the original style used and this template does not ship (a layout contact sheet, the creator's own footage)
  are not needed: the script draws everything from the plan and the profile.
