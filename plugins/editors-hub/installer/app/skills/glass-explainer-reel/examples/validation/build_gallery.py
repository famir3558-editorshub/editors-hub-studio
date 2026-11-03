#!/usr/bin/env python3
"""Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.

Component gallery - the kit's real interfaces and bigger graphics inside the panel layout's graphics area.
NOT a real edit: it runs over the test footage with made-up timings, only to check that every component fits, reads
and moves correctly. python3 build_gallery.py  (overwrites index.html; run build.py afterwards to restore the reel)."""
import os
import glass_engine as E, glass_kit as K
ROOT = os.path.dirname(os.path.abspath(__file__)); E.init(ROOT); DUR = E.P["dur"]
# a reel cover to show being saved: the first image in assets/reels (the creator's own covers, copied in at setup) or assets/media;
# with none, a plain grey card is drawn so the gallery still builds.
COVER, COVER_ORIGIN = None, "the creator's own reel cover"
for d in ("assets/reels", "assets/media"):
    p = os.path.join(ROOT, d)
    if os.path.isdir(p):
        for f in sorted(os.listdir(p)):
            if f.lower().endswith((".jpg", ".jpeg", ".png")): COVER = f"{d}/{f}"; break
    if COVER: break
if not COVER:
    from PIL import Image
    os.makedirs(os.path.join(ROOT, "assets/media"), exist_ok=True); COVER = "assets/media/_gallery_cover.jpg"
    Image.new("RGB", (540, 960), (58, 58, 60)).save(os.path.join(ROOT, COVER)); COVER_ORIGIN = "plain grey stand-in (no reel cover supplied)"
E.full([])
E.heading(0.0, 2.4, "They Tell You", "It *Worked*")
E.heading(2.5, 5.0, "Everything Lives", "In *One Doc*")
E.heading(5.1, 7.6, "Make It Worth", "*Saving*")
E.heading(7.7, 10.2, "Retention", "Tells The *Truth*")
E.heading(10.3, DUR, "A Tip Versus", "A *System*")
with E.scene(0.0, 2.4) as s:
    K.notifs(s, [("Instagram", "viewer_one commented: METHOD", 0.3, False), ("Instagram", "viewer_two commented: sent you a DM", 0.9, False), ("Your Name", "Just sent it over. Check your DMs", 1.5, True)], top=430)
with E.scene(2.5, 5.0) as s:
    K.gdoc(s, "The Method", ["Why You", "Why This", "Why Now"], 420, t=2.7, hl=[(0, 3.4), (1, 4.2)])
with E.scene(5.1, 7.6) as s:
    K.saved(s, COVER, 540, 410, t=5.3, t_tap=6.2, name="creator", caption="Stop losing viewers in the first 5 seconds", origin=COVER_ORIGIN)
with E.scene(7.7, 10.2) as s:
    K.graph(s, [(0, 40), (150, 90), (330, 120), (520, 150), (740, 170)], 540, 430, t=8.2, dur=1.3, label="viewers still watching", ghost=[(0, 40), (120, 200), (300, 290), (740, 320)], marks=[(330, 120, 9.3)])
    s.count(540, 900, 0, 72, t=9.3, dur=0.7, suffix="%", size=110, color="var(--o)")
    s.chip("watched to the end", 540, 1030, t=9.9)
with E.scene(10.3, DUR) as s:
    K.versus(s, ("Before", "Another\ntip"), ("After", "The one they\nneed *now*"), 440, t_a=10.5, t_b=11.2, t_hot=11.9)
    s.typed("Hook", "Make your videos too sticky to skip.", 540, 760, 700, 250, t=11.0, dur=1.1)
E.build()
