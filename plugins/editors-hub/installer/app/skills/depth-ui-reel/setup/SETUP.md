# Setup: depth-ui-reel

The first-run interview for this skill (the gate in `SKILL.md` sends you here), and again whenever the creator says
"redo my setup". Read `SHARED-SETUP.md` first ("How to run the interview"): **one question per message**, save each
answer as you go, never guess, never fill in from memory. It takes about ten minutes. The goal is that the first reel
is already theirs.

**If `creator-setup` has been run, the shared answers are already in the profile: read them back in one line and ask
ONLY this skill's own questions (Part 2).** Check:

```bash
cd ~/.claude/skills/depth-ui-reel
python3 setup/apply_profile.py --status
```

and read `~/.claude/creator-profile/profile.json` if it exists. Anything already saved by another skill in the pack is
read back in one line and confirmed, not asked again.

If nothing is saved yet, start by telling the creator, in two or three lines, what is about to happen: a short series of
questions about their brand and how they like their reels to look, asked one at a time, which only happens once. Then
mention what this skill needs on their computer (section A6 checks it): **HyperFrames**, **ffmpeg**, and a
transcriber. This style also builds on the **business-short-form-reels** skill for the cut, the crop and the cut-out:
check it is installed (`ls ~/.claude/skills/business-short-form-reels`). If it is not, the cut-out can still be made
with `npx hyperframes remove-background`, and a tight 9:16 cut from any source works; say so.

## Part 1: the shared questions

This is an editing skill, so run these sections of `SHARED-SETUP.md`, in order. Skip any answer already in the profile
after reading it back. Save shared answers with `python3 setup/apply_profile.py --set key=value`.

| Section | What it settles | Notes for this skill |
|---|---|---|
| A1 Who you are | `creator_name`, `brand_name`, `handle`, `platform`, `niche` | The brand name and handle appear on the channel card by default. `niche` steers which interfaces and examples fit. |
| A2 Brand colours | `accent`, `accent_name`, optional `bg`, `paper`, `grey` | The accent colour is the glow of the ring, the lit person icon, the awning stripes and the emphasis words: the one focal colour. The reel sits on the creator's own footage, so the background colour only shows in the dim. Positive green and negative red stay as they are. |
| A3 Fonts | `font_main_name`, `font_main_bold`, `font_main_regular`, `font_accent_name`, `font_accent`, `font_caption_name`, `font_caption` | Three roles. Main bold: every figure and label inside the graphics. Main regular (or medium): small labels, tab rows (the bold is reused if it is left unset). Caption font: the small 1-3 word captions, ideally a semibold sans (the main bold is reused if unset). Emphasis font: the one or two key words per reel, large (the shipped Playfair Display Italic if they have no preference). Numbers never go in the emphasis font. |
| A4 Your face on screen | `avatar.jpg` in the profile | Used on every channel card the reel shows for their own channel. If they skip it the card shows a letter tile and the engine lists it as a placeholder. |
| A5 Transcription | `transcriber` | Used by the cut (business-short-form-reels step 1). Never ask for the key in chat. |
| A6 The tools | (check, do not ask) | Also check Node 22 and `npx hyperframes remove-background --help` (the cut-out needs it; the first run downloads a model). |
| A7 Where files live | `output_rule`, `media_drive`, `work_root`, `projects_root` | Projects hold symlinks to the media: keep them on the internal drive. |
| A8 Sound | `sfx_dir`, `music_dir`, `music_rule`, `sfx_map.json`, `music.json` | Optional here. Sound effects are sparse and only on real animations; no pack means no effects. |
| A9 Your real material | `proof_dir` | This style shows real thumbnails, channel cards and reel covers, so this folder is searched on every reel. |
| References they love | notes file, `## Style overrides` | Always ask. Compare with "The look" in `SKILL.md`: how often something new lands (default every 1-2 s), how much of the frame the graphics take, caption size and position, how hard the camera punches. |

## Part 2: this skill's questions

Ask each on its own. Save with `python3 setup/apply_profile.py --set-skill key=value` (quote the pair when the value has
spaces). If they do not mind, say what the default is and save the default.

### How we work together

| Ask (use `AskUserQuestion`) | Key | Default |
|---|---|---|
| "Should I check design choices with you before I build (which interface goes on which sentence, the wording, the opening), or build the whole reel my way and tell you what I chose, what I invented and what I could not find?" | `working_style` = `consult` or `build-first` | `build-first` |

Music is already settled by A8 (`music_rule`). Say once: the reel is always previewed first and only rendered at full
quality after they approve.

### What may be shown

| Ask | Key | Default |
|---|---|---|
| "When you name a platform, an account or a document, the reel is strongest with the real thing. May I fetch real thumbnails, avatars, logos and screenshots from the web? You decide what you are comfortable publishing: I list every source in my report." (`AskUserQuestion`: yes, list the sources / only my own material and public pages / no, only my own material) | `web_assets` | `yes: real over drawn, every source listed in the report` |
| "Is there anything that must never be shown on screen: names, clients, competitors, figures, old offers, topics?" | `never_show` | `nothing listed` |

### The look: confirm the defaults

Describe each in one line and show it where you can (a still from their own footage with the caption laid on it is
worth more than a description). One message each; `AskUserQuestion` with "Keep it" first. Save only what they change.

| Ask | Key | Default |
|---|---|---|
| "Behind the graphics the background is dimmed a little so dark panels read against your room. 0.4 is standard; 0.6 is heavy; 0 is none." | `dim_level` | `0.40` |
| "On each sentence cut the picture punches in. 1.06 is gentle, 1.10 standard, 1.14 strong." | `punch_max` | `1.10` |
| "Captions are one to three words on your chest, 64 px. Bigger or smaller?" (check against a still: the text must stay clear of the chin and above y 1250) | `caption_size` | `64` |
| "How low should they sit?" (top edge in pixels from the top; between 1100 and 1250) | `caption_y` | `1146` |
| "The one or two emphasis words per sentence are set large in the emphasis font. 132 px is standard." | `emph_size` | `132` |

### Where the head sits (measure, do not ask)

Graphics behind the head only work if the head is where the numbers say. After the first cut exists, grab a still of
`cam_full.mp4` (`ffmpeg -ss 3 -i cam_full.mp4 -frames:v 1 still.jpg`), look at it with Read, and find the box that
covers the head and shoulders at scale 1 in the 1080 x 1920 frame. Save it as `head_box` (`x0 y0 x1 y1`, default
`320 320 840 1120`) and, if it differs a lot, say so: behind panels, people icons and front cards are then placed
against this box rather than the defaults written in `SKILL.md`.

Then confirm the rest of the default style in one message (keep / change), and write anything they change under
`## Style overrides` in `~/.claude/creator-profile/notes/depth-ui-reel.md`, not in the profile:

1. They are full frame from the first frame to the last: no split screen, no full-screen animation, no B-roll.
2. Real interfaces float behind the head; simple glowing icons and counters sit round them.
3. No head sticker and no cursor, ever.
4. Captions of one to three words on the chest, emphasis words in the accent colour and emphasis font, never numbers.
5. Green always means positive and red always means negative.

## Part 3: finish

1. Read every answer back as a short summary (shared and this skill's). Fix anything they correct.
2. `python3 setup/apply_profile.py`. It fills every placeholder, copies their fonts, profile picture and sound map into
   `assets/`, and writes `.configured`. It must end with "configured". If it prints `STILL TO ASK` or `UNFILLED`, ask
   for exactly those and run it again.
3. Check the fonts are really there: every file named in the profile is in `assets/fonts/`, and a font saved as `local`
   is installed (Adobe Fonts only render while Creative Cloud is running: tell them).
4. Open `SKILL.md` again (it now carries their values) and tell them in two lines what is set up and what to try first:
   "Give me a raw talking-head clip and say 'do the depth UI reel'."
5. On the very first reel, show a still with the first caption and graphic laid on their own footage before building the
   whole thing, and check every font in the first snapshot is the real one.

Later changes ("redo my setup", "change my colours", "bigger captions", "softer punch-in"): ask only the affected
questions, save them, and run `python3 setup/apply_profile.py` again. A project that is already scaffolded keeps its
own copy of the engine: copy the refreshed `engine/depth_engine.py` into it. Rules they give while working go into
`~/.claude/creator-profile/notes/depth-ui-reel.md` under `## Style overrides`, dated.
