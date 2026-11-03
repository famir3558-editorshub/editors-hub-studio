# Setup: visual-essay-reel

The first-run interview for this skill (the gate in `SKILL.md` sends you here), and again whenever the creator says
"redo my setup". Read `SHARED-SETUP.md` first ("How to run the interview"): **one question per message**, save each
answer as you go, never guess, never fill in from memory. It takes about ten minutes. The goal is that the first reel
is already theirs.

**If `creator-setup` has been run, the shared answers are already in the profile: read them back in one line and ask
ONLY this skill's own questions (Part 2).** Check with `python3 setup/apply_profile.py --status` and read
`~/.claude/creator-profile/profile.json`. Anything the profile already holds is confirmed in one line, not asked again.

Otherwise start by telling the creator, in two or three lines, what is about to happen: a short series of questions
about their brand and how they like these reels made, asked one at a time, which only happens once.

```bash
cd ~/.claude/skills/visual-essay-reel
python3 setup/apply_profile.py --status
```

## Part 1: the shared questions

This is an editing skill, so run these sections of `SHARED-SETUP.md`, in order. Save shared answers with
`python3 setup/apply_profile.py --set key=value`.

| Section | What it settles | Notes for this skill |
|---|---|---|
| A1 Who you are | `creator_name`, `brand_name`, `handle`, `platform`, `niche` | `niche` steers which real examples fit. |
| A2 Brand colours | `accent`, `accent_name` (optional `bg`, `paper`, `grey` are not used by this engine) | **One accent colour is the whole look**: the light, the near-black, the charcoal and the highlights are all derived from it. Show it on a swatch. A clearly saturated colour works best; warn on a very pale or grey one (weak glow). The backdrop is black by design: do not offer a light backdrop. |
| A3 Fonts | `font_main_name`, `font_main_bold`, `font_main_regular`, `font_caption_name`, `font_caption`, `font_accent_name`, `font_accent` | This engine uses four faces: the **caption font** (captions, labels, figures; the main bold is reused if unset), the **main font** bold and regular (small credits and sub-lines), and the **emphasis font** (key words, and the first line of the opening title). If they want no second font for emphasis, save the main bold again as `font_accent` and its name as `font_accent_name`. With no preference, the emphasis font defaults to the Playfair Display Italic that ships in `assets/fonts/`. |
| A4 Your face on screen | (skip) | The engine does not use a profile picture. |
| A5 Transcription | `transcriber` | The tight cut works on word edges, so ElevenLabs gives a cleaner first cut; local is free and works, but the cut then needs a closer listen. Never ask for the key in chat. |
| A6 The tools | (check, do not ask) | Also check `python3 -c "import numpy, soundfile, requests, PIL"` (`pip3 install numpy soundfile requests pillow`; add `fonttools` if any font is saved as `local`, so the font check can see it). The cut-out uses `npx hyperframes remove-background`: run `npx hyperframes doctor` and say plainly if it is unavailable (the build then falls back to a rounded panel). |
| A7 Where files live | `output_rule`, `media_drive`, `work_root`, `projects_root` | The cut, crops and renders are written beside the raw file. |
| A8 Sound | `sfx_dir`, `music_dir`, `music_rule`, `sfx_map.json`, `music.json` | Sound effects are optional and quiet: run `python3 scripts/sfx_probe.py "<folder>" --write` and correct the map with them. Only `woosh` and `pop` are needed. No pack: the reels are delivered without sound effects; say so. For `music_rule`, the default for this skill is `ask`: music is always a separate question, and both versions are delivered. |
| A9 Your real material | `proof_dir` | This style shows real things whenever one is named, so this folder is searched first on every reel. |
| References they love | notes file, `## Style overrides` | Always ask, and ask for **evidence-style** references: "Are there one or two reels where the thing being talked about appears on screen as it is said?" Compare with `references/reference-study.md` and "Defaults of this style" in `SKILL.md`: count how often the wall changes in 10 seconds, where the presenter sits, caption size and position. |

## Part 2: this skill's questions

Ask each one on its own. Save with `python3 setup/apply_profile.py --set-skill key=value` (quote the pair when the
value has spaces: `--set-skill "work_rule=run to the end, then report"`). If they do not mind, say what the default
is and save the default.

### What may be shown

| Ask | Key | Default |
|---|---|---|
| "Besides your proof folder, are there other folders I should search for real things to show: client work, brand assets, B-roll, screenshots?" (full paths; several are fine, saved as a JSON list) | `asset_dirs` | `none` |
| "When you name a person, a company, a post, a study or a website, the edit is strongest when I show the real thing. May I fetch real posts, profiles, articles and screenshots from the web? You decide what you are comfortable publishing: I list every source in my report." (`AskUserQuestion`: yes, list the sources / only my own material and screenshots of public pages / no, only my own material) | `web_assets` | `yes: real over drawn, every source listed in the report` |
| "Is there anything that must never be shown on screen: names, clients, competitors, figures, old offers, topics?" | `never_show` | `nothing listed` |

### The cut

| Ask | Key | Default |
|---|---|---|
| "How much space should I leave between sentences in the tight cut? 0.12 seconds keeps natural pacing; lower is tighter, higher is looser." | `cut_gap` (a number, seconds) | `0.12` |

Their voice is never processed (no loudness change, no noise removal). Say so once.

### The look: confirm the defaults

Describe each in one line and ask keep or change. One message each; `AskUserQuestion` with "Keep it" first. Show a
mock-up still of the frame (black backdrop, the accent light, a cut-out placeholder, the wall box, a caption line) so
they can see what each setting does.

| Ask | Key | Default |
|---|---|---|
| "Where do you sit in the frame? The default puts the top of your head 52% of the way down, so you fill the lower half and the evidence wall sits above you." (pixels from the top of a 1920 px frame) | `head_y` | `1000` |
| "How large is your head in the frame, from the top of the hair to the chin? 320 px is about 17% of the frame height." | `head_px` | `320` |
| "Caption size. 54 px is deliberately small, because the evidence is the loudest thing on screen." | `caption_size` | `54` |
| "The opening title: first line in your emphasis font (the editorial look), or in your main font?" (`AskUserQuestion`) | `title_font` = `emphasis` or `main` | `emphasis` |
| "Where does the accent light come from by default? Bottom is the usual; it can change per chapter of the script." | `glow_default` = `bottom`, `low-left`, `low-right`, `left`, `right`, `behind`, `top` | `bottom` |

Then confirm the rest of the style in one message (keep / change), and write anything they change under
`## Style overrides` in `~/.claude/creator-profile/notes/visual-essay-reel.md`, not in the profile:

1. Evidence keeps its own look and changes on hard cuts, one idea on the wall at a time.
2. Every visual names its reason; a line with nothing to show stays empty and the presenter carries it.
3. Emphasis words about 3 to 6 a minute; figures are never set in the emphasis font.
4. No sound effects or music unless they say so.
5. No watermark.

### How we work together

| Ask (use `AskUserQuestion`) | Key | Default |
|---|---|---|
| "Should I finish the whole reel and then give you a full report (every asset and where it came from, every wording choice), or stop and check with you at each stage: after the cut, after the cut-out check, after the evidence plan, after the draft?" | `work_rule` = `run to the end, then report` or `stop and ask at each stage` | `run to the end, then report` |

Music is already settled by A8 (`music_rule`; for this skill the default is to ask every time and deliver a version
with and without).

## Part 3: finish

1. Read every answer back as a short summary (shared and this skill's). Fix anything they correct.
2. `python3 setup/apply_profile.py`. It fills every placeholder, copies their fonts and sound map into `assets/`, and
   writes `.configured`. It must end with "configured". If it prints `STILL TO ASK` or `UNFILLED`, ask for exactly
   those and run it again.
3. Check the fonts are really there: every file named in the profile is in `assets/fonts/`, and a font saved as
   `local` is installed (Adobe Fonts only render while Creative Cloud is running: tell them).
4. Open `SKILL.md` again (it now carries their values) and tell them in two lines what is set up and what to try
   first: "Give me a raw talking-head video and say 'visual essay reel'."
5. On the very first video, show them the three cut-out stills and the evidence plan before rendering anything, and
   check every font in the first snapshot is the real one.

Later changes ("redo my setup", "change my colours", "I sit too low", "smaller captions"): ask only the affected
questions, save them, and run `python3 setup/apply_profile.py` again. For a video that is already scaffolded, run
`python3 scripts/08_new_project.py <slug> --refresh` afterwards so the project picks the change up (re-run
`06_cutout.py` first if the presenter's position or size changed). Rules they give
while working go into `~/.claude/creator-profile/notes/visual-essay-reel.md` under `## Style overrides`, dated.
