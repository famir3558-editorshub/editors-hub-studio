---
name: ranking-format
description: The ranking format - turn a talking-head video where someone RANKS things (tier list - "weekly check-ins, A tier", "group chats, F tier") into a 9:16 reel with an S A B C D E F tier table on screen. The presenter stays full frame, a topic title sits at the top, and each thing they rank pops up over the table as a card (a picture that represents it plus its name), then shrinks into its tier row when they give the verdict, so the table fills up through the video. Does the whole job from a raw file - assess the video, word-timed transcript, tight cut (silences, mistakes, repeats out), find every item and verdict, source a real image per item, check the table never covers the face (shows the creator placement options on a real frame), captions, preview, final. Use whenever the creator or a client says "ranking format", "ranking video", "tier list", "tier list reel", "S tier / A tier video", "rank these", "put them in the table", or hands over a video where things are rated into tiers. Only for ranking videos - not for ordinary talking-head reels (use the business or personal short-form reel skills).
---

# Ranking format (tier-list reel)

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/ranking-format/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first. Do not start the task, and do
  not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if it exists,
  `~/.claude/creator-profile/notes/ranking-format.md`. Rules under `## Style overrides` in that notes file win over
  the defaults written below.

"redo my setup" re-runs the interview at any time.

## Your setup

Filled in by setup. To change a line, change the answer (`setup/SETUP.md`), never this text.

| | |
|---|---|
| Creator | @@CREATOR_NAME@@ · @@BRAND_NAME@@ · @@HANDLE@@ (@@PLATFORM@@) |
| What they teach, and to whom | @@NICHE@@ |
| Colours | accent @@ACCENT@@ (@@ACCENT_NAME@@) · background @@BG@@ · text @@PAPER@@ |
| Fonts | main: @@FONT_MAIN_NAME@@ (title, tier letters, item names on the cards) · captions: @@FONT_CAPTION_NAME@@ |
| Topic title | style @@TITLE_STYLE@@, case @@TITLE_CASE@@, in the accent colour |
| Item name on the card | colour @@CARD_NAME_COLOUR@@, outlined |
| Captions | @@CAPTIONS@@ |
| Transcriber | @@TRANSCRIBER@@ |
| Item images | @@WEB_ASSETS@@ · own material first in `@@PROOF_DIR@@` and `@@ASSET_DIRS@@` |
| Never show | @@NEVER_SHOW@@ |
| Face rule | @@FACE_RULE@@ |
| How far to go alone | @@WORK_RULE@@ |
| Music | @@MUSIC_RULE@@ · music folder: @@MUSIC_DIR@@ |
| Footage drive | @@MEDIA_DRIVE@@ |
| Finished videos go | @@OUTPUT_RULE@@ |
| Folders | working files `@@WORK_ROOT@@` · HyperFrames projects `@@PROJECTS_ROOT@@` |

`K=~/.claude/skills/ranking-format`. Engine: `engine/rank_engine.py` (driven by `plan.json`, no code to write per
reel). Look first: `examples/placeholder-sample/index.html` (a 15 s placeholder sample of the whole format: grey
stand-in presenter, three made-up items) and `examples/plan.example.json`. They are structure references only: never
reuse their wording, names or images.

**HyperFrames only.** The reel is built and rendered with HyperFrames (`npx hyperframes`).

## The look

- **One mode.** Presenter full frame, 9:16, start to finish. No split screen, no B-roll, no zooms.
- **Topic title** at the top (y 286): accent colour, caps by default, main font, italic by default, 58 px.
- **Tier table:** always the seven tiers **S A B C D E F**, even if only some get used. Label colours
  S `#FF7F7E`, A `#FFBF7F`, B `#FFFF7F`, C `#7FFF7F`, D `#7FBFFF`, E `#807FFF`, F `#FF7FFE` (the classic tier-list
  palette, a convention of the format rather than a brand colour); rows `#1b1a1d` on black. 760 x 500 px at full
  size, centred, on screen from the first second.
- **Item card:** when they name the thing, a 16:9 card (560 x 315) pops up over the middle of the table: a picture that
  represents the thing, with its name in heavy outlined caps. It holds while they explain.
- **Verdict:** on the word that gives the tier, the card shrinks into that row (0.42 s) and the row flashes. It stays
  there. Several items in one tier line up left to right; thumbnails shrink automatically when a row gets crowded.
- **Captions:** 3-6 words on ONE line, sentence case, no punctuation, caption font 46 px, tracking -45, sitting just
  above the table (so moving the table moves the captions with it). The item's name is its own caption in the accent
  colour. Captions can be switched off at setup or per reel (`"captions": false` in `plan.json`).
- **After the ranking** (a bonus question, a sign-off): table and title fade out (`table_out`) and it is talking head +
  captions only.
- Figures and money are set in the main font, never in the emphasis serif. No em dashes on screen. No watermarks on
  images.

## The face rule (default)

The table must **never cover the person's face**. Order of preference:
1. **A** - full size inside the safe zone (table y 1000-1500).
2. **B** - full size but pushed down into the bottom zone the apps' interface covers. Go into the safe zone **first**.
3. **C90 / C80** - only when the bottom zone is already used up: make the table 10%, then 20% smaller.

`scripts/layout.py` measures the lowest the chin gets across the whole cut, tests the four placements in that order,
recommends the first that clears the face, and writes `work/layout_options.jpg`: every option drawn on the worst
frame with the safe-zone lines and the face box. **Whenever the recommendation is not A, stop: show the creator that
picture, say which one is recommended and why, pass on the warnings it prints (how many pixels sit under the apps'
interface, lower tiers E / F possibly hidden, title touching the head), and let them choose** (smaller, lower, or
re-crop). Record the choice with `--choose`. If nothing clears the face the presenter is too big in frame: re-crop
wider or lower, then run it again. Never scale or shift the footage itself to make room: move the table.

## Steps

0. **Assess the video.** Watch it (the `watch` skill, or frames + transcript) before anything else and answer:
   - Is it really a ranking video (things given tiers)? If not, say so and suggest another skill.
   - **Raw or already cut?** Silences, false starts, repeated takes, set-up footage = raw: do step 1 in full. Already
     tight: skip the cut but still transcribe.
   - Framing: 16:9 or 9:16, where the head sits, how much body is below the chin (the table needs that space).
   - How many items, which tiers, and anything after the ranking ends.
1. **Transcribe and cut** with the `business-short-form-reels` scripts
   (`S=~/.claude/skills/business-short-form-reels/scripts`, its workflow steps 1-3): transcript with the transcriber
   chosen at setup (@@TRANSCRIBER@@), tight cut (dead space, mistakes, false starts, repeats out; never cut inside a
   verdict or between an item's name and its explanation), verify, then word timings of the cut
   (`cut/words.json`). Voice stays natural, only raised to about -16 LUFS. `scripts/stt.py` here is the same shared
   transcription helper those scripts use (it also lets you check the ElevenLabs key is found).
2. **Crop to 9:16** (`07_crops.sh` with `NO_MATTE=1`: no cut-out is needed, the table sits in front). For this format
   crop as WIDE as the footage allows and place the head high (chin above about y 880 is ideal) so the table has
   room. Open a still and check the speaker is centred.
3. **Scaffold:** `$K/scripts/new_reel.sh @@PROJECTS_ROOT@@/<slug>-rank <hf-media>/cam_full.mp4 <cut>/words.json`.
4. **Plan** (`plan.json`): `title` (the topic, 1-3 words), `duration`, `table_in`, `table_out` (null, or when the
   ranking ends), and one entry per item, in order, with times from `words.json`:
   `label` (short name for the card, 1-4 words), `image`, `t_in` (start of the word where they name it), `t_name_end`
   (end of the name), `t_rank` (start of the word that gives the tier, e.g. the "A" of "A tier"), `tier`.
   If they change their mind ("actually, B"), use the final verdict. If they never say a tier out loud, ask.
5. **One image per item** in `assets/items/`, 16:9 or wider, that REPRESENTS the thing: a real screenshot, product,
   interface or photo first (the creator's own material in the proof and asset folders, then the web as the setup
   answer allows), a clean generated or hand-built image last. Subject in the upper two thirds (the name covers the
   bottom). No watermarks, nothing on the never-show list, readable at 107 px wide once it is in the row. Tell the
   creator afterwards what you used and where each image came from: what they are comfortable publishing is their call.
6. **Layout:** `python3 $K/scripts/layout.py <project>` (add `--to <table_out>` when the table leaves early), LOOK at
   `work/layout_options.jpg`, follow the face rule above, then `--choose <A|B|C90|C80>` if the creator picks differently.
7. **Preview:** `$K/scripts/preview.sh <project> "<CUT file with the voice>" "<label>"`. Look at `work/sheet.jpg`:
   every card readable, every card lands in the right row, no caption under a card, face never covered. Hand the
   creator `review/preview_720.mp4`.
8. **Final after approval:** `$K/scripts/final.sh <project> "<CUT file>" "<Title> - 9x16 Ranking.mp4"`, then file it
   where finished videos go (@@OUTPUT_RULE@@).

## Preview first (applies to every render)

Do NOT render the full-quality final first. Render the 720p preview (`scripts/preview.sh`), give the creator the file
(and `work/sheet.jpg` if useful), and wait for their approval before `scripts/final.sh`. Apply their timestamped notes
by editing `plan.json` (times, tiers, labels, images) or the layout choice, re-preview, and render the final only once
approved. The engine writes `review_events.json` (table, every card, every verdict, every caption, with stable ids and
times) and `review_words.json`: use them to turn a note like "the second card is late" into the exact event. If the
creator keeps a review tool of their own, point `REVIEW_HOOK` at it (see the header of `preview.sh`).

## How to work with the creator

The setup answer "how far to go alone" is @@WORK_RULE@@. Whatever it says: always show the layout options frame when
the recommendation is not A, and always say which images you chose.

**Music and sound effects:** @@MUSIC_RULE@@ (music folder: @@MUSIC_DIR@@). If music is wanted, use the business
skill's `engine/mix.py` standard (music 28 dB under the voice, sparse effects only on real animations) and deliver a
with-music and a no-music version. This format has no sound effects of its own.

## Gotchas

- `hyperframes lint` may report `font_family_without_font_face` when a font is a macOS system font saved as a local
  font: it renders correctly on a Mac that has the font. On another machine, bundle the font file.
- `rank_engine.py` warns when an image is missing or when a tier has so many items the thumbnails drop under 60 px.
- Card names are sized for a main font about 0.58 em per character wide. For a very condensed or very wide main font,
  set `card_char_w` in `plan.json` (about 0.47 condensed, 0.65 wide).
- Captions sit 78 px above the table top, so moving the table moves the captions with it. `title_y` in `plan.json`
  moves the title.
- The project links to the media: keep it on the same drive as the cut.
- `layout.py` compiles `face_boxes.swift` (Apple Vision) into `work/` on first run: macOS with the Xcode command line
  tools only. Without it, find the lowest chin by eye on a few frames and choose with `--choose`.
- When the presenter leans or the camera moves a lot, run `layout.py` on the whole table section, not a short sample:
  the recommendation is based on the worst frame.
- The safe-zone numbers (y 270-1500, hard limit 1720) are for Instagram Reels, TikTok and Shorts: the interface covers
  the top and bottom of the frame.
