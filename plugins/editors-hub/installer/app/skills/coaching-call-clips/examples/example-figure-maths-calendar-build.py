#!/usr/bin/env python3
"""Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.
Kit build, speaker right of centre (rside / rsidep): a figure card, a two-line sum with ticking results, a calendar of slots that turn green.   python3 build.py 16x9 | 9x16"""
import os, sys
import coach_engine as E, coach_kit as K
ROOT = os.path.dirname(os.path.abspath(__file__)); R = sys.argv[1] if len(sys.argv) > 1 else "16x9"

E.init(ROOT, R, face=(799, 452))


def tag(p):
    return K.card(p + "c", 150, 150, 380, 240, f'<div class="lab" style="position:absolute;left:0;right:0;top:34px;text-align:center">minimum</div><div id="{p}n" class="fig" style="position:absolute;left:0;right:0;top:86px;text-align:center;font-size:96px;opacity:0">$2,000</div>')


def maths(p):
    return K.card(p + "c", 40, 30, 600, 480, f'''<div id="{p}k" class="tag to" style="position:absolute;left:36px;top:28px;opacity:0">10% commission</div>
<div id="{p}a1" class="t38" style="position:absolute;left:36px;top:112px;opacity:0;color:rgba(255,255,255,.8)">$2,000 × 10%</div><div id="{p}r1" class="fig" style="position:absolute;left:36px;top:160px;opacity:0;color:{E.GREEN}">= $0</div>
<div id="{p}a2" class="t38" style="position:absolute;left:36px;top:292px;opacity:0;color:rgba(255,255,255,.8)">$1,000 × 10%</div><div id="{p}r2" class="fig" style="position:absolute;left:36px;top:340px;opacity:0;color:{E.RED}">= $0</div>''')


def maths_js(p, t0):
    return (K.show(f"#{p}c", t0) + f'fin("#{p}k",9.72,{{s:.8}}); fin("#{p}a1",10.47); fin("#{p}r1",11.34); counter("#{p}r1",0,200,11.3,.5,"= $",""); fin("#{p}a2",13.57); fin("#{p}r2",14.25); counter("#{p}r2",0,100,14.2,.5,"= $","");')


def cal12(p):
    slots = "".join(f'<div id="{p}s{k}" class="slot" style="left:{36 + (k % 4) * 134}px;top:{104 + (k // 4) * 118}px;width:118px;height:100px;opacity:0"></div>' for k in range(12))
    return K.card(p + "c", 40, 30, 600, 480, f'<div class="lab" style="position:absolute;left:36px;top:30px">Calls today</div><div id="{p}d" class="tag tg" style="position:absolute;right:36px;top:20px;opacity:0">5 deals a day</div>' + slots)


def cal12_js(p, t0):
    return (K.show(f"#{p}c", t0) + f'fin("#{p}d",18.46,{{s:.8}});' + "".join(f'fin("#{p}s{k}",{20.55 + k * 0.05:.2f},{{s:.8}});' for k in range(12)) + "".join(K.on(f"#{p}s{k}", round(21.3 + n * 0.08, 2), "--good", 1, .2) for n, k in enumerate([0, 3, 5, 8, 10])))


BT, BM = (150, 150, 530, 390), (40, 30, 640, 510)
if R == "16x9":
    shots = [(0, "punch"), (4.463, "rside"), (6.506, "rsidep"), (9.635, "rside"), (15.057, "punch"), (17.643, "rside"), (18.435, "rsidep"), (22.731, "wide"), (24.274, "punch")]
    stages = [(4.463, 6.506, tag("a"), K.show("#ac", 4.45) + 'fin("#an",5.45);', BT, "side"), (6.506, 15.057, maths("b"), maths_js("b", 6.5), BM, "side"), (17.643, 22.731, cal12("c"), cal12_js("c", 17.63), BM, "side")]
    K.build(R, shots, stages, scrim=[(4.463, 15.0), (17.643, 22.7)])
else:
    shots = [(0, "him"), (4.463, "split"), (6.506, "anim"), (15.057, "him"), (15.724, "him2"), (17.643, "anim"), (22.731, "him"), (24.274, "him2")]
    stages = [(4.463, 6.506, tag("a"), K.show("#ac", 4.45) + 'fin("#an",5.45);', BT, "split"), (6.506, 15.057, maths("b"), maths_js("b", 6.5), BM, "anim"), (17.643, 22.731, cal12("c"), cal12_js("c", 17.63), BM, "anim")]
    K.build(R, shots, stages, hook=(0, 4.463, "First line of the hook", "second line."))
