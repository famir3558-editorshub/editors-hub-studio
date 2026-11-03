# Setup: cutout-backdrop-reel

The first-run interview for this skill (the gate in `SKILL.md` sends you here), and again whenever the creator says
"redo my setup". Read `SHARED-SETUP.md` first ("How to run the interview"): **one question per message**, save each
answer as you go, never guess, never fill in from memory. It takes about five minutes.

**If `creator-setup` has been run, the shared answers are already in the profile: read them back in one line and ask
ONLY this skill's own questions (Part 2).** Otherwise start by telling the creator, in two or three lines, what is
about to happen: a short series of questions about their brand and how they like these reels built, asked one at a
time, which only happens once. Then check what is already answered:

```bash
cd ~/.claude/skills/cutout-backdrop-reel
python3 setup/apply_profile.py --status
```

and read `~/.claude/creator-profile/profile.json` if it exists. Anything already saved by another skill in the pack
is read back in one line and confirmed, not asked again.

## Part 1: the shared questions

This is an editing skill. Run these sections of `SHARED-SETUP.md`, in order, skipping any that are already answered.
Save shared answers with `python3 setup/apply_profile.py --set key=value`.

| Section | What it settles | Notes for this skill |
|---|---|---|
| A1 Who you are | `creator_name`, `brand_name`, `handle`, `platform`, `niche` | `niche` steers which metaphors and images fit the audience. |
| A2 Brand colours | `accent`, `accent_name` | Steps 1 and 2 only. The accent colour is used only if they choose the accent-colour hook label (Part 2). The cut-out sits on full-screen pictures, so no background colour is needed. |
| A3 Fonts | `font_main_name`, `font_main_bold`, `font_main_regular`, `font_caption_name`, `font_caption` | Main font = the hook and its sub-line (bold) and small text. Caption font = the one-line captions: a condensed or medium weight reads best at this size, so suggest one if they have none. There is no emphasis font in this style: skip that row. The script reads these from the profile at build time; a font saved as `{"file": ...}` must be in `~/.claude/creator-profile/assets/fonts/` and then copied in by `apply_profile.py`. |
| A5 Transcription | `transcriber` | Needed for the word timings every caption is matched to. Never ask for the key in chat. |
| A6 The tools | (check, do not ask) | `ffmpeg`, Node 22 and `npx hyperframes doctor` (background removal runs through HyperFrames), plus `python3 -c "import PIL"` (`pip3 install pillow`; `pip3 install fonttools` too if a font is saved as `local`). If they are not on a Mac, the matte still runs but say plainly that it is untested there. |
| A7 Where files live | `output_rule`, `media_drive`, `work_root` | The matte is a video file at full resolution: keep the work folder on a drive with space for the clip. |
| A8 Sound | `music_dir`, `music_rule` | Items 2 and 3 only (music). There is no sound-effect track in this style, so skip the sound-effects pack question. |
| A9 Your real material | `proof_dir` | Real screenshots and photos make the best backdrops. |
| References they love | notes file, `## Style overrides` | Always ask: "Are there two or three vertical videos in this cut-out style whose feel you want?" Compare how often the backdrop changes, where the cut-out sits, caption size and position, and how the opening collage and hook look, with "The look" in `SKILL.md`. |

## Part 2: this skill's questions

Ask each one on its own. Save with `python3 setup/apply_profile.py --set-skill key=value` (quote the pair when the
value has spaces: `--set-skill "review_rule=preview first, wait for approval"`). If they do not mind, say what the
default is and save the default.

### The look

Show a line set in their caption font on a dark picture if you can.

| Ask (use `AskUserQuestion` where it is a choice) | Key | Default |
|---|---|---|
| "Should the hook sit on a white label with dark text, or on a label in your accent colour?" | `hook_label` = `white` or `accent` | `white` |
| "How big should the captions be? The default suits a one-line caption of 3 to 6 words." (a pixel size on the 1080 x 1920 frame) | `caption_size` | `58` |
| "Where should the captions sit? They stay in exactly one spot in the middle of the frame, never moving." (a y position on the 1920-pixel-high frame; the default is just above centre) | `caption_y` | `885` |
| "Should the cut-out get a thin light edge, so dark clothes or hair do not vanish on dark pictures? 0.5 is subtle, 0 is off." | `rim` | `0.5` |

### The pictures

| Ask | Key | Default |
|---|---|---|
| "Do you have your own folders of images (screenshots, photos, a swipe file) I should use first for the backdrops?" (full paths; several are fine, saved as a JSON list) | `image_dirs` | `none` |
| "If your own folders do not have the picture, may I search the web for images? You decide what you are comfortable publishing. I never use anything with a watermark." (`AskUserQuestion`: yes / only my own folders) | `web_images` | `yes: search the web, never anything with a watermark` |
| "Is there anything that must never appear in a backdrop: people, brands, competitors, topics?" | `never_show` | `nothing listed` |

### How we work together

| Ask (use `AskUserQuestion`) | Key | Default |
|---|---|---|
| "Should I show you a quick preview and wait for your yes before the final render, or go straight to the final?" | `review_rule` = `preview first, wait for approval` or `render the final straight away` | `preview first, wait for approval` |

Then confirm the rest of the default style in one message (keep / change), and write anything they change under
`## Style overrides` in `~/.claude/creator-profile/notes/cutout-backdrop-reel.md`, not in the profile:

1. The speaker is large over a collage with the hook for the first 4 seconds, then small and jumping corner to corner.
2. A new backdrop every 1.5 to 3 seconds, hard cuts, with one slow 5% push-in on each.
3. Captions are 3 to 6 words on one line and never move.
4. If something behind them will not cut out cleanly (a chair), it stays in on every frame: nothing is chased out
   with a second mask.
5. Stills only for backdrops.

## Part 3: finish

1. Read every answer back as a short summary (shared and this skill's). Fix anything they correct.
2. `python3 setup/apply_profile.py`. It fills every placeholder, copies their fonts and profile picture into
   `assets/`, and writes `.configured`. It must end with "configured". If it prints `STILL TO ASK` or `UNFILLED`, ask
   for exactly those and run it again.
3. Check the fonts: the first build prints one `FONT:` line each for the hook, the sub-line and the caption. Each must
   name the real font, not a `NOT FOUND` fallback (an Adobe Font only renders while Creative Cloud is running: tell
   them).
4. Open `SKILL.md` again (it now carries their values) and tell them in two lines what is set up and what to try
   first: "Give me an edited vertical clip and say 'cut-out reel'", or a script for a grey-silhouette test.

Later changes ("redo my setup", "change my colours", "bigger captions", "I have a new font"): ask only the affected
questions, save them, and run `python3 setup/apply_profile.py` again. Rules they give while working go into
`~/.claude/creator-profile/notes/cutout-backdrop-reel.md` under `## Style overrides`, dated.
