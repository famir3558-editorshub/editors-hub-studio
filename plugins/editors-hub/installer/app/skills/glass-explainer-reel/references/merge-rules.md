# What came from where (the two styles merged here)

Sources: `explainer-panel-reel` (the edit) and `business-short-form-reels` (the graphics). Where they
disagree, the panel edit wins.

## Kept from the explainer panel reel, unchanged
- Two layouts only: full-frame close-ups and the panel layout, joined by hard cuts.
- The speaker's cut-out rising above the bottom panel; their real background inside the panel; the panel's geometry
  (x 70-1010, top y 1407, radius 36, running off the bottom).
- Black frame with the dot grid; rectangular composition; heading at y 190; graphics area y 380-1190, x 65-1015.
- Heading behaviour (written on from the left, accent block or an emphasis-font accent word with underline, numbered
  section bars).
- Captions: every word, one line of 1-3 words, caption font tracking -50, emphasis in the emphasis font and accent
  colour, figures in the main font and accent colour, never stacked; positions under the chin / above the head.
- Switches: on edit cuts, BIG cuts on switches; full frame 20-30% of the runtime; close-ups 1-8 s; panel
  stretches 2-20 s; a close-up at least every ~20 s.
- Speech sync: an element lands ON the word that names it (entrance starts 0.15 s early); something new every
  ~3-4 s in a panel stretch; an idea's graphic clears when the speaker moves on; one accent focal point.
- The whole pipeline: prep, ElevenLabs transcript, tight cut, verification by re-transcription, cut render, crops
  and cut-out, captions, export settings, the review script and checklist.

## Brought across from the business reel, adapted to the panel's graphic area
| Business reel | Here |
|---|---|
| A signature graphic per reel for its core idea | Same rule; built from engine parts or `s.raw`, inside y 380-1190 |
| Real people: uncropped photos / footage in a card of the asset's shape | `K.person` |
| Simple hand-built YouTube channel card, no banner, real picture | `K.ytchannel` (rectangular glass card) |
| Real reel covers (the creator's and other creators') | `s.grid`, `s.img`, the creator's covers in `assets/reels` |
| Instagram notification banners, newest on top | `K.notifs` (focus-pull drop, no spring) |
| "Save it for later": Reel in a phone, tap, "Saved" toast | `K.saved` |
| Google Docs window scrolling to and highlighting named headings, no cursors | `K.gdoc` |
| Anything quoted goes in a real interface, not a pill | `s.typed` (glass card), `K.gdoc` |
| Drawn graph with a dot riding the front, markers | `K.graph` (in a glass chart frame) |
| Plain ticking counter that takes the accent colour on landing | `s.count`, `K.ytchannel(count=...)` |
| Comparison cards; positive green, negative red | `K.versus`, `col=K.GREEN / K.RED` |
| Light sweep across the element that becomes active | `s.hot` (adds the sweep), `s.sweep` |
| Liquid Glass on cards | Kept as a finish only, on RECTANGULAR cards (radius 6-10), toned down |
| Light orbs behind the glass | Two faint orbs per scene inside the graphics area |
| Text in graphics kept modest; few labels; do not repeat the caption | Same |
| Quiet sound effects on key moments (~40 per 90 s), TRIM -8.5 | `sfx.json` + `09_render.py`; the creator's own pack, played by role from `sfx_map.json` |
| Music only when asked, two versions | `09_render.py --music`; never assumed |
| Real assets first; list everything invented | `find_assets.py`, `E.asset`, `review.json`; **and do not stop to ask** |

## Deliberately NOT imported
- The three-mode structure and the rules about rotating modes; split-screen halves; full-screen animation sections.
- The mandatory opening text hook over the face; the reel-cover carousel around the speaker; graphics behind the head.
- One-word captions; lower-case captions; any alternate caption font; 2-4 word captions on a seam.
- The earlier entrance timing (elements starting ~0.6 s before the word) and whole-graphic focus pulls on switches.
- The slow zoom out on the footage (off, as in the panel skill; `E.ZOOM_FULL = 1.04` exists if the creator asks).
- "Boxes are pills, pills stack vertically": reversed here. Cards are rectangular; no stacked oval pills.
- The accent glow / grain background: the frame stays dark with the dot grid.
- The agenda box (the panel skill's numbered list and section bar do that job).
- Spring drops, 3D tilts, `rig` rotations.
- "Ask before every design choice": replaced by the creator's working rule (default: finish the best version, then report what to review).
- The HyperFrames catalog check before each build (optional here, not a step).

## Where a business graphic needs more room than the area gives
Redesign it for 950 x 810 px, or split its reveal across successive panel scenes with the close-ups between them
falling on their normal cuts. Never widen the area, never take the full frame, never move a switch to suit a graphic.
