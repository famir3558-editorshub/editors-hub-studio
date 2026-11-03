# Setup: ranking-format

The first-run interview for this skill (the gate in `SKILL.md` sends you here), and again whenever the creator says
"redo my setup". Read `SHARED-SETUP.md` first ("How to run the interview"): **one question per message**, save each
answer as you go, never guess, never fill in from memory. It takes a few minutes. The goal is that the first tier-list
reel is already theirs.

**If `creator-setup` has been run**, the shared answers are already in the profile: read them back in one line (name,
brand, accent colour, fonts, transcriber) and ask ONLY this skill's own questions in Part 2. Otherwise run Part 1.

Start by telling the creator, in two or three lines, what is about to happen: a short series of questions about their
brand and how they want their ranking videos to look, asked one at a time, which only happens once. Then check what is
already answered:

```bash
cd ~/.claude/skills/ranking-format
python3 setup/apply_profile.py --status
```

and read `~/.claude/creator-profile/profile.json` if it exists. Anything already saved by another skill in the pack
is read back in one line and confirmed, not asked again.

## Part 1: the shared questions

This is an editing skill, so run these sections of `SHARED-SETUP.md`, in order. Save shared answers with
`python3 setup/apply_profile.py --set key=value`.

| Section | What it settles | Notes for this skill |
|---|---|---|
| A1 Who you are | `creator_name`, `brand_name`, `handle`, `platform`, `niche` | `niche` steers the pictures chosen for the items. |
| A2 Brand colours | `accent`, `accent_name`, optional `bg`, `paper`, `grey` | The accent colour is the topic title and the item name when it is spoken as a caption. The tier row colours are the classic tier-list palette and are not asked about. The background only shows if the footage does not fill the frame; keep the default. |
| A3 Fonts | `font_main_name`, `font_main_bold`, `font_caption_name`, `font_caption` | Two roles only: the main bold (topic title, tier letters, the item names on the cards) and the caption font (leave unset to reuse the main bold). There is no emphasis font in this format: skip that row. |
| A4 Your face on screen | | Skip: this format shows no avatar. |
| A5 Transcription | `transcriber` | The cut uses the business-short-form-reels scripts, which read the same profile. ElevenLabs gives cleaner word edges; local is free and works, the cut then needs a closer listen. Never ask for the key in chat. |
| A6 The tools | (check, do not ask) | Also check `swiftc --version` (the face check uses Apple's Vision framework, macOS only: `xcode-select --install` if missing) and `python3 -c "import PIL"` (`pip3 install pillow`). If they are not on a Mac, say plainly that the table placement must then be chosen by eye on a few frames. |
| A7 Where files live | `output_rule`, `media_drive`, `work_root`, `projects_root` | Keep the project on the same drive as the cut. |
| A8 Sound | `music_dir`, `music_rule` | Music only: this format has no sound effects of its own. For `music_rule` the default is `ask`. |
| A9 Your real material | `proof_dir` | The first place a picture for each ranked item is looked for. |
| References they love | notes file, `## Style overrides` | Always ask: "Do you have a ranking or tier-list reel you want yours to feel like?" Compare with "The look" in `SKILL.md`: title size and colour, card shape and how it lands in the row, caption position, how long a card holds before the verdict. |

Also confirm that `business-short-form-reels` is installed in `~/.claude/skills/`: steps 1-3 of this format (transcript,
cut, crops) run its scripts. If it is not, say so and ask before continuing.

## Part 2: this skill's questions

Ask each one on its own. Save with `python3 setup/apply_profile.py --set-skill key=value` (quote the pair when the
value has spaces). If they do not mind, say what the default is and save the default.

### The pictures

| Ask | Key | Default |
|---|---|---|
| "Besides your proof folder, are there other folders I should search for a picture that represents each thing you rank?" (full paths; several are fine, saved as a JSON list) | `asset_dirs` | `none` |
| "When I need a picture of a real company, app or product, may I fetch real screenshots, logos and photos from the web? You decide what you are comfortable publishing: I list every source in my report." (`AskUserQuestion`: yes, list the sources / only my own material and screenshots of public pages / no, only my own material) | `web_assets` | `yes: real over drawn, every source listed in the report` |
| "Is there anything that must never appear on a card: names, brands, competitors, people?" | `never_show` | `nothing listed` |

### The look: confirm the defaults

Show the sample first if it helps (`examples/placeholder-sample/index.html`, render a snapshot of it). One message each;
`AskUserQuestion` with "Keep it" first.

| Ask | Key | Default |
|---|---|---|
| "The topic title sits at the top in your accent colour, in capitals, italic. Keep that, or upright or as written?" | `title_style` (`italic` or `normal`) and `title_case` (`uppercase` or `none`) | `italic`, `uppercase` |
| "The name printed on each item card is bold, outlined in black, in yellow so it reads on any picture. Keep yellow, or use another colour?" (a hex code) | `card_name_colour` | `#FFE53B` |
| "Captions: three to six words on one line just above the table, the item's name in your accent colour. On, or no captions at all?" | `captions` (`on` or `off`) | `on` |
| "If the table would cover your face, the order is: full size inside the safe zone, then pushed lower into the bottom zone, then 10 to 20 percent smaller. I always show you the options on a real frame before building. Keep that order?" | `face_rule` | `safe zone first, then lower into the bottom zone, then 10-20% smaller; always show the option frames and let the creator choose` |

The tier table is always the seven tiers S to F and the footage is never scaled or shifted to make room. Say that
once; if they want something else, write it under `## Style overrides` in their notes file.

### How we work together

| Ask (use `AskUserQuestion`) | Key | Default |
|---|---|---|
| "Should I build the preview and report, stopping only to show you the table placement when it cannot sit in the safe zone, or stop and check with you after the plan as well?" | `work_rule` | `build a preview, show the layout options when the table cannot sit in the safe zone, then wait for approval before the final` |

Either way a preview is always shown and approved before the final is rendered.

## Part 3: finish

1. Read every answer back as a short summary (shared and this skill's). Fix anything they correct.
2. `python3 setup/apply_profile.py`. It fills every placeholder, copies their fonts into `assets/`, and writes
   `.configured`. It must end with "configured". If it prints `STILL TO ASK` or `UNFILLED`, ask for exactly those and
   run it again.
3. Check the fonts are really there: every file named in the profile is in `assets/fonts/`, and a font saved as
   `local` is installed (Adobe Fonts only render while Creative Cloud is running: tell them).
4. Open `SKILL.md` again (it now carries their values) and tell them in two lines what is set up and what to try
   first: "Give me a video where you rank things and say 'make this a ranking video'."
5. On the first video, look at the first snapshot and check the fonts are the real ones and not a fallback.

Later changes ("redo my setup", "change my colours", "no captions"): ask only the affected questions, save them, and
run `python3 setup/apply_profile.py` again. Rules they give while working go into
`~/.claude/creator-profile/notes/ranking-format.md` under `## Style overrides`, dated.
