#!/usr/bin/env python3
"""Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.
ytkit build, speaker centred and looking at the camera: a 3x3 grid of avatars where the highlighted one fades into the rest,
then a list of pills that dim one by one.   python3 build.py 16x9 | 9x16"""
import os, sys
import clip_engine as E, ytkit as K
ROOT = os.path.dirname(os.path.abspath(__file__)); RATIO = sys.argv[1] if len(sys.argv) > 1 else "16x9"; W16 = RATIO == "16x9"
K.start(ROOT, RATIO, face=(1045, 402)); D = E.P["dur"]
GREY = "rgba(255,255,255,.30)"
GRID = "".join(f'<div id="{"me" if (r, c) == (1, 1) else f"g{r}{c}"}" style="left:{115 + 150 * c}px;top:{45 + 150 * r}px;width:110px;height:110px;border-radius:50%;overflow:hidden;background:{E.O if (r, c) == (1, 1) else GREY};{"box-shadow:0 0 44px rgba(@@ACCENT_RGB@@,.7)" if (r, c) == (1, 1) else ""}">{K.AV}</div>' for r in range(3) for c in range(3))
GJS = K.to("#me", {"backgroundColor": GREY, "boxShadow": "0 0 0px rgba(@@ACCENT_RGB@@,0)", "duration": 2.7, "ease": "power1.inOut"}, 21.64)
ITEMS = [("Your offer", 28.89), ("What you do", 30.28), ("Your service", 31.45), ("How good you are", 32.23)]
LIST = "".join(K.pill(f"it{k}", "pl-w", "", t, 90, 40 + 120 * k, 500) for k, (t, _) in enumerate(ITEMS))
LJS = "".join(K.fin(f"#it{k}", t) + K.to(f"#it{k}", {"opacity": 0.38, "duration": 0.6}, t + 0.75) for k, (_, t) in enumerate(ITEMS))
if W16:
    E.shots([(0, "wide"), (5.6, "punch"), (7.7, "wide"), (12.267, "punch"), (18.2, "side"), (21.067, "sidep"), (26.7, "side"), (30.2, "sidep"), (32.433, "side")])
    K.show(18.35, 28.3, f'<div id="grid" style="left:0;top:0;width:680px;height:540px;opacity:0">{GRID}</div>'.replace("left:115", "position:absolute;left:115").replace("left:265", "position:absolute;left:265").replace("left:415", "position:absolute;left:415"), K.fin("#grid", 18.5) + GJS, box=(115, 45, 525, 455))
    K.show(28.6, D, LIST, LJS, box=(90, 40, 590, 484))
else:
    E.shots([(0, "him"), (5.6, "him2"), (7.7, "him"), (12.267, "him2"), (18.2, "split"), (26.7, "anim"), (32.433, "him")])
    K.hook(0, 5.6, "First line of the hook", "second line.")
    K.show(18.2, 26.7, f'<div id="grid" style="left:0;top:0;width:680px;height:540px">{GRID}</div>'.replace("left:115", "position:absolute;left:115").replace("left:265", "position:absolute;left:265").replace("left:415", "position:absolute;left:415"), GJS, box=(115, 45, 525, 455))
    K.show(26.7, 32.433, LIST, LJS, box=(90, 40, 590, 484))
K.finish()
