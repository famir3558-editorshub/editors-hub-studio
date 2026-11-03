# Setup: image-cluster-reel

The first-run interview for this skill (the gate in `SKILL.md` sends you here), and again whenever the creator says
"redo my setup". Read `SHARED-SETUP.md` first ("How to run the interview"): **one question per message**, save each
answer as you go, never guess, never fill in from memory. It takes about five minutes. The goal is that the first
reel, even the grey-silhouette test, already looks like theirs.

**If `creator-setup` has been run, the shared answers are already in the profile: read them back in one line and ask
ONLY this skill's own questions (Part 2).** Otherwise, start by telling the creator, in two or three lines, what is
about to happen: a short series of questions about their brand and how they like image-cluster reels made, asked one
at a time, which only happens once. Then check what is already answered:

```bash
cd ~/.claude/skills/image-cluster-reel
python3 setup/apply_profile.py --status
```

and read `~/.claude/creator-profile/profile.json` if it exists. Anything already saved by another skill in the pack
is read back in one line and confirmed, not asked again.

## Part 1: the shared questions

This is an editing skill, so run these sections of `SHARED-SETUP.md`, in order. Save shared answers with
`python3 setup/apply_profile.py --set key=value`.

| Section | What it settles | Notes for this skill |
|---|---|---|
| A1 Who you are | `creator_name`, `brand_name`, `handle`, `platform`, `niche` | `niche` steers which metaphors and examples fit their audience. |
| A2 Brand colours | `accent`, `accent_name`, optional `bg`, `paper`, `grey` | This style draws no accent colour (images and white captions only). Ask anyway, quickly, so the one profile is complete for the other skills in the pack. |
| A3 Fonts | `font_main_name`, `font_main_bold`, `font_main_regular`, `font_caption_name`, `font_caption` | The only font this style draws is the **caption font**, tiny and white. Ask the main-font row (a regular or medium cut is used for captions when no caption font is set), then the caption row. Skip the emphasis-font row: nothing here uses it. Show a line in the font at 30 px, since that is the real size. |
| A4 Your face on screen | (skip) | This style has no notification or DM mock-ups. |
| A5 Transcription | `transcriber` | Word timings place every image and caption. ElevenLabs gives the tighter edges; local works but captions may need a nudge. Never ask for the key in chat. |
| A6 The tools | (check, do not ask) | This skill needs `ffmpeg`, `ffprobe`, `curl`, `python3` and **Google Chrome** (or Chromium; the frames are drawn in headless Chrome). It does not use HyperFrames unless `transcriber` is `local`. macOS or Linux paths for Chrome are found automatically; otherwise `CHROME=<path>`. |
| A7 Where files live | `output_rule`, `media_drive`, `work_root`, `projects_root` | Previews are 720p and small; finals are full size, so keep them on the drive with the raw file when the internal disk is tight. |
| A8 Sound | (skip the sound pack) | This skill does not mix sound. Still ask the music question: `music_dir` and `music_rule` (the default is `ask`). |
| A9 Your real material | `proof_dir` | Real screenshots, results or reel covers can be used as images when the idea is theirs. |
| References they love | notes file, `## Style overrides` | Always ask: "Are there two or three reels in this style, or close to it, that you want yours to feel like?" Compare with "The look" in `SKILL.md`: cluster size and count, how often it changes, caption size and position, how literal the images are. |

## Part 2: this skill's questions

Ask each one on its own. Save with `python3 setup/apply_profile.py --set-skill key=value` (quote the pair when the
value has spaces: `--set-skill "image_types=metaphors and diagrams only"`). If they do not mind, say what the default
is and save the default.

### Captions

Show a mock caption in their font at the chosen size on a still of a 1080 x 1920 frame if you can.

| Ask | Key | Default |
|---|---|---|
| "How big should the captions be? 30 px on a 1080-wide frame is the tiny, quiet size this style is built on." | `caption_size` (a number) | `30` |
| "Where should the left edge of the captions sit? I put them beside your chin on the side with the most clear space, so this is only the starting point." | `caption_x` (px from the left) | `92` |
| "How far down should the top of the captions sit? Always above 1250, so the platform's buttons do not cover them." | `caption_y` (px from the top) | `1196` |

### The images

| Ask | Key | Default |
|---|---|---|
| "Which kinds of image do you want above your head: metaphors and surreal art, memes, known experiments and diagrams, quote screenshots of people you mention? Anything you do not want?" (`AskUserQuestion`: the full mix / no memes / their own list) | `image_types` | `a mix of metaphor and surreal art, memes people recognise, known experiments or diagrams, and quote screenshots or the person when one is named` |
| "Where should I look for images: Pinterest in your own logged-in Chrome (needs the Claude in Chrome extension), a web image search, only your own folders, or a mix?" | `image_sources` | `Pinterest through the Claude in Chrome extension when it is connected, otherwise the web image search script, plus the creator's own folders first` |
| "Besides your proof folder, are there folders of your own images I should search first: screenshots, past reels, a saved collection?" (full paths; several are fine, saved as a JSON list) | `image_dirs` | `none` |
| "Is there anything or anyone that must never be shown on screen: people, brands, topics, competitors?" | `never_show` | `nothing listed` |

Say once, and do not raise it again: there is never a watermark on any image, found or added, and picking images that
may be used is the creator's call, not this skill's.

### Framing, said once

Tell them the filming requirement in one line: "This style needs you low in the frame with clear space above your
head, so the images have somewhere to sit. If a clip is framed high, I will show you where the head line falls and you
decide: re-film, accept smaller images higher up, or accept fewer images. I never move your footage on my own."

### How we work together

| Ask (use `AskUserQuestion`) | Key | Default |
|---|---|---|
| "Should I show you a quick 720p preview and wait for your notes before the full-quality render, or go straight to the final?" | `review_rule` | `show a preview and wait for approval before the final render` |

## Part 3: finish

1. Read every answer back as a short summary (shared and this skill's). Fix anything they correct.
2. `python3 setup/apply_profile.py`. It fills every placeholder, copies nothing else (this skill has no `assets/`
   folder: the scripts read the font and caption defaults straight from the profile), and writes `.configured`. It
   must end with "configured". If it prints `STILL TO ASK` or `UNFILLED`, ask for exactly those and run it again.
3. Check the caption font is really there: a file named in the profile is in
   `~/.claude/creator-profile/assets/fonts/`, and a font saved as `local` is installed (Adobe Fonts only render while
   Creative Cloud is running: tell them). Render a one-cluster layout sheet and look at the caption.
4. Open `SKILL.md` again (it now carries their values) and tell them in two lines what is set up and what to try
   first: "Give me a script and I will build a grey-silhouette version to test the images, or give me a clip framed
   low and say 'image cluster reel'."

Later changes ("redo my setup", "smaller captions", "no memes", "new caption font"): ask only the affected questions,
save them, and run `python3 setup/apply_profile.py` again. Rules they give while working go into
`~/.claude/creator-profile/notes/image-cluster-reel.md` under `## Style overrides`, dated, the moment they say them.
