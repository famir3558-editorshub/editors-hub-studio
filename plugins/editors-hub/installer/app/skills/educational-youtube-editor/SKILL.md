---
name: educational-youtube-editor
description: Educational YouTube Editor - turn a long-form educational talking-head video (5 to 60+ minutes, 16:9) into a polished, highly visual YouTube video built in HyperFrames. Does the whole job from the RAW file - a word-timed transcript, a clean dialogue edit first (mistakes, false starts, repetition and dead space out; natural rhythm and meaning kept), a full read of the argument (promise, sections, frameworks, lists, stories, statistics, every company / person / product / website named), a scored edit plan, real-world asset retrieval (the creator's own files first, then the web), and the build - the speaker moves between full-screen talking head, designed overlays beside them, a genuine 50/50 split screen, a side panel and full-screen explainer animations (flows, framework maps, funnels, visual metaphors, counters, graphs, "what you'll learn" previews that hold the curiosity), motivated punch-ins and a barely-felt camera drift, a meaningful visual change inside the first 3 seconds, faces never cropped, density that breathes in waves, quiet sound design, a chunked render and a quality audit. Use whenever the creator hands over a long YouTube video, lesson, tutorial, podcast-style solo episode or VSL and says "edit this YouTube video", "long-form edit", "educational edit", "YouTube editor skill", "add the graphics / b-roll / examples to this video", "make this more visual", "split screen with examples", "same as the last YouTube edit", or asks for one part alone - only the dialogue edit, only the content analysis, only the edit plan, only the intro, the asset hunt, a re-render after notes. Not for 9:16 reels or shorts (use a short-form reel skill), clips cut out of a long video (youtube-clips), coaching-call clips (coaching-call-clips) or written content from a video (video-to-written-content).
---

# Educational YouTube Editor

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/educational-youtube-editor/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first. Do not start the task, and do
  not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if it exists,
  `~/.claude/creator-profile/notes/educational-youtube-editor.md`. Rules under `## Style overrides` in that notes file
  win over the defaults written below.

"redo my setup" re-runs the interview at any time.

## Your setup

Filled in by setup. To change a line, change the answer (`setup/SETUP.md`), never this text.

| | |
|---|---|
| Creator | @@CREATOR_NAME@@ · @@BRAND_NAME@@ · @@HANDLE@@ |
| What they teach, and to whom | @@NICHE@@ |
| Colours | accent @@ACCENT@@ (@@ACCENT_NAME@@) · background @@BG@@ · text @@PAPER@@ · small labels @@GREY@@ |
| Fonts | main: @@FONT_MAIN_NAME@@ · emphasis: @@FONT_ACCENT_NAME@@ |
| Logo · wordmark | @@LOGO@@ · @@WORDMARK@@ |
| Where the logo appears | @@LOGO_USE@@ |
| Transcriber | @@TRANSCRIBER@@ |
| Raw long-form files live in | @@RAW_DIR@@ |
| Footage drive | @@MEDIA_DRIVE@@ |
| Finished videos go | @@OUTPUT_RULE@@ |
| Folders | working files `@@WORK_ROOT@@` · HyperFrames projects `@@PROJECTS_ROOT@@` |
| Real material (proof) | @@PROOF_DIR@@ |
| Other folders to search for real assets | @@ASSET_DIRS@@ |
| Real assets from the web | @@WEB_ASSETS@@ |
| Dialogue edit | pauses over @@PAUSE_OVER@@ s are shortened to @@PAUSE_TO@@ s · breaths: @@BREATHS@@ |
| Punch-in strength | @@PUNCH_PERCENT@@% |
| Depth and 3D in graphics | @@DEPTH_3D@@ |
| Captions | @@CAPTIONS@@ |
| Master resolution | @@MASTER_RESOLUTION@@ |
| How far to go alone | @@WORK_RULE@@ |
| Music | @@MUSIC_RULE@@ · music folder: @@MUSIC_DIR@@ |
| Sound effects | @@SFX_DIR@@ |
| Never show | @@NEVER_SHOW@@ |

## What this skill is for

Long-form 16:9 educational edits at scale. The goal is not maximum editing. It is **maximum clarity, comprehension, retention and visual storytelling**: premium educational YouTube editing + modern explainer animation + real-world visual evidence + clean motion design.

**Clean dialogue first. Intelligent visuals second. Retention and comprehension throughout.** It should feel as if an editor first made an excellent YouTube dialogue edit, then layered a visual storytelling and motion-design system on top.

**Every visual needs a reason to exist.** A graphic goes on screen because it explains, demonstrates, proves, shows a real example, simplifies, creates curiosity, emphasises, keeps momentum or helps memory, never because the screen has been still for a few seconds. The engine enforces this: every scene must name its `why`, and a scene without one does not build. The edit should feel like the editor understood the argument, not like software reacting to keywords.

This is **not** a short-form style stretched out. It shares the eye of a good reel (real assets, focus-pull motion, green = positive / red = negative, real interfaces, quiet sound) but long-form needs restraint, the creator's face on screen most of the time, and density that rises and falls. Read `references/` as each step calls for it; the files are short and each one covers one part of the job.

| When | Read |
|---|---|
| Before cutting anything | `references/dialogue-edit.md` |
| Before reading for the visuals | `references/analysis.md` |
| Before planning any visual | `references/decision-engine.md` |
| Planning the first 45 seconds | `references/intro-playbook.md` |
| Choosing or building a graphic | `references/component-library.md` |
| Anything named that could be shown | `references/asset-retrieval.md` |
| Building and animating | `references/motion-sound-design.md` |
| Before calling it done | `references/quality-check.md` |

## How to work with the creator

How far to go without asking is a setup answer: see "How far to go alone" in **Your setup**.

- **`run to the end, then report` (the pack default).** This skill exists for volume, so do not stop to ask for each asset or each wording choice: search the creator's own files, then the web (if "Real assets from the web" allows it), build, and at the end list every asset with its source, every wording you chose, and anything invented or mocked up. On a first pass of a new video, show the plan before the build as a short table (time, what is said, state, graphic, why) and carry on building. A plan is cheap to change; a 40-minute render is not.
- **`stop and ask at each stage`.** Stop and wait for a yes at three points: after the dialogue edit (give the raw length against the cut length and the notable removals), after the edit plan (the same short table), and after the draft render (the review sheets). Within a stage, still do not ask about each asset or wording choice: list them at the stop.
- **Two things are always asked, whichever answer they gave:** anything they drag in as a screenshot or file (where it goes), and music when "Music" in **Your setup** says `ask` (whether, and which track; deliver with and without).
- **Real over drawn, always.** When the creator names a thing, the viewer should think "that is exactly what they are talking about". Rights to third-party images are the creator's to manage: they answered how far to go at setup ("Real assets from the web"), and every source is listed in the report so they can decide.
- **Nothing on the "Never show" line ever appears**, in a graphic, a screenshot, a browser capture or the background of a photo. Check every fetched asset against it.
- **Each video gets its own signature**: one visual idea that belongs to this video only (its core framework or metaphor), introduced early and returned to.
- The creator reviews the actual file. Deliver the master and the review sheets, and say plainly what is unverified.
- Anything they tell you while working ("never do X", "always Y") goes into `~/.claude/creator-profile/notes/educational-youtube-editor.md` under `## Style overrides`, dated, the moment they say it.

## The five visual states

The creator's face is the default and should stay on screen roughly 70% or more of the time.

| State | What it is | Use it when |
|---|---|---|
| **head** | The creator, full screen. A very slow camera drift keeps it alive; an occasional motivated punch-in adds emphasis | Story, emotion, nuance, personality, a line that lands on its own, and any stretch where no graphic genuinely helps |
| **float** | The creator full screen + one designed element in the empty space beside them, or a bottom title, or the top framework tracker | A supporting example, a named term, a small piece of proof, "you are here" |
| **panel** | A side panel slides in and the creator slides across | A short list or a stat they keep talking over |
| **split** | A genuine 50/50 split, divided cleanly down the middle: the real footage, cropped naturally around the creator, fills one half edge to edge; the branded side holds the supporting content | A real-world example, a screenshot, a diagram, a comparison they are reacting to. A core technique. **The creator is never put in a floating card, rounded rectangle, frame or box** (the engine refuses). Swap sides now and then |
| **full** | A full-screen visual explanation; the voice carries on | The few moments that deserve it: a framework, a process, a cause and effect, a metaphor, the "what you'll learn" preview |

## Workflow

`S=~/.claude/skills/educational-youtube-editor/scripts` · work dir `@@WORK_ROOT@@/<slug>` (small files) · project `@@PROJECTS_ROOT@@/<slug>-yt` · output: the output folder (`@@OUTPUT_RULE@@`); by default `"<video folder>/<video name> - Edit"`, on the drive the video is on. Video files are large: the cut, the working copy and the rendered chunks stay on the drive that holds the raw file. Run long steps in the background. One render at a time when writing to an external drive.

If the creator names a video without a path, look in the raw folder from **Your setup** first; if it is not there, ask.

1. **Receive the raw video and prepare.** `python3 $S/01_prep.py "<raw video>" <slug> ["<output folder>"]`. The creator gives the raw file, not a pre-edit. Pass the output folder only when "Finished videos go" in **Your setup** names somewhere other than beside the raw file.
2. **Transcribe the whole video.** `python3 $S/02_transcribe.py <slug>`. It uses the transcriber chosen at setup through `scripts/stt.py` (ElevenLabs, or free on this computer). If it reports that the ElevenLabs key is missing, tell the creator how to add it to their shell profile themselves (`setup/SHARED-SETUP.md`, A5), or offer to switch to local transcription. **Never ask for the key in chat.**
3. **Understand the entire video.** Read the full script for the argument, teaching points, stories and examples (`references/analysis.md`) before marking a single cut.
4. **Identify mistakes, repetition, dead space and content that does not serve the point.** Write `drops.json` with a reason on every entry (`references/dialogue-edit.md`).
5. **Create the clean dialogue edit.** `python3 $S/03_cut.py <slug> && python3 $S/04_verify.py <slug>` until clean; read `edit.txt` as a script and check every cut preserves the meaning; then `python3 $S/05_render_cut.py <slug>`. Tight, confident, natural: pauses over @@PAUSE_OVER@@ s are shortened to @@PAUSE_TO@@ s, not removed (the script reads these from setup), and not every filler goes. **The voice is never processed** beyond the cuts. With local transcription the word edges are looser: listen to `edit.wav` around the joins before rendering the cut.
6. **Analyse where visuals improve comprehension or retention.** `python3 $S/06_new_project.py <slug> "<Title>"` (open `face-check.jpg`; re-run with `--refresh --face X,Y` if the ring is not on the nose: the split crops around it). It prints which brand images and fonts it found: a font reported as not found must be fixed before anything is rendered. Fill in `content_map.json`, then write `edit_plan.json` following `references/decision-engine.md`: one entry per moment with what is being communicated, the `why`, a 1-5 score, the state, the component and the asset wanted, plus the stretches deliberately left alone. `python3 $S/plan_check.py <slug>`.
7. **Build the visual edit.** Get the real assets first (`references/asset-retrieval.md`: `find_assets.py`, then `get_asset.py`; look at every image with Read). Write `build.py` with `yt_engine` (E) and `yt_kit` (K); time everything from the words with `E.w("exact words", after)`. Look as you go: `python3 $S/snap.py <slug> --scene <id> ...`. `python3 build.py` prints the audit each time.
8. **A meaningful visual change inside the first 3 seconds.** Talking head, then a motion graphic or visual explanation of what is being said, then back to the creator or a split, then the next visual. It must support the narration, not interrupt it. The video also opens on a very subtle zoom in or out (`E.OPEN`).
9. **Something develops every 2-5 seconds for the first 30 seconds.** A graphic where one helps; otherwise a punch-in, a change of composition, a slow reframing or a word of emphasis. Never an irrelevant image to fill a gap.
10. **Then settle into sustainable long-form pacing**: waves of roughly 3-7 scenes a minute with real stretches of just the creator (slow drift on) between them.
11. **Review the image crops.** Every still goes through the face-safe crop (`E.img`, used by every kit component). `python3 $S/08_render.py <slug> --draft`, then `python3 $S/09_review.py <slug>` writes `crops-*.jpg`: each image with the shown area boxed and each detected face marked. Confirm with your own eyes that no face or important subject is cut; detection misses small and turned faces.
12. **Review the final edit** for pacing, continuity, visual quality and natural dialogue: the review sheets, the audit, and the checklist in `references/quality-check.md`. Fix, re-render (only changed chunks re-render), render the master without `--draft` (at the master resolution in **Your setup**), and deliver: show the review sheets (send the files if the app allows it, otherwise give their paths) and the master's path, with what was cut from the dialogue and why, the audit line, the asset list with sources, wording you chose, anything mocked up or unverified, and the open questions (music).
13. **Captions, only if setup asks for them.** `Captions: none` (the pack default): nothing to do. `Captions: srt`: `python3 $S/make_srt.py <slug>` writes a caption file beside the master for uploading to YouTube; read it once for misheard names. See "Captions" below for burned-in captions.

Changing a finished edit: copy `build.py` to `build_vN.py` first, edit, re-render with `--tag vN`. The creator compares versions.

## The decision engine in one screen

Full version in `references/decision-engine.md`. Before adding any edit, answer: what is being communicated; does this moment need a visual at all; what would make it easier to understand; is there a real-world example; would an illustration or a diagram explain it better; should the creator stay visible; split or full; is it important enough for sophisticated motion; has a similar treatment been used recently; can this be said **without repeating the narration as text**.

- **Score every candidate 1-5.** 5 = hook, promise, intro, a major framework, a key example, a surprising statistic, a key conclusion. 4 = new section, comparison, story moment, list, process. 3 = supporting example, extra explanation. 1-2 = filler, transitions, repeated points: leave the creator alone.
- **Spend where it pays.** Full-screen and split go to 4s and 5s. A 3 gets a float. A 1-2 gets nothing.
- **Pace in waves.** Intro high. Major teaching section medium. Personal story or emotional explanation low. Important framework high. Nuance low. Real-world example high. Transition medium. Roughly 6-10 scenes in the first 45 seconds, then about 3-7 a minute averaged, with real stretches of nothing.
- **Show, do not caption.** "Attention becomes trust, trust becomes demand, demand becomes sales" is a `flow`, not a sentence on screen. "Most creators focus on views when they should focus on trust" is VIEWS struck out and replaced by *Trust*, two words.
- **Vary inside one design system.** Leave `variant="auto"` and the kit rotates looks; the audit flags the same component and variant inside 150 seconds, three of the same state in a row, and a text-heavy plan.
- **Frameworks get one map, reused.** Introduce it once (`K.framework` with `times`), come back to the same map with the current stage lit, and pin `K.tracker` (1 2 [3] 4 5) at the top while the creator talks through a stage.
- **Stories get less, not more.** Photos, places, dates, a slow drift. If the delivery carries it, leave the creator on screen.
- **Do not force graphics. Meaningful visual change beats random visual change.** When no graphic genuinely helps, use a punch-in, subtle reframing, the slow drift, a composition change or a word of emphasis. That is always better than an irrelevant image or animation, including in the opening.
- **Punch-ins are motivated and occasional** (`E.punch(a, b, "reason")`): an important statement, a strong opinion, a reveal, a change of thought, an emotional moment, a key takeaway. Start one on a cut where you can. The audit flags them when they bunch up or pass about 1.5 a minute. The strength is a setup answer (@@PUNCH_PERCENT@@%).
- **Long stretches of just the creator get simulated camera movement**: one slow move from 100% towards 103-106% (or the reverse) over the stretch, alternating direction between stretches. Felt, not noticed. Never in and out.

## The default style

These are the pack's defaults. The creator's own values are in **Your setup**; rules in their notes file win over anything here.

- **HyperFrames only.** The page is 1920x1080 at the source frame rate; the master is rendered at the resolution in **Your setup**. The dark background with a soft glow in the accent colour and fine grain sits behind splits and full-screen graphics; the accent colour goes on the focal element only; text in the off-white text colour; small labels in grey.
- **Type:** the main font, bold, for everything. Accent words in the emphasis font and the accent colour (mark them `*like this*`). **Figures are always in the main font**, never the emphasis font (the kit does this for anything containing a digit). Keep text inside graphics modest. If a font cannot be loaded the browser falls back silently: `06_new_project.py` reports it, and a fallback is never shipped.
- **Positive = green `#2FA65A`, negative = red `#B3261E`, every time.** That is a meaning, not a brand colour. The accent colour stays for the neutral focal element.
- **No headline, kicker or sub-line explaining a graphic.** Only text that is part of the graphic (labels, UI text, numbers, list items, name tags). A bottom-centre title over the creator is fine (`K.title`).
- **No em dashes in any on-screen text** (it reads as machine-written). Commas, full stops, or a middle dot.
- **When YouTube is named, show YouTube; a comment or DM is the real notification; a document is the real document.** A real interface beats a text card.
- **A person is named: their real photo or footage, with their name on it.** Look in the proof folder (`@@PROOF_DIR@@`) and the other asset folders from **Your setup** first.
- **Never crop through a face.** Frames take the image's own shape by default. When a layout needs another shape, faces are detected and the crop is placed around the subject; if they cannot fit, the layout changes (smaller, repositioned, another aspect, the whole image on a blurred extension of itself) or a better image is found. Protecting the subject beats fitting the template.
- **Nothing runs off the frame.** Full-screen graphics sit at about 84% (the engine does this). After any size change, pull frames and check the edges.
- **Depth and 3D** follow the setup answer (`@@DEPTH_3D@@`). On (the pack default): cards separating through depth, a frame resting at a slight angle, layers at different distances, always to mean something. Off: the engine keeps every graphic flat (it drops the 3D part of each move and never picks the tilted look), so build custom graphics flat as well.
- **The logo** follows "Where the logo appears" in **Your setup**. The pack default is no watermark: the logo or wordmark appears only where a graphic calls for it (the creator's own channel card, an end card, a "from the brand" moment). In `build.py`, `E.brand_asset("logo")`, `E.brand_asset("wordmark")` and `E.brand_asset("avatar")` return the file to use, or `None` when the creator did not give one: always handle `None` (use the brand name set in the main font, or leave the mark out). Never draw a stand-in logo. If their answer asks for a constant watermark, call `E.watermark()` once in `build.py` (a small mark in one corner for the whole video; it does nothing when no logo was given).
- **Sound: key moments only, far under the voice.** A soft whoosh as a graphic arrives, a pop or tick on a small element landing. Never a sound on every element. Sounds come from the creator's own pack through `sfx_map.json` (made at setup with `scripts/sfx_probe.py`). No pack = the video is delivered without sound effects: say so in the report, do not invent sounds.
- **Music** follows the setup answer: `ask` means ask every time whether, and which track; `pick` means choose from their music folder or favourites and say which. Either way deliver a with-music and a without-music file.

### Captions

The pack default is **no constant subtitles**: this style does not caption the video, and text on screen is emphasis, never a transcript. The setup answer decides:

- `none`: no captions of any kind.
- `srt`: a caption file for YouTube's own caption track (`make_srt.py`), nothing burned in.
- Burned-in captions are not part of this engine (it has no caption track, and a transcript on screen fights the graphics). If the creator asks for them, say so plainly, offer the caption file, and record the request in their notes file rather than improvising a caption layer.

### Defaults this style avoids (change only if the creator asks)

- Random zooms, bounce, spin, whip pans. Motion is a focus pull in, a soft fade out, elements landing just ahead of the word. The only camera moves on the creator are the slow drift and the motivated punch-in.
- The creator inside a card, rounded box or frame in a split.
- Headlines that explain a graphic, sentences of narration repeated as text, constant subtitles.
- A sound on every element; music added without asking (unless their music rule says `pick`).
- A graphic, image or animation placed only to fill time.
- Stock imagery where a specific real example exists.

## Gotchas

- Times in `build.py` are on the cut timeline for the whole video; `snap.py` and the render script translate to chunk time for you. A raw `npx hyperframes snapshot --at` needs chunk-local times (printed by `build.py`).
- `E.w()` fails loudly with the nearby words when a phrase is not found: fix the phrase, never guess a time.
- Hide anything that enters later with `class="h"`; entrances are `fromTo` with `immediateRender:false`, so an element without `h` is visible from the start of its scene.
- `E.punch` needs the creator full screen for its whole length; it may end exactly where a full-screen graphic starts (head, punch, graphic is a good opening).
- Use `E.img(src, w, h, sid=...)` for any still in a custom graphic, never a bare `object-fit:cover`: it is what protects faces and feeds the crop review.
- A float needs room beside the creator: the engine refuses one when there is under 400 px and tells you to use a panel or split.
- GSAP resets the CSS `translate` property on anything it animates: position with a wrapper. Scene CSS is global to the page: keep class names unique. No `//` comments in injected JS.
- SVG lines that draw on need `pathLength="1000"` with `stroke-dasharray:1000;stroke-dashoffset:1000` (the renderer rounds dash offsets otherwise).
- `hyperframes lint` warns `nested_structure_needs_subcomposition` for every scene. That is a Studio display note, not an error; zero errors is the bar.
- Transcription goes through `scripts/stt.py` only. A chat connector's transcription tool usually returns no word timings, and the cut needs them.
- Some ffmpeg builds have no drawtext / subtitle filters: all text is HTML in the composition, and captions are a separate file.
- Variable-frame-rate sources drift: `01_prep.py` warns and prints the fix. HDR sources: tell the creator before rendering.
- A 4K master renders the same 1920x1080 page at twice the density: it takes several times longer and only pays when the source is 4K (`06_new_project.py` says so when it is not). Drafts are always 1080p.
- Face finding uses Apple's Vision framework (`faces.swift`, compiled on first use with `swiftc`): macOS only.
- The engine and kit are copied into each project by `06_new_project.py`. After changing a setup answer and re-running `setup/apply_profile.py`, run `06_new_project.py <slug> --refresh` so an existing project picks the change up.

## What is in the box

- `engine/yt_engine.py` (states, camera glide between states, drift and punch-ins, face-safe crops, chunking, the audit) and `engine/yt_kit.py` (the component library). Both are copied into each project.
- `scripts/` 01-05 the dialogue edit, `stt.py` (the one door to transcription), `faces.swift` (Apple Vision face detection, compiled on first use), 06 scaffold, `plan_check.py`, `find_assets.py`, `get_asset.py`, `snap.py`, 08 render, 09 review, `cut_times.py`, `make_srt.py` (optional caption file), `sfx_probe.py` (maps the creator's sound pack at setup).
- `templates/` starter `build.py`, `content_map.json`, `edit_plan.json`.
- `assets/` GSAP and one open-licence emphasis font. The creator's own fonts, logo, wordmark, profile picture and sound map are added at setup. No commercial fonts, sound packs or music ship with the skill.
- `examples/component-sheet/build.py`: most components declared once, as a reference for structure and API use. Read it before building for the first time; never reuse its wording.
- `setup/` the first-run interview and the script that fills in the answers.

## Related

- HyperFrames builds and renders everything here: `npx hyperframes doctor` checks the install, and `npx hyperframes catalog --query "<look>" --json` finds an effect when a moment wants something the kit lacks.
- In the same pack, if installed: `youtube-clips` turns the finished long-form video into short clips, and `video-to-written-content` turns it into emails and posts.
