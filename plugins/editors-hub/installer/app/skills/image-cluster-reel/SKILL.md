---
name: image-cluster-reel
description: Image-cluster reel - a 9:16 talking-head style where the creator sits in the lower half of the frame, clusters of found images (metaphors, memes, abstract or surreal art, diagrams, a quote screenshot or a person they name) pop on above their head and change every few seconds, and tiny left-aligned captions sit beside their chin. Does the image plan, the image hunt (no watermarks, ever), the layout, the captions, a layout sheet, the review preview and the final; also builds a grey-silhouette placeholder version from a script or transcript before anything is filmed. Use whenever the creator says "image cluster reel", "the images above my head style", "images around me", "the collage style with the small captions", "do the silhouette test with this script", or sends a clip framed low with headroom and asks for images and captions. Not for big stacked captions (fitted-stacked-captions), split-screen animation reels, B-roll edits or the panel styles.
---

# Image-cluster reel

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/image-cluster-reel/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first. Do not start the task, and do
  not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if it exists,
  `~/.claude/creator-profile/notes/image-cluster-reel.md`. Rules under `## Style overrides` in that notes file win over
  the defaults written below.

"redo my setup" re-runs the interview at any time.

## Your setup

Filled in by setup. To change a line, change the answer (`setup/SETUP.md`), never this text.

| | |
|---|---|
| Creator | @@CREATOR_NAME@@ · @@BRAND_NAME@@ · @@HANDLE@@ |
| What they teach, and to whom | @@NICHE@@ |
| Caption font | @@FONT_CAPTION_NAME@@ (white, a regular or medium weight reads best at this size) |
| Caption size and position | @@CAPTION_SIZE@@ px · left edge x @@CAPTION_X@@ · top y @@CAPTION_Y@@ (on a 1080 x 1920 frame; `plan.json` can override per reel) |
| Kinds of image | @@IMAGE_TYPES@@ |
| Where to look for images | @@IMAGE_SOURCES@@ |
| The creator's own image folders | @@IMAGE_DIRS@@ · proof folder: @@PROOF_DIR@@ |
| Never show | @@NEVER_SHOW@@ |
| Review | @@REVIEW_RULE@@ |
| Transcriber | @@TRANSCRIBER@@ |
| Music | @@MUSIC_RULE@@ · music folder: @@MUSIC_DIR@@ |
| Finished videos go | @@OUTPUT_RULE@@ |
| Footage drive | @@MEDIA_DRIVE@@ |
| Working files | `@@WORK_ROOT@@` |

The scripts read the caption font and the caption defaults straight from the profile, so this table is for you to
read, not something the code needs.

> **REVIEW GATE.** The default (see "Review" above): do NOT render the full-quality final first. Render the **720p
> preview** (`cluster_reel.py preview`), show it to the creator, ask for timestamped notes, apply them, re-preview, and
> render the final only once they approve. The script writes `review_events.json` next to the working files: every
> image and caption with its start and end time and a stable id, so a note such as "swap the image at 0:07" maps to a
> line. If the creator's answer to "Review" says they want the final straight away, do that, and still look at the
> layout sheet first.

Scripts: `S=~/.claude/skills/image-cluster-reel/scripts` (`cluster_reel.py`, `fetch_images.py`, `check_images.py`,
`make_words.py`, `stt.py`). A structure example of `plan.json` is in `examples/structure.plan.json` (its images are
not shipped; it is only there to show the format and the arrangements).

## The look

- **Framing (this is a filming requirement).** The speaker must be in the LOWER half of the 9:16 frame with clear space
  above their head: top of the head at about 45% of the height (y of about 860 on 1080x1920). The images live in that
  headroom. If a clip has them centred or high, the images would land on their face: **never cover the face, and never
  scale or shift the footage yourself to make room.** Tell the creator plainly what you see (show a frame with the
  head line drawn on), and let them choose: re-film or re-frame it themselves, accept a build with the image band
  compressed higher and smaller (`imageTop` / `imageBottom` in `plan.json`), or accept fewer, smaller images. Then
  build what they chose.
- **Images.** Above the head, inside **y 270 to 830** (the platform interface covers the area above 270, the hair line limits the bottom). **1 to 3 at a time**, each **300-540 px wide**, mixed shapes (square, portrait, landscape), different sizes in
  the same cluster. Arrangements to rotate through: one alone (bigger); a small one beside a big one; two overlapping
  at a corner; three with the middle one on top of both; two on one side overlapping from the bottom. Square corners,
  **no border, no shadow, no rounding, no animation**.
- **Timing.** Each image **hard-pops** on, one at a time, on the phrase it belongs to (usually 1-2 s apart). The whole
  cluster is replaced on a hard cut when the thought changes: a new cluster every **3-5 s** (never longer than about
  6 s).
- **Captions.** The caption font at the caption size above, white, **lower-case, no punctuation** (keep the capital on
  "I" and on names), **left-aligned**, **1-3 short lines of 3-5 words**, shown as a block that is replaced by the next
  block (not word by word), 0.1 s before the first word. Position: beside the chin on the side with the most clear
  space (default x and y from "Your setup"), or centred under the chin if neither side is clear. Always above y 1250
  so the platform's interface does not cover them.

## Choosing images (the part that makes or breaks it)

Depict what the speaker is saying **without being literal**. For each thought ask "what picture gives the feeling or
the idea?", not "what is the noun?". Mix these types across a reel (the creator's "Kinds of image" answer says which
they want; if it names only some, use only those):
- **Metaphor / surreal or abstract art** (a door opening into clouds for "opportunities", a painting of two figures
  with covered faces for "not seeing").
- **Memes** people recognise (a "not me turning 26" cake; a man on his phone missing a whale behind him for "it flies
  right by you"). Skip this type if the creator's answer excludes memes.
- **A known experiment, diagram or sketch** that carries the idea (the invisible gorilla test; a "frequency illusion"
  doodle).
- **A quote screenshot or the person**, only when the speaker quotes or names someone.
A literal picture is fine now and then when the line is itself an image (a red car), but pair it with a non-literal
one. Avoid stock-photo looks, corporate illustrations and anything that reads as an advert. Nothing from the
"Never show" list ever goes on screen.

**No watermarks, ever**: no stock watermark, site logo or photographer credit on any image, and the skill never adds
one of its own. Image rights are the creator's to manage (they decided this at setup): do not raise licensing again,
but never use a picture that carries someone else's mark.

**Where to look.** Start from the creator's own image folders and proof folder when the idea is theirs (a real result,
a real screenshot). For found images, follow "Where to look for images" in your setup. From this machine, automated
search hits walls: Pinterest in the built-in browser serves a couple of searches then blank pages; Google Images
shows its robot check (never try to pass it). So: (1) if the Claude in Chrome extension is connected, search
Pinterest there, in the creator's own logged-in Chrome, a few searches at a time; (2) otherwise use `fetch_images.py`
(Bing image search with stock and print-shop sites filtered out). `site:pinterest.com` on Bing returns junk: do not
use it.

## Steps

1. **Inputs.** Either the edited 9:16 clip + its word timings, or (placeholder test) just a script or transcript with
   word timings. Word timings from a clip: `python3 $S/make_words.py clip.mp4 W/words.json` (uses the transcriber from
   your setup). With a script and no audio, estimate timings at about 3 words a second and say the timing is
   estimated.
2. **Plan the thoughts.** Split the transcript into thoughts of 3-5 s. For each: 1-3 image ideas (types above) and
   the moment each one should pop (the phrase it illustrates).
3. **Find images.** Write `queries.txt` (`key|search words`, 1-2 queries per image idea), run
   `python3 $S/fetch_images.py queries.txt W/src`, look at the `sheet_*.jpg` files and pick. (Or search in Chrome as
   above, or take from the creator's own folders.)
4. **Watermark check (never skip).** `python3 $S/check_images.py W/picks.jpg <chosen files>` and LOOK: thumbnails hide
   watermarks. Replace anything marked; crop only if the mark is in a plain border. Copy the keepers to `W/images/`.
5. **Write `plan.json`** (format in the script header and `examples/structure.plan.json`): caption blocks in order,
   clusters with each image's file, pop time, x, y, width and z. Captions must contain every spoken word once, in
   order.
6. **Layout sheet.** `python3 $S/cluster_reel.py sheet --plan plan.json --words words.json --work W [--video clip.mp4]`
   then look at `W/sheet.png`. Fix every `CHECK:` line and anything that crowds the head or repeats the same
   arrangement twice in a row.
7. **Preview** and show it for review: `... cluster_reel.py preview ... --out W/review/preview_720.mp4`
   (no `--video` = grey silhouette on dark grey; `--audio` to add or replace sound).
8. **Final after approval:** `... cluster_reel.py final --video clip.mp4 --out "<Title> - 9x16 Reel.mp4"`, saved
   where the output rule in your setup says.

Rendering needs Google Chrome (or Chromium; set `CHROME=<path>` if it is somewhere unusual) and ffmpeg. The frames are
drawn in headless Chrome and laid over the clip, so the footage itself is never re-scaled.

## Status

The placeholder (silhouette) path and the real-footage path both run. Sound is not handled here: the clip's audio is
passed through untouched and the voice is never filtered. If music is wanted, follow the music answer in "Your setup"
and keep it well under the voice. After the first real reel, write the creator's notes into
`~/.claude/creator-profile/notes/image-cluster-reel.md` under `## Style overrides`.
