# Setup: youtube-clips

The first-run interview for this skill. Read `SHARED-SETUP.md` first ("How to run the interview"): **one question
per message**, save each answer as you go, never guess, never fill in from memory. Start by checking what is already
answered:

```bash
cd ~/.claude/skills/youtube-clips
python3 setup/apply_profile.py --status
```

and read `~/.claude/creator-profile/profile.json` if it exists. Anything already saved by another skill in the pack
is read back in one line and confirmed, not asked again.

## Part 1: the shared questions

This is an editing skill, so run these sections of `SHARED-SETUP.md`, in order:

| Section | What it settles | Notes for this skill |
|---|---|---|
| A1 Who you are | `creator_name`, `brand_name`, `handle`, `platform`, `niche` | |
| A2 Brand colours | `accent`, `accent_name`, optional `bg`, `paper`, `grey` | |
| A3 Fonts | `font_main_name`, `font_main_bold`, `font_main_regular`, `font_accent_name`, `font_accent`, optional `font_caption_name`, `font_caption` | The engine uses the main bold (hooks, figures), a regular or medium weight of the main font (small labels: the bold is reused if it is left unset) and the emphasis font (caption key words). If they want no second font for emphasis, save the main bold again as `font_accent` and its name as `font_accent_name`. If they have no preference at all, the emphasis font defaults to the Playfair Display Italic that ships in `assets/fonts/`. This skill does not use the handwritten Caveat font and does not ship it. |
| A4 Your face on screen | `avatar.jpg` in the profile | Used in notification and profile mock-ups. |
| A5 Transcription | `transcriber` | A solo video does not need speaker labels, so local transcription costs little here; say that ElevenLabs is still the more accurate of the two and labels guests. Never ask for the key in chat. |
| A6 The tools | (check, do not ask) | Also check `yt-dlp --version` (`brew install yt-dlp`; only needed for links), `swiftc --version` (face finding uses Apple's Vision framework, macOS only; `xcode-select --install` if it is missing) and `python3 -c "import numpy, soundfile, requests, PIL"` (`pip3 install numpy soundfile requests pillow`). If they are not on a Mac, say plainly that the clip list and prompts will work but the build half will not. |
| A7 Where files live | `output_rule`, `media_drive`, `work_root`, `projects_root` | Clips always sit beside the video in a "- Clips" folder; where the finished files go is asked below. |
| A8 Sound | `sfx_dir`, `music_dir`, `music_rule`, `sfx_map.json`, `music.json` | These clips default to no music and no effects. Ask A8 anyway so the profile is complete; if they have no sound pack, say that is fine for this skill. |
| A9 Your real material | `proof_dir` | |
| References they love | notes file, `## Style overrides` | Always ask. Compare with `references/style.md` and `references/layouts.md`. |

## Part 2: this skill's questions

Ask each one on its own. Save with `python3 setup/apply_profile.py --set-skill key=value` (quote the pair when the
value has spaces: `--set-skill "finals_dir=beside the video"`). If they do not mind, say what the default is and
save the default.

### Your channel and your files

| Ask | Key | Default |
|---|---|---|
| "What is your YouTube channel called, and what is its link?" (so I can tell your videos from other people's) | `channel` (name and link in one value) | none: must be answered |
| "Where do the raw recordings and clean cuts of your videos live: the versions with no captions, graphics or music added? I look there before downloading anything, because a clean picture makes much better clips." (a folder, or several) | `raw_dir` | `none: ask each time` |
| "Do your published videos have captions or music burned into them?" (`AskUserQuestion`: captions / music / both / neither / it varies) | `published_look` | `check each video` |

Do not ask where downloads go unless A7 showed their disk is short of space or their footage lives on an external
drive; then offer a "YouTube Downloads" folder on that drive. Otherwise save the default.

| (ask only if needed) | Key | Default |
|---|---|---|
| "When I download a video from a link, where should I keep it?" | `downloads_dir` (a full path) | `~/Movies/YouTube Downloads` |

### What can be clipped

| Ask | Key | Default |
|---|---|---|
| "Do you ever want clips from other people's videos, or only your own? By default I stop and ask you each time before going past the clip list on a video that is not yours." | `other_creators` = `ask each time`, `never` or their own rule | `ask each time` |
| "Is there anything that must never be clipped: topics, names, sponsors, old offers?" | `never_clip` | `nothing listed` |
| "If there is swearing, it stays in the audio. In the captions, do you want it starred (f\*\*\*) or written as spoken?" | `swear_captions` = `starred` or `as spoken` | `starred` |

### How much, and how far I go on my own

| Ask | Key | Default |
|---|---|---|
| "How many clips at most from one video? I keep every clip that is good enough to post, with no minimum, up to this number." | `max_clips` | `10` |
| "Which versions do you want of each clip?" (both / horizontal 16:9 only / vertical 9:16 only) | `ratios` = `both`, `16x9` or `9x16` | `both` |
| "Once I have written the clip list and the editing prompts, should I stop and ask which ones to build, or build them all and report?" | `build_rule` = `ask` or `build` | `ask` |
| "Music or sound effects on these clips, or just the video's own sound?" (none / sound effects / music / both / ask each time) | `clip_sound` | `none` |
| "Should clips point back to the full video, with a small title tag at the start or an end card?" | `full_video_tag` = `no tag`, `title tag`, or what they describe | `no tag` |
| "Where should the finished clips go? The default is a Finals folder beside the video." | `finals_dir` = `beside the video` or a folder path | `beside the video` |

## Part 3: finish

1. Read every answer back as a short summary (shared and this skill's). Fix anything they correct.
2. `python3 setup/apply_profile.py`. It fills every placeholder, copies their fonts and profile picture into
   `assets/`, and writes `.configured`. It must end with "configured". If it prints `STILL TO ASK` or `UNFILLED`,
   ask for exactly those and run it again.
3. Check the fonts are really there: every file named in the profile is in `assets/fonts/`, and a font saved as
   `local` is installed (Adobe Fonts only render while Creative Cloud is running: tell them).
4. Tell them in two lines what is set up and what to try first: "Give me one of your videos, or its link, and say
   'clip this video'." On the first video, build one clip, show it, and note what they say before building the rest.

Later changes ("redo my setup", "change my colours", "my raws are on a new drive"): ask only the affected
questions, save them, and run `python3 setup/apply_profile.py` again. Rules they give while working go into
`~/.claude/creator-profile/notes/youtube-clips.md` under `## Style overrides`, dated.
