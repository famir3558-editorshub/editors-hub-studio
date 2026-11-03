# Final quality check

An edit is not complete until the **rendered file** has been reviewed. Previews lie: frames from the finished video do not.

## Procedure

1. `python3 scripts/08_render.py <slug> --draft` (or the master).
2. `python3 scripts/09_review.py <slug> "<rendered file>"`. It writes, into `<project>/review/`:
   - `intro-*.jpg`: one frame per second of the intro.
   - `scenes-*.jpg`: three frames of every scene (in, middle, out), labelled with state, component, variant, reason and score.
   - `rhythm.jpg`: the whole video as one strip, a frame every ten seconds or so. The waves should be visible: dense intro, then stretches of just the creator, then clusters.
   - `joins.jpg`: a frame either side of every chunk join. They must look continuous.
   - `crops-*.jpg`: every image used, with the shown area boxed (red = a face is cut) and each detected face marked.
3. **Read every sheet.** Then read the audit line and its warnings. Each warning is either fixed or answered with a reason.
4. Answer every question in the checklist below, honestly, from the sheets. "Probably" is a no.
5. Fix in `build.py`, re-run the render (only the changed chunks re-render), and review the changed scenes again (`scripts/snap.py <slug> --scene <id>` is the quick way).
6. Show the creator the review sheets with the report.

## The checklist

FINAL QUALITY CHECK (answer each from the rendered frames, not from memory):
 A. DIALOGUE: does the creator sound tight, confident and natural? No clipped words, no leftover false starts, no dead air, no robotic over-cutting, and every edited sentence still means what the creator meant?
 B. OPENING: is there a meaningful visual change within the first 3 seconds, and something developing every 2-5 seconds through the first 30, each one supporting what the creator is saying?
 C. CROPS: in crops-*.jpg, is every face and important subject fully inside the shown area (checked by eye, not only by the detector)?
 D. SPLITS: is every split a genuine 50/50 division with the real footage filling its half (no card, rounding, frame or box around the creator)?
 E. CAMERA: are punch-ins occasional and motivated, and is the slow drift felt rather than noticed (no visible zooming in and out)?
 F. FORCED: is any graphic there only to fill time? Remove it or replace it with a punch-in or nothing.
 1. Does the intro immediately feel premium, from the first frame?
 2. Does the intro confirm the click (the title / thumbnail promise is visibly on screen within seconds)?
 3. Are previewed ideas visualised without completely revealing them?
 4. Are the most important ideas receiving the strongest visuals (do the 5s look like 5s)?
 5. Are real-world examples used wherever they genuinely improve understanding?
 6. Do screenshots and images have polished presentation (never a raw image dumped on screen)?
 7. Are rounded corners and shadows consistent across the whole video?
 8. Are split screens composed properly (the creator is centred in their half, the graphic fills its half, nothing cramped or floating)?
 9. Are full-screen animations genuinely explaining concepts, not restating the narration as text?
10. Is there enough visual variation?
11. Are any animations repetitive (same component and look too close together)?
12. Is anything over-edited (a story, a nuance, a filler line)?
13. Is anything important under-edited (a framework, a key example, a statistic with nothing on screen)?
14. Does the creator remain visible enough for personality and connection (about 70% or more)?
15. Are graphics helping comprehension rather than distracting?
16. Does motion feel smooth (no pops, no jumps at chunk joins, nothing frozen, nothing frantic)?
17. Does the video feel like one cohesive design system?
18. Does the pacing work for long-form YouTube (waves, with room to breathe)?
19. Could any generic asset be replaced by a better real-world example?
20. Are there sections where an illustration would explain the idea better than what is there?
21. Does the video feel human-edited rather than template-generated (does it have its own signature)?
Also check: nothing touches or runs off the frame edge; no em dashes on screen; every font is the real one and not a fallback; figures in the main font; every figure matches what the creator says; every named person is the right person; nothing on the creator's "Never show" line is visible anywhere; sound effects are barely there; the audio is untouched and in sync at the end of the video.

## What the audit already measures

`python3 build.py` prints it; `audit.json` keeps it. It covers the measurable half of the checklist so the human half gets the attention:

| Checklist | Audit signal |
|---|---|
| B, 1, 2 | No meaningful change in the first 3 s; more than about 5 s unchanged in the first 30 s; fewer than 5 scenes in the first 45 s; intro not clearly denser than the body |
| C | Images with people counted; any crop through a detected face flagged; images shown whole on a blurred extension noted |
| E | Punch-ins counted; back-to-back or more than about 1.5 a minute flagged |
| 4, 12, 13 | A score of 1-2 given a split or full treatment; stretches over 75 s with nothing (confirm they are deliberate) |
| 5, 19 | Count of tier 1-3 real-world assets; every stock (tier 6) use flagged |
| 9 | Scenes with more than 14 words; share of text-led scenes over 40% |
| 10, 11 | Same component and variant within 150 s; three scenes in the same state in a row; number of component types used |
| 14 | Percentage of the video the creator is on screen |
| 16 | Chunk durations checked against the plan at render; big jump cuts left visible on the creator |
| 18 | Scenes per minute, intro against body; body over about 9 a minute flagged |
| Text rules | Em or en dashes in on-screen text |

Numbers do not judge taste. A clean audit with a dull video is still a dull video: questions 1, 6, 8, 15, 17 and 21 are answered only by looking.

## Sync check

At the end of a long video, compare a frame of the creator's mouth with the audio (play the last 20 seconds). Chunks are whole numbers of frames and the render script warns if a chunk is the wrong length, but confirm it: drift, if it happens, shows up at the end.

## Report to the creator

- The file path(s), length, and what was done in one or two sentences.
- The dialogue edit: raw length against edited length, and the notable removals (tangents, repeated sections) with the reason, so the creator can ask for anything back.
- The audit line, and any warning you chose to leave with the reason.
- Assets: what each shows, its source, its tier; anything mocked up or not found.
- Wording you chose for on-screen text.
- What is unverified (for example: only the draft was reviewed, or a section was not re-checked after a change).
- Open questions: music, the title and thumbnail if they were not known, any person not confirmed to be named, any third-party asset the creator should decide about.
