# YouTube clips

Give Claude one of your long-form YouTube videos (a file, or a link) and get back a handful of clips worth posting,
each in a horizontal (16:9) and a vertical (9:16) version.

What it does, in order:

1. Finds the cleanest file of the video (your raw or clean cut if you have it), or downloads it from the link.
2. Transcribes the whole video and reads all of it.
3. Finds, scores and ranks the strongest standalone moments, and gives you a short clip list.
4. Tightens each one into a 30 to 60 second story, with the strongest line you actually said moved to the front.
5. Writes an editing prompt for each version of each clip.
6. Cuts each clip out of the video, and (when you say go) builds the finished edits: captions, graphics beside you
   in the horizontal version, full screen / split / animation in the vertical one, levelled sound.

It only ever uses words that were really said, and it stops and asks before clipping a video that is not yours.

## What you need

- A Mac (macOS). The scripts use zsh, Apple's VideoToolbox encoder and Apple's Vision framework for face finding,
  which needs the Xcode command line tools (`xcode-select --install`).
- Claude Code.
- Node 22 or newer and ffmpeg: `brew install node ffmpeg`
- HyperFrames, which builds and renders every edit: `npx hyperframes@latest doctor`
- yt-dlp, for working from a YouTube link: `brew install yt-dlp`
- Python 3 with a few packages: `pip3 install numpy soundfile requests pillow`
- Optional: an ElevenLabs API key for the most accurate transcript (about $0.22 per hour of audio). Without one,
  transcription runs free on your own computer.

## Install

Copy this whole folder to `~/.claude/skills/` so it sits at `~/.claude/skills/youtube-clips`.

## First run

Say "clip this video" and give Claude the file or the link. The first time, it asks you a short set of setup
questions, one at a time: your name and brand, colours and fonts, how you want transcription done, your channel,
where your raw recordings live, how many clips you want, where finished clips go. Your answers are saved once in
`~/.claude/creator-profile/` and shared with the other skills in this pack, so you are not asked twice. Say "redo my
setup" whenever something changes.

## What is in the folder

- `SKILL.md`: the instructions Claude follows.
- `setup/`: the first-run questions and the script that fills in your answers.
- `scripts/`: downloading, preparing and transcribing the video, cutting clips out of it, the tight-cut pipeline
  (`scripts/cut/`), face finding, loudness.
- `engine/`: the HyperFrames engine and graphics kit that build both versions of a clip.
- `references/`: how clips are chosen, the style, the layouts, the prompt format.
- `examples/`: three worked builds, kept only as references for structure.
- `assets/fonts/`: one open-licence font (Playfair Display Italic, the default for emphasis words). Your own fonts are
  copied in at setup.
