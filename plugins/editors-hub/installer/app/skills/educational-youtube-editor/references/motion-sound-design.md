# Design system, motion, text and sound

Animations vary; the design system does not. Everything below is set once in `yt_engine.py` (the constants at the top and `BASE_CSS`) so every scene in a video, and every video, shares it. Change a value there, not per scene.

## The design system (visual consistency)

| Token | Value | Where |
|---|---|---|
| Corner radius | 28 px cards, image frames, panels · 16 px small inner elements · full round for pills. **The creator's footage has no corners, border, shadow or frame, ever** | `RADIUS`, `RADIUS_S`, `--r`, `--rs` |
| Shadow | One soft black shadow for every lifted object: `0 34px 90px rgba(0,0,0,.55), 0 8px 24px rgba(0,0,0,.35)` | `--sh` |
| Border | 1 px, `rgba(242,240,236,.14)`; a little brighter on images with dark edges | `--line` |
| Spacing | A split divides the frame exactly in half with no margin or gap; graphics fill about 90% of their half and 84% of a full frame; nothing touches the edge | `FILL` |
| Backdrop | The dark background colour, a soft glow in the accent colour from the lower left, very fine grain. No grid, no coarse grain | `#bg`, `#fgbg` |
| Colour | The accent colour on the focal element only · the off-white text colour · grey labels · green `#2FA65A` positive · red `#B3261E` negative (the creator's exact values are in "Your setup" in `SKILL.md`) | `--o`, `--paper`, `--grey`, `--good`, `--bad` |
| Type | The main font, bold, tight tracking, for everything · the emphasis font in the accent colour for accent words · interface mock-ups in the system interface font (`--sf`), because a real interface uses it · figures always in the main font | `.B`, `i.a` |
| Surfaces | `.card` (solid dark) and `.glass` (Liquid Glass: translucent, bright top rim). Glass only over the dark backdrop; over bright footage use solid, or it washes out. A funnel is never glass | `.card`, `.glass` |
| Illustration style | Flat, rounded, two-tone: paper-grey shapes, one focal shape in the accent colour. People are the simple head-and-shoulders icon | `.dot`, `.blk` |
| Depth | One perspective (1700 px) for every 3D scene. A setup answer switches depth off altogether (`DEPTH`) | `.p3` |

Text sizes on the 1920 frame, before the engine scales a piece into its state: labels and row titles 34-50 px, small tags 21-30 px, hero numbers up to about 210 px, a single emphasis word up to about 190 px, bottom titles 78 px. Text inside graphics stays modest: when in doubt, smaller.

## Motion

Motion should feel smooth, premium, intentional, modern, clean and physically believable.

| Rule | How |
|---|---|
| Entrance | **Focus pull**: starts blurred and slightly large (108%), resolves sharp in about 0.5 s, `power3.out`. `E.enter(sel, t, "focus")` |
| Timing | Elements land just ahead of the word: they start `LEAD` (0.35 s) before it. Time from the words with `E.w()`, never by eye |
| Exit | Soft fade, about 0.3 s, before the scene ends |
| State changes | Into a split the creator glides: the frame divides and the footage slides so the creator sits centred in their half, over 0.8 s, `power3.inOut`. On an edit cut, switch hard (`cut=True`) |
| Easing | `power3.out` in, `power2.in` out, `power3.inOut` for moves, `sine.inOut` for slow drifts. Linear only for a constant drift |
| Depth | Z movement for separation and emphasis; a slight rest angle on a frame; layers at different depths. See component-library.md |
| Momentum and overshoot | A small settle (`back.out(1.25)`) on small things that pop into place (a dot, a highlight box). Never on cards, pills, panels or images |
| Blur | In the focus pull, and on things passing through depth. Not as a decoration |
| Parallax and layering | Layers move different distances in a collage or a 3D stack |
| Masking | Pages scroll inside their browser window; images drift inside their frame |
| Stagger | 0.05-0.1 s between siblings |
| Life while on screen | A 4-5% scale drift on images; a slow rotation easing on a tilted frame; nothing is frozen, nothing is busy |

Avoid: cheap preset-looking animation, bounce on anything large, random zooms, spinning, whip pans, wipes for their own sake, anything that pulls the eye away from what the creator is teaching. A full-screen graphic never scales past the frame (a centred drift of at most about 1.06).

## Camera movement on the creator

Simulated camera movement, not an editing effect. Two tools only:

| Move | What | Rules |
|---|---|---|
| **Slow drift** (automatic) | One move per stretch of uncovered talking head: 100% towards 103-106% (longer stretch, larger move), or the reverse. Stretches alternate direction. The video opens on it (`OPEN = "in"` or `"out"`) | At most 45 s per move, then it holds. Never in then out. Reset happens hidden under a full-screen graphic or inside the glide to a split. The viewer should not consciously notice it. `DRIFT = (0, 0)` turns it off |
| **Punch-in** (`E.punch(a, b, "reason")`) | A hard cut-in around the creator's face, and back. The strength is a setup answer (pack default 112%; `PUNCH`) | Motivated only: important statement, strong opinion, reveal, change of thought, emotional moment, key takeaway. Best started on an edit cut. Occasional |

No other zooms: no zoom on every sentence, no bouncing scale, no zooming in and out.

## Text

Do not turn the video into subtitles or blocks of text. The narration already carries the sentence; the graphic carries the emphasis.

- Text highlights: important words, numbers, framework names, steps, statistics, contrasts, key conclusions.
- Instead of "Most creators are focusing too much on getting views when they should focus on building trust", show **VIEWS**, struck through, then ***Trust***.
- No headline, kicker or sub-line explaining a graphic. Only text that is part of the graphic: labels, UI text, numbers, list items, name tags.
- No em or en dashes on screen. Commas, full stops, a middle dot.
- Accent at most one or two words per scene in the emphasis font. Whole words only. Anything containing a digit stays in the main font (the kit does this automatically).
- Sentence case or lower case in labels; capitals only for a single emphasis word.

## Sound design

Subtle sound supports movement. It should never sound like a gaming montage.

| Moment | Sound | Notes |
|---|---|---|
| A graphic or state arrives | Soft whoosh (`woosh`, `swoosh`, `swish`) | One per arrival, not one per element |
| A small element lands, a highlight box, a list row | Soft pop (`pop`) | Every second or third item in a run, not every one |
| A counter or graph | `data` | Under the count |
| The right answer, a winner, a gap closing | `accept` | Once |
| Something becomes the active one, a reveal | `shine` | Sparingly |
| Words changing in an emphasis swap | `dtext` | |

The names in the table are **roles**, not files. Each role is played from the creator's own sound pack through `sfx_map.json`, made at setup with `scripts/sfx_probe.py` (only `woosh` and `pop` are needed; a missing role falls back to one of those). With no sound pack there are no sound effects: say so in the report and never invent or download sounds.

The kit places these for you (`E.sfx(t, name, level)`); the render script thins them so no two fall within 0.35 s and mixes them far under the voice (whooshes peak around -29.5 dBFS, pops around -32.5; a voice peaks near -3). Expect roughly 8-15 a minute in a normally paced edit and more in the intro. If it is noticeable, it is too loud. Stories get fewer, or none.

**Music** follows the creator's music rule ("Music" in `SKILL.md`). `ask`, the pack default: asked every time, never assumed, whether and which track. `pick`: choose from their music folder or their favourites (`assets/music.json` in the creator profile, if it exists) and say which. If there is music: `08_render.py --music "<file>" --music-start <s>` lays a bed about 11 dB under the voice (-39 dB mean), 0.4 s fade in, 1.5 s fade out, and writes a with-music file beside the normal one. Deliver both.

**The voice is never processed.** The cut's audio track is carried across as it is. If the creator cleans up their audio in a tool of their own and wants the cut-only audio for that, it is `edit.wav` in the work folder.
