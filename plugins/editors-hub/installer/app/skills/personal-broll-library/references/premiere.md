# Getting the plan into the edit: Premiere Pro and other editing apps

The creator's editing app is **@@EDITING_APP@@** (usual sequence: @@SEQUENCE_FPS@@ fps, @@SEQUENCE_FORMAT@@).
The sections below are written for Premiere Pro, where the export was built and checked. "Other editing
apps" further down says honestly what works elsewhere.

## What works today

### 1. FCP7 XML import (reliable, recommended)

`broll export <plan> --to xml --fps 25 --width 1920 --height 1080`

In Premiere: **File > Import** the `.xml`. Premiere creates a new sequence named
"<project> - Personal B-roll" and imports any media it needs:

- V1 / A1(+A2): the main video (only if the plan had `main_video`)
- V2: each B-roll clip trimmed to the chosen section, video only (the B-roll's own audio is not
  placed, so dialogue is preserved)
- Markers: one per placement (what is said) and one per gap ("B-roll gap (no personal clip)")

To bring the B-roll into the real edit: select everything on V2 in the imported sequence, copy,
open the real sequence, target V2 (or an empty track), put the playhead at 00:00:00:00, paste.
Times line up because both start at zero. If the real sequence does not start at zero or the
main video sits later on the timeline, set `at` values relative to the real sequence instead.

Match `--fps` and frame size to the real sequence (the CLI falls back to 25 fps and 1920x1080 when
neither the command nor the plan gives them, so always pass them; 23.976/29.97/59.94 are handled as
NTSC). Vertical edits: `--width 1080 --height 1920`. If you do not know the sequence's frame rate,
read it from the main video with ffprobe or ask.

If Premiere shows media offline after import, the footage drive is not mounted at the path in the
index: plug it in, or `broll relink`, re-export.

### 2. ExtendScript placer (experimental)

`broll export <plan> --to jsx` writes a self-contained `.jsx`. Run it inside Premiere with the
target sequence open (VS Code + the Adobe "ExtendScript Debugger" extension, target "Adobe
Premiere Pro"). It:

1. clones the active sequence (the original is never edited) and renames the clone "+ B-roll";
2. imports each source file once into the bin "Personal B-roll (auto)";
3. creates a **video-only subclip** for each placement's exact section (`createSubClip`, takeAudio=0);
4. `overwriteClip`s it onto the target track (V2 by default) at the placement time;
5. reports what was placed and what was skipped.

It needs the target track to exist. It has not been verified against the creator's Premiere version.
Adobe is moving Premiere scripting from ExtendScript to UXP, so newer versions may not run it;
the XML route does not depend on scripting. Treat the first run as a test on a project copy.

## Other editing apps

The plan JSON and the `.csv` sheet are app-neutral. The `.xml` is FCP7 XML (xmeml version 4), an older
interchange format that some apps still read. Nothing below has been run by this skill inside those
apps: say that, and treat the first import as a test on a copy of the project.

- **DaVinci Resolve**: File > Import > Timeline, choose the `.xml` (Resolve lists "Final Cut Pro 7 XML"
  among its timeline formats). Expect a new timeline with the main video on V1 and B-roll on V2. Check
  three things after import: the clips sit at the right times, the B-roll has no audio, and the
  timeline frame rate matches (Resolve fixes a project's frame rate once media is in it, so the export
  `--fps` must match the project). If media shows offline, relink to the footage folder. Markers may
  not all survive; the `.csv` has the same information.
- **Final Cut Pro**: reads FCPXML, not FCP7 XML, so the `.xml` does not import directly. Routes that
  can work: a converter app (SendToX is the usual one), or importing the `.xml` into the free DaVinci
  Resolve and exporting an FCPXML from there. Each conversion can drop markers or shift media links.
  When the creator has no converter, give them the `.csv` and offer to walk through the placements.
- **CapCut**: no XML timeline import. Use the `.csv`: each row is one clip, the section to use
  (`source_in` to `source_out`) and where it goes (`timeline_in`). For more than a dozen placements,
  suggest importing just the listed clips first, then placing them in order.
- **Anything else**: if its import menu lists "Final Cut Pro 7 XML" or "XML (xmeml)", try the `.xml`
  on a copy; otherwise the `.csv`.

The `.jsx` script is Premiere Pro only.

## The automation roadmap (Premiere Pro)

Everything above is driven by the same plan JSON, so any future integration only needs a new
"executor" for it. When a Premiere automation tool becomes available in a session (a Premiere
MCP server, a UXP plugin with a local bridge, or computer use on the creator's computer):

1. **Read the timeline**: get sequence name, fps, frame size, track count, and the main clip's
   position; get a transcript (Premiere's own captions or an SRT export).
2. **Plan**: Workflow C exactly as in SKILL.md -> plan JSON -> `plan-check`.
3. **Confirm with the creator** before touching the project: show the plan table.
4. **Execute non-destructively**: duplicate the sequence (or work on an empty track they name),
   import media if needed, place video-only sections on the empty track above the main footage,
   trim to duration. Never ripple, delete, or move existing clips. Never change audio tracks.
5. **Verify** by reading the timeline back and comparing to the plan; report mismatches.
6. Only then say what was placed, with the sequence name. If any step could not be done, say
   which and fall back to the XML export.

Computer use (clicking in Premiere) is the last resort: it is slow and fragile for precise
timing. Prefer XML import plus copy-paste for anything over a couple of clips.
