# Setup: coaching-call-clips

The first-run interview for this skill. Read `SHARED-SETUP.md` first ("How to run the interview"): **one question
per message**, save each answer as you go, never guess, never fill in from memory. Start by checking what is already
answered:

```bash
cd ~/.claude/skills/coaching-call-clips
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
| A5 Transcription | `transcriber` | Say this when you ask: ElevenLabs labels who is speaking, which matters on a call with several people; local transcription has no speaker labels, so I work out who is speaking from what is said. Never ask for the key in chat. |
| A6 The tools | (check, do not ask) | Also check `swiftc --version` (face finding uses Apple's Vision framework, macOS only; `xcode-select --install` if it is missing) and `python3 -c "import numpy, soundfile, requests, PIL"` (`pip3 install numpy soundfile requests pillow`). If they are not on a Mac, say plainly that the clip list and prompts will work but the build half will not. |
| A7 Where files live | `output_rule`, `media_drive`, `work_root`, `projects_root` | Clips always sit beside the call recording in a "- Clips" folder; where the finished files go is asked below. |
| A8 Sound | `sfx_dir`, `music_dir`, `music_rule`, `sfx_map.json`, `music.json` | These clips default to no music and no effects. Ask A8 anyway so the profile is complete; if they have no sound pack, say that is fine for this skill. |
| A9 Your real material | `proof_dir` | |
| References they love | notes file, `## Style overrides` | Always ask. Compare with `references/style.md` and `references/layouts.md`. |

## Part 2: this skill's questions

Ask each one on its own. Save with `python3 setup/apply_profile.py --set-skill key=value` (quote the pair when the
value has spaces: `--set-skill "camera_angle=off to the side"`). If they do not mind, say what the default is and
save the default.

### How your calls are recorded

| Ask | Key | Default |
|---|---|---|
| "How do you record your coaching calls: Zoom, Fathom, a separate camera, something else?" | `call_recorder` | `Zoom` |
| "On the recording, is the camera off to one side while you look at the client on your screen, or facing you?" (`AskUserQuestion`: off to the side / facing the camera / it varies) | `camera_angle` | `off to the side` |
| "What resolution are the recordings usually? If you are not sure, point me at a recent one and I will check." (check with `ffprobe` rather than making them look it up) | `call_resolution` | `1080p` |

If the usual recording is 720p or lower, say now that the vertical version will be soft when they are full screen,
and that recording at 1080p or with a separate camera fixes it.

### Whose voices can be used (required)

| Ask | Key | Default |
|---|---|---|
| "Have the people on your calls agreed to be clipped and posted? This decides whether I can use their voice and their questions, or only yours." (`AskUserQuestion`: Yes, everyone has agreed / No, or not all of them / It depends on the call: ask me each time) | `clip_consent` = `yes`, `no` or `ask each call` | none: must be answered |

Say what each answer means before they choose: with `no`, the skill only clips their own voice, cuts everyone else's
lines, keeps clients' names and faces off screen, and lists any moment that needs someone else's words under "Needs
a yes first". Do not talk them into `yes`. Save exactly one of the three values: the scripts read it.

| Ask | Key | Default |
|---|---|---|
| "Is there anything that must never be clipped: topics, client names, programmes, numbers?" | `never_clip` | `nothing listed` |
| "Clients usually come through your speakers, so they can be hard to hear. When that happens, should I cut their lines and let the clip run on your words?" (cut their lines / keep them with captions) | `quiet_client` | `cut their lines` |
| "If there is swearing, it stays in the audio. In the captions, do you want it starred (f\*\*\*) or written as spoken?" | `swear_captions` = `starred` or `as spoken` | `starred` |

### How much, and how far I go on my own

| Ask | Key | Default |
|---|---|---|
| "How many clips at most from one call? I keep every clip that is good enough to post, with no minimum, up to this number." | `max_clips` | `10` |
| "Which versions do you want of each clip?" (both / horizontal 16:9 only / vertical 9:16 only) | `ratios` = `both`, `16x9` or `9x16` | `both` |
| "Once I have written the clip list and the editing prompts, should I stop and ask which ones to build, or build them all and report?" | `build_rule` = `ask` or `build` | `ask` |
| "Music or sound effects on these clips, or just the call's own sound?" (none / sound effects / music / both / ask each time) | `clip_sound` | `none` |
| "Where should the finished clips go? The default is a Finals folder beside the recording." | `finals_dir` = `beside the recording` or a folder path | `beside the recording` |

## Part 3: finish

1. Read every answer back as a short summary (shared and this skill's). Fix anything they correct.
2. `python3 setup/apply_profile.py`. It fills every placeholder, copies their fonts and profile picture into
   `assets/`, and writes `.configured`. It must end with "configured". If it prints `STILL TO ASK` or `UNFILLED`,
   ask for exactly those and run it again.
3. Check the fonts are really there: every file named in the profile is in `assets/fonts/`, and a font saved as
   `local` is installed (Adobe Fonts only render while Creative Cloud is running: tell them).
4. Tell them in two lines what is set up and what to try first: "Give me a recorded call and say 'clip this call'."

Later changes ("redo my setup", "change my colours", "my clients have all signed the release now"): ask only the
affected questions, save them, and run `python3 setup/apply_profile.py` again. Rules they give while working go into
`~/.claude/creator-profile/notes/coaching-call-clips.md` under `## Style overrides`, dated.
