# Choosing the clips and editing them as stories

## What to look for

Go through the video map and mark every moment that is one of these:

- An insight someone would write down
- A strong opinion, or advice that goes against what most people say
- A story (the creator's own, a client's result, something they watched happen)
- A complete item from a list video ("number three" with its reason and example), when it stands without the others
- An analogy that makes a hard idea easy
- A framework or a process with named parts
- A question asked out loud and then answered
- A mistake or misconception corrected ("most people think X; it's Y")
- Before-and-after thinking
- A concrete example (a real page, post, offer, number)
- An emotional or relatable moment
- A one-liner that leads into a deeper explanation
- A stretch where something is explained unusually clearly
- Expertise shown without being claimed: the problem is named more exactly than the viewer could name it

A moment is a candidate only if it has a payoff. A good line with nothing after it is a quote, not a clip.

Not candidates: the cold open (it previews lines that land later: clip the place where they land), the channel
intro, subscribe and comment asks, sponsor reads, the outro, and "in the next video" teases.

The chapters and the "most replayed" points printed by the prep script are worth a look after your own pass: a
most-replayed stretch you did not shortlist deserves a second read. They never replace reading the transcript.

## Scoring

Score each candidate 1-5 on each line, then rank by total (out of 40).

| Criterion | 5 looks like |
|---|---|
| Hook strength | A line in the speaker's own words that stops a stranger in the first three seconds |
| Insight / value | The viewer can do something differently afterwards |
| Memorability | A phrase, image or number that sticks a day later |
| Standalone clarity | Makes complete sense to someone who has not seen the rest of the video |
| Story quality | Clear beginning, development and payoff |
| Emotional interest | Tension, relief, recognition, surprise |
| Authority shown | The speaker is plainly the expert, without saying so |
| Social potential | Someone would save it, send it, or argue with it |

Three gates sit above the total:

- **Standalone clarity under 4: out**, whatever the total. If the clip needs "as I said earlier", "the second
  one", or something that was on screen ("as you can see here") to land, either a sentence of context can be included
  from elsewhere in the same section, the thing on screen can be rebuilt as a graphic, or it is not a clip.
- **Not the creator's to publish: out** (see the main skill's rules: a guest's private details, sponsor reads,
  dated offers).
- **The never-clip list**: anything on it is out.

Then keep every candidate that clears the gates and that you would be glad to see posted, up to the ceiling set at
setup. Drop a clip only when it makes the same point as a stronger one, when it cannot be cut cleanly (the thought
is interrupted, it depends on a guest's words or on music under the picture, it has no ending), or when it needs material that is not the
creator's to publish. A varied list (a story, a framework, a correction) is better, but variety is not a reason to
drop a strong clip.

## The story edit

Think like a story editor, not someone trimming silence. Every sentence that stays must do one of five jobs:

1. Build curiosity
2. Add context the viewer needs
3. Advance the idea
4. Give evidence or an example
5. Deliver the payoff

If it does none, it goes. In practice that means removing:

- Long pauses, filler, false starts, and pointers to the rest of the video ("like I said", "we'll come back to that",
  "link in the description", "let me pull this up")
- Repetition: when a point is explained twice, keep the clearer version, whichever came first
- Tangents, and asides that only make sense inside the full video
- The middle of an answer, when the opening and the conclusion connect without it
- Wind-down after the payoff ("so yeah, that's kind of how I think about it")

And keeping:

- Natural speech. Whole sentences, the speaker's rhythm, a pause before a punchline. If removing a clause makes the
  next sentence start oddly, keep the clause. A clip that sounds chopped sounds edited to make a point that was
  not made.
- Any qualifier that changes what the advice means.
- One clean ending: stop on the payoff line. The last word must be a real end of sentence in the speaker's
  intonation, not a mid-thought cut.

Shape to aim for: **hook** (0-4 s) → **why it matters or the problem** → **the idea, with its example** →
**payoff**. Not every clip has all four; every clip has the first and the last.

### Guests, interviewers and played clips

Default: build the clip on the creator's words alone. If an answer does not make sense without the question, either
a short written question card carries it (2-3 s over the speaker), or the vertical text hook does, or it is not a
clip. Keep another voice only when it is clearly audible on a phone speaker and the moment depends on it, and flag
it in the clip list.

## Hooks

Look through the whole clip for the sentence that would stop someone scrolling: usually the conclusion, the
contrarian claim, or the number. If it sits late, move it to the front (put its segment first in `clips.json`).

Allowed:
- Opening on a line said later in the same answer, then playing the answer from the start. The line may then be
  heard again at its natural place, or be cut from there: decide by ear. If it repeats, the second hearing must feel
  like a landing, not a glitch.
- Opening on the last clause of a sentence when that clause is complete on its own.

Not allowed:
- A line from a different section of the video used to tease this one.
- The video's own cold-open line, if the clip does not contain the part of the video that pays it off.
- A line whose "it" or "that" refers to something the clip never shows.
- A question the speaker was quoting, presented as their own view; a view they were arguing against, presented as
  their claim.
- Anything that was not said. No invented narration, no AI voice.

If no line works as a hook, the vertical version's text hook (written, two lines) can carry the promise instead. It
must be a fair summary of what the clip delivers, written in the creator's voice, and it is listed in the report as
written by you.

The join after a moved hook is the most visible cut in the clip. Plan what hides it (see `layouts.md`).
