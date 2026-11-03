# Setup: fitted-stacked-captions

The first-run interview for this skill (the gate in `SKILL.md` sends you here), and again whenever the creator says
"redo my setup". Read `SHARED-SETUP.md` first ("How to run the interview"): **one question per message**, save each
answer as you go, never guess, never fill in from memory. This is a short interview (about five minutes): the skill
only does captions, so it needs the accent colour, two fonts and a few numbers.

**If `creator-setup` has been run**, the shared answers are already in the profile: read them back in one line
("I have you as Sam Okafor, accent #1E6BFF, main font Montserrat, transcribing with ElevenLabs. Still right?") and ask
ONLY this skill's own questions (Part 2). Do not walk the shared sections again.

Start by telling the creator, in two lines, what is about to happen: a few questions about colour and fonts so the big
word and the small words match their brand, asked one at a time, once. Then check what is already answered:

```bash
cd ~/.claude/skills/fitted-stacked-captions
python3 setup/apply_profile.py --status
```

and read `~/.claude/creator-profile/profile.json` if it exists. Anything already saved by another skill in the pack is
read back in one line and confirmed, not asked again.

## Part 1: the shared questions

Run these sections of `SHARED-SETUP.md`, in order, and skip any whose answers are already in the profile. Save shared
answers with `python3 setup/apply_profile.py --set key=value`.

| Section | What it settles | Notes for this skill |
|---|---|---|
| A1 Who you are | `creator_name`, `brand_name`, `handle`, `platform`, `niche` | Only the name and brand are needed for the captions; the rest are filled for the other skills. |
| A2 Brand colours | `accent`, `accent_name` | Steps 1 and 2 only. The accent colour is the colour of the big anchor word, so show it. Skip the background question: captions are white with a soft shadow and sit on top of the video. |
| A3 Fonts | `font_main_name`, `font_main_bold`, `font_accent_name`, `font_accent`, `font_caption_name`, `font_caption` | Two faces matter. The **emphasis font** is the big anchor word: a contrasting serif italic looks best, and if they have none the shipped Playfair Display Italic is the default. The **caption font** is the small fitted words: a bold weight of a clean sans (leave `font_caption` unset to use the main bold). Show a line of text set in each choice. Both must be found on their computer as described in A3; an Adobe font needs Creative Cloud running. The main regular weight is not used here. |
| A5 Transcription | `transcriber` | The captions are timed to the word, so ElevenLabs gives the cleanest result. Local is free and works; say that word edges are a little looser. Never ask for the key in chat. |
| A7 Where files live | `output_rule` | Only the output rule and the working folder matter here. Skip the drive question unless the raw footage is on one. |
| References they love | notes file, `## Style overrides` | Ask: "Are there one or two reels whose captions you want yours to feel like?" Compare them with "What the style is" in `SKILL.md`: word-by-word timing, how many words stack, size of the big word, position. Only the changes they pick become rules. |

Not needed for this skill: A4, A6 beyond a quick `ffmpeg -version`, A8 (no sound), A9. Also check that Google Chrome is
installed (`ls "/Applications/Google Chrome.app"`): the layout is measured in headless Chrome. If it is not, tell
them to install it or point `CHROME` at a Chromium build.

## Part 2: this skill's questions

Ask each one on its own. Save with `python3 setup/apply_profile.py --set-skill key=value` (quote the pair when the
value has spaces: `--set-skill "review_rule=render the final straight away"`). If they do not mind, say what the
default is and save the default. All of these have defaults, so none blocks the first caption.

### How the captions look

Show a layout sheet if you can: write a three-caption `plan.json` from a sentence they say, run `sheet`, and let them
see the result before the numbers are asked. This needs setup finished first, so do it after "Finishing" below and
come back to these only if they want a change.

| Ask | Key | Default |
|---|---|---|
| "How far ahead of your voice should each word appear? 0.22 seconds makes people read just before they hear it. Closer to 0 makes the words land on the beat." (seconds) | `lead_seconds` | `0.22` |
| "How big should the one big word be? 195 is a strong, readable size on a vertical video. Go smaller for a quieter look." (pixels on a 1080-wide frame) | `anchor_px` | `195` |
| "And the small words fitted around it? 48 is the default." (pixels) | `small_px` | `48` |
| "What is the lowest the captions may sit? Instagram and TikTok put buttons and text at the bottom of the screen, so 1250 on a 1920-tall frame keeps them clear." (a y position) | `bottom_limit` | `1250` |

These sizes and timings are the style's defaults; most creators keep them. Do not push a change.

### How we work together

| Ask (use `AskUserQuestion`) | Key | Default |
|---|---|---|
| "Before the full-quality render, should I give you a quick preview and wait for your yes, or render the final straight away?" | `review_rule` = `preview first, wait for approval` or `render the final straight away` | `preview first, wait for approval` |

## Finishing

1. Read the answers back as a short summary (name, accent colour with its name, the two fonts, the numbers, the review
   rule). Fix anything they correct.
2. `python3 setup/apply_profile.py` fills every placeholder in this skill, copies the fonts in and writes `.configured`.
   If it prints `STILL TO ASK` or `UNFILLED`, ask for exactly those and run it again. If it prints a font WARNING, the
   font file is not in `~/.claude/creator-profile/assets/fonts`: copy it there and run it again.
3. Run a quick check: write a three-caption `plan.json` and a matching `words.json` for a sentence they say aloud (or
   use `examples/example.plan.json` as the shape and their own words), run `fit_captions.py sheet`, and show them
   `sheet.png`. If a font does not load the script stops and names it.
4. Tell them in two lines what is set up and what the first thing to try is (send me a finished vertical reel and I
   will put the captions on it, or tell me to use this style inside a reel skill).
