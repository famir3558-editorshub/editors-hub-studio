#!/usr/bin/env python3
"""Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.
Kit build, speaker right of centre: a row of week slots, bars that grow with their labels, and a stack of pills joined by drawn
lines with a light sweep on the active one (split across two 9:16 stages).   python3 build.py 16x9 | 9x16"""
import os, sys
import coach_engine as E, coach_kit as K
ROOT = os.path.dirname(os.path.abspath(__file__)); R = sys.argv[1] if len(sys.argv) > 1 else "16x9"

E.init(ROOT, R, face=(943, 469))


def weeks(p):
    cols = "".join(f'<div id="{p}w{k}" class="slot" style="left:{36 + k * 134}px;top:84px;width:118px;height:118px;display:flex;align-items:center;justify-content:center">{K.CAL}</div><div class="lab" style="position:absolute;left:{36 + k * 134}px;top:214px;width:118px;text-align:center;font-size:22px">Week {k + 1}</div>' for k in range(4))
    return K.card(p + "c", 40, 120, 600, 280, f'<div class="lab" style="position:absolute;left:36px;top:28px">Masterclass</div>' + cols)


def weeks_js(p, t0):
    return K.show(f"#{p}c", t0) + "".join(f'tl.to("#{p}w{k}",{{backgroundColor:"{E.O}",borderColor:"{E.O}",duration:.25}},{3.3 + k * 0.28:.2f});' for k in range(4))


def sales(p):
    rows = "".join(f'<div id="{p}t{k}" class="t38" style="position:absolute;left:36px;top:{40 + k * 104}px;opacity:0">{n} sales</div><div id="{p}b{k}" style="position:absolute;left:230px;top:{48 + k * 104}px;width:{w}px;height:34px;border-radius:17px;background:{E.GREEN};transform-origin:0 50%;transform:scaleX(0)"></div>' for k, (n, w) in enumerate([(2, 110), (3, 170), (5, 290)]))
    return K.card(p + "c", 40, 30, 600, 480, rows + f'<div id="{p}r" class="tag tg" style="position:absolute;left:36px;top:372px;height:68px;line-height:68px;border-radius:34px;font-size:36px;padding:0 30px;opacity:0">4K to 10K this week</div>')


def sales_js(p, t0):
    return K.show(f"#{p}c", t0) + "".join(f'fin("#{p}t{k}",{t}); tl.to("#{p}b{k}",{{scaleX:1,duration:.5,ease:"power2.out"}},{t + 0.2});' for k, t in enumerate([5.95, 7.41, 8.67])) + f'fin("#{p}r",11.67,{{s:.85}});'


def target(p, n=4):
    P = [("t0", "pl-o", K.TICK, "Monthly target", 20), ("t1", "pl-w", K.TICK, "Sales needed", 146), ("t2", "pl-w", K.AV and K.TICK, "Sign-ups per masterclass", 272), ("t3", "pl-w", K.TICK, "Conversion rate", 398)][:n]
    return "".join(K.pill(p + i, c, ic, tx, 70, top, 540) for i, c, ic, tx, top in P) + "".join(K.vline(p + f"l{k}", 340, 108 + k * 126, 142 + k * 126) for k in range(n - 1))


BW, BS, BT = (40, 120, 640, 400), (40, 30, 640, 510), (70, 20, 610, 482)
TJ = lambda p, ts: "".join((f'draw("#{p}l{k - 1}",{t - 0.3:.2f},.25);' if k else "") + f'fin("#{p}t{k}",{t}); sweep("#{p}t{k}",{t + 0.1:.2f});' for k, t in ts)
if R == "16x9":
    shots = [(0, "punch"), (1.501, "rside"), (5.881, "rsidep"), (7.382, "rside"), (12.387, "punch"), (15.891, "rside"), (17.726, "rsidep")]
    stages = [(1.501, 5.881, weeks("a"), weeks_js("a", 1.49), BW, "side"), (5.881, 12.387, sales("b"), sales_js("b", 5.87), BS, "side"),
              (15.891, 23.0, target("c"), TJ("c", [(0, 16.96), (1, 18.23), (2, 19.67), (3, 22.04)]), BT, "side")]
    K.build(R, shots, stages, scrim=[(1.501, 12.35), (15.891, 23.2)])
else:
    shots = [(0, "him"), (1.501, "split"), (5.881, "anim"), (12.387, "him"), (15.891, "split"), (17.726, "anim"), (20.771, "him")]
    stages = [(1.501, 5.881, weeks("a"), weeks_js("a", 1.49), BW, "split"), (5.881, 12.387, sales("b"), sales_js("b", 5.87), BS, "anim"),
              (15.891, 17.726, target("c", 1), TJ("c", [(0, 16.96)]), (70, 20, 610, 104), "split"),
              (17.726, 20.771, target("d", 3), K.show("#dt0", 17.71) + TJ("d", [(1, 18.23), (2, 19.67)]), (70, 20, 610, 356), "anim")]
    K.build(R, shots, stages, hook=(0, 1.501, "First line of the hook", "second line."))
