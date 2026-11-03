# Setup: split-screen-document-plus-animations

The first-run interview for this skill (the gate in `SKILL.md` sends you here), and again whenever the creator says
"redo my setup". Read `SHARED-SETUP.md` first ("How to run the interview"): **one question per message**, save each
answer as you go, never guess, never fill in from memory. It takes about eight minutes. The goal is that the first
lesson edit is already theirs.

If `creator-setup` has been run, the shared answers are already in the profile: read them back in one line
("I have you as <name>, <brand>, accent <colour>, <font>, transcribing with <engine>. Still right?") and ask ONLY this
skill's own questions (Part 2). Otherwise start by telling the creator, in two or three lines, what is about to happen:
a short series of questions about their brand and how they like their lessons edited, asked one at a time, which only
happens once. Then check what is already answered:

```bash
cd ~/.claude/skills/split-screen-document-plus-animations
python3 setup/apply_profile.py --status
```

and read `~/.claude/creator-profile/profile.json` if it exists. Anything already saved by another skill in the pack is
read back in one line and confirmed, not asked again.

Also check the skill this one is built on: `python3 ~/.claude/skills/educational-youtube-editor/setup/apply_profile.py --status`.
If it is not installed, tell the creator to install it from the pack; if it is installed but `"configured": false`,
run its setup after this one (the shared answers are the same, so it only asks its own few questions). This skill's
scripts call its cut, render and review scripts.

## Part 1: the shared questions

This is an editing skill, so run these sections of `SHARED-SETUP.md`, in order. Save shared answers with
`python3 setup/apply_profile.py --set key=value`.

| Section | What it settles | Notes for this skill |
|---|---|---|
| A1 Who you are | `creator_name`, `brand_name`, `handle`, `platform`, `niche` | `niche` steers which interfaces and examples the illustrations use (a coach, an agency, a course creator each need different pictures). |
| A2 Brand colours | `accent`, `accent_name`, optional `bg`, `paper`, `grey` | The accent colour is the glow behind full-screen graphics and the colour of the one focal element. The graphics sit on a dark background by design (see A2, step 3). The document on the left is the creator's own and keeps its own colours. |
| A3 Fonts | `font_main_name`, `font_main_bold`, `font_main_regular`, `font_accent_name`, `font_accent` | The engine uses three faces: the main bold (everything in graphics, every figure), a regular weight of the main font (small labels) and the emphasis font (the one or two accent words in a scene). If they want no second font, save the main bold again as `font_accent`. If they have no preference, the emphasis font defaults to the Playfair Display Italic that ships with the educational-youtube-editor. There is no caption font to ask about: skip that row. |
| A4 Your face on screen | `avatar.jpg` in the profile | Used in the profile-header illustration (`D.ig_card`). Optional: without it the card uses a neutral person icon. |
| A5 Transcription | `transcriber` | The dialogue cut works on word edges, so ElevenLabs gives a cleaner first cut. Local is free and works; say that the cut then needs a closer listen. Never ask for the key in chat. |
| A6 The tools | (check, do not ask) | Also check `swiftc --version` (face tracking uses Apple's Vision framework, macOS only; `xcode-select --install` if missing), `python3 -c "import numpy, soundfile, requests, PIL"` (`pip3 install numpy soundfile requests pillow`) and that the educational-youtube-editor is installed. The split-screen step is built for a **3840x2160 camera file**: ask what resolution they record at and, if it is lower, say plainly that the base step will stop and a 4K camera setting is needed. If they are not on a Mac, the cut and graphics plan work but the base step does not. |
| A7 Where files live | `output_rule`, `media_drive`, `work_root`, `projects_root` | A 4K base video and its chunks are large. Keep them on the drive that holds the raw recording and render one video at a time. |
| A8 Sound | `sfx_dir`, `sfx_map.json` | Step 1 only (the sound-effects pack). The roles this kit uses are `woosh`, `swish`, `pop`, `accept`, `dtext` and `data`; only `woosh` and `pop` are needed. No pack: say that the video will be delivered without sound effects until they have one. **Skip the music questions**: this format is delivered without music by default. If they want music, put it in their notes file under `## Style overrides`. |
| A9 Your real material | `proof_dir` | Channel avatars, plaques, client reviews and screenshots shown in illustrations come from here first. |
| References they love | notes file, `## Style overrides` | Always ask, and ask for **lesson / long-form** references: "Are there two or three YouTube lessons whose editing you want yours to feel like?" Compare with "The rules of this format" in `SKILL.md`. Count how often the layout changes, how much of the time the creator is full screen, and what the graphics are made of (interfaces, objects, or text). |

## Part 2: this skill's questions

Ask each one on its own. Save with `python3 setup/apply_profile.py --set-skill key=value` (quote the pair when the
value has spaces: `--set-skill "recorder=Tella: a camera track and a screen track per recording"`). If they do not
mind, say what the default is and save the default.

### Your recordings

| Ask | Key | Default |
|---|---|---|
| "What do you record your lessons with? Tella (a camera track and a screen track per recording) is the supported default. Anything else works if you can give me a 4K camera file and a screen recording of the same length." | `recorder` | `Tella: a camera track and a screen track per recording` |
| "Where do your raw lesson recordings live? I look there first when you name a video." (a folder, or several) | `raw_dir` | `none: ask each time` |
| "What colour is the page of your document on screen? Say a hex code, or leave it and I read the colour from the recording itself." | `doc_page_color` | `auto` |
| "How short may a full-screen moment be, in seconds? Five is the default; raise it if the switching between the document and you feels busy." | `min_full_seconds` (a number) | `5` |

Explain the format in two lines first, so they know what the questions are for: the video shows their document on the
left and them on the right, goes full screen on them when they look to camera, and the animations appear only in those
full-screen moments.

### What may be shown

| Ask | Key | Default |
|---|---|---|
| "Besides your proof folder, are there other folders I should search for real things to show: client work, brand assets, screenshots?" (full paths; several are fine, saved as a JSON list) | `asset_dirs` | `none` |
| "When you name a company, a person, a channel or a website, the illustration is strongest with the real thing. May I fetch real logos, avatars, screenshots and thumbnails from the web? You decide what you are comfortable publishing: I list every source in my report." (`AskUserQuestion`: yes, list the sources / only my own material and screenshots of public pages / no, only my own material) | `web_assets` | `yes: real over drawn, every source listed in the report` |
| "Is there anything that must never be shown on screen: names, clients, competitors, figures, old offers?" | `never_show` | `nothing listed` |

### Sound and audio

| Ask (use `AskUserQuestion`) | Key | Default |
|---|---|---|
| "Quiet recordings: some microphones come into a screen recorder far too quiet. If yours measures quiet, should I ask you first before raising the voice (recommended), fix it automatically, or never touch the audio?" | `quiet_audio_fix` = `ask`, `auto` or `never` | `ask` |
| "If the voice is raised, to what loudness? The default is gentle: about -19.8 LUFS, natural, nothing else added (no EQ, compressor or filters)." | `voice_target_lufs` (a number) | `-19.8` |
| "A boost brings up mic hiss, so a light de-noise goes with it. 6 dB is light; 0 turns it off." | `voice_denoise_db` (a number) | `6` |
| "Alongside the version with quiet sound effects, should I also deliver a copy with no sound effects at all?" | `no_sfx_copy` = `yes` or `no` | `yes` |

Their voice is otherwise never processed. Say so once.

### The look: confirm the defaults

Describe each in one line and ask keep or change. One message each; `AskUserQuestion` with "Keep it" first.

| Ask | Key | Default |
|---|---|---|
| "When a line really matters, the picture cuts in closer on you for a moment (only while you are full screen). How strong? 112% is clear but gentle." (gentle 108 / standard 112 / strong 118) | `punch_percent` (a number) | `112` |
| "Graphics can use depth: cards separating towards the viewer, a screenshot resting at a slight angle. Keep that, or keep everything flat?" | `depth_3d` = `on` or `off` | `on` |

Then confirm the rest of the format's defaults in one message (keep / change), and write anything they change under
`## Style overrides` in `~/.claude/creator-profile/notes/split-screen-document-plus-animations.md`, not in the profile:

1. Document on the left, creator on the right, full screen when they look to camera.
2. Graphics only in the full-screen moments; the document sections are never touched.
3. Every graphic illustrates (an interface, an object, a real asset); none restates their words as text.
4. 1080p, no music, quiet sound effects.
5. Green always means positive and red always means negative.

### How we work together

| Ask (use `AskUserQuestion`) | Key | Default |
|---|---|---|
| "How far should I go before checking in? Show you the plan for the graphics as a short table and then build to the end and report, or stop and ask after the base, after the cut, after the plan and after the preview?" | `work_rule` = `show the plan as a short table, then run to the end and report` or `stop and ask at each stage` | `show the plan as a short table, then run to the end and report` |

The preview-first rule (a 720p preview approved before the final render) applies whichever they choose.

## Part 3: finish

1. Read every answer back as a short summary (shared and this skill's). Fix anything they correct.
2. `python3 setup/apply_profile.py`. It fills every placeholder and writes `.configured`. It must end with
   "configured". If it prints `STILL TO ASK` or `UNFILLED`, ask for exactly those and run it again.
3. Check the fonts are really there: every file named in the profile is in `~/.claude/creator-profile/assets/fonts/`
   and in the educational-youtube-editor's `assets/fonts/` (run its `apply_profile.py` if it is not), and a font saved
   as `local` is installed (Adobe Fonts only render while Creative Cloud is running: tell them).
4. Open `SKILL.md` again (it now carries their values) and tell them in two lines what is set up and what to try first:
   "Give me a lesson recording (the camera file and the screen file) and say 'edit this lesson, document on the left'."
5. On the very first video, show them a frame of each layout (document and full screen) and the section list before the
   full base render, whatever their working rule says, and check every font in the first snapshot is the real one.

Later changes ("redo my setup", "change my colours", "never fix the audio", "my document page is a different colour"): ask only
the affected questions, save them, and run `python3 setup/apply_profile.py` again. A video that is already scaffolded
picks the change up with `python3 ~/.claude/skills/educational-youtube-editor/scripts/06_new_project.py <slug> --refresh`
followed by `python3 scripts/02_project.py <slug> "<Title>"` (it reinstalls this skill's engine over the project's).
Rules they give while working go into `~/.claude/creator-profile/notes/split-screen-document-plus-animations.md` under
`## Style overrides`, dated.
