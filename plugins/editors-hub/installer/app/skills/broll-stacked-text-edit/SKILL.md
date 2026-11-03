---
name: broll-stacked-text-edit
description: Edit one talking-head video into a polished, fast-flowing, fully captioned 9:16 video with B-roll. Does the whole job - a word-timed transcript, tight cut (dead space, false starts, repeated takes and speaking mistakes removed, head and tail trimmed to the first and last word), B-roll chosen from the creator's own B-roll library (every clip reviewed) and placed where it explains what is being said or hides a jump cut, captions on every spoken line below the speaker's chin, and for the few important phrases a stacked caption whose lines are revealed one by one as they speak, with an optional key word in the emphasis font and accent colour; then checked and exported. Use whenever the creator gives a talking-head video to edit with B-roll or captions, or says "edit this with my B-roll", "B-roll edit", "cut this and add B-roll", "caption this", "stacked captions", "stacked text", "same edit as last time". Also use for one part alone - only the tight cut, only the B-roll pass, only the captions, or a re-render after notes. Not for split-screen animation reels (business-short-form-reels, split-reel). To index or search the footage library on its own, use personal-broll-library.
---

# B-roll + stacked text edit

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/broll-stacked-text-edit/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first. Do not start the task, and do
  not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if they exist,
  `~/.claude/creator-profile/notes/broll-stacked-text-edit.md` and `~/.claude/creator-profile/notes/all-styles.md`.
  Rules under `## Style overrides` in those notes files win over the defaults written below.

"redo my setup" re-runs the interview at any time.

## Your setup

Filled in by setup. To change a line, change the answer (`setup/SETUP.md`), never this text.

| | |
|---|---|
| Creator | @@CREATOR_NAME@@ · @@BRAND_NAME@@ · @@HANDLE@@ |
| Accent colour (the key word in a stack) | @@ACCENT@@ (@@ACCENT_NAME@@) |
| Fonts | captions and small lines: @@FONT_CAPTION_NAME@@ · large line: @@FONT_MAIN_NAME@@ bold · key word: @@FONT_ACCENT_NAME@@ |
| Transcriber | @@TRANSCRIBER@@ |
| B-roll folders | @@BROLL_DIRS@@ |
| Never use as B-roll | @@NEVER_SHOW@@ |
| Footage drive | @@MEDIA_DRIVE@@ |
| Finished videos go | @@OUTPUT_RULE@@ |
| Working files | `@@WORK_ROOT@@/<slug>` (the shared B-roll library is `@@WORK_ROOT@@/broll-library`) |
| Horizontal source in the vertical frame | @@SOURCE_FRAMING@@ |
| Caption size · stack large line | @@CAPTION_SIZE@@ px · @@STACK_SIZE@@ px |
| B-roll share of the runtime | at most about @@BROLL_MAX_SHARE@@% |
| Stacked captions | @@STACK_DENSITY@@ |
| Before the final render | @@REVIEW_RULE@@ |

One talking-head video goes in; B-roll comes from the creator's B-roll library. A tight 9:16 edit comes out: the
speaker's voice runs unbroken, B-roll replaces the picture where it helps, every spoken line is captioned below the
chin, and the few important phrases become stacked captions.

`S=~/.claude/skills/broll-stacked-text-edit/scripts` · work dir `W=@@WORK_ROOT@@/<slug>` (small files; pass the
slug to every script) · outputs go to the folder the output rule gives (default `"<video folder>/<video name> - Edit/"`).
Video files are large: renders stay beside the source (the footage drive, when there is one), one render at a time,
and long renders run in the background. Every script prints its own usage.

**Review before the final.** Follow the "Before the final render" row above. When it says to wait: render only the
fast 720p `--draft` (section 7), give the creator its path and what to look at, wait for approval, apply their
timestamped notes to `plan.json`, re-draft, and render `--final` only once approved. For a batch, gate the first
video, then apply its notes to the rest.

## 1. Identify the inputs
- **The video** is the single talking-head file the creator names, drags in, or points at. **B-roll** comes from
  their standing folders (section 4) plus any folder they name for this video.
- If they give only a folder: the main video is the long clip with continuous speech, the B-roll is the rest. If two
  files could be the main video, or the footage drive is not connected, ask once with `AskUserQuestion`. Do not guess.
- **The finished video is always 9:16 (1080x1920)**, whatever the source. A portrait source fills the frame. A
  16:9 source either fills it (`"frame": {"mode": "fill", "focus": [x, 0.5]}`, cropped around the speaker: pick `x`
  from a still so they are centred) or sits whole inside it (`"mode": "fit"`, black above and below). The default is
  the creator's setup answer (above), normally fill for a talking head; use fit only when the crop would lose
  something that matters, or they ask. The footage itself is never scaled or shifted beyond that choice: if the
  framing is poor, say so and let them decide.
- `python3 $S/01_prep.py "<video>" <slug>` - act on its warnings (variable frame rate needs a constant-rate copy
  first; HDR is worth telling the creator about).

## 2. Transcribe
`python3 $S/02_transcribe.py <slug>` - uses the transcriber chosen at setup through `scripts/stt.py` (ElevenLabs
Scribe, or local transcription through HyperFrames; the result has the same shape either way). The API key is read
from the environment or the shell profile, never printed and never asked for in chat. Do not use an ElevenLabs
connector's transcribe tool (about 30x the cost). Read the whole script it prints and `words.txt` (numbered words
with times). With the local engine word edges are looser: expect to loosen `--pad-out` in step 3 and listen to the joins.

## 3. Decide the cut
Write `W/drops.json`: `{"words": [[i, j], ...], "secs": [[a, b], ...]}` (word-index ranges from `words.txt`;
`secs` for things that are not words: coughs, off-camera chat).

Remove:
- **False starts and repeated takes.** When a line is said more than once, keep the LAST complete take and drop
  every earlier attempt in full, including the half-sentence that led into it.
- **Speaking mistakes**: stumbles, a wrong word followed by the corrected one, "um / uh", a restarted phrase,
  throat clears, "sorry", "let me say that again", anything said to themselves or off camera.
- Dead space, breaths, and the head and tail: the script does these itself. Never list them.

Keep:
- **The speaker's meaning.** After the drops every sentence must still be a sentence and the argument must still
  follow. When unsure whether a repeat is a mistake or emphasis ("it works. It really works."), keep it.
- A scripted mid-video call to action AND the end one. Only drop a CTA when it is another take of the same slot.
- Never reorder, never splice words into a sentence that was not said.

`python3 $S/03_cut.py <slug>` then `python3 $S/04_verify.py <slug>` (re-transcribes the edited audio and
compares it word for word). Read the EDIT as a script and every MISSING / EXTRA / CHANGED / PAUSE / REPEAT line.
Fix `drops.json` and repeat until it is clean and the head and tail are under ~0.25 s. If a word sounds clipped,
loosen with `--pad-out 0.06`; if it feels breathless or the creator asks for more air, `--gap 0.2`.
Then `python3 $S/05_render_cut.py <slug>` (background).

Everything after this uses **cut-timeline seconds**: `W/edit.txt` (script + every word's time) and `W/cuts.json`
(every join; `big` = a dropped take or a long removal, the jumps a viewer notices).

## 4. The B-roll library (review every clip)
The creator's standing B-roll folders are the `broll_dirs` answer in the setup table. Use all of them for every edit
unless they name another folder for that video; a folder they name is added with `06_broll.py "<folder>"`. Anything in
"Never use as B-roll" is recorded in the clip's notes as unusable and never placed.

Clips are catalogued once into a shared library, `@@WORK_ROOT@@/broll-library` (`library.json` + one contact
sheet per clip), so each clip is reviewed once and reused by every edit:
- `python3 $S/06_broll.py` - catalogue new or changed clips (background; the first run takes a long time).
- `python3 $S/06_broll.py --todo` - clips with no notes yet. **Open each one's sheet with Read and save notes**
  with `06_broll.py --note <id> "<notes>"`: where it is, what the person is doing, how they are framed (wide / close,
  portrait / landscape), the usable seconds, the mood, and the kinds of line it could illustrate. No clip is
  skipped: before planning B-roll, `--todo` must be empty (hand batches of sheets to parallel sub-agents when
  there are many).
- `python3 $S/06_broll.py --find <word> ...` - search the notes when matching clips to lines. Read
  `library.json` in full at least once per edit so the choice is made from everything, not only search hits.
- Before placing a clip, look at its sheet again and pull closer frames around the seconds you intend to use.

This catalogue is this skill's own: it is what `plan.json` and the render read. The footage can also be indexed with
the pack's `personal-broll-library` skill (a searchable database with concepts, usable seconds and exports). The two
do not share files, so when the creator already has that index, use it to find candidate clips and their notes, then
make sure each chosen clip is in this catalogue (the same folder passed to `06_broll.py`) before it is placed.

## 5. Plan the B-roll (`"broll"` in `W/plan.json`)
Pick by this order:
1. **It explains the line.** The clip shows the thing being talked about at that moment (the speaker says "when I'm
   filming" and the clip is them filming). Start it on the first word of that idea.
2. **It hides a big jump cut.** Where a `big` cut has no explanatory clip nearby, use footage that keeps the
   picture flowing (walking, working, setting up) across the join.
3. **It gives the eye a change** in a long stretch on the speaker (roughly 8 s or more with nothing else happening).

Rules:
- 1.5-4 s each. Start and end either exactly on a cut time from `cuts.json` or at least 0.25 s clear of one, and
  on the start of a phrase, not mid-word.
- The speaker stays the main picture. Do not cover: the first sentence (the hook), a punchline, a moment where
  the face or hands carry the point, or a call to action. Stay under the creator's B-roll share (about a third by
  default; the lint warns 10 points above it). Do not let a B-roll edge land in the middle of a stack.
- **Shape.** `"mode": "fit"` (default for a landscape clip) shows the whole 16:9 picture inside the vertical
  frame; `"mode": "fill"` crops it to cover the frame. Use fill only when the subject survives the crop
  (`"focus"` chooses the part kept); portrait clips fill. Captions follow automatically: inside a fitted picture
  they sit in its lower half, never in the black.
- Each clip once. Use the best seconds of it (`"in"`), not from 0 by default. B-roll audio is never used.
- Not every big cut needs covering. A visible jump on the speaker is better than B-roll that means nothing over an
  important line.
- Write a `"why"` on every placement; it goes in the report.

## 6. Captions and stacks (`"captions"` and `"text"` in `W/plan.json`)
The whole video is captioned. `07_text.py` builds the captions from the verified transcript, so every spoken
word is on screen exactly once, timed to the speech. The treatment is described in `references/text-reference.md`.

**Regular captions (simple and consistent).** Short phrases of 2-4 words, one line, the caption font, white,
tracking -50, soft shadow, words as transcribed. They change on the word; no animation.
- Read `W/captions.txt` in full after every build. Fix names, brand words and mis-heard words with
  `"captions": {"fix": {"acme": "Acme"}}` (a wrong word that is really a transcription error in the cut itself is
  fixed back in step 3).
- **Position: below the chin.** Get gridded frames (`python3 $S/frames.py <slug> <t> ...`) from several points
  in the video and set `"captions": {"y": <centre line>}` on the upper chest, clear of the chin and, where
  possible, of where the hands usually are. Keep it inside the safe zone (y 270-1500, ideally above 1330).
- **Adjust per shot.** If the framing changes (a jump cut that moves the speaker, a different take, a zoom), add
  `"zones": [{"from": t, "to": t, "y": ...}]` for that stretch. A caption must never sit on the face.
- **16:9 footage inside the vertical frame** (a fitted B-roll clip, or the main video in fit mode): captions go
  in the lower half of the actual picture. This is automatic; never move them into the black above or below it,
  and never to the top of the screen.

**Stacks (only where emphasis improves the message).** For an important phrase the caption turns into a stack:
`{"id": "s1", "at": 12.4, "lines": ["when it comes", "to *marketing*"]}`.
- The lines are the speaker's exact words in order (the script refuses anything else) and replace the regular
  captions for those words. Each line is revealed as its first word is spoken, one by one, with a gentle fade and a
  small move (`"move": "up"` or `"down"`); the stack clears when the next phrase starts.
- Small lines look like the regular caption; the **last line is large** (main font bold, about 2.4x). Two lines is
  the usual form; three when the phrase needs it. Lines are left-aligned as one compact block.
- **Key word, when the phrase has one:** wrap it in `*asterisks*` in the large line. It is set in the emphasis font
  in the accent colour, larger than the words around it, and the sans words fit around it on the same line. One per
  stack, and not every stack needs one. A figure stays in the sans, in the accent colour (never the emphasis font).
- Choose phrases that END on a beat (a full stop, a pause, the end of a thought) so the complete stack can be
  read before the next words arrive; the script warns when the last line gets under 0.6 s. Put enough words in
  the large line that it stays up while they are said.
- **Selective:** the named idea, the number, the turn, the line to remember, at the creator's stack density (above),
  never back to back. Everything else stays a plain caption.
- Position: by default the stack sits where the captions are (small line on the caption line, block centred).
  If it would cover the hands or runs wide, give `"anchor": [x, y]` (top-left of the block) in open space
  beside or below the speaker for that shot. Never over the face.

`python3 $S/07_text.py <slug>` builds the full text layer and a preview per stack. **Run it again after any
change to `plan.json`**, including B-roll changes (caption positions depend on them); the render refuses a
stale layer. It prints the three fonts it found; any line starting FALLBACK means a font could not be loaded.

## 7. Check, render, check again
1. `python3 $S/08_render.py <slug> --lint` - fix every ERROR; read every WARN and either fix it or be able to
   say why it stands.
2. `python3 $S/08_render.py <slug> --draft` then `python3 $S/09_check.py <slug>` and **read every check sheet**:
   - Cuts: no half-blink or mid-gesture flash, no sliver of a dropped take, first frame already on the speaker talking.
   - B-roll: first and last frames are good frames (not a blur, not the speaker looking at the camera to stop
     recording), nobody is cropped badly, colour sits with the main video, and it starts and ends where planned.
   - Captions (`captions_NN.jpg`, one tile per caption): every line of `captions.txt` is there, spelled right,
     readable at phone size, below the chin, off the face, and inside the picture's lower half on fitted 16:9.
   - Stacks (`stacks_NN.jpg`): lines arrive one by one with the words, the block is clean and left-aligned in
     the 9:16 frame, nothing clipped or over the face, fonts are right, and it is gone when the next caption starts.
   - The file is 1080x1920.
   - Sound: starts and ends within ~0.25 s; length matches the plan.
   Fix the plan and repeat until a pass is clean. Listen to `W/edit.wav` around any join that looked doubtful.
3. If the review rule says to wait for approval, stop here with the draft. Then
   `python3 $S/08_render.py <slug> --final [--tag v2]` and `09_check.py` once more on the master.

## 8. Export and report
`--final` writes `<name> - EDIT.mp4` (full resolution, HEVC) and `<name> - EDIT (phone).mp4` (H.264, under
30 MB). Give the creator the path of the master and of the phone copy. Report, briefly:
- length before and after, and what was cut that they might want back (dropped takes, any CTA, any line removed
  for meaning rather than as a mistake);
- each B-roll placement and its `why`; clips left unused; big cuts left visible;
- the caption corrections made, and each stack's words;
- anything chosen without asking, and any warning left standing.
For notes after review, copy `plan.json` to `plan_vN.json`, edit, and re-render with `--tag vN`; the creator compares versions.

## Defaults of this style (change only when the creator asks)
Captions at the creator's caption size, words as transcribed, hard on/off · stack lines fade in over 0.3 s with a
26 px move, large line at the creator's stack size · landscape B-roll shown whole inside the frame (fit) on black ·
hard cuts into and out of B-roll · no music, no sound effects, no zooms. Ask before adding any of those.

## Gotchas
- ffmpeg here may have no drawtext/subtitles filters: text is rendered by headless Chrome to PNGs and overlaid.
  Google Chrome must be installed (or set `CHROME_PATH`).
- Fonts are loaded from the creator profile. A font saved as `local` (an Adobe Font, for example) is found by name on
  the computer and only renders while its app (Creative Cloud) is running. If `07_text.py` prints FALLBACK, tell the
  creator: do not ship the fallback as final.
- `05_render_cut.py` selects frames by number, so the source must be constant frame rate.
- A stack across a big jump cut can end up on top of the speaker after the jump: check both sides.
- B-roll with a different frame rate is conformed to the video's; slow motion is `"speed": 0.5` (uses half the
  clip time). HDR B-roll over an SDR video looks washed out: flag it.
- One render at a time when writing to an external drive.
- The encoders used are Apple VideoToolbox (HEVC and H.264): the render scripts need a Mac.

## Related
`personal-broll-library` (indexing and searching the footage) · `business-short-form-reels` (the animated 9:16
reels; its cut rules are the same standard) · `split-reel` · `fitted-stacked-captions` (a different, word-by-word
stacked caption style).
