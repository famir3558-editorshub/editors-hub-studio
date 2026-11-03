# Educational YouTube editor

Give Claude the raw recording of a long-form educational video (5 to 60 minutes or more, horizontal) and get back a
finished, visual YouTube edit: tightened dialogue, real examples on screen, split screens, explainer animations and
quiet sound.

What it does, in order:

1. Transcribes the whole video and reads all of it.
2. Makes a clean dialogue edit first: mistakes, false starts, repeats and dead space out, your natural rhythm kept.
3. Maps the argument: the promise, the sections, frameworks, lists, stories, figures, and every company, person,
   product or website you name.
4. Plans where a visual genuinely helps, scores each moment, and leaves you alone on screen where nothing would.
5. Finds the real things to show, in your own folders first, then on the web if you allow it.
6. Builds the edit: you full screen, a designed element beside you, a side panel, a clean half-and-half split screen,
   or a full-screen explanation, with a strong first 30 seconds and calmer pacing after.
7. Renders it in parts, checks the finished file against a quality checklist, and reports every asset, source and
   wording choice.

Your voice is never processed, your face is never cropped or boxed, and no picture is ever cut through someone's face.

## What you need

- A Mac (macOS). The scripts use Apple's VideoToolbox encoder and Apple's Vision framework for face finding, which
  needs the Xcode command line tools (`xcode-select --install`).
- Claude Code.
- Node 22 or newer and ffmpeg: `brew install node ffmpeg`
- HyperFrames, which builds and renders every edit: `npx hyperframes@latest doctor`
- Python 3 with a few packages: `pip3 install numpy soundfile requests pillow`
- Google Chrome, for screenshots of websites you mention.
- Optional: an ElevenLabs API key for the most accurate transcript (about $0.22 per hour of audio). Without one,
  transcription runs free on your own computer.
- Optional: a sound-effects pack and music you are allowed to use. None ship with the skill.

## Install

Copy this whole folder to `~/.claude/skills/` so it sits at `~/.claude/skills/educational-youtube-editor`.

## First run

Say "edit this YouTube video" and give Claude the raw file. The first time, it asks you a short set of setup
questions, one at a time: your name and brand, colours and fonts, your logo, how you want transcription done, where
your recordings live, how tight you like your pauses, whether you want captions, the master resolution, what must
never be shown, and whether it should run to the end and report or check with you at each stage. It also asks for two
or three long-form videos whose editing you like. Your answers are saved once in `~/.claude/creator-profile/` and
shared with the other skills in this pack, so you are not asked twice. Say "redo my setup" whenever something changes.

A long video takes a while: the cut and the render run in the background, and a 4K master takes several times longer
than 1080p.

## What is in the folder

- `SKILL.md`: the instructions Claude follows.
- `setup/`: the first-run questions and the script that fills in your answers.
- `scripts/`: preparing and transcribing the video, the dialogue edit and its check, the project scaffold, finding and
  fetching real assets, snapshots, the render, the review sheets, an optional caption file.
- `engine/`: the HyperFrames engine and the library of graphics that build the edit.
- `references/`: how the dialogue is cut, how the video is read, how each visual is decided, the intro, the graphics
  library, real assets, motion and sound, the final quality check.
- `templates/`: the starter files each new video begins from.
- `examples/`: one worked build, kept only as a reference for structure.
- `assets/`: the animation library and one open-licence font (Playfair Display Italic, the default for emphasis
  words). Your own fonts, logo and sound map are added at setup.
