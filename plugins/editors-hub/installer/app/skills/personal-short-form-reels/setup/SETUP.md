# First-run setup: Personal Short Form Reels

Run this the first time the skill is used (the gate in `SKILL.md` sends you here), and again whenever the creator says
"redo my setup". The goal is complete clarity on how this creator's personal reels should be edited, so the first
edit is already theirs.

**Ask one question per message, wait for the answer, save it, then ask the next.** The full rules for running the
interview are at the top of `setup/SHARED-SETUP.md`: read them before the first question.

Start by telling the creator, in two or three lines, what is about to happen: a short series of questions about their
brand, their footage and how they like their videos edited, asked one at a time, which only happens once. Mention the
three things this skill needs on their computer, and check them yourself (section A6): **HyperFrames** (it builds and
renders every reel), **ffmpeg**, and a transcriber: **ElevenLabs** is the best and is what the skill was built on,
or transcription that runs locally on their computer for free.

## Part 1: the shared questions

Work through `setup/SHARED-SETUP.md` sections **A1 to A9**, in order. Skip any answer already in
`~/.claude/creator-profile/profile.json` after reading it back in one line (if they set up another skill in this pack
first, most of these are already answered).

Save shared answers with `python3 setup/apply_profile.py --set key=value`.

For this skill, section A8 (sound) matters more than usual: ask for their **favourite music beds** by name. For each
one they give, find the file, look at its loudness profile (`python3 scripts/music_profile.py "<file>"`), choose the
second the music should start from (where it is already playing properly, not a quiet intro), and write the list to
`~/.claude/creator-profile/assets/music.json`:

```json
{"root": "<music folder>", "favourites": [{"label": "Short name", "file": "path inside root", "start": 12.0, "feel": "one line"}], "rejected": []}
```

## Part 2: references

Run the **"References they love"** section of `setup/SHARED-SETUP.md`. Ask it plainly:

> "Do you have two or three short videos whose editing you want yours to feel like? Download them and upload them to
> this chat so I can study them properly."

Analyse each one against this skill's defaults (creator full screen with one-word captions, fast full-frame B-roll on
the cuts, a small graphic under the caption, split screen for software, quiet sound, a music bed). Tell them what
already matches, what you would change, and what the engine cannot do as built. Save only the changes they choose to
`~/.claude/creator-profile/notes/personal-short-form-reels.md`.

## Part 3: questions for this skill

Save these with `python3 setup/apply_profile.py --set-skill key=value`.

### 3a. How you film

| Ask | Key | Default |
|---|---|---|
| "How do you film your personal videos: phone or camera, vertical or horizontal, where?" | `camera_setup` | their words, e.g. "iPhone, vertical, handheld" |
| (only if they film horizontally) "Send me one raw clip from that set-up so I can work out the framing." | `crop_full`, `crop_top` | see below |

A vertical source needs no crops. For a horizontal source, work out two crop windows in source pixels, each written
as `width height x y`: `crop_full` (a 9:16 window with the face centred and the whole head in frame) and `crop_top` (a
9:8 window with the head near the top). Test with `scripts/prep_cams.py "<clip>" /tmp/camtest --full ... --top ...`,
open `cam_full.jpg` and `cam_top.jpg`, show the creator, adjust, then save both.

### 3b. Your B-roll

| Ask | Key | Default |
|---|---|---|
| "Do you have your own B-roll: clips of you working, walking, your desk, your day? Where is it?" | `broll_source` | see below |

- They have footage and the `personal-broll-library` skill is installed and set up: save
  `broll_source` = `personal-broll-library (index at <library path>)`.
- They have footage but no library yet: offer to index it with the `personal-broll-library` skill from this pack
  (recommended: it is analysed once and searched forever). Until then save `broll_source` = `folder: <path>`.
- They have none: save `broll_source` = `none yet`. Reels are built with creator windows and graphics, and each report
  lists a few shots worth filming.

Also ask: "Is there anything in your footage I should never show (people, places, screens)?" and write the answer to
the notes file under `## Style overrides`.

### 3c. How we work together

| Ask (use `AskUserQuestion`) | Key | Default |
|---|---|---|
| "Should I build the whole reel my way and then tell you what I chose, or check the plan with you before I build?" | `working_style` | `build-first` (or `consult`) |
| "Is there anything you never want in your videos? Words, effects, emoji, topics." | notes file, `## Style overrides` | none |

### 3d. The look: confirm the defaults

Describe each default in one line and ask keep or change (`AskUserQuestion`, "Keep it" first, one message each).
Changes go in the notes file under `## Style overrides`.

1. **Captions**: one word at a time, bold, lower-case, white, under your chin, with a key word every couple of seconds
   in your accent colour and emphasis font. Each word stays until the next one.
2. **Pace**: fast. B-roll clips of about a second each, landing exactly on the edit cuts so no jump cut is ever seen.
3. **Horizontal B-roll** stays horizontal with black bars rather than being cropped.
4. **A small graphic** under the caption whenever you are full screen, and real logos when you name a brand.
5. **Music**: a quiet bed under your voice from your favourites, plus quiet sound effects.

## Part 4: finish

1. Read the whole setup back as a short summary. Fix what they correct.
2. `python3 setup/apply_profile.py`. If it prints `STILL TO ASK` or `UNFILLED`, ask exactly those and run it again.
3. Open `SKILL.md` again (it now carries their values) and tell them, in two lines, that setup is done and that they
   can hand over a raw clip and say "personal reel".
4. On the very first reel, check the fonts in the first snapshot and show them the opening frame before rendering.
