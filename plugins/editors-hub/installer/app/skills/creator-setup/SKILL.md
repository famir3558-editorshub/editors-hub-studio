---
name: creator-setup
description: Creator Setup - run this FIRST. A short one-time interview that learns the creator's brand (name, handle, colours, fonts, logo, profile picture, transcription choice, folders, sound, reference videos), checks and installs the tools the editing skills need (HyperFrames, Node, ffmpeg, yt-dlp), and fills in every other skill in the Creator Skill Pack from one shared profile. Use when the creator has just installed the pack, says "set me up", "run setup", "redo my setup", "change my colours", "I have a new font", "new logo", "switch transcriber", or when any pack skill reports that setup has not been done.
---

# Creator Setup

The pack's editing skills never hold anyone's brand in their own text. They read ONE profile,
`~/.claude/creator-profile/profile.json`, that this skill builds. Answer the brand questions here once and every skill
in the pack is filled from the same answers.

## Step 1: check what already exists

```bash
python3 ~/.claude/skills/creator-setup/setup/apply_profile.py --status
python3 ~/.claude/skills/creator-setup/scripts/apply_all.py --status
```

- Profile exists and `missing_answers` is empty: tell them what you already have in three lines (name, accent colour,
  fonts) and ask which part they want to change. Ask only about that part, then go to Step 4.
- No profile: run the full interview below.

## Step 2: the interview

Read `setup/SHARED-SETUP.md` in this folder and follow it exactly: one question per message, show do not describe,
never guess, save every answer the moment they give it with
`python3 ~/.claude/skills/creator-setup/setup/apply_profile.py --set key=value`.

Run these sections, in order: **A1** who you are, **A2** brand colours, **A3** fonts, **A4** your face on screen,
**A5** transcription, **A7** where files live, **A8** sound, **A9** your real material. Skip A6 here (Step 3 does it).
Then **References they love**: ask for two or three videos whose editing they want theirs to feel like. Because there
is no single skill at this point, save the notes to `~/.claude/creator-profile/notes/all-styles.md` under
`## Style overrides` and `## References`; every pack skill reads that file as well as its own notes file.

Speak plainly. They are a creator, not a developer.

## Step 3: the tools

Check, do not ask:

```bash
node -v                     # 22 or newer
ffmpeg -version | head -1
yt-dlp --version
npx --yes hyperframes doctor
```

For anything missing, say in one line what it is for ("ffmpeg cuts and joins the video"), then ask before installing:

| Missing | Install (after they say yes) |
|---|---|
| Homebrew | tell them to install it from https://brew.sh themselves, it asks for their password |
| Node 22+ | `brew install node` |
| ffmpeg | `brew install ffmpeg` |
| yt-dlp (only the skills that take YouTube links) | `brew install yt-dlp` |
| HyperFrames | `npx --yes hyperframes@latest doctor` (fetches itself), then re-run the check |

Re-run the check until it passes. The scripts are written for macOS; if they are on Windows, say so plainly and tell
them which skills will not work yet. Never ask them to paste an API key into the chat (A5 explains the safe way).

## Step 4: fill every installed skill

```bash
python3 ~/.claude/skills/creator-setup/setup/apply_profile.py     # this skill itself: writes .configured
python3 ~/.claude/skills/creator-setup/scripts/apply_all.py       # every other pack skill
```

The report lists which skills are READY and which still need their own few answers. Tell them the second group asks
only its own questions (how they film, how they like to work) the first time they use it. The brand is never asked
again.

If a skill printed `UNFILLED` for a brand token, a shared answer is missing: ask exactly that question, `--set` it,
and run `apply_all.py` again.

## Step 5: the first thing to try

Finish with two lines: what is set up, and the one thing to try first ("drop a raw clip into the chat and say
'make this a reel'" for the short-form skills, or "paste a YouTube link" for the clip skills). Offer to show a
swatch and a line set in their fonts as proof it picked up their brand.

## Later changes

"Change my colours", "new font", "new logo", "switch to local transcription": ask only the affected questions, `--set`
them, then run Step 4 again. Every pack skill updates at once. New rules they give you while working ("never do X")
go into `~/.claude/creator-profile/notes/<skill name>.md` under `## Style overrides`, or `all-styles.md` when the rule
applies everywhere.
