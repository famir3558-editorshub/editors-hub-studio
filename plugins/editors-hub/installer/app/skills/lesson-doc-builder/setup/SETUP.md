# Setup: lesson-doc-builder

The first-run interview for this skill. Read `SHARED-SETUP.md` first ("How to run the interview"): **one question
per message**, save each answer as you go, never guess, never fill in from memory. Start by checking what is already
answered:

```bash
cd ~/.claude/skills/lesson-doc-builder
python3 setup/apply_profile.py --status
```

and read `~/.claude/creator-profile/profile.json` if it exists. Anything already saved by another skill in the pack
is read back in one line and confirmed, not asked again.

This skill builds a document, not a video edit, so it needs only part of the shared interview and no transcriber.

## Part 1: the shared questions

Run these sections of `SHARED-SETUP.md`, in order, with the notes for this skill:

| Section | What it settles | Notes for this skill |
|---|---|---|
| A1 Who you are | `creator_name`, `brand_name`, `handle`, `platform`, `niche` | The niche sentence is used to pick examples and diagrams. Keep their words. |
| A2 Brand colours | `accent`, `accent_name` | **Steps 1 and 2 only.** The document is a white page with black bars, so skip the dark-background, `paper` and `grey` questions (leave whatever another skill saved). After saving the accent, show them a swatch of it next to the darker shade the skill derives for small text and labels, on white. If their accent is very pale (a yellow, a pastel), say that the title keyword and arrows may read weakly on white and ask whether to use a deeper version of it for documents; if yes, save that as this skill's own accent with `--set-skill accent=#......` so their video skills keep the original. |
| A3 Fonts | `font_main_name`, `font_main_bold`, `font_main_regular`, `font_accent_name`, `font_accent` | See "Fonts for a document" below: this skill needs the regular weight, which the video skills treat as optional. Skip the caption font. |
| A9 Your real material | `proof_dir` | The proof grid at the top of every document is built from this folder. |

Skip A4 (profile picture), A5 (transcription), A7 (video files), A8 (sound) and "References they love" unless
another skill needs them. Do ask the reference question in Part 2 below, which is this skill's own version.

### Fonts for a document

A document is mostly paragraphs, so the **regular weight of the main font is required here**.

1. Ask the main font question from A3 and find both the bold and the regular weight on their computer. Save
   `font_main_bold` and `font_main_regular`.
2. If their headline font is a display face with no regular weight (or one that is tiring to read in paragraphs),
   say so and ask which font they want for body text. Save it as this skill's own regular weight, for example
   `--set-skill 'font_main_regular={"local": ["Helvetica Neue", "Arial"]}'`. A system font saved as `local` needs
   no file.
3. Ask: "Do you want the big title at the top in a different font from your headings, for example a serif, or the
   same font?" If different, find it, copy the file to `~/.claude/creator-profile/assets/fonts/`, and save
   `font_title` (`{"file": "..."}` or `{"local": [...]}`) and `font_title_name`. If the same, save nothing: it
   defaults to the main bold.
4. Ask the emphasis font question from A3: it sets the one keyword in the title. No preference: it defaults to the
   Playfair Display Italic that ships in `assets/fonts/`. Same font as the title, just in their colour: save the
   title font again as `font_accent` and its name as `font_accent_name`.

### The tools (check, do not ask)

```bash
node -v                                    # 18 or newer
ls ~/.claude/creator-profile/tools/node_modules/puppeteer-core >/dev/null 2>&1 && echo "renderer ok" || echo "renderer missing"
ffmpeg -version | head -1                  # only used for the split-screen mock
```

- Node missing: `brew install node` on a Mac, or the installer from nodejs.org.
- Renderer missing: tell them you are installing a small tool that takes the preview pictures, wait for the yes,
  then `npm install --prefix ~/.claude/creator-profile/tools puppeteer-core`. It does not download a browser.
- It drives a browser they already have: Google Chrome, Microsoft Edge, Brave, Arc or Chromium. If none is
  installed, ask them to install Chrome.
- ffmpeg missing: everything works except the split-screen mock picture. Offer `brew install ffmpeg`; do not insist.

## Part 2: this skill's questions

Ask each one on its own. Save with `python3 setup/apply_profile.py --set-skill key=value` (quote the pair when the
value has spaces: `--set-skill "series_name=The Sunday Sessions"`). If they do not mind, say what the default is
and save the default.

### What the documents say about you

| Ask | Key | Default |
|---|---|---|
| "Every document opens with a short 'why you should listen to me' section. What are the two or three real results you want there? For example: who you have helped, from where to where, how many people, how long you have done this. Give me the facts in your own words; I will never add to them." | `credibility` (their facts, in one value, kept in their words) | none: must be answered |
| "What should the small line above the title say: the name of your series, your channel, or your programme? It reads like 'Series Name · Episode 3 · Topic'." | `series_name` | `the channel name` |
| "Do you have your own framework images, models or diagrams for what you teach? Tell me the folder, or where they live." (so I use yours instead of drawing new ones) | `model_dir` | `none: draw the diagrams` |
| "One section gives the same advice for two kinds of viewer, for example 'If you're a coach' and 'If you sell a service'. Which two kinds of people watch you?" | `audience_types` | `decide per lesson from the script` |
| "Partway through, the document points viewers to one thing. What is that usually: a free download for that lesson, one main free resource, a booking link, a paid programme? And is there anything I must never say about it, such as the price?" | `cta_default` (what it is, its link if there is one, and any rules, in one value) | `a free download for that lesson; ask for its name and link each time` |

### How you write

| Ask | Key | Default |
|---|---|---|
| "British or American spelling?" (`AskUserQuestion`) | `spelling` = `British` or `American` | none: must be answered |
| "Drop in one or two scripts or posts that sound exactly like you (or paste them). I will write the documents in that voice." | not a profile key: see below | skipped if they have none |

For the samples: read them, then write 5 to 8 plain lines under `## Voice` in
`~/.claude/creator-profile/notes/lesson-doc-builder.md` describing how they write (sentence length, how they open
and close a point, words they use and avoid, how direct they are, humour, how they talk about their clients). Read
the lines back and correct them with the creator. If they have no sample, write "Voice: match the script given for
each lesson" there and move on.

### How you work

| Ask | Key | Default |
|---|---|---|
| "Where do your scripts and outlines live: do you paste them into the chat, or should I look somewhere (a folder, Google Docs, Notion)?" If it is an app, check whether a connector for it is available in this session and say plainly if it is not. | `script_source` | `pasted into the chat` |
| "Do you want the full document, with everything written out, or a notes version with just headings, diagrams and prompts to talk around?" (`AskUserQuestion`: full / notes / ask me each time) | `doc_version` = `full`, `notes` or `ask` | `full` |
| "When you record, is the document on the left of the screen with you on the right, or the other way round?" | `doc_side` = `left` or `right` | `left` |
| "Where should I save the documents?" | `docs_root` (a full path) | `~/lesson-docs` |

### A reference, if they have one

"Is there a video where someone teaches from a document on screen in a way you like? Drop the file in, or give me
the link." If yes: watch it (the `watch` skill if installed, otherwise frames with ffmpeg), note the layout, the
section order, how much text is on screen at once and how the diagrams look, compare with the section order in
`SKILL.md`, and tell them in a short list what already matches and what you would change. Only the changes they
pick become rules, saved under `## Style overrides` in the notes file, dated. A reference guides structure and
feel: never copy its wording or its diagrams.

## Part 3: finish

1. Read every answer back as a short summary (shared and this skill's). Fix anything they correct.
2. `python3 setup/apply_profile.py`. It fills every placeholder, copies their fonts into `assets/fonts/`, and writes
   `.configured`. It must end with "configured". If it prints `STILL TO ASK` or `UNFILLED`, ask for exactly those
   and run it again.
3. Prove the look before the first real document: `node scripts/render.cjs examples/sample-lesson/doc.html`, check
   it reports every font as loaded, then Read `examples/sample-lesson/preview/view-0.png` and show it to them: "This
   is a sample page in your colours and fonts. Anything to change?" Fix and re-run until they are happy. A font
   saved as `local` only renders while it is installed (Adobe Fonts need Creative Cloud running): tell them.
4. Tell them in two lines what is set up and what to try first: "Give me a script or an outline and say 'build the
   lesson doc'."

Later changes ("redo my setup", "change my colours", "new font"): ask only the affected questions, save them, run
`python3 setup/apply_profile.py` again, then `scripts/new.sh <slug>` on any existing document they want re-skinned
(it refreshes that document's CSS and fonts and leaves the writing alone). Rules they give while working go into
`~/.claude/creator-profile/notes/lesson-doc-builder.md` under `## Style overrides`, dated.
