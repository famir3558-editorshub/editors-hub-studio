# Scene library: motion ideas with working code

> **Safe zone first.** Whatever idea you pick, the graphic and any text live in frame y 270–1500 and x 65–1015, and captions end above y 1250. The source reel was built before this rule and on an earlier layout (creator on top): its split graphics run to the bottom of the panel and its full-screen animation captions sit at y 1609. Copy the motion from it, not the vertical placement.

Every scene below is real, working code in `examples/scene-library-source/build.py` (search for the scene id). It is another creator's reel kept as a source of motion: copy the block, change the content and the word times, never reuse its wording or assets. **Use each idea once per reel**: variety matters, and at most ONE carousel.

| Idea | Scene id | Use it when the creator... | What moves |
|---|---|---|---|
| Instagram profile grid | `s01-hook` | names a problem the viewer has ("stuck on a few hundred views") | 8 reel covers drop in with a spring, view counts tick, grid greys out, chips pop |
| Before/after 3D flip + count-up | `s02-proof` | cites a client result with numbers | two real screenshots tilt in 3D, the "after" flips in, number counts with a scale swell, sparks rise |
| Before/after slider + growth curve | `s02-proof` (the `BB_ALT` block) | same, alternate look | one card, an accent-colour slider wipes before→after, exponential curve + dot, count rides the curve |
| Framework cards, one at a time | `s03-matrix` (helper `mcards`) | introduces a named framework with N parts | cards spring up one by one (~0.55 s apart), the current one lights in the accent colour and its word resolves from blur |
| Phone feed scroll | `s04-change` | talks about scrolling / feeds / attention | phone with real covers snap-scrolls, then a blurred flick; two tilted cards float either side |
| Coverflow that stops (THE carousel) | `s05-clarity` | says "stop", "scroll past", "thumb-stop" | covers rush past in 3D, expo-brake to a stop, centre one glows, progress bar starts |
| Crowd + spotlight | `s06-target` | talks about the ideal client / audience / "who it's for" | 48 person icons pop in, an accent-colour spotlight hunts across and locks on one, rings + burst |
| Funnel with falling reels | `s07-avatar` | mentions funnel stages / narrowing | tiers build, reel tiles pour in and shrink through, bottom tier lights, one drops out |
| Tilt comparison | `s08-subject` | contrasts wrong vs right ("don't do X, do Y") | two reel cards; the wrong one tilts away grey, the right one comes forward with a glow |
| Heartbeat → flatline → payoff | `s09-curiosity` | says "live or die", "most important" | ECG line draws, flatlines grey, then the framework cards return and the last one bursts |
| Teased reveal → loop ring | `s10-loop` | talks about curiosity / open loops / suspense | blurred reel with a "?", a slider teases a sliver; then a ring draws with a reel riding it, eye → tick |
| Timeline loops + retention graph | `s11-loops` | talks about retention / keeping people watching | playhead crosses a timeline, arcs open and close, stars pop, retention line stays high vs dotted "without" |
| Chat mock with typing | `s12-skill` | describes a tool / AI skill / process | glass chat card, message slides in, checklist rows, rewrite types out, chips pop |
| Comment box → DM | `s13-cta` | gives the CTA ("comment WORD and I'll send it") | offer card + "100% FREE", comment box types the keyword, Post presses, DM notification lands |

## Face-window overlays (the creator is full screen; graphics over and behind them)

From the 16 s proof in `examples/overlay-source/build.py`. Built with `E.overlay(...)`; engine usage in `examples/overlay-source/engine-usage.py`. Different treatment in each face window. **The current default style keeps only real reels and real screenshots behind the head** (no headline, counter or label there): the rows marked * are kept as ideas for a creator who asks for them.

| Idea | In the proof at | Use it when the creator... | What moves |
|---|---|---|---|
| Headline behind the head * | 0–1.7 s | opens a thought with a strong line | white main-font line rises, the emphasis-font line in the accent colour resolves from blur, the head covers the bottom edge |
| Counter behind the head * | 5.4–7.5 s | cites a number that grew | big main-font number runs from → to behind them, flashes the accent colour on landing, small chart card draws in step |
| Real profile / proof card | 4.1–7.5 s | names a client or a result | the real screenshot slides in from the side with motion blur and settles at a 2° tilt |
| Orbit * | 7.6–9.2 s | names a framework, tool stack or set of parts | pills travel a dotted ellipse round the shoulders, pass behind the head, pop in one at a time |
| Label behind the head * | 9.3–15.6 s | starts a numbered part ("the first one is…") | small main-font line + large emphasis-font word hold above the head for the whole part |
| Instagram comments | 10.8–12.9 s | voices the viewer's thoughts or objections, or quotes feedback | white comment cards slide in from alternating sides, ~0.35 s apart, drop out together |
| Background whip | 15.7–16.5 s | talks about scrolling, feeds, volume | two columns of reel covers streak upward behind them with vertical blur |

Still to try in face windows: a real DM or sales notification landing, a stack of client screenshots fanning out behind them, a chart line drawing across the wall, icons orbiting instead of pills.

## Ideas not used yet (keep the variety going)
- Number wall (big main-font digits ticking up).
- Calendar / week strip filling in.
- Map of steps: nodes connecting with a drawn line.
- Split bar "before vs after" growing in opposite directions.
- Stack of cards being swiped away until one stays.
- Real client screenshots (from the proof folder) sliding in as a proof stack.
- HyperFrames registry blocks: search first — `npx hyperframes catalog --query "<look>" --json`. The carousel families
  (`carousel-vision/orbit/circle/path-N`) take `image1..N`, `background`, `speed` variables and are 1920×1080: host them in an
  untimed wrapper `<div class="blk" style="left:…;top:…;transform:scale(…);transform-origin:0 0">` in index. Remember: one carousel per reel.

## Helper API (inside scene JS)
- `T(g)` global seconds → scene-local. `q("name")` → `"#<sceneid>-name"`. `ID`, `START`, `DUR` are defined.
- `pop(tl, name, g, {from, r, d, e})` spring-pop. `rise(tl, name, g, {y, d})` rise + blur resolve. `out(tl, name, g, d)` fade/blur out.
- `draw(tl, name, g, d, ease)` stroke draw — the SVG element needs `pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"`.
- `floaty(tl, name, amp, period, from, dur)` ambient bob (finite yoyo). `words(tl, name, [g…])`, `note(…)` exist but headline text and notes are no longer used.
- Proxy pattern for anything GSAP can't tween directly (carousel layout, counters, typing, clip-path wipes):
  `const P = {v:0}; tl.fromTo(P, {v:0}, {v:1, duration:…, ease:…, onUpdate: function(){ /* set styles from P.v */ }}, T(g));`
  It is seek-safe because the styles are a pure function of the proxy value.

## Brand classes (assets/brand.css)
`de-glass` frosted card · `de-hot` accent border + glow · `de-tile` rounded image tile (put an `<img>` inside) ·
`de-chip` / `de-chip on` dashed / filled chip · `de-num` main-font tabular numbers · `de-label` small spaced grey label ·
colours `var(--o)` (the accent colour), `var(--paper)`, `var(--grey)`. Font aliases (names only; the files are the creator's, set at setup): `"HelvB"` = main font bold, `"HelvR"` = main font regular, `"PlayIt"` = emphasis font (words only, never numbers).
