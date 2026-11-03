# Setup: cutout-grid-reel

The first-run interview for this skill (the gate in `SKILL.md` sends you here), and again whenever the creator says
"redo my setup". Read `SHARED-SETUP.md` first ("How to run the interview"): **one question per message**, save each
answer as you go, never guess, never fill in from memory. It takes about five minutes. The goal is that the first
grid reel is already theirs.

**If `creator-setup` has been run, the shared answers are already in the profile.** Read them back in one line
("I have you as Sam Okafor, main font Inter, ElevenLabs for transcription. Still right?") and ask ONLY this skill's own
questions in Part 2. Check first:

```bash
cd ~/.claude/skills/cutout-grid-reel
python3 setup/apply_profile.py --status
```

and read `~/.claude/creator-profile/profile.json` if it exists. Anything already saved by another skill in the pack
is read back in one line and confirmed, not asked again.

If there is no profile yet, start by telling the creator, in two or three lines, what is about to happen: a short
series of questions about their name, fonts and how they like this style, asked one at a time, which only happens once.

## Part 1: the shared questions (skip what the profile already has)

This is an editing skill, but it draws very little brand: the hook label and captions use the creator's font, and a
thin off-white rim goes round the cut-out. Run these sections of `SHARED-SETUP.md`, in order. Save shared answers with
`python3 setup/apply_profile.py --set key=value`.

| Section | What it settles | Notes for this skill |
|---|---|---|
| A1 Who you are | `creator_name`, `brand_name`, `handle`, `platform`, `niche` | `niche` helps pick fitting image ideas for each subject. |
| A2 Brand colours | optional `paper` only | **Skip the accent and background questions**: this style uses neither. Ask only if the creator volunteers a brand off-white; otherwise leave the default. |
| A3 Fonts | `font_main_name`, `font_main_bold`, `font_main_regular`, `font_caption_name`, `font_caption` | The main bold is the hook label. The caption font is what sits on the chest (the main bold when none is set). **Skip the emphasis-font row**: this style has no emphasised words. Captions are drawn by a Python script that loads a font **file**, so find the file on the computer (A3 explains how); a font saved as `local` is matched against installed fonts, and Adobe Fonts only work while Creative Cloud is running. |
| A5 Transcription | `transcriber` | Word timings come from this. ElevenLabs gives tighter caption timing; local is free. Never ask for the key in chat. |
| A6 The tools | (check, do not ask) | `node -v` (22+), `ffmpeg -version`, `npx hyperframes doctor` (the background removal runs through HyperFrames), and `python3 -c "import PIL"` (`pip3 install pillow`; add `fonttools` if a font is saved as `local`). macOS is assumed. |
| A7 Where files live | `output_rule`, `media_drive`, `work_root`, `projects_root` | The matte of a long clip is large: working files go on the footage drive when there is one. |
| A8 Sound | `music_dir`, `music_rule` | Music only. This style plays no sound effects, so skip the sound-effects pack question. Default `music_rule` is `ask`. |
| A9 Your real material | `proof_dir` | The image hunt looks here before the web. |
| References they love | notes file, `## Style overrides` | Always ask: "Are there two or three reels in this collage style whose feel you want?" Compare with "The look" in `SKILL.md`: how often the set changes, cut-out size, caption size and position. Only the changes they pick become rules. |

Skip A4 (profile picture): nothing in this style uses it.

## Part 2: this skill's questions

Ask each one on its own. Save with `python3 setup/apply_profile.py --set-skill key=value` (quote the pair when the
value has spaces). If they do not mind, say what the default is and save the default.

### The look

Show a still example when you can: a grey-silhouette sheet from `grid_reel.py sheet` with no clip makes a fast
visual of the caption position and the cut-out size.

| Ask | Key | Default |
|---|---|---|
| "How wide should you appear in the centre of the frame? 540 px is head to chest at medium size; bigger hides more of each picture." | `cutout_width` (a number, 400 to 720) | `540` |
| "Caption size on your chest: 46 px keeps a four to six word line about as wide as your chest. Bigger or smaller?" | `caption_size` (a number) | `46` |
| "Letter spacing of the captions: slightly tight, -0.045 em, suits a clean sans. A wide or script font wants 0." | `caption_tracking` (a number, em) | `-0.045` |
| "Should the opening carry a text hook, a bold line on a white label across the top two images until the first set change? Always, never, or ask each video?" (`AskUserQuestion`) | `hook_rule` = `ask each time`, `always` or `never` | `ask each time` |

### What may be shown

| Ask | Key | Default |
|---|---|---|
| "May I search the web for the pictures? I filter out stock and print-shop sites and list every source in my report. You decide what you are comfortable publishing. Or use only your own images." (`AskUserQuestion`: yes, list the sources / only my own material) | `web_images` | `yes: web search, every source listed in the report` |
| "Is there anything that must never be shown: people, brands, competitors, topics?" | `never_show` | `nothing listed` |

## Part 3: finish

1. Read every answer back as a short summary (shared and this skill's). Fix anything they correct.
2. `python3 setup/apply_profile.py`. It fills every placeholder and writes `.configured`. It must end with
   "configured". If it prints `STILL TO ASK` or `UNFILLED`, ask for exactly those and run it again.
3. Check the fonts: the main bold and caption font files are in `~/.claude/creator-profile/assets/fonts/` (or installed,
   for `local`). Grid reels are drawn by a script, so a missing font would silently fall back: the script prints a
   `WARNING` on every run when that happens, and then it is fixed before anything ships.
4. Tell them in two lines what is set up and what to try first: "Give me an edited 9:16 clip and say 'cut-out grid
   reel'." Remind them that the first step on any new layout idea is a still mock-up for a yes.

Later changes ("redo my setup", "bigger captions", "no hook", "new font"): ask only the affected questions, save them,
and run `python3 setup/apply_profile.py` again. Rules they give while working go into
`~/.claude/creator-profile/notes/cutout-grid-reel.md` under `## Style overrides`, dated, the moment they say them.
