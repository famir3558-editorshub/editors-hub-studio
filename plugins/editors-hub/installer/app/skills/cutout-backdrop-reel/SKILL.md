---
name: cutout-backdrop-reel
description: Cut-out backdrop reel - a 9:16 style where the speaker is cut out of their talking-head clip and placed over full-screen images that change with every idea, a text hook sits over an opening collage, the cut-out jumps to a different corner on each backdrop, and small captions (3-6 words) stay in exactly the same spot in the middle. Does the background removal, the plan of ideas, the image hunt (no watermarks), the layout sheet, the review preview and the final; also builds a grey-silhouette placeholder version from a script or transcript before anything is filmed. Use whenever the creator says "cut-out reel", "cutout backdrop", "the cut-out style", "cut me out and put images behind me", "images in the background style", "the green screen style", or hands over a talking-head clip and asks for the version with them cut out over pictures. Not for images above the head with the speaker un-cut (image-cluster-reel), cut-out over a changing grid of images (cutout-grid-reel), split-screen animation reels or B-roll edits.
---

# Cut-out backdrop reel

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/cutout-backdrop-reel/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first. Do not start the task, and do
  not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if it exists,
  `~/.claude/creator-profile/notes/cutout-backdrop-reel.md`. Rules under `## Style overrides` in that notes file win
  over the defaults written below.

"redo my setup" re-runs the interview at any time.

## Your setup

Filled in by setup. To change a line, change the answer (`setup/SETUP.md`), never this text.

| | |
|---|---|
| Creator | @@CREATOR_NAME@@ · @@BRAND_NAME@@ · @@HANDLE@@ |
| What they make, and for whom | @@NICHE@@ |
| Accent colour | @@ACCENT@@ (@@ACCENT_NAME@@), text on it @@ON_ACCENT@@ |
| Fonts | hook and sub-line: @@FONT_MAIN_NAME@@ · captions: @@FONT_CAPTION_NAME@@ |
| Hook label | @@HOOK_LABEL@@ (white label with dark text, or an accent-colour label) |
| Captions | size @@CAPTION_SIZE@@ px, centred at y @@CAPTION_Y@@ |
| Light rim round the cut-out | @@RIM@@ (0 = off) |
| Transcriber | @@TRANSCRIBER@@ |
| Images: own folders first | @@IMAGE_DIRS@@ |
| Images: from the web | @@WEB_IMAGES@@ |
| Never show | @@NEVER_SHOW@@ |
| Review | @@REVIEW_RULE@@ |
| Music | @@MUSIC_RULE@@ · music folder: @@MUSIC_DIR@@ |
| Real material (proof) | @@PROOF_DIR@@ |
| Finished videos go | @@OUTPUT_RULE@@ |
| Folders | working files `@@WORK_ROOT@@` |

The fonts are read from the creator profile at build time (`font_main_bold`, `font_main_regular`, `font_caption`): the
script prints a `FONT:` line for each one and a `NOT FOUND` line if it had to fall back. A fallback is never shipped:
tell the creator and fix the font first.

## Preview first (the review rule)

Never render the full-quality final first. Render the **720p preview** (`cutout_reel.py preview`), show it to the
creator, and wait for their approval before rendering the final (unless the review answer above says to go straight
to the final). Apply their timestamped notes, re-preview, then render the final once approved. Every preview and final
also writes `review_events.json` (the hook, every backdrop, every caption, with stable ids and times) so notes can be
matched to exact items. Rules they give while reviewing go into the notes file under `## Style overrides`.

# How this style works

Scripts: `S=~/.claude/skills/cutout-backdrop-reel/scripts` (`cutout_reel.py`, `fetch_images.py`, `check_images.py`,
`stt.py`). The plan format is in the header of `cutout_reel.py`; a worked structure example is
`examples/example.plan.json` (a reference for structure only, its images are not shipped).

## The look

- **Opening (about the first 4 s, until the first point starts).** The speaker is LARGE at the bottom centre (cut-out
  about 1000 px wide, head top near y 1050) over a **mosaic collage** of 6-8 images about the topic, edge to edge, no
  gaps. The **hook** sits at y 400: bold text in the main font on a rounded label (white with dark text by default, or the
  accent colour), 2 lines, with a smaller white bracketed line under it. The hook leaves on the cut to the first
  backdrop. The creator writes the hook: use their words, or a plain placeholder taken from their first sentence, and say
  it is a placeholder.
- **Backdrops.** ONE full-bleed image per idea, **hard cuts**, a new one every **1.5-3 s**, cut about 0.05 s before the
  phrase it illustrates. Each still gets a slow 5% push-in (the one slow drift; nothing else animates).
- **Cut-out.** After the opening the speaker shrinks to **560 x 480** (head to upper chest, chest cropped flat at the
  bottom) and **jumps to a different corner on every backdrop**: TR, TL, BL, BR. Never the same corner twice in a row,
  never over the subject of the image, never over the caption line. They stay inside y 280-1500 (the reel safe zone:
  platform interface covers the rest). Bring them back large for the close of a full reel.
- **Captions.** One line, **3-6 words**, sentence case, no full stops, in the caption font with a thin dark outline,
  centred at the caption position above, replaced in place 0.08 s before the first word. They never move.
- A thin warm-white rim is drawn round the cut-out because dark clothes and hair vanish on dark backdrops
  (`cutout.rim` in the plan, 0 turns it off).

## The cut-out (the rule)

Background removal runs on the normal footage (no green screen needed): `cutout_reel.py matte`, about 5 s per second of
video, through `npx hyperframes remove-background`. **If something behind the speaker will not separate cleanly (a dark
chair, a coat rack), KEEP it in the cut-out on every frame and remove everything else.** An object that is always there
is fine; one that flickers in and out is not. So the matte is used as it comes: do not add a second person-only mask to
chase the object out (it flickers).

**Check the matte before building:** pull 4-6 frames from `matte.webm` (decode with `-c:v libvpx-vp9`) onto bright
green and look. Fine: a kept chair, soft edges on fast hands. Not fine: head or shoulders eaten, big chunks of room left
in, anything that comes and goes. If it is not fine, say so and show the creator rather than shipping it.

Filming advice to pass on when asked: a plain wall, nothing dark touching the outline, a top that is not black.
`cutout.top` in the plan is the source y just above the head (250 is a typical starting value for a seated talking-head
clip): set it per clip so the head is not cropped and the small cut-out ends at the upper chest. Never stretch the
footage: the crop is scaled uniformly.

## Choosing backdrops

Show the idea, **not always literally** (chess kings for "contrast", a tightrope walker for "let the gap do the work",
a child's crayon horse then an oil-painted horse for "amateur versus professional"). The image fills a 9:16 frame, so
prefer **portrait or square** pictures at 1000 px or more on the short side; a landscape picture only works if the
subject survives a narrow centre crop (use `fx` / `fy` to aim the crop). Dark or busy images are fine, the captions
have an outline. Vary colour and type from one backdrop to the next. Short video clips as backdrops are a possible
extension; the script takes stills only, so ask before adding clips.

**No watermarks, ever**: no stock mark, site logo, AI-tool badge or photographer credit. The creator handles licensing
of what they choose; do not raise it. Real examples over invented ones, and nothing on the "Never show" line.

Where to look, in order: the creator's own image folders (see **Your setup**), then, if the web answer allows it,
`fetch_images.py` (Bing image search with stock and print-shop sites filtered out). Pinterest and Google Images block
automated search; if a logged-in browser tool is connected, searching there works a few searches at a time.

## Steps

1. **Inputs.** The edited 9:16 clip (1080x1920, already tight-cut) and its word timings. Word timings come from
   `python3 $S/stt.py clip.mp4 words.json` (the ElevenLabs shape, whichever transcriber is set; check the words against
   what is said). A clip that is not 1080x1920 must be reframed first, never stretched. For a placeholder test: just a
   script or transcript with timings (no `--video` = grey silhouette). A sample is 15-20 s; ask how long if unclear.
2. **Matte** (real footage): `python3 $S/cutout_reel.py matte --video clip.mp4 --work W`, then check it (above). Put `W`
   on the drive with the most free space for long clips.
3. **Plan of ideas.** Captions first (every spoken word once, in order, 3-6 words each). Then one backdrop per idea with
   its cut time, plus 6-8 collage ideas for the opening.
4. **Find images.** The creator's own folders first. For web search: `queries.txt` (`key|search words`, 1-2 per idea,
   add "vertical" where it helps), run `python3 $S/fetch_images.py queries.txt W/src --n 5`, look at the `sheet_*.jpg`
   files and pick.
5. **Watermark check (never skip).** `python3 $S/check_images.py W/picks.jpg <chosen files>` and LOOK at it: marks do
   not show on the small sheets. Also check the pixel size of each pick. Copy the keepers to `W/images/`.
6. **Write `plan.json`** (format in the script header and the example).
7. **Layout sheet.** `python3 $S/cutout_reel.py sheet --plan plan.json --words words.json --work W [--video clip.mp4]`,
   look at `W/sheet.jpg`. Fix every `CHECK:` line, any cut-out sitting on the subject of an image, and any crop that
   lost the point of the picture.
8. **Preview** and show it: `... cutout_reel.py preview ... --out W/review/preview_720.mp4`.
9. **Final after approval:** `... cutout_reel.py final --video clip.mp4 --out "<Title> - 9x16 Reel.mp4"`, delivered to
   the output folder (`@@OUTPUT_RULE@@`).

Music and sound effects are not handled by the script: follow the music answer in **Your setup** (ask whether and
which, or add a favourite and say which), and keep the voice natural and clearly above the music.

## Defaults this style avoids (change only if the creator asks)

- A second person-only mask to chase a chair or object out of the cut-out (it flickers).
- The cut-out in the same corner twice in a row, or over the subject of the image or the caption line.
- Captions that move, wrap onto two lines or run over 6 words.
- Any image with a watermark, stock mark or credit.
- Video clips as backdrops (stills only unless the creator asks).

## Status

The look and the matte rule are the pack's default style. Unconfirmed until the first full reel is reviewed: the
caption font and size, stills only for backdrops, the light rim. After the first full reel, fold the creator's notes
into `~/.claude/creator-profile/notes/cutout-backdrop-reel.md` under `## Style overrides`.
