#!/usr/bin/env python3
"""__TITLE__ - glass explainer reel.   python3 build.py   (edit THIS file; index.html is generated)
All times are GLOBAL seconds on the cut timeline: take them from cut_words.json / the work dir's edit.txt.
Coordinates are frame pixels (1080x1920): cx = centre, top = top edge. Graphics area: y 380-1190, x 65-1015."""
import os
import glass_engine as E, glass_kit as K

ROOT = os.path.dirname(os.path.abspath(__file__))
E.init(ROOT)
DUR = E.P["dur"]

# ---- 1. modes: full-frame close-up windows; the rest is the panel layout. Put every edge on an edit cut (cut_times.py).
E.full([
    # [3.28, 5.28],
])

# ---- 2. headings / numbered sections: one per point, written on as the speaker starts it, gone when they move on.
# E.heading(0.0, 5.2, "Line One In White", "Line Two With *Emphasis*")
# E.section(9.1, 19.6, "01", "Name Of The Point")

# ---- 3. graphics: one scene per idea. Build each element ON the word that names it; clear it when the speaker moves on.
#         Record where every real asset came from: E.asset("assets/media/x.jpg", "<path or URL it came from>").
# with E.scene(6.0, 12.0) as s:
#     K.person(s, "assets/media/guest.mp4", 300, 420, 560, t=6.4, tag="Guest name", origin="<where the file came from>")
#     K.ytchannel(s, "Channel Name", "@channelhandle", 740, 470, t=7.2, avatar="assets/media/channel.jpg", count=(0, 100000, 8.0))
# with E.scene(0.0, 5.2) as s:
#     a = s.node(540, 480, t=0.6, icon="?")
#     n = s.box("New\nConcept", 200, 900, t=1.4)
#     x = s.box("Existing\nConcept", 880, 900, t=2.2)
#     s.link((540, 545), (200, 900), t=1.2); s.link((540, 545), (880, 900), t=2.0)
#     s.link((300, 950), (780, 950), t=2.8, dashed=True, dot=False)
#     s.box("Relating To", 540, 918, t=3.0, size=44)

E.build()
