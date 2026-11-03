#!/usr/bin/env python3
"""Scene library source: the long-hand reel that references/scene-library.md points at (search for a scene id).
Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.
Written against an earlier layout of the engine: copy the scene BODIES (html, css, js), not the scaffolding or the vertical placement.
Run:  python3 build.py
      BB_ALT=1 python3 build.py   (alternate proof scene: slider wipe + growth curve)
All scene times are GLOBAL seconds on the cut; T(g) converts to scene-local."""
import json, os
import reel_engine as E
from reel_engine import scene, head

ROOT = os.path.dirname(os.path.abspath(__file__))
DUR = 63.272
FACE = [[10.62, 12.95], [23.70, 27.60], [34.05, 38.00], [49.60, 51.45]]            # full-screen face
FULL = [[7.66, 10.62], [20.95, 23.70], [38.00, 43.05], [51.45, 55.80], [60.50, DUR]]  # full-screen animation
E.init(ROOT, DUR, FACE, FULL, title="3C Hook Matrix")

F = lambda i: f"assets/reels/f{i:02d}.jpg"
R = lambda i: f"assets/reels/r{i:02d}.jpg"
C = lambda i: f"assets/clips/c{i:02d}.mp4"

def mcards(pref, filled=()):
    out = ""
    for i, (n, k) in enumerate([("C1", "CHANGE"), ("C2", "CLARITY"), ("C3", "CURIOSITY")]):
        f = i in filled
        out += f"""<div id="{{ID}}-{pref}{i}" class="mc de-glass"><div class="mn">{n}</div><div class="mw"><span class="qq" style="opacity:{0 if f else 1}">? ? ?</span><span id="{{ID}}-{pref}k{i}" class="kw" style="opacity:{1 if f else 0};color:{'var(--paper)' if f else 'var(--o)'};text-shadow:{'none' if f else '0 0 34px rgba(@@ACCENT_RGB@@,.6)'}">{k}</span></div></div>"""
    return out
MCSS = """.stack{position:absolute;left:120px;width:840px;z-index:5}
    .mc{position:relative;height:200px;margin-bottom:30px;display:flex;align-items:center;gap:40px;padding:0 50px;box-sizing:border-box;border:2px dashed rgba(255,255,255,.26);background:rgba(20,20,20,.92)}
    .mn{font-family:"HelvB";font-size:108px;letter-spacing:-.06em;color:rgba(255,255,255,.36);width:170px}
    .mw{position:relative;font-family:"HelvB";font-size:84px;letter-spacing:-.045em}
    .qq{color:rgba(255,255,255,.22)} .kw{position:absolute;left:0;top:0}"""

# ------------------------------------------------------------------ 01 Hook (split) — IG profile grid, views stuck in the hundreds
VIEWS = [214, 187, 302, 96, 241, 158, 133, 279]
grid = "".join(f'<div class="gt de-tile" id="{{ID}}-g{i}" style="left:{62 + (i % 4) * 242}px;top:{96 + (i // 4) * 326}px"><img src="{R(i + 1)}"/><div class="vc" id="{{ID}}-v{i}">▶ {VIEWS[i]}</div></div>' for i in range(8))
scene("s01-hook", 0, 3.80, False, grid + """
    <div class="slots"><span id="{ID}-c0" class="de-chip">C <b>?</b></span><span id="{ID}-c1" class="de-chip">C <b>?</b></span><span id="{ID}-c2" class="de-chip">C <b>?</b></span></div>
""",
    """.gt{width:230px;height:310px;border-radius:14px;z-index:4}
    .vc{position:absolute;left:10px;bottom:10px;padding:6px 12px;border-radius:999px;background:rgba(10,10,10,.85);font-family:"HelvB";font-size:26px;letter-spacing:-.02em}
    .slots{position:absolute;left:0;right:0;top:786px;display:flex;justify-content:center;gap:30px;z-index:6}
    .slots .de-chip{font-size:50px;background:rgba(10,10,10,.9)} .slots b{color:var(--grey)}""",
    """const V = """ + json.dumps(VIEWS) + """;
    for (let i=0;i<8;i++){ tl.fromTo(q("g"+i), {opacity:0, y:-50, rotation:(i%2?6:-6), scale:0.8}, {opacity:1, y:0, rotation:0, scale:1, duration:0.5, ease:"back.out(1.7)"}, T(-0.25 + i*0.09));
      const el = document.getElementById(ID+"-v"+i), o = {v:V[i]-40};
      tl.fromTo(o, {v:V[i]-40}, {v:V[i]+7, duration:3.4, ease:"power1.out", onUpdate:function(){ el.textContent = "▶ " + Math.round(o.v); }}, T(0.2)); }
    tl.to("#"+ID+"-box .gt img", {filter:"grayscale(1) brightness(.6)", duration:0.5, stagger:0.04}, T(2.4));
    [3.0, 3.18, 3.38].forEach(function(g,i){ pop(tl, "c"+i, g); });""")

# ------------------------------------------------------------------ 02 Proof (split)
parts = "".join(f'<div class="dot" id="{{ID}}-d{i}" style="left:{640 + (i*53)%320}px;top:{640 + (i*37)%80}px"></div>' for i in range(18))
scene("s02-proof", 3.80, 7.66, False, """
    <div class="numwrap"><div id="{ID}-num" class="de-num">13,000</div><div class="de-label" style="margin-top:8px">FOLLOWERS</div></div>
    <div class="stage3d">
      <div id="{ID}-b" class="card de-glass"><img src="assets/proof/bb-before.png"/></div>
      <div id="{ID}-a" class="card de-glass de-hot"><img src="assets/proof/bb-after.png"/></div>
    </div>
    <div id="{ID}-bl" class="de-label lab" style="left:96px">BEFORE</div>
    <div id="{ID}-al" class="de-label lab" style="left:604px;color:var(--o)">AFTER</div>
    <svg class="arrow" width="150" height="70"><path id="{ID}-arr" d="M10,35 L128,35 M104,14 L130,35 L104,56" fill="none" stroke="@@ACCENT@@" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/></svg>
    """ + parts,
    """.numwrap{position:absolute;left:0;right:0;top:56px;text-align:center;z-index:5}
    #{ID}-num{font-size:128px;line-height:1;color:var(--paper);display:inline-block;transform-origin:50% 100%}
    .stage3d{position:absolute;inset:0;perspective:1400px}
    .card{position:absolute;top:262px;width:380px;height:476px;overflow:hidden;padding:0;border-radius:26px}
    .card img{width:100%;height:100%;object-fit:cover;object-position:top;display:block}
    #{ID}-b{left:96px} #{ID}-a{left:604px}
    .lab{position:absolute;top:762px;width:380px;text-align:center}
    .arrow{position:absolute;left:466px;top:466px;overflow:visible;z-index:6}
    .dot{position:absolute;width:12px;height:12px;border-radius:6px;background:var(--o);box-shadow:0 0 14px rgba(@@ACCENT_RGB@@,.9);opacity:0;z-index:6}""",
    """tl.fromTo(q("num"), {opacity:0, y:20}, {opacity:1, y:0, duration:0.4, ease:"power3.out"}, T(5.05));
    const n = {v:13000}; const el = document.getElementById(ID+"-num");
    tl.fromTo(n, {v:13000}, {v:500000, duration:0.95, ease:"power2.inOut", onUpdate:function(){ el.textContent = Math.round(n.v).toLocaleString("en-US") + (n.v >= 499999 ? "+" : ""); el.style.color = n.v >= 499999 ? "@@ACCENT@@" : "@@PAPER@@"; }}, T(6.2));
    tl.fromTo(q("num"), {scale:1}, {scale:1.08, duration:0.95, ease:"power2.in"}, T(6.2));
    tl.to(q("num"), {scale:1, duration:0.3, ease:"back.out(3)"}, T(7.15));
    tl.fromTo(q("b"), {opacity:0, rotationY:-60, x:-80, transformPerspective:1400}, {opacity:1, rotationY:14, x:0, duration:0.6, ease:"power3.out"}, T(3.3));
    tl.fromTo(q("bl"), {opacity:0}, {opacity:1, duration:0.3}, T(3.5));
    draw(tl, "arr", 6.0, 0.45);
    tl.fromTo(q("a"), {opacity:0, rotationY:-100, scale:0.8, transformPerspective:1400}, {opacity:1, rotationY:-14, scale:1, duration:0.7, ease:"back.out(1.6)"}, T(6.2));
    tl.fromTo(q("al"), {opacity:0}, {opacity:1, duration:0.3}, T(6.5));
    tl.to(q("b"), {opacity:0.55, filter:"grayscale(1)", duration:0.5}, T(6.4));
    for (let i=0;i<18;i++){ tl.fromTo(q("d"+i), {opacity:0, y:0, scale:0.4}, {opacity:1, y:-(160 + (i*29)%160), scale:1, duration:0.9 + (i%4)*0.12, ease:"power2.out"}, T(6.35 + (i%9)*0.07)); tl.to(q("d"+i), {opacity:0, duration:0.3}, T(7.2 + (i%5)*0.06)); }
    floaty(tl, "b", 6, 2.2, 3.9, 3.6);""")

# ------------------------------------------------------------------ 02 (ALT, BB_ALT=1) — one profile card: slider wipes before→after, growth curve rockets
if os.environ.get("BB_ALT"):
    CW, CH = 470, 330
    cpts = []
    for k in range(0, 61):
        u = k / 60
        cpts.append(f"{u*CW:.1f},{CH - (CH-14) * (2.718281828 ** (4.2*u) - 1) / (2.718281828 ** 4.2 - 1):.1f}")
    scene("s02-proof", 3.80, 7.66, False, """
    <div id="{ID}-card" class="card de-glass">
      <img src="assets/proof/bb-before.png"/>
      <div id="{ID}-rev" class="rev"><img src="assets/proof/bb-after.png"/></div>
      <div id="{ID}-edge" class="edge"><div class="knob">‹ ›</div></div>
    </div>
    <div id="{ID}-lb" class="de-label lab">BEFORE</div>
    <div id="{ID}-la" class="de-label lab" style="color:var(--o)">AFTER</div>
    <div class="numwrap"><div id="{ID}-num" class="de-num">13,000</div><div class="de-label" style="margin-top:8px">FOLLOWERS</div></div>
    <div class="chart">
      <svg width="470" height="330" viewBox="0 0 470 330" style="overflow:visible">
        <defs><linearGradient id="{ID}-g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="@@ACCENT@@" stop-opacity=".45"/><stop offset="1" stop-color="@@ACCENT@@" stop-opacity="0"/></linearGradient>
        <clipPath id="{ID}-cp"><rect id="{ID}-cpr" x="0" y="-20" width="0" height="370"/></clipPath></defs>
        <line x1="0" y1="330" x2="470" y2="330" stroke="rgba(255,255,255,.3)" stroke-width="3"/>
        <g clip-path="url(#{ID}-cp)"><polygon points="0,330 """ + " ".join(cpts) + """ 470,330" fill="url(#{ID}-g)"/><polyline points=\"""" + " ".join(cpts) + """\" fill="none" stroke="@@ACCENT@@" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></g>
        <circle id="{ID}-dot" cx="0" cy="330" r="14" fill="@@PAPER@@" opacity="0"/>
      </svg>
      <div class="ax" style="left:0">13K</div><div id="{ID}-ax2" class="ax" style="right:0;color:var(--o)">500K</div>
    </div>
""",
    """.card{position:absolute;left:70px;top:150px;width:440px;height:552px;overflow:hidden;padding:0;border-radius:30px;z-index:4}
    .card img{width:100%;height:100%;object-fit:cover;object-position:top;display:block}
    .rev{position:absolute;inset:0;clip-path:inset(0 100% 0 0)}
    .edge{position:absolute;top:0;bottom:0;left:0;width:6px;margin-left:-3px;background:var(--o);box-shadow:0 0 22px rgba(@@ACCENT_RGB@@,.9);opacity:0}
    .knob{position:absolute;left:-30px;top:246px;width:66px;height:66px;border-radius:33px;background:var(--o);color:@@ON_ACCENT@@;font-family:"HelvB";font-size:30px;display:flex;align-items:center;justify-content:center;letter-spacing:.06em}
    .lab{position:absolute;left:70px;top:726px;width:440px;text-align:center;font-size:26px}
    .numwrap{position:absolute;left:560px;top:160px;width:470px;text-align:left;z-index:5}
    #{ID}-num{font-size:104px;line-height:1;color:var(--paper);display:inline-block;transform-origin:0% 100%}
    .chart{position:absolute;left:560px;top:372px;width:470px;height:330px;z-index:4}
    .ax{position:absolute;top:344px;font-family:"HelvB";font-size:28px;color:var(--grey)}""",
    """tl.fromTo(q("card"), {opacity:0, y:50, rotationY:-24, transformPerspective:1400}, {opacity:1, y:0, rotationY:0, duration:0.55, ease:"power3.out"}, T(3.3));
    tl.fromTo(q("lb"), {opacity:0}, {opacity:1, duration:0.3}, T(3.5));
    tl.fromTo(q("num"), {opacity:0, y:20}, {opacity:1, y:0, duration:0.4, ease:"power3.out"}, T(5.05));
    const CW = 470, CH = 330, E = Math.exp(4.2) - 1;
    const W = {p:0}; const rev = document.getElementById(ID+"-rev"), edge = document.getElementById(ID+"-edge"), cpr = document.getElementById(ID+"-cpr"), dot = document.getElementById(ID+"-dot"), num = document.getElementById(ID+"-num");
    function upd(){ const p = W.p; rev.style.clipPath = "inset(0 " + (100 - p*100).toFixed(2) + "% 0 0)"; edge.style.transform = "translateX(" + (440*p).toFixed(1) + "px)";
      cpr.setAttribute("width", (CW*p + 6).toFixed(1)); dot.setAttribute("cx", (CW*p).toFixed(1)); dot.setAttribute("cy", (CH - (CH-14)*(Math.exp(4.2*p)-1)/E).toFixed(1));
      const v = 13000 + (500000-13000)*(Math.exp(4.2*p)-1)/E; num.textContent = Math.round(v).toLocaleString("en-US") + (p >= 0.999 ? "+" : ""); num.style.color = p >= 0.999 ? "@@ACCENT@@" : "@@PAPER@@"; }
    tl.fromTo(q("edge"), {opacity:0}, {opacity:1, duration:0.2}, T(5.9));
    tl.fromTo(q("dot"), {opacity:0}, {opacity:1, duration:0.2}, T(6.0));
    tl.fromTo(W, {p:0}, {p:1, duration:1.05, ease:"power2.inOut", onUpdate:upd}, T(6.15));
    tl.to(q("lb"), {opacity:0, duration:0.2}, T(6.7)); tl.fromTo(q("la"), {opacity:0}, {opacity:1, duration:0.25}, T(6.75));
    tl.to(q("edge"), {opacity:0, duration:0.25}, T(7.2));
    tl.to(q("card"), {borderColor:"@@ACCENT@@", boxShadow:"0 0 60px rgba(@@ACCENT_RGB@@,.55)", duration:0.3}, T(7.2));
    tl.fromTo(q("card"), {scale:1}, {scale:1.04, duration:0.16, yoyo:true, repeat:1, ease:"power2.out"}, T(7.2));
    tl.fromTo(q("num"), {scale:1}, {scale:1.1, duration:0.16, yoyo:true, repeat:1, ease:"power2.out"}, T(7.2));
    tl.fromTo(q("ax2"), {opacity:0.4}, {opacity:1, duration:0.2}, T(7.2));""")

# ------------------------------------------------------------------ 03 Matrix (FULL) — cards pop up one at a time
scene("s03-matrix", 7.66, 10.62, True, f"""<div class="stack" style="top:630px">{mcards("c")}</div>""",
    MCSS,
    """[7.6, 8.25, 8.8].forEach(function(g,i){ tl.fromTo(q("c"+i), {opacity:0, y:90, scale:0.82}, {opacity:1, y:0, scale:1, duration:0.5, ease:"back.out(1.9)"}, T(g)); });
    tl.to(q("c0"), {borderColor:"@@ACCENT@@", boxShadow:"0 0 50px rgba(@@ACCENT_RGB@@,.5)", duration:0.25}, T(9.62));
    tl.to("#"+ID+"-c0 .mn", {color:"@@ACCENT@@", duration:0.25}, T(9.62));
    tl.to("#"+ID+"-c0 .qq", {opacity:0, duration:0.2}, T(10.1));
    tl.fromTo(q("ck0"), {opacity:0, scaleX:1.35, filter:"blur(12px)", transformOrigin:"0% 50%"}, {opacity:1, scaleX:1, filter:"blur(0px)", duration:0.45, ease:"expo.out"}, T(10.12));
    tl.fromTo(q("c0"), {scale:1}, {scale:1.04, duration:0.15, yoyo:true, repeat:1, ease:"power2.out"}, T(10.12));""")

# ------------------------------------------------------------------ 04 Change (split; visible 12.95-16.45)
feed = "".join(f'<div class="ft"><img src="{R(i + 9)}"/></div>' for i in range(8))
scene("s04-change", 10.62, 16.45, False, f"""
    <div id="{{ID}}-phone" class="phone"><div id="{{ID}}-col" class="col">{feed}</div><div class="notch"></div></div>
    <div class="side" id="{{ID}}-gw" style="left:36px"><div id="{{ID}}-g" class="gl de-glass"><div class="sg">+</div><div class="sw">GAIN</div></div></div>
    <div class="side" id="{{ID}}-lw" style="left:744px"><div id="{{ID}}-l" class="gl de-glass"><div class="sg">−</div><div class="sw">LOSE</div></div></div>
""",
    """.phone{position:absolute;left:355px;top:118px;width:370px;height:724px;border-radius:50px;overflow:hidden;border:8px solid #2a2a2a;box-shadow:0 0 0 2px rgba(255,255,255,.14),0 40px 90px rgba(0,0,0,.7);z-index:4;background:#000}
    .notch{position:absolute;left:130px;top:10px;width:110px;height:26px;border-radius:14px;background:#000;z-index:3}
    .col{position:absolute;left:0;top:0;width:100%}
    .ft{width:354px;height:708px;overflow:hidden} .ft img{width:100%;height:100%;object-fit:cover;display:block}
    .side{position:absolute;top:370px;width:300px;perspective:900px;z-index:5}
    .gl{height:220px;display:flex;flex-direction:column;align-items:center;justify-content:center;border:2px dashed rgba(@@ACCENT_RGB@@,.85);background:rgba(20,20,20,.92)}
    .sg{font-family:"HelvB";font-size:96px;line-height:1;color:var(--o)} .sw{font-family:"HelvB";font-size:54px;letter-spacing:-.04em;margin-top:4px}""",
    """tl.fromTo(q("phone"), {opacity:0, y:60, rotationX:24, transformPerspective:1200}, {opacity:1, y:0, rotationX:0, duration:0.6, ease:"power3.out"}, T(10.4));
    const H = 708; const col = q("col");
    [[12.2,1],[13.1,2],[13.9,3],[14.7,4]].forEach(function(s){ tl.to(col, {y:-H*s[1], duration:0.42, ease:"power3.inOut"}, T(s[0])); });
    tl.to(col, {y:-H*7, duration:0.75, ease:"power2.in"}, T(15.55));
    tl.fromTo(col, {filter:"blur(0px)"}, {filter:"blur(7px)", duration:0.4, ease:"power2.in"}, T(15.65));
    tl.fromTo(q("g"), {opacity:0, rotationY:70, x:-60}, {opacity:1, rotationY:22, x:0, duration:0.55, ease:"back.out(1.6)"}, T(13.9));
    tl.fromTo(q("l"), {opacity:0, rotationY:-70, x:60}, {opacity:1, rotationY:-22, x:0, duration:0.55, ease:"back.out(1.6)"}, T(14.36));
    tl.fromTo(q("gw"), {y:-7}, {y:7, duration:0.9, yoyo:true, repeat:3, ease:"sine.inOut"}, T(14.2));
    tl.fromTo(q("lw"), {y:7}, {y:-7, duration:0.9, yoyo:true, repeat:3, ease:"sine.inOut"}, T(14.6));""")

# ------------------------------------------------------------------ 05 Clarity (split) — the ONE carousel: rush, then stop
NT = 10
tiles = "".join(f'<div class="cf de-tile" id="{{ID}}-t{i}"><img src="{R(i + 3)}"/></div>' for i in range(NT))
scene("s05-clarity", 16.45, 20.95, False, f"""
    <div class="flow">{tiles}</div>
    <div id="{{ID}}-barw" class="bar"><div id="{{ID}}-bar" class="barin"></div></div>
""",
    """.flow{position:absolute;left:0;top:0;width:1080px;height:960px;perspective:1300px;z-index:4}
    .cf{width:330px;height:587px;left:375px;top:150px;transform-origin:50% 50%}
    .bar{position:absolute;left:375px;top:800px;width:330px;height:10px;border-radius:5px;background:rgba(255,255,255,.2);z-index:6;overflow:hidden;opacity:0}
    .barin{width:100%;height:100%;background:var(--o);transform-origin:0 50%;transform:scaleX(0)}""",
    """const tiles = []; for (let i=0;i<""" + str(NT) + """;i++) tiles.push(document.getElementById(ID+"-t"+i));
    const P = {p:0.4, sel:0};
    function lay(){ for (let i=0;i<tiles.length;i++){ const d = i - P.p, a = Math.abs(d), sg = d<0?-1:1;
        const x = a<=1 ? d*236 : sg*(236 + (a-1)*150); const ry = Math.max(-62, Math.min(62, -d*48));
        const sc = (1 - Math.min(a,3)*0.11) * (i===6 ? 1 + 0.1*P.sel : 1);
        const t = tiles[i]; t.style.transform = "translateX(" + x.toFixed(1) + "px) rotateY(" + ry.toFixed(1) + "deg) scale(" + sc.toFixed(3) + ")";
        t.style.zIndex = String(100 - Math.round(a*10)); t.style.opacity = String(Math.max(0, 1 - Math.max(0, a-3.2)*0.6) * (i===6 ? 1 : 1 - 0.5*P.sel));
        t.style.filter = "blur(" + (Math.max(0, 1 - (P.p-0.4)/5.6) * 5 * (a < 0.5 ? 0.4 : 1)).toFixed(2) + "px)";
        if (i===6) { t.style.borderColor = P.sel>0.5 ? "@@ACCENT@@" : "rgba(255,255,255,.16)"; t.style.boxShadow = "0 0 " + (60*P.sel).toFixed(0) + "px rgba(@@ACCENT_RGB@@," + (0.6*P.sel).toFixed(2) + "), 0 24px 60px rgba(0,0,0,.6)"; } } }
    tl.fromTo(P, {p:0.4}, {p:6, duration:2.75, ease:"expo.out", onUpdate:lay}, T(16.45));
    tl.fromTo(P, {sel:0}, {sel:1, duration:0.4, ease:"back.out(2)", onUpdate:lay}, T(19.2));
    tl.fromTo(q("barw"), {opacity:0}, {opacity:1, duration:0.2}, T(19.2));
    tl.fromTo(q("bar"), {scaleX:0}, {scaleX:1, duration:1.7, ease:"none"}, T(19.25));""")

# ------------------------------------------------------------------ 06 Target (FULL) — a crowd, a spotlight hunts and locks onto ONE viewer
PERSON = '<svg viewBox="0 0 24 24" width="100%" height="100%"><circle cx="12" cy="7.6" r="4.3" fill="currentColor"/><path d="M3.2,22 C4.2,15.2 19.8,15.2 20.8,22 Z" fill="currentColor"/></svg>'
crowd, CP = "", []
for i in range(48):
    cx = 140 + (i % 8) * 114 + ((i * 37) % 30) - 15
    cy = 560 + (i // 8) * 150 + ((i * 53) % 34) - 17
    CP.append([cx, cy])
    crowd += f'<div class="pp" id="{{ID}}-p{i}" style="left:{cx - 44}px;top:{cy - 44}px">{PERSON}</div>'
TGT = 28
scene("s06-target", 20.95, 23.70, True, f"""
    <div class="crowd">{crowd}</div>
    <div id="{{ID}}-spot" class="spot"></div>
    <svg class="tg" width="1080" height="1920"><circle id="{{ID}}-r0" cx="{CP[TGT][0]}" cy="{CP[TGT][1]}" r="170" fill="none" stroke="rgba(255,255,255,.35)" stroke-width="4" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/><circle id="{{ID}}-r1" cx="{CP[TGT][0]}" cy="{CP[TGT][1]}" r="96" fill="none" stroke="@@ACCENT@@" stroke-width="7" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/><circle id="{{ID}}-burst" cx="{CP[TGT][0]}" cy="{CP[TGT][1]}" r="60" fill="none" stroke="@@ACCENT@@" stroke-width="6" opacity="0"/></svg>
""",
    """.crowd{position:absolute;inset:0;z-index:3}
    .pp{position:absolute;width:88px;height:88px;color:rgba(242,240,236,.4)}
    .spot{position:absolute;left:0;top:0;width:340px;height:340px;margin:-170px 0 0 -170px;border-radius:50%;background:radial-gradient(closest-side, rgba(@@ACCENT_RGB@@,.5), rgba(@@ACCENT_RGB@@,0));z-index:2}
    .tg{position:absolute;left:0;top:0;z-index:4;overflow:visible}""",
    """const CP = """ + json.dumps(CP) + """, TG = """ + str(TGT) + """;
    for (let i=0;i<48;i++) tl.fromTo(q("p"+i), {opacity:0, scale:0.3}, {opacity:1, scale:1, duration:0.35, ease:"back.out(2)"}, Math.max(0, T(20.75) + ((i*7)%48)*0.012));
    const path = [[200,640],[880,760],[380,1240],[800,1100],CP[TG]];
    tl.fromTo(q("spot"), {x:path[0][0], y:path[0][1], opacity:0}, {opacity:1, duration:0.3}, T(20.95));
    [[21.25,1,"power2.inOut"],[21.7,2,"power2.inOut"],[22.15,3,"power2.inOut"],[22.6,4,"back.out(1.4)"]].forEach(function(k){ tl.to(q("spot"), {x:path[k[1]][0], y:path[k[1]][1], duration:0.42, ease:k[2]}, T(k[0])); });
    tl.to("#"+ID+"-box .pp", {opacity:0.25, duration:0.3}, T(22.95));
    tl.to(q("p"+TG), {color:"@@ACCENT@@", opacity:1, scale:1.7, duration:0.4, ease:"back.out(2.4)"}, T(22.97));
    draw(tl, "r1", 23.0, 0.35); draw(tl, "r0", 23.08, 0.45);
    tl.fromTo(q("burst"), {attr:{r:60}, opacity:0.9}, {attr:{r:360}, opacity:0, duration:0.6, ease:"power2.out"}, T(23.05));""")

# ------------------------------------------------------------------ 07 Funnel (split; visible from 27.6)
fall = ""
FX = [120, 820, 300, 640, 470, 900, 200, 560, 380, 740, 150, 660, 430, 870]
for i, x in enumerate(FX):
    fall += f'<div class="fd de-tile" id="{{ID}}-f{i}" style="left:{x}px"><img src="{R(i % 16 + 1)}"/></div>'
scene("s07-avatar", 23.70, 31.40, False, f"""
    <div class="fall">{fall}</div>
    <div id="{{ID}}-t0" class="tier" style="left:110px;top:230px;width:860px">TOP</div>
    <div id="{{ID}}-t1" class="tier" style="left:210px;top:408px;width:660px">MIDDLE</div>
    <div id="{{ID}}-t2" class="tier tb" style="left:300px;top:586px;width:480px">BOTTOM</div>
    <div id="{{ID}}-out" class="de-tile de-hot pop"><img src="{R(4)}"/></div>
""",
    """.tier{position:absolute;height:150px;clip-path:polygon(0 0,100% 0,92% 100%,8% 100%);background:rgba(60,60,60,.92);display:flex;align-items:center;justify-content:center;font-family:"HelvB";font-size:50px;letter-spacing:-.03em;z-index:5}
    .fall{position:absolute;inset:0;z-index:4}
    .fd{width:72px;height:128px;top:60px;border-radius:12px;opacity:0}
    .pop{left:490px;top:640px;width:100px;height:178px;border-radius:14px;opacity:0;z-index:6}""",
    """[0,1,2].forEach(function(i){ tl.fromTo(q("t"+i), {opacity:0, y:24, scaleX:0.6}, {opacity:1, y:0, scaleX:1, duration:0.4, ease:"back.out(1.6)"}, T(27.05 + i*0.12)); });
    const FX = """ + json.dumps(FX) + """;
    for (let i=0;i<FX.length;i++){ const g = 27.3 + i*0.27; const tx = 540 - 36 - FX[i];
      tl.fromTo(q("f"+i), {opacity:0, x:0, y:-40, scale:1, rotation:(i%2?14:-14)}, {opacity:1, duration:0.18}, T(g));
      tl.to(q("f"+i), {x:tx*0.85, y:600, scale:0.35, rotation:0, duration:1.25, ease:"power2.in"}, T(g));
      tl.to(q("f"+i), {opacity:0, duration:0.2}, T(g + 1.1)); }
    tl.to(q("t2"), {background:"rgba(@@ACCENT_RGB@@,1)", duration:0.4}, T(30.1));
    tl.fromTo(q("t2"), {scale:1}, {scale:1.06, duration:0.2, yoyo:true, repeat:1}, T(30.1));
    tl.fromTo(q("out"), {opacity:0, y:-40, scale:0.6}, {opacity:1, y:120, scale:1, duration:0.55, ease:"back.out(1.8)"}, T(30.3));""")

# ------------------------------------------------------------------ 08 Subject (split; visible 31.40-34.05)
scene("s08-subject", 31.40, 38.00, False, f"""
    <div class="st">
      <div id="{{ID}}-av" class="rc de-tile"><img src="{R(6)}"/><div class="cap">“If you’re a coach who…”</div></div>
      <div id="{{ID}}-sb" class="rc de-tile"><img src="{R(2)}"/><div class="cap">“The hook mistake killing your views”</div></div>
    </div>
    <div id="{{ID}}-la" class="de-label lb" style="left:120px">AVATAR ✕</div>
    <div id="{{ID}}-ls" class="de-label lb" style="left:620px;color:var(--o)">SUBJECT ✓</div>
""",
    """.st{position:absolute;inset:0;perspective:1400px;z-index:4}
    .rc{width:340px;height:604px;top:120px}
    #{ID}-av{left:120px} #{ID}-sb{left:620px}
    .cap{position:absolute;left:14px;right:14px;top:190px;padding:14px 16px;border-radius:14px;background:rgba(10,10,10,.88);font-family:"HelvB";font-size:30px;letter-spacing:-.03em;line-height:1.12;text-align:center}
    .lb{position:absolute;top:760px;width:340px;text-align:center;z-index:5;font-size:26px}""",
    """tl.fromTo(q("av"), {opacity:0, y:50, rotationY:0}, {opacity:1, y:0, duration:0.5, ease:"power3.out"}, T(31.0));
    tl.fromTo(q("sb"), {opacity:0, y:50}, {opacity:1, y:0, duration:0.5, ease:"power3.out"}, T(31.1));
    tl.fromTo(q("la"), {opacity:0}, {opacity:1, duration:0.3}, T(31.3)); tl.fromTo(q("ls"), {opacity:0}, {opacity:1, duration:0.3}, T(32.6));
    tl.to(q("av"), {rotationY:38, x:-40, scale:0.9, opacity:0.45, filter:"grayscale(1)", duration:0.6, ease:"power3.inOut"}, T(32.05));
    tl.to(q("sb"), {rotationY:-8, x:-60, scale:1.08, duration:0.6, ease:"back.out(1.6)"}, T(32.5));
    tl.to(q("sb"), {borderColor:"@@ACCENT@@", boxShadow:"0 0 60px rgba(@@ACCENT_RGB@@,.55)", duration:0.3}, T(32.6));
    tl.to(q("ls"), {x:-60, duration:0.6, ease:"back.out(1.6)"}, T(32.5));
    tl.fromTo(q("sb"), {y:-6}, {y:6, duration:1.1, yoyo:true, repeat:3, ease:"sine.inOut"}, T(33.1));""")

# ------------------------------------------------------------------ 09 Curiosity (FULL) — heartbeat → flatline → the matrix completes, C3 bursts
pts, pts2 = [], []
for i in range(0, 121):
    x = i * 4.5; u = i / 200; ph = (u * 7) % 1
    y = 170 - (150 if 0.42 < ph < 0.5 else (-80 if 0.5 < ph < 0.56 else 0)) * (1 - 0.2 * u)
    pts.append(f"{x:.1f},{y:.1f}")
for i in range(120, 201):
    pts2.append(f"{i*4.5:.1f},170")
rays = "".join(f'<div class="ray" style="transform:rotate({i*15}deg)"><i></i></div>' for i in range(24))
scene("s09-curiosity", 38.00, 43.05, True, f"""
    <div id="{{ID}}-A">
      <svg class="ecg" width="900" height="340" viewBox="0 0 900 340"><polyline id="{{ID}}-e1" points="{' '.join(pts)}" fill="none" stroke="@@ACCENT@@" stroke-width="9" stroke-linejoin="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/><polyline id="{{ID}}-e2" points="{' '.join(pts2)}" fill="none" stroke="rgba(255,255,255,.6)" stroke-width="9" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/></svg>
      <div id="{{ID}}-lv" class="lab" style="left:90px;color:var(--o)">LIVE</div>
      <div id="{{ID}}-ld" class="lab" style="right:90px;color:var(--grey)">OR DIE</div>
    </div>
    <div id="{{ID}}-B">
      <div id="{{ID}}-rays" class="rays">{rays}</div>
      <div class="stack" style="top:630px">{mcards("m", filled=(0, 1))}</div>
    </div>
""",
    MCSS + """
    .ecg{position:absolute;left:90px;top:760px;overflow:visible;z-index:5}
    .lab{position:absolute;top:1150px;font-family:"HelvB";font-size:54px;letter-spacing:.02em;z-index:5}
    .rays{position:absolute;left:540px;top:1190px;width:0;height:0;z-index:3}
    .ray{position:absolute;left:0;top:-3px;width:900px;height:6px;transform-origin:0 50%}
    .ray i{display:block;margin-left:470px;width:300px;height:6px;border-radius:3px;background:linear-gradient(90deg, rgba(@@ACCENT_RGB@@,.9), rgba(@@ACCENT_RGB@@,0));transform-origin:0 50%}""",
    """tl.fromTo(q("e1"), {strokeDashoffset:1000}, {strokeDashoffset:0, duration:3.1, ease:"none"}, T(37.45));
    tl.fromTo(q("lv"), {opacity:0, scale:0.7}, {opacity:1, scale:1, duration:0.35, ease:"back.out(2)"}, T(40.15));
    tl.to(q("e1"), {stroke:"rgba(255,255,255,.6)", duration:0.25}, T(40.7));
    tl.fromTo(q("e2"), {strokeDashoffset:1000}, {strokeDashoffset:0, duration:0.6, ease:"power1.out"}, T(40.7));
    tl.fromTo(q("ld"), {opacity:0}, {opacity:1, duration:0.3}, T(40.75));
    tl.to(q("A"), {opacity:0, scale:0.94, filter:"blur(10px)", duration:0.3, ease:"power2.in"}, T(41.55));
    [41.75, 41.93, 42.11].forEach(function(g,i){ tl.fromTo(q("m"+i), {opacity:0, y:90, scale:0.82}, {opacity:1, y:0, scale:1, duration:0.42, ease:"back.out(1.9)"}, T(g)); });
    tl.to(q("m2"), {borderColor:"@@ACCENT@@", boxShadow:"0 0 60px rgba(@@ACCENT_RGB@@,.55)", duration:0.2}, T(42.36));
    tl.to("#"+ID+"-m2 .mn", {color:"@@ACCENT@@", duration:0.2}, T(42.36));
    tl.to("#"+ID+"-m2 .qq", {opacity:0, duration:0.15}, T(42.36));
    tl.fromTo(q("mk2"), {opacity:0, scaleX:1.35, filter:"blur(12px)", transformOrigin:"0% 50%"}, {opacity:1, scaleX:1, filter:"blur(0px)", duration:0.4, ease:"expo.out"}, T(42.38));
    tl.fromTo("#"+ID+"-rays .ray i", {scaleX:0, opacity:1}, {scaleX:1, duration:0.5, ease:"expo.out", stagger:0.012}, T(42.38));
    tl.fromTo(q("rays"), {rotation:0}, {rotation:22, duration:0.7, ease:"power1.out"}, T(42.38));""")

# ------------------------------------------------------------------ 10 Open a loop (split, after FULL → prebuilt)
EYE = '<svg viewBox="0 0 120 70" width="200" height="117"><path d="M5,35 C30,2 90,2 115,35 C90,68 30,68 5,35 Z" fill="none" stroke="@@PAPER@@" stroke-width="7" stroke-linejoin="round"/><circle cx="60" cy="35" r="15" fill="@@PAPER@@"/></svg>'
CHECK = '<svg viewBox="0 0 120 120" width="210" height="210"><path id="{ID}-chk" d="M22,64 L50,92 L100,32" fill="none" stroke="@@ACCENT@@" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/></svg>'
scene("s10-loop", 43.05, 49.60, False, f"""
    <div id="{{ID}}-A">
      <div id="{{ID}}-tz" class="tz de-tile"><img class="bl" src="{R(8)}"/><div id="{{ID}}-rev" class="rev"><img src="{R(8)}"/></div><div id="{{ID}}-edge" class="edge"></div></div>
      <div id="{{ID}}-qm" class="qm">?</div>
    </div>
    <div id="{{ID}}-B">
      <svg class="ring" width="1080" height="960"><circle cx="540" cy="480" r="300" fill="none" stroke="rgba(255,255,255,.12)" stroke-width="26"/><circle id="{{ID}}-arc" cx="540" cy="480" r="300" fill="none" stroke="@@ACCENT@@" stroke-width="26" stroke-linecap="round" pathLength="1" stroke-dasharray="0 1" transform="rotate(-90 540 480)"/></svg>
      <div id="{{ID}}-rider" class="rider de-tile de-hot"><img src="{R(8)}"/></div>
      <div id="{{ID}}-eye" class="mid">{EYE}</div>
      <div id="{{ID}}-ok" class="mid">{CHECK}</div>
    </div>
""",
    """.tz{left:340px;top:124px;width:400px;height:711px;z-index:4}
    .tz .bl{filter:blur(24px) brightness(.7);transform:scale(1.15)}
    .rev{position:absolute;inset:0;clip-path:inset(0 100% 0 0)} .rev img{width:100%;height:100%;object-fit:cover}
    .edge{position:absolute;top:0;bottom:0;left:0;width:6px;background:var(--o);box-shadow:0 0 18px rgba(@@ACCENT_RGB@@,.9);opacity:0}
    .qm{position:absolute;left:340px;width:400px;top:300px;text-align:center;font-family:"PlayIt";font-style:italic;font-size:330px;line-height:1;color:var(--o);text-shadow:0 0 50px rgba(@@ACCENT_RGB@@,.7);z-index:6}
    .ring{position:absolute;left:0;top:0;z-index:4;overflow:visible}
    .rider{width:104px;height:185px;left:488px;top:87px;border-radius:14px;z-index:6;opacity:0}
    .mid{position:absolute;left:0;right:0;top:375px;height:210px;display:flex;align-items:center;justify-content:center;z-index:6;opacity:0}""",
    """tl.fromTo(q("tz"), {opacity:0, y:50, rotationX:20, transformPerspective:1200}, {opacity:1, y:0, rotationX:0, duration:0.5, ease:"power3.out"}, T(42.55));
    tl.fromTo(q("qm"), {opacity:0, scale:0.6}, {opacity:1, scale:1, duration:0.5, ease:"back.out(2)"}, T(42.6));
    tl.fromTo(q("qm"), {rotation:-5}, {rotation:5, duration:0.7, yoyo:true, repeat:3, ease:"sine.inOut"}, T(43.1));
    const RV = {v:100}; const rev = document.getElementById(ID+"-rev"), edge = document.getElementById(ID+"-edge");
    function ru(){ rev.style.clipPath = "inset(0 " + RV.v.toFixed(2) + "% 0 0)"; edge.style.transform = "translateX(" + (400*(1-RV.v/100)).toFixed(1) + "px)"; }
    tl.fromTo(q("edge"), {opacity:0}, {opacity:1, duration:0.15}, T(43.55));
    tl.fromTo(RV, {v:100}, {v:66, duration:0.5, ease:"power3.out", onUpdate:ru}, T(43.55));
    tl.to(RV, {v:74, duration:0.35, ease:"power2.inOut", onUpdate:ru}, T(44.2));
    tl.to(RV, {v:58, duration:0.5, ease:"power2.inOut", onUpdate:ru}, T(44.9));
    tl.to(q("A"), {opacity:0, filter:"blur(10px)", duration:0.3}, T(45.6));
    tl.fromTo(q("B"), {opacity:0}, {opacity:1, duration:0.01}, T(45.85));
    const ARC = {v:0}; const arc = document.getElementById(ID+"-arc"); const rider = document.getElementById(ID+"-rider");
    function upd(){ arc.setAttribute("stroke-dasharray", ARC.v.toFixed(4) + " 1"); const th = -Math.PI/2 + ARC.v*Math.PI*2; rider.style.transform = "translate(" + (Math.cos(th)*300).toFixed(1) + "px," + (Math.sin(th)*300 + 300).toFixed(1) + "px) rotate(" + (ARC.v*360).toFixed(1) + "deg)"; }
    tl.fromTo(ARC, {v:0}, {v:0.82, duration:1.6, ease:"power2.inOut", onUpdate:upd}, T(45.9));
    tl.to(ARC, {v:0.86, duration:1.4, ease:"sine.inOut", onUpdate:upd}, T(47.5));
    tl.to(ARC, {v:1, duration:0.45, ease:"power3.in", onUpdate:upd}, T(48.95));
    tl.fromTo(q("rider"), {opacity:0}, {opacity:1, duration:0.2}, T(45.95));
    tl.to(q("arc"), {filter:"drop-shadow(0 0 22px rgba(@@ACCENT_RGB@@,.9))", duration:0.3}, T(49.35));
    tl.fromTo(q("eye"), {opacity:0, scale:0.7}, {opacity:1, scale:1, duration:0.35, ease:"back.out(2)"}, T(47.6));
    tl.fromTo(q("eye"), {scaleY:1}, {scaleY:0.1, duration:0.09, yoyo:true, repeat:1}, T(48.3));
    tl.to(q("eye"), {opacity:0, duration:0.15}, T(49.25));
    tl.fromTo(q("ok"), {opacity:0, scale:0.6}, {opacity:1, scale:1, duration:0.3, ease:"back.out(2.4)"}, T(49.32));
    draw(tl, "chk", 49.32, 0.25);""")

# ------------------------------------------------------------------ 11 Loops (FULL; visible from 51.45) — loops along a timeline + retention graph
LOOPS = [[90, 270], [250, 450], [430, 620], [600, 800], [780, 990]]
arcs = ""
for i, (a, b) in enumerate(LOOPS):
    r = (b - a) / 2
    arcs += f'<path id="{{ID}}-a{i}" d="M{a},760 A{r},{r} 0 0 1 {b},760" fill="none" stroke="rgba(255,255,255,.9)" stroke-width="10" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/><circle id="{{ID}}-d{i}" cx="{b}" cy="760" r="0" fill="@@ACCENT@@"/><text id="{{ID}}-st{i}" x="{b}" y="840" text-anchor="middle" font-family="HelvB" font-size="46" fill="@@ACCENT@@" opacity="0">★</text>'
scene("s11-loops", 49.60, 55.80, True, f"""
    <svg class="tlsvg" width="1080" height="1920"><line x1="90" y1="760" x2="990" y2="760" stroke="rgba(255,255,255,.3)" stroke-width="8" stroke-linecap="round"/><line id="{{ID}}-prog" x1="90" y1="760" x2="90" y2="760" stroke="@@ACCENT@@" stroke-width="8" stroke-linecap="round"/>{arcs}<circle id="{{ID}}-ph" cx="90" cy="760" r="19" fill="@@PAPER@@"/></svg>
    <div class="chart"><div class="de-label" style="position:absolute;left:0;top:-52px;font-size:26px">RETENTION</div><div id="{{ID}}-pct" class="pct de-num">100%</div>
      <svg width="900" height="400" viewBox="0 0 900 400" style="overflow:visible"><line x1="0" y1="400" x2="900" y2="400" stroke="rgba(255,255,255,.3)" stroke-width="3"/><line x1="0" y1="0" x2="0" y2="400" stroke="rgba(255,255,255,.3)" stroke-width="3"/><polyline points="0,24 120,146 300,285 520,352 900,386" fill="none" stroke="rgba(255,255,255,.34)" stroke-width="6" stroke-dasharray="12 14"/><polyline id="{{ID}}-ret" points="0,24 90,73 180,53 270,100 360,75 460,116 530,90 640,126 710,102 840,134 900,112" fill="none" stroke="@@ACCENT@@" stroke-width="9" stroke-linejoin="round" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/></svg>
      <div class="lg"><span style="color:var(--o)">━ with loops</span>   <span style="color:var(--grey)">┅ without</span></div></div>
""",
    """.tlsvg{position:absolute;left:0;top:0;z-index:5;overflow:visible}
    .chart{position:absolute;left:90px;top:1000px;width:900px;height:400px;z-index:4}
    .pct{position:absolute;right:0;top:-84px;font-size:76px;color:var(--o)}
    .lg{position:absolute;left:0;top:420px;font-family:"HelvB";font-size:28px;letter-spacing:.02em;white-space:pre}""",
    """const LOOPS = """ + json.dumps(LOOPS) + """;
    const PH = {x:90}; const ph = document.getElementById(ID+"-ph"), pr = document.getElementById(ID+"-prog");
    function upd(){ ph.setAttribute("cx", PH.x.toFixed(1)); pr.setAttribute("x2", PH.x.toFixed(1)); }
    tl.fromTo(PH, {x:90}, {x:990, duration:T(55.6) - T(49.7), ease:"none", onUpdate:upd}, T(49.7));
    tl.fromTo(q("ret"), {strokeDashoffset:1000}, {strokeDashoffset:0, duration:T(55.6) - T(49.7), ease:"none"}, T(49.7));
    const PC = {v:100}; const pe = document.getElementById(ID+"-pct");
    tl.fromTo(PC, {v:100}, {v:78, duration:T(55.6) - T(49.7), ease:"power1.out", onUpdate:function(){ pe.textContent = Math.round(PC.v) + "%"; }}, T(49.7));
    const sp = (990-90)/(T(55.6)-T(49.7));
    LOOPS.forEach(function(L,i){ const t0 = T(49.7) + (L[0]-90)/sp, t1 = T(49.7) + (L[1]-90)/sp;
      tl.fromTo(q("a"+i), {strokeDashoffset:1000}, {strokeDashoffset:0, duration:t1-t0, ease:"none"}, t0);
      tl.to(q("a"+i), {stroke:"@@ACCENT@@", duration:0.15}, t1);
      tl.fromTo(q("d"+i), {attr:{r:0}}, {attr:{r:17}, duration:0.35, ease:"back.out(3)"}, t1);
      tl.fromTo(q("st"+i), {opacity:0, scale:0.3, transformOrigin:"50% 50%"}, {opacity:1, scale:1, duration:0.35, ease:"back.out(3)"}, Math.max(t1, T(53.9) + i*0.06)); });""")

# ------------------------------------------------------------------ 12 Claude skill (split, after FULL → prebuilt)
REW = "“Stuck on a few hundred views? Your hook is missing one of these 3 things.”"
scene("s12-skill", 55.80, 60.50, False, f"""
    <div id="{{ID}}-card" class="chat de-glass">
      <div class="top"><span class="sq"></span>3C Hook Matrix <span style="color:var(--grey);font-family:HelvR">· skill</span></div>
      <div id="{{ID}}-u" class="ub">“5 tips to grow on Instagram”</div>
      <div id="{{ID}}-r0" class="row"><span class="ic x">✕</span><b>Change</b><span class="d">no gain or loss</span></div>
      <div id="{{ID}}-r1" class="row"><span class="ic ok">✓</span><b>Clarity</b><span class="d">subject is clear</span></div>
      <div id="{{ID}}-r2" class="row"><span class="ic x">✕</span><b>Curiosity</b><span class="d">no open loop</span></div>
      <div id="{{ID}}-rw" class="rw de-hot"><div class="de-label" style="color:@@ACCENT_LIGHT@@;font-size:20px">REWRITE</div><div id="{{ID}}-txt" class="txt"></div></div>
      <div class="chips"><span id="{{ID}}-c0" class="de-chip on cc">✓ Change</span><span id="{{ID}}-c1" class="de-chip on cc">✓ Clarity</span><span id="{{ID}}-c2" class="de-chip on cc">✓ Curiosity</span></div>
    </div>
""",
    """.chat{position:absolute;left:70px;top:96px;width:940px;height:768px;padding:28px 38px;box-sizing:border-box;z-index:5;font-family:-apple-system,"HelvR",sans-serif;background:rgba(20,20,20,.94)}
    .top{display:flex;align-items:center;gap:12px;font-family:"HelvB";font-size:28px;padding-bottom:18px;border-bottom:1px solid rgba(255,255,255,.14)}
    .sq{width:30px;height:30px;border-radius:8px;background:var(--o);display:inline-block}
    .ub{margin:22px 0 0 auto;width:max-content;padding:18px 26px;border-radius:24px;background:rgba(255,255,255,.14);font-size:32px}
    .row{display:flex;align-items:center;gap:16px;height:60px;font-size:31px;margin-top:6px}
    .row b{font-family:"HelvB";width:180px} .row .d{color:var(--grey)}
    .ic{width:38px;height:38px;border-radius:19px;display:flex;align-items:center;justify-content:center;font-family:"HelvB";font-size:23px}
    .ic.x{border:2px solid rgba(255,255,255,.4);color:var(--grey)} .ic.ok{background:var(--o);color:@@ON_ACCENT@@}
    .rw{margin-top:20px;padding:20px 26px;border-radius:24px;background:rgba(40,24,12,.96);min-height:142px;box-sizing:border-box}
    .txt{font-family:"HelvB";font-size:34px;letter-spacing:-.02em;line-height:1.22;margin-top:6px}
    .chips{display:flex;gap:14px;margin-top:22px} .cc{font-size:26px;padding:8px 18px;border-radius:12px}""",
    """tl.fromTo(q("card"), {opacity:0, y:60, rotationX:18, transformPerspective:1400}, {opacity:1, y:0, rotationX:0, duration:0.5, ease:"power3.out"}, T(55.3));
    tl.fromTo(q("u"), {opacity:0, x:80, scale:0.9}, {opacity:1, x:0, scale:1, duration:0.4, ease:"back.out(1.8)"}, T(55.4));
    [57.6, 57.8, 58.0].forEach(function(g,i){ tl.fromTo(q("r"+i), {opacity:0, x:-50}, {opacity:1, x:0, duration:0.3, ease:"power3.out"}, T(g)); });
    tl.fromTo(q("rw"), {opacity:0, y:20}, {opacity:1, y:0, duration:0.35, ease:"power3.out"}, T(58.35));
    const TXT = """ + json.dumps(REW) + """; const te = document.getElementById(ID+"-txt"); const K = {n:0};
    tl.fromTo(K, {n:0}, {n:TXT.length, duration:1.1, ease:"none", onUpdate:function(){ te.textContent = TXT.slice(0, Math.round(K.n)) + (K.n < TXT.length ? "▍" : ""); }}, T(58.45));
    [59.3, 59.45, 59.6].forEach(function(g,i){ pop(tl, "c"+i, g); });""")

# ------------------------------------------------------------------ 13 CTA (FULL) — comment box types HOOKS, posts, the DM lands
scene("s13-cta", 60.50, DUR, True, f"""
    <div id="{{ID}}-sk" class="sk de-glass"><span class="sq2"></span><div><div class="t1">3C Hook Matrix</div><div class="t2">Claude skill · analyze + rewrite</div></div><span id="{{ID}}-free" class="free">100% FREE</span></div>
    <div id="{{ID}}-cm" class="cm de-glass"><div class="av"></div><div class="inp"><span id="{{ID}}-ty" class="ty"></span></div><div id="{{ID}}-send" class="send">Post</div></div>
    <div id="{{ID}}-dm" class="dm de-glass de-hot"><div class="dav">@</div><div><div class="d1">@@HANDLE@@</div><div class="d2">Here’s your 3C Hook skill 🔥</div></div></div>
""",
    """.sk{position:absolute;left:90px;top:560px;width:900px;padding:34px 38px;box-sizing:border-box;display:flex;align-items:center;gap:24px;z-index:5;background:rgba(20,20,20,.94)}
    .sq2{width:84px;height:84px;border-radius:20px;background:var(--o);flex:none}
    .t1{font-family:"HelvB";font-size:48px;letter-spacing:-.02em} .t2{font-family:"HelvR";font-size:30px;color:var(--grey);margin-top:6px}
    .free{margin-left:auto;padding:12px 22px;border-radius:14px;border:3px solid var(--o);box-shadow:0 0 34px rgba(@@ACCENT_RGB@@,.45);font-family:"HelvB";font-size:30px;letter-spacing:.08em;white-space:nowrap}
    .cm{position:absolute;left:90px;top:800px;width:900px;height:150px;display:flex;align-items:center;gap:24px;padding:0 32px;box-sizing:border-box;border-radius:75px;z-index:5;background:rgba(20,20,20,.94)}
    .av{width:86px;height:86px;border-radius:43px;background:linear-gradient(135deg,#555,#2a2a2a);flex:none}
    .inp{flex:1;font-family:"HelvB";font-size:64px;letter-spacing:-.02em} .send{font-family:"HelvB";font-size:42px;color:var(--o)}
    .dm{position:absolute;left:90px;top:1030px;width:900px;padding:30px 34px;box-sizing:border-box;display:flex;align-items:center;gap:24px;z-index:5;background:rgba(20,20,20,.96)}
    .dav{width:92px;height:92px;border-radius:46px;background:var(--o);color:@@ON_ACCENT@@;font-family:"HelvB";font-size:50px;display:flex;align-items:center;justify-content:center;flex:none}
    .d1{font-family:"HelvB";font-size:36px} .d2{font-family:"HelvR";font-size:40px;margin-top:6px}""",
    """tl.fromTo(q("sk"), {opacity:0, y:-40, scale:0.9}, {opacity:1, y:0, scale:1, duration:0.4, ease:"back.out(1.8)"}, T(60.1));
    pop(tl, "free", 61.22, {r:-8});
    tl.fromTo(q("cm"), {opacity:0, y:40}, {opacity:1, y:0, duration:0.4, ease:"power3.out"}, T(61.3));
    const W = "HOOKS", ty = document.getElementById(ID+"-ty"), K = {n:0};
    tl.fromTo(K, {n:0}, {n:W.length, duration:0.45, ease:"none", onUpdate:function(){ ty.textContent = W.slice(0, Math.round(K.n)) + (K.n < W.length ? "▍" : ""); }}, T(61.8));
    tl.fromTo(q("send"), {scale:1}, {scale:0.8, duration:0.09, yoyo:true, repeat:1, ease:"power2.in"}, T(62.3));
    tl.to(q("cm"), {borderColor:"@@ACCENT@@", duration:0.2}, T(62.35));
    tl.fromTo(q("dm"), {opacity:0, y:-50, scale:0.9}, {opacity:1, y:0, scale:1, duration:0.45, ease:"back.out(1.8)"}, T(62.55));""")

E.build()
