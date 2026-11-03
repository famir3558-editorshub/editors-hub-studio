#!/usr/bin/env python3
"""Face-window overlay source (0-16.55 s), 9:16: the long-hand proof that references/scene-library.md points at.
Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.
Full-screen face the whole way; graphics sit over (and behind) the creator. Edit this file, not index.html.
  python3 build.py && npx hyperframes lint
"""
import json, os, re

DUR = 16.55
# Instagram/TikTok safe zone: nothing that matters above y 270 or below y 1500; captions end above y 1250.
# SAFE=1 python3 build.py draws the zones for snapshots (never render with it on).
GUIDE = ('<div style="position:absolute;inset:0;z-index:99"><div style="position:absolute;left:0;top:0;width:1080px;height:270px;background:rgba(255,0,60,.28)"></div>'
         '<div style="position:absolute;left:0;top:1500px;width:1080px;height:420px;background:rgba(255,0,60,.28)"></div>'
         '<div style="position:absolute;left:0;top:1250px;width:1080px;height:3px;background:rgba(255,200,0,.95)"></div>'
         '<div style="position:absolute;left:950px;top:1000px;width:130px;height:500px;background:rgba(255,200,0,.22)"></div></div>') if os.environ.get("SAFE") else ""
WORDS = [w for w in json.load(open("work/words.json")) if w["s"] < DUR and not w.get("event")]

ITALIC = {"missing", "three", "grow", "matrix", "change", "selfish", "gain", "lose", "scrolling"}
KEEP_CASE = {"I've", "C", "3C"}
SKIP = {"13,000", "500,000"}          # shown by the counter instead
HEADLINE_END = 1.70                   # the hook headline carries these words

caps, tl_caps = [], []
for i, w in enumerate(WORDS):
    raw = w["w"]
    if w["s"] < HEADLINE_END or raw in SKIP:
        continue
    txt = re.sub(r"[.,!?]", "", raw)
    key = txt.lower()
    if txt not in KEEP_CASE:
        txt = key
    nxt = WORDS[i + 1]["s"] if i + 1 < len(WORDS) else DUR
    end = min(nxt, w["e"] + 0.45)
    cls = "cw"
    if key in ITALIC:
        cls += " it"
    if txt == "3C":
        cls += " num"
    caps.append(f'<span id="cw{i}" class="{cls}" data-layout-allow-overlap>{txt}</span>')
    if "it" in cls:
        tl_caps.append(f"tl.fromTo('#cw{i}',{{opacity:0,filter:'blur(6px)'}},{{opacity:1,filter:'blur(0px)',duration:0.12,ease:'power2.out'}},{w['s']:.3f});")
    else:
        tl_caps.append(f"tl.set('#cw{i}',{{opacity:1}},{w['s']:.3f});")
    tl_caps.append(f"tl.set('#cw{i}',{{opacity:0}},{end:.3f});")

FONTS = """
@font-face { font-family: "HelvB"; src: @@FONT_MAIN_BOLD_SRC@@; font-weight: 700; }
@font-face { font-family: "HelvR"; src: @@FONT_MAIN_REGULAR_SRC@@; font-weight: 400; }
@font-face { font-family: "PlayIt"; src: @@FONT_ACCENT_SRC@@; font-style: italic; }
"""

CSS = FONTS + """
:root { --o: @@ACCENT@@; --paper: @@PAPER@@; }
body { margin: 0; background: @@BG@@; }
#root { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: @@BG@@; }
#stage { position: absolute; inset: 0; transform-origin: 540px 780px; filter: blur(0px); }
#stage video { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; display: block; }
#vBase { z-index: 1; } #behind { position: absolute; inset: 0; z-index: 2; } #vFg { z-index: 3; }
#front { position: absolute; inset: 0; z-index: 4; }
#caps { position: absolute; left: 0; top: 1085px; width: 1080px; height: 130px; z-index: 20; }
.sh { text-shadow: 0 4px 22px rgba(0,0,0,.55), 0 0 3px rgba(0,0,0,.5); }
.hb { font-family: "HelvB", Helvetica, sans-serif; font-weight: 700; letter-spacing: -0.05em; color: #fff; line-height: 1; }
.pi { font-family: "PlayIt", serif; font-style: italic; color: var(--o); letter-spacing: -0.02em; line-height: 1; }
.cw { position: absolute; left: 0; width: 1080px; top: 0; text-align: center; opacity: 0; font-family: "HelvB", Helvetica, sans-serif; font-weight: 700; font-size: 92px; letter-spacing: -0.05em; line-height: 1; color: #fff;
  text-shadow: 0 4px 22px rgba(0,0,0,.7), 0 0 3px rgba(0,0,0,.6); }
.cw.it { font-family: "PlayIt", serif; font-style: italic; font-weight: 400; font-size: 122px; top: -18px; color: var(--o); letter-spacing: -0.02em; text-shadow: 0 4px 26px rgba(0,0,0,.8), 0 0 4px rgba(0,0,0,.7); }
.cw.num { color: var(--o); }
.line { position: absolute; left: 0; width: 1080px; text-align: center; opacity: 0; }
/* hook */
#h1 { top: 274px; font-size: 54px; } #h2 { top: 322px; font-size: 94px; white-space: nowrap; }
.q { position: absolute; top: 1206px; width: 170px; height: 170px; border-radius: 40px; background: rgba(14,12,11,.78); border: 2px solid rgba(255,255,255,.16); box-shadow: 0 18px 50px rgba(0,0,0,.5); display: flex; align-items: center; justify-content: center; opacity: 0; }
.q span { font-family: "PlayIt", serif; font-style: italic; font-size: 116px; color: var(--o); line-height: 1; }
/* proof */
#cnt { top: 306px; font-size: 214px; letter-spacing: -0.065em; }
#cntl { top: 150px; font-size: 76px; }
#prof { position: absolute; left: 90px; top: 1214px; width: 700px; height: 236px; border-radius: 34px; overflow: hidden; background: #000 url("assets/img/client-profile.jpg") no-repeat; background-size: 700px auto; background-position: 0 -12px; box-shadow: 0 26px 70px rgba(0,0,0,.6), 0 0 0 2px rgba(255,255,255,.12); opacity: 0; }
#chart { position: absolute; left: 650px; top: 1346px; width: 290px; height: 150px; border-radius: 30px; background: rgba(12,10,9,.9); border: 2px solid rgba(@@ACCENT_RGB@@,.75); box-shadow: 0 0 44px rgba(@@ACCENT_RGB@@,.35), 0 22px 60px rgba(0,0,0,.6); opacity: 0; }
#chart svg { position: absolute; left: 18px; top: 16px; width: 254px; height: 118px; }
/* orbit */
.ring { position: absolute; left: 0; top: 0; }
.pill { position: absolute; left: 0; top: 0; width: 168px; height: 82px; margin: -41px 0 0 -84px; border-radius: 41px; background: rgba(12,10,9,.88); border: 2px solid var(--o); box-shadow: 0 0 34px rgba(@@ACCENT_RGB@@,.45), 0 12px 30px rgba(0,0,0,.5); display: flex; align-items: center; justify-content: center; font-family: "HelvB", Helvetica, sans-serif; font-weight: 700; font-size: 46px; letter-spacing: -0.04em; color: #fff; opacity: 0; }
/* label */
#lb1 { top: 274px; font-size: 44px; } #lb2 { top: 304px; font-size: 122px; }
/* comments */
.cm { position: absolute; width: 580px; padding: 20px 78px 16px 30px; border-radius: 28px; background: #fff; box-shadow: 0 22px 60px rgba(0,0,0,.45); opacity: 0; box-sizing: border-box; }
.cm b { display: block; font-family: "HelvR", Helvetica, sans-serif; font-weight: 400; font-size: 36px; letter-spacing: -0.02em; color: #111; line-height: 1.12; }
.cm i { display: block; margin-top: 8px; font-family: "HelvR", Helvetica, sans-serif; font-style: normal; font-size: 22px; color: #8e8e8e; }
.cm svg { position: absolute; right: 26px; top: 22px; }
/* gain / lose */
.gl { position: absolute; top: 1236px; width: 350px; height: 140px; border-radius: 36px; background: rgba(12,10,9,.88); display: flex; align-items: center; justify-content: center; gap: 18px; font-family: "HelvB", Helvetica, sans-serif; font-weight: 700; font-size: 66px; letter-spacing: -0.04em; color: #fff; opacity: 0; }
#gain { left: 150px; border: 2px solid var(--o); box-shadow: 0 0 44px rgba(@@ACCENT_RGB@@,.45), 0 18px 50px rgba(0,0,0,.5); }
#lose { left: 580px; border: 2px solid rgba(255,255,255,.22); box-shadow: 0 18px 50px rgba(0,0,0,.5); color: #b9b3ac; }
/* scroll columns */
#colwrap { position: absolute; left: 0; top: 270px; width: 1080px; height: 1230px; overflow: hidden; }
.col { position: absolute; top: 0; width: 290px; opacity: 0; }
.col img { display: block; width: 290px; height: 516px; object-fit: cover; border-radius: 28px; margin-bottom: 26px; box-shadow: 0 18px 50px rgba(0,0,0,.5); }
#colL { left: 26px; } #colR { left: 764px; }
"""

def cm(i, left, top, text):
    heart = '<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#8e8e8e" stroke-width="1.8"><path d="M12 20.5s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.6a4.3 4.3 0 0 1 7.5 2.7c0 5.6-7.5 10.2-7.5 10.2z"/></svg>'
    return f'<div id="cm{i}" class="cm" style="left:{left}px;top:{top}px;filter:url(#fx{i})"><b>{text}</b><i>2h &nbsp; Reply</i>{heart}</div>'

RING = '<ellipse cx="540" cy="1100" rx="400" ry="150" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="5" stroke-linecap="round" stroke-dasharray="1 17"/>'
ARROW_UP = '<svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="@@ACCENT@@" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20V5M5 11l7-7 7 7"/></svg>'
ARROW_DN = '<svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="#b9b3ac" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v15M5 13l7 7 7-7"/></svg>'
SPARK = "M6 150 C 40 148, 70 140, 100 138 S 150 128, 180 118 S 230 104, 252 82 S 300 44, 350 10"

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<title>3C Hook Matrix — overlay proof</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{DUR}" data-fps="24">
  <svg width="0" height="0" style="position:absolute">
    <defs>
      {''.join(f'<filter id="fx{i}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur id="fg{i}" stdDeviation="0 0"/></filter>' for i in range(1, 8))}
    </defs>
  </svg>
  <div id="stage">
    <video id="vBase" src="assets/cam.mp4" playsinline data-has-audio="true" data-start="0" data-duration="{DUR}" data-track-index="0"></video>
    <div id="behind">
      <div id="h1" class="line hb sh">if you're really stuck on</div>
      <div id="h2" class="line pi sh">a few hundred views</div>
      <div id="cnt" class="line hb sh">13,000</div>
      <svg class="ring" id="ringB" width="1080" height="1920" style="opacity:0">{RING}</svg>
      <div id="pb1" class="pill">C1</div><div id="pb2" class="pill">C2</div><div id="pb3" class="pill">C3</div>
      <div id="lb1" class="line hb sh">the first C</div>
      <div id="lb2" class="line pi sh">change</div>
      <div id="colwrap"><div id="colL" class="col" style="filter:url(#fx6)"><img src="assets/img/r01.jpg"><img src="assets/img/r03.jpg"><img src="assets/img/r05.jpg"></div>
      <div id="colR" class="col" style="filter:url(#fx7)"><img src="assets/img/r02.jpg"><img src="assets/img/r04.jpg"><img src="assets/img/r06.jpg"></div></div>
    </div>
    <video id="vFg" src="assets/fg.webm" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="1"></video>
    <div id="front">
      <div id="q1" class="q" style="left:235px"><span>?</span></div><div id="q2" class="q" style="left:455px"><span>?</span></div><div id="q3" class="q" style="left:675px"><span>?</span></div>
      <div id="prof" style="filter:url(#fx4)"></div>
      <div id="chart"><svg viewBox="0 0 358 166"><path id="spark" d="{SPARK}" fill="none" stroke="@@ACCENT@@" stroke-width="7" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/><circle id="dot" cx="350" cy="10" r="11" fill="#fff" opacity="0"/></svg></div>
      <svg class="ring" id="ringF" width="1080" height="1920" style="opacity:0;clip-path:inset(1100px 0 0 0)">{RING}</svg>
      <div id="pf1" class="pill">C1</div><div id="pf2" class="pill">C2</div><div id="pf3" class="pill">C3</div>
      {cm(1, 80, 1196, "ok but what's in it for me?")}
      {cm(2, 360, 1294, "will this get me more views?")}
      {cm(3, 110, 1392, "how long is this going to take")}
      <div id="gain" class="gl">{ARROW_UP}GAIN</div><div id="lose" class="gl">{ARROW_DN}LOSE</div>
    </div>
  </div>
  <div id="caps">{''.join(caps)}</div>
  {GUIDE}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
const $ = (s) => document.querySelector(s);

// ---- helpers ---------------------------------------------------------------
// slide in with real directional motion blur (SVG gaussian on one axis)
function slide(sel, fid, dx, dy, t, dur) {{
  dur = dur || 0.42;
  tl.fromTo(sel, {{ x: dx, y: dy }}, {{ x: 0, y: 0, duration: dur, ease: 'expo.out' }}, t);
  tl.fromTo(sel, {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1, ease: 'none', immediateRender: false }}, t);
  gsap.set(sel, {{ opacity: 0 }});
  const p = {{ b: 1 }}, node = $('#fg' + fid), bx = Math.abs(dx) / 9, by = Math.abs(dy) / 9;
  tl.fromTo(p, {{ b: 1 }}, {{ b: 0, duration: dur * 0.75, ease: 'power3.out', onUpdate: () => node.setAttribute('stdDeviation', (bx * p.b).toFixed(2) + ' ' + (by * p.b).toFixed(2)) }}, t);
}}
function pop(sel, t, from) {{ tl.fromTo(sel, {{ scale: from || 0.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.34, ease: 'back.out(2.2)' }}, t); }}
function rise(sel, t, dy) {{ tl.fromTo(sel, {{ y: dy || 26, opacity: 0, filter: 'blur(8px)' }}, {{ y: 0, opacity: 1, filter: 'blur(0px)', duration: 0.28, ease: 'power3.out' }}, t); }}
function out(sel, t, dur) {{ tl.to(sel, {{ opacity: 0, scale: 0.96, duration: dur || 0.14, ease: 'power2.in' }}, t); }}
// animated punch-in / punch-out with a blur peak at the midpoint
function zoom(s, t) {{
  tl.to('#stage', {{ scale: s, duration: 0.26, ease: 'power3.inOut' }}, t - 0.13);
  tl.to('#stage', {{ filter: 'blur(7px)', duration: 0.13, ease: 'power1.in' }}, t - 0.13);
  tl.to('#stage', {{ filter: 'blur(0px)', duration: 0.15, ease: 'power1.out' }}, t);
}}
const TIGHT = 1.16;
function capY(y, t) {{ tl.set('#caps', {{ y: y }}, t); }}

// ---- A. hook: headline builds behind the head (0–1.7), then three "?" tiles ----
rise('#h1', 0.05, 30);
tl.fromTo('#h2', {{ opacity: 0, y: 34, filter: 'blur(10px)' }}, {{ opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.3, ease: 'power3.out' }}, 0.86);
out('#h1', 1.60); out('#h2', 1.60);
zoom(TIGHT, 1.72); capY(42, 1.66);
pop('#q1', 2.76); pop('#q2', 3.22); pop('#q3', 3.46);
out('#q1', 3.80, 0.1); out('#q2', 3.80, 0.1); out('#q3', 3.80, 0.1);

// ---- B. proof: real profile slides in, counter runs behind the head ----
zoom(1, 3.90); capY(0, 3.86);
slide('#prof', 4, 520, 0, 4.14, 0.46);
tl.fromTo('#prof', {{ rotation: 4 }}, {{ rotation: -2, duration: 0.46, ease: 'expo.out', immediateRender: false }}, 4.14);
rise('#cnt', 5.36, 40);
const c = {{ n: 13000 }}, cnt = $('#cnt');
tl.fromTo(c, {{ n: 13000 }}, {{ n: 500000, duration: 0.95, ease: 'power2.inOut', onUpdate: () => {{ cnt.textContent = Math.round(c.n).toLocaleString('en-US'); }} }}, 6.48);
tl.to('#cnt', {{ color: '@@ACCENT@@', duration: 0.12 }}, 7.36);
tl.to('#cnt', {{ scale: 1.05, duration: 0.1, ease: 'power2.out', yoyo: true, repeat: 1 }}, 7.36);
pop('#chart', 5.40, 0.8);
tl.fromTo('#spark', {{ strokeDashoffset: 1000 }}, {{ strokeDashoffset: 0, duration: 1.8, ease: 'power1.inOut' }}, 5.5);
tl.fromTo('#dot', {{ opacity: 0, scale: 0, svgOrigin: '350 10' }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: 'back.out(3)' }}, 7.3);
out('#prof', 7.48); out('#chart', 7.48); out('#cnt', 7.48);

// ---- C. the 3C matrix: three pills orbit the creator (behind the head on the far side) ----
zoom(TIGHT, 7.60); capY(42, 7.56);
tl.fromTo('#ringB', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, 7.62);
tl.fromTo('#ringF', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, 7.62);
const orb = {{ a: 0, k1: 0, k2: 0, k3: 0, fade: 1 }};
function placeOrbit() {{
  [1, 2, 3].forEach((i) => {{
    const th = (orb.a + (i - 1) * 120 + 200) * Math.PI / 180, s = Math.sin(th);
    const x = 540 + 400 * Math.cos(th), y = 1100 + 150 * s, k = orb['k' + i] * orb.fade, sc = (0.86 + 0.16 * s) * (0.6 + 0.4 * orb['k' + i]);
    const f = $('#pf' + i), b = $('#pb' + i), tf = 'translate(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px) scale(' + sc.toFixed(3) + ')';
    f.style.transform = tf; b.style.transform = tf;
    f.style.opacity = s >= 0 ? k : 0; b.style.opacity = s >= 0 ? 0 : k * 0.9;
  }});
}}
tl.fromTo(orb, {{ a: 0 }}, {{ a: 150, duration: 1.72, ease: 'power1.out', onUpdate: placeOrbit }}, 7.6);
tl.fromTo(orb, {{ k1: 0 }}, {{ k1: 1, duration: 0.3, ease: 'back.out(2)', onUpdate: placeOrbit }}, 7.66);
tl.fromTo(orb, {{ k2: 0 }}, {{ k2: 1, duration: 0.3, ease: 'back.out(2)', onUpdate: placeOrbit }}, 7.84);
tl.fromTo(orb, {{ k3: 0 }}, {{ k3: 1, duration: 0.3, ease: 'back.out(2)', onUpdate: placeOrbit }}, 8.02);
tl.fromTo(orb, {{ fade: 1 }}, {{ fade: 0, duration: 0.12, ease: 'none', onUpdate: placeOrbit }}, 9.14);
tl.to('#ringB', {{ opacity: 0, duration: 0.12 }}, 9.14); tl.to('#ringF', {{ opacity: 0, duration: 0.12 }}, 9.14);

// ---- D. "the first C / change" label, tucked behind the head ----
zoom(1, 9.28); capY(0, 9.24);
rise('#lb1', 9.34, 20);
tl.fromTo('#lb2', {{ opacity: 0, y: 30, filter: 'blur(12px)' }}, {{ opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.3, ease: 'power3.out' }}, 10.22);

// ---- E. viewer comments slide in with motion blur ----
slide('#cm1', 1, -420, 0, 10.80); slide('#cm2', 2, 460, 0, 11.14); slide('#cm3', 3, -420, 0, 11.90);
tl.to('#cm1', {{ opacity: 0, y: 30, duration: 0.14, ease: 'power2.in' }}, 12.86);
tl.to('#cm2', {{ opacity: 0, y: 30, duration: 0.14, ease: 'power2.in' }}, 12.89);
tl.to('#cm3', {{ opacity: 0, y: 30, duration: 0.14, ease: 'power2.in' }}, 12.92);

out('#lb1', 12.88); out('#lb2', 12.88);   // label leaves before the punch-in (a zoom would push it into the top UI band)
// ---- F. gain / lose ----
zoom(TIGHT, 13.06); capY(42, 13.02);
pop('#gain', 13.98); pop('#lose', 14.52);
out('#gain', 15.56); out('#lose', 15.56);

// ---- G. "keep scrolling": reel covers whip up behind the creator ----
zoom(1, 15.68); capY(0, 15.64);
tl.set(['#colL', '#colR'], {{ opacity: 1 }}, 15.62);
tl.fromTo('#colL', {{ y: 1150 }}, {{ y: -1750, duration: 0.95, ease: 'none' }}, 15.62);
tl.fromTo('#colR', {{ y: 1500 }}, {{ y: -1400, duration: 0.95, ease: 'none' }}, 15.62);
const sb = {{ b: 0 }};
tl.fromTo(sb, {{ b: 22 }}, {{ b: 26, duration: 0.95, ease: 'power1.in', onUpdate: () => {{ $('#fg6').setAttribute('stdDeviation', '0 ' + sb.b.toFixed(1)); $('#fg7').setAttribute('stdDeviation', '0 ' + sb.b.toFixed(1)); }} }}, 15.62);

// ---- captions: one word at a time ----
{chr(10).join(tl_caps)}

placeOrbit();
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
open("index.html", "w").write(HTML)
print("index.html written:", len(caps), "caption words")
