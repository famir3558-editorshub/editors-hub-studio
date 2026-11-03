# The style: captions, vertical layout, graphics, motion, sound, review

This is the pack's **default style** for clips. It is one system: do not mix in other looks clip by clip. The
creator's own changes live in `~/.claude/creator-profile/notes/<this skill's name>.md` under `## Style overrides`
and win over everything here. Brand values (accent colour @@ACCENT@@, main font @@FONT_MAIN_NAME@@, emphasis font
@@FONT_ACCENT_NAME@@, caption font @@FONT_CAPTION_NAME@@) come from setup and are already filled into the engine.

If the pack's `business-short-form-reels` skill is installed, sections 2-5 below are the same look that skill
uses. Its notes file (`~/.claude/creator-profile/notes/business-short-form-reels.md`) is where the vertical look is
kept in step: when a vertical rule changes there, apply it here too.

---

## 1. Captions (the whole clip, including under graphics)

- **Every spoken word is on screen once, in order, timed to the speech.** The caption script
  (`scripts/cut/06_captions.py`) refuses a phrases file that does not match the verified cut word for word, so
  captions cannot drift from what is said.
- **One short line, 1-3 words** (about two on average; the 16:9 frame can take one more), changing on the word.
  Break at the natural phrase; never split a number from its unit or a first name from a surname.
- **Type**: the caption font, bold, tight tracking (`letter-spacing: -0.05em`), white, soft shadow. About 68 px in
  16:9 and 66 px in 9:16 (`E.CAP[ratio]["size"]`).
- **Emphasis**: the word that carries the point switches to **the emphasis font in the accent colour**, on the same
  line, same baseline, inside the normal caption. Nothing else about the caption changes. A figure (`*400,000*`)
  stays in the caption font and turns the accent colour: the emphasis font is only for whole words. Use it about
  3-6 times a minute, never on two captions running. The engine sets emphasis words 12% larger so a lighter serif
  reads the same size as the bold caption font (`E.EM_SCALE`; set it to 1.0 when the emphasis font is the same
  family as the caption font).
- **No stacked captions.** One line only: no multi-line blocks, no enlarged word, no line-by-line reveals. If a
  phrase is too long for one line, split it into two captions.
- **Position, 16:9**: bottom centre, the same place for the whole clip, including when a graphic is up.
- **Position, 9:16**: under the chin on the upper chest when the speaker is full screen (never on the face); on the
  seam just above the speaker's head in split; under the graphic in a full-screen animation. These are
  `E.CAP["9x16"]`; check a still of each shot and adjust when the framing differs.
- A line spoken by someone other than the main speaker is marked `"other": true` in `captions.json` and shown in a
  paler colour.
- Fix mis-heard words with `{heard|Shown}` in `phrases.txt`; capitals and punctuation can be edited directly. Read
  `captions.txt` in full after every run and clear every LONG / SHORT line.

After the first build, look at a snapshot and check every font is the real one and not a fallback.

---

## 2. The vertical (9:16) structure

**Three modes**

1. **Speaker full screen** (engine shots `him`, `him2`): a very slow, eased zoom out over the block (starts 5%
   enlarged, eases back to 100%; built into the engine). Captions and the hook sit on other layers and never move.
2. **Split** (`split`): animation in the top half, the speaker in the bottom half, framed so the whole face sits
   above the platform's bottom interface.
3. **Full-screen animation** (`anim`): the graphic alone on the brand background, smaller and centred, with the
   background's soft accent glow around it.

**Order.** Always open full screen on the speaker. After that the modes follow the content, not a fixed rotation:
full screen for the hook, opinions, punchlines, the emotional moment and the last line; split when they are
explaining and there is something to look at; full-screen animation for a framework, a real example that needs the
whole screen, or a join that needs covering. Keep all three available; use fewer in a simple clip.

**Lengths.** Full-screen animation: about 3 s, 5 at most, longer only when the cuts fall that way. Speaker full
screen: about 7 s at most before something changes. No block under about 0.9 s: it reads as a flash (the engine
warns).

**Cut alignment (the rule that matters most)**

- No block showing the speaker (full screen or split) may contain a visible jump cut. Every edit cut is either a
  mode switch or hidden under a full-screen animation.
- When cuts come very close together, ignore them until the block adds up to about 3-5 s, then switch on the next
  cut. No 1-2 s blocks just to follow every cut.
- A switch may land a little early or late against the sentence so that it hits the cut.
- Every switch is set from the exact frame. `E.shots` snaps the time you give it to the frame; for anything else
  that must hit a cut use `E.fr(t)`. A time rounded up to the millisecond lands one frame late, and it shows.
- Check on the rendered file, on the frames either side of every switch, not by eye in a preview.

**The opening.** It must grab attention; that is the only fixed rule.

- A **text hook** is on screen from the first frame, at the top just above the speaker's head, two lines at most:
  line 1 plain white in the main font (bold, about 84 px, soft shadow); line 2 black on a squared white block
  (about 80 px). `E.hook(a, b, line1, line2)`. It leaves on the first mode switch.
- The hook wording is a fair summary of what the clip delivers. It is written by you, so list it in the report.
- An opening graphic is optional. Use one only when it helps this clip.

**Frame.** 1080x1920 at the source frame rate. Keep everything about 65 px off the edge of the frame; keep captions
and the key part of a graphic out of the bottom fifth and the top eighth, where the platforms put their interface.
Centre every graphic horizontally.

**When the speaker is full screen**

- Nothing sits behind the speaker's head unless it is a real asset (a real post cover, a real screenshot) and the
  cut-out is clean. No pills, text or number circles behind the head.
- Pills go below the caption word: a centred stack, three at most, and none that repeats the caption.
- Anything quoted gets a real interface, not a pill: a hook or script line is typed into a document window; a
  comment or DM is a notification.

**Split and full-screen animation**

- **No headline, kicker or sub-line on any animation.** Only text that is part of the graphic (labels, interface
  text, numbers). The caption carries the sentence.
- A different kind of graphic in each scene. Parts of a framework appear one at a time, as they are named.

---

## 3. Graphic language

- **Background**: the brand's dark background (@@BG@@) with a soft glow in the accent colour. No coarse grain, no
  grid.
- **Colour**: the accent colour only on the one focal element. Text in the off-white (@@PAPER@@), small labels in
  the grey (@@GREY@@). **Positive is green (`#2FA65A`) and negative is red (`#B3261E`), every time** (gain / loss,
  right / wrong, chosen / struck out). That is a meaning, not a brand colour, and it does not change with the brand.
- **Type**: the main font for everything inside graphics; the emphasis font for the occasional whole word;
  **numbers are always in the main font**.
- **Boxes are pills, and pills stack vertically** (icon + label). No square tiles, no 2x2 grids.
- **Glass**: cards and pills in the animations have a translucent glass finish (blur, bright top rim). A pill that
  sits over the speaker stays solid so it reads. A funnel is solid, never glass.
- **Keep text inside graphics modest.** On the 680x540 stage: labels and pill text about 26-38 px, small tags
  22-30 px, a hero number about 84-120 px. The caption stays the biggest text apart from a hero number.
- **Real assets first**: real screenshots, real photos, real post covers, the creator's real profile picture
  (`avatar.jpg` in the profile). Where a detail is missing (a commenter's name, a caption on a mock-up, a line in a
  document) use a clearly generic default and list every one in the report.
- **Never crop a person.** Show a clip or photo of someone whole, in a card that matches its shape.
- **Real interfaces**: a comment or DM is a phone notification banner; a document is a real-looking document
  window that scrolls to the heading being named; a website is the real page in a simple browser frame; a post is
  the real post, uncropped, with its own handle visible; a channel is a simple card (picture, name, handle, count,
  button), no banner.
- **Each clip gets its own graphic for its core idea.** Do not reuse the same pill stack clip after clip. If a
  drawing can show the idea, build the drawing rather than another list.
- No pill or label that repeats the caption word.

What to show for a given sentence is in `layouts.md`.

---

## 4. Motion

- **Entrances: focus pull.** An element starts transparent, slightly large (108%) and heavily blurred, and snaps
  into sharp focus in about half a second (`fin(sel, t)`). Elements land just ahead of the word that names them
  (`EARLY`).
- **Exits**: a soft fade with a slight blur over about 0.25 s, just before the switch (`fout`). A stage that ends
  on a hard cut is cut, not faded.
- No bounce or overshoot on pills and cards. No whip or slide entrances.
- A band of light sweeps across a pill when it becomes the active one (`sweep`).
- Counters tick up as a plain number (`counter`); no rolling-digit wheel.
- Lines and graphs draw on (`draw`, with `pathLength="1000"`); text types (`typeText`).
- No 3D.

HyperFrames notes that save time: build every clip from `build.py` and never edit `index.html` by hand; GSAP
resets the CSS `translate` property on anything it animates, so position with a wrapper and animate the inner
element; a multi-part SVG path draws all its parts at once, so put arrowheads in their own path; class names in a
stage's CSS are global to the page, so keep them unique; all text is HTML in the composition (no ffmpeg text
filters are assumed).

---

## 5. Sound

The default for these clips is the recording's own sound and nothing else. The setup answer decides (see "Your
setup" in `SKILL.md`). When the creator wants more:

- **Sound effects**: key moments only (a soft whoosh as an animation comes in, an accent on the big reveals), never
  one per element. They sit well under the voice: whooshes peak about -29.5 dBFS and pops about -32.5 when the voice
  peaks near -3. The creator's sound-effects folder and the role map (`sfx_map.json`) are in the profile, made at
  setup with `scripts/sfx_probe.py`. If there is no pack, the clip is delivered without effects: say so, do not
  invent sounds.
- **Music**: only a track from the creator's music folder or favourites list (`music.json` in the profile), never a
  guess. A quiet bed about 11 dB under the voice, started where the track settles in, 0.4 s fade in, 1.5 s fade
  out. When music is used, deliver two versions: with and without.
- Mix after the render and before the loudness pass. If the pack's `business-short-form-reels` skill is installed,
  its mixer places effects by role; otherwise mix with ffmpeg, for example a music bed:

  ```bash
  ffmpeg -i "<render>" -ss <music start s> -i "<track>" -filter_complex \
    "[1:a]volume=-24dB,afade=t=in:d=0.4,afade=t=out:st=<clip length - 1.5>:d=1.5[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 320k "<with music>"
  ```

  Measure before trusting the number: the bed should sit about 11 dB under the voice (compare mean volume with
  `ffmpeg -i <file> -af volumedetect -f null -`).
- The voice itself is never processed beyond the loudness step.

---

## 6. Review (every render)

Look at the rendered file, not just previews.

Picture
- First frame: the speaker is already talking and the layout is in place (in 9:16 the text hook is on). Last frame:
  not a blink, a look down at notes or a half-faded graphic.
- Either side of every shot change (`ffmpeg -ss <t> -i "<render>" -frames:v 1 out.jpg` one frame before and after):
  a clean hard cut, no single-frame flash of the other layout, the caption in the right place for each shot.
- Captions: every line of `captions.txt` is there and spelled right; one line only; readable at phone size; never
  on the face; emphasis words in the emphasis font and the accent colour, figures in the caption font; nothing
  clipped at the frame edge.
- Graphics: each has landed on its word, is spelled right, sits inside the frame, overlaps nothing, matches what is
  being said, and leaves when the speaker moves on. The accent colour is the brand's everywhere. Fonts are the real
  ones.
- 16:9: no `WARN FACE` in the build, and by eye no graphic touches the face, head or a gesturing hand.
- No BIG jump cut visible on the speaker; no sliver of a dropped take.
- Then watch it once at normal speed, or read a 2-frames-a-second contact sheet of the whole clip for rhythm.

Sound
- Starts on the first word and ends after the last, with the last word's sound complete.
- In sync with the picture at the start and at the end.
- No clipping. After `05_loudness.py`: about -14 LUFS, peak under -1 dBTP.

Fix, render again, review again until a pass is clean.

---

## 7. Defaults this style avoids (change only if the creator asks)

The speaker on the top half in split · opening on split · graphics across the speaker's chest or over their face ·
pills, text or number circles behind the head · square boxes and 2x2 grids · a rolling-digit counter · collaborator
cursors on a document mock-up · fast slide or whip entrances and bouncy pops · headlines or sub-lines over
animations · a sound on every element · 3D · stacked or multi-line captions · the emphasis font on numbers · a
slow zoom and punch-ins in the same 16:9 clip · cropping a person out of their own photo or clip.
