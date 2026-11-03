# Personal Short Form Reels (Claude Code skill)

Hand Claude one raw talking-head clip and get back a finished, fast-paced 9:16 reel: tight cut, hook, your own B-roll
on the cuts, one-word captions, small motion graphics, real logos, a split screen when you show software, sound
effects and music.

## You need

- macOS, with [Claude Code](https://claude.com/claude-code)
- **HyperFrames** (builds and renders every reel): Node.js 22 or newer, then `npx hyperframes doctor`
- **ffmpeg**: `brew install ffmpeg`
- A transcriber: **ElevenLabs** is the best and is recommended (an account and an API key, about $0.22 per hour of
  audio). Or free transcription that runs on your own computer through HyperFrames.
- Recommended: the `personal-broll-library` skill from this pack, so Claude can search your own footage.

## Install

Copy this folder to `~/.claude/skills/personal-short-form-reels/`.

## First use

Open Claude Code and say "set up the personal reels skill" (or just hand it a clip). The first time, Claude asks you a
short series of questions, one at a time: your name and brand, your colours and fonts, how you film, where your B-roll
and music live, and two or three reference videos to study (download them and drop them into the chat). Your answers
fill the skill in. This happens once; say "redo my setup" to change anything.

Your answers are stored in `~/.claude/creator-profile/` and shared with the other skills in this pack.

## Use

"Personal reel: <path to the raw clip>" (add a screen recording if the video shows software).
