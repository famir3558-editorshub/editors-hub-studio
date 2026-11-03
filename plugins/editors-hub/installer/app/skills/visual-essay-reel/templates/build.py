#!/usr/bin/env python3
"""__TITLE__ - visual essay reel.   python3 build.py   (edit THIS file; index.html is generated)
All times are GLOBAL seconds on the cut timeline: take them from cut_words.json / the work dir's edit.txt.
A box is (cx, top, w, h) in frame pixels (1080x1920). The evidence wall is x 65-1015, y 200-1060; the presenter fills the frame below it.
Every visual needs a reason: the word at its time names it, proves it or is explained by it."""
import os
import essay_engine as E

ROOT = os.path.dirname(os.path.abspath(__file__))
E.init(ROOT)
DUR = E.P["dur"]

# ---- 1. light: where the accent colour enters the black. One setting per chapter of the script, changed on a cut.
E.glow(0, E.GLOW_DEFAULT)
# E.glow(14.2, "low-left")

# ---- 2. the wall: one scene per idea, each visual ON the word that names it. Record where every asset came from.
# E.title(0.0, 2.4, "Borrowed *Proof*", "How To Sell Without Results")
# with E.scene(0.0, 2.4) as s:
#     s.card("assets/media/tweet.png", E.slot("hero"), t=0.0, how="cut", origin="https://x.com/<handle>/status/<id>")
# with E.scene(2.4, 6.0) as s:                                   # comparison: side by side, second one on its word
#     a, b = E.slot("pair")
#     s.card("assets/media/before.jpg", a, t=2.4, label="Before", origin="<path or URL it came from>")
#     s.card("assets/media/after.jpg", b, t=3.9, label="After", origin="<path or URL it came from>")
# with E.scene(6.0, 9.2) as s:                                   # statistic: only when there is no page to show for it
#     s.stat("{}%", "more likely to buy", E.slot("hero"), t=6.3, count=(0, 55), source="Journal of Consumer Psychology")
# E.backdrop("assets/media/street.mp4", 9.2, 12.0, mode="top", origin="<path or URL it came from>")      # story -> b-roll behind the presenter

# ---- 3. the presenter is the anchor. Move them only when the composition needs it; punch in only on a line that earns it.
# E.me(12.0, "corner-left"); E.backdrop("assets/media/billboard.jpg", 12.0, 15.0, mode="bottom", origin="...")
# E.me(15.0, "center"); E.punch(17.3, 1.1, hold=1.4)
# E.solo(17.3, 20.0)                                             # straight to camera: the wall is empty on purpose

E.build()
