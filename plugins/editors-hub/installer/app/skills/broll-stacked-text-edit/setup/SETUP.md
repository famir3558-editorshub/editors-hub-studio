# Setup: broll-stacked-text-edit

The first-run interview for this skill (the gate in `SKILL.md` sends you here), and again whenever the creator says
"redo my setup". Read `SHARED-SETUP.md` first ("How to run the interview"): **one question per message**, save each
answer as you go, never guess, never fill in from memory. It takes a few minutes.

**If `creator-setup` has been run, the shared answers are already in the profile** (`~/.claude/creator-profile/profile.json`):
read them back in one line ("I have you as <name>, accent <colour>, captions in <font>, transcribing with <engine>. Still
right?") and ask ONLY this skill's own questions in Part 2. Run Part 1 only for the shared answers that are missing.

Start by telling the creator, in two or three lines, what is about to happen: a few questions about their brand and
their B-roll footage, asked one at a time, which only happens once. Then check what is already answered:

```bash
cd ~/.claude/skills/broll-stacked-text-edit
python3 setup/apply_profile.py --status
```

and read `~/.claude/creator-profile/profile.json` if it exists.

## Part 1: the shared questions

Run these sections of `SHARED-SETUP.md`, in order, skipping any whose answers are already saved. Save shared answers
with `python3 setup/apply_profile.py --set key=value`.

| Section | What it settles | Notes for this skill |
|---|---|---|
| A1 Who you are | `creator_name`, `brand_name`, `handle`, `platform` | Names are used in the report and in the notes file. |
| A2 Brand colours | `accent`, `accent_name` | Only the accent colour is used: it is the colour of the one key word in a stacked caption (and of figures inside a stack). The captions themselves are white. Skip the background, text and label colours. |
| A3 Fonts | `font_main_name`, `font_main_bold`, `font_main_regular`, `font_caption`, `font_caption_name`, `font_accent`, `font_accent_name` | Three faces are used: the **caption font** (regular captions and the small lines of a stack; the regular or medium weight reads best), the **main bold** (the large line of a stack) and the **emphasis font** (the key word). If they have only one font, save its regular as `font_caption` and its bold as `font_main_bold`; if there is no regular weight, the bold is reused. If they want no second font for the key word, save the main bold again as `font_accent`. With no preference the emphasis font is the Playfair Display Italic shipped in `assets/fonts/`. |
| A5 Transcription | `transcriber` | The cut is verified by transcribing the edited audio a second time, so a long video costs about twice its length. ElevenLabs gives tighter word edges; local is free, and the cut then needs a closer listen (say so). Never ask for the key in chat. |
| A6 The tools | (check, do not ask) | This skill needs `ffmpeg` and `ffprobe`, Google Chrome (text is rendered by headless Chrome; or `CHROME_PATH`), and `python3 -c "import numpy, PIL, soundfile, requests"` (`pip3 install numpy pillow soundfile requests`; add `fonttools` if any font is saved as `local`, so the font check can find it). Node and HyperFrames are only needed for the local transcriber. The render scripts use Apple VideoToolbox encoders: if they are not on a Mac, say plainly that the analysis and the plan will work but the render will not. |
| A7 Where files live | `output_rule`, `media_drive` | The cut, crops and renders are written beside the source file, so the drive that holds the footage needs free space of about twice the source. |
| References they love | notes file, `## Style overrides` | Ask for two or three short vertical videos whose captions and B-roll they want theirs to feel like. Compare with the defaults in `SKILL.md` (sections 5 and 6) and write only the differences, plainly, under `## Style overrides` in `~/.claude/creator-profile/notes/broll-stacked-text-edit.md`. |

Skip A4, A8 and A9: this style uses no profile picture, no sound effects or music, and no proof folder.

## Part 2: this skill's questions

Ask each one on its own. Save with `python3 setup/apply_profile.py --set-skill key=value` (quote the pair when the
value has spaces; a list is JSON: `--set-skill 'broll_dirs=["/path/one","/path/two"]'`). If they do not mind, say what
the default is and save the default.

### Your B-roll

| Ask | Key | Default |
|---|---|---|
| "Where does your B-roll footage live? Give me the folder, or several." (full paths, saved as a JSON list; if `personal-broll-library` is set up, offer its `footage_dir`) | `broll_dirs` | none: required |
| "Is there anything in your footage that must never be used as B-roll: people, places, private screens?" | `never_show` | `nothing listed` |
| "What is the most of the video B-roll may cover, as a percentage? The speaker stays the main picture." | `broll_max_share` (a number) | `35` |

Check the folders exist now (`ls`); if one is on an external drive that is not connected, say so and ask them to plug
it in. Offer to catalogue the footage straight away (`python3 scripts/06_broll.py`, in the background): the first run
takes a long time, and every clip must then be looked at once and given notes (see `SKILL.md` section 4).

### The look: confirm the defaults

Describe each in one line and ask keep or change. One message each; `AskUserQuestion` with "Keep it" first.

| Ask | Key | Default |
|---|---|---|
| "Your talking head is horizontal but the finished video is vertical. Crop it to fill the frame, centred on you, or show the whole picture with black above and below?" (`AskUserQuestion`: fill / fit) | `source_framing` | `fill` |
| "How big should the regular captions be on the 1080 x 1920 frame? 54 px reads well on a phone." | `caption_size` (a number) | `54` |
| "How big should the large line of a stacked caption be? 132 px, shrunk automatically when the phrase is too wide." | `stack_size` (a number) | `132` |
| "How many stacked captions do you want? They are for the idea, the number, the turn, the line to remember." | `stack_density` | `2 to 4 a minute at most, never back to back` |

Show them what a stack looks like in their fonts before they answer the last three: render one throwaway card (the
engine's `07_text.py` preview on the first real video is the proof, but a quick still from the saved fonts and accent
colour is enough here). Check the three fonts are real and not fallbacks.

Then confirm the rest of the default style in one message (keep / change), and write anything they change under
`## Style overrides` in `~/.claude/creator-profile/notes/broll-stacked-text-edit.md`, not in the profile:

1. Hard cuts into and out of B-roll, 1.5 to 4 seconds each, never over the opening sentence, a punchline or a call
   to action.
2. Landscape B-roll is shown whole inside the vertical frame (fit) unless the subject survives a crop.
3. No music, no sound effects and no zooms unless they ask.
4. Captions never sit on the face; stacks are left-aligned blocks that reveal line by line.

### How we work together

| Ask (use `AskUserQuestion`) | Key | Default |
|---|---|---|
| "Should I show you a quick draft and wait for your approval before rendering the full-quality final, or render the final straight away and report?" | `review_rule` = `show the draft and wait for approval before the final render` or `render the final straight away and report` | `show the draft and wait for approval before the final render` |

## Part 3: finish

1. Read every answer back as a short summary (shared and this skill's). Fix anything they correct.
2. `python3 setup/apply_profile.py`. It fills every placeholder, copies their fonts into `assets/fonts/`, and writes
   `.configured`. It must end with "configured". If it prints `STILL TO ASK` or `UNFILLED`, ask for exactly those and
   run it again.
3. Check the fonts are really there: every file named in the profile is in `assets/fonts/`, and a font saved as
   `local` is installed (Adobe Fonts only render while Creative Cloud is running: tell them).
4. Open `SKILL.md` again (it now carries their values) and tell them in two lines what is set up and what to try
   first: "Give me a talking-head video and say 'edit this with my B-roll'."
5. On the very first video, check every font in the first stack preview is the real one, and show them the cut script
   and one caption sheet before rendering the whole thing, whatever the review rule says.

Later changes ("redo my setup", "change my colours", "bigger captions", "my B-roll moved to a new drive"): ask only the
affected questions, save them, and run `python3 setup/apply_profile.py` again. Rules they give while working go into
`~/.claude/creator-profile/notes/broll-stacked-text-edit.md` under `## Style overrides`.
