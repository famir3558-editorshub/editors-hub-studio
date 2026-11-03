# The intro: highest priority

The first section gets the highest editing density and the most sophisticated motion in the video. Viewers decide in these seconds whether the click was right.

## The opening rules

1. **A meaningful visual change within the first 3 seconds.** Do not leave the viewer on an unchanged talking-head shot for 3 seconds or more. Ideally cut to a motion graphic or visual explanation of exactly what the creator is saying.
2. **The opening flows**: talking head, motion graphic, talking head or split screen, next visual. Vary the exact treatment with the content.
3. **Something develops every 2-5 seconds for the first 30 seconds**, then the edit settles into sustainable long-form pacing.
4. **The video starts on subtle camera movement**: a very gentle zoom in or zoom out (`E.OPEN = "in"` or `"out"`), smooth and premium, felt rather than noticed.
5. **The graphic must support the narration**, not act as a pattern interrupt. The 2-5 second rule never justifies an irrelevant visual: when nothing useful exists for a moment, use a punch-in, a reframing, a composition change or a word of emphasis.

A graphic that keeps building (cards separating, nodes landing one by one) counts as development while it builds. A bottom title on its own does not count as the first change: it is text over the same shot.

## What the intro must do

1. **Confirm the click.** What the title and thumbnail promised is visibly on screen within the first few seconds. Ask the creator for the title and thumbnail if they are not in the folder; if they are not decided yet, use the promise from the content map.
2. **Create curiosity.** Open a question the video will close.
3. **Establish what the viewer will learn**, as a structure they can see.
4. **Show production quality immediately.** Motion graphics from the very first seconds, not just a line of text.
5. **Prevent early drop-off.** No slow start, no logo sting before the hook, no dead air.

## A shape that works (adapt it, do not copy it every time)

| Time | Moment | Treatment |
|---|---|---|
| 0-3 s | The hook line | The creator full screen on the subtle opening zoom, perhaps with a bottom title of the promise (`K.title`), then **before 3 s** cut to a motion graphic of what the creator is saying, or punch in on the key word if nothing useful can be shown yet |
| 3-8 s | The hook pays off | The graphic resolves, back to the creator or into a split with the real thing |
| 5-15 s | Why believe the creator / the stakes | The strongest real evidence in a split: a real result, the real example, a real screenshot. Counter on the number |
| 15-30 s | What you'll learn | The preview (below), full screen |
| 30-45 s | Hand-off into section one | Back to the creator. If a framework runs the video, show its map once here so the whole video has a spine |

Aim for a change every 2-5 seconds through the first 30, mixing states, graphics and punch-ins. Then visibly slow down: the contrast is part of why the intro feels premium.

## "What you'll learn": visualise the structure

When the creator previews several things ("there are five things you need to understand about fat loss"), do **not** put "5 THINGS ABOUT FAT LOSS" on screen. Build a visual system that *is* five things:

- One object appears.
- It duplicates.
- The copies separate through depth (or simply apart, when depth is off at setup).
- Five now exist, and they may rotate, stack, expand, slide or move through Z.

`K.preview(sid, a, b, n, variant, labels, reveal, t_split, t_reveal)` does this. The objects change per video:

| Variant | Objects | Suits |
|---|---|---|
| `cards` | Glass cards in a 3D arc (a flat row when depth is off at setup) | Principles, mistakes, lessons |
| `pills` | A vertical stack of pills | Steps, rules, a checklist |
| `tiles` | Square tiles at alternating depths | Tools, features, categories |
| `docs` | Paper pages fanning out of a stack | Scripts, templates, chapters, documents |
| `orbs` | Circles on a ring | Parts of a cycle or a system |

Squares, rectangles, floating panels, windows and abstract shapes work the same way. When the topic suggests its own object (reel covers for a video about reels, dumbbells for training, coins for money), build it once with `K.custom` using the same choreography: one, duplicate, separate through depth. **Do not use the same variant in consecutive videos**; check the last project's `build.py` if unsure.

## Do not reveal everything

The preview shows *that* there are five and *that* they are distinct, without handing over the content. Options, all supported:

- **First one revealed, the rest obscured.** `labels=["Protein"], reveal=1`: card 1 shows its name and gets the accent-colour edge; cards 2-5 show blurred lines.
- **All obscured.** `reveal=0`: numbers only, contents blurred.
- **Abstract contents.** Icons or shapes instead of words (custom).
- **Too quick to read.** Reveal labels and move on within a second (custom timing).

Never write the five answers in a list in the intro. If the creator says them all aloud in the intro, still keep the cards to short labels and let the later sections do the explaining; and when each section arrives, bring back the **same object** (card 3 opens into section 3) so the preview pays off.

## Hook visuals that confirm the click

- The real thing the video is about, shown at once: the thumbnail-worthy image, the result, the product, the person.
- A number with a counter when the promise is a number.
- A before / after when the promise is a change.
- Floating real examples either side of the creator's head (thumbnails, posts, screenshots) when the video is about a category of thing.
- The signature graphic in its simplest form, to be completed later in the video.

## Checks for the intro

The audit warns if there is no meaningful change in the first 3 s, if anything in the first 30 s sits unchanged for more than about 5 s, if there are fewer than 5 scenes in the first 45 s, and if the intro is not clearly denser than the body. `09_review.py` writes one frame per second of the intro: read that strip as a stranger would. Does it look premium from frame one? Is the promise on screen? Is the structure clear and the answer still hidden?
