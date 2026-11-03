#!/usr/bin/env python3
"""Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.
Kit build, speaker right of centre: ONE graphic (a generic phone mock-up with a default avatar) that carries on across 9:16 mode
switches as separate instances with their earlier state pre-set; tags and a drawn line.   python3 build.py 16x9 | 9x16"""
import os, sys
import coach_engine as E, coach_kit as K
ROOT = os.path.dirname(os.path.abspath(__file__)); R = sys.argv[1] if len(sys.argv) > 1 else "16x9"

E.init(ROOT, R, face=(849, 438))


def reel(p):
    return (f'''<div id="{p}ph" style="left:150px;top:10px;width:270px;height:500px;border-radius:38px;border:3px solid rgba(255,255,255,.35);background:linear-gradient(170deg,#3a3633,#171514);box-shadow:0 26px 60px rgba(0,0,0,.5);overflow:hidden;opacity:0;box-sizing:border-box">
  <div class="av" style="position:absolute;left:65px;top:170px;width:140px;height:140px">{K.AV}</div>
  <div id="{p}th" style="position:absolute;left:0;right:0;top:44px;text-align:center;opacity:0;font-family:HelvB,sans-serif;letter-spacing:-0.04em"><div style="font-size:24px">Your hook</div><div style="display:inline-block;margin-top:4px;font-size:23px;color:#000;background:#fff;padding:1px 9px 3px">goes here.</div></div>
  <div id="{p}cb" style="position:absolute;left:28px;right:28px;top:372px;height:54px;border-radius:12px;border:2px dashed rgba(255,255,255,.45);opacity:0"></div>
  <div style="position:absolute;left:24px;right:24px;bottom:22px;height:6px;border-radius:3px;background:rgba(255,255,255,.2)"><div id="{p}pb" style="width:100%;height:100%;border-radius:3px;background:#fff;transform-origin:0 50%;transform:scaleX(0)"></div></div>
</div>'''
            + f'<div id="{p}nt" class="tag tr" style="left:440px;top:384px;opacity:0">no captions</div>'
            + f'<div id="{p}mk" class="tag" style="left:440px;top:446px;opacity:0;background:rgba(255,255,255,.16)">3 to 5 s</div>'
            + f'<div id="{p}on" class="tag to" style="left:440px;top:50px;opacity:0">hook stays on</div>'
            + f'<svg class="ln" viewBox="0 0 680 540" width="680" height="540"><path id="{p}up" d="M450 300 C 500 296, 520 250, 560 236 S 610 180, 640 150" fill="none" stroke="{E.GREEN}" stroke-width="6" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/></svg>'
            + f'<div id="{p}vw" class="lab" style="left:450px;top:310px;opacity:0">views</div>')


def r_js(p, t0, stage):            # 0 = discovery, 1 = quiet (phone only), 2 = hook + progress, 3 = result
    js = K.show(f"#{p}ph", t0)
    if stage == 0: return js + f'fin("#{p}cb",4.6,{{s:.95}}); fin("#{p}nt",4.69,{{s:.8}});'
    js += f'gsap.set("#{p}cb",{{opacity:1}});'
    if stage in (2, 9): js += f'fin("#{p}th",14.81,{{s:.9}}); tl.fromTo("#{p}pb",{{scaleX:0}},{{scaleX:1,duration:5.5,ease:"none"}},15.5); fin("#{p}mk",18.24,{{s:.8}}); tl.to("#{p}mk",{{opacity:0,duration:.25}},19.6); fin("#{p}on",19.92,{{s:.8}});'
    if stage == 3: js += f'gsap.set("#{p}th,#{p}on",{{opacity:1}}); gsap.set("#{p}pb",{{scaleX:1}});'
    if stage in (3, 9): js += f'draw("#{p}up",23.2,.7); tl.to("#{p}vw",{{opacity:1,duration:.25}},23.4);'
    return js


BX = (150, 10, 660, 510)
if R == "16x9":
    shots = [(0, "punch"), (3.378, "rside"), (6.048, "rsidep"), (7.174, "rside"), (11.595, "rsidep"), (14.514, "rside"), (17.184, "rsidep"), (21.313, "rside"), (24.191, "punch"), (25.442, "wide")]
    stages = [(3.378, 11.595, reel("a"), r_js("a", 3.37, 0), BX, "side"), (11.595, 24.191, reel("b"), r_js("b", 11.4, 9), BX, "side")]
    K.build(R, shots, stages, scrim=[(3.378, 24.15)])
else:
    shots = [(0, "him"), (3.378, "anim"), (11.595, "split"), (14.514, "anim"), (21.313, "split"), (24.191, "him"), (25.442, "him2")]
    stages = [(3.378, 11.595, reel("a"), r_js("a", 3.37, 0), BX, "anim"), (11.595, 14.514, reel("b"), r_js("b", 11.58, 1), BX, "split"),
              (14.514, 21.313, reel("c"), r_js("c", 14.5, 2), BX, "anim"), (21.313, 24.191, reel("d"), r_js("d", 21.3, 3), BX, "split")]
    K.build(R, shots, stages, hook=(0, 3.378, "First line of the hook", "second line."))
