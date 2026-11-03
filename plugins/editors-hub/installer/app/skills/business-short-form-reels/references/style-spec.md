# Business Short Form Reel: the default style spec

This is the style the pack ships with. It is a starting point that has been tested on real reels: use it as written
until the creator's own references and corrections say otherwise. Those live in
`~/.claude/creator-profile/notes/business-short-form-reels.md` under `## Style overrides`, and they win.

Brand values (the accent colour, the fonts) are the creator's, set at setup and listed in `SKILL.md` under
"Your setup". Below they are called the accent colour, the main font and the emphasis font.

---

## 1. The cut
1. Transcribe with word-level timings (the transcriber chosen at setup; ElevenLabs is the most accurate).
2. Remove every silence and breath. Cuts are sharp, with no gap at the start or end of a sentence, and never clip a
   word.
3. Remove mistakes: failed takes, repeated words, throat clears, off-script chat. Keep the last complete take of each
   section.
4. A scripted mid-video CTA and an end CTA are both kept.
5. Re-transcribe the finished cut and read it as a script before building anything.

## 2. Format and safe zone
1. 9:16, 1080 x 1920, 23.976 fps. Built and rendered in HyperFrames only.
2. Keep roughly 65 px clear all round, and keep anything that must be read inside y 270-1500 (captions above y 1250)
   so the platform's interface does not cover it.
3. Every graphic is centred horizontally.

## 3. Structure
1. Three modes: **creator full screen**, **split screen**, **full-screen animation**.
2. Always open full screen on the creator.
3. First cut goes to split screen, then full-screen animation, then repeat that rotation. The order bends where the
   edit cuts demand it.
4. Split screen: animation on the top half, the creator on the bottom half. The camera is cropped so the whole face
   sits above the platform's bottom interface.
5. Full-screen animation: aim for about 3 seconds and 5 at most, but it can run longer when that is where the cuts
   fall.
6. Creator full screen: about 7 seconds maximum, and never without a graphic.

## 4. Cut alignment
1. No block of the creator (full screen or split) may contain a visible jump cut. Every edit cut is either a mode
   switch or hidden under a full-screen animation.
2. When cuts come very close together, ignore them (leave them visible) until the block adds up to about 3-5 seconds,
   then switch on the next cut. No 1-2 second blocks just to follow every cut.
3. Switches may land a little early or late against the sentence to hit the cut.
4. Every switch is set from the exact frame number (frame / 23.976 - 0.002 s). Rounding to the millisecond puts it one
   frame late.
5. Verify on the rendered file by comparing frames against the camera footage, not by eye.

## 5. The opening
The opening must grab attention; that is the only fixed rule. Pick whatever is best for this video. If a custom
graphic would do that better, build one.
1. **Text hook**, on screen from the first frame, at the top just above the head, 2 lines maximum.
   - Line 1: plain white, main font bold, 84 px, soft shadow.
   - Line 2: black, main font bold, 80 px, on a squared white block.
2. One opening option, a **reel carousel around the creator**: eight reel covers (about 300 x 532) on a tilted ring.
   Large across the chest in front, smaller as they swing behind the head. They whoosh in with motion blur and fade
   out with the hook at about 2.9 s.
3. Covers can be other creators' reels as well as the creator's own.

## 6. When the creator is full screen
1. Slow zoom out, barely noticeable: starts 5% zoomed in and eases back to 100% over the block. The graphics do not
   zoom with the footage.
2. **Nothing sits behind the head except real reels or real screenshots.** No pills, text or number circles there.
3. Pills and stacks sit below the caption word, centred (600 x 100 px, 50 px text), three at most.
4. Anything quoted gets a real interface: a script line in a Notion page or Google Doc, a comment or DM as an
   Instagram notification.
5. Captions: one word at a time under the chin, lower-case, white, main font bold (92 px). Two to five key words per
   block switch to the accent colour and the emphasis font. Numbers stay in the main font.

## 7. Split screen and full-screen animation
1. Captions: 2-4 words at a time, white, main font bold, sentence case, no punctuation, exact words spoken.
   - Split: on the seam between the panel and the creator.
   - Full-screen animation: under the graphic, at about y 1180.
2. Split graphics fill roughly 75-90% of the panel width.
3. Full-screen graphics are smaller and centred (about 84% scale), with the dark background around them.
4. **No headline, kicker or sub-line text on any animation.** Only text that is part of the graphic (labels, UI text,
   numbers).
5. A different kind of graphic in each scene. Framework parts appear one at a time.
6. While a mechanism is walked through, a squared agenda box at the top of the screen tracks which part is active.

## 8. Brand
1. Background: the dark background colour with a soft glow in the accent colour and very fine grain. No coarse grain,
   no grid.
2. The accent colour only on the focal element. Off-white for text. Grey for small labels.
3. Fonts: the main font, bold, tight tracking, for everything; the emphasis font for emphasis words only. **Numbers
   are always in the main font.**
4. Positive is green (#2FA65A) and negative is red (#B3261E), every time. One accent of deep red is allowed for the
   odd one out: pulse twice, then stay red.

## 9. Graphic language
1. **Boxes are pills, and pills stack on top of each other.** No 2 x 2 grids, no square tiles. Icon + label inside
   each pill.
2. **Liquid Glass** on pills and cards in the animations only: translucent, blurs the soft light drifting behind it,
   bright top rim. Pills on the creator stay solid so they read. A funnel is never glass.
3. **Always prioritise real assets** over drawn stand-ins: real client screenshots, real photos, real reel covers, the
   creator's real profile picture.
4. A person who is mentioned is shown with real footage or photos, whole and uncropped, in a card that matches the
   clip's shape.
5. Each reel gets its own signature graphic for its core idea. Few text pills: if a graphic can show it, build the
   graphic.
6. No 3D.

## 10. Real interfaces
1. **Comments or DMs mentioned** -> iPhone-style Instagram notification banners, dark mode: Instagram badge on the
   avatar, "now", real wording. Each banner drops in on a spring; the newest lands on top and pushes the pile down.
   The creator's own DM uses their real profile picture.
2. **A document mentioned** -> a real-looking Google Docs window in white: blue Docs icon, title, menu row, Share
   button, the creator's profile picture, toolbar, white page. The page scrolls to each heading named and highlights
   it. Use it on every doc CTA in the reel. No collaborator cursors.
3. **"Save it for later"** -> an Instagram Reel inside a phone; a finger tap presses the bookmark, it fills white, a
   "Saved" toast appears.
4. **YouTube** -> a simple channel card built by hand (picture, name, handle, subscriber count, button), no banner.

## 11. Motion
1. Entrances: **focus pull**. Elements start heavily blurred and slightly large (108%), and snap into sharp focus in
   about half a second. The whole graphic does the same at each switch.
2. Elements land just ahead of the word that names them (they start about 0.6 s before it).
3. Exits: soft fade out over about 0.3 s just before the switch.
4. No bounce or overshoot on pills and cards.
5. A band of light sweeps across a pill when it becomes the active one.
6. Counters tick up as a plain number and take the accent colour on landing. No rolling-digit wheel.
7. Graphs draw on, with a dot riding the front of the line and dots popping at the markers.

## 12. Sound
1. **Sound effects**, key moments only (about 40 per 90 s): a soft whoosh each time an animation comes in, plus
   accents on the big moments.
2. Opening carousel: one long swirl, plus a soft tick each time a cover crosses the front.
3. Sounds come from the creator's own pack, mapped to roles at setup (`sfx_map.json`).
4. Level: well under the voice. Whooshes peak about -29.5 dB, pops about -32.5 dB (a voice peaks near -3 dB).
5. **Music**: follow the music rule chosen at setup. When used: a quiet bed about 11 dB under the voice, started where
   the beat drops, 0.4 s fade in, 1.5 s fade out. Sound effects go on top.
6. When music is used, **deliver two versions: one with music and one without** (sound effects in both).

## 13. Working with the creator
1. Follow the working style chosen at setup (consult on design choices, or build first and report).
2. **Always check the HyperFrames catalog** for styles and effects that would suit the video being edited.
3. **Any screenshot dragged in: assume it should be animated into the reel, but ask first** (where it goes and how it
   should move).
4. Where real details are missing (usernames, comment text, captions on mock-ups, doc lines), use generic defaults and
   list every one at the end so real ones can be swapped in.
5. Deliver: the master in the output folder and a phone-size copy sent in chat (with-music and without-music versions
   when music is used).
6. Check the rendered file, not just previews: frames either side of every switch, nothing too close to the frame
   edge, and the cut alignment.

## 14. Defaults this style avoids (change only if the creator asks)
- The creator on the top half in split screen.
- Opening on split screen.
- Graphics across the chest when the creator is full screen; pills or text behind the head.
- Square boxes and 2 x 2 grids.
- Rolling-digit number wheel.
- Collaborator cursors on the Google Doc.
- Fast slide-in or whip entrances; bouncy pops.
- Headlines over animations.
- Sound effects on every single element (kept to key moments).
- 3D.
