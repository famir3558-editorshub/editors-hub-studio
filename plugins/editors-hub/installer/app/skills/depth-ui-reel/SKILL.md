---
name: depth-ui-reel
description: Depth UI reel - a 9:16 business reel style in which the creator stays full frame for the WHOLE reel (no split screen, no full-screen animation, no B-roll), real interfaces (YouTube video grids, channel cards, Instagram reel grids, channel shelves) float BEHIND their head through their cut-out, simple glowing icons and counters sit round them, small 1-3 word captions sit on their chest with the odd emphasis word in a big contrasting font, the camera punches in and out on sentence cuts, and everything arrives and leaves on a fast blur. No head sticker and no cursor. Built in HyperFrames from the business short-form reels skill's tight cut and matte. Use whenever the creator says "depth UI reel", "graphics behind my head the whole way", "the full-frame style with the interfaces behind me", "interfaces floating behind me", or hands over a talking-head clip and asks to be kept full frame with real interfaces behind them. Not for the three-mode business reels (business-short-form-reels), panel or glass explainer reels (glass-explainer-reel and its panel sibling), cut-out backdrop or grid reels (cutout-backdrop-reel, cutout-grid-reel), or B-roll edits (broll-stacked-text-edit). On first use it asks a short series of setup questions before editing anything.
---

# Depth UI reel

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/depth-ui-reel/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first. Do not start the task, and do
  not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if it exists,
  `~/.claude/creator-profile/notes/depth-ui-reel.md`. Rules under `## Style overrides` in that notes file win over the
  defaults written below.

"redo my setup" re-runs the interview at any time.

## Your setup

Filled in by setup. To change a line, change the answer (`setup/SETUP.md`), never this text.

| | |
|---|---|
| Creator | @@CREATOR_NAME@@ · @@BRAND_NAME@@ · @@HANDLE@@ (@@PLATFORM@@) |
| What they teach, and to whom | @@NICHE@@ |
| Colours | accent @@ACCENT@@ (@@ACCENT_NAME@@) · background @@BG@@ · text @@PAPER@@ |
| Fonts | main: @@FONT_MAIN_NAME@@ (every figure and label) · emphasis: @@FONT_ACCENT_NAME@@ (the few key words, never numbers) · captions: @@FONT_CAPTION_NAME@@ |
| Transcriber | @@TRANSCRIBER@@ |
| Working style | @@WORKING_STYLE@@ |
| Folders | working files `@@WORK_ROOT@@` · HyperFrames projects `@@PROJECTS_ROOT@@` · finished reels: @@OUTPUT_RULE@@ |
| Real material (proof) | @@PROOF_DIR@@ · footage drive: @@MEDIA_DRIVE@@ |
| Real assets from the web | @@WEB_ASSETS@@ |
| Never show | @@NEVER_SHOW@@ |
| Music | @@MUSIC_RULE@@ (library: @@MUSIC_DIR@@) · sound effects: @@SFX_DIR@@ |
| Captions | @@CAPTION_SIZE@@ px, top edge at y @@CAPTION_Y@@, emphasis words @@EMPH_SIZE@@ px |
| Camera | strongest punch-in x@@PUNCH_MAX@@ · background dim @@DIM_LEVEL@@ |
| Head box (at scale 1, in the 1080 x 1920 frame) | x0 y0 x1 y1 = @@HEAD_BOX@@ |

**HyperFrames only.** The reel is built and rendered with HyperFrames (`npx hyperframes`). Do not switch to another
motion-graphics tool part-way. Engine: `engine/depth_engine.py`. Worked example: `examples/worked-example/build.py`
(structure and API only; its words, figures and images are placeholders).

## The look

- **One mode.** The creator full frame from first frame to last. No split screen, no full-screen animation, no B-roll.
- **Depth.** Layers, bottom to top: their footage, a dim over the background, graphics BEHIND them, their cut-out,
  graphics in FRONT, captions. Panels sit behind the head so they cover the middle of them; small cards sit on the
  chest under the caption.
- **Background dim** (about 40% by default, the setup value above) so dark panels read against a bright room.
- **Real interfaces, real assets.** YouTube video grid, channel card with a ticking count, Instagram reels grid,
  channel shelves. Real thumbnails, names, handles, avatars and figures only; if a figure cannot be established, leave it
  out. Other creators' reel covers are fine behind them (the creator decides what they are comfortable publishing; the
  web-assets setting above says what may be fetched). Generic UI labels are allowed but list them when handing over.
  A real image that is missing becomes a plain placeholder tile, never a made-up picture: the engine lists every one
  in `placeholders.txt`; report them.
- **Simple diagrams.** A glowing accent-colour ring with a counter, person icons round the head with one lit in the
  accent colour, a red wash and an X for "not this", green for a win. The accent colour is the focal colour; positive
  green `#2FA65A` and negative red `#E5372B` keep their meaning in every brand.
- **Captions.** 1-3 words (about 11 characters) in the caption font, white, on the chest (position and size in the
  setup table), sentence case as spoken, no punctuation. Two to five emphasis words per reel switch to the accent
  colour in the emphasis font, large. **Numbers never go in the emphasis font** (main font only).
- **Camera.** A step on each sentence cut: punch in to about 1.07-1.09 (never beyond the setup ceiling), back to 1.0 on
  the next, with a slow drift inside each block. Only the two camera layers (full frame and cut-out) move; graphics and
  captions stay put.
- **Motion.** Panels rise or drop in on a heavy blur (about 0.5 s) and leave the same way; small things pop in from a
  blur; grids drift slowly while on screen; counters tick as plain numbers. Something new lands every 1-2 s, just ahead
  of the word.

### Defaults this style avoids (change only if the creator asks)

- A floating cut-out of the creator's head (a "head sticker"), a cursor, or lines drawn from either. Buttons that need
  pressing press themselves.
- Split screen, full-screen animations and B-roll: this style is one full-frame mode.
- Numbers in the emphasis font.
- Drawn or invented logos, thumbnails, avatars and figures where a real one can be found.

## Layout numbers (1080 x 1920)

The numbers below are for a tight 9:16 crop where the head covers roughly the head box from the setup table (at scale
1). Measure it from a still of the actual cut and adjust everything below to it before placing graphics (see step 1).

- **Behind panels:** x 80-1000, top at y 150, 800 tall. Only the top strip and the two side columns show: put what must
  be read there (tab row, shelf labels on the left, an X badge top right), and let the head cover the rest.
- **Round the head:** left column x 100-220, right column x 890-960, y 400-920; top right corner for a ring (790, 150).
- **Front cards:** below the caption, y 1270-1500, 780 wide, centred. Hands move through here; that is fine.
- Nothing readable above y 270 or below y 1500 (the platforms' own interface sits there). Captions stay above y 1250.
- Graphics never cover the face. Behind panels cannot, by construction; check front cards and the people icons.

## Working with the creator

- **Working style: @@WORKING_STYLE@@.** `consult` = ask about design choices (which interface per sentence, the opening
  graphic, wording) with 2-4 concrete options before building. `build-first` = build the whole reel on your own
  judgement and report everything you chose, everything invented and every placeholder.
- **Review first.** Never render the full-quality final first. Render the 720p preview, give the creator the file and the
  contact sheet, and wait for approval. Apply their timestamped notes (the engine writes `review_events.json`: every
  caption, graphic and zoom with stable ids and times), re-preview, and render the final only once approved.
- **Any screenshot the creator drags in** is probably meant for the reel: animate it in, but ask first where it goes
  and how it moves.
- **Music: @@MUSIC_RULE@@.** `ask` = never assume a track: ask whether they want music and which. `pick` = choose a
  favourite from the library that suits the video and say which. When music is used, deliver a with-music and a
  no-music version.
- **Real assets first.** Look in the proof folder, the other asset folders and the earlier projects' `assets/`, then
  the web (per the web-assets setting). Never show anything on the never-show list.
- Report at the end: what was built, every real asset and where it came from, every placeholder, every generic label.

## Steps

1. **Cut, crop, matte** with the business-short-form-reels skill (`S=~/.claude/skills/business-short-form-reels/scripts`;
   its steps 1-3: transcript, tight cut, `07_crops.sh`). That gives `hf-media/cam_full.mp4` (the 9:16 cut, silent) and
   `cam_fg.webm` (the cut-out), and `cut/words.json` (word timings on the cut's clock). Open a still and check the
   creator is centred before cropping, and measure the head box from it. An existing business reel project already has
   all three. If a 9:16 tight cut exists from anywhere else, make the cut-out with
   `npx hyperframes remove-background cam_full.mp4 -o cam_fg.webm --quality best` and a `words.json` of
   `[[start, end, word], ...]`.
2. **Scaffold:** `K=~/.claude/skills/depth-ui-reel; $K/scripts/new_reel.sh @@PROJECTS_ROOT@@/<slug>-depth "<hf-media dir>" <cut words.json>`.
   It links the media, copies the engine, fonts, profile picture and reel covers saved at setup, and starts `build.py`
   from the worked example.
3. **Plan the graphics.** Read the script sentence by sentence. For each sentence choose ONE thing to show (an interface
   when they name a platform, account, number or document; a diagram when they explain an idea) and whether it goes
   behind the head or on the chest. Vary the kind of graphic from sentence to sentence. Mark the sentence cuts for the
   camera. Collect the real assets first (put thumbnails in `assets/yt/`, covers in `assets/reels/`, other images in
   `assets/real/`).
4. **Write `build.py`** from the example: `D.init(...)`, `D.captions()`, `D.camera([...])`, then per sentence
   `D.behind(...)` / `D.front(...)` with a piece (`yt_grid`, `ig_grid`, `shelves`, `channel`, `ring`, `people`) or your
   own HTML plus `D.css(...)`, timed with `blur_in`, `blur_out`, `pop`, `fade`, `drift`, `counter`, `light_up`, `shake`,
   `D.js(...)`. Call `D.ev(...)` for each graphic. A reel should get its own signature graphics: the pieces are a start,
   not a template to repeat.
5. **Preview:** `$K/scripts/preview.sh <project> "<Title> - CUT 16x9.mp4"`. Look at `work/sheet.jpg` and a few snapshots
   (`npx hyperframes snapshot . --at 1.5,4,... --no-end --describe false`) before handing over. Check the fonts in the
   first snapshot are the real ones, not a fallback.
6. **Final after approval:** `$K/scripts/final.sh <project> "<CUT file>" "<Title> - 9x16 Reel.mp4"`, then move it per the
   output rule above.

**Music and sound effects:** follow the music rule above. When wanted, use the business-short-form-reels skill's
`engine/mix.py` standard (voice natural at about -16 LUFS, music about 28 dB under, sparse sound effects only on real
animations, never on cuts or punch-ins) and deliver a with-music and a no-music version. Without a sound-effects pack,
the reel is delivered without effects; do not invent sounds.

## Gotchas

- `hyperframes check` reports `text_occluded ... inside #vFg` for everything behind the head: intended. Fix anything else.
- `hyperframes render` has no 720p setting; `preview.sh` renders a 1080 draft and scales it.
- `cam_full.mp4` from `07_crops.sh` is silent: the voice comes from the CUT file passed to the scripts.
- An element that tweens `scale` must not carry a CSS `transform`; a `fromTo` that reveals must end with `opacity:1`.
- The project folder has symlinks to the media: keep it on the internal drive; renders can go to the footage drive.
- The matte keeps whatever sits behind or beside them (a chair, a plant) in. Graphics behind them are covered by that as
  well as by them: check the lower corners.
- A caption group longer than 11 characters is split by the engine; a much larger caption size needs `max_chars` lowered
  in `D.captions(max_chars=...)`.
