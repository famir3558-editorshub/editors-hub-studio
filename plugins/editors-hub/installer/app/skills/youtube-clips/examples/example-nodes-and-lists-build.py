#!/usr/bin/env python3
"""Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.
ytkit build: two nodes joined by a drawn line (A to B) with warning dots, then a Before list and a Now list of pills.   python3 build.py 16x9 | 9x16"""
import os, sys
import clip_engine as E, ytkit as K
ROOT = os.path.dirname(os.path.abspath(__file__)); RATIO = sys.argv[1] if len(sys.argv) > 1 else "16x9"; W16 = RATIO == "16x9"
K.start(ROOT, RATIO, face=(1053, 410)); D = E.P["dur"]
def ab(p, la="", lb=""):
    return (K.div(p + "A", "node glass", "left:70px;top:150px", "A") + K.line(p + "L", 232, 225, 448, 225) + K.div(p + "B", "node glass", "left:460px;top:150px;border-color:var(--o)", "B")
            + (K.div(p + "a", "tx", "left:70px;top:330px;width:150px;text-align:center", la) + K.div(p + "b", "tx", "left:460px;top:330px;width:150px;text-align:center", lb) if la else "")
            + "".join(K.div(f"{p}d{k}", "", f"left:{560 + 34 * k}px;top:{118 - 12 * (k % 2)}px;width:26px;height:26px;border-radius:50%;background:var(--r);box-shadow:0 0 18px var(--r)") for k in range(3)))
def lst(p, head, items, col):
    return (K.div(p + "h", "tag", f"left:40px;top:40px;background:{col}", head)
            + "".join(K.pill(f"{p}{k}", "pl-w" if col != E.RED else "pl-r", "", t, 40, 120 + 120 * k, 600) for k, t in enumerate(items)))
BEF = lst("bf", "Before", ["Can't afford groceries", "Don't want to go to work"], "rgba(255,255,255,.22)")
NOW = lst("nw", "Now", ["Family asking for money", "New relationships", "Unfulfilled"], E.RED)
J1 = K.fin("#xA", 1.81) + K.draw("#xL", 1.95, 0.3) + K.fin("#xB", 2.11) + "".join(K.fin(f"#xd{k}", 3.46 + 0.16 * k, s=0.4, d=0.3) for k in range(3))
J2 = K.draw("#yL", 8.97, 0.5) + K.fin("#yB", 9.39) + K.fin("#ya", 10.63, s=1) + K.fin("#yb", 11.27, s=1)
JB = K.fin("#bf0", 16.87) + K.fin("#bf1", 19.56)
JN = K.fin("#nw0", 24.51) + K.fin("#nw1", 27.39) + K.fin("#nw2", 29.47)
if W16:
    E.shots([(0, "side"), (5.8, "punch"), (7.033, "side"), (12.667, "wide"), (15.4, "side"), (21.633, "sidep"), (28.867, "side"), (34.5, "punch"), (37.2, "wide"), (43.067, "punch")])
    K.show(1.2, 5.7, ab("x"), J1, box=(70, 100, 660, 300))
    K.show(7.3, 12.6, ab("y", "Broke", "Rich"), K.fin("#yA", 7.67) + J2, box=(70, 150, 610, 380))
    K.show(15.5, 21.55, BEF, K.fin("#bfh", 15.6) + JB, box=(40, 40, 640, 324))
    K.show(21.75, 34.4, NOW, K.fin("#nwh", 21.85) + JN, box=(40, 40, 640, 444))
else:
    E.shots([(0, "him"), (5.8, "him2"), (7.033, "split"), (12.667, "him"), (15.4, "split"), (21.633, "split"), (28.867, "him"), (34.5, "him2"), (37.2, "him"), (43.067, "him2")])
    K.hook(0, 5.8, "First line of the hook", "second line.")
    K.show(7.033, 12.667, ab("y", "Broke", "Rich"), K.setp("#yA", {"opacity": 1}, 7.02) + J2, box=(70, 150, 610, 380))
    K.show(15.4, 21.633, BEF, K.setp("#bfh", {"opacity": 1}, 15.38) + JB, box=(40, 40, 640, 324))
    K.show(21.633, 28.867, NOW, K.setp("#nwh", {"opacity": 1}, 21.62) + JN, box=(40, 40, 640, 444))
K.finish()
