#!/usr/bin/env python3
"""Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.
ytkit build: a drawn rising line on a glass card, an account card whose status tag flips, two rows that get flagged, a list of
crossed pills.   python3 build.py 16x9 | 9x16"""
import os, sys
import clip_engine as E, ytkit as K
ROOT = os.path.dirname(os.path.abspath(__file__)); RATIO = sys.argv[1] if len(sys.argv) > 1 else "16x9"; W16 = RATIO == "16x9"
K.start(ROOT, RATIO, face=(1051, 417)); D = E.P["dur"]
COST = (K.div("cc", "glass", "left:40px;top:60px;width:600px;height:420px", '<div class="lab" style="position:absolute;left:34px;top:28px">Cost per lead</div>')
        + K.path("ccL", "M90 430 C 240 420, 400 380, 590 130", E.RED, 8))
ACC = K.div("ac", "glass", "left:40px;top:130px;width:600px;height:280px",
            f'<div style="position:absolute;left:34px;top:34px;width:96px;height:96px;border-radius:50%;overflow:hidden;background:rgba(255,255,255,.3)">{K.AV}</div>'
            '<div class="tx" style="position:absolute;left:156px;top:44px">Ad account</div><div class="bar" style="position:absolute;left:156px;top:98px;width:220px;height:16px;opacity:.5"></div>'
            '<div id="acG" class="tag g" style="position:absolute;left:34px;top:184px">Active</div><div id="acR" class="tag r" style="position:absolute;left:34px;top:184px;opacity:0">Restricted</div>')
def row(i, name, top, extra=""):
    return K.div(i, "glass", f"left:40px;top:{top}px;width:600px;height:150px", f'<div class="tx" style="position:absolute;left:34px;top:50px;font-size:48px">{name}</div><div id="{i}T" class="tag r" style="position:absolute;right:30px;top:50px;opacity:0">Restricted</div>{extra}')
TWO = row("rM", "Meta", 90) + row("rG", "Google", 280, '<div id="rGd" class="lab" style="position:absolute;left:36px;top:108px;opacity:0">within a day</div>')
LOST = [("Run ads", 37.54), ("DM people", 38.4), ("Links", 39.45)]
LIST = "".join(K.pill(f"ls{k}", "pl-r", K.CROSS, t, 140, 70 + 130 * k, 400) for k, (t, _) in enumerate(LOST))
LJS = "".join(K.fin(f"#ls{k}", t) for k, (_, t) in enumerate(LOST))
AJS = K.draw("#ccL", 8.3, 1.3)
BJS = K.setp("#acG", {"opacity": 0}, 11.28) + K.fin("#acR", 11.28, s=1.4, d=0.35)
TJS = K.fin("#rMT", 26.25, s=1.4, d=0.35) + K.fin("#rG", 28.49) + K.fin("#rGT", 29.09, s=1.4, d=0.35) + K.fin("#rGd", 29.73, s=1)
if W16:
    E.shots([(0, "wide"), (1.267, "punch"), (6.3, "side"), (10.033, "sidep"), (17.933, "wide"), (21.833, "side"), (26.867, "sidep"), (30.433, "wide"), (33.833, "punch"), (36.3, "side"), (39.367, "sidep")])
    K.show(6.6, 9.95, COST, K.fin("#cc", 6.8) + AJS, box=(40, 60, 640, 480))
    K.show(10.15, 17.85, ACC, K.fin("#ac", 10.4) + BJS, box=(40, 130, 640, 410))
    K.show(25.2, 30.4, TWO, K.fin("#rM", 25.45) + TJS, box=(40, 90, 640, 430))
    K.show(36.5, D, LIST, LJS, box=(140, 70, 540, 414))
else:
    E.shots([(0, "him"), (6.3, "split"), (10.033, "anim"), (17.933, "him"), (21.833, "him2"), (26.1, "anim"), (30.433, "him"), (33.833, "him2"), (36.3, "anim"), (40.367, "him")])
    K.hook(0, 6.3, "First line of the hook", "second line.")
    K.show(6.3, 10.033, COST, K.setp("#cc", {"opacity": 1}, 6.28) + AJS, box=(40, 60, 640, 480))
    K.show(10.033, 17.933, ACC, K.setp("#ac", {"opacity": 1}, 10.02) + BJS, box=(40, 130, 640, 410))
    K.show(26.1, 30.433, TWO, K.setp("#rM", {"opacity": 1}, 26.08) + TJS, box=(40, 90, 640, 430))
    K.show(36.3, 40.367, LIST, LJS, box=(140, 70, 540, 414))
K.finish()
