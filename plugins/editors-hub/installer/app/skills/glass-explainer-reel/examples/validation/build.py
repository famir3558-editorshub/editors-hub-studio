#!/usr/bin/env python3
"""Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.

A short validation build for the glass explainer reel: a real-world example scene (the creator -> a real channel -> a
real person), an explainer scene (boxes, a drawn connection, the active item lighting up) and a numbered section.
All times are GLOBAL seconds on the cut timeline (cut_words.json / the work dir's edit.txt).
Coordinates are frame pixels (1080x1920): cx = centre, top = top edge. Graphics area: y 380-1190, x 65-1015.

The files named below (assets/media/...) are placeholders for the creator's own material: the build needs them to exist.

Example script this was timed against: "With what you've done. For me, it's the channel I helped grow from zero to over
400,000 subscribers. | If you don't have any big results yet, borrow some. | Show them that someone they already trust has
done it. The second component is why this?"
"""
import os
import glass_engine as E, glass_kit as K

ROOT = os.path.dirname(os.path.abspath(__file__))
E.init(ROOT)
DUR = E.P["dur"]

# ---- 1. modes: the close-up carries the direct line ("If you don't have any big results yet, borrow some.")
E.full([[5.82, 8.06]])

# ---- 2. headings
E.heading(0.0, 5.7, "Show Them What", "You've *Already Done*")
E.heading(8.06, 10.66, "No Results Yet?", "*Borrow* Some")
E.section(10.82, DUR, "02", "Why This?")

# ---- 3a. REAL-WORLD EXAMPLE: the creator -> the real channel -> the real person. Each part lands on the word that names it.
E.asset("assets/media/channel.jpg", "the channel's own public profile picture, saved from its page (URL here)")
E.asset("assets/media/guest.mp4", "a clip the creator supplied (path or URL here)")
with E.scene(0.0, 5.8) as s:
    me = s.node(540, 462, t=1.3, r=66, img=K.ME)                                   # "For ME": the creator's profile picture
    s.chip("Strategist", 540, 548, t=2.1)                                          # "the STRATEGIST"
    s.link((540, 600), (300, 690), t=2.72, dot=False)
    ch = K.ytchannel(s, "Channel Name", "@channelhandle", 300, 690, t=2.88, w=440, h=430, fs=25,
                     avatar="assets/media/channel.jpg", count=(0, 400000, 3.7, 1.3))   # "the CHANNEL" ... "from ZERO to over 400,000"
    s.hot(me, 3.7, on=False)                                                       # one accent focal point: it moves to the number
    s.link((540, 600), (790, 690), t=4.95, dot=False)
    K.person(s, "assets/media/guest.mp4", 790, 690, 430, t=5.14, tag="Guest name",  # "SUBSCRIBERS": the real person, whole clip, not cropped
             origin="a clip the creator supplied")

# ---- 3b. EXPLAINER SCENE: borrowed trust. Boxes, a drawn connection, the active item lights with a sweep.
with E.scene(8.06, 10.66) as s:
    v = s.box("Your\nViewer", 540, 410, t=8.3, size=42)                            # "show THEM"
    o = s.box("Someone They\nAlready Trust", 770, 720, t=8.68, size=42)            # "SOMEONE else"
    s.link((600, 520), (770, 720), t=9.3)                                          # "ALREADY trust": the line the viewer already has
    s.chip("Trust", 725, 590, t=9.74)
    s.hot(o, 9.74, sound=True)                                                     # "TRUST": the key moment of this scene
    y = s.box("You", 300, 745, t=10.1, size=42)                                    # "has DONE it": you stand next to their result
    s.link((530, 772), (372, 772), t=10.38, dashed=True, dot=False)

# ---- 3c. numbered section: the list walks on
with E.scene(10.82, DUR) as s:
    s.list(["Why You", "Why This", "Why Now"], 430, [10.9, 11.96], show_at=10.82)

E.build()
