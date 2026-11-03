# First-run setup: Business Short Form Reels

Run this the first time the skill is used (the gate in `SKILL.md` sends you here), and again whenever the creator says
"redo my setup". It takes about ten minutes. The goal is complete clarity on how this creator's reels should be
edited, so the first edit is already theirs.

**Ask one question per message, wait for the answer, save it, then ask the next.** The full rules for running the
interview are at the top of `setup/SHARED-SETUP.md`: read them before the first question.

Start by telling the creator, in two or three lines, what is about to happen: a short series of questions about their
brand and how they like their videos edited, asked one at a time, which only happens once. Then mention the three
things this skill needs on their computer, and check them yourself (section A6): **HyperFrames** (it builds and
renders every reel), **ffmpeg**, and a transcriber: **ElevenLabs** is the best and is what the skill was built on,
or transcription that runs locally on their computer for free.

## Part 1: the shared questions

Work through `setup/SHARED-SETUP.md` sections **A1 to A9**, in order. Skip any answer already in
`~/.claude/creator-profile/profile.json` after reading it back in one line.

Save shared answers with `python3 setup/apply_profile.py --set key=value`.

## Part 2: references

Run the **"References they love"** section of `setup/SHARED-SETUP.md`. Ask it plainly:

> "Do you have two or three reels whose editing you want yours to feel like? Download them and upload them to this
> chat so I can study them properly. Your own best-performing reel counts too."

Analyse each one against this skill's defaults (three modes, one-word captions when full screen, split with the
animation on top, stacked pills, real interfaces, focus-pull entrances, quiet sound). Tell them what already matches,
what you would change, and what the engine cannot do as built. Save only the changes they choose to
`~/.claude/creator-profile/notes/business-short-form-reels.md`.

If they have no references, show them what the default looks like in words (the "style" summary in `SKILL.md`, in
five lines) and move on.

## Part 3: questions for this skill

Save these with `python3 setup/apply_profile.py --set-skill key=value`.

### 3a. How you film

| Ask | Key | Default |
|---|---|---|
| "How do you film your business videos: camera or phone, horizontal or vertical, sitting at a desk or standing?" | `camera_setup` | their words, e.g. "4K horizontal, seated at a desk" |
| "Send me one raw clip from that set-up (a few seconds is enough) so I can work out the framing." | `crop_full`, `crop_top` | see below |

With the sample clip: grab a still (`ffmpeg -ss 2 -i "<clip>" -frames:v 1 still.jpg`), find the face, and work out two
crop windows in source pixels, each written as `width height x y`:

- `crop_full`: a 9:16 window with the face centred horizontally and the whole head in frame (for a 3840x2160 source
  that is 1215 wide by 2160 high; for 1920x1080, 608 by 1080).
- `crop_top`: a 9:8 window (for the bottom half of the split screen) with the head near the top and the chin and chest
  below (3840x2160: about 1800 by 1600; 1920x1080: about 900 by 800).

Test them (`scripts/07_crops.sh "<clip>" /tmp/croptest` with `NO_MATTE=1`), open the stills, show the creator, adjust
until the face is centred and the head is not cut, then save both. A vertical source needs no `crop_full`: say so and
save only `crop_top` as a y offset note in `camera_setup`. If they film in more than one set-up, save the main one and
note the others in the notes file: the crop is checked on every video anyway.

### 3b. How we work together

| Ask (use `AskUserQuestion`) | Key | Default |
|---|---|---|
| "When I edit, do you want me to check design choices with you before I build (which graphic, the opening, the wording), or build the whole reel my way and then tell you what I chose?" | `working_style` | `consult` (or `build-first`) |
| "How do your videos usually end: 'comment a word and I'll send it', 'link in bio', 'follow for more', something else?" | `cta_style` | their words |
| "Is there anything you never want in your videos? Words, effects, colours, emoji, topics." | goes in the notes file under `## Style overrides` | none |

### 3c. The look: confirm the defaults

Describe each default in one line and ask keep or change. One message each; `AskUserQuestion` with "Keep it" first.
Anything they change goes in the notes file under `## Style overrides`, not in the profile.

1. **Captions when you are full screen**: one word at a time under your chin, lower-case, with a few key words in your
   accent colour and emphasis font.
2. **Captions over animations**: two to four words at a time in white.
3. **The opening**: you full screen with a two-line text hook above your head from the first frame, plus an
   attention-grabbing graphic.
4. **Split screen**: the animation on the top half, you on the bottom half.
5. **Graphics**: stacked pills on glass, real Instagram notifications for comments and DMs, real Google Docs and
   Notion windows for anything written, real screenshots and real people wherever they exist.
6. **Sound effects**: quiet, on key moments only.

### 3d. Reel covers (optional)

"One of the opening graphics circles reel covers around you. If you would like to use it, drop 8 to 16 reel cover
screenshots (yours, or creators in your space) into the chat." Save them as
`~/.claude/creator-profile/assets/reels/r01.jpg`, `r02.jpg`, ... If they skip this, that opening is simply not offered.

## Part 4: finish

1. Read the whole setup back as a short summary (name, brand, colour, fonts, transcriber, working style, what changed
   from the defaults). Fix what they correct.
2. `python3 setup/apply_profile.py`. If it prints `STILL TO ASK` or `UNFILLED`, ask exactly those and run it again.
3. Open `SKILL.md` again (it now carries their values) and tell them, in two lines, that setup is done and that they
   can hand over a raw clip and say "do the business reel".
4. On the very first reel, check the fonts in the first snapshot (the real fonts, not a fallback) and show them the
   opening frame before rendering the whole thing.
