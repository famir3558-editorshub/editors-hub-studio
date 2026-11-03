# Setup: split-reel

The first-run interview for this skill (the gate in `SKILL.md` sends you here), and again whenever the creator says
"redo my setup". Read `SHARED-SETUP.md` first ("How to run the interview"): **one question per message**, save each
answer as you go, never guess, never fill in from memory. It takes about five minutes. The goal is that the first
split reel is already theirs.

**If `creator-setup` has been run, the shared answers are already in the profile: read them back in one line and ask
ONLY this skill's own questions** (Part 2), plus the tool check in Part 3. Check first:

```bash
cd ~/.claude/skills/split-reel
python3 setup/apply_profile.py --status
```

and read `~/.claude/creator-profile/profile.json` if it exists. Anything already saved by another skill in the pack
is read back in one line and confirmed, not asked again.

If nothing is saved yet, tell the creator in two or three lines what is about to happen: a short series of questions
about their brand and how they like their split reels made, asked one at a time, which only happens once.

## Extra requirement: Remotion (through npx)

Unlike the rest of the pack, this skill's panels are built as Remotion compositions (React), not HyperFrames. Nothing
needs installing by hand: `scripts/new.sh` creates a small Remotion project from the skill's `kit/` folder at
`<projects_root>/split-reel-kit` the first time it runs and runs `npm install` there; Remotion is then run with `npx`
from that folder. Tell the creator this once, in plain words: "the first reel sets up a small animation project on
your computer, which takes a few minutes and needs an internet connection; after that it is quick." It needs Node 22
or newer and a network connection for the first install (and for the headless browser Remotion downloads the first
time it renders). The final video is assembled with ffmpeg.

## Part 1: the shared questions

This is an editing skill, so run these sections of `SHARED-SETUP.md`, in order. Save shared answers with
`python3 setup/apply_profile.py --set key=value`.

| Section | What it settles | Notes for this skill |
|---|---|---|
| A1 Who you are | `creator_name`, `brand_name`, `handle`, `platform`, `niche` | `niche` steers which examples and diagrams fit. The creator's name is used on the call-to-action panel if they want it there. |
| A2 Brand colours | `accent`, `accent_name`, optional `bg`, `paper`, `grey` | The accent colour is the glow, the keyword colour and the one filled chip. The panels sit on pure black so they blend into the black half of the reel; `bg` is not used here, so do not push the creator towards a custom background. |
| A3 Fonts | `font_main_name`, `font_main_bold`, `font_main_regular`, `font_accent_name`, `font_accent` | Two roles are used: the main font (headlines in CAPS, labels, every figure; the regular weight is for small sub-lines and is the bold if left unset) and the emphasis font (the kicker line and the one or two accent phrases). If they want no second font, save the main bold again as `font_accent`. If they have no preference the emphasis font defaults to the open-licence Playfair Display Italic that ships in `assets/fonts/`. Skip the caption-font row: this style has no caption track. |
| A5 Transcription | `transcriber` | Panels are timed to the words, so accurate word times matter. ElevenLabs is the most accurate; local is free and fine for animation cues (about +-0.1 s). Never ask for the key in chat. |
| A7 Where files live | `output_rule`, `media_drive`, `work_root`, `projects_root` | The reel and its `Animations/` folder are written beside the cut by default. The Remotion project lives under `projects_root`. |
| A9 Your real material | `proof_dir` | Panels show real client screenshots, thumbnails and reel covers wherever they exist. |
| References they love | notes file, `## Style overrides` | Always ask: "Are there two or three split-screen reels whose animations you want yours to feel like?" Compare with "Design language" and "Motion" in `SKILL.md` (kicker and CAPS headline, one diagram per beat, entrances on the spoken word, nothing still for more than 1.5 s). Count how often the picture in the lower half changes per 10 seconds and how long each headline holds. |

Skip A4, A6 (replaced by the tool check in Part 3) and A8: this skill never touches the creator's audio and adds no
sound effects or music.

## Part 2: this skill's questions

Ask each one on its own. Save with `python3 setup/apply_profile.py --set-skill key=value` (quote the pair when the
value has spaces: `--set-skill "work_rule=run to the end, then report"`). If they do not mind, say what the default
is and save the default.

### What may be shown

| Ask | Key | Default |
|---|---|---|
| "Besides your proof folder, are there other folders I should search for real things to show: client work, brand assets, reel covers, screenshots?" (full paths; several are fine, saved as a JSON list) | `asset_dirs` | `none` |
| "When a panel names a company, a person, a website or a video, the reel is strongest with the real thing. May I fetch real logos, photos, screenshots and thumbnails from the web? You decide what you are comfortable publishing: I list every source in my report." (`AskUserQuestion`: yes, list the sources / only my own material and screenshots of public pages / no, only my own material) | `web_assets` | `yes: real over drawn, every source listed in the report` |
| "Is there anything that must never be shown on screen: names, clients, competitors, figures, old offers, topics?" | `never_show` | `nothing listed` |

### How the reel is built

| Ask | Key | Default |
|---|---|---|
| "Sometimes a reel has a moment where it is just you, full screen, no graphics. If you do not tell me which parts, should I pick one to three short, punchy moments (the hook, the promise, a personal line) and tell you which, or add none?" (`AskUserQuestion`) | `fullscreen_rule` = `pick 1 to 3 short moments and tell me which` or `none unless I say` | `pick 1 to 3 short moments and tell me which` |
| "What do you usually ask viewers to do at the end of a reel: comment a keyword, follow, a link in your bio, or something else?" | `cta_default` | `comment a keyword` |
| "Should your name appear, faint, on the final call-to-action panel only?" (yes / no) | `cta_signature` | `yes` |
| "You normally cut the video yourself and I do not re-cut it. If you ever ask me to tighten the silences, what is the shortest pause I should treat as a silence? 0.32 seconds is tight but natural." | `tighten_gap` (a number, in seconds) | `0.32` |

### How we work together

| Ask (use `AskUserQuestion`) | Key | Default |
|---|---|---|
| "Should I render a quick 720p preview and wait for your yes before the final render? It adds one round of review and saves a long re-render." | `preview_first` = `yes: a 720p preview first, the final after approval` or `no: straight to the final` | `yes: a 720p preview first, the final after approval` |
| "Should I run the whole reel to the end and then report (the sections I chose, the full-screen picks, every invented line of mock text), or stop and ask after the section plan and after the preview?" | `work_rule` = `run to the end, then report` or `stop and ask at each stage` | `run to the end, then report` |

Then confirm the rest of the default style in one message (keep / change), and write anything they change under
`## Style overrides` in `~/.claude/creator-profile/notes/split-reel.md`, not in the profile:

1. Headlines are centred, in CAPS, with one or two glowing accent words.
2. One simple diagram per beat, building on the words as they are said.
3. Figures and currency are always in the main font.
4. Full-screen sections are hard cuts, and the panel that follows has something on screen at once.
5. Their audio is used untouched.

## Part 3: tools check (do not ask)

```bash
node -v            # 22 or newer
ffmpeg -version    # any recent build
ffprobe -version
python3 -c "import numpy, soundfile, requests"   # numpy and soundfile are only for tighten.py; requests for ElevenLabs
```

If a Python module is missing: `pip3 install numpy soundfile requests`. Remotion needs nothing installed up front (see
above). The scripts are written for macOS and zsh; `tighten.py` uses Apple's `hevc_videotoolbox` encoder. Say so
plainly if they are on Windows or Linux (everything but `tighten.py` and the zsh scripts' paths needs adapting).

## Part 4: finish

1. Read every answer back as a short summary (shared and this skill's). Fix anything they correct.
2. `python3 setup/apply_profile.py`. It fills every placeholder (including the kit's `src/brand.js`), copies their
   fonts into `assets/fonts/`, and writes `.configured`. It must end with "configured". If it prints `STILL TO ASK` or
   `UNFILLED`, ask for exactly those and run it again.
3. Check the fonts are really there: every file named in the profile is in `assets/fonts/`, and a font saved as
   `local` is installed.
4. Tell them in two lines what is set up and what to try first: "Give me your cut and say 'do the split reel'."
5. On the first reel, show them the framing stills (the two crops drawn on) and the section plan before building the
   panels, whatever their working rule says.

Later changes ("redo my setup", "change my colours", "tighter silences", "my footage is on a new drive"): ask only
the affected questions, save them, and run `python3 setup/apply_profile.py` again. For a reel that is already
scaffolded, run `scripts/new.sh --refresh` so the kit picks up the new brand values. Rules they give while working go
into `~/.claude/creator-profile/notes/split-reel.md` under `## Style overrides`, dated.
