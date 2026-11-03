# First-run setup: Personal B-Roll Library

Run this when `python3 setup/apply_profile.py --status` says `"configured": false`, or when the creator says
"redo my setup". Work from the skill folder (`cd ~/.claude/skills/personal-broll-library`) so the commands below run
as written.

Read `setup/SHARED-SETUP.md` first: its opening section ("How to run the interview") is the rulebook. The short
version: **one question per message**, wait for the answer, save it straight away, never fill an answer in from
memory, and offer the default whenever they do not know or do not mind.

Start by checking what is already answered (another skill in the pack may have asked the shared questions):

```bash
python3 setup/apply_profile.py --status
cat ~/.claude/creator-profile/profile.json 2>/dev/null
```

Then tell them in two lines what is about to happen: "A few quick questions so this works with your footage and your
editing app. About three minutes. After that I can scan your footage straight away."

---

## Part 1: the shared questions (from SHARED-SETUP.md)

This is not an editing skill, so it runs only two of the shared sections. Skip A2-A4, A6-A9 and "References they
love" completely: no colours, fonts, sound or profile picture are needed here.

| Section | Run it? | Notes |
|---|---|---|
| **A1. Who you are** | Yes, all four rows | `creator_name` and `niche` are required by this skill. `brand_name`, `handle` and `platform` are shared with the other skills in the pack: ask them once, and accept "skip" for any of the three. |
| **A5. Transcription** | **Optional here** | This skill only transcribes in one situation: matching B-roll to a video that has no captions file yet (Workflow C). Ask: "Sometimes I will need a transcript of a video to match B-roll to it. Want to choose how now, or leave it until the first time it comes up?" If now, run A5 as written. If later, save nothing and move on; Workflow C runs A5 the first time it is needed. Never ask for an API key in chat. |

Check the tools without asking (this skill needs far less than the editing skills):

```bash
python3 --version      # 3.9 or newer
ffmpeg -version        # any recent build; ffprobe comes with it
python3 -c "import PIL; print('Pillow ok')"    # optional: timestamp labels on the contact sheets
```

If ffmpeg is missing, give them the one command (`brew install ffmpeg` on a Mac) and wait until it passes. Pillow is
optional: offer `pip3 install pillow`, and carry on without it if they decline.

---

## Part 2: this skill's questions

Ask them in this order, one per message. Save each answer the moment you have it with
`python3 setup/apply_profile.py --set-skill key=value` (quote the whole pair when the value has spaces:
`--set-skill "footage_dir=/path/to/Media Drive/B-Roll"`).

### Where the footage is

| Ask | Saves to | Default / what to do with the answer |
|---|---|---|
| "Where does your B-roll live? Drag the folder into the chat, or tell me where it is." | `footage_dir` | No default: it is the first folder this skill scans and the one used in every example. Check it exists (`ls "<folder>" \| head`) and say how many video files you can see. If they have several folders, take the main one now; the others can be scanned later and are remembered by the library. If they have no B-roll folder yet, save the folder they plan to use and say the first scan will happen when there is footage in it. |
| "Is that on an external drive? Which one?" (skip the question and save the answer yourself when the path makes it obvious, e.g. on a Mac the path sits under the Volumes folder: say what you saved) | `footage_drive` | Default `this computer's internal disk`. For an external drive save its name (e.g. `external drive "Media Drive"`). Explain in one line: the drive only needs to be plugged in when I am looking at new clips or when you import into your editing app; searching works without it. |
| "I keep a small index of your clips on this computer, so you can search even when the drive is unplugged. I will put it in a folder called BrollLibrary in your home folder unless you want it somewhere else." | `library_dir` | Default `~/BrollLibrary`. If they name a folder on the external drive, say plainly that search will then only work with the drive plugged in, and let them decide. Never put it inside the footage folder. |

### How they edit

| Ask | Saves to | Default / what to do with the answer |
|---|---|---|
| "Which app do you finish your videos in?" Use `AskUserQuestion` with: Premiere Pro / DaVinci Resolve / Final Cut Pro / CapCut / I do not edit myself. | `editing_app` | Default `none (placement sheet only)`. Save one of: `Premiere Pro`, `DaVinci Resolve`, `Final Cut Pro`, `CapCut`, `none (placement sheet only)`, or the name of another app in their words. Then tell them honestly, in one or two lines, what they will get (the table below). Do not promise more than the table says. |
| "What frame rate do you usually edit at? 24, 25, 30 or 60. If you are not sure, I will read it from each video." | `sequence_fps` | Default `match the main video`. Save the number alone (`25`, `23.976`, `30`) or the default phrase. |
| "Are your edits horizontal (YouTube), vertical (Reels, Shorts, TikTok), or both?" Use `AskUserQuestion`. | `sequence_format` | Save exactly one of: `horizontal 1920x1080`, `vertical 1080x1920`, `both: horizontal 1920x1080 and vertical 1080x1920 (ask per edit)`. Default is `both`. If they edit at another size (4K, square), save it in their words with the pixel size. |

What to tell them about their editing app:

| App | What they get |
|---|---|
| Premiere Pro | A file they import with File > Import. It opens as a new sequence with the B-roll already placed above the main video. Their existing sequences are never touched. |
| DaVinci Resolve | The same file, imported with File > Import > Timeline. Resolve reads this format, but it was built and checked against Premiere, so the first import is a test, with a placement sheet as the backstop. |
| Final Cut Pro | Final Cut cannot open that file directly. They get a placement sheet (which clip, which seconds, where it goes), and if they have a converter app, or do not mind a detour through the free DaVinci Resolve, the timeline file can be converted. |
| CapCut | CapCut cannot import a timeline file. They get the placement sheet and place the clips by hand; the finding and choosing is still done for them. |
| None / other | The placement sheet, which any editor (or the person who edits for them) can follow. |

### What is in the footage, and what the videos are about

These two answers steer how clips get tagged and how searches are widened. Keep their own words.

| Ask | Saves to | Default / what to do with the answer |
|---|---|---|
| "What does your B-roll mostly show? For example: you at your desk, filming, at the gym, travelling, with clients, screen recordings." | `footage_shows` | No default. If they do not know yet ("I just film everything"), save `a mix: to be learned from the first scan` and update it after the first scan with what you actually saw. |
| "What do you make videos about? The topics and ideas that come up again and again." | `video_topics` | No default. If the `niche` answer already covers it, read it back and ask what they would add. Save as one line in their words. |
| Then offer: "Want me to teach the search your topics? For each one I will note what it tends to look like on screen, so that searching for 'sleep training' also finds the cot, the monitor and the night-time clips." | `niche_concepts_added` | If yes: follow "Adding their niche concepts" below. If no: skip; it can be done any time. |
| "Is there anything in your footage that must never be used or shown? People (a partner, children, a client), places (your home's street, a workplace), private screens (bank, messages, client accounts)." | `never_show` | Default `nothing listed`. Save as one line, specific enough to act on (`my children's faces; the front of the house; any screen showing client names`). Say what it means: those clips still get indexed, but they are flagged and never placed in an edit. |

#### Adding their niche concepts

The search widens a query through `concepts.json`: a concept on the left, the things that would literally be on
screen on the right. The skill ships a general starter set (`assets/concepts.json`); their niche goes into the copy
inside **their library**, never into the skill's seed file.

1. Make sure the library exists: `python3 scripts/broll.py init` (it reads `library_dir` from the profile; it copies
   the starter `concepts.json` in on first run).
2. From `video_topics` and `niche`, draft 6 to 12 concepts in their vocabulary. For each, list 5 to 10 visual
   terms that plausibly exist in the footage they described in `footage_shows`. Example for a sleep consultant:
   `"sleep training": ["cot", "baby monitor", "night", "dark room", "rocking", "bedtime", "blackout blind"]`.
   Do not invent footage they do not have; terms are only useful if a clip can match them.
3. Show the draft as a short list and let them add, remove or reword. Their words win.
4. Read `<library>/concepts.json`, add the agreed entries (lowercase keys; do not remove or overwrite an existing
   key without saying so), and write it back as valid JSON.
5. Save the names: `python3 setup/apply_profile.py --set-skill 'niche_concepts_added=["sleep training", "night feeds"]'`.

---

## Finishing

1. Read every answer back as a short summary (name, what they do, footage folder and drive, library folder, editing
   app, frame rate and shape, what the footage shows, topics, never-use list). Fix anything they correct.
2. Fill the skill:

   ```bash
   python3 setup/apply_profile.py
   ```

   It must end with `configured: every placeholder is filled.` If it prints `STILL TO ASK` or `UNFILLED`, ask for
   exactly those answers, save them, and run it again.
3. Tell them in two lines what is set up, then **offer the first scan straight away**:
   "Want me to look through your footage now? I will list every clip first (that part is quick and changes nothing),
   then watch them in batches of ten and build the library. You can stop me at any point and carry on later."
   - Yes: run Workflow A in `SKILL.md` on `footage_dir`. After `scan`, report the counts (new, duplicates,
     unsupported) and how long the analysis is likely to take before starting `extract`. For 50 or more clips, say
     you will do it in batches and report after each one.
   - Drive not plugged in: say so, and that the scan will start the next time they ask with the drive connected.
   - No: tell them the phrase to use later ("index my B-roll") and stop.
4. If `footage_shows` was saved as "to be learned from the first scan", update it after the scan with what the
   footage actually shows, run `python3 setup/apply_profile.py` again, and tell them what you wrote.

## Later changes

- "Redo my setup": run this file again from the top; read back each saved answer and only change what they change.
- "I moved my footage" / "new drive": ask for the new folder, `--set-skill` `footage_dir` and `footage_drive`, run
  `apply_profile.py`, then `broll roots` and `broll relink --from "<old>" --to "<new>"`. No re-analysis is needed.
- "I switched to a different editing app": `--set-skill editing_app=...`, run `apply_profile.py`, and tell them what
  changes in how they receive B-roll plans (the table above).
- "Never show X": add it to `never_show` (keep what is already there), run `apply_profile.py`, then search the
  library for clips that match and add the flag to each one's `issues` and `avoid_for` by re-ingesting its record.
- Moving the library index: move the folder yourself only if they ask, then `--set-skill library_dir=<new>` and run
  `apply_profile.py`. The footage is never moved by this skill.
- Any new standing rule they give while working ("always prefer vertical clips", "never suggest gym footage for
  business videos") goes into `~/.claude/creator-profile/notes/personal-broll-library.md` under
  `## Style overrides`, dated, the moment they say it.
