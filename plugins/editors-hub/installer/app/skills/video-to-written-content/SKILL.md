---
name: video-to-written-content
description: Turn a YouTube video URL or video file into standalone written content in the creator's own voice, such as emails and YouTube Community posts, and optionally LinkedIn posts and X / Threads posts. Transcribes the video accurately, mines the full transcript for the strongest distinct ideas, and writes platform-native copy with nothing invented. Use when the user shares a YouTube link or video file and asks for emails, Community posts, LinkedIn posts, tweets or threads, newsletter ideas, or written content from it, types /video-to-written-content, or says "redo my setup" for this skill.
---

# Video to Written Content

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/video-to-written-content/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first. Do not start the task, and do
  not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if it exists,
  `~/.claude/creator-profile/notes/video-to-written-content.md`. That notes file holds the creator's `## Voice`
  (how their writing reads, taken from samples they wrote themselves) and any `## Style overrides`. Rules under
  `## Style overrides` win over the defaults written below.

"redo my setup" re-runs the interview at any time.

## Your setup

Filled in by the setup interview. If a line still shows a placeholder in double at-signs, setup has not finished.

| | |
|---|---|
| Creator (the voice everything is written in) | @@CREATOR_NAME@@ |
| Brand | @@BRAND_NAME@@ |
| What they do | @@NICHE@@ |
| Formats to write by default | @@OUTPUTS@@ |
| Voice samples | @@VOICE_SAMPLES@@ (analysis in `~/.claude/creator-profile/notes/video-to-written-content.md` under `## Voice`) |
| Offers, lead magnets and links a CTA may point to | @@OFFERS@@ |
| CTA when nothing else fits | @@DEFAULT_CTA@@ |
| Email sign-off | @@EMAIL_SIGNOFF@@ |
| What they call their list / audience | @@AUDIENCE_NAME@@ |
| Spelling | @@SPELLING@@ |
| Names and terms the transcriber must spell correctly | @@KEYTERMS@@ |
| Extra words and phrases never to use | @@BANNED_PHRASES@@ |
| Output folder | `@@OUTPUT_DIR@@` |
| Transcription | @@TRANSCRIBER@@ |

## The job

The job is not to repurpose a video. The job is to find the intellectual value inside it and rewrite the strongest ideas as content that feels like it was written for each platform from the start, in the speaker's voice, with nothing invented.

The finished work should read like: "I watched the video, pulled the best ideas, and wrote them properly for these platforms." Never like: "AI summarised a transcript."

Two sources, two jobs. **The transcript is the only source of ideas and facts.** The **voice samples** (the `## Voice` notes) tune how it reads on the page: sentence length, how a piece opens, the words they reach for and the ones they avoid, how they sign off. A sample never supplies a story, a number or an opinion for a piece, and a habit from the samples never overrides an accuracy rule.

## Inputs

- A YouTube URL, or a path to a video/audio file (mp4, mov, m4a, mp3, wav...).
- Optional, for this run only: a different set of formats ("just emails this time", "add LinkedIn"), an output location, a CTA/offer/lead magnet to use, or extra names and terms the transcript should spell correctly. A request in the conversation wins over the saved setup for that run; it does not change the saved setup unless they say so.

## Which formats to write

Write only the formats listed under "Formats to write by default" (`@@OUTPUTS@@`), unless the creator names a different set for this run. The four formats and their folders:

| Format key | What it is | Folder | Section |
|---|---|---|---|
| `emails` | Standalone emails to their list | `emails/` | Step 3 |
| `youtube-community` | Posts for the YouTube Community tab | `youtube-community/` | Step 4 |
| `linkedin` | LinkedIn posts | `linkedin/` | Step 5 |
| `x-threads` | Posts and threads for X and Threads | `x-threads/` | Step 6 |

Skip the step, the folder and the index section of any format that was not chosen. Do not create empty folders.

## Output structure

One folder per video, named with a short slug of the video title:

```
<output folder>/<video-name>/
  transcript.md
  content-index.md
  emails/                 (only the chosen formats get a folder)
    01-<topic>.md
    02-<topic>.md
  youtube-community/
    01-<topic>.md
  linkedin/
    01-<topic>.md
  x-threads/
    01-<topic>.md
  _source/                (raw transcription output, kept for reference)
```

The parent folder is the output folder from setup (`@@OUTPUT_DIR@@`; a path starting with `./` is relative to the current working directory) unless the user names another location for this run.

---

## Step 1: Transcribe

Run the bundled script. It handles YouTube download (yt-dlp), audio extraction (ffmpeg) and the transcription itself, and creates the project folder.

```bash
python3 ~/.claude/skills/video-to-written-content/scripts/transcribe.py "<url-or-file>" \
  [--out <folder>] [--keyterms "Guest Name,Product Name"] [--speakers N] [--language en]
```

- The script transcribes with the engine chosen at setup (`@@TRANSCRIBER@@`), through `scripts/stt.py`:
  - **`elevenlabs` (recommended for accuracy)**: ElevenLabs Speech-to-Text. The most accurate words, speaker labels on interviews, and it uses the key terms. About $0.22 per hour of audio.
  - **`local` (the free option)**: runs on this computer through HyperFrames. No cost and nothing leaves the machine. Names and unusual terms are misheard more often, there are no speaker labels, and key terms are not used, so Step 1b needs a closer read.
- The key terms saved at setup (`@@KEYTERMS@@`) are passed automatically. Use `--keyterms` only to **add** proper nouns specific to this video that you can anticipate: guest names from the title or description, a product or book that is mentioned.
- Pass `--speakers` if the video is clearly an interview or podcast with a known number of people. Speakers are detected automatically on ElevenLabs; the number is a note for you.
- `--language` is only needed when the video is not in English and the engine guesses wrong.
- The script prints `project_folder=...` and `engine=...` when done. Use that path for everything below.

Requirements: `ffmpeg` and `yt-dlp`; for ElevenLabs, Python `requests` and `ELEVENLABS_API_KEY` in the environment or shell profile; for local, `npx hyperframes` (Node 22). If anything is missing, the script names it. Install tools with the one command it gives (`pip3 install yt-dlp requests`, `brew install ffmpeg`).

If the ElevenLabs key is missing or rejected: **never ask for the key in chat and never print one.** Tell the creator to add it to their shell profile themselves (the steps are in section A5 of `setup/SHARED-SETUP.md`), or offer to switch to local transcription (`python3 setup/apply_profile.py --set transcriber=local`, then run `apply_profile.py` again). Switching engine is their decision: say what changes (accuracy, speaker labels) and wait for the answer.

Do not fall back silently to YouTube auto-captions or any other transcriber, because accuracy matters more than speed here. If the chosen engine cannot run, stop and say so.

If the session has no shell but has an ElevenLabs connector, upload the audio and use its transcribe tool instead, then continue from Step 1b.

### Step 1b: Clean the transcript into transcript.md

Read `_source/transcript.raw.md` in full. Write `transcript.md` in the project folder:

- Keep every sentence and the original order. This is the complete record, not a summary.
- Fix obvious mis-hearings using context (wrong homophones, mangled names, brand names). The key terms in the setup table are the correct spellings. Never change what the speaker meant.
- Fix punctuation and sentence breaks so it reads cleanly. Keep the `[mm:ss]` markers.
- Remove pure filler only where it adds nothing ("um", "uh", stutters, false starts that restart the same sentence). Keep the speaker's phrasing, slang and verbal style.
- If a word is genuinely unclear, write `[unclear: best guess]` rather than inventing.
- With local transcription there are no speaker labels: on an interview, work out who is speaking from what is said and label the paragraphs. Where you cannot tell, mark it `[speaker unclear]` and never attribute that passage to the creator in a finished piece.
- Header: video title, source URL or file, date processed, transcription engine.

Every later step works from this full transcript. Do not summarise before analysing.

---

## Step 2: Analyse the whole transcript

Read `transcript.md` end to end before writing anything. Build a private idea list (not a file) of every standalone idea, with its timestamp range. Look for:

strong opinions, contrarian points, lessons, stories, realisations, frameworks, step-by-step advice, mistakes, misconceptions, useful tips, memorable lines, analogies, personal experiences, problem/solution pairs, interesting questions, moments that challenge a common assumption, ideas that would start a conversation.

Rules for the list:

- Extract ideas, not sections. One section of the video can hold three ideas. One idea can be spread across the whole video; gather all of it.
- Test each idea: would it give real value to someone who has never seen the video? If not, drop it.
- Merge ideas that make the same point. No two finished pieces in the same format should communicate the same core message.
- For each idea, note what the transcript actually supplies: the claim, the reasoning, any story, example, number, client result or memorable phrase. That is the full pool of material you are allowed to use.
- Note any CTA the video itself makes (offer, lead magnet, another video, community, app, book, link in description).

Then decide where each idea goes, among the chosen formats only:

- **Email** when the idea has depth: a story, an argument with reasoning, a framework, a mistake-and-lesson, something that rewards 2 to 4 minutes of reading.
- **Community post** when the idea lands fast for people who already follow the channel: a sharp opinion, a single realisation, a question worth debating, a quick list, a memorable line, a poll-shaped choice.
- **LinkedIn post** when the idea carries a lesson about work, business, craft or a career that a professional stranger can use: a story with a point, a counter-intuitive opinion with the reasoning, a framework, a mistake and what changed.
- **X / Threads** when the idea compresses to a line or two without losing its truth (single post), or unfolds as a clear sequence of short steps (thread).
- An idea can feed more than one format only if the pieces take genuinely different angles (for example the email tells the full story, the Community post asks the audience the question the story raises, the LinkedIn post draws the professional lesson, the X post is the one line people would quote). Never ship a piece that is just a shortened or lengthened copy of another piece.

There is no target count. A 10-minute video might give 2 emails and 5 posts; a 60-minute one might give 8 and 15, or the reverse. Only write a piece when there is a distinct, valuable idea behind it. Never write filler to fill a number.

---

## Step 3: Write the emails  *(format `emails`)*

One idea per email. Each email must work on its own and must read like it was written as an email.

You may restructure the point completely for reading: change the order, open with the story's end, cut the tangents, combine scattered remarks into one argument. You may not change the argument or the speaker's point of view.

Each email needs:
- 3 to 5 subject line options, varied in approach (curiosity, bold claim, plain-spoken, question, specific detail). Short, lowercase-friendly, no clickbait the email doesn't pay off.
- A strong first line that pulls the reader in. No "Hey friend, hope you're well." No "In this email I'll...". If the `## Voice` notes show how the creator really opens their emails (a greeting they always use, straight into a story), open that way.
- One clear central idea.
- Supporting explanation, story or example from the transcript where it exists. Use storytelling when the transcript gives enough material; if it doesn't, don't fake a story.
- A takeaway the reader can act on or think about.
- A natural ending. A CTA only if the video naturally connects to one. Choose it in this order: (1) a CTA the creator asked for in this run; (2) a CTA the video itself makes; (3) an offer, lead magnet or link from the setup table whose "use when" genuinely fits this email's idea; (4) the default CTA from the setup table (`@@DEFAULT_CTA@@`). Never force a sales CTA. "Hit reply and tell me..." is fine when it fits. Use only the names and URLs in the setup table or the transcript; never invent a link, a price or a deadline. If the source is a local file with no URL, write `[link to the video]` where the link goes.
- The sign-off from the setup table (`@@EMAIL_SIGNOFF@@`), exactly as given.
- When the email addresses the readers as a group, use the creator's name for them (`@@AUDIENCE_NAME@@`). If that says there is no name, address one reader as "you".

File format (`emails/NN-<topic-slug>.md`):

```markdown
# <Email Title>

## Subject Line Options

1. ...
2. ...
3. ...

## Email

<email copy>

## Source

<Which idea or part of the video inspired this, with timestamp range, e.g. "[04:12–07:30] the story about losing the first client and what it taught them about pricing">
```

---

## Step 4: Write the YouTube Community posts  *(format `youtube-community`)*

Written for the Community tab specifically: someone scrolling, reading in two seconds whether it's worth stopping for.

Should be easy to read, conversational, interesting from the first line, opinionated where the speaker was, able to stand alone, and built to make people think, reply or vote.

Vary the format based on the material. Do not use one template for every post. Options:
- short observation
- a question
- contrarian opinion
- mini story
- quick lesson
- list
- framework (simple, a few lines)
- poll idea (write the question plus 2 to 4 options, and label it `Poll` so the user knows to use the poll feature)
- statement followed by a short explanation
- conversation starter

Some posts can be one or two lines if the idea is strong. Others can run longer when the context makes it better. End with a natural question only where it genuinely invites discussion. No engagement bait tacked onto every post ("Thoughts? 👇").

File format (`youtube-community/NN-<topic-slug>.md`):

```markdown
# Community Post

<finished post, ready to paste>

## Source

<Which idea or part of the video inspired this, with timestamp range>
```

---

## Step 5: Write the LinkedIn posts  *(format `linkedin`)*

Written for the LinkedIn feed specifically: a reader who does not know the creator, sees two lines and a "see more", and decides in that moment. Most of them are at work, reading as professionals, and will only stop for something they can use or argue with.

What makes a post native to LinkedIn:
- **The first two lines do all the work.** Only about the first 200 characters show before "see more" (fewer on a phone). Open with the tension, the claim or the moment of the story, in the creator's words. No warm-up, no "I've been thinking about...", no "Excited to share".
- **Built for reading on a phone.** Short paragraphs of one to three sentences with a blank line between them. Plain text only: LinkedIn has no bold or headings, so no markdown inside the post. A simple list with hyphens or numbers is fine when the idea really is a list.
- **One idea, taken to a useful conclusion.** Most posts land between 600 and 1,500 characters. The hard limit is 3,000. Length follows the idea: a strong opinion can be five lines.
- **A lesson from experience, not a lecture.** LinkedIn rewards "this happened, this is what I learned, this is what I do now". Use the story when the transcript gives one. If it does not, state the opinion and the reasoning; do not fake a story.
- **Professional, in their voice.** Keep the creator's phrasing, terms and directness. Do not polish it into corporate language, and do not adopt the LinkedIn clichés: one-word lines stacked for drama, "Agree?", "Here's what nobody tells you", humble-brag openings, emoji bullets.
- **An ending that earns a reply.** A specific question the reader can answer from their own experience, or a clean last line. A CTA only when it fits, chosen by the same order as in Step 3. LinkedIn tends to show posts with a link in the body to fewer people, so write the post to stand without one and put any link on its own line under `## Link (first comment or end of post)` for the creator to place.
- **Hashtags**: none by default. At most three, specific to the topic, on the last line, and only if the `## Voice` notes show the creator uses them.

Vary the format based on the material. Options:
- story with a lesson
- contrarian opinion with the reasoning
- mistake and what changed
- framework or short numbered list
- observation from working with clients or customers (only what the transcript states)
- a before / after
- a question worth debating, with the creator's own answer first

File format (`linkedin/NN-<topic-slug>.md`):

```markdown
# LinkedIn Post

<finished post, plain text, ready to paste>

## Link (first comment or end of post)

<the URL and one line to go with it, or "None">

## Source

<Which idea or part of the video inspired this, with timestamp range>
```

---

## Step 6: Write the X / Threads posts  *(format `x-threads`)*

Written for X and Threads specifically: a fast feed where a post is judged in one glance and shared when it says something a reader wishes they had said. The same file serves both platforms.

What makes a post native here:
- **Compression without distortion.** One idea, said as tightly as the creator would say it at their sharpest. If shortening it would strengthen the claim beyond what was said, it is not a single post: make it a thread or leave it for another format.
- **Every post fits in 280 characters**, including each post inside a thread, so it works on a standard X account and on Threads (which allows 500). Count them. Only go longer if the `## Style overrides` notes say the creator posts long-form.
- **The first post must stand alone.** In a thread, most readers only ever see post one. It carries the claim or the promise by itself. No "A thread 🧵", no "Let me explain".
- **Plain text.** No hashtags, no markdown, no emoji unless the `## Voice` notes show the creator uses them. Line breaks are fine and often help.
- **Memorable lines word for word.** This is the format where the creator's exact phrase from the transcript matters most. Use it when it works in writing.
- **Links at the end.** A link goes in the last post of a thread, or in a reply to a single post, chosen by the same order as in Step 3. Many posts need no CTA at all.

Vary the format based on the material. Options:
- single post: a sharp opinion, a realisation, a one-line reframe
- single post: a question the creator genuinely wants answered
- single post: a short list (3 to 5 lines)
- single post: a two-line contrast (what people do, what works) when the transcript makes that contrast
- thread (3 to 8 posts): a story told in order, a step-by-step method, or a framework with one part per post. Each post makes sense if read alone, and the last one lands the point rather than asking for a follow.

A thread is only worth writing when the idea has real sequence. Never pad a single idea into a thread, and never cut an email into numbered pieces.

File format (`x-threads/NN-<topic-slug>.md`):

```markdown
# X / Threads: <Single post | Thread (N posts)>

<For a single post: the finished post, ready to paste.>

<For a thread: each post under its own number, ready to paste one at a time.>

1/
<post>

2/
<post>

## Link (last post or reply)

<the URL and one line to go with it, or "None">

## Source

<Which idea or part of the video inspired this, with timestamp range>
```

---

## Step 7: content-index.md

A simple review sheet for the whole video. Include a section only for each format that was written:

```markdown
# Content Index: <Video Title>

Source: <url or file> · Processed: <date> · Transcribed with: <engine>

## Emails

1. **<Email Title>** (`emails/01-....md`)
   Core idea: <one sentence>

## YouTube Community Posts

1. **<Short label>** (`youtube-community/01-....md`) · Format: <question / list / poll / ...>
   Core idea: <one sentence>

## LinkedIn Posts

1. **<Short label>** (`linkedin/01-....md`) · Format: <story / opinion / framework / ...>
   Core idea: <one sentence>

## X / Threads Posts

1. **<Short label>** (`x-threads/01-....md`) · Format: <single post / thread (N posts)>
   Core idea: <one sentence>

## Ideas considered but not used

- <idea>: <why, e.g. "overlaps with email 2", "needs the visual from the video", "too thin to stand alone">
```

The "not used" list is short and helps the user see the judgment calls.

---

## Voice and writing rules (apply to every finished piece)

Voice:
- Keep the speaker's personality, beliefs, arguments, terminology and point of view. If they say "bro", call things by their own names, use specific coined terms or framework names, keep them.
- Keep memorable phrases from the speaker word for word when they work in writing. Rewrite the surrounding material for clarity.
- Write in the first person as the speaker. If the video is an interview or features someone other than the creator, write only from what the creator said, and ask before writing in anyone else's voice.
- Apply the `## Voice` notes from the creator's own writing samples: their typical sentence length, how they open and close, the words they use and avoid, their punctuation habits and how they sign off. Where the notes and the way they speak in this video differ, the page follows the notes for rhythm and form and the video for substance.
- If there are no voice samples yet (the setup table says so), write from how they speak in the transcript, and mention once in the report that two or three samples of their own writing would sharpen the voice.

Accuracy (hard rules):
- Never invent stories, results, statistics, numbers, client names, experiences, quotes or opinions. Every factual claim must trace back to the transcript.
- Never strengthen a claim beyond what was said ("a lot of clients" does not become "hundreds of clients").
- If a piece would need a detail the video doesn't give, rewrite the piece so it doesn't need it, or drop it.
- The voice samples and the setup table are never a source of facts for a piece, with one exception: the names and URLs of the creator's own offers, used only in a CTA.

Style:
- Natural and conversational. Write how the speaker talks, minus the repetition that only works out loud.
- No em dashes (—) anywhere in finished copy. Use a full stop, comma, colon or brackets instead. En dashes are only allowed in timestamp ranges in Source sections. This holds even if the creator's samples use them, unless a `## Style overrides` note says otherwise.
- Never call a section of a story, script or framework a "beat". Use "part", "step", "section" or "moment".
- No generic AI language: delve, unlock, unleash, game-changer, elevate, navigate the landscape, in today's fast-paced world, it's not just X it's Y, let that sink in, here's the thing, buckle up.
- The creator's own banned list, on top of the one above: @@BANNED_PHRASES@@. Plus anything listed under "avoids" in the `## Voice` notes.
- No hollow motivation ("You've got this!", "The choice is yours."). No corporate polish.
- Short paragraphs. Minimal headings inside the copy itself (none in Community, LinkedIn or X / Threads posts, rarely in emails).
- Avoid reflexive groups of three and tidy rhetorical symmetry.
- Spelling: @@SPELLING@@. ("match the speaker" means British or American as the creator themselves writes and speaks: check the voice samples first, then the accent and vocabulary in the video. Be consistent across every file.)

---

## Final check before reporting back

Run through every finished file, in the folders of the formats that were written:

1. `grep -rn "—" emails youtube-community linkedin x-threads 2>/dev/null` returns nothing in the copy.
2. `grep -rniE "\bbeats?\b" emails youtube-community linkedin x-threads 2>/dev/null` returns nothing used in the sense of a section. Then search the same folders for every phrase on both banned lists (the built-in one and the creator's own).
3. Each piece has one central idea, and no two pieces make the same point in the same way.
4. Every story, number and result appears in transcript.md. Spot-check each against its Source timestamp. Every link and offer name appears in the setup table or the transcript.
5. No piece is a shortened or stretched copy of another: no Community post that is a shortened email, no thread that is an email cut into pieces.
6. Each email has 3 to 5 subject lines and the right sign-off; every post in `x-threads/` is 280 characters or fewer; each file has a Source section.
7. Spelling is consistent with the setup choice, and the key terms are spelled as given.
8. content-index.md lists every file and the counts match the folders. No folder exists for a format that was not chosen.

Then tell the user, briefly: where the folder is, how many pieces came out in each format, and the one or two strongest pieces worth looking at first. Don't recap the steps.

If they give feedback that is a standing rule ("never open with a question", "my emails are always under 200 words"), save it straight away under `## Style overrides` in `~/.claude/creator-profile/notes/video-to-written-content.md`, dated, and apply it from then on.
