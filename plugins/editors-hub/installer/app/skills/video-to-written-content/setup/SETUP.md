# First-run setup: Video to Written Content

Run this when `python3 setup/apply_profile.py --status` says `"configured": false`, or when the creator says
"redo my setup". Work from the skill folder (`cd ~/.claude/skills/video-to-written-content`) so the commands below
run as written.

Read `setup/SHARED-SETUP.md` first: its opening section ("How to run the interview") is the rulebook. The short
version: **one question per message**, wait for the answer, save it straight away, never fill an answer in from
memory, and offer the default whenever they do not know or do not mind.

Start by checking what is already answered (another skill in the pack may have asked the shared questions):

```bash
python3 setup/apply_profile.py --status
cat ~/.claude/creator-profile/profile.json 2>/dev/null
```

Then tell them in two lines what is about to happen: "Before I write anything as you, a few questions so it sounds
like you and points to the right places. About five minutes, and the most useful part is two or three things you
wrote yourself."

---

## Part 1: the shared questions (from SHARED-SETUP.md)

This is a writing skill, not an editing skill. It runs two of the shared sections and skips the rest (A2-A4, A6-A9
and "References they love"): no colours, fonts, sound, profile picture or footage folders are needed here.

| Section | Run it? | Notes |
|---|---|---|
| **A1. Who you are** | Yes, all four rows | `creator_name`, `brand_name` and `niche` are required by this skill. `handle` and `platform` are shared with the other skills in the pack: ask them once, and accept "skip" for either. |
| **A5. Transcription** | Yes | Every run starts by transcribing. Ask it as written. For this skill, add one line to the comparison: ElevenLabs also spells names and brand terms correctly more often (it is given the list from the "key terms" question below) and labels speakers on interviews; the free local option does neither. Never ask them to paste an API key into the chat. |

Check the tools without asking:

```bash
ffmpeg -version | head -1
yt-dlp --version
python3 -c "import requests; print('requests ok')"     # only needed for ElevenLabs
```

If something is missing, give them the one command that fixes it (`brew install ffmpeg yt-dlp`,
`pip3 install requests`) and wait until it passes. If they chose local transcription, also check
`npx hyperframes doctor`.

---

## Part 2: this skill's questions

Ask them in this order, one per message. Save each answer the moment you have it with
`python3 setup/apply_profile.py --set-skill key=value`. Quote the whole pair when the value has spaces or is a
list: `--set-skill 'outputs=["emails", "linkedin"]'`, `--set-skill "default_cta=link to the source video"`.

### 1. What to write

| Ask | Saves to | Default / what to do with the answer |
|---|---|---|
| "Which kinds of writing do you want from each video by default?" Use `AskUserQuestion` with multi-select: **Emails** (to your list) / **YouTube Community posts** / **LinkedIn posts** / **X and Threads posts**. Say that they can ask for a different mix on any single video. | `outputs` | Default `["emails", "youtube-community"]`. Save a JSON list using exactly these keys: `emails`, `youtube-community`, `linkedin`, `x-threads`. At least one. Do not talk them into more formats than they will use: unused drafts are clutter. |

### 2. Their voice on the page (the most important question)

Ask: "Paste or upload two or three emails or posts you wrote **yourself** and are proud of. Things that sound like
you on a good day. They do not need to be about the same topic as your videos."

Say why: the video tells me what you think; these tell me how you write it down. People do not write the way they
talk.

- Samples for the formats they chose are the most useful (an email if they chose emails, a LinkedIn post if they
  chose LinkedIn). Ask for the missing kind once if they only give one kind; do not insist.
- If a sample was written by a copywriter, a team member or an AI tool, ask for one they wrote themselves. If they
  have none, that is an answer: go to "No samples" below.
- A link to a public post or a newsletter archive is fine: open it and read it.

**Analyse the samples** (read each one fully first). Write down, with a short quoted example for each point where
it helps (a few words, never whole paragraphs):

1. **Sentences**: typical length, how much it varies, fragments or full sentences, how often a one-line paragraph.
2. **Paragraphs and layout**: length, line breaks, lists, headings, bold, capitals for emphasis.
3. **Openings**: how each piece starts (greeting or none, straight into a story, a claim, a question).
4. **Endings and sign-off**: how they close, how they ask for something, the exact sign-off and any P.S. habit.
5. **Vocabulary they use**: favourite words and phrases, coined terms, slang, swearing or none, how formal.
6. **Vocabulary they avoid**: what is noticeably absent (jargon, hype words, exclamation marks, emoji).
7. **Person and address**: "I" and "you" or "we", how they refer to the reader and to clients.
8. **Punctuation and spelling**: British or American, contractions, dashes, ellipses, brackets, emoji, hashtags.
9. **Tone**: two or three plain words (dry, warm, blunt, teacherly), and what they never sound like.
10. **Differences by format**, if the samples show them (their emails versus their posts).

Read the summary back to them in five or six plain lines ("Short sentences, often one per line. You open in the
middle of a story and never greet. You say 'folks', never 'guys'...") and ask what is wrong or missing. Their
corrections win over your reading.

**Save it** to `~/.claude/creator-profile/notes/video-to-written-content.md` (create the folder and file if needed;
keep any other sections already in the file):

```markdown
## Voice

Based on <n> samples the creator wrote themselves (<what they were>), analysed <date>.

- Sentences: ...
- Paragraphs and layout: ...
- Openings: ...
- Endings and sign-off: ...
- Uses: ...
- Avoids: ...
- Person and address: ...
- Punctuation and spelling: ...
- Tone: ...
- By format: ...

Phrases that are theirs (use sparingly, never as filler): "...", "..."

## Samples

Saved in ~/.claude/creator-profile/notes/voice-samples/: <file names>
```

Save the samples themselves as plain text files in `~/.claude/creator-profile/notes/voice-samples/` so the analysis
can be redone later. They stay on this computer. Then:

```bash
python3 setup/apply_profile.py --set-skill "voice_samples=3 samples analysed (2 emails, 1 LinkedIn post)"
```

Two rules to say out loud, because they shape what they can expect: the samples only tune **how it reads**. The
ideas, stories, numbers and opinions in every piece come from the video's transcript and nowhere else. And the pack's
fixed style rules (nothing invented, no em dashes in finished copy, no stock AI phrases) still apply even where a
sample breaks them, unless they tell you to change one, which goes under `## Style overrides` in the same notes file.

**No samples**: save `--set-skill "voice_samples=none yet: voice taken from how they speak in each video"` and tell
them they can add samples at any time by saying "here are some voice samples". Do not write a `## Voice` section
from guesswork.

### 3. Where a call to action may point

| Ask | Saves to | Default / what to do with the answer |
|---|---|---|
| "What can a piece point people to? Offers, free guides or lead magnets, a newsletter, a community, a booking link. For each one give me its name, the link, and when it fits." Take them one at a time if there are several. | `offers` | Default `none`. Save a JSON list of strings, one per item, in the form `Name: URL (use when ...)`, for example `--set-skill 'offers=["Free pricing guide: https://example.com/guide (use when the piece is about pricing or money)", "Coaching call: https://example.com/call (use only when they ask for it)"]'`. Copy names and URLs exactly; never tidy or guess a link. Do not use the upright bar character in an answer (it breaks the setup table in SKILL.md). If they have nothing, save the string `none`. |
| "When none of those fits a piece, what should the ending point to? The usual choice is a link to the video it came from." | `default_cta` | Default `link to the source video`. Other common answers: `ask them to reply`, `no call to action`. |

Say once: a call to action is only added when it fits the piece. Most short posts will have none.

### 4. Emails and audience

Ask these two even if they did not choose emails as a default format (they can ask for emails on any video), but
keep it quick.

| Ask | Saves to | Default / what to do with the answer |
|---|---|---|
| "How do you sign off your emails? Give me the exact words." If the voice samples already show it, read it back instead: "You sign off 'Speak soon, Sam'. Keep that?" | `email_signoff` | Default `the creator's first name on its own line` (save it with their real first name: `--set-skill "email_signoff=Sam"`). Save multi-line sign-offs with ` / ` for the line break (`Speak soon, / Sam`). |
| "Do you have a name for your list or your audience? Some people write to 'the Sunday crew' or 'founders'. No name is fine." | `audience_name` | Default `no name: write to one reader as "you"`. |

### 5. Spelling and the words that must be right

| Ask | Saves to | Default / what to do with the answer |
|---|---|---|
| "British or American spelling?" Use `AskUserQuestion`: British / American / Match how I speak in each video. If the samples settle it, read it back instead of asking. | `spelling` | Default `match the speaker`. Save `British`, `American` or `match the speaker`. |
| "Which names, brand names and terms does the transcript need to spell correctly? Your own frameworks and product names, people you mention often, anything a transcriber would get wrong." | `keyterms` | Always start the list with their name and brand name from A1, then add what they give. Save a JSON list: `--set-skill 'keyterms=["Sam Okafor", "Okafor Studio", "The Quiet Launch", "Kajabi"]'`. Check the spelling of each with them: this list is treated as correct from now on. It is passed to the transcriber automatically on every run. Keep it under about 50 terms; the most-used ones first. |
| "Are there words or phrases you never want to see in your copy? Things that make you wince." Read them the built-in list first so they do not repeat it: delve, unlock, unleash, game-changer, elevate, "in today's fast-paced world", "let that sink in", "here's the thing", "buckle up". | `banned_phrases` | Default `none added`. Save a JSON list of what they add (`--set-skill 'banned_phrases=["hustle", "crush it", "journey"]'`), or the string `none added`. Their list is added to the built-in one; it never replaces it. |

### 6. Where the writing goes

| Ask | Saves to | Default / what to do with the answer |
|---|---|---|
| "Where should the finished writing go? Each video gets its own folder. By default that is a folder called video-content inside whatever folder you are working in." | `output_dir` | Default `./video-content`. For one fixed place, save a full path (`~/Documents/Video Content`). Check that a named folder exists or can be created. |

---

## Finishing

1. Read every answer back as a short summary (name and brand, formats, the voice in three lines, offers and default
   call to action, sign-off and audience name, spelling, key terms, banned words, output folder, transcription).
   Fix anything they correct.
2. Fill the skill:

   ```bash
   python3 setup/apply_profile.py
   ```

   It must end with `configured: every placeholder is filled.` If it prints `STILL TO ASK` or `UNFILLED`, ask for
   exactly those answers, save them, and run it again.
3. If they chose ElevenLabs, check the key is in place without printing it (from the skill folder):
   `python3 -c "import sys; sys.path.insert(0,'scripts'); import stt; print('key found' if stt.el_key(False) else 'no key yet')"`.
   If it says no key yet, give them the three steps from section A5 again and wait. Never ask for the key in chat.
4. Tell them in two lines what is set up and what to try first: "Give me a YouTube link or a video file and say
   'turn this into written content'."

## Later changes

- "Redo my setup": run this file again from the top; read back each saved answer and only change what they change.
- "Here are some voice samples" / "that doesn't sound like me": add the samples to the voice-samples folder, redo
  the analysis over all of them, rewrite `## Voice`, update `voice_samples`, run `apply_profile.py`. Specific
  corrections ("I never start with a question") go under `## Style overrides`, dated.
- "I have a new offer" / "that link changed": update `offers` (send the whole list again with the change made), run
  `apply_profile.py`. Never leave an old link in the list.
- "Add LinkedIn" / "stop writing Community posts": update `outputs`, run `apply_profile.py`.
- "Always spell X like this": add it to `keyterms` (send the whole list again), run `apply_profile.py`.
- "Never use the word X": add it to `banned_phrases`, run `apply_profile.py`.
- Switch transcription: `python3 setup/apply_profile.py --set transcriber=local` (or `elevenlabs`), then run
  `apply_profile.py`.
