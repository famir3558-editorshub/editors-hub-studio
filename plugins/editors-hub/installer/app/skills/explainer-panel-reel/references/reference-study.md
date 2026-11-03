# The panel style: layout, pacing and motion

The look this skill produces was taken from a study of two 9:16 explainer reels (73 s and 124 s, 25 fps) by other
creators. This file is the written result of that study: the measurements and rules the engine is built on. Their
accent colour, logo, handle and examples are not part of the style and are never reused: the system is rebuilt in the
creator's own brand. Measurements are on the 1080x1920 frame.

## Layout
- **Two layouts only**, joined by hard cuts: a full-frame close-up, and a black frame with the speaker in a panel at
  the bottom.
- **Panel**: x 70-1010, top edge y ~1407, runs off the bottom of the frame, top corners rounded (~36 px), faint light
  edge. It shows a wide shot with the room visible. The speaker's head (and a raised hand) rises ~65 px above the
  panel's top edge: they are cut out and layered over the black.
- **Black area**: pure black with a faint dot grid. Heading at the top (two centred lines, bold sans, tight
  tracking; line 2 on a solid accent block; some words in a serif italic). Graphics fill the middle.
- **Close-up**: head top ~14% down the frame, head ~42% of the frame height, slightly soft background.
- **Caption**: one line, 1-3 words (mostly 1-2), bold sans, white, tight tracking, at the same height in both
  layouts (y ~1287): under the chin in the close-up, in the gap above the head in the panel layout. Emphasised words
  switch to the serif italic in place. Captions run through graphics sections without exception.
- An optional small platform glyph and handle sits beside the graphics and moves between two positions.

## Pacing
| | Reference 1 (73 s) | Reference 2 (124 s) |
|---|---|---|
| Opens on | panel, heading and first graphic inside 1 s | panel |
| Full-frame share | 20% | 31% |
| Close-up length | 1.5-6.2 s | 1.0-7.8 s |
| Panel stretch length | 3.3-21.6 s | 2.2-12.3 s |
| Layout changes | 11 | 25 |

Close-ups carry direct statements, punchlines, transitions and the call to action. Panel stretches carry the
explaining. Inside a panel stretch something new appears every 1-3 s.

## Motion
- Headings are written on from the left; the accent block grows with line 2.
- Elements resolve from a blur at slightly reduced scale (a focus pull), ~0.3-0.5 s, on the word that names them.
- Diagrams grow part by part: node, line drawn to a box, second line, dashed relation, label.
- A list is shown whole with unreached items blurred; the current item takes a bar with an accent edge, which then
  becomes the section heading.
- Screenshots and reel thumbnails arrive one after another in a grid; counters tick; text is typed into a card.
- Existing graphics shrink or slide aside to make room; old ones fade when the idea changes.
- One accent-coloured element at a time; everything else white hairlines on black.
- No transitions between layouts: hard cuts, usually on an edit point.

## How it maps to this skill
| In the studied reels | Here |
|---|---|
| their accent colour | the creator's accent colour (profile `accent`) |
| serif italic words | the creator's emphasis font, in the accent colour (profile `font_accent`) |
| bold grotesque | the creator's caption font (profile `font_caption`, or the main bold), tracking -50 |
| their handle / logo | the creator's handle, only if they asked for the watermark |
| their examples and screenshots | the creator's content and real assets |
