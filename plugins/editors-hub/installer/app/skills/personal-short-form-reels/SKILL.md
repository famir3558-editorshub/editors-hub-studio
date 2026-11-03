---
name: personal-short-form-reels
description: Personal Short Form Reels - turn one raw talking-head clip into a finished, fast-paced 9:16 reel in the creator's own brand. Does the whole job - transcript, tight cut, the creator full screen with a hook and an opening graphic, full-frame B-roll from the creator's own footage library on the edit cuts, one-word bold captions, a small motion graphic whenever the creator is full screen, real brand logos, a split screen (screen recording on top, creator on the bottom) when software or a service is being shown, sound effects and a music bed. Use whenever the creator hands over a raw personal or talking-head clip and says "personal reel", "personal short form", "edit this with my B-roll", "the B-roll style", "edit this video" for a short vertical clip, or gives a clip plus a screen recording. Also for one part alone (the cut, captions, a new music bed, a new version). Not for the three-mode business reels (business-short-form-reels) or long-form YouTube. On first use it asks a short series of setup questions (brand, fonts, footage, references) before editing anything.
---

# Personal Short Form Reels

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/personal-short-form-reels/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first, one question at a time. Do not
  start the edit, and do not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if it exists,
  `~/.claude/creator-profile/notes/personal-short-form-reels.md`. Rules under `## Style overrides` in that notes file
  win over the defaults written below. That file is where the creator's references and corrections live.

"Redo my setup" re-runs the interview at any time. A new rule given while working is written into the notes file,
dated, the moment it is said.

## Your setup

| | |
|---|---|
| Creator | @@CREATOR_NAME@@ (@@HANDLE@@, @@PLATFORM@@) |
| Brand | @@BRAND_NAME@@: @@NICHE@@ |
| Accent colour | @@ACCENT@@ (@@ACCENT_NAME@@) |
| Caption font | @@FONT_CAPTION_NAME@@, bold |
| Emphasis font | @@FONT_ACCENT_NAME@@ (key words only) |
| Transcriber | @@TRANSCRIBER@@ |
| Working style | @@WORKING_STYLE@@ |
| B-roll | @@BROLL_SOURCE@@ |
| Music | @@MUSIC_RULE@@ (library: @@MUSIC_DIR@@; favourites in `assets/music.json`) |
| Sound effects | @@SFX_DIR@@ |
| Folders | work `@@WORK_ROOT@@/<slug>` · projects `@@PROJECTS_ROOT@@/<slug>-psf` · finals: @@OUTPUT_RULE@@ |
| Usual camera | @@CAMERA_SETUP@@ (horizontal default crops: full `@@CROP_FULL@@`, top `@@CROP_TOP@@`) |

One raw talking-head file in, one finished 1080x1920 reel out. Before designing, read
`examples/fear-of-failure/build.py`: a worked reel in this style, kept as a structure reference (another creator's
reel: copy how it is put together, never its wording, names or assets).

`SK=~/.claude/skills/personal-short-form-reels` · `S=$SK/scripts` · work dir `W=@@WORK_ROOT@@/<slug>` (small files) ·
project `P=@@PROJECTS_ROOT@@/<slug>-psf` · output `OUT` = @@OUTPUT_RULE@@ (default:
`"<folder of the raw file>/<Title> - Edit"`). Video files are large: keep the big files on the drive that holds the
raw file. Long steps run in the background; render one reel at a time.

**HyperFrames only.** Every reel is built and rendered with HyperFrames (`npx hyperframes`).

## How to work with the creator

- **Working style: @@WORKING_STYLE@@.**
  - `build-first` (the default for this format): build the whole reel, then report. Do not stop to ask about every
    graphic. Ask only what cannot be guessed (which of two files is the take, whether a screen recording exists for a
    software video).
  - `consult`: show the plan table (step 3) and ask about the opening, the B-roll picks and the music before building.
- The creator reviews the phone copy on their phone. Send it with `SendUserFile`, then say briefly what was cut, what
  each block shows, and **everything invented or chosen without asking** (comment wording, hook wording, stand-in
  names).
- Changing a finished reel: copy `build.py` to `build_vN.py` first, change, render with a new stem (`v2`). The creator
  compares versions.
- Never call a section of the video a "beat". Say block, moment, section or line.

## The style

These are the pack's defaults. The creator's own references and corrections (the notes file) override them.

**Structure.** 9:16, 1080x1920, 23.976 fps. Three kinds of window:

| Window | What is on screen | When |
|---|---|---|
| **Creator** (FACE) | The creator full screen with a slow zoom out, the caption under the chin, a small motion graphic below the caption | The opening, the punchlines, the close |
| **B-roll** (FULL) | The creator's own footage over the whole frame, in quick bursts; the voice carries on | Whenever a line can be *shown* loosely (see B-roll) |
| **Split** | A screen recording in a rounded card on the top half, the creator on the bottom half | Only when software, a service, a page or a tool is being shown |

- **Open on the creator, full screen**, with a 2-line hook at the top from frame 1 (`K.hook`: line 1 white, line 2
  black on a white block, caption font bold) and an attention-grabbing graphic tied to the topic (for a video about
  fear of judgment: judging Instagram comments dropping in). Close on the creator.
- **Fast.** B-roll clips run about 0.9-1.5 s each, never more than 5 s; several short clips beat one long one when
  the library has them. A creator window can be as short as 1.3 s when it holds a punchline. Aim for roughly half
  creator, half B-roll.
- **Every edit cut is hidden.** A B-roll or split window **starts or ends exactly on** each visible cut, so two takes
  of the creator never butt together. Ideally the window *ends* on the cut and the creator comes back. A window that
  sits wholly inside one take touches no cut and is fine. Use `P.sw(frame)` for every window edge: a time rounded up
  lands one frame late, and it shows.

**Captions.** One word at a time, **the caption font in bold**, lower-case, white, soft shadow, about 95 px under the
chin and never on the face. Key words in **the accent colour and the emphasis font** (roughly one every 1.5-2 s: the
words that carry the point; a figure takes the accent colour but stays in the caption font). **No pop-in animation.**
**Each word stays on screen until the next word starts**, through pauses and through every switch; the last word
holds to the end. Brand and people names keep their capitals (`keep=`). Phrase captions (1-3 words on a line) are a
different format: do not mix them into this one.

**Motion graphics on the creator.** One small, original graphic per creator window, below the caption (about y
1200-1560), landing just ahead of the word:
- something that *shows* the line, not a text pill repeating it (a dot heading for a flag with a red wall dropping in
  its way for "fear of failing"; a typing bubble for "now that I think about it"; the creator's profile picture with
  others appearing either side for "not the only one");
- anything quoted or received is a **real interface**: comments and DMs are Instagram notification banners
  (`P.comments`), a document is a Google Doc, a script line is a Notion page (see `kit.py`);
- positive = green `#2FA65A`, negative = red `#B3261E`, the neutral focal element = the accent colour `@@ACCENT@@`;
  text inside graphics stays modest (labels 34-50 px); nothing behind the head; no 3D, no bounces, no headlines over
  anything.
Entrances are a short focus pull (`opop`), exits a soft fade before the switch (`oout`).

**B-roll (the creator's own footage, loosely matched).** Source: @@BROLL_SOURCE@@. With the `personal-broll-library`
skill installed, search it (`broll.py search`, then judge the candidates yourself). Without it, ask the creator for
the footage folder and look at the clips directly.
- it does **not** have to match the words literally: eating a meal covers "no more takeaways", any phone clip covers
  "screen time";
- **look at the exact frames before using a clip** (`sheet.py every` on the source, or pull stills at the in-point):
  pick the moment that carries the feeling, inside a usable segment;
- vertical and horizontal footage both work; **horizontal clips stay horizontal with black bars** top and bottom
  (never crop them to fill, unless the creator asks);
- video only: the B-roll's own sound is never used; the footage on the drive is only ever read, never changed;
- vary the shots (close, wide, over-shoulder) and do not reuse a clip inside one reel; note anything showing
  strangers, children, private screens or logos in the report.
If the creator has no B-roll yet, say so, list what would be worth filming for this video, and build the reel with
creator windows and graphics only.

**Showing software or a service (split screen).** Read the transcript for anything being *demonstrated or pointed
at*: an app, a site, a feature, a dashboard, a setting, a result on a page. If the video is about one of those:
1. **Get the recording.** If the creator attached a screen recording, use it. If not, and the thing is public (a
   website, a product page), you may record it yourself: drive the page in the browser and capture it
   (`screencapture -v -V <seconds> "<file>.mov"` records the screen on macOS; needs Screen Recording permission; this
   route is **untested**, so check the file plays and shows the right window, and if it does not, ask the creator to
   record it). Anything behind a login (their own accounts, client data) the creator records.
2. **Find the right moments.** `python3 $S/sheet.py every "<recording>" 2` and read the sheets (go to 1 s or 0.5 s
   steps around the parts that matter). For each line, note the second of the recording that shows exactly that: the
   page loading, the button named, the number quoted, the before and the after. The picture must match the words *as
   they are said*, not arrive late.
3. **Cut the pieces** with `cut_clips.py` (`"fit": "screen"`; `"speed": 2.0` for a long scroll or a wait) and place
   them with `P.screen(...)`. Use `zooms=[(t, 1.8, ox, oy), (t2, 1)]` to push in on the button / field / figure on the
   word that names it, then back out. One split window may hold several pieces. Captions sit in the gap between the
   card and the creator's head.
4. Hide private details (emails, balances, client names) by choosing another moment or cropping the piece; say what
   was hidden.
Split windows follow the same cut rule (start or end on a cut) and replace B-roll for those lines; the creator is
still full screen for the opening and the close.

**Real logos.** When a brand, company, app or platform is named, show its **real logo** on the word (`P.logos`: white
rounded tiles below the caption). Find the official file: the company's own press / brand page first, then Wikimedia
Commons, then an image search in the browser. Take a clean, current, full-colour mark (SVG or a transparent PNG at
512 px or more), save it to `assets/logos/<brand>.png`, and open it to check it is the right, current logo. Never
redraw, recolour or stretch a logo, and never use a low-resolution or watermarked copy. Tell the creator in one line
which logos are being fetched and from where before downloading; list the sources in the report.

**Sound.** Quiet effects on key moments only (a soft whoosh as each B-roll or split window comes in, a pop on a
graphic landing): `K.ac(t, name)` and the scene helpers log them, `mix.py` adds them from the creator's own pack
(`sfx_map.json`, made at setup; no map = no sound effects, and say so). **Music: @@MUSIC_RULE@@.** `pick` = choose
one of the creator's favourites from `assets/music.json` whose feel suits the video, vary it from reel to reel, start
it at the listed second. `ask` = ask whether to add music and which track. The bed sits at **-43 dB mean** (the mix
default; -39 reads as loud under a voice). Deliver the music version and a no-music version and say which track was
used. Claude cannot hear: when the creator wants other options, choose by what is known of the piece plus
`music_profile.py`, and send 2-3 labelled versions to audition (`mix.py ... "<label>"`). Music rights are the
creator's to manage: commercial tracks can get a post muted.

## Workflow

**1. Transcribe** with the transcriber chosen at setup (@@TRANSCRIBER@@).
```bash
mkdir -p $W && ffmpeg -v error -y -i "$RAW" -vn -ac 1 -ar 48000 -c:a pcm_s16le $W/a48.wav && ffmpeg -v error -y -i $W/a48.wav -ar 16000 $W/a16.wav
python3 $S/01_transcribe.py $W && python3 $S/01b_el_to_tx.py $W          # prints the script with times and pauses
```
The ElevenLabs key is read from the shell profile by `stt.py`: never print it, never ask for it in chat. If the
transcript stops early with one long "audio event", measure the audio before assuming a fault: the camera is often
left rolling after the last take.

**2. The tight cut.** Write `$W/flubs.json` = `[[start, end], ...]` in raw seconds: everything before the piece, every
earlier attempt at a line (**keep the LAST complete take**), stumbles, throat clears, asides, and everything after the
last word. Pauses and breaths are removed by the script. Keep the meaning: never reorder or splice words.
```bash
python3 $S/02_cut.py $W && python3 $S/02b_guard_words.py $W && python3 $S/03_verify_cut.py $W     # read the EDIT line as a script
python3 $S/04_render_cut.py "$RAW" $W/edl.json "$OUT/<Title> - CUT.mp4"
python3 $S/prep_cams.py "$OUT/<Title> - CUT.mp4" "$OUT/hf-media"                                  # open cam_full.jpg and cam_top.jpg
python3 $S/05b_cut_words.py $W                                                                    # cut/words.json: every word's time on the cut
python3 $S/cut_times.py $W/edl.json "$OUT/hf-media/cam_full.mp4"                                  # the edit cuts, how big each jump is
```
Phone clips are often vertical footage stored with a rotation flag (ffprobe says 3840x2160 but it plays 2160x3840):
`prep_cams.py` handles both and says which it found. For a 16:9 source the default crops are the ones saved at setup;
check the crop stills and pass `--full` / `--top` when the framing differs.

**3. Plan the windows from the cuts.** List the words with their frames (`cut/words.json`, frame = time x 23.976).
Then:
- put a B-roll or split window so it starts or ends on every cut `cut_times.py` marks as a jump that must be hidden;
- add B-roll inside a take where a line can be shown (a list of things named is ideal: one short clip per item);
- keep the creator on screen for the hook, the punchlines and the close;
- decide per line: B-roll, split (software), a logo, or a graphic on the creator.
Write the plan as a small table (time, window, line, what is shown) in `$W/plan.md`; it goes in the report.

**4. Gather the pictures.** B-roll: search the library, look at the frames, write `$W/broll.json`. Screen recording:
steps above, write `$W/screen.json`. Logos: into the project's `assets/logos/`.
```bash
$S/new_project.sh <slug> "<Title>" "$OUT" $W/cut/words.json
python3 $S/cut_clips.py "$OUT/hf-media/broll" $W/broll.json && python3 $S/cut_clips.py "$OUT/hf-media/screen" $W/screen.json
```
Each piece is cut to its exact frame count (the script adds two spare frames).

**5. Build.** Write `build.py` with `psf.py` (docstring lists every call; `kit.py` has the interface mock-ups):
```python
A1, A2 = P.sw(77), P.sw(131); C1, C2 = P.sw(163), P.sw(261)            # frames of the cut
FACE = [[0, A1], [A2, C1], [C2, DUR]]; FULL = [[A1, A2]]               # C1..C2 is in neither list = a SPLIT window
P.setup(ROOT, DUR, FACE, FULL, "Title", emph={"fear", "failing"}, keep={"Notion"})
P.broll("b01", A1, A2, [("assets/broll/b1.mp4", 77, 21), ("assets/broll/b2.mp4", 98, 33)])
P.screen("s01", C1, C2, [("assets/screen/s1.mp4", 163, 98)], zooms=[(8.2, 1.8, 30, 40), (10.0, 1)])
K.hook("The one thing that", "held me back", A1 - 0.3)
P.comments([("dan.w", "commented: who does he think he is?", 0.02), ...], A1 - 0.3)
P.logos("lg", [("assets/logos/notion.png", 11.2)], C2 - 0.3)
K.OF.append('<div id="g2" style="position:absolute;...;opacity:0">...</div>'); K.ojs("opop('#g2', 5.5); oout('#g2', 6.5);")
P.finish()
```
`python3 build.py && npx hyperframes lint` (expect only "track too dense" and nested-media warnings), then
`npx hyperframes snapshot --no-end --describe false --at <a moment in every window, and each graphic at its peak>` and
**read every frame**: hook and fonts right (the creator's real fonts, no fallback), caption under the chin, graphics
clear of the caption and inside the frame, B-roll filling the frame or letterboxed, the recording readable.

**6. Render, mix, verify, deliver.**
```bash
$S/09_render.sh $P "$OUT" "<Title>" " (v1 - no SFX)"                                       # background; ~25 s for a 16 s reel
cd $P && python3 mix.py "$OUT" "<Title>" "v1" "<music root>/<file>" <start s> "<label>"   # writes "... (v1 - no music)" and "... (v1 - music <label>)", master + phone copy
python3 $S/sheet.py frames "<master>" <the frame of every window edge and every B-roll-to-B-roll change>
python3 $S/sheet.py every "<master>" 1
```
Open both sheets. Every change must land **on** its frame (the frame before shows the old picture, the frame on it the
new one), with no black frame; a word may carry one or two frames across a switch, which is right. Then send the
phone copy (`$P/renders/...(phone).mp4`, under 30 MB) and report: length before and after; what was cut that the
creator might want back; the plan table; the key words; the music track and start; logos and their sources;
everything invented; anything to check before posting (strangers, children, private screens, brand logos on
clothing). Say plainly what was verified on frames and what was not (Claude cannot listen to the mix).

## Gotchas
- `words=None` in the engine is deliberate: every caption comes from `captions.json` (written by `P.setup`), which is
  what makes the words hold through switches. Do not pass `words=` or `emph=` to `E.init` yourself.
- B-roll and split scenes neutralise the engine's glass / focus-pull wrapper with `!important` CSS; do the same for
  any other hard-cut scene.
- The bottom-half camera (`#camTop`) is hidden except in split windows; `cam_top.mp4` still carries the reel's audio,
  so it must always exist.
- In a split window the head must sit below the seam: if the top of the head is cut in `cam_top.jpg`, re-run
  `prep_cams.py` with a smaller `--top-y` (vertical source) or a different `--top` crop.
- Overlay CSS is global to the page: give every graphic a unique id. GSAP resets CSS `translate`: position with
  left/top, animate x/y/scale.
- `fromTo` opacity 0 to 1 inside a *scene* is treated as an entrance by the engine and shifted early; use the raw
  `__ft` / `__tt` for exact timing.
- `09_render.sh` names the file `<Title> - 9x16 Reel<suffix>.mp4`; `mix.py` looks for `(<stem> - no SFX)`, so keep the
  suffix in that form.
- Many ffmpeg builds have no drawtext / subtitles filters: all text is HTML. `SendUserFile` limit is 30 MB.
- A font activated through Adobe Fonts only renders while Creative Cloud is running. If a snapshot shows a fallback
  font, tell the creator rather than shipping it.

## Defaults this style avoids (change only if the creator asks)
Phrase captions (1-3 words on a line) · caption pop-in · words disappearing in pauses · cropping horizontal B-roll to
fill the frame · B-roll that straddles an edit cut · long B-roll holds when several short clips exist · music louder
than -43 dB mean · anything behind the head · 3D and bounces.

## Related
`personal-broll-library` (the footage index and `broll.py`) · `business-short-form-reels` (the engine's home;
three-mode business reels) · `hyperframes`, `hyperframes-cli`, `hyperframes-animation` (framework rules).
