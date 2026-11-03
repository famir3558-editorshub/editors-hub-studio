---
name: cutout-grid-reel
description: Cut-out grid reel - a 9:16 style and a variation of the cut-out backdrop reel. The screen is split into four full images at all times (a 2x2 grid, two on top, two below, no gaps), all four change together when the subject changes (every 5-10 s), the creator is cut out of their talking-head clip at medium size and stays fixed in the exact centre where the four images meet, and small captions (3-6 words) sit on their chest. Does the background removal, the caption and image plan, the image hunt (no watermarks), the layout sheet, the review preview and the final; also builds a grey-silhouette placeholder from a script. Use whenever the creator says "cut-out grid reel", "the four image version", "4x4 collage", "2x2 collage", "four images behind me", "me in the middle with four pictures", "the grid version of the cut-out reel", or hands over a talking-head clip and asks for themselves cut out in the centre of a collage. Not for one full-screen image per idea with the speaker jumping between corners (cutout-backdrop-reel), images above the head with the speaker un-cut (image-cluster-reel), split-screen animation reels or B-roll edits.
---

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/cutout-grid-reel/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first. Do not start the task, and do
  not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if they exist,
  `~/.claude/creator-profile/notes/cutout-grid-reel.md` and `~/.claude/creator-profile/notes/all-styles.md`. Rules under
  `## Style overrides` in those notes files win over the defaults written below.

"redo my setup" re-runs the interview at any time.

## Your setup

Filled in by setup. To change a line, change the answer (`setup/SETUP.md`), never this text.

| | |
|---|---|
| Creator | @@CREATOR_NAME@@ · @@BRAND_NAME@@ · @@HANDLE@@ |
| Fonts | main (hook): @@FONT_MAIN_NAME@@ · captions: @@FONT_CAPTION_NAME@@ |
| Caption size · tracking | @@CAPTION_SIZE@@ px · @@CAPTION_TRACKING@@ em |
| Cut-out width on screen | @@CUTOUT_WIDTH@@ px |
| Opening hook | @@HOOK_RULE@@ |
| Images from the web | @@WEB_IMAGES@@ |
| Never show | @@NEVER_SHOW@@ |
| Real material (own images) | @@PROOF_DIR@@ |
| Transcriber | @@TRANSCRIBER@@ |
| Footage drive | @@MEDIA_DRIVE@@ |
| Finished videos go | @@OUTPUT_RULE@@ |
| Folders | working files `@@WORK_ROOT@@` · projects `@@PROJECTS_ROOT@@` |
| Music | @@MUSIC_RULE@@ · music folder: @@MUSIC_DIR@@ |

The only brand values this style draws are the fonts (hook and captions) and a thin light rim round the cut-out, which
takes the profile's off-white. No logo and no accent colour are involved.

## Review gate (applies to every render this skill produces)

Never render the full-quality final first. Render the **720p preview** (`grid_reel.py preview`), give the creator the
path (or register it in whatever review tool they use), and **wait for their approval** before rendering the final.
Apply their timestamped notes, re-preview, and render the final only once approved. The script writes
`review_events.json` next to the work files: the hook, every image of every set and every caption, each with a stable
id and a start and end time, so notes can point at one of them exactly.

# Cut-out grid reel

Look first at `examples/example.plan.json` (the plan format, with placeholder wording). Scripts:
`S=~/.claude/skills/cutout-grid-reel/scripts` (`grid_reel.py`, `fetch_images.py`, `check_images.py`, `stt.py`).
It is the sibling of the cut-out backdrop reel (one full-screen image per idea, the cut-out jumping between corners):
same cut-out, same caption and hook style, a different layout.

## The look

- **Grid.** Four images on screen **at all times**: top-left, top-right, bottom-left, bottom-right, each a quarter of the
  frame (540 x 960), edge to edge, **no gaps, borders or rounding**.
- **Changes.** **All four change together** on one hard cut. Change when the **subject changes**, which lands every
  **5-10 s**; never one square at a time, never faster just to add movement. Each quarter has a slow 5% push-in over the
  life of the set; nothing else animates.
- **The speaker.** Cut out, **medium size: 540 px wide by default** (head to chest, chest cropped flat), and **fixed in
  the exact centre of the frame, where the four images meet, for the whole video**. They never move or resize. 540 is
  the default because a larger cut-out (720 px) was 20-30% too big and hid too much of each image; the width is a setup
  answer if the creator wants it different.
- **Captions.** On the body: centred on the chest, 140 px above the bottom of the cut-out. The caption font at the size
  and tracking in **Your setup**, white with a thin dark outline, sentence case, no full stops, one line, **3-6 words**,
  replaced in place 0.08 s before the first word. Keep a caption about as wide as the chest; reword the split if one
  runs wide (the script prints `CHECK: caption too wide` past 980 px).
- **Hook (optional).** Black bold text on a white rounded label (the main font), a smaller bracketed line under it, across
  the top two images at y 330 until the first set change. Whether this variation carries one is the setup answer
  `hook_rule`: `ask each time`, `always`, or `never`. The creator writes the hook copy; if they have not, use a plain
  placeholder taken from the first sentence and say it is a placeholder.
- A thin light rim is drawn round the cut-out because dark clothes vanish on dark images (`cutout.rim`, 0 turns it off).

## The cut-out

Background removal runs on the normal footage: `grid_reel.py matte`, about 5 s per second of video. **If something behind
the speaker will not separate cleanly (a dark chair, a plant), KEEP it in on every frame and remove everything else**;
do not add a second mask to chase it out, it flickers. Check 4-6 matte frames on a bright green before building; if the
head or shoulders are eaten or things come and go, show the creator rather than shipping it. `cutout.top` is the source
y just above the head (230 on a typical 1080x1920 clip), `cutout.height` how far down the crop goes (1180 = upper chest
with hands): set them per clip. If the framing is poor (the head close to the top edge, the hands cut off), tell the creator and let them decide; adjust only
the crop numbers, never stretch the footage.

## Choosing the four images

One **set of four per subject**: four different takes on the same idea, not always literal (for "contrast": chess kings,
fire and ice hands, a half-black half-white face, a tightrope walker over a gap). When a section gives examples, give each
example a square (one dollar / a room of cash / a child's crayon horse / an oil-painted horse).
- Each square is a **9:16 portrait crop**: prefer portrait or square pictures, 600 px or more on the short side.
- **The inner corner of every square is hidden behind the speaker** (roughly the 270 x 300 px nearest the centre). Pick
  pictures whose subject sits toward the outside, or aim the crop with `fx` / `fy`, and check the sheet.
- Mix colour and type within a set (a photo, a painting, a dark one, a bright one) so the four read as four.
- **No watermarks, ever** (stock marks, site logos, AI-tool badges, credits). The creator decides what they are
  comfortable publishing (licensing is theirs): list every source in the report, do not lecture. Never stretch an
  image (cover-crop only), and never use a person or subject the creator listed under "never show".
- Their own material first: look in the real-material folder in **Your setup** before searching the web. Where the web
  is allowed, `fetch_images.py` (Bing image search, stock and print-shop sites filtered out) does the search. Pinterest
  and Google Images block automated search; with a browser tool available they work a few searches at a time.

## Steps

1. **Inputs.** The edited 9:16 clip (1080x1920, already tight-cut) and its word timings. No clip = grey silhouette test.
   Word timings: `python3 $S/stt.py clip.mp4 words.json` (uses the transcriber in **Your setup**; the output keeps the
   ElevenLabs shape the script reads). If the clip has no sound, pass `--audio`.
2. **Matte:** `python3 $S/grid_reel.py matte --video clip.mp4 --work W`, then check it. Keep `W` on the footage drive for
   long clips.
3. **Plan.** Captions first (every spoken word once, in order, 3-6 words). Then mark where the subject changes
   (5-10 s apart) and write four image ideas for each.
4. **Find images.** `queries.txt` (`key|search words`), `python3 $S/fetch_images.py queries.txt W/src --n 5`, pick from the
   `sheet_*.jpg` files.
5. **Watermark check (never skip).** `python3 $S/check_images.py W/picks.jpg <chosen files>` and LOOK. Copy keepers to `W/images/`.
6. **Write `plan.json`** (format in the script header and `examples/example.plan.json`; image order is TL, TR, BL, BR).
7. **Layout sheet.** `python3 $S/grid_reel.py sheet --plan plan.json --words words.json --work W [--video clip.mp4]`, look
   at `W/sheet.jpg`. Fix every `CHECK:` line and any square whose point is hidden behind the speaker. Check the fonts:
   the script prints a `WARNING` if a profile font was not found and a fallback was used.
8. **Preview** and hand over: `... grid_reel.py preview ... --out W/review/preview_720.mp4`.
9. **Final after approval:** `... grid_reel.py final --video clip.mp4 --out "<Title> - 9x16 Reel.mp4"`.

Needs `ffmpeg`, Node 22 (the matte runs through `npx hyperframes remove-background`) and Python with `pillow`
(`pip3 install pillow`).

**New layout ideas: show a still mock-up first.** Before any moving sample of a layout variation, show a still example
and wait for a yes; this is the default working rule for this style.

Music and sound effects are not handled by the script: ask whether to add music and which (see **Your setup**, music
rule), and keep the voice natural and clearly above the music.

## Defaults to confirm on the first full reel

The opening hook, the caption size (46 px was picked so the line stays about chest-wide) and the light rim are defaults
without a proven preference behind them. After the first full reel, ask what to change and save the answer as a style
override in the notes file.
