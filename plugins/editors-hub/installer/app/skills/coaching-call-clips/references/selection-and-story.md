# Choosing the clips and editing them as stories

## What to look for

Go through the call map and mark every moment that is one of these:

- A coaching insight someone would write down
- A strong opinion, or advice that goes against what most people say
- A story (the coach's own, a client's result, something they watched happen)
- An analogy that makes a hard idea easy
- A framework or a process with named parts
- A client question followed by a strong answer
- A mistake or misconception corrected ("most people think X; it's Y")
- Before-and-after thinking
- A concrete example (a real page, post, offer, number)
- An emotional or relatable moment
- A one-liner that leads into a deeper explanation
- A stretch where something is explained unusually clearly
- Expertise shown without being claimed: the coach diagnoses the problem faster than the client can describe it

A moment is a candidate only if it has a payoff. A good line with nothing after it is a quote, not a clip.

## Scoring

Score each candidate 1-5 on each line, then rank by total (out of 40).

| Criterion | 5 looks like |
|---|---|
| Hook strength | A line in the speaker's own words that stops a stranger in the first three seconds |
| Insight / value | The viewer can do something differently afterwards |
| Memorability | A phrase, image or number that sticks a day later |
| Standalone clarity | Makes complete sense with no knowledge of the call or the client |
| Story quality | Clear beginning, development and payoff |
| Emotional interest | Tension, relief, recognition, surprise |
| Authority shown | The coach is plainly the expert in the room, without saying so |
| Social potential | Someone would save it, send it, or argue with it |

Three gates sit above the total:

- **Standalone clarity under 4: out**, whatever the total. If the clip needs "as I said earlier" or the client's
  backstory to land, either a sentence of context can be included from elsewhere in the same answer, or it is not a
  clip.
- **Client-sensitive content: out** (see the main skill's rules: even a client who has agreed to be clipped has not
  agreed to have their private details broadcast).
- **Consent and the never-clip list**: a moment that needs the words, name or face of someone who has not agreed
  goes under "Needs a yes first", not on the list. Anything on the creator's never-clip list is out.

Then keep every candidate that clears the gates and that you would be glad to see posted, up to the ceiling set at
setup. Drop a clip only when it makes the same point as a stronger one, when it cannot be cut cleanly (the thought
is interrupted, it depends on a client's words, it has no ending), or when it needs material that is not the
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

- Long pauses, filler, false starts, technical interruptions ("can you hear me", "let me share my screen")
- Repetition: when a point is explained twice, keep the clearer version, whichever came first
- Tangents, and asides addressed to this client only
- The middle of an answer, when the opening and the conclusion connect without it
- Wind-down after the payoff ("so yeah, that's kind of how I think about it")

And keeping:

- Natural speech. Whole sentences, the speaker's rhythm, a pause before a punchline. If removing a clause makes the
  next sentence start oddly, keep the clause. A clip that sounds chopped loses the feeling of a real conversation,
  which is the whole point of the format.
- Any qualifier that changes what the advice means.
- One clean ending: stop on the payoff line. The last word must be a real end of sentence in the speaker's
  intonation, not a mid-thought cut.

Shape to aim for: **hook** (0-4 s) → **why it matters or the problem** → **the idea, with its example** →
**payoff**. Not every clip has all four; every clip has the first and the last.

### Client questions

Clients are usually heard through the coach's speakers and are hard to hear. Under the default setup answer their
lines are cut, so: leave the client's words out and open on the coach's answer. If the answer does not make sense
without the question, either a short written question card carries it ("A client asked: how do I price a new
offer?", 2-3 s over the coach listening), or the vertical text hook does, or it is not a clip. Keep the client's own
audio only when it is clearly audible on a phone speaker, the moment depends on it, and consent allows it.

## Hooks

Look through the whole clip for the sentence that would stop someone scrolling: usually the conclusion, the
contrarian claim, or the number. If it sits late, move it to the front (put its segment first in `clips.json`).

Allowed:
- Opening on a line said later in the same answer, then playing the answer from the start. The line may then be
  heard again at its natural place, or be cut from there: decide by ear. If it repeats, the second hearing must feel
  like a landing, not a glitch.
- Opening on the last clause of a sentence when that clause is complete on its own.

Not allowed:
- A line from a different topic in the call used to tease this one.
- A line whose "it" or "that" refers to something the clip never shows.
- A question the speaker was quoting, presented as their own view; a view they were arguing against, presented as
  their claim.
- Anything that was not said. No invented narration, no AI voice.

If no line works as a hook, the vertical version's text hook (written, two lines) can carry the promise instead. It
must be a fair summary of what the clip delivers, written in the creator's voice, and it is listed in the report as
written by you.

The join after a moved hook is the most visible cut in the clip. Plan what hides it (see `layouts.md`).
