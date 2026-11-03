# Business Short Form Reels (Claude Code skill)

Hand Claude one raw talking-head clip and get back a finished 9:16 reel in your brand: tight cut, text hook, a
rotation of you full screen / split screen / full-screen animation, captions, motion graphics, sound.

## You need

- macOS, with [Claude Code](https://claude.com/claude-code)
- **HyperFrames** (builds and renders every reel): Node.js 22 or newer, then `npx hyperframes doctor`
- **ffmpeg**: `brew install ffmpeg`
- A transcriber: **ElevenLabs** is the best and is recommended (an account and an API key, about $0.22 per hour of
  audio). Or free transcription that runs on your own computer through HyperFrames.

## Install

Copy this folder to `~/.claude/skills/business-short-form-reels/`.

## First use

Open Claude Code and say "set up the business reels skill" (or just hand it a clip). The first time, Claude asks you a
short series of questions, one at a time: your name and brand, your colours and fonts, how you film, how you like to
work, and two or three reference reels to study (download them and drop them into the chat). Your answers fill the
skill in. This happens once; say "redo my setup" to change anything.

Your answers are stored in `~/.claude/creator-profile/` and shared with the other skills in this pack, so you are not
asked the same things twice.

## Use

"Do the business reel: <path to the raw clip>"

## What is inside

```
SKILL.md                   the instructions Claude follows (your details appear here after setup)
setup/                     the first-run questions and the script that fills the placeholders
engine/                    the HyperFrames reel engine, the graphics kit and the sound mix
scripts/                   transcribe, tight cut, crops, captions, scaffold, render, checks
references/                the full default style and a library of scene ideas with working code
examples/                  worked reels kept as structure references
assets/                    brand CSS, fonts (yours are added at setup), the safe-zone guide
```
