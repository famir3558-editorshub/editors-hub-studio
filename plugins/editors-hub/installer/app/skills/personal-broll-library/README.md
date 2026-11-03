# Personal B-Roll Library (Claude Code skill)

Analyse your own B-roll once, then search it in plain English, match it to a script or a video you are
editing, and get the picks into your editing app.

## What it does

- **Indexes your footage.** Claude looks at every clip (frames from start to finish, not the file name)
  and records what it shows, what ideas it can stand for, which seconds are usable and when it would be
  the wrong choice.
- **Searches by meaning.** "Find B-roll of me working", "do I have clips of me on my phone?",
  "something for procrastination".
- **Matches B-roll to a script, captions file or video** and gives you a placement plan: what is said,
  which clip, which seconds, why, plus the gaps worth filming.
- **Hands the plan to your editing app.** A timeline file for Premiere Pro (also readable by DaVinci
  Resolve), and a placement sheet that works with anything, including Final Cut Pro and CapCut.

## What it never does

Never moves, renames, deletes, compresses or overwrites your footage. Never edits an existing sequence
or project. Never claims something happened in your editing app when it did not.

## Requirements

- Claude Code on a Mac (the commands are written for macOS; the script itself is plain Python).
- Python 3.9 or newer and ffmpeg: `brew install ffmpeg`
- Optional: `pip3 install pillow` for timestamp labels on the contact sheets.
- Optional, only for matching B-roll to a video that has no captions yet: an ElevenLabs account
  (accurate, about $0.22 per hour of audio) or free transcription on your computer through HyperFrames
  (`npx hyperframes`, needs Node 22). You choose at setup, or later.

## Install

Copy this whole folder into `~/.claude/skills/` so it sits at `~/.claude/skills/personal-broll-library/`.
That is all.

## First run

The first time you use it, Claude asks a few setup questions, one at a time (about three minutes):
your name and what you do, where your B-roll lives, where to keep the index, which editing app you
finish in, your usual frame rate and shape, what your footage shows and what your videos are about,
and anything that must never be used. Your answers are saved to `~/.claude/creator-profile/profile.json`
(shared with the other skills in this pack, so you are not asked twice) and written into the skill.
Then it offers to scan your footage straight away.

To change an answer later, say **"redo my setup"**, or just say what changed ("I moved my footage",
"I switched to Resolve", "never show my kids").

## Use it (just talk to Claude Code)

- "Index my B-roll"
- "I added new footage, update the library"
- "Find B-roll of me working" / "Do I have clips of me on my phone?"
- "Here's my script (or captions file): where should my B-roll go?"
- "Make the timeline file with the B-roll for this video"

## Where things live

The index is in `~/BrollLibrary` unless you chose another folder at setup. It stays on your computer,
so you can search with the footage drive unplugged. Your footage stays exactly where it is. See
`references/schema.md` for the details.

## Files

```
SKILL.md                      instructions Claude follows
setup/SETUP.md                the first-run questions for this skill
setup/SHARED-SETUP.md         the questions shared by every skill in the pack
setup/questions.json          the list of answers this skill needs
setup/apply_profile.py        saves your answers and writes them into the skill
scripts/broll.py              the CLI (index, search, transcript, plan check, export)
scripts/stt.py                transcription (ElevenLabs or on this computer), used only when needed
assets/concepts.json          starter concept -> visual term map (copied into your library)
references/analysis-guide.md  how each clip is analysed and tagged
references/matching-guide.md  B-roll selection rules for edits
references/schema.md          metadata schema, plan format, duplicate/update logic
references/premiere.md        importing into Premiere Pro and other editing apps
```
