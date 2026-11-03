# Setup: educational-youtube-editor

The first-run interview for this skill (the gate in `SKILL.md` sends you here), and again whenever the creator says
"redo my setup". Read `SHARED-SETUP.md` first ("How to run the interview"): **one question per message**, save each
answer as you go, never guess, never fill in from memory. It takes about ten minutes. The goal is that the first
long-form edit is already theirs.

Start by telling the creator, in two or three lines, what is about to happen: a short series of questions about their
brand and how they like their long videos edited, asked one at a time, which only happens once. Then check what is
already answered:

```bash
cd ~/.claude/skills/educational-youtube-editor
python3 setup/apply_profile.py --status
```

and read `~/.claude/creator-profile/profile.json` if it exists. Anything already saved by another skill in the pack
is read back in one line and confirmed, not asked again.

## Part 1: the shared questions

This is an editing skill, so run these sections of `SHARED-SETUP.md`, in order. Save shared answers with
`python3 setup/apply_profile.py --set key=value`.

| Section | What it settles | Notes for this skill |
|---|---|---|
| A1 Who you are | `creator_name`, `brand_name`, `handle`, `platform`, `niche` | `niche` matters here: it steers which real examples and metaphors fit their audience. |
| A2 Brand colours | `accent`, `accent_name`, optional `bg`, `paper`, `grey` | The accent colour is the glow behind every split and full-screen graphic and the colour of the one focal element. The background is dark by design (see A2, step 3). |
| A3 Fonts | `font_main_name`, `font_main_bold`, `font_main_regular`, `font_accent_name`, `font_accent` | This engine uses three faces: the main bold (everything in graphics, and every figure), a regular or medium weight of the main font (small labels and sub-lines; the bold is reused if it is left unset) and the emphasis font (the one or two accent words in a scene). If they want no second font for emphasis, save the main bold again as `font_accent` and its name as `font_accent_name`. If they have no preference, the emphasis font defaults to the Playfair Display Italic that ships in `assets/fonts/`. There is no caption font to ask about: skip that row of A3. |
| A4 Your face on screen | `avatar.jpg` in the profile | Used when a graphic shows their own channel, post or comment. Optional here: if they skip it, those graphics use a neutral profile icon. |
| A5 Transcription | `transcriber` | The dialogue edit cuts on word edges, so ElevenLabs gives a cleaner first cut. Local is free and works; say that the cut then needs a closer listen. A long video costs little either way (about $0.22 per hour with ElevenLabs, and the cut is transcribed twice to verify it). Never ask for the key in chat. |
| A6 The tools | (check, do not ask) | Also check `swiftc --version` (face finding uses Apple's Vision framework, macOS only; `xcode-select --install` if it is missing), `python3 -c "import numpy, soundfile, requests, PIL"` (`pip3 install numpy soundfile requests pillow`; `pip3 install fonttools` as well if any font is saved as `local`, so the font check can see it) and that Google Chrome is installed (website screenshots use it; without it, pages are captured in the browser tool instead). If they are not on a Mac, say plainly that the analysis and the edit plan will work but the cut and the build will not. |
| A7 Where files live | `output_rule`, `media_drive`, `work_root`, `projects_root` | Long-form files are large. The cut, the working copy and the rendered parts are written beside the raw file, so the drive that holds the raw needs free space of roughly twice the raw file. |
| A8 Sound | `sfx_dir`, `music_dir`, `music_rule`, `sfx_map.json`, `music.json` | The edit plays quiet sound effects by role from their own pack: run `python3 scripts/sfx_probe.py "<folder>" --write` and correct the map with them. The roles this kit uses are `woosh`, `swish`, `swoosh`, `pop`, `shine`, `accept`, `dtext` and `data`; only `woosh` and `pop` are needed. No pack: say that the video will be delivered without sound effects until they have one. For `music_rule`, the default for this skill is `ask`. |
| A9 Your real material | `proof_dir` | This skill shows real things whenever one is named, so this folder is searched on every video. |
| References they love | notes file, `## Style overrides` | Always ask, and ask for **long-form** references: "Are there two or three YouTube videos whose editing you want yours to feel like?" Compare with "The default style" in `SKILL.md`, `references/decision-engine.md` and `references/motion-sound-design.md`. Count how often something changes on screen in the first 30 seconds and in a typical later minute, and how much of the time the speaker is visible: those three numbers are what the engine's audit measures. |

## Part 2: this skill's questions

Ask each one on its own. Save with `python3 setup/apply_profile.py --set-skill key=value` (quote the pair when the
value has spaces: `--set-skill "work_rule=run to the end, then report"`). If they do not mind, say what the default
is and save the default.

### Your files

| Ask | Key | Default |
|---|---|---|
| "Where do your raw long-form recordings live? I look there first when you name a video." (a folder, or several) | `raw_dir` | `none: ask each time` |
| "Besides your proof folder, are there other folders I should search for real things to show: client work, brand assets, B-roll, screenshots?" (full paths; several are fine, saved as a JSON list) | `asset_dirs` | `none` |

### Your logo

"Do you have a logo file I can use? Drop it into the chat." Then: "And a wide wordmark, your name or brand written
out, that works on a dark background? It is optional."

- Save what they give as `~/.claude/creator-profile/assets/logo.png` (square mark) and
  `~/.claude/creator-profile/assets/wordmark.png` (wide, light, transparent background if they have it). Convert other
  formats with `sips -s format png "<file>" --out "<target>"`; an SVG can be opened and exported in the browser. Look
  at the result with Read: a dark logo on a transparent background disappears on the dark backdrop, so ask for the
  light version if that is what they sent.
- Then save `logo=logo.png` and, if given, `wordmark=wordmark.png`. If they have no logo, save nothing: the default is
  `none`, and the engine works without one (their brand name is set in the main font where a mark is wanted).
- The files are picked up from the profile folder by every new project. Nothing else needs copying.

| Ask (use `AskUserQuestion`) | Key | Default |
|---|---|---|
| "Should your logo sit in the corner for the whole video as a watermark, or only appear where a graphic calls for it, like your channel card or the end of the video?" | `logo_use` = `only where a graphic calls for it, never a constant watermark`, `small corner watermark throughout`, or what they describe | `only where a graphic calls for it, never a constant watermark` |

Skip this question if they have no logo.

### What may be shown

| Ask | Key | Default |
|---|---|---|
| "When you name a company, a person, a website or a video, the edit is strongest when I show the real thing. May I fetch real logos, photos, screenshots and thumbnails from the web? You decide what you are comfortable publishing: I list every source in my report." (`AskUserQuestion`: yes, list the sources / only my own material and screenshots of public pages / no, only my own material) | `web_assets` | `yes: real over drawn, every source listed in the report` |
| "Is there anything that must never be shown on screen: names, clients, competitors, figures, old offers, topics?" | `never_show` | `nothing listed` |

### The dialogue edit

Explain it in one line first: the raw video is tightened before any graphics go on, and it should still sound like them.

| Ask | Key | Default |
|---|---|---|
| "How tight do you like your pauses? The default leaves you sounding natural: any pause longer than half a second is shortened to a quarter of a second, never removed." (`AskUserQuestion`: natural, 0.5 to 0.25 / looser, 0.7 to 0.35 / tighter, 0.35 to 0.15 / their own numbers) | `pause_over` and `pause_to` (two numbers, in seconds) | `0.5` and `0.25` |
| "Breaths between sentences: keep them, which sounds natural, or cut them, which is tighter?" | `breaths` = `keep` or `cut` | `keep` |

Their voice is never processed (no loudness change, no noise removal). Say so once; if they clean up their own audio
in another tool, tell them the cut-only audio is saved for that.

### The look: confirm the defaults

Describe each in one line and ask keep or change. One message each; `AskUserQuestion` with "Keep it" first.

| Ask | Key | Default |
|---|---|---|
| "When a line really matters, the picture cuts in closer on your face for a moment. How strong should that be? 112% is clear but gentle." (gentle 108 / standard 112 / strong 118) | `punch_percent` (a number) | `112` |
| "Graphics can use depth: cards separating towards the viewer, a screenshot resting at a slight angle. Keep that, or keep everything flat?" | `depth_3d` = `on` or `off` | `on` |
| "Captions: this style does not put subtitles on the picture. Do you want none at all, or a caption file you can upload to YouTube so viewers can switch captions on?" | `captions` = `none` or `srt` | `none` |
| "Master resolution: 1080p, or 4K? 4K only pays if you film in 4K, and renders take several times longer." | `master_resolution` = `1080p` or `4k` | `1080p` |

If they ask for captions burned into the picture: say plainly that this engine does not have a caption track, offer
the caption file, and write the request under `## Style overrides` in their notes file so it is not lost.

Then confirm the rest of the default style in one message (keep / change), and write anything they change under
`## Style overrides` in `~/.claude/creator-profile/notes/educational-youtube-editor.md`, not in the profile:

1. Their face stays on screen about 70% of the time or more.
2. A split screen is a clean half-and-half division: they are never put in a card or a rounded box.
3. The opening changes within the first 3 seconds and keeps developing every 2 to 5 seconds for the first 30, then
   settles.
4. A very slow camera drift on long stretches of them talking.
5. Sound effects are quiet and only on key moments.
6. Green always means positive and red always means negative.

### How we work together

| Ask (use `AskUserQuestion`) | Key | Default |
|---|---|---|
| "A long edit has many small choices. Should I run the whole thing to the end and then give you a full report (every asset and where it came from, every wording choice), or stop and check with you at each stage: after the cut, after the plan, and after the draft?" | `work_rule` = `run to the end, then report` or `stop and ask at each stage` | `run to the end, then report` |

Music is already settled by A8 (`music_rule`; for this skill the default is to ask every time and deliver a version
with and without).

## Part 3: finish

1. Read every answer back as a short summary (shared and this skill's). Fix anything they correct.
2. `python3 setup/apply_profile.py`. It fills every placeholder, copies their fonts, profile picture and sound map
   into `assets/`, and writes `.configured`. It must end with "configured". If it prints `STILL TO ASK` or
   `UNFILLED`, ask for exactly those and run it again.
3. Check the fonts are really there: every file named in the profile is in `assets/fonts/`, and a font saved as
   `local` is installed (Adobe Fonts only render while Creative Cloud is running: tell them).
4. Open `SKILL.md` again (it now carries their values) and tell them in two lines what is set up and what to try
   first: "Give me a raw long-form video and say 'edit this YouTube video'."
5. On the very first video, show them the cut script and the opening 45 seconds as a draft before rendering the whole
   thing, whatever their working rule says, and check every font in the first snapshot is the real one.

Later changes ("redo my setup", "change my colours", "tighter pauses", "my raws are on a new drive"): ask only the
affected questions, save them, and run `python3 setup/apply_profile.py` again. For a video that is already scaffolded,
run `python3 scripts/06_new_project.py <slug> --refresh` afterwards so the project picks the change up. Rules they
give while working go into `~/.claude/creator-profile/notes/educational-youtube-editor.md` under `## Style overrides`,
dated.
