# Output formats

Plain language, the creator's own spelling conventions, no em dashes in anything that could end up on screen. Times
as `m:ss`.

## 1. `Clip list.md` (also shown in chat, kept short)

```markdown
# <Call name>: clip list

**The call in brief** (4-5 lines: topics in order with times, so the creator can see all of it was heard)

**Transcribed with:** ElevenLabs (speakers labelled) / on this computer (no speaker labels: speakers worked out from what was said)

**Recommended: N clips** (and one line on why not more)

## Clip 1: <Working title>
- **Source:** 41:12-43:50 of the call (kept: 41:58-42:06, 41:12-41:40, 42:10-43:02)
- **Estimated length:** 0:48
- **Opening hook:** "<the exact line said>" (moved from 42:58 / already at the start)
- **Core idea:** one sentence
- **Why publish it:** one or two sentences: what the viewer gets, what it shows about the creator
- **Score:** 34/40 (hook 5 · value 5 · memorable 4 · standalone 5 · story 4 · emotion 3 · authority 4 · social 4)
- **Flags:** client's voice in the question / client named at 0:12 / none

## Clip 2: ...

## Needs a yes first            ← only when consent is not settled for someone on the call
- 31:40 "<short label>": strong, but it does not work without <person>'s question

## Considered and left out
- 12:30 "<short label>": good line, no payoff
- 55:10 "<short label>": depends on the client's private numbers
```

The left-out list matters: it lets the creator rescue something you ranked low, and shows the choice was a choice.

## 2. The editing prompts (one file per ratio, per clip)

Each prompt must be enough for an editing agent that has never seen the call or this conversation. Same header in
both; the sections differ.

```markdown
# Clip 1: <Working title> (16:9 horizontal edit)        ← or (9:16 vertical edit)

## Brief
- **Source file:** "<out>/01-title/01-title - source.mov" (cut from "<call file>"; pieces and joins in "01-title - source.json")
- **Target:** 1920x1080, about 0:48                       ← 1080x1920 for the vertical
- **What this clip is:** two sentences: the idea and the feeling (a private coaching call the viewer has been let into)
- **Read first:** this skill's SKILL.md (step 7), references/cut.md, references/style.md, references/layouts.md · the hyperframes skill
- **Do not:** make it look direct-to-camera · add words that were not said · cover the speaker's face · add a graphic where the section says none

## The script (final words, in order: the verified cut must match this exactly)
> "<hook line>" / "<next sentence>" / ...

**Removed from the source range:** the client's "right, right" at 41:44 · a restart at 42:07 · the aside about <x>
**Joins to hide:** 0:04 (after the moved hook) · 0:31

## Framing notes (from stills at 41:12 and 42:30)
- The speaker sits in the right third, facing left, eyes about y 420. Graphic zone: x 110-900, y 120-820 (plain wall).
- [9:16 only] Crop: face centre at x 46% of the frame, looking room on the left...

## Captions
One line, the caption font. [16:9: bottom centre, about 68 px.] [9:16: under the chin / on the seam / under the graphic.]
Emphasis words for the whole clip: *story*, *price*, *3x* (a figure stays in the caption font).

## Sections

### 0:00-0:04  Hook
- **Source dialogue:** "<exact words>" (call 42:58)
- **Visual treatment:** what the viewer sees, in one or two sentences
- **Caption emphasis:** *word*
- **Motion graphic:** none: stay on the speaker        ← a real answer, use it often
- **Framing:** [16:9] natural frame at 112% punch-in / [9:16] full screen on the speaker, text hook lines 1 and 2: "…" / "…"

### 0:04-0:11  The problem
- **Source dialogue:** "..."
- **Visual treatment:** ...
- **Caption emphasis:** ...
- **Motion graphic:** what it is, what it is built from, where it sits, which word each part lands on, when it leaves
- **Framing:** ...

(continue to the end; a section is one idea, usually 3-10 s)

## Assets
| Asset | For section | Status |
|---|---|---|
| Screenshot of <real page> | 0:11 | found: "<path>" / to capture from <url> / ask the creator |

## Sound
The original audio, untouched. Effects and music: as the setup answer says (none / which ones / ask).

## Open questions for the creator
- ...

## Invented or assumed (to be swapped for the real thing)
- ...
```

Notes on writing sections:

- **Source dialogue** is verbatim from the transcript, so the editor can check the cut against it.
- **Motion graphic** names the component in the kit's vocabulary where one exists (a glass `card`, a `pill` stack, a
  `counter`, a drawn line, a notification, a document window), so the builder reaches for the existing helper
  instead of inventing one.
- Times are estimates from `03_clips.py`; say so once in the brief ("timings shift by a second or two in the edit;
  graphics are tied to the words, not the clock") and tie every graphic to the word it lands on.
- The 9:16 sections also state the **mode** (speaker / split / animation) and which join each switch hides.
- The 16:9 sections state the graphic **size** (beside the speaker / takeover / full screen).
- Do not copy the 16:9 sections into the 9:16 file and change the numbers. Plan the vertical from the script again:
  its sections often fall in different places because a switch has to land on a cut.
- Write only the ratios the creator asked for at setup.
