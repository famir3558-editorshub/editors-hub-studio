#!/usr/bin/env python3
# Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.
"""Smoke Test - explainer panel reel.   python3 build.py   (edit THIS file; index.html is generated)
All times are GLOBAL seconds on the cut timeline: take them from cut_words.json / the work dir's edit.txt.
Coordinates are frame pixels (1080x1920): cx = centre, top = top edge. Graphics area: y 380-1190, x 65-1015."""
import os
import panel_engine as E

ROOT = os.path.dirname(os.path.abspath(__file__))
E.init(ROOT)
DUR = E.P["dur"]


E.full([[5.82, 8.06]])
E.heading(0.0, 5.7, "Show Them What", "You've *Already Done*")
E.section(10.82, DUR, "02", "Why This?")
with E.scene(0.0, 5.8) as s:
    n = s.node(540, 480, t=1.2, icon="A")
    a = s.box("Strategist", 250, 760, t=2.1)
    b = s.box("The\nChannel", 830, 748, t=3.0)
    s.link((540, 545), (250, 760), t=1.9); s.link((540, 545), (830, 748), t=2.8)
    s.link((390, 790), (735, 790), t=3.3, dashed=True, dot=False)
    c = s.count(540, 930, 0, 400000, t=4.2, dur=0.9, color="var(--o)")
    s.chip("subscribers", 540, 1070, t=4.9)
    s.hot(b, 3.6)
with E.scene(8.06, 10.8) as s:
    s.term("Someone They Trust", 540, 520, t=8.6)
    s.typed("New Script", "What's something else that works in a similar way?", 540, 660, 620, 380, t=9.2, dur=1.3)
with E.scene(10.82, DUR) as s:
    s.list(["Why You", "Why This", "Why Now"], 420, [10.9, 11.4, 99], show_at=10.82)

E.build()
