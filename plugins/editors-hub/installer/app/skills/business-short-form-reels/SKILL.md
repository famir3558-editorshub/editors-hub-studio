---
name: business-short-form-reels
description: Business Short Form Reels - turn one raw business talking-head clip (16:9 or vertical, desk or studio set-up) into a finished, premium 9:16 reel built in HyperFrames, in the creator's own brand. Does the whole job - transcript, tight cut (silences, repeated words and failed takes removed), an attention-grabbing opening with a text hook, and a rotation of full-screen creator (slow zoom out, one-word captions, real reels behind the head), split screen (animation on top, creator on the bottom) and full-screen animation, with every mode switch landing on a real edit cut. Liquid Glass stacked pills, real Instagram notifications, real Google Docs and Notion windows, real assets, quiet sound effects and optional music. Use whenever the creator hands over a raw business reel or a cut and says "do the business reel", "short form reel", "edit this reel", "split screen with animations", "do the next one the same way", "use the reels skill", or asks for a new version / different animation of an existing reel. Also use for one part alone - just the tight cut, just the captions, the sound mix, or re-rendering after a change. On first use it asks a short series of setup questions (brand, fonts, references) before editing anything.
---

# Business Short Form Reels

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/business-short-form-reels/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first, one question at a time. Do not
  start the edit, and do not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if it exists,
  `~/.claude/creator-profile/notes/business-short-form-reels.md`. Rules under `## Style overrides` in that notes file
  win over the defaults written below. That file is where the creator's references and corrections live.

"Redo my setup" re-runs the interview at any time. A new rule given while working ("never do X", "always Y") is
written into the notes file, dated, the moment it is said.

## Your setup

| | |
|---|---|
| Creator | @@CREATOR_NAME@@ (@@HANDLE@@, @@PLATFORM@@) |
| Brand | @@BRAND_NAME@@: @@NICHE@@ |
| Accent colour | @@ACCENT@@ (@@ACCENT_NAME@@) on background @@BG@@ |
| Main font | @@FONT_MAIN_NAME@@ (bold for hooks, captions, labels, numbers) |
| Emphasis font | @@FONT_ACCENT_NAME@@ (key words only, never numbers) |
| Transcriber | @@TRANSCRIBER@@ |
| Working style | @@WORKING_STYLE@@ |
| Music | @@MUSIC_RULE@@ (library: @@MUSIC_DIR@@) |
| Sound effects | @@SFX_DIR@@ |
| Real assets | @@PROOF_DIR@@ |
| Folders | work `@@WORK_ROOT@@/<slug>` · projects `@@PROJECTS_ROOT@@/<slug>-hf` · finals: @@OUTPUT_RULE@@ |
| Usual camera | @@CAMERA_SETUP@@ (default crops: full `@@CROP_FULL@@`, top `@@CROP_TOP@@`) |
| CTA style | @@CTA_STYLE@@ |

**Worked examples:** the three `examples/*-final/build.py` reels. Read one before building; they use `engine/kit.py`.
They are another creator's reels kept as structure references: copy how a reel is put together, never its wording,
names or assets. Read `references/style-spec.md` (the full default style) before designing.

**HyperFrames only.** Every reel is built and rendered with HyperFrames (`npx hyperframes`). Do not switch to another
motion-graphics tool part-way.

## How to work with the creator (as important as the look)

- **Working style: @@WORKING_STYLE@@.**
  - `consult` (the default): ask about design choices before building. Sizing, motion, easing, wording, which graphic,
    which catalog effect: ask with `AskUserQuestion`, offer 2-4 concrete options, then build. Do not decide alone and
    report afterwards.
  - `build-first`: build the whole reel on your own judgment, then report everything you chose. Ask only what cannot
    be guessed.
- **Always check the HyperFrames catalog** for a style or effect that suits the video being edited
  (`npx hyperframes catalog --query "<look>" --json`), then offer it. `hyperframes add <name>` drops the item in
  `compositions/components/`; read its motion spec and rebuild the effect inside the scene to that spec (catalog blocks
  do not mount into this layout as-is). Say so when reporting.
- **Any screenshot the creator drags in:** assume it should be animated into the reel, but ask first (where it goes,
  how it moves).
- **Music: @@MUSIC_RULE@@.** `ask` = never assume a track; ask whether to add music and which one. `pick` = choose a
  favourite that suits the video and say which. When music is used, deliver two versions: with and without.
- **Always prioritise real assets:** real client screenshots, real photos, real reel covers (other creators' as well
  as the creator's own), the creator's real profile picture. Look in the proof folder (`@@PROOF_DIR@@`) first. Where a
  detail is missing (commenter names, mock-up captions, doc lines) use a generic default and list every one at the end.
- The creator reviews the phone copy. Report what changed, what you chose without asking, and anything invented.

## The style (summary; `references/style-spec.md` is the full list)

These are the pack's defaults. The creator's own references and corrections (the notes file) override them.

**Structure**
- 9:16, 1080x1920, 23.976 fps. Three modes: **creator full screen**, **split** (animation top half, creator bottom
  half), **full-screen animation**.
- **Always open full screen on the creator**, with a 2-line text hook at the top above the head (line 1 white, main
  font bold, 84 px; line 2 black, main font bold, 80 px, on a squared white block) on screen from frame 1, plus
  whatever opening graphic grabs attention best for this video. Build a custom graphic if that is best; a carousel of
  reel covers circling the creator (`K.carousel`) is one option, not a rule.
- Then split, then full-screen animation, and repeat. The order bends where the cuts demand it.
- Full-screen animation: aim for ~3 s, 5 s at most, longer only when the cuts fall that way. Creator full screen:
  about 7 s at most, never without a graphic.
- Keep everything off the edge of the frame (~65 px) and clear of the platform's interface: on Instagram and TikTok,
  graphics and captions stay inside y 270-1500, captions above y 1250 (`scripts/safe_check.sh` draws the zones).
  Centre every graphic horizontally.

**Cut alignment (the rule that matters most)**
- No block showing the creator (full screen or split) may contain a visible jump cut: every edit cut is a mode switch
  or sits under a full-screen animation.
- When cuts are very close together, ignore them until the block adds up to about 3-5 s, then switch on the next cut.
  No 1-2 s blocks just to follow every cut.
- Set every switch from the exact frame: `frame / 23.976 - 0.002`. A time rounded up to the millisecond is one frame
  late, and it shows.
- `scripts/cut_times.py` lists the cuts, how visible each jump is, and the switch value to paste.
  `scripts/check_cuts.py` verifies the render.

**When the creator is full screen**
- **Slow zoom out, very subtle and eased** (barely noticeable): full-screen footage starts 5% enlarged and eases
  (`sine.out`) back to 100% over the block; full-screen animations do the same from 4% on the animation layer.
  Captions, pills, the hook and the agenda box sit on other layers and never move. Built into the engine
  (`ZOOM_FACE`, `ZOOM_ANIM`).
- **Nothing behind the head except real reels**: other creators' reel covers or real screenshots. **No pills, no
  text, no number circles behind the head.**
- **Pills go below the caption word**: centred stack, 600x100, 50 px, three at most (`K.lps`).
- **Anything quoted gets a real interface**, not a pill: a hook or script line is typed into a Notion page
  (`K.scriptcard` on the creator, `K.notion` as a scene) or a Google Doc; a comment or DM is an Instagram notification.
- Captions: one word at a time under the chin, lower-case, white, main font bold; 2-5 key words per block in the
  accent colour and the emphasis font. Numbers stay in the main font.

**Colour and type**
- **Positive = green (#2FA65A), negative = red (#B3261E), every time** (gain/lose, wins/failures, struck-out vs
  chosen, growth numbers): `K.lps(..., "green"|"red")`, `K.stack(good=, bad=)`, `K.count(tone=)`, `K.graph(col=)`.
  The accent colour stays for the neutral focal element.
- Emphasis font letter-spacing is -0.04em. No arrows between before/after screenshots.
- Keep all three modes: a two-mode reel (creator + split only) reads flat.
- **Agenda box:** while a mechanism is walked through (a named framework's parts, "two ways", "three steps"),
  `K.agenda([(lead, label, t_active)...], t_in, t_out)` shows a SQUARED box at the top of the screen in every mode.
- **No 3D.**
- **Each reel is original:** give it its own signature graphic for its core idea (a drawn bridge between app icons
  for a "bridge" idea; an ear, a heartbeat and an eye for a three-senses framework; a before/after slider, a focus
  lens on a crowd, a heartbeat against a flatline). Do not reuse the same pill stacks reel after reel.
- **Don't overdo text pills.** If a graphic can show the idea, build the graphic. On the creator: at most two or
  three short pills in a block, and none where the caption already says it.
- **A person is mentioned -> real footage or photos of them.** Look in the proof folder (`@@PROOF_DIR@@`) first, then
  ask the creator.
- **Never crop the person.** Show the clip WHOLE in a card that matches its shape:
  `K.pcard(src, t, dur, left, top, h, tag)` for portrait footage.
- **YouTube = a simple channel card you build yourself**, not a screenshot and **no banner**: picture, name, handle,
  subscriber count, button. `K.ytchannel(name, handle, subs, left, top, w, h, avatar=...)`. The simpler the better.
- **Keep the text inside graphics modest.** On the 1080-wide frame: labels and pill text 34-50 px, small tags
  22-30 px, hero numbers about 110-136 px (never 200), a named word inside a graphic about 70 px. The kit defaults are
  already set to this; the caption (56-62 px, 92 px one-word) stays the biggest text apart from a hero number.
- **Profile pictures:** if you don't have one, search the person's name (their YouTube / Instagram page) and use the
  real one, after telling the creator which you are fetching. If you still can't get one, use the default grey profile
  picture **and make sure their name is on the card** so they can be identified.
- Modes can come in any order that fits the video.

**Split and full-screen animation**
- Captions: 2-4 words, white, main font bold, exact words. Split: on the seam above the creator's head. Animation:
  under the graphic.
- **No headline, kicker or sub-line on any animation.** Only text that is part of the graphic.
- Full-screen graphics are smaller and centred (~84%). A different kind of graphic each scene; framework parts appear
  one at a time.

**Brand and graphic language**
- Dark background (@@BG@@) with a soft glow in the accent colour and very fine grain. The accent colour (@@ACCENT@@)
  only on the focal element, off-white @@PAPER@@ for text, grey @@GREY@@ for small labels. One deep red accent
  (#B3261E, pulse twice then stay) for the odd one out.
- The main font (bold) for everything; the emphasis font for emphasis words; numbers always in the main font.
- **Boxes are pills, and pills stack vertically** (icon + label). No square tiles, no 2x2 grids.
- **Liquid Glass** on pills and cards in the animations only (the engine adds it, with drifting light orbs behind).
  Pills on the creator stay solid. **A funnel is never Liquid Glass**: solid pills (`K.stack(..., solid=True)`).

**Real interfaces**
- Comments or DMs mentioned -> iPhone Instagram notification banners (dark), spring drop, newest on top pushing the
  pile down, the creator's real profile picture on their own DM. (`K.notifs`, `K.obanner`, `NBCSS` in `kit.py`.)
- A document mentioned -> a real Google Docs window (white) that scrolls to and highlights the headings named. Use it
  on every doc CTA. No collaborator cursors. (`K.gdoc` in `kit.py`.)
- "Save it for later" -> an Instagram Reel in a phone, a finger tap fills the bookmark, "Saved" toast.

**Motion**
- Entrances: **focus pull** (opacity 0, 108%, 16 px blur -> sharp in ~0.5 s, power3.out) for elements and for the
  whole graphic at each switch. Elements land just ahead of the word (start ~0.6 s early). Both are built into the
  engine.
- Exits: soft fade (~0.3 s) before the switch. No bounce on pills. A light sweep (`sweep(tl, id, t)`) crosses a pill
  when it becomes the active one.
- Counters tick up as a plain number (no rolling wheel). Graphs draw on with a dot riding the front.

**Sound** (mixed after the render)
- Key moments only (~40 sounds per 90 s): a soft whoosh on each animation coming in plus accents; an opening carousel
  gets one swirl plus a tick per cover.
- Sounds come from the creator's own pack through `sfx_map.json` (made at setup with `scripts/sfx_probe.py`). No
  map = no sound effects: say so in the report rather than inventing any.
- Quiet: `TRIM = -8.5` in `mix.py` (whooshes peak ~-29.5 dBFS, pops ~-32.5; a voice peaks near -3).
- Music, when used: ~-39 dB mean (about 11 dB under the voice), started where the beat drops, 0.4 s fade in, 1.5 s
  fade out. Tracks live in `@@MUSIC_DIR@@`.

## Workflow

`S=~/.claude/skills/business-short-form-reels/scripts` · work dir `W=@@WORK_ROOT@@/<slug>` (small files) · project
`@@PROJECTS_ROOT@@/<slug>-hf` · output `OUT` = @@OUTPUT_RULE@@ (default: `"<folder of the raw file>/<Title> - Edit"`).
Long steps run in the background. Video files are large: keep the cut, crops and renders on the drive that holds the
raw file, and render one reel at a time.

1. **Transcribe** with the transcriber chosen at setup (@@TRANSCRIBER@@).
   `mkdir -p $W && ffmpeg -v error -y -i "<raw>" -vn -ac 1 -ar 48000 $W/a48.wav && ffmpeg -v error -y -i $W/a48.wav -ar 16000 $W/a16.wav`,
   then `python3 $S/01_transcribe.py $W`, then `python3 $S/01b_el_to_tx.py $W` to print the script with times.
   ElevenLabs gives the most accurate word edges; with local transcription, check step 2's output more closely for
   clipped words. The key is read from the shell profile by `stt.py`: never print it, never ask for it in chat.
2. **Choose takes.** Write `$W/flubs.json` = `[[start,end],...]` raw-second ranges to drop (failed takes, repeats,
   chat, throat clears; keep the LAST complete take; keep both a mid-video CTA and an end CTA). Then
   `python3 $S/02_cut.py $W && python3 $S/02b_guard_words.py $W && python3 $S/03_verify_cut.py $W`. The guard stops a
   silence cut clipping a word. Read the EDIT line as a script.
3. **Render the cut and crops.** `python3 $S/04_render_cut.py "<raw>" $W/edl.json "$OUT/<Title> - CUT 16x9.mp4"`,
   then `$S/07_crops.sh "$OUT/<Title> - CUT 16x9.mp4" "$OUT/hf-media"` (check a still first: the default crops are the
   ones saved at setup for the usual camera; pass new numbers when the framing differs; it also makes the cut-out used
   for behind-the-head graphics, skip it with `NO_MATTE=1`), then `python3 $S/05b_cut_words.py $W` for
   `cut/words.json`. A vertical source needs no 9:16 crop: scale it, and crop only the 9:8 top window.
4. **Captions.** Write `$W/phrases.txt` (one caption per line, 2-4 words, every word in order),
   `python3 $S/06_captions.py $W/cut/words.json $W/phrases.txt $W/captions.json`.
5. **Scaffold.** `$S/08_new_reel.sh <slug>-hf "<Title>" "$OUT"` (copies the engine, kit, mix, fonts, brand CSS,
   profile picture and sound map into the project), then copy `captions.json` and `cut/words.json` in.
6. **Plan the blocks from the cuts.** `python3 $S/cut_times.py $W/edl.json "$OUT/hf-media/cam_full.mp4"`. Group cuts
   into blocks of 3-5 s (animation ~3 s), alternate creator / split / animation, put every big jump on a switch or
   under an animation. **Show the plan as a small table.** In `consult` mode, ask about the opening, each block's
   graphic, catalog effects and music before building.
7. **Build `build.py`** with `engine/kit.py` (`examples/3c-hook-matrix-final/build.py` is a short worked example):
   `FACE` / `FULL` windows with exact switch values, one `scene(...)` per block, `E.overlay(...)` for everything on
   the creator. Start a split scene ~0.25 s before its switch when a face window precedes it.
   `python3 build.py && npx hyperframes lint && npx hyperframes snapshot --at <every moment that matters>`; read every
   tile. On the first build, check the fonts are the real ones and not a fallback.
8. **Render, mix, verify, deliver.**
   `$S/09_render.sh @@PROJECTS_ROOT@@/<slug>-hf "$OUT" "<Title>" " (v1 - no SFX)"`, then
   `python3 mix.py "$OUT" "<Title>" "v1" [music file] [music start s]` (reads `sfx.json` written by `K.flush()`;
   writes "no music" and "with music" for the master and the phone copy). Render ONE reel at a time.
   `python3 $S/check_cuts.py "<reel>" "$OUT/hf-media" $W/edl.json` must report nothing off a cut. `$S/sheet.sh` makes a
   contact sheet from the rendered file either side of every switch: open it. Send the phone copy with `SendUserFile`
   (30 MB limit).

Changing a finished reel: copy `build.py` to `build_vN.py` first, edit, re-run step 8 with a new suffix. The creator
compares versions.

## Gotchas
- The renderer rounds `strokeDashoffset`: use `pathLength="1000"` (the `draw` helper does). A multi-part path draws
  all parts at once: put arrowheads in their own path and compute them from the curve's end tangent.
- Overlay CSS is global to the page: a scene class with the same name as an overlay class inherits it. Keep class
  names unique.
- GSAP resets the CSS `translate` property on anything it animates: position panels with a wrapper, not `translate`.
- A `//` comment inside the engine's one-line JS patch comments out the rest of the line and silently kills every
  scene timeline.
- A motion blur filter on a layer blurs everything in it: wrap only the moving items.
- `fromTo` with opacity 0 -> 1 inside a scene is treated as an entrance by the engine (focus pull, started 0.6 s
  early). For exact timing or custom motion use the raw `__ft` / `__tt`, or `tl.set`.
- Entrances authored at or before a scene's start are set instantly, so the graphic is complete on the switch frame.
- Many ffmpeg builds have no subtitle/drawtext filters: captions are HTML in the composition. `SendUserFile` limit is
  30 MB.
- `-apple-system` gives the system font for the interface mock-ups; the brand fonts come from `assets/fonts` or from
  fonts installed on the computer (set at setup). A font activated through Adobe Fonts only renders while Creative
  Cloud is running.
- Two renders writing to the same external drive at once can fail: one at a time.

## Defaults this style avoids (change only if the creator asks)
Creator on top in split · opening on split · graphics across the chest · pills or text behind the head · square boxes
and grids · rolling-digit counter · collaborator cursors on the Doc · fast slide / whip entrances and bouncy pops ·
headlines over animations · a sound on every element · 3D · mixing motion-graphics tools.

## Related
`hyperframes`, `hyperframes-core`, `hyperframes-animation`, `hyperframes-registry` (framework rules and the catalog) ·
`references/style-spec.md` (the full default style) · `references/scene-library.md` (scene ideas with working code) ·
`personal-short-form-reels` (the B-roll style for personal clips; shares this engine) · `coaching-call-clips`,
`youtube-clips` (clips from long recordings, built in this look).
