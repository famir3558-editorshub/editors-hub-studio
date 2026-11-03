# Video to Written Content (Claude Code skill)

Turns one of your YouTube videos (a link) or a video file into finished written content in your own voice.

## What it does

- Transcribes the whole video accurately, with your names and brand terms spelled the way you spell them.
- Reads all of it and pulls out the strongest distinct ideas: opinions, stories, lessons, frameworks.
- Writes each idea properly for the place it is going, not as a summary of the video:
  - **Emails** to your list, each with 3 to 5 subject line options
  - **YouTube Community posts**
  - **LinkedIn posts** (optional)
  - **X and Threads posts and threads** (optional)
- Writes only the formats you chose, and only as many pieces as there are real ideas.
- Never invents a story, a number, a client or a quote: everything traces back to what you said in the
  video, with the timestamp noted in each file.

## Requirements

- Claude Code on a Mac.
- ffmpeg and yt-dlp: `brew install ffmpeg yt-dlp`
- Transcription, one of:
  - **ElevenLabs (recommended for accuracy)**: an ElevenLabs account and an API key with Speech to Text
    access (about $0.22 per hour of audio), plus `pip3 install requests`. You add the key to your own
    computer during setup; you are never asked to paste it into the chat.
  - **On your computer (free)**: runs through HyperFrames (`npx hyperframes`, needs Node 22). Names and
    unusual terms are misheard more often and there are no speaker labels.

## Install

Copy this whole folder into `~/.claude/skills/` so it sits at `~/.claude/skills/video-to-written-content/`
(or into `<project>/.claude/skills/` to keep it to one project). That is all.

## First run

The first time you use it, Claude asks a few setup questions, one at a time (about five minutes):
your name and what you do, how to transcribe, which formats you want, your offers and links, how you
sign off, British or American spelling, the names and terms that must be spelled right, words you never
want used, and where the files should go.

The most useful part: it asks for **two or three emails or posts you wrote yourself**. It studies how you
write (sentence length, how you open, the words you use and avoid, how you sign off) so the result sounds
like you on the page. Your videos stay the only source of the ideas and the facts.

Your answers are saved to `~/.claude/creator-profile/profile.json` (shared with the other skills in this
pack, so you are not asked twice), your voice notes to
`~/.claude/creator-profile/notes/video-to-written-content.md`, and the skill is filled in from them.

To change anything later, say **"redo my setup"**, or just say what changed ("here are more voice
samples", "I have a new lead magnet", "add LinkedIn", "never use the word hustle").

## Use

In Claude Code:

```
/video-to-written-content https://www.youtube.com/watch?v=...
```

or just: "Turn this video into written content: <link or file path>"

For one video you can ask for a different mix: "just emails from this one", "LinkedIn posts only".

Output lands in `./video-content/<video-name>/` unless you chose another folder at setup: a clean
transcript, an index of every piece, and one folder per format.

## Files

```
SKILL.md                 instructions Claude follows
setup/SETUP.md           the first-run questions for this skill
setup/SHARED-SETUP.md    the questions shared by every skill in the pack
setup/questions.json     the list of answers this skill needs
setup/apply_profile.py   saves your answers and writes them into the skill
scripts/transcribe.py    downloads or extracts the audio and transcribes it
scripts/stt.py           transcription engine switch (ElevenLabs or on this computer)
```
