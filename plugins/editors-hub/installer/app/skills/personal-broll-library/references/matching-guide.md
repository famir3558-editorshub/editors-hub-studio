# Matching guide: choosing personal B-roll for a script or edit

B-roll exists to make a point land harder, not to change the picture for the sake of it. A
talking-head that holds attention does not need covering every five seconds.

## 1. Find the moments worth covering

Go through the timed segments and flag lines where a visual would add something:

- **Concrete actions or objects** - "I sat down and wrote the script", "my phone buzzed",
  "I opened Premiere". Strongest matches; personal footage shines here.
- **Stories** - "three years ago I was editing at 2am" - show the situation.
- **Abstract ideas with a clear visual metaphor** - procrastination (scrolling), focus (typing,
  headphones on), clarity (walking outdoors), growth (stairs, running).
- **Lists and steps** - one clip per item can carry a run of points.
- **Lines that make the speaker look away from the lens or pause** - natural cut points.

Usually leave on camera:

- the hook and the first few seconds (face builds trust), unless the hook is itself a visual;
- emotional or vulnerable lines and direct calls to action;
- jokes that depend on the creator's expression;
- moments where on-screen graphics, screen recordings or text bars are already planned.

Rough density for a talking-head YouTube video: one personal B-roll moment every 20-60 seconds,
denser in story sections, lighter in teaching sections. Short-form: B-roll can carry more of the
runtime, but keep the creator's face in the first 1-2 seconds.

## 2. Decide the visual before searching

For each moment write `visual_idea` in plain words first ("hands scrolling phone on the couch"),
then search for that. This stops the search being steered by whatever clips exist.

## 3. Pick the clip

From the search candidates choose by, in order:

1. **Relevance to what is being said** - does it reinforce this exact line?
2. **No conflict** - check `avoid_for` and `issues`; reject clips whose mood contradicts the line,
   and any clip flagged for the creator's never-use list (@@NEVER_SHOW@@).
3. **Quality** - prefer quality >= 3; never use quality 1-2 unless it is the only true match and
   say so.
4. **Variety** - avoid the same shot type and the same location back-to-back; follow a wide with a
   close-up where possible.
5. **Freshness** - avoid repeating a clip in one video. If you must, use a different section of it
   and keep them far apart. Prefer clips with a low `used` count (search `--fresh`).

Personal B-roll beats stock when it fits. If no personal clip genuinely fits, do not force a
weak tag match; record a `gap` with the visual idea and whether stock footage, a screen
recording, or a new shot would serve best.

## 4. Pick the section and length

- Start inside a `usable` segment, ideally within `best_section`. Never use the first or last
  0.5s of a recording, setup moments, or reaches toward the camera.
- Length follows the line: cover the phrase it illustrates, typically **2-5 seconds**. Up to
  ~8 seconds for a story moment or a walking shot under a longer sentence. Under 1.5s only for
  deliberate fast montage.
- Start the B-roll on (or a few frames after) the key word, and end at a natural pause or the
  start of the next idea, so cuts land with the speech.
- Moving shots (tracking, push in) need a little longer to read than static inserts.

## 5. Write the plan

Use the plan format in `schema.md`. Every placement needs `says` (the words it sits under) and
`why` (one line). Include `alternatives` (1-2 other clip ids) so the creator can swap quickly.
Run `broll plan-check` and resolve errors before presenting.

## 6. Presenting it

Table per placement: timecode, what is said, clip (filename) + section, length, why. Then the
gaps with the visual idea and what to film/source. Then the export files and how to bring them into
their editing app (see Workflow D in SKILL.md: the right file depends on the app).
