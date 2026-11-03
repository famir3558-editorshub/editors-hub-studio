# Input analysis: understand the video before editing it

Read the **entire** transcript (the `edit.txt` from the cut, or the script printed by `02_transcribe.py`) before deciding a single visual. Editing decisions are contextual: a graphic at minute 14 is better when it is the same map the viewer saw at minute 4. You cannot do that reading 30 seconds at a time.

For a long video, read it in one pass for the argument, then a second pass with the list below, noting cut-timeline times. Write the result to `<project>/content_map.json` (the scaffold created the template). `plan_check.py` later uses it to catch what the plan forgot.

## What to pull out

| Field | What to capture | Why it matters to the edit |
|---|---|---|
| `topic`, `promise`, `viewer` | What the video is about, what the viewer gets by the end, who it is for | The intro has to confirm this within seconds |
| `hook` | The opening line and why it works | Gets the most designed treatment in the video |
| `learn` | The things the creator says they will cover, in the order given | Becomes the "what you'll learn" preview: structure shown, answers held back |
| `sections` | Each section with start, end, `kind` (intro, teaching, framework, story, example, nuance, transition, cta), `energy` (high / medium / low) and the one `point` it must land | Sets the density wave. A story is low. A framework is high |
| `frameworks` | Name, steps, where it is introduced, and **every time the creator returns to it** with the step | One map, reused, with the current stage lit |
| `lists` | "Five mistakes", "three reasons": the count, the items, where it was previewed | A list previewed in the intro and delivered later should look related |
| `comparisons` | A versus B, before versus after, wrong way versus right way | Compare component, or a split |
| `stories` | Start, end, who, where, when, whether it is emotional | Photos, places, dates, restraint |
| `statistics` | The value, the claim, the source if the creator gives one | Counter or graph, on the word. Use their spoken figure |
| `entities` | Every company, person, product, website, app, book, study, place, post or object the creator names, with their exact words | Each is a candidate for a real-world asset |
| `abstract` | Ideas with no picture of their own, plus how each could be **shown** | Where explainer illustrations and metaphors earn their place |
| `callbacks` | Later moments that refer back to earlier ones | Reuse the earlier visual so the viewer connects them |
| `conclusions`, `memorable` | Key conclusions and lines worth remembering | Emphasis, a bottom title, or simply their face with nothing on it |

## Reading for what is being communicated, not for keywords

For each moment ask what the creator is **doing**: making a claim, proving it, giving an example, telling a story, defining a term, walking through steps, contrasting two things, handling an objection, or moving on. The same word needs different treatment depending on that:

- "Apple" in "Apple spends years on one product" is an example: show the product or the launch.
- "Apple" in "it's not like you're Apple" is a throwaway: show nothing.
- "YouTube" in "post it on YouTube" is a step in a process: it belongs in the flow.
- "YouTube" in "YouTube is the second most visited website in the world" is a statistic with evidence: show YouTube and the number.

A keyword match with no purpose is the mark of a template edit. If you cannot say what the viewer understands better because the visual is there, it is not a moment.

## Check your reading

Before planning, you should be able to say in a few sentences: what the video promises, the three or four ideas it is built on, which idea is the centre (that becomes the signature visual), where the viewer is most likely to get lost (that is where explanation goes), and where the creator is at their most personal (that is where editing stays away).

If the figure in a screenshot and the spoken figure differ (it happens: a spoken 13K against 17.7K in the image), the spoken figure goes in text and a neutral or "after" image is shown.

While reading, also mark anything that touches the "Never show" line in `SKILL.md` ("Your setup"): a name, a client, an old offer, a topic. Those moments get no graphic and no asset, whatever they score.
