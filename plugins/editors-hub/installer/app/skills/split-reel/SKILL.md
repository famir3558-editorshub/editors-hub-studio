---
name: split-reel
description: Turn an already-cut 16:9 talking-head video into a split-screen 9:16 reel. The creator's face is cropped into the top half, and custom animations that explain what they are saying play in the black bottom half, in a clean diagram style (kicker, CAPS headline with one glowing keyword, one simple diagram per beat). Optional full-screen sections show just the speaker with no graphics, then hard-cut back to the split. Every section animation is also delivered as its own file. Use whenever the creator hands over a cut (or a video plus "do the split screen", "face on top, animations at the bottom", "9:16 split reel"), asks for "the split reel" or "animations for each section", or says which parts should be "full screen". Not for 16:9 side cards, cut-out speaker edits, or plain captions.
---

# Split reel (9:16: face on top, animations below)

## Step 0: setup gate (every session, before anything else)

Run `python3 ~/.claude/skills/split-reel/setup/apply_profile.py --status`.

- `"configured": false` -> read `setup/SETUP.md` and run the setup interview first. Do not start the task, and do
  not infer the answers from memory, CLAUDE.md or this file's prose. Asking is the feature.
- `"configured": true` -> read `~/.claude/creator-profile/profile.json` and, if it exists,
  `~/.claude/creator-profile/notes/split-reel.md`. Rules under `## Style overrides` in that notes file win over the
  defaults written below.

"redo my setup" re-runs the interview at any time.

## Your setup

Filled in by setup. To change a line, change the answer (`setup/SETUP.md`), never this text.

| | |
|---|---|
| Creator | @@CREATOR_NAME@@ · @@BRAND_NAME@@ · @@HANDLE@@ |
| What they teach, and to whom | @@NICHE@@ |
| Colours | accent @@ACCENT@@ (@@ACCENT_NAME@@) · text on the accent @@ON_ACCENT@@ · chips and light text @@PAPER@@ · small labels @@GREY@@ (the panel base is always black, so it blends into the black half of the composite) |
| Fonts | main: @@FONT_MAIN_NAME@@ · emphasis: @@FONT_ACCENT_NAME@@ |
| Transcriber | @@TRANSCRIBER@@ |
| Footage drive | @@MEDIA_DRIVE@@ |
| Finished reels go | @@OUTPUT_RULE@@ |
| Folders | working files `@@WORK_ROOT@@` · Remotion project (the kit) `@@PROJECTS_ROOT@@/split-reel-kit` |
| Real material (proof) | @@PROOF_DIR@@ |
| Other folders to search for real assets | @@ASSET_DIRS@@ |
| Real assets from the web | @@WEB_ASSETS@@ |
| Never show | @@NEVER_SHOW@@ |
| Full-screen windows when none are named | @@FULLSCREEN_RULE@@ |
| Usual call to action | @@CTA_DEFAULT@@ |
| Name on the call-to-action panel | @@CTA_SIGNATURE@@ |
| Silence tightening (only when asked) | gaps longer than @@TIGHTEN_GAP@@ s |
| Preview before the final | @@PREVIEW_FIRST@@ |
| How far to go alone | @@WORK_RULE@@ |

## Preview first (applies to every render this skill produces)

Do not render the full-quality final first. Build a fast 720p preview, show it to the creator, wait for a yes, apply
their notes, and only then render the final:

1. Render the panels (`render_scenes.sh`) and composite with `python3 composite.py <reel.json> --preview`. That writes
   `<Title> - 9x16 Reel - PREVIEW.mp4` (720x1280, fast encode) next to the final's name.
2. Give the creator the file path and a scene table, and ask them to watch it and give timestamped notes.
3. Apply the notes (they usually mean editing a scene's cue times or text, re-rendering only those scenes, and
   compositing again), re-preview, and render the final (`composite.py` without `--preview`) only once they approve.

If the setup answer for "Preview before the final" starts with `no`, still render the preview for your own frame checks but go
straight to the final without waiting. If the creator uses a review tool of their own, register the preview there.

## What you deliver (in `<out_dir>`)

1. `Animations/NN - Name.mp4`: one 1080x960 panel per section, on black. Each is its own file.
2. `<Title> - 9x16 Reel.mp4`: 1080x1920. The creator is in the top half (a 9:8 crop of the cut), and the panels play
   in the lower half. Any `fullscreen` windows are a 9:16 crop of just them.

**Division of labour:** the creator makes the cuts (takes, flubs, silences). You do not re-cut unless they ask. If
they ask for tighter silences, run `scripts/tighten.py` (default gap is the `tighten_gap` answer in **Your setup**).
Never drop or reorder their content yourself.

## Pipeline

All scripts are in `~/.claude/skills/split-reel/scripts/`. Panels are Remotion compositions in a small Remotion
project, the kit, at `@@PROJECTS_ROOT@@/split-reel-kit`. `new.sh` creates it from the skill's `kit/` folder the first
time (it runs `npm install` there, a few minutes, needs Node 22 and a network connection) and refreshes the shared
files (`src/brand.js`, `src/splitReel/kit.tsx`, `register.tsx`) from the skill on every run, so brand changes made in
setup reach the panels. Put one-off pieces in the reel's own `<PREFIX>.tsx`, not in the kit files. Remotion itself is
run through `npx`; nothing is installed globally.

### 1. Set up
```bash
S=~/.claude/skills/split-reel/scripts
$S/new.sh <folder> <PREFIX> "<Title>" "<cut.mp4>" "<out_dir>"
#   e.g. new.sh myReel MR "My Reel" ".../cut.mp4" ".../My Reel - Edit"
```
- This creates `src/<folder>/reel.json` plus `<PREFIX>.tsx` in the kit, and registers `<PREFIX>-<sceneid>` comps in
  `src/Root.tsx`. The crops in `reel.json` are worked out from the cut's size (centred, full height for the 9:16
  crop): a starting point, see step 3.
- Keep `out_dir` next to the source, on the footage drive if there is one (`@@MEDIA_DRIVE@@`), and keep it off a
  nearly full internal disk. Output location rule: `@@OUTPUT_RULE@@`.
- `reel.json` is the single source of truth. The scenes import it, and `composite.py` reads it. `examples/reel.example.json`
  shows the shape.

### 2. Transcribe
```bash
python3 $S/transcribe.py "<cut.mp4>" <work_dir>      # work_dir under @@WORK_ROOT@@
```
- Produces `words.json` and `readable.txt`, using the transcriber chosen at setup (`stt.py`). Run it in the background
  for long cuts.
- Times are on the creator's cut, which is the same clock as the panels.
- Fix obvious recognition slips when you read it: product names, framework names, the call-to-action keyword. Check
  those against what the creator says, not against the transcript.

### 3. Framing
```bash
$S/stills.sh "<cut.mp4>" @@WORK_ROOT@@/split-reel/frame.jpg <reel.json>
```
- Orange box = top-half crop (9:8). Cyan box = full-screen crop (9:16).
- The defaults assume the speaker is roughly centred. Always look at the four stills and adjust:
  - The top crop should keep the eyes about 40% of the way down the top half, below the platform's top bar, with a
    little headroom, and not clip the head.
  - The full-screen crop should be centred on the face. If the cut is already full height, no zoom happens.
- If the camera moved or the speaker sits off-centre, shift x so the face is centred, and write the values into
  `reel.json` (`top_crop: [w,h,x,y]`, `fs_crop: [w,h,x,y]`, both in source pixels).
- A bad frame (head cut off, speaker pushed to one edge) is the creator's call: say what you see, offer the nearest
  crop that works, and push the graphics higher or lower rather than rescaling the footage.

### 4. Plan the sections
- Read `readable.txt` and split it at idea changes. Typically: hook, proof, framework intro, one scene per part,
  promise, call to action. Usually 6 to 9 scenes, each about 3 to 16 s.
- Write `scenes: [{id:"01-Hook", start, end}]` with ids `NN-Name`. Scenes must tile the timeline (each `end` equals the
  next `start`).
- **Full screen:** the creator says which parts, e.g. "full screen from 'if you do this' to 'ever'". Convert them with
  `$S/find.py <work>/words.json "if you do this" "ever"` and add them to `fullscreen: [[a,b]]`.
  - If they only say "some full-screen bits, you pick" (or give no instruction and the setup answer is to pick), choose
    1 to 3 short, punchy moments: the hook line, the promise, or an emotional or personal line. Not the teaching parts,
    because those need the diagram. Tell them which ones you picked. If the setup answer is `none unless I say`, add
    none.
  - Full-screen windows are **hard cuts**, in and out.
  - **The panel scene that follows a full-screen window must have something on screen in its first frame.** Start its
    first beat at, or 0.1 s after, the window's end. Otherwise the reel cuts back to an empty black half.
  - A scene that is fully covered by full screen still needs a panel file, because it is delivered as its own file.
    Make it a strong standalone graphic.
- Look for the creator's own framework names and visuals first: their proof folder (`@@PROOF_DIR@@`), the extra asset
  folders (`@@ASSET_DIRS@@`), and anything they pasted into the chat. Use their named frameworks verbatim, with
  whatever trademark or capitalisation they use.

### 5. Build the panels (`src/<folder>/<PREFIX>.tsx` in the kit)
One component per scene, in `reel.json` order. Each scene does:
```tsx
const t = useT(SCENES[i].from);
```
**`t` is in seconds on the cut**, so paste word times straight from `words.json`: "the headline word lands on the
word they say". `examples/WorkedExample.tsx` shows a hook scene and a two-phase scene end to end (structure only:
never reuse its wording).

Design language (a diagram-carousel look adapted to a 1080x960 panel):
- `Stage` = black base, grain, an accent light leak and a black top fade. **Black so it blends into the bottom half.**
  `Stage` also loads the creator's fonts into the render.
- Top of the panel: a `Kicker` (emphasis font, accent colour) above a CAPS `Head` (main font bold, -0.045em tracking,
  1 to 2 glowing accent words).
  - Headlines are **centred**.
  - Per-section pattern: a kicker like "part one", a giant one-word head, and a sub-line with one emphasis-font phrase
    in the accent colour.
- One diagram per beat, building on their words. Kit pieces:
  - `glass` / `hot` cards
  - dashed accent boxes
  - light chips (`PAPER`) around a solid accent core (mind map)
  - `Note` (Caveat handwriting plus a drawn accent arrow; use `until` to fade it before the next beat)
  - `Radar` (three sectors, labels are yours, sweep, blips, active sector), `Wave` (call waveform), `Bubble` (comment)
  - iOS / app mocks (notes list, chat, week strip), set in the system UI stack `SF`
  - number counters
- **Multi-beat scenes:** crossfade between phases A, B, C with `easeInOut(prog(...))`, and keep the kicker and head as
  the anchor. Swap the kicker text when the meaning flips (e.g. "the best one" to "not just theirs").
- Motion:
  - Entrances use `In`: rise, fade and a blur that resolves, about 0.35 to 0.45 s, starting **on** the spoken word.
  - Use `back()` for a pop on chips and stamps.
  - Use continuous motion where it makes sense: a radar sweep, a list that keeps filling, a thumbnail strip scrolling.
  - Nothing should sit still and empty for more than about 1.5 s.
- **Real assets over mock-ups:** use the creator's real channels, thumbnails, reel covers and client screenshots from
  `@@PROOF_DIR@@` and `@@ASSET_DIRS@@`. Real thumbnails of a YouTube channel can be fetched (`yt-dlp --flat-playlist
  --print "%(id)s"`, then `i.ytimg.com/vi/<id>/mqdefault.jpg`) when the web-assets answer is a yes. Put new assets in
  `public/<folder>/` in the kit and reference them with `staticFile("<folder>/name.png")`. Never show anything under
  "Never show". List every real asset and its source in the report.
- Brand rules (defaults of this style):
  - The accent colour only on keywords, single filled chips, the core node, and the call to action.
  - **Figures and currency are always set in the main font, never in the emphasis font.**
  - The creator's name (faint, emphasis font) goes on the call-to-action panel only, when "Name on the call-to-action
    panel" is yes.
- Call to action: show what is being offered (a mock of the thing), then the action the creator usually asks for
  (see **Your setup**: for a comment keyword that is COMMENT plus a huge emphasis-font "KEYWORD" and its sub-line).
  Keep the keyword verbatim from their script.

### 6. QA the panels
Render a still at the end of every beat:
```bash
$S/qa_stills.sh <folder> <PREFIX> @@WORK_ROOT@@/split-reel/qa.jpg "01-Hook:85" "04-Part:120" ...
```
Look at every tile, and fix:
- overlaps, especially handwritten notes left over from an earlier phase (use `until`)
- arrows crossing text
- a headline wrapping differently from the planned breaks
- an empty or half-built panel at a scene's last frame
- fonts that fell back to defaults (check against the fonts in **Your setup**)

### 7. Render and composite
```bash
$S/render_scenes.sh <folder> <PREFIX>            # all panels -> <out_dir>/Animations (or list ids to re-render some)
python3 $S/composite.py <kit>/src/<folder>/reel.json --preview     # the 720p preview first (see "Preview first")
python3 $S/composite.py <kit>/src/<folder>/reel.json               # the final, after approval
$S/reel_sheet.sh "<out_dir>/<Title> - 9x16 Reel.mp4" @@WORK_ROOT@@/split-reel/reel.jpg 2 8 20 ...   # include +-0.1 s around every full-screen edge
```
- `<kit>` is `@@PROJECTS_ROOT@@/split-reel-kit`.
- Panels: H.264 CRF 14, about 20 s each.
- `composite.py`:
  - overlays each panel at its `start` on a black 1080x960 base
  - vstacks it under the top crop
  - overlays the full-screen crop during the `fullscreen` windows (frame-snapped)
  - uses the creator's audio untouched (AAC 320k)
- About 3 min for a 1-minute reel at full quality; the preview is much faster.

### 8. Deliver
- Give the creator the path of the reel (and `Animations/`). Large files may not preview in a chat window, so give the
  folder as well.
- Give a scene table: file, what it shows, the words it is timed to.
- List the full-screen windows.
- Flag invented mock text so the creator can swap it: usernames, comment and call quotes, view counts, skill or
  product names, "12 ideas extracted"-type numbers.
- List every real asset used and where it came from.

## Gotchas
- **Fractional fps works in Remotion** (24000/1001). Use the source's rate so panel frames line up with the cut.
- `ffmpeg concat` lists resolve relative to the list file, so `composite.py` uses absolute paths.
- Remotion `defaultProps` merge into props, so these scenes take none and read `reel.json` instead.
- `rm` with an unset variable is blocked by some harnesses, so use literal paths or `"${VAR:?}"`.
- Long renders: if a command might pass 2 min, run it in the background and wait with an until-loop, not with `sleep`.
- After a refactor, a pixel-diff of one still against the approved QA still confirms nothing changed.
- The first Remotion bundle downloads a headless browser if it is not cached; allow a minute.
- `tighten.py` re-encodes with `hevc_videotoolbox` (macOS hardware encoder) and needs `numpy` and `soundfile`.

## Defaults this style avoids (change only if the creator asks)
- Re-cutting or reordering the creator's content.
- Left-aligned or top-left headlines: they are centred.
- Figures or currency in the emphasis font.
- Accent colour used as decoration instead of on the keyword.
- Full-screen sections over the teaching parts that need the diagram.
- A panel that is empty on its first frame after a full-screen window.

## Files
- `kit/`: the Remotion project template (`src/splitReel/kit.tsx` primitives, `register.tsx`, `src/brand.js` filled from the profile).
- `templates/Reel.tsx`: the scene skeleton `new.sh` copies into a reel.
- `examples/`: `reel.example.json` and `WorkedExample.tsx` (structure only).
- `scripts/`: `new.sh`, `transcribe.py`, `stt.py`, `find.py`, `stills.sh`, `qa_stills.sh`, `render_scenes.sh`, `composite.py`, `reel_sheet.sh`, `tighten.py`, `kit_env.sh`.
- `assets/fonts/`: the creator's fonts, copied in by setup (an open-licence italic serif ships as the default emphasis font).
- `setup/`: the first-run interview.

## Related
- `glass-explainer-reel`: another panel-over-speaker layout, if the creator prefers glass cards over the half-and-half split.
- `video-to-written-content`, `coaching-call-clips`: upstream skills that produce the cuts this one is built on.
