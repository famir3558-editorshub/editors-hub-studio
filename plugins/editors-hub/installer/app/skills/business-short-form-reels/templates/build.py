#!/usr/bin/env python3
"""__TITLE__ - Business Short Form reel (HyperFrames).   python3 build.py
Edit THIS file, never the generated compositions/*.html or index.html.
All times are GLOBAL seconds on the cut (paste word times from the cut's words.json); T(g) makes them scene-local.
Worked examples (built with kit.py): ~/.claude/skills/business-short-form-reels/examples/*/build.py"""
import json, os
import reel_engine as E
from reel_engine import scene, comment

ROOT = os.path.dirname(os.path.abspath(__file__))
DUR = __DUR__

# ---- mode plan. Rule: OPEN FULL SCREEN ON THE CREATOR (hook on frame 1), then rotate the three modes; every switch lands on a real edit cut.
FACE = []   # full-screen face windows       e.g. [[10.62, 12.95], [23.70, 27.60]]
FULL = []   # full-screen animation windows  e.g. [[7.66, 10.62], [20.95, 23.70], [60.50, DUR]]
# words=: the cut's words.json -> ONE-WORD captions inside FACE windows; emph = words set in the accent colour and the emphasis font
# (2-5 per face window, the words that carry the point; never a number). keep = names that keep capitals.
# hide = spans where a headline/counter already shows the words, so no caption is drawn.
E.init(ROOT, DUR, FACE, FULL, title="__TITLE__", words="words.json", emph=set(), keep=set(), hide=[])

R = lambda i: f"assets/reels/r{i:02d}.jpg"     # reel covers collected at setup (assets/reels/r01.jpg ...), if any; add topic-specific ones

# ---------------------------------------------------------------- scenes
# scene(id, start, end, full?, BODY_HTML, CSS, JS)
#  - ids look like "s01-hook"; every element id inside is "{ID}-name" and reached in JS with q("name")
#  - SAFE ZONE: graphics and text in frame y 270-1500 (may run to ~1585 at the bottom; the top is strict), x 65-1015; captions end above y 1250 (Instagram/TikTok UI
#    covers the rest). Split scenes (full=False): panel-local y 20-540. Full scenes: graphic y 290-1150, caption at 1180.
#    Check with:  SAFE=1 python3 build.py && npx hyperframes snapshot --at ...   (then rebuild WITHOUT SAFE=1)
#  - scenes must tile the timeline: each end == the next start. A scene hidden under a FACE window still needs to exist
#  - a scene that starts right after a hard cut must already be built on its first frame: author its entrances
#    ~0.4-0.5 s BEFORE the scene start (negative local time is handled by the engine)
#  - NO headline / kicker / sub-line text and no handwritten notes. Only text that is part of a graphic (labels, UI, numbers)

scene("s01-hook", 0, DUR, False, """
    <div id="{ID}-card" class="card de-glass"><div class="big de-num" id="{ID}-num">0</div><div class="de-label">EXAMPLE</div></div>
""",
    """.card{position:absolute;left:240px;top:300px;width:600px;height:360px;display:flex;flex-direction:column;align-items:center;justify-content:center;background:rgba(20,20,20,.92);z-index:4}
    .big{font-size:150px;line-height:1;color:var(--o)}""",
    """pop(tl, "card", 0.0);
    const n = {v:0}, el = document.getElementById(ID+"-num");
    tl.fromTo(n, {v:0}, {v:100, duration:1.2, ease:"power2.out", onUpdate:function(){ el.textContent = Math.round(n.v); }}, T(0.4));""")

# ---------------------------------------------------------------- FACE-window overlays (graphics while the creator is full screen)
# E.overlay(behind=HTML, front=HTML, css=CSS, js=JS)  - see SKILL.md "When the creator is full screen".
# behind = real reel covers or screenshots tucked BEHIND the head (nothing else goes there);
# front = real profiles, real proof, Instagram comments, the front half of an orbit. JS: GLOBAL seconds on `tl`.
# E.overlay(
#   behind='<div id="cnt" class="ov-line ov-hb" style="top:306px;font-size:214px">13,000</div>',
#   front='<div id="prof"></div>' + comment("cm1", 50, 1318, "a real comment from the creator's posts"),
#   css='#prof{position:absolute;left:150px;top:1400px;width:780px;height:262px;border-radius:34px;background:#000 url("assets/proof/x.jpg") no-repeat;background-size:780px auto;opacity:0}',
#   js="slide('#prof',520,0,4.14); orise('#cnt',5.36,40); counter('#cnt',13000,500000,6.48); slide('#cm1',-420,0,10.8); oout('#prof',7.48); oout('#cnt',7.48); oout('#cm1',12.86);")

E.build()
