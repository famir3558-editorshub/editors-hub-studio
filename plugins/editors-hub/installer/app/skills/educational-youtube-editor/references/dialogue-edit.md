# The clean dialogue edit (always first)

The creator hands over the **raw** talking-head file. Before any visual work, make an excellent YouTube dialogue edit: tight, confident, concise, and still unmistakably the creator. The visuals are layered on top of that. Never trade their natural flow for more edits.

## Order

1. `01_prep.py`, then `02_transcribe.py` (the whole video, with the transcriber chosen at setup). It prints the timed script and a list of likely fillers, repeats and restarts. Those are hints only.
2. **Read the entire script for meaning before marking anything.** You need to know what each section is for (see `analysis.md`) to judge what is a mistake and what is a deliberate pause.
3. Write `drops.json` in the work folder (`<work root>/<slug>/`, see "Your setup" in `SKILL.md`), with a reason on every entry:
   ```json
   {"words": [[412, 431, "false start, the sentence restarts at 432"],
              [980, 1012, "tangent about the mic, does not serve the point"]],
    "secs":  [[745.2, 751.0, "cough and a look off camera"]]}
   ```
   Word numbers come from `words.txt`.
4. `03_cut.py <slug>` then `04_verify.py <slug>`. Repeat until the verify pass is clean, then **read `edit.txt` top to bottom as a script** and listen to `edit.wav` around every big join (marked `||`).
5. `05_render_cut.py <slug>`. Only now does the visual edit begin.

## Remove

- Dead space, and pauses that are long without doing any work.
- Mistakes, stumbles, and words the creator corrects.
- False starts and abandoned sentences. Keep the **last complete take**.
- Accidental repetition (the same sentence or phrase said twice while finding their words).
- Sections that do not contribute to the point: tangents, housekeeping, talking to someone off camera.
- Filler ("um", "you know", "like", "so yeah") **where removing it improves the flow**.

## Keep

- Natural pauses: before a reveal, after a strong line, between sections. A pause that lets a point land is part of the delivery.
- Deliberate repetition for emphasis ("it works. It really works.").
- Filler that is part of how the creator talks when cutting it would make the line sound clipped or robotic. Do not strip every "so" and "and".
- Breaths (kept by default; a setup answer).
- A mid-video call to action and the end one, both.

The script does the mechanical part from the creator's setup answers ("Dialogue edit" in `SKILL.md`): a pause is only touched when it is longer than the first number, and it is shortened to the second, not removed. The pack default is over 0.5 s, shortened to 0.25 s, breaths kept. For one video, loosen (`--gap 0.7 --leave 0.35`) if the result sounds rushed, or tighten slightly for a high-energy one. Do not go reel-tight on long-form. If the creator wants a different feel for every video, change the setup answers rather than passing flags each time.

## Preserve the meaning (the rule that matters most)

Every removal is checked against the words around it. Before finalising a drop, read the sentence that will exist **after** the cut, from the last kept word before it to the first kept word after it:

- Is it a complete, grammatical sentence that the creator could have said?
- Does it still say what the creator meant? Watch for a cut that removes a "not", a "don't", a qualifier ("usually", "for most people"), a number, or the second half of a comparison.
- Does a pronoun or "that" still have something to refer to? If the thing it points at was in the removed part, keep it or move the cut.
- When the creator restarts a sentence, cut from where the **abandoned** version begins to just before the restart, so the kept take starts cleanly. Do not splice the first half of one take onto the second half of another unless it reads perfectly and sounds like one breath.
- A stutter on a tiny word ("that that", "the the") is usually safer left in than cut: word-boundary cuts on very short words clip.
- If a mistake cannot be removed without making the sentence wrong or unnatural, leave the mistake.

With local transcription the word edges are looser than with ElevenLabs: expect a few more clipped-word reports in the verify pass, and listen to more of the joins.

`04_verify.py` re-transcribes the edited audio and compares it word for word with what the cut was meant to keep: MISSING, EXTRA or CHANGED means a clipped word or a leftover fragment; PAUSE means dead air still in; REPEAT is worth a look. It cannot judge meaning. Reading `edit.txt` as a script is the meaning check.

## Then

The joins are listed by `cut_times.py`. Big ones are visible jump cuts on the creator. A long-form viewer accepts some, but each is a good place for a punch-in (`E.punch` starting on the cut), a state change, or the start of a graphic, so the jump reads as an edit decision. See `decision-engine.md`.

The audio is not processed beyond the cuts (8 ms fades at each join). No loudness change, no noise reduction. If the creator cleans up their own audio in another tool, the cut-only audio is `edit.wav` in the work folder.

If the creator ever does hand over a video that is already edited, say so and use `06_new_project.py --no-cut`; the default assumption is raw.
