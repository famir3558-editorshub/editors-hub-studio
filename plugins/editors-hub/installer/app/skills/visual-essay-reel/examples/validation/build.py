#!/usr/bin/env python3
"""Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.
A short test build: collage opening with a title, a proof clip with a counting statistic beside it, a side-by-side pair,
a backdrop behind the presenter, then a straight-to-camera close. Every time is GLOBAL seconds on the cut timeline.
A box is (cx, top, w, h) in frame pixels (1080x1920). The evidence wall is x 65-1015, y 200-1060."""
import os
import essay_engine as E

ROOT = os.path.dirname(os.path.abspath(__file__))
E.init(ROOT)
DUR = E.P["dur"]

E.glow(0, "bottom")
E.title(0.0, 1.12, "Borrowed *Proof*", "When You Have No Results Yet")
E.collage([f"assets/media/cover0{k}.jpg" for k in range(1, 7)], 0.0, 1.12, cols=2, tint=0.55, dim=0.35, origin="<path or URL it came from>")
with E.scene(1.14, 5.82) as s:
    a, b = E.slot("hero+side")
    s.card("assets/media/proof_clip.mp4", a, t=2.1, frame="white", origin="<path or URL it came from>", source="Where the clip is from")
    s.stat("{}", "subscribers", (790, 330, 400, 500), t=4.2, count=(0, 400000), size=92)
E.glow(5.82, "low-left")
with E.scene(5.82, 8.06) as s:
    a, b = E.slot("pair")
    s.card("assets/media/theirs.jpg", a, t=5.82, how="cut", label="Theirs", origin="<path or URL it came from>")
    s.card("assets/media/yours.jpg", b, t=6.9, label="Yours", origin="<path or URL it came from>")
E.backdrop("assets/media/place.jpg", 8.06, 10.82, mode="top", tint=0.0, dim=0.1, origin="<path or URL it came from>")
E.me(8.06, "left")
E.me(10.82, "close"); E.solo(10.82, DUR); E.glow(10.82, "behind", 0.8)

E.build()
