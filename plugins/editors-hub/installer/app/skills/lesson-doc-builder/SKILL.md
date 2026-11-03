---
name: lesson-doc-builder
description: Build the on-screen teaching document a creator scrolls through while recording a long-form YouTube lesson. It is a split-screen format - a plain white "report" document fills one half of the frame and the creator is on camera in the other half. The document follows a fixed teaching layout (credibility + proof grid, reframe, named framework + formula, a method, Part #1/#2/#3 each with accent labels, a diagram, a black callout bar and a Diagnose list, in-video call to action, audience-type examples, Two Honest Limitations, apply-it loop, close + next episode) in the creator's own colours and fonts. Use whenever the creator asks for a "lesson doc", "episode doc", "doc for episode N", "the document I scroll in the video", "teaching doc", "rebuild for episode N", a "notes version" of one, a PDF of one, or wants a script, outline, lesson or topic turned into an on-screen teaching document. Not for slide decks, carousels or editing the recorded video.
---

# Lesson Doc Builder

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/lesson-doc-builder/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first. Do not start the task, and do
  not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if it exists,
  `~/.claude/creator-profile/notes/lesson-doc-builder.md`. Rules under `## Style overrides` in that notes file win
  over the defaults written below, and its `## Voice` section is how the creator writes.

"redo my setup" re-runs the interview at any time.

## Your setup

Filled in by setup. To change a line, change the answer (`setup/SETUP.md`), never this text.

| | |
|---|---|
| Creator | @@CREATOR_NAME@@ · @@BRAND_NAME@@ · @@HANDLE@@ |
| What they teach | @@NICHE@@ |
| Series or channel name (the kicker line) | @@SERIES_NAME@@ |
| Colours | accent @@ACCENT@@ (@@ACCENT_NAME@@) · small accent text and labels @@ACCENT_DARK@@ · page white · bars #111 |
| Fonts | body and headings: @@FONT_MAIN_NAME@@ · big title: @@FONT_TITLE_NAME@@ · title keyword: @@FONT_ACCENT_NAME@@ |
| Why people should listen (the credibility section) | @@CREDIBILITY@@ |
| Real proof (screenshots, results, reviews) lives in | `@@PROOF_DIR@@` |
| Their own framework images / models live in | `@@MODEL_DIR@@` |
| Scripts and outlines come from | @@SCRIPT_SOURCE@@ |
| Spelling | @@SPELLING@@ |
| The two audience types for the examples section | @@AUDIENCE_TYPES@@ |
| What the in-video call to action usually points to | @@CTA_DEFAULT@@ |
| Which version to build | @@DOC_VERSION@@ |
| The document sits on this half of the frame | @@DOC_SIDE@@ |
| Docs are saved in | `@@DOCS_ROOT@@/<slug>/` |

## What it makes

One self-contained HTML document (960px wide: one half of a 1080p frame), plus PNG previews:

- a full page
- 960×1080 scroll stops
- @4k stills (1920×2160: one half of a 4K frame)
- a split-screen mock with the document on the @@DOC_SIDE@@

The creator opens the HTML in their browser and scrolls it while recording. Alternatively, the @4k stills go into
the edit. On request it also makes a paged PDF for reading or presenting from a tablet.

Output goes to `@@DOCS_ROOT@@/<slug>/` (for example `ep03-topic-name`).

**Skill layout** (`SK=~/.claude/skills/lesson-doc-builder`):

- `assets/doc.css`: the design system, in the creator's colours and fonts. `assets/doc.js`: dot-grid and mix-bar
  helpers. `assets/starter.html`: a skeleton with the section order. `assets/fonts/`: the creator's fonts.
- `references/components.md`: classes, type hierarchy and diagram patterns. **Read it before writing.**
- `examples/sample-lesson/doc.html`: a complete worked document on an invented topic. Match its density, section
  rhythm and diagram style. It is a structure reference only: never reuse its wording.
- `scripts/new.sh <slug>`: scaffolds the folder (doc.html, doc.css, doc.js, fonts/, assets/). Running it again on
  an existing doc refreshes the CSS, JS and fonts without touching doc.html.
- `scripts/render.cjs <doc.html> [--stops 0,1300,…]`: renders the previews and reports whether each font loaded.
- `scripts/make-pdf.cjs <doc.html> <out.pdf>`: a 960×1280 paged PDF, one section per page.

## Workflow

1. **Find the source.** Scripts and outlines come from: @@SCRIPT_SOURCE@@. If the creator pasted or attached a
   script, outline, transcript or notes, that is the source. If they only gave a topic, ask for whatever they have
   (a script, a previous video on it, bullet points); with nothing but a topic, write an outline first and get a yes
   before building. For an episode in a series, read the previous episode's close ("In the next video…") so this
   one picks up where it left off. Their short-form scripts on the same topic are good for examples and for the
   one-line "land" sentences. Say which sources you used.
2. **Collect real assets:**
   - **Model image:** if the creator has their own framework image or diagram for the topic, use it (look in
     `@@MODEL_DIR@@`, or ask). If it comes from a link that expires (a Notion or cloud-drive file link), download it
     immediately. Make a web copy about 1400px wide (`sips -Z 1400 <file>` on a Mac).
   - **Proof shots:** take them from `@@PROOF_DIR@@`. Pick four that support this episode's claim. If the folder is
     empty or unset, ask the creator for four, and if they have none yet, leave the grid out rather than faking it.
   - Copy everything into `<slug>/assets/`. Use real assets; don't draw substitutes. Only draw SVG diagrams where no
     model image exists.
3. **Scaffold:** run `$SK/scripts/new.sh <slug>`, then write `doc.html` following the section order below.
4. **Render and check:** run `node $SK/scripts/render.cjs "@@DOCS_ROOT@@/<slug>/doc.html"`. It must report every
   font as loaded. Then Read the view-N.png files and check:
   - nothing is clipped
   - diagrams are legible
   - no orphaned single words in callout bars
   - the proof crops show faces and numbers
5. **Deliver:** show `preview/split-screen-1080p.png` (full-page.png is often too large to send to a phone, so say
   it is in the folder) and give the path of `doc.html`. Then list every `[bracketed]` item the creator must fill
   in.

## Section order (follow it; this is the format)

1. **Kicker + H1:** "@@SERIES_NAME@@ · Episode N · Pillar" (drop the parts that do not apply). The title is the
   video title, with one keyword in `<em>`.
2. **Credibility:** the `.runin` "How I know this works and why you should listen to me", one or two short
   paragraphs built only from the creator's real results (see "Why people should listen" in Your setup), then the
   `.proof` 2×2 grid.
3. **Reframe:** an h3 stating the common belief bluntly ("More input feels like progress. It isn't."), then why it
   fails, plus one diagram.
4. **Framework:** h2 with the framework name, "You can't control X. But you **can** …", an h5 "Map The …", a
   `.formula` line, a link to the free download or offer ("I'll show you how to use it in a minute"), then the
   `.model` image and "Each part has one job".
5. **Method:** an h3 with 3 numbered steps starting with bold verbs, one line, and a `.bar`.
6. **Part #1…#N.** Each h2 is a question ("Part #1: What Would You Actually Say This Week?"). Inside each:
   - explanation
   - an h4 sub-framework with `.label`s
   - a diagram
   - a real example
   - a `.bar`
   - an h4 "Diagnose …" list in the form `<b>Symptom:</b> what to check`
   - a transition line
7. **In-video call to action:** placed right after the part that creates the need. An h3 "If You're Working Through
   This Yourself", an h5 "I Can Show You With This Episode", the pitch for what it points to (default:
   @@CTA_DEFAULT@@), "Notice when that came up…", and a `.bar`. If the creator gave rules about their offer (never
   state the price, no guarantees, a named method), follow them exactly.
8. **By audience type:** two h3s, one per audience type (@@AUDIENCE_TYPES@@), each with bold-lead bullets, plus a
   `.bar`.
9. **Two Honest Limitations:** two bold-lead bullets.
10. **Apply it:** an h2 practical test ("Test It On Your Last Ten …") and a loop diagram.
11. **Close:** a summary `.bar`, a one-paragraph recap, "It won't be perfect. But it stops X and starts Y.", then an
    h3 "Continue With Episode N+1" with a `[link]`. For a one-off video, close on the call to action instead.

## The notes version

Some creators prefer a bare-bones document to riff from instead of a full script on screen. Build this when "Which
version to build" says `notes`, when it says `ask` and they choose it, or whenever they ask for "the notes version".

- Same kicker, title and credibility section.
- Each point: its heading, a one-line hook, the diagrams, 2 to 4 prompt bullets and its `.bar`.
- The in-video call to action stays.
- No Diagnose lists, no audience-type section, no limitations section.
- No `[bracketed]` or `.tbd` items on the page at all (the creator presents from it): list the open items in the
  chat instead.

Name the folder `<slug>-notes` so both versions can exist.

## PDF

When they want it on a tablet: `node $SK/scripts/make-pdf.cjs "<doc.html>" "<out.pdf>"`. Open the PDF and check no
diagram or proof grid was split across pages.

## Rules

- **Voice:** the creator's, never a generic one. Read `## Voice` in the notes file and the source script, and write
  the way they talk. The format's defaults, unless their voice says otherwise: short declarative sentences, "not X,
  but Y" contrasts, every section ending with a line that leads into the next. Use the script's own strongest
  one-line statements as `.bar`s. Spelling: @@SPELLING@@.
- **Copy is original.** If the creator shows a reference video or document, copy its structure only; never reuse
  another creator's wording.
- **Never invent** client names, results, stats, links, prices or the next episode's title. Put the missing item in
  `[brackets]` wrapped in `.tbd` and list it at the end. Only use proof captions you can read off the screenshot or
  that the creator has given you.
- **Brand:** white page, the main font for body text and headings, the title font for the h1 only, #111 bars, the
  accent colour for arrows, highlights and the title keyword, the darker accent for small text and labels. In SVG
  use the colour classes from `doc.css`, never a typed accent hex.
- **Figures stay in the main font.** Anything with a digit ("Part #1", "$10K", "400K") is set in the main font even
  inside the title: wrap digits in the h1 in `<span class="num">`.
- **Length:** around 8,000 to 10,000px tall, 6 to 8 `.bar`s, 5 to 7 diagrams. Paragraphs of no more than 3 lines.
- **Do not give the list away early.** In a "N rules / N steps" lesson, tease the number and the payoff in the
  opening; name each item only when its part arrives.
- Fill-in blanks use ▁ characters, never underscores.
- No em dashes in the document.
- Anything the creator tells you while working ("never do X", "always Y") goes straight into
  `~/.claude/creator-profile/notes/lesson-doc-builder.md` under `## Style overrides`, dated, and applies from then on.

## Where the format comes from

A long split-screen lesson: a white document on one half, the speaker on a plain colour on the other. They scroll
as they talk, zoom the proof screenshots to fill the document half, and cut away to live browser pages. The
document is the visual spine of the video, so it has to read clearly at a glance from a phone: big type, one idea
per screen, a diagram or a bar every screen or two.
