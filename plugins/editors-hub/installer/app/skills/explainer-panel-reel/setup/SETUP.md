# Setup: explainer-panel-reel

The first-run interview for this skill (the gate in `SKILL.md` sends you here), and again whenever the creator says
"redo my setup". Read `SHARED-SETUP.md` first ("How to run the interview"): **one question per message**, save each
answer as you go, never guess, never fill in from memory. It takes about ten minutes. The goal is that the first
panel reel is already theirs.

**If `creator-setup` has been run, the shared answers are already in the profile: read them back in one line and ask
ONLY this skill's own questions (Part 2).** Otherwise run Part 1 first.

Start by telling the creator, in two or three lines, what is about to happen: a short series of questions about their
brand and how they like the panel reels edited, asked one at a time, which only happens once. Then check what is
already answered:

```bash
cd ~/.claude/skills/explainer-panel-reel
python3 setup/apply_profile.py --status
```

and read `~/.claude/creator-profile/profile.json` if it exists. Anything already saved by another skill in the pack
is read back in one line and confirmed, not asked again.

## Part 1: the shared questions

This is an editing skill, so run these sections of `SHARED-SETUP.md`, in order. Save shared answers with
`python3 setup/apply_profile.py --set key=value`.

| Section | What it settles | Notes for this skill |
|---|---|---|
| A1 Who you are | `creator_name`, `brand_name`, `handle`, `platform`, `niche` | The handle is only drawn if they say yes to the watermark question in Part 2. `niche` steers which examples and graphics fit their audience. |
| A2 Brand colours | `accent`, `accent_name`, optional `bg`, `paper`, `grey` | The accent colour is the one colour on the black frame: the active element, the end markers, the glow, the emphasis words and (by default) the block behind line 2 of each heading. The look is built on black: if they ask for a light background, say plainly that it needs restyling. |
| A3 Fonts | `font_main_name`, `font_main_bold`, `font_accent_name`, `font_accent`, `font_caption_name`, `font_caption` | Three roles. Main bold: headings, labels and every figure. Caption font: every caption and heading (leave unset to reuse the main bold). Emphasis font: the few words per minute that change colour, in a contrasting face; if they want no second font, save the main bold again as `font_accent` and set `emphasis_scale` to 1.0 in Part 2. With no preference the emphasis font is the Playfair Display Italic that ships in `assets/fonts/`. Ask whether the caption font is a bold weight: captions are set at weight 700. |
| A4 Your face on screen | `avatar.jpg` in the profile | Optional here: it is only used if a graphic shows their own profile or comment (`s.img`). |
| A5 Transcription | `transcriber` | The cut is made on word edges and checked by transcribing the edit again, so ElevenLabs gives a cleaner cut; local is free and works with a closer check. A short reel costs a few cents either way. Never ask for the key in chat. |
| A6 The tools | (check, do not ask) | Also check `python3 -c "import numpy, soundfile, requests, PIL"` (`pip3 install numpy soundfile requests pillow`; `pip3 install fonttools` as well if any font is saved as `local`, so the font check can see it). The cut-out of the speaker (`npx hyperframes remove-background`) is needed for the head to rise above the panel: it downloads a model the first time. |
| A7 Where files live | `output_rule`, `media_drive`, `work_root`, `projects_root` | Reels are short, but the cut and the cropped camera files are written beside the raw file, so the drive that holds the raw needs free space of roughly three times the raw file. |
| A8 Sound | `music_rule` only | This skill adds no sound effects, so skip the sound-effects questions. If they ever ask for music, the answer to "ask which track, or pick a favourite and tell you" decides how. Default `ask`. |
| A9 Your real material | `proof_dir` | Real screenshots, posts and results are shown wherever the speaker names one. |
| References they love | notes file, `## Style overrides` | Always ask, and ask for **vertical explainer reels**: "Are there two or three reels whose editing you want yours to feel like?" Compare them with "Default style choices" in `SKILL.md` and `references/reference-study.md`: layout (how much is full frame, how big the panel is), caption size and treatment, how often something new arrives above the speaker, heading style. The reference study lists the numbers the engine uses; tell them which of those they would change. |

## Part 2: this skill's questions

Ask each one on its own. Save with `python3 setup/apply_profile.py --set-skill key=value` (quote the pair when the
value has spaces: `--set-skill "work_rule=run to the end, then report"`). If they do not mind, say what the default
is and save the default.

### What may be shown

| Ask | Key | Default |
|---|---|---|
| "Besides your proof folder, are there other folders I should search for real things to show: screenshots, posts, documents, B-roll?" (full paths; several are fine, saved as a JSON list) | `asset_dirs` | `none` |
| "Do you want your handle drawn as a small watermark beside the graphics? It is shown with the Instagram glyph if Instagram is your platform, and as the handle alone otherwise." (`AskUserQuestion`: no / yes) | `watermark` = `no` or `yes` | `no` |

### The look: confirm the defaults

Describe each in one line, show a still where you can (a frame with the panel and caption line drawn on is ideal once
a first video is prepared), and ask keep or change. One message each; `AskUserQuestion` with "Keep it" first.

| Ask | Key | Default |
|---|---|---|
| "The second line of every heading can sit on a solid block of your accent colour, or stay plain with a thin underline in the accent colour. Which do you prefer?" | `heading_block` = `block` or `underline` | `block` |
| "In the panel layout your head and raised hands can rise above the top edge of the panel, which looks layered and a bit more premium. It needs a clean cut-out of you from the video; if the edge is poor on a given video I switch it off for that one. On, or keep everything inside the panel?" | `popout` = `on` or `off` | `on` |
| "Emphasis words are set in your emphasis font. A serif italic looks smaller than a bold sans at the same size, so I set it 12% larger by default. Keep 1.12, or another number? (1.0 if the emphasis font is your main font.)" | `emphasis_scale` (a number) | `1.12` |
| "Close-ups can have a very slow zoom-out so they never sit completely still. Off by default; on?" | `close_up_zoom` = `on` or `off` | `off` |

Then confirm the rest of the default style in one message (keep / change), and write anything they change under
`## Style overrides` in `~/.claude/creator-profile/notes/explainer-panel-reel.md`, not in the profile:

1. Captions are one line of one to three words, on every spoken word, never stacked, with about three to six emphasis
   words a minute.
2. Full frame is about 20 to 30% of the video; every layout switch lands on an edit cut.
3. Graphics build on the word that names them and leave when the speaker moves on; nothing is restated as text.
4. Hard cuts between the two layouts; no bounces, spins, slides across the frame or 3D.
5. Green means positive and red means negative, only when the speaker contrasts good and bad.

### How we work together

| Ask (use `AskUserQuestion`) | Key | Default |
|---|---|---|
| "A reel has several choices (what to cut, which graphics, the wording of headings). Should I show you the plan before building and the draft before the final render, or run it to the end and report every choice afterwards?" | `work_rule` = `show the plan before building and the draft before the final render` or `run to the end, then report` | `show the plan before building and the draft before the final render` |

## Part 3: finish

1. Read every answer back as a short summary (shared and this skill's). Fix anything they correct.
2. `python3 setup/apply_profile.py`. It fills every placeholder, copies their fonts and profile picture into
   `assets/`, and writes `.configured`. It must end with "configured". If it prints `STILL TO ASK` or `UNFILLED`, ask
   for exactly those and run it again.
3. Check the fonts are really there: every file named in the profile is in `assets/fonts/`, and a font saved as
   `local` is installed (Adobe Fonts only render while Creative Cloud is running: tell them).
4. Open `SKILL.md` again (it now carries their values) and tell them in two lines what is set up and what to try
   first: "Give me a raw talking-head video and say 'panel edit'."
5. On the very first video, show the cut script, the framing stills and a draft before rendering the final, whatever
   the working rule says, and check every font in the first snapshot is the real one and not a fallback.

Later changes ("redo my setup", "change my colours", "I want the underline on headings"): ask only the affected
questions, save them, and run `python3 setup/apply_profile.py` again. For a video that is already scaffolded, run
`python3 scripts/08_new_project.py <slug> --refresh` afterwards so the project picks the change up. Rules they give
while working go into `~/.claude/creator-profile/notes/explainer-panel-reel.md` under `## Style overrides`, dated.
