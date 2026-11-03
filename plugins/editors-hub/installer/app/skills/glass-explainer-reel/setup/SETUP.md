# Setup: glass-explainer-reel

The first-run interview for this skill (the gate in `SKILL.md` sends you here), and again whenever the creator says
"redo my setup". Read `SHARED-SETUP.md` first ("How to run the interview"): **one question per message**, save each
answer as you go, never guess, never fill in from memory. It takes about ten minutes. The goal is that the first
reel is already theirs.

**If `creator-setup` has been run, the shared answers are already in the profile: read them back in one line and ask
ONLY this skill's own questions (Part 2).** Check with `python3 setup/apply_profile.py --status` and by reading
`~/.claude/creator-profile/profile.json`. Only run Part 1 for the shared answers that are missing.

Otherwise, start by telling the creator, in two or three lines, what is about to happen: a short series of questions
about their brand and how they like their reels built, asked one at a time, which only happens once. Then:

```bash
cd ~/.claude/skills/glass-explainer-reel
python3 setup/apply_profile.py --status
```

Anything already saved by another skill in the pack is read back in one line and confirmed, not asked again.

## Part 1: the shared questions

This is an editing skill, so run these sections of `SHARED-SETUP.md`, in order. Save shared answers with
`python3 setup/apply_profile.py --set key=value`.

| Section | What it settles | Notes for this skill |
|---|---|---|
| A1 Who you are | `creator_name`, `brand_name`, `handle`, `platform`, `niche` | `niche` steers which real examples and metaphors fit their audience. `platform` decides whether the watermark carries the Instagram glyph. |
| A2 Brand colours | `accent`, `accent_name`, optional `bg` | The accent colour is the key word in every heading and caption, the chips, the active element and the glow. The frame is dark by design (see A2, step 3). `paper` and `grey` are not used by this engine: skip them. |
| A3 Fonts | `font_main_name`, `font_main_bold`, `font_main_regular`, `font_accent_name`, `font_accent`, `font_caption_name`, `font_caption` | Three roles are used: the **main font** (graphics, labels, numbers), the **emphasis font** (the one key word in a heading or caption; with no preference it defaults to the Playfair Display Italic that ships in `assets/fonts/`; if they want no second font, save the main bold again as `font_accent`) and the **caption font** (also sets the heading type; leave unset to reuse the main bold). The main regular weight is used for small interface text (Google Docs window, notifications); leave it unset to reuse the bold. Ask the caption row of A3: this skill has one. |
| A4 Your face on screen | `avatar.jpg` in the profile | Shown on "me" nodes and as the sender of a notification mock-up. If they skip it, a neutral grey picture is drawn and listed as a mock-up in every report. |
| A5 Transcription | `transcriber` | The tight cut works on word edges, so ElevenLabs gives a cleaner first cut. Local is free and works; say that the cut then needs a closer listen. Never ask for the key in chat. |
| A6 The tools | (check, do not ask) | Also `python3 -c "import numpy, soundfile, requests, PIL"` (`pip3 install numpy soundfile requests pillow`; add `fonttools` if any font is saved as `local`, so the font check can see it). The cut-out uses `npx hyperframes remove-background`. Scripts are written for a Mac. |
| A7 Where files live | `output_rule`, `media_drive`, `work_root`, `projects_root` | Default output: a "<video name> - Edit" folder beside the raw file. |
| A8 Sound | `sfx_dir`, `music_dir`, `music_rule`, `sfx_map.json`, `music.json` | The reel plays quiet effects by role from their own pack: run `python3 scripts/sfx_probe.py "<folder>" --write` and correct the map with them. Roles used: `woosh`, `swish`, `swoosh`, `pop`, `shine`, `shine2`, `accept`, `dtext`, `data`; only `woosh` and `pop` are needed, others fall back. No pack: say the reel is delivered with the voice only until they have one. `music_rule` default: `ask`. |
| A9 Your real material | `proof_dir` | This style shows real people, channels, reel covers and results wherever one exists, so this folder is searched for every reel. Also ask for **reel covers**: if they have 5 to 20 of their own, copy them into `~/.claude/creator-profile/assets/reels/` (they are used in saved-Reel and grid graphics). |
| References they love | notes file, `## Style overrides` | Always ask. Compare with the style in `SKILL.md` and `references/reference-study.md`. Count the layout switches per minute, the full-frame share and how often a graphic changes in a panel stretch. |

## Part 2: this skill's questions

Ask each one on its own. Save with `python3 setup/apply_profile.py --set-skill key=value` (quote the pair when the
value has spaces). If they do not mind, say what the default is and save the default.

### Their files

| Ask | Key | Default |
|---|---|---|
| "Besides your proof folder, are there other folders I should search for real things to show: client work, brand assets, screenshots, reel covers?" (full paths; several are fine, saved as a JSON list) | `asset_dirs` | `none` |
| "When a script names a person, a channel, a post or a page, may I fetch the real picture or screenshot from the web? You decide what you are comfortable publishing: I list every source in my report." (`AskUserQuestion`: yes, list the sources / only my own material and screenshots of public pages / no, only my own material) | `web_assets` | `yes: real over drawn, every source listed in the report` |
| "Is there anything that must never be shown on screen: names, clients, competitors, figures, old offers, topics?" | `never_show` | `nothing listed` |

### The look: confirm the defaults

Describe each in one line and ask keep or change (`AskUserQuestion` with "Keep it" first).

| Ask | Key | Default |
|---|---|---|
| "Do you want your handle on the video as a small watermark that moves between the two layouts, or no watermark?" Skip the follow-up if they say no; if yes, check `handle` and `platform` are saved. | `watermark` = `on` or `off` | `off` |
| "The graphics get a restrained glass finish: translucent cards over a faint moving light. Keep it as it is, soften the light, or turn it off for plain hairline cards?" Show a still from the gallery (`examples/validation/build_gallery.py`) if you can. | `glass_look` = `full`, `soft` or `off` | `full` |
| "Quiet sound effects on the key reveals, when you have a sound pack: on or off?" Skip if there is no pack. | `sound_effects` = `on` or `off` | `on` |

Then confirm the rest of the default style in one message (keep / change), and write anything they change under
`## Style overrides` in `~/.claude/creator-profile/notes/glass-explainer-reel.md`, not in the profile:

1. Two layouts only: full-frame close-ups and the panel layout, joined by hard cuts; full frame is 20 to 30% of the runtime.
2. One short caption line of one to three words, every spoken word, emphasis rare (three to six a minute).
3. One signature visual metaphor per reel, different every reel; show, never repeat the caption as text.
4. Cards are rectangular; no stacked oval pills; only real interfaces keep their own shape.
5. Quiet sound only on key reveals; no music unless they say yes.
6. Green always means positive and red always means negative.

### How we work together

| Ask (use `AskUserQuestion`) | Key | Default |
|---|---|---|
| "When I need a picture or a wording choice, should I find the best asset and write the best wording myself, finish the whole reel and then tell you what to check, or stop and ask you at each stage (after the cut, after the plan, after the draft)?" | `work_rule` = `finish the best version, then report` or `stop and ask at each stage` | `finish the best version, then report` |

Music is already settled by A8 (`music_rule`; the default is to ask every time and deliver a version with and
without).

## Part 3: finish

1. Read every answer back as a short summary (shared and this skill's). Fix anything they correct.
2. `python3 setup/apply_profile.py`. It fills every placeholder, copies their fonts, profile picture, reel covers and
   sound map into `assets/`, and writes `.configured`. It must end with "configured". If it prints `STILL TO ASK` or
   `UNFILLED`, ask for exactly those and run it again.
3. Check the fonts are really there: every file named in the profile is in `assets/fonts/`, and a font saved as
   `local` is installed (Adobe Fonts only render while Creative Cloud is running: tell them).
4. Open `SKILL.md` again (it now carries their values) and tell them in two lines what is set up and what to try
   first: "Give me a raw talking-head video and say 'glass explainer reel'."
5. On the very first reel, show the draft (the `--draft` render) before the final whatever the working rule
   says, and check every font in the first snapshot is the real one.

Later changes ("redo my setup", "change my colours", "turn the watermark on", "I have a new profile picture"): ask only
the affected questions, save them, and run `python3 setup/apply_profile.py` again. For a video that is already
scaffolded, run `python3 scripts/08_new_project.py <slug> --refresh` afterwards so the project picks the change up.
Rules they give while working go into `~/.claude/creator-profile/notes/glass-explainer-reel.md` under
`## Style overrides`, dated.
