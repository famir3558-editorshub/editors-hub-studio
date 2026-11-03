# Components

All classes live in `assets/doc.css`. The complete live example is `examples/sample-lesson/doc.html`. Copy its SVG
diagrams instead of drawing them from scratch, then change the labels.

"The main font", "the title font", "the emphasis font" and "the accent colour" are the creator's, set at setup (see
"Your setup" in `SKILL.md`).

## Type hierarchy
| Element | Use | Look |
|---|---|---|
| `.kicker` | Series · Episode · Pillar | 13px caps, tracked, grey |
| `h1` | Episode title, once | title font, 50px, one `<em>` keyword in the emphasis font and the accent colour |
| `h2` | Framework name and each "Part #N: Question?" | main font bold 34px |
| `h3` | Reframe, method, audience type, limitations, close | main font bold 26px |
| `h4` | Sub-framework, "Diagnose …" | main font bold 21px |
| `h5` | Underlined sub-head ("Map The …", "I Can Show You …") | bold and underlined |
| `.runin` | Bold opener above a paragraph | bold block |
| `.formula` | The bold equation line | bold |

Headings are in Title Case. **Figures stay in the main font**: h2 to h5 already are; a digit inside the h1 goes in
`<span class="num">`.

## Emphasis
- `.bar`: black (#111) full-width callout with white bold centred text. One principle sentence each. Use about 1 per
  section, 6 to 8 per doc. `<em>` inside turns a word the accent colour.
- `.label`: numbered highlight in the darker accent with bold text ("1. Where They Are Now"), always followed by one
  plain line.
- Bullets that start with a bold phrase: `<li><b>Symptom:</b> what to check.</li>`
- `.fill`: ▁▁▁▁▁ blanks for fill-in lines. Never use "____".
- `.tbd`: pale accent highlight on any `[bracketed]` detail the creator must supply. Never invent names, stats or
  links.

## Blocks
- `.proof`: 2×2 grid of `figure > .shot > img` with `figcaption > b(name) + span(result)`. Add `class="contain"` to
  the img for dark phone screenshots (letterboxed on black); use cover for photos and set `object-position` as
  needed so faces and numbers stay in the crop. `.proof.one` is a single wide shot.
- `.model`: full-bleed bordered frame for the creator's own framework image. Always use their image when one exists
  for the topic.
- `figure.diagram`: inline SVG, 780px wide. Labels are 11px bold caps (`class="cap"`).

## Diagram colours
Neutral greys and black are typed as hex: #D9D4CD / #F6F4F1 / #E6E1DA for neutral shapes, #111 for key boxes, #fff
for text on them. The accent is **never typed**: use the classes, so one colour change re-skins every document.

| Class | Does |
|---|---|
| `af` | fill = accent (dots, arrowheads) |
| `as` | stroke = accent (arrows, the outline of the centre pill) |
| `at` | fill = darker accent (small accent text and caps captions) |
| `nf` / `ns` | fill / stroke = neutral grey |
| `mt` | fill = muted grey text |

## Diagram patterns (copy from the sample lesson)
1. **Dot grid**, the crowd against the few that count: `<g data-dots="78" data-accent="11,40,67" data-y="44">`
   (`doc.js` draws it; `data-accent` lists which dots take the accent colour).
2. **3-box flow**: light, dark, light boxes with accent arrows and accent caps captions underneath.
3. **Same goal, different reason**: two left boxes into a centre accent pill, out to two right boxes.
4. **Mix bar**: `<g data-mix="10" data-split="5">`, light against #111 squares with captions.
5. **Formula pill bar**: a dark rounded bar holding white pills joined by accent arrows
   (I HELP [WHO] → GET [RESULT] → SO THAT [BENEFIT]).
6. **Loop**: four boxes in a diamond with accent arrows and an accent caps label in the centre.

Other good fits: a before/after line chart (grey drop against an accent steady line), a funnel tube with an accent
pinch, or a 2-column surface against deep table.

Every diagram earns its place by showing the mechanism of the point it sits under. If a diagram would only decorate,
use a `.bar` instead.
