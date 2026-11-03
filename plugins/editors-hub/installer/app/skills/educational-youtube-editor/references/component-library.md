# Component library (`yt_kit.py`)

Reusable, parameterised primitives so a 40-minute edit is assembled, not hand-drawn, and still does not look like the last one. Every component returns a *piece*; hand it to a state:

```python
import yt_engine as E, yt_kit as K
E.init(__file__); M = "assets/media/"
t = E.w("stripe", 300)                                              # when it is said
E.split(K.browser("stripe", t - 0.3, t + 6, M + "stripe-home.png", "stripe.com", hl=(6, 22, 48, 30, t + 2)),
        why="example", score=4, tier=2)                             # tier = how real the asset is (asset-retrieval.md)
E.float_(K.term("cac", t2, t2 + 4, "Customer acquisition cost", "what one new client costs you"), why="explain", score=3, side="left")
E.full(K.flow("chain", t3 - 0.3, t3 + 7, ["Attention", "Trust", "Demand", "*Sales*"], [t3, t4, t5, t6]), why="explain", score=5)
E.build()
```

State calls: `E.float_(piece, why, score, side="left"|"right", zone="bottom"|"top", dim=0-0.6)` · `E.panel(piece, why, score, side)` · `E.split(piece, why, score, side, cut=False)` (a genuine 50/50 split; there is no card style) · `E.full(piece, why, score, cut=False)` · `E.punch(a, b, "reason")` (a motivated punch-in on the creator; not a scene). `side` is the side the **graphic** is on. Pieces are designed at a fixed size and scaled to fit the state, so any component works in any state.

Common arguments: `sid` (unique id), `a`, `b` (on-screen window, cut-timeline seconds), `variant` (leave `"auto"` to rotate). Accent a word with `*asterisks*`.

## Real-world evidence

| Component | Use it for | Variants |
|---|---|---|
| `K.frame(sid,a,b,src, tag, ratio, w, video=)` | One real image, screenshot or clip, presented as a designed object: rounded corners, soft shadow, slow life | `float` flat with drift · `tilt` arrives from depth, rests at a slight 3D angle · `lift` rises in · `polaroid` photo print (people, places, memories) |
| `K.browser(sid,a,b,src,url, scroll, scroll_t, hl)` | A real website in a floating browser window. `scroll` moves the page to what the creator is talking about; `hl=(x%,y%,w%,h%,t)` boxes the exact thing | `float` · `tilt` |
| `K.collage(sid,a,b,srcs, times, ratio, tags)` | Several real examples at once (a channel's thumbnails, a set of posts, a product range), arriving one by one | `fan` · `scatter` (layered depths) · `grid` · `stack` |
| `K.person(sid,a,b,src,name,role, ratio, video=)` | A named person: real photo or footage, whole, with their name | `portrait` · `circle` |
| `K.social(sid,a,b,name,handle,text, avatar, media, stats)` | A real post quoted exactly, as the post | one look |
| `K.ytvideo(sid,a,b,thumb,title,channel,meta)` | A real YouTube video: thumbnail, title, channel | one look |

Frames take the image's own shape unless you pass `ratio`. Every still is placed by `E.img`, which finds the faces and crops around them (asset-retrieval.md, "Protect faces when cropping"). Pass `video=<start second>` to play a clip, muted.

## Structure and relationships

| Component | Use it for | Variants |
|---|---|---|
| `K.preview(sid,a,b,n, labels, reveal, t_split, t_reveal)` | "What you'll learn": one object becomes N through depth, contents held back (intro-playbook.md) | `cards` · `pills` · `tiles` · `docs` · `orbs` |
| `K.flow(sid,a,b,steps,times)` | A chain where each thing becomes the next. Nodes land on their words, connectors draw, the live node is lit | `down` · `across` · `loop` |
| `K.framework(sid,a,b,steps, active, times)` | **The** map of a framework. One variant per framework, reused on every return with `active` lit | `rail` · `cards` · `ring` |
| `K.tracker(sid,a,b,steps,active)` | The small 1 2 [3] 4 5 marker at the top while the creator talks through a stage (`zone="top"`) | chips |
| `K.timeline(sid,a,b,items,times)` | Dates or stages in order; items are `(label, sub)` | `line` · `steps` |
| `K.section(sid,a,b,n,name,total)` | A major topic change (occasionally) | `number` · `card` · `rail` |

## Numbers and comparisons

| Component | Use it for | Variants |
|---|---|---|
| `K.stat(sid,a,b,value,label, t, frm, pre, suf, tone, pct)` | A number that matters. Counts up plainly on the word, then takes the tone colour (`good` green, `bad` red, `o` the neutral accent colour) | `count` · `ring` · `bar` (the last two need `pct`) |
| `K.graph(sid,a,b,pts, t, dur, label, tone, xlabels)` | A trend, with the real figures as spoken | `line` (draws on, ends on a dot) · `bars` |
| `K.compare(sid,a,b,left,right,tA,tB, win, t_win)` | Two things against each other; `win` turns one side green and the other red | `versus` · `columns` (crosses and ticks) · `beforeafter` (two real screenshots, no arrow) |

## Words (use sparingly: emphasis, not subtitles)

| Component | Use it for | Variants |
|---|---|---|
| `K.emph(sid,a,b,words,times)` | The two or three words that carry the point | `swap` (VIEWS struck out, replaced by *Trust*) · `stack` |
| `K.title(sid,a,b,text,label)` | Bottom-centre line over the creator (`zone="bottom"`): the promise, a key conclusion | one look |
| `K.term(sid,a,b,text,sub)` | A named idea pinned beside the creator while they define it | chip |
| `K.rows(sid,a,b,items,times)` | A list the creator walks through, a row per item; titles of two to five words | `rows` · `checks` · `numbered` |
| `K.quote(sid,a,b,text,who,src)` | Someone's exact words: a study's finding, a customer, a named person | `card` · `big` |

Text should highlight important words, numbers, framework names, steps, statistics, contrasts and key conclusions. The audit flags any scene with more than 14 words on screen and any plan that is over 40% text-led.

## Explainer illustrations and visual metaphors

Clean illustrations that make an abstract idea tangible, and move in a way that carries the meaning.

| Component | The idea | What the viewer sees |
|---|---|---|
| `K.funnel(sid,a,b,stages,keep,times)` | People falling out of a funnel | Solid pills narrowing; people drop out red between stages |
| `K.crowd(sid,a,b,t_hot,n,label)` | A crowded market, everyone the same | A field of identical cards; one lifts out in colour |
| `K.compound(sid,a,b,times,label)` | Content / trust / skill compounds | Pieces landing, each column taller than the last |
| `K.spread(sid,a,b,t_split,n,label)` | Spreading yourself too thin | One solid thing splits into many, smaller and fainter |
| `K.gap(sid,a,b,t_move,close,left,right)` | Distance between you and the audience (no trust), or the gap closing | Two parties drifting apart, or coming together with a bridge |
| `K.grow(sid,a,b,times,start,per,label)` | Posting builds an audience | Content pieces travel to an audience that grows as each lands |

**Do not interpret everything literally.** For any abstract line, ask what physical thing behaves the same way, then animate that behaviour. When no component matches, build it:

```python
body = '<div id="x-a" class="blk o h" style="left:100px;top:200px;width:200px;height:200px"></div>'
p = K.custom("x", a, b, body, size=(900, 600), name="bridge", css_=K.MT_CSS)
E.enter("#x-a", t, "focus"); E.tw("#x-a", t + 1, 0.8, {"x": 300}, None, "power2.inOut"); E.sfx(t, "woosh")
E.full(p, why="simplify", score=5)
```

`E.enter(sel, t, fx)` gives the standard entrances (`focus`, `rise`, `left`, `right`, `depth`, `settle`, `fade`); `E.tw(sel, t, dur, to, frm, ease)` is any GSAP tween; `E.count(sel, t, frm, to)` a counter; `E.vid(src, t, dur, media_start)` a clip inside a scene; `E.img(src, w, h, sid=sid)` a still with faces protected; `E.brand_asset("logo" | "wordmark" | "avatar")` the creator's own brand image, or `None` when they gave none at setup (always handle `None`); `E.watermark(which, corner, size, opacity)` a small corner mark for the whole video, only when the creator's setup asks for one. Hide anything that enters later with `class="h"`. Shared illustration classes: `.dot` (a person), `.blk` (a block, `.o` for the accent colour), `.mlab` (a small label), `.glass`, `.card`, `.fr` (image frame), `.p3` (a 3D stage).

The first time a moment needs something the kit lacks, check the HyperFrames catalog (`npx hyperframes catalog --query "<look>" --json`), then build it custom. **If the same custom graphic is needed in a second video, add it to `yt_kit.py` in the skill with at least two variants** and note it here. That is how the library grows without every video looking the same.

## Depth and 3D

Depth is a setup answer ("Depth and 3D in graphics" in `SKILL.md`). **On** (the pack default): everything below applies. **Off**: the engine drops `z`, `rotationX` and `rotationY` from every move, the `depth` entrance becomes a focus pull and `"auto"` never picks a `tilt` look, so the kit's components stay flat without any change to `build.py`; build custom graphics flat too.

Use depth to mean something: things separating (one becomes many), something coming forward because it matters (the differentiated card), layers at different distances (a collage), a frame resting at an angle so it reads as an object. Never spin, never tumble, never use Z purely as decoration. Put 3D elements inside a `.p3` wrapper and animate `z`, `rotationY`, `rotationX`. Check a 3D scene with `npx hyperframes snapshot --angle iso` if anything looks clipped.

## Variation rules

The same content type should not always get the same component:

| Content | Rotate between |
|---|---|
| "Here are N things" | `preview` (five variants), `rows` in a panel, `framework`, a `collage` of real examples, a custom object |
| A real example | `browser`, `frame` (four variants), `collage`, `social`, `ytvideo`, `person` |
| A number | `stat` (three variants), `graph`, a number inside the real screenshot it came from |
| A contrast | `compare` (three variants), `emph` swap, a split |
| No useful graphic | `E.punch`, the slow drift, a side change, one word of `emph`: never an irrelevant image |
| A process | `flow` (three variants), `timeline`, `framework` |

Corners (28 px, small 16 px), shadows, type, spacing and motion behaviour stay the same across all of them: that is the design system. See `motion-sound-design.md`.
