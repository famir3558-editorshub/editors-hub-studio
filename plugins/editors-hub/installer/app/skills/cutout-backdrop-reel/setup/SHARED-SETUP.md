# Shared setup: the questions every skill in this pack needs answered once

This file is the same in every skill of the pack. The answers are saved to ONE profile,
`~/.claude/creator-profile/profile.json`, so the creator is asked each of these once, not once per skill.
The skill's own `SETUP.md` tells you when to run this part and which sections it needs.

## How to run the interview (read this first)

- **One question per message.** Ask, stop, wait for the answer, save it, then ask the next one. Never send the list.
  Use `AskUserQuestion` when the answer is a choice (2-4 concrete options, your recommendation first); ask in plain
  chat when it is free text (a name, a hex code, a folder).
- **Do not guess and do not fill in from memory, CLAUDE.md or an earlier conversation.** Asking is the point. The one
  exception: an answer already saved in the profile. Read it back in one line ("I have your accent colour as #1E6BFF
  from an earlier setup. Still right?") and move on when they say yes.
- **Say why you are asking** in a few words when it is not obvious ("so the captions use your font").
- **Show, don't describe**, wherever you can: a colour swatch, a line set in their font, a still with the crop drawn on.
- If they do not know or do not care, offer the default, say what it is, and save it. Never leave a question hanging.
- Save as you go: `python3 setup/apply_profile.py --set key=value` (shared answers) so a closed window loses nothing.
  Values with spaces: quote the whole pair, `--set "creator_name=Sam Okafor"`. Lists and objects are JSON.
- Speak plainly. They are a creator, not a developer: no file formats, flags or jargon unless they ask.
- At the end, read the whole profile back as a short summary and let them correct anything before you fill the skill.

Check first what is already answered: `python3 setup/apply_profile.py --status` and read the profile file if it exists.

---

## A1. Who you are  *(every skill)*

| Ask | Saves to | Notes |
|---|---|---|
| "What name should I use for you: the one that appears on screen and in my notes?" | `creator_name` | Full name as they want it shown. |
| "What is the business or brand called?" | `brand_name` | If it is just their name, save the name again. |
| "What is your main handle, and on which platform do you post most?" | `handle`, `platform` | Handle with the @. Platform: Instagram / TikTok / YouTube / LinkedIn. |
| "In one sentence: what do you help people with, and who are they?" | `niche` | Used to pick fitting graphics, examples and wording. Keep their words. |

## A2. Brand colours  *(editing skills)*

1. "Do you have a brand guide, a logo file or a website I can take your colours from? Drop the file into the chat or
   paste the link. If you already know the hex codes, just tell me."
   - A file or screenshot: read it and pull the colours out. A website: open it and read the colours it uses.
   - No brand yet: offer three accent colours that suit their niche and let them pick.
2. Confirm the **accent colour** (the one colour used for the key word, the active element, the glow) by showing it.
   Save `accent` (hex, e.g. `#1E6BFF`) and `accent_name` (the plain word for it: "blue", "gold", "lime").
3. "These edits are built on a dark background so the graphics glow. Keep the near-black default, or use your own dark
   colour?" Save `bg` only if they change it (default `#050505`). The engines are designed for a dark background:
   if they ask for a light one, say plainly that glass cards and glows will need restyling and note it in the profile
   notes rather than promising it works.
4. Optional, only if their guide has them: `paper` (off-white text colour, default `#F2F0EC`) and `grey` (default
   `#9A928A`).

Positive = green and negative = red stay as they are in every skill (gain / loss, right / wrong). That is a meaning,
not a brand colour.

## A3. Fonts  *(editing skills)*

Three roles. Ask them one at a time, and show a line set in each font when you have it.

| Role | Ask | Saves to |
|---|---|---|
| **Main font** (hooks, labels, numbers, everything in graphics) | "Which font do you use for headlines? If you do not have one, I suggest a clean bold sans." | `font_main_name`, `font_main_bold`, `font_main_regular` |
| **Emphasis font** (the few key words that change colour) | "Do you want key words in a second, contrasting font, like an elegant serif italic, or the same font just in your colour?" | `font_accent_name`, `font_accent` |
| **Caption font** | "Captions in the same main font, or a different one?" | `font_caption_name`, `font_caption` (leave unset to reuse the main bold) |

Then find each font **on their computer** (never assume it is installed):

```bash
fc-list | grep -i "<name>"                       # if fontconfig is installed
ls ~/Library/Fonts /Library/Fonts /System/Library/Fonts /System/Library/Fonts/Supplemental | grep -i "<name>"
```

- **A single .ttf / .otf / .woff2 file exists:** copy it to `~/.claude/creator-profile/assets/fonts/` and save
  `{"file": "<filename>"}`.
- **It only exists inside a .ttc collection, or it is activated through Adobe Fonts** (no file to copy): save
  `{"local": ["<Full name>", "<PostScript-Name>"]}`, for example
  `--set 'font_main_bold={"local": ["Helvetica Neue Bold", "HelveticaNeue-Bold"]}'`. Adobe Fonts only render while
  Creative Cloud is running: tell them.
- **It is a Google Font they do not have:** say you will download it from Google Fonts, wait for the yes, download
  the static file for the weight you need, then treat it as a file.
- **They have no preference:** the editing skills ship an open-licence emphasis font in `assets/fonts/` (Playfair Display
  italic; the two reel skills also carry Caveat for handwritten notes). For the main font suggest a free bold sans from Google Fonts (Inter,
  Manrope, Archivo) and download it once they agree.
- A font they do not have a licence for is their call, not yours: use what is installed, and never download a
  commercial font from an unofficial site.

After the first build, look at a snapshot and check every font is the real one and not a fallback.

## A4. Your face on screen  *(editing skills)*

"Drop in the profile picture you use on your main platform. It appears in the notification and DM mock-ups."
Save it as `~/.claude/creator-profile/assets/avatar.jpg` (square crop, 400 px or more).

## A5. Transcription  *(every skill)*

Anything that starts from spoken audio is transcribed first. Ask with `AskUserQuestion`:

- **ElevenLabs (recommended)**: the most accurate words and timings, speaker labels on calls, about $0.22 per hour of
  audio. Needs an ElevenLabs account and an API key.
- **On this computer (free)**: runs through HyperFrames. Private and free; timings are slightly looser, so cuts need a
  closer check, and there are no speaker labels.

Save `transcriber` = `elevenlabs` or `local`.

If ElevenLabs: **never ask them to paste the key into the chat.** Tell them to do this themselves, once:

1. ElevenLabs website -> Developers -> API Keys -> create a key with Speech to Text access.
2. In Terminal, with their key in place of the dots:
   ```bash
   echo 'export ELEVENLABS_API_KEY="..."' >> ~/.zshrc
   ```
3. Then check it without printing it: `python3 -c "import sys; sys.path.insert(0,'scripts'); import stt; print('key found' if stt.el_key(False) else 'no key yet')"`

They can switch at any time: `python3 setup/apply_profile.py --set transcriber=local`.

## A6. The tools  *(editing skills)*

Check, do not ask:

```bash
node -v            # 22 or newer
ffmpeg -version    # any recent build
npx hyperframes doctor
```

HyperFrames is what builds and renders every edit in this pack. If anything is missing, give them the one command
that fixes it (`brew install ffmpeg node`, `npx hyperframes@latest doctor`) and wait until it passes. The scripts are
written for macOS (zsh, Apple's Vision framework for face finding); say so plainly if they are on Windows.

## A7. Where files live  *(editing skills)*

| Ask | Saves to | Default |
|---|---|---|
| "Where should finished videos go? Next to the raw file in an '- Edit' folder is the default." | `output_rule` | `beside the raw file` |
| "Is your raw footage on an external drive? Which one?" | `media_drive` | none |
| (do not ask) small working files | `work_root` | `~/reel-work` |
| (do not ask) HyperFrames projects | `projects_root` | `~/videos` |

Video files are large. If their internal disk is nearly full, keep the cut, crops and renders on the drive that holds
the raw file and render one video at a time.

## A8. Sound  *(editing skills that mix sound)*

1. "Do you have a sound-effects pack (whooshes, pops, clicks)? Tell me the folder."
   - Yes: `python3 scripts/sfx_probe.py "<folder>"` lists every file with its length and peak level. Choose one file
     for each role the mix uses (`woosh`, `swish`, `swoosh`, `pop`, `shine`, `swirl`, plus any others the folder
     offers), write `~/.claude/creator-profile/assets/sfx_map.json` in the format the probe prints, and save `sfx_dir`.
   - No: the edit is delivered without sound effects until they have one. Say so; do not invent sounds.
2. "Where do you keep music you are allowed to use, and are there tracks you always come back to?"
   Save `music_dir`. Favourites go in `~/.claude/creator-profile/assets/music.json` (label, file, the second the
   music should start from, one line on its feel). Music rights are theirs to manage: remind them once that
   commercial tracks can get a post muted, then follow their decision.
3. "Should I always ask before adding music, or add a favourite and tell you which?" Save `music_rule`
   (`ask` or `pick`).

## A9. Your real material  *(editing skills)*

"Where do you keep the real things I can show on screen: client results, testimonials, screenshots, your own reel
covers?" Save `proof_dir` (a folder, or "none yet"). These edits use real screenshots and real people wherever
something real exists, and a clearly generic stand-in where it does not, listed in the report every time.

---

## References they love  *(editing skills: always ask)*

"Are there two or three videos whose editing you want yours to feel like? Download them and drop the files into the
chat (or give me the folder they are in). A link is second best: I can only study a link if the video is public."

For each reference:

1. Watch it properly: use the `watch` skill if it is installed, otherwise pull frames with ffmpeg
   (`ffmpeg -i ref.mp4 -vf fps=2 frames/%04d.jpg`) and read them in order, and transcribe the audio.
2. Write down what you see, in this order: frame layout and how it changes; how often the picture changes (count the
   cuts in 10 seconds); captions (words at a time, case, size, position, font feel, emphasis); the opening two
   seconds; what graphics appear and how they move in and out; colour and background; sound effects and music.
3. Compare it with this skill's defaults (the "style" section of `SKILL.md`). Tell them, in a short list, what
   already matches, what you would change to move towards the reference, and what the engine cannot do as built.
4. Ask which of those changes they want. Only the ones they pick become rules.
5. Save the result in `~/.claude/creator-profile/notes/<skill name>.md` under `## Style overrides` (one line per
   rule, dated), with the reference files listed under `## References`. That file wins over the defaults in
   `SKILL.md` and is read at the start of every session.

A reference is a guide to feel, pace and structure. Never copy another creator's wording, graphics or assets.

---

## Finishing

1. Read the answers back as a short summary. Fix anything they correct.
2. `python3 setup/apply_profile.py` fills every placeholder in this skill, copies the fonts and profile picture in,
   and writes `.configured`. If it prints `STILL TO ASK` or `UNFILLED`, ask for exactly those and run it again.
3. Tell them in two lines what is set up and what the first thing to try is.

Later: "redo my setup", "change my colours", "I have a new font" -> ask only the affected questions, `--set` them,
run `apply_profile.py` again. New rules they give while working ("never do X", "always Y") go straight into
`~/.claude/creator-profile/notes/<skill name>.md` under `## Style overrides`, dated, the moment they say them.
