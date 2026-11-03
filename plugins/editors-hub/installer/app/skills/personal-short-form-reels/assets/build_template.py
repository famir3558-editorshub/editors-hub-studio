#!/usr/bin/env python3
"""__TITLE__ - Personal Short Form reel.   python3 build.py
Edit THIS file, never the generated compositions/*.html or index.html. All times are GLOBAL seconds on the cut; frames are frames of the cut.
Worked example: ~/.claude/skills/personal-short-form-reels/examples/fear-of-failure/build.py"""
import os
import reel_engine as E, kit as K, psf as P

ROOT = os.path.dirname(os.path.abspath(__file__))
DUR = __DUR__
# ---- the plan, in frames of the cut (scripts/cut_times.py lists the edit cuts and how visible each jump is).
# Every big cut is hidden: a B-roll or split window STARTS or ENDS on it. Use P.sw(frame) for every window edge.
FACE = [[0, DUR]]      # the creator full screen           e.g. [[0, P.sw(77)], [P.sw(131), P.sw(163)], ...]
FULL = []              # B-roll over the whole frame e.g. [[P.sw(77), P.sw(131)], [P.sw(163), P.sw(261)]]
# anything in neither list is a SPLIT window (screen recording on top, the creator on the bottom)
P.setup(ROOT, DUR, FACE, FULL, "__TITLE__", emph=set(), keep=set())

# P.broll("b01", a, b, [("assets/broll/b1.mp4", start_frame, n_frames), ...])
# P.screen("s01", a, b, [("assets/screen/s1.mp4", start_frame, n_frames)], zooms=[(t, 1.8, ox, oy), (t2, 1)])
# K.hook("Line one", "line two", out)                       # opening hook, on screen from frame 1
# P.comments([(user, "commented: ...", t), ...], out)       # Instagram notifications below the caption
# P.logos("lg", [("assets/logos/brand.png", t), ...], out)  # real logos on the word that names the brand
# K.OF.append('<div id="g1" style="position:absolute;...;opacity:0">...</div>'); K.ojs("opop('#g1', t); oout('#g1', out);")

P.finish()
