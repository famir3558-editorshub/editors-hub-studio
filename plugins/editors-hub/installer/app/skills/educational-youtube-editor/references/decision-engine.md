# The editing decision engine

How a moment becomes (or does not become) a visual. Work through this for the whole video in `edit_plan.json` before building; `plan_check.py` checks the result and the engine's audit checks the build.

## 1. The twelve questions

Ask them in order for each candidate moment. Stop as soon as the answer is "leave the creator alone".

1. What is the creator communicating here (claim, proof, example, story, definition, process, contrast, objection, transition)?
2. Does this moment need a visual at all?
3. What would make it easier to understand?
4. Is there a real-world example to show?
5. Would an illustration explain it better?
6. Would a diagram explain it better?
7. Should the creator stay visible?
8. Should this become a split screen?
9. Should this become full screen?
10. Is it important enough to justify sophisticated motion design?
11. Has a similar treatment been used recently?
12. Can this be communicated without simply repeating the narration as text?

## 2. Score it (1 to 5)

Not every sentence deserves an edit. Spend editing where it buys the most comprehension and retention.

| Score | Priority | Typical moments | Treatment it can earn |
|---|---|---|---|
| 5 | Very high | Hook, the video's promise, the intro, a major framework, an important example, a surprising statistic, a key conclusion | Full or split, custom or 3D motion, the signature visual |
| 4 | High | New section, comparison, story moment, list, process | Split, panel, or a short full-screen explanation |
| 3 | Medium | Supporting example, additional explanation | Float beside the creator |
| 2 | Low | Transitional wording, a repeated point | Usually nothing |
| 1 | Low | Filler | Nothing |

The engine warns when a 1-2 gets a full or split treatment, and the plan check warns when a 5 gets only a float.

## 3. Name the reason (`why`)

One of: `explain`, `demonstrate`, `evidence`, `example`, `simplify`, `curiosity`, `emphasis`, `momentum`, `memory`. A scene without one does not build. `momentum` is allowed but is the weakest reason: if a plan has many of them, the edit is decorating.

## 4. Choose the state

| If the moment is... | State | Notes |
|---|---|---|
| A story, a feeling, a nuance, a strong line, the creator being themselves | head | Protect it. Mark it in `left_alone` so it is a decision, not an oversight |
| A named term, a small proof point, a person mentioned in passing, a product glimpse | float | Beside the creator in the free space. One element, not three |
| "You are here" inside a framework | float, `zone="top"` | `K.tracker` |
| The promise in the intro, a key conclusion | float, `zone="bottom"` | `K.title`: a handful of words, built word by word |
| A short list or a stat the creator keeps talking across | panel | The creator slides aside; rows land as each item is reached |
| A real website, post, screenshot, product, person, before / after, graph the creator is reacting to | split | The core technique. A genuine 50/50 division: the real footage fills one half, the evidence sits in the branded half |
| An important statement, strong opinion, reveal, change of thought, emotional moment or key takeaway with nothing useful to show | head + `E.punch` | A motivated punch-in. Occasional |
| A long stretch where no graphic improves the explanation | head | Stay on the creator. The slow camera drift is already running |
| A relationship between ideas, a process, a framework's first appearance, cause and effect, a metaphor, the "what you'll learn" preview | full | Think explainer video. Keep it as long as the idea needs and no longer |

**Split composition.** A genuine split screen: the division runs cleanly down the frame. One half is the branded environment (the dark backdrop with its glow in the accent colour) holding the supporting content: motion graphics, text, images, illustrations, diagrams, animations, screenshots, examples, UI, data. The other half is the **actual talking-head footage**, cropped naturally around them so it fills that half edge to edge and feels like part of the video frame. The creator is never placed inside a floating card, rounded rectangle, artificial frame or cropped box; the engine refuses a card style. Graphic left, them right by default; reverse it now and then (`side="right"`). Use `cut=True` when the switch lands on an edit cut so the jump is hidden by the change of state; otherwise the creator glides across.

**Do not force graphics.** Meaningful visual change beats random visual change, everywhere, including the opening. If there is no useful graphic for a moment, the options in order are: leave the creator on screen (the drift keeps the shot alive), a punch-in on a line that deserves it, a subtle reframing or composition change, or one or two words of emphasis. An irrelevant image or animation is never the answer.

**Punch-ins.** `E.punch(a, b, "reason")` cuts in on the creator's face and back out. The strength is a setup answer (pack default 112%; "Punch-in strength" in `SKILL.md`). Use for an important statement, a strong opinion, a reveal, a change in thought, an emotional moment, a key takeaway. Start it on an edit cut where there is one (it turns a jump cut into a choice) or on the first word of the line; end it at the end of the thought, or straight into a full-screen graphic. Not constantly: outside the opening, more than about 1.5 a minute or two back to back stops feeling motivated, and the audit says so.

**Slow camera movement.** While the creator is full screen with nothing covering the footage, the engine runs one slow move per stretch: 100% towards 103-106% depending on the length, or the reverse, alternating between stretches, over at most 45 seconds and then holding. The reset happens unseen under the next graphic or during the glide into a split. It should be felt, not noticed. Do not add zooms on top of it.

**Full screen is earned.** The creator's face leaving the screen costs connection. Roughly 60% of the *graphic* moments can be full-screen (the default style prefers full-screen explanations to side panels), but the total time the creator is off screen should stay under about 30%.

## 5. Choose the form: show the concept

Prefer, in this order: the real thing (question 4), an illustration or metaphor that makes the idea tangible (5), a diagram of the relationship (6), and only then words. If the plan says "text" for an explanation, look again:

| The creator says | Weak (narration as text) | Strong (the idea shown) |
|---|---|---|
| "Attention becomes trust, trust becomes demand, demand becomes sales" | The sentence on screen | `K.flow`: each stage lands on its word and hands on to the next |
| "Most creators focus on views when they should focus on trust" | The sentence | `K.emph`: VIEWS struck out, replaced by *Trust* |
| "People are falling out of your funnel" | "Leaky funnel" title | `K.funnel`: people visibly dropping out between stages |
| "You're competing in a crowded market" | "Crowded market" | `K.crowd`: identical cards, one lifts out |
| "Your content compounds" | "Compounding" | `K.compound`: pieces stacking into something larger |
| "Posting builds an audience over time" | A calendar icon | `K.grow`: content pieces travel to an audience that grows |
| "There are five things" | "5 THINGS" | `K.preview`: one object becomes five, contents held back |

## 6. Pace in waves

Long-form editing breathes. Use the section `energy` from the content map:

| Section | Density | What that looks like |
|---|---|---|
| Opening (first 30 s) | Highest | A meaningful visual change inside 3 s, then something developing every 2-5 s. Graphics where they help; punch-ins and composition changes where they do not |
| Rest of the intro (to ~45 s) | High | The most sophisticated motion in the video, then a visible step down into long-form pacing |
| Major teaching section | Medium | 3-6 a minute, mostly float and split, one full-screen explanation |
| Personal story, emotional explanation | Low | 0-3 a minute. A photo, a place, a date. Often nothing |
| Important framework | High | The map builds full screen, then the tracker stays while the creator walks it |
| Nuance, caveats | Low | The creator |
| Real-world example | High | Split with the real thing, perhaps two angles of it |
| Transition to next section | Medium | One connecting move, not a title card every time |

After a dense passage, leave a real gap. Fatigue comes from sameness of rhythm as much as from volume. The audit prints scenes per minute for the intro and the body, flags a body over about 9 a minute (reel pacing) and flags any stretch over 75 seconds with nothing so you can confirm it is deliberate.

## 7. Variation without chaos

- The design system is fixed (corners, shadows, type, spacing, motion behaviour). What varies is the component, its variant, the state, the side, and the metaphor.
- Leave `variant="auto"`: the kit picks the variant used least recently. Name a variant when the content calls for one.
- Do not reuse one animation for every "here are N things". The preview has five variants; lists can also be rows in a panel, a framework rail, or a collage of real examples.
- The audit flags: the same component and variant within 150 s, three scenes in the same state in a row, more than 40% text-led scenes.
- One signature graphic per video, built with `K.custom` if no component tells the idea. That is what stops videos looking like each other.

## 8. Frameworks

1. First appearance: `K.framework(..., times=[...])` full screen, stages building one at a time on the words. Pick the variant (`rail`, `cards`, `ring`) once.
2. Each return: the **same** call without `times`, with `active=<stage>`, so the whole map is there and the current stage is lit.
3. While the creator talks through a stage: `E.float_(K.tracker(...), zone="top")`, the small 1 2 [3] 4 5 marker.
4. Use sids that include the framework id from the content map (for example `fw1-intro`, `fw1-s3`) so `plan_check.py` can see the returns.

## 9. Stories

Help the viewer into the story: relevant photos (polaroid frames suit this), the location, a screenshot from the time, the product, a date or a short timeline, a map, environmental imagery, a slow drift. Quieter sound, or none. Do not over-edit emotional storytelling. If the best visual is the creator's face, the plan says so in `left_alone`.

## 10. Section transitions

Major topic changes *occasionally* get a transition, and it should connect ideas rather than announce them:

- Return to the framework map and move the lit stage to the next one (best when a framework runs the video).
- End a section on a split and cut the next section's first graphic in on an edit cut.
- `K.section` (number, card or rail) for a hard chapter change. Not every time; repeated title cards are exactly the fatigue to avoid.
- A graphic becoming the next scene (a card from the preview expands into its section) is a `K.custom` job and worth it once or twice per video.

## 11. Cut alignment

`python3 scripts/cut_times.py <slug>` lists the big jump cuts left by the dialogue edit. In long-form they do not all need hiding, but each is a natural home for a punch-in (`E.punch(E.snap(t), ...)`), and when a split or full-screen moment sits near one, start or end it exactly there: `E.snap(t)` returns the nearest cut, frame-exact, and `cut=True` makes the switch hard instead of a glide. The audit reports how many big jumps are left visible on the creator.
