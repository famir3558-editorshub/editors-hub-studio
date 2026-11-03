# Lesson doc builder

Give Claude a script, an outline or a topic and get back the document you scroll through on screen while you record
a long-form lesson: a clean white "report" page that fills one half of the frame while you are on camera in the
other half.

What it does, in order:

1. Reads your script or outline (or helps you outline the topic first).
2. Collects your real material: your own framework image if you have one, and four proof screenshots.
3. Writes the document in a fixed teaching layout: why you should listen, the common belief and why it fails, your
   named framework, a method, each part with a diagram, a black one-line callout and a "diagnose" list, a call to
   action partway through, examples for two kinds of viewer, two honest limitations, a practical test and the close.
4. Draws the diagrams in your colours.
5. Takes preview pictures, checks nothing is cut off, and shows you a mock of the split screen.
6. Lists anything it left in [brackets] for you to fill in. It never invents names, results or links.

You open the finished page in your browser and scroll it while recording. It can also make 4K stills of each screen
for your editor, a shorter "notes version" to talk around, and a PDF for a tablet.

## What you need

- Claude Code.
- Node 18 or newer: `brew install node` on a Mac, or the installer from nodejs.org.
- Google Chrome (or Edge, Brave, Arc or Chromium).
- Optional: ffmpeg, for the split-screen mock picture: `brew install ffmpeg`.

Claude installs one small helper the first time (it asks first). No API keys, no paid services.

## Install

Copy this whole folder to `~/.claude/skills/` so it sits at `~/.claude/skills/lesson-doc-builder`.

## First run

Say "build a lesson doc" and give Claude your script. The first time, it asks you a short set of setup questions,
one at a time: your name and brand, your colour and fonts, the real results that go in the "why listen to me"
section, where your proof screenshots live, how you write, and how you record. Then it shows you a sample page in
your colours and fonts before it builds anything real. Your answers are saved once in `~/.claude/creator-profile/`
and shared with the other skills in this pack, so you are not asked twice. Say "redo my setup" whenever something
changes.

## What is in the folder

- `SKILL.md`: the instructions Claude follows.
- `setup/`: the first-run questions and the script that fills in your answers.
- `assets/`: the page design (`doc.css`), the diagram helpers (`doc.js`), the starting skeleton, and your fonts
  once setup has run. One open-licence font ships with it (Playfair Display Italic, the default for the title
  keyword).
- `references/components.md`: every building block and diagram pattern.
- `examples/sample-lesson/`: a complete sample document on an invented topic, kept only as a reference for
  structure.
- `scripts/`: starting a new document, taking the preview pictures, making the PDF.
