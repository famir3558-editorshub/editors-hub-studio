#!/usr/bin/env python3
"""Fear Of Failure - a Personal Short Form reel.   python3 build.py
Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.
Edit THIS file, never the generated compositions/*.html or index.html. All times are GLOBAL seconds on the cut; frames are frames of the cut."""
import os
import reel_engine as E, kit as K, psf as P

ROOT = os.path.dirname(os.path.abspath(__file__))
DUR = 15.808
# ---- the plan, in frames. Edit cuts (cut_times.py): 163, 261, 345 - all big jumps, so each one is hidden by B-roll starting or ending on it.
A1, A2 = P.sw(77), P.sw(131)        # B-roll 1 (inside block 1): "creating content, start my own business, etc."
C1, C2 = P.sw(163), P.sw(261)       # cut 1 -> cut 2: B-roll 2 fills the block ("I feared what other people would think...")
B3, C3 = P.sw(309), P.sw(345)       # B-roll 3 ends on cut 3 ("such a crazy way to think")
FACE = [[0, A1], [A2, C1], [C2, B3], [C3, DUR]]
FULL = [[A1, A2], [C1, C2], [B3, C3]]
P.setup(ROOT, DUR, FACE, FULL, "Fear Of Failure", emph={"everything", "content", "business", "fear", "failing", "people", "fail", "think", "crazy", "only"})

BR = "assets/broll/"
P.broll("b01-create", A1, A2, [(BR + "b1.mp4", 77, 21), (BR + "b2.mp4", 98, 33)])                              # camera set-up at the desk | working at the monitor
P.broll("b02-people", C1, C2, [(BR + "b3.mp4", 163, 36), (BR + "b4.mp4", 199, 34), (BR + "b5.mp4", 233, 28)])   # audience watching (horizontal, letterboxed) | hand over mouth | head in hand
P.broll("b03-crazy", B3, C3, [(BR + "b6.mp4", 309, 36)])                                                       # hands over face at the dark desk

# 0 - 3.2 s  OPENING: 2-line hook from frame 1 + judging comments (wording invented)
K.hook("The one thing that", "held me back", A1 - 0.3)
P.comments([("dan.w", "commented: who does he think he is?", 0.02), ("kieran_92", "commented: bro thinks he's a YouTuber", 1.0), ("old school friend", "commented: this won't last lol", 1.95)], A1 - 0.3)

# 5.46 - 6.80 s  "was just the fear of failing": a dot heads for the goal, a red wall drops in its way
K.OF.append("""<div id="g2" style="position:absolute;left:190px;top:1218px;width:700px;height:150px;opacity:0"><svg width="700" height="150" viewBox="0 0 700 150" style="overflow:visible">
  <line x1="40" y1="84" x2="640" y2="84" stroke="rgba(255,255,255,.38)" stroke-width="10" stroke-linecap="round"/>
  <path d="M650,112 V34 M650,36 L692,50 L650,66" fill="@@PAPER@@" stroke="@@PAPER@@" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
  <rect id="g2b" x="352" y="22" width="18" height="124" rx="9" fill="#B3261E" style="filter:drop-shadow(0 0 16px rgba(179,38,30,.9))"/>
  <circle id="g2d" cx="40" cy="84" r="22" fill="#FFFFFF" style="filter:drop-shadow(0 4px 12px rgba(0,0,0,.6))"/></svg></div>""")
K.ojs("""tl.fromTo('#g2', {opacity:0}, {opacity:1, duration:0.18, ease:'power2.out'}, %s);
  tl.fromTo('#g2d', {attr:{cx:40}}, {attr:{cx:322}, duration:0.5, ease:'power2.in'}, 5.56);
  tl.fromTo('#g2b', {scaleY:0, transformOrigin:'50%% 50%%'}, {scaleY:1, duration:0.18, ease:'power3.out'}, 5.96);
  tl.to('#g2d', {attr:{cx:286}, duration:0.4, ease:'power2.out'}, 6.07);
  tl.to('#g2', {opacity:0, duration:0.2, ease:'power2.inOut'}, %s);""" % (A2 + 0.02, C1 - 0.22))
K.ac(5.96, "slide", -23)

# 10.88 - 12.89 s  "and now that I think about it": a typing bubble thinking it over
K.OF.append('<div id="g3" style="position:absolute;left:435px;top:1222px;width:210px;height:104px;border-radius:52px;background:#2C2C2E;border:1px solid rgba(255,255,255,.14);box-shadow:0 18px 44px rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;gap:16px;opacity:0;box-sizing:border-box">'
            + "".join('<i id="g3d%d" style="display:block;width:26px;height:26px;border-radius:13px;background:#9A9AA0;opacity:.4"></i>' % i for i in range(3)) + '</div>')
K.ojs("opop('#g3', %s); oout('#g3', %s);" % (C2 + 0.04, B3 - 0.26) + "".join(
    "tl.fromTo('#g3d%d', {opacity:0.4, y:0}, {opacity:1, y:-9, duration:0.26, ease:'sine.inOut', yoyo:true, repeat:5}, %s);" % (i, round(C2 + 0.3 + i * 0.13, 3)) for i in range(3)))
K.ac(C2 + 0.04, "pop", -24)

# 14.39 s - end  "I know I'm not the only one": the creator's real profile picture, then others appear either side
for i in range(7):
    me = i == 3
    K.OF.append('<div id="g4a%d" style="position:absolute;left:%dpx;top:1222px;width:110px;height:110px;border-radius:55px;overflow:hidden;opacity:0;box-sizing:border-box;border:%s;box-shadow:0 14px 34px rgba(0,0,0,.5);%s">%s</div>' % (
        i, 101 + i * 128, "5px solid @@ACCENT@@" if me else "3px solid rgba(255,255,255,.5)", "background:url(assets/proof/avatar.jpg) center/cover" if me else "",
        "" if me else K.ANON.replace('width="112" height="112"', 'width="100%" height="100%"')))
K.ojs("".join("opop('#g4a%d', %s);" % (i, t) for i, t in [(3, C3 + 0.04), (2, 14.92), (4, 14.92), (1, 15.12), (5, 15.12), (0, 15.32), (6, 15.32)]))
K.ac(14.92, "pops", -23)

P.finish()
