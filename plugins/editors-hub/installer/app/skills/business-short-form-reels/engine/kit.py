#!/usr/bin/env python3
"""Reusable components in the pack's default reel style so a new reel's build.py stays short.
    import reel_engine as E, kit as K
    K.stack(...), K.count(...), K.shots(...), K.versus(...), K.notifs(...), K.gdoc(...), K.chat(...), K.graph(...), K.raw(...)   -> scenes
    K.hook(...), K.bps(...), K.lps(...), K.word(...), K.nums(...), K.tiles(...), K.carousel(...)  -> face-window overlays; call K.flush() before E.build()
Split scenes: design box 1080 x 560 (the engine shifts it under the top edge). Full scenes: 1080 x 1920, graphic in y 330-1100 (engine scales to 84%).
All times are GLOBAL seconds on the cut. Every scene call also records a glide-in for the sound mix (K.GL) and accents go in K.AC."""
import json, os
import reel_engine as E
from reel_engine import scene as _scene

GL, AC = [], []          # sound: glide-in times, accents [(t, name, level)]
OB, OF, OC, OJ = [], [], [], []
R = lambda i: f"assets/reels/r{i:02d}.jpg"
PERSON = '<svg viewBox="0 0 24 24" width="100%" height="100%"><circle cx="12" cy="7.6" r="4.3" fill="currentColor"/><path d="M3.2,22 C4.2,15.2 19.8,15.2 20.8,22 Z" fill="currentColor"/></svg>'
CHK = '<svg viewBox="0 0 40 40" width="54" height="54"><circle cx="20" cy="20" r="19" fill="@@ACCENT@@"/><path d="M11,21 L17.5,27 L29,14" fill="none" stroke="@@ON_ACCENT@@" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
def ac(t, name, lv=-21): AC.append((round(t, 3), name, lv))

def scene(sid, a, b, full, body, css, js):
    vis = next((y for x, y in E.FACE if x - 0.001 <= a < y), a) if not full else a
    GL.append(round(vis, 3)); return _scene(sid, a, b, full, body, css, js)
raw = scene

R3D = 'tl.set(q("%s"), {transformPerspective:1500, transformOrigin:"50%% 100%%"}, 0); __ft(q("%s"), {rotationX:52, y:120, scale:0.78}, {rotationX:0, y:0, scale:1, duration:0.95, ease:"expo.out"}, T(%s));'
R3D = R3D.replace('q("%s"), {rotationX', 'q("%s"), {rotationX')
def _vis(a, full): return a if full else next((y for x, y in E.FACE if x - 0.001 <= a < y), a)

# ------------------------------------------------------------------ icons
def igicon(u): return ('<svg viewBox="0 0 48 48" width="50" height="50"><defs><radialGradient id="igG%s" cx="30%%" cy="107%%" r="150%%"><stop offset="0" stop-color="#FEDA75"/><stop offset=".25" stop-color="#FA7E1E"/>'
    '<stop offset=".5" stop-color="#D62976"/><stop offset=".75" stop-color="#962FBF"/><stop offset="1" stop-color="#4F5BD5"/></radialGradient></defs><rect width="48" height="48" rx="12" fill="url(#igG%s)"/>'
    '<rect x="11" y="11" width="26" height="26" rx="8" fill="none" stroke="#fff" stroke-width="3"/><circle cx="24" cy="24" r="6.5" fill="none" stroke="#fff" stroke-width="3"/><circle cx="32.2" cy="15.8" r="1.9" fill="#fff"/></svg>') % (u, u)
def ig(sz=64, u="x"): return igicon(u).replace('width="50" height="50"', 'width="%d" height="%d"' % (sz, sz))
def yt(sz=64): return '<svg viewBox="0 0 48 48" width="%d" height="%d"><rect x="2" y="9" width="44" height="30" rx="9" fill="#FF0000"/><path d="M20,17 L32,24 L20,31 Z" fill="#fff"/></svg>' % (sz, sz)
def mail(sz=64): return '<svg viewBox="0 0 48 48" width="%d" height="%d"><rect x="3" y="9" width="42" height="30" rx="6" fill="@@PAPER@@"/><path d="M6,13 L24,27 L42,13" fill="none" stroke="@@ON_ACCENT@@" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>' % (sz, sz)
DOCI = '<svg viewBox="0 0 48 64" width="38" height="50"><path d="M4,0 H30 L48,18 V60 a4,4 0 0 1 -4,4 H4 a4,4 0 0 1 -4,-4 V4 a4,4 0 0 1 4,-4 Z" fill="#4285F4"/><path d="M30,0 L48,18 H34 a4,4 0 0 1 -4,-4 Z" fill="#A1C2FA"/><path d="M11,30 H37 M11,38 H37 M11,46 H29" stroke="#fff" stroke-width="3.4" stroke-linecap="round"/></svg>'
ANON = '<svg viewBox="0 0 24 24" width="112" height="112"><rect width="24" height="24" fill="#3A3A3C"/><circle cx="12" cy="9.4" r="4.2" fill="#8E8E93"/><path d="M3.4,24 C4.2,16.4 19.8,16.4 20.6,24 Z" fill="#8E8E93"/></svg>'

# ------------------------------------------------------------------ stacked glass pills
def stack(sid, a, b, full, items, times, light=(), dim=(), strike=(), reveal=(), good=(), bad=(), widths=None, w=None, solid=False, rig=False, extra="", xcss="", xjs=""):
    """items: label or (lead, label) - lead is a number / icon svg. times: entrance per pill. light=[(i,t)], dim=[([i..],t)], strike=[(i,t)] (deep red line, then dims)."""
    n = len(items)
    if full: W, H, G, FS, NS = w or 840, (170 if n <= 4 else 140), 26, (50 if n <= 4 else 44), 74; top = 730 - (n * (H + G) - G) // 2
    else: W, H, G, FS, NS = w or 700, (112 if n >= 4 else 132), 18, (38 if n >= 4 else 42), 54; top = max(6, (556 - (n * (H + G) - G)) // 2)
    html = ""; rv = dict(reveal)
    for i, it in enumerate(items):
        lead, lab = it if isinstance(it, (tuple, list)) else ("", it)
        Wi = widths[i] if widths else W; left = (1080 - Wi) // 2
        if i in rv: lab = '<span id="{ID}-q%d" class="qq">? ? ?</span><span id="{ID}-k%d" class="kw">%s</span>' % (i, i, lab)
        html += (('<div id="{ID}-m%d" class="mc' + (" solid" if solid else "") + '" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx;border-radius:%dpx">%s<span class="mw">%s</span><i id="{ID}-x%d" class="sx"></i></div>')
                 % (i, left, top + i * (H + G), Wi, H, H // 2, ('<span class="mn">%s</span>' % lead) if lead != "" else "", lab, i))
    css = """.mc{position:absolute;display:flex;align-items:center;justify-content:center;gap:26px;padding:0 44px;box-sizing:border-box;z-index:5;opacity:0}
    .mn{font-family:"HelvB";font-size:%dpx;line-height:1;letter-spacing:-.06em;color:rgba(255,255,255,.5);display:flex;align-items:center}
    .mw{position:relative;font-family:"HelvB";font-size:%dpx;letter-spacing:-.045em;white-space:nowrap} .qq{color:rgba(255,255,255,.3)} .kw{position:absolute;left:0;top:0;opacity:0;color:var(--o)} .mw:has(.kw){min-width:5.6em}
    .sx{position:absolute;left:8%%;right:8%%;top:50%%;height:8px;margin-top:-4px;border-radius:4px;background:#B3261E;transform:scaleX(0);transform-origin:0 50%%;box-shadow:0 0 18px rgba(179,38,30,.8)}""" % (NS, FS) + xcss
    js = "".join('tl.fromTo(q("m%d"), {opacity:0, y:30}, {opacity:1, y:0, duration:0.5, ease:"power2.inOut"}, T(%s));' % (i, t) for i, t in enumerate(times))
    if solid:
        css += """ #root .mc.solid{background:#1B1917;-webkit-backdrop-filter:none;backdrop-filter:none;border:3px solid rgba(255,255,255,.34);box-shadow:0 14px 34px rgba(0,0,0,.5)}"""
        for i, t in light: js += 'tl.to(q("m%d"), {backgroundColor:"@@ACCENT@@", borderColor:"@@ACCENT_LIGHT@@", color:"@@ON_ACCENT@@", boxShadow:"0 0 50px rgba(@@ACCENT_RGB@@,.55)", duration:0.3}, T(%s));' % (i, t)
        light = ()
    for i, t in light:
        js += 'tl.to(q("m%d"), {borderColor:"@@ACCENT@@", boxShadow:"0 0 50px rgba(@@ACCENT_RGB@@,.5)", duration:0.25}, T(%s)); tl.to("#"+ID+"-m%d .mn", {color:"@@ACCENT@@", duration:0.25}, T(%s)); sweep(tl, "m%d", %s);' % (i, t, i, t, i, t)
    for ids, t in dim: js += 'tl.to([%s], {opacity:0.35, duration:0.4, ease:"power2.inOut"}, T(%s));' % (",".join('q("m%d")' % i for i in ids), t)
    for lst, col, rgb in ((good, "#2FA65A", "47,166,90"), (bad, "#B3261E", "179,38,30")):
        for i, t in lst: js += 'tl.to(q("m%d"), {borderColor:"%s", boxShadow:"0 0 50px rgba(%s,.55)", duration:0.25}, T(%s)); tl.to(["#"+ID+"-m%d .mn", "#"+ID+"-m%d .mw"], {color:"%s", duration:0.25}, T(%s)); sweep(tl, "m%d", %s);' % (i, col, rgb, t, i, i, "#7BE0A0" if col == "#2FA65A" else "#FF8A80", t, i, t)
    for i, t in reveal: js += 'tl.to(q("q%d"), {opacity:0, duration:0.15}, T(%s)); __ft(q("k%d"), {opacity:0, scaleX:1.3, filter:"blur(12px)", transformOrigin:"0%% 50%%"}, {opacity:1, scaleX:1, filter:"blur(0px)", duration:0.4, ease:"expo.out"}, T(%s));' % (i, t, i, t)
    for i, t in strike: js += '__ft(q("x%d"), {scaleX:0}, {scaleX:1, duration:0.3, ease:"power2.out"}, T(%s)); tl.to("#"+ID+"-m%d .mw", {opacity:0.45, duration:0.3}, T(%s + 0.2));' % (i, t, i, t)
    if rig:
        html = '<div id="{ID}-rig" style="position:absolute;inset:0">' + html + '</div>'
        js += 'tl.set(q("rig"), {transformPerspective:1100, transformOrigin:"50%% %dpx"}, 0); __ft(q("rig"), {rotationY:-20, rotationX:11}, {rotationY:9, rotationX:-3, duration:%s, ease:"power2.inOut"}, T(%s));' % (730 if full else 280, round(min(4.0, b - _vis(a, full)), 2), _vis(a, full))
    return scene(sid, a, b, full, html + extra, css, js + xjs)

# ------------------------------------------------------------------ counter (plain ticking number, accent colour on landing), optional real image above it
def count(sid, a, b, full, frm, to, t, label, dur=1.25, img=None, img_t=None, pre="", suf="", tone="@@ACCENT@@", xbody="", xcss="", xjs=""):
    if full: nt, lt, fs, ih = (880 if img else 590), (1040 if img else 750), 136, 500
    else: nt, lt, fs, ih = (180 if not img else 340), (330 if not img else 470), (130 if not img else 108), 300
    body = (('<div id="{ID}-plq" class="plq" style="background-image:url(%s)"></div>' % img) if img else "") + '<div id="{ID}-num" class="num de-num">%s%s%s</div><div id="{ID}-lab" class="de-label lab">%s</div>' % (pre, f"{frm:,}", suf, label) + xbody
    css = """.plq{position:absolute;left:%dpx;top:%dpx;width:%dpx;height:%dpx;border-radius:40px;border:4px solid #fff;background:#000 no-repeat center 30%%;background-size:cover;box-shadow:0 30px 80px rgba(0,0,0,.6);opacity:0;z-index:5}
    .num{position:absolute;left:0;width:1080px;top:%dpx;text-align:center;font-size:%dpx;line-height:1;color:var(--paper);opacity:0;z-index:5}
    .lab{position:absolute;left:0;width:1080px;top:%dpx;text-align:center;font-size:26px;opacity:0}""" % ((1080 - ih) // 2, 330 if full else 10, ih, ih, nt, fs, lt) + xcss
    js = ('tl.fromTo(q("plq"), {opacity:0, scale:0.9}, {opacity:1, scale:1, duration:0.5, ease:"power2.inOut"}, T(%s));' % (img_t if img_t is not None else t - 0.9) if img else "") + """
    tl.fromTo(q("num"), {opacity:0, y:30}, {opacity:1, y:0, duration:0.5, ease:"power2.inOut"}, T(%s)); tl.fromTo(q("lab"), {opacity:0}, {opacity:1, duration:0.5, ease:"power2.inOut"}, T(%s));
    const n = {v:%d}, el = document.getElementById(ID+"-num");
    __ft(n, {v:%d}, {v:%d, duration:%s, ease:"power2.inOut", onUpdate:function(){ el.textContent = "%s" + Math.round(n.v).toLocaleString("en-US") + "%s"; el.style.color = Math.abs(n.v - %d) < 1 ? "%s" : "@@PAPER@@"; }}, T(%s));""" % (t - 0.1, t, frm, frm, to, dur, pre, suf, to, tone, t)
    ac(t, "data", -24); ac(t + dur, "shine", -21)
    return scene(sid, a, b, full, body, css, js + xjs)

# ------------------------------------------------------------------ real screenshots tilting in
def shots(sid, a, b, full, items, out=None, tilt=False, xbody="", xcss="", xjs=""):
    """items: [(src, left, top, w, h, rot, t)]"""
    body = "".join('<div id="{ID}-p%d" class="shot" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx"><img src="%s"/></div>' % (i, l, tp, w, h, s) for i, (s, l, tp, w, h, r, t) in enumerate(items))
    css = """.shot{position:absolute;border-radius:26px;overflow:hidden;border:2px solid rgba(255,255,255,.18);box-shadow:0 30px 70px rgba(0,0,0,.65);z-index:4;background:#111;opacity:0}
    .shot img{width:100%;height:100%;object-fit:cover;display:block}""" + xcss
    js = "".join('tl.fromTo(q("p%d"), {opacity:0, y:%d, rotation:%s}, {opacity:1, y:0, rotation:%s, duration:0.5, ease:"power2.inOut"}, T(%s));' % (i, 40 if i % 2 else -40, r * 2, r, t) for i, (s, l, tp, w, h, r, t) in enumerate(items))
    if tilt:
        js = "".join('tl.set(q("p%d"), {transformPerspective:1300}, 0); __ft(q("p%d"), {opacity:0, x:%d, rotationY:%d}, {opacity:1, x:0, rotationY:%d, duration:0.9, ease:"power3.out"}, T(%s));'
                     % (i, i, 220 if i % 2 else -220, -40 if i % 2 else 40, -13 if i % 2 else 13, t) for i, (s_, l, tp, w, h, r, t) in enumerate(items))
    if out: js += 'tl.to([%s], {opacity:0, duration:0.35, ease:"power2.inOut"}, T(%s));' % (",".join('q("p%d")' % i for i in range(len(items))), out)
    return scene(sid, a, b, full, body + xbody, css, js + xjs)

# ------------------------------------------------------------------ two glass cards: A (plain) vs B (hot)
def versus(sid, a, b, tagA, txA, tagB, txB, tA, tB, tHot, full=True):
    top = (430, 760) if full else (20, 290); H = 236 if full else 230
    body = """<div id="{ID}-a" class="sc" style="top:%dpx"><div class="tg">%s</div><div class="tx">%s</div></div><div id="{ID}-ln" class="ln"></div>
    <div id="{ID}-b" class="sc good" style="top:%dpx;opacity:0"><div class="tg to">%s</div><div class="tx">%s</div></div>""" % (top[0], tagA, txA, top[1], tagB, txB)
    css = """.sc{position:absolute;left:90px;width:900px;height:%dpx;border-radius:%dpx;padding:34px 80px;box-sizing:border-box;z-index:5}
    .tg{display:inline-block;padding:8px 16px;border-radius:12px;background:rgba(255,255,255,.08);font-family:"HelvB";font-size:22px;letter-spacing:.14em;color:var(--grey)} .to{background:rgba(@@ACCENT_RGB@@,.18);color:#FFC58F}
    .tx{font-family:"HelvB";font-size:50px;letter-spacing:-.04em;margin-top:30px;white-space:nowrap} .tx b{display:inline-block;color:#5FD08A;text-shadow:0 0 30px rgba(47,166,90,.6)} .sc:not(.good) .tx b{color:#FF8A80;text-shadow:none}
    #root .sc.good{border-color:#2FA65A;box-shadow:inset 0 2px 1px rgba(220,255,230,.5), 0 0 46px rgba(47,166,90,.45), 0 22px 54px rgba(0,0,0,.45)} .sc.good .to{background:rgba(47,166,90,.2);color:#9BE8B8} .sc:not(.good) .tg{background:rgba(179,38,30,.22);color:#FFB0A8}
    .ln{position:absolute;left:538px;top:%dpx;width:4px;height:%dpx;background:#2FA65A;transform-origin:50%% 0;transform:scaleY(0);z-index:4}""" % (H, H // 2, top[0] + H + 4, top[1] - top[0] - H - 8)
    js = """tl.fromTo(q("a"), {opacity:0, y:-40}, {opacity:1, y:0, duration:0.4, ease:"power3.out"}, T(%s));
    __ft(q("ln"), {scaleY:0}, {scaleY:1, duration:0.25, ease:"power2.out"}, T(%s - 0.5));
    tl.fromTo(q("b"), {opacity:0, y:50}, {opacity:1, y:0, duration:0.42, ease:"power2.out"}, T(%s));
    tl.to(q("a"), {opacity:0.4, duration:0.3}, T(%s));
    tl.to(q("b"), {scale:1.05, boxShadow:"0 0 100px rgba(47,166,90,.7), inset 0 0 30px rgba(47,166,90,.16)", duration:0.4, ease:"power2.out"}, T(%s)); sweep(tl, "b", %s);""" % (tA, tB, tB, tHot, tHot, tHot)
    ac(tHot, "shine2", -22)
    return scene(sid, a, b, full, body, css, js)

# ------------------------------------------------------------------ Instagram notification banners (iOS dark). Newest lands on top, pushes the pile down.
def banner(i, top, title, body, me=False):
    av = '<div class="nav" style="background-image:url(assets/proof/avatar.jpg)">' if me else '<div class="nav">' + ANON
    return ('<div id="{ID}-n%s" class="nb" style="top:%dpx">%s<span class="nig">%s</span></div><div class="nt"><div class="n1"><span>%s</span><span class="ntm">now</span></div><div class="n2">%s</div></div></div>'
            % (i, top, av, igicon("{ID}" + str(i)), title, body))
NBCSS = """.nb{translate:0 var(--dy,0px);position:absolute;left:70px;width:940px;height:196px;border-radius:54px;background:rgba(40,40,43,.86);-webkit-backdrop-filter:blur(30px) saturate(160%);backdrop-filter:blur(30px) saturate(160%);border:1px solid rgba(255,255,255,.14);box-shadow:0 24px 60px rgba(0,0,0,.55);display:flex;align-items:center;gap:30px;padding:0 36px;box-sizing:border-box;font-family:-apple-system,"SF Pro Text","HelvR",Helvetica,sans-serif;color:#fff;z-index:5;opacity:0}
    .nav{width:112px;height:112px;border-radius:56px;background-size:cover;background-position:center;position:relative;flex:none} .nav > svg:first-child{border-radius:56px;display:block}
    .nig{position:absolute;right:-10px;bottom:-10px;width:50px;height:50px;border-radius:13px;box-shadow:0 0 0 4px rgba(40,40,43,1)} .nig svg{display:block}
    .nt{flex:1;min-width:0} .n1{display:flex;justify-content:space-between;align-items:baseline;font-size:38px;font-weight:600;letter-spacing:-.01em} .ntm{font-size:30px;font-weight:400;color:rgba(235,235,245,.6)}
    .n2{font-size:38px;font-weight:400;color:rgba(255,255,255,.94);margin-top:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"""
NJS = """function drop(id, g){ const el = document.querySelector(q("n"+id)), d = {t:0};
      tl.set(el, {opacity:1}, T(g)); __ft(d, {t:0}, {t:0.9, duration:0.9, ease:"none", onUpdate:function(){ el.style.setProperty("--dy", (-300*Math.exp(-6.5*d.t)*Math.cos(5.1*d.t)).toFixed(2)+"px"); }}, T(g)); }
    function push(ids, g, n){ ids.forEach(function(id){ __tt(q("n"+id), {y: 226*n, duration:0.45, ease:"power3.out"}, T(g)); }); }
"""
def notifs(sid, a, b, full, items):
    """items: [(title, body, me?, t)] oldest first. t=None on the first = already there on the switch frame."""
    top = (450 if len(items) > 2 else 560) if full else 16
    body = "".join(banner(chr(97 + i), top, ti, bo, me) for i, (ti, bo, me, t) in enumerate(items)); js = NJS
    for i, (ti, bo, me, t) in enumerate(items):
        c = chr(97 + i)
        if t is None: js += 'tl.set(q("n%s"), {opacity:1}, 0);' % c
        else:
            js += 'drop("%s", %s);' % (c, t); ac(t, "accept" if me else "pop", -21)
            for k in range(i): js += 'push(["%s"], %s, %d);' % (chr(97 + k), t, i - k)
    return scene(sid, a, b, full, body, NBCSS, js)

# ------------------------------------------------------------------ Google Docs window (split). Scrolls to and highlights the two headings named.
def gdoc(sid, a, b, title, h1, h2, ts, full=False, r3d=False):
    body = """<div id="{ID}-win" class="gd">
      <div class="gtop"><span class="gic">%s</span><div class="gtt"><div class="gname">%s <span class="gstar">&#9734;</span></div>
        <div class="gmenu"><span>File</span><span>Edit</span><span>View</span><span>Insert</span><span>Format</span><span>Tools</span><span>Extensions</span><span>Help</span></div></div>
        <div class="gshare"><svg viewBox="0 0 24 24" width="24" height="24"><path d="M7,10 V7 a5,5 0 0 1 10,0 V10" fill="none" stroke="#001D35" stroke-width="2.4"/><rect x="5" y="10" width="14" height="10" rx="2.5" fill="#001D35"/></svg>Share</div><div class="gav"></div></div>
      <div class="gbar"><span>100%%</span><i></i><span>Normal text</span><i></i><span>Arial</span><i></i><span>11</span><i></i><b>B</b><em>I</em><u>U</u><span style="color:#1A73E8">A</span></div>
      <div class="gcanvas"><div id="{ID}-page" class="gpage"><h1>%s</h1><p class="gln" style="width:96%%"></p><p class="gln" style="width:88%%"></p><p class="gln" style="width:92%%"></p><p class="gln" style="width:60%%"></p><h2><span id="{ID}-ex">%s</span></h2><p class="gln" style="width:94%%"></p><p class="gln" style="width:86%%"></p><p class="gln" style="width:90%%"></p><p class="gln" style="width:72%%"></p><h2><span id="{ID}-tp">%s</span></h2><p class="gln" style="width:92%%"></p><p class="gln" style="width:84%%"></p><p class="gln" style="width:95%%"></p><p class="gln" style="width:66%%"></p><p class="gln" style="width:88%%"></p></div></div>
    </div>""" % (DOCI, title, title, h1, h2)
    css = """.gd{position:absolute;left:60px;top:%dpx;width:960px;height:%dpx;border-radius:24px;background:#F9FBFD;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.6);z-index:5;font-family:"HelvR",Arial,Helvetica,sans-serif;color:#1F1F1F}
    .gtop{height:88px;display:flex;align-items:center;gap:16px;padding:0 22px} .gic{flex:none;display:flex} .gtt{flex:1}
    .gname{font-size:27px;color:#1F1F1F} .gstar{color:#5F6368;font-size:24px;margin-left:8px} .gmenu{display:flex;gap:17px;font-size:18px;color:#444746;margin-top:5px}
    .gshare{display:flex;align-items:center;gap:10px;height:54px;padding:0 28px;border-radius:27px;background:#C2E7FF;color:#001D35;font-family:"HelvB";font-size:21px}
    .gav{width:50px;height:50px;border-radius:25px;background:url(assets/proof/avatar.jpg) center/cover}
    .gbar{margin:0 18px;height:50px;border-radius:25px;background:#EDF2FA;display:flex;align-items:center;gap:20px;padding:0 26px;font-size:18px;color:#444746} .gbar i{width:1.5px;height:22px;background:#C7C7C7} .gbar b{font-family:"HelvB"} .gbar u{text-underline-offset:3px}
    .gcanvas{position:absolute;left:0;right:0;top:150px;bottom:0;overflow:hidden}
    .gpage{position:absolute;left:150px;top:14px;width:660px;height:900px;background:#fff;box-shadow:0 1px 3px rgba(60,64,67,.3),0 4px 8px rgba(60,64,67,.15);padding:44px 58px;box-sizing:border-box}
    .gpage h1{font-family:"HelvR";font-weight:400;font-size:40px;margin:0 0 20px;color:#1F1F1F} .gpage h2{font-family:"HelvR";font-weight:400;font-size:28px;margin:26px 0 14px;color:#1F1F1F} .gpage h2 span{padding:2px 4px;margin-left:-4px;border-radius:3px}
    .gln{height:11px;border-radius:6px;background:#DADCE0;margin:0 0 15px}""" % ((390, 700) if full else (8, 548))
    js = """tl.to(q("page"), {y:-150, duration:1.2, ease:"power2.inOut"}, T(%s)); tl.to(q("ex"), {backgroundColor:"#D3E3FD", duration:0.3, ease:"power2.inOut"}, T(%s));
    tl.to(q("page"), {y:-300, duration:0.9, ease:"power2.inOut"}, T(%s)); tl.to(q("tp"), {backgroundColor:"#D3E3FD", duration:0.3, ease:"power2.inOut"}, T(%s));""" % tuple(ts)
    if r3d: js += R3D % ("win", "win", _vis(a, full))
    return scene(sid, a, b, full, body, css, js)

# ------------------------------------------------------------------ Claude-style chat window: a skill at work. user bubble, then reply lines appear one at a time.
SPARK = '<svg viewBox="0 0 40 40" width="%d" height="%d"><g stroke="#D97757" stroke-width="4.6" stroke-linecap="round">' + "".join('<line x1="20" y1="20" x2="%.1f" y2="%.1f"/>' % (20 + 15 * __import__("math").cos(k * 0.5236), 20 + 15 * __import__("math").sin(k * 0.5236)) for k in range(12)) + '</g></svg>'
def chat(sid, a, b, full, skill, user, lines, t_user, t_lines, r3d=False):
    """lines: reply rows (html). t_lines: one time per row."""
    H = 548 if not full else 760
    body = """<div id="{ID}-cw" class="cw"><div class="ctop"><span class="cdot"></span><span class="cdot"></span><span class="cdot"></span><div class="ctt">%s</div><div class="csk">%s Skill</div></div>
      <div id="{ID}-u" class="cu">%s</div>
      <div class="cr"><span class="csp">%s</span><div class="crl">%s</div></div>
      <div class="cin"><span>Reply to Claude&hellip;</span><b>&uarr;</b></div></div>""" % (skill, SPARK % (20, 20), user, SPARK % (44, 44), "".join('<div id="{ID}-l%d" class="cl">%s</div>' % (i, l) for i, l in enumerate(lines)))
    css = """.cw{position:absolute;left:60px;top:%dpx;width:960px;height:%dpx;border-radius:26px;background:#FAF9F5;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.6);z-index:5;font-family:-apple-system,"SF Pro Text","HelvR",Helvetica,sans-serif;color:#1F1E1D}
    .ctop{height:70px;display:flex;align-items:center;gap:10px;padding:0 26px;border-bottom:1.5px solid #E8E6DC} .cdot{width:15px;height:15px;border-radius:8px;background:#DAD8CE}
    .ctt{flex:1;text-align:center;font-size:25px;font-weight:600;color:#3D3D3A} .csk{display:flex;align-items:center;gap:8px;padding:7px 16px;border-radius:18px;background:#F0EEE6;border:1.5px solid #E0DDD0;font-size:20px;font-weight:600;color:#6B6A65}
    .cu{position:absolute;right:40px;top:96px;max-width:640px;padding:18px 26px;border-radius:24px;background:#F0EEE6;font-size:%dpx;line-height:1.25;opacity:0}
    .cr{position:absolute;left:40px;right:40px;top:%dpx;display:flex;gap:20px} .csp{flex:none;margin-top:2px} .crl{flex:1}
    .cl{font-size:%dpx;line-height:1.25;margin-bottom:%dpx;opacity:0;white-space:nowrap} .cl b{font-weight:700} .cl em{font-style:normal;color:#C6613F;font-weight:700} .cl s{color:#9A988F}
    .cin{position:absolute;left:40px;right:40px;bottom:24px;height:66px;border-radius:22px;background:#fff;border:1.5px solid #DEDCD1;box-shadow:0 4px 14px rgba(0,0,0,.06);display:flex;align-items:center;justify-content:space-between;padding:0 14px 0 26px;font-size:24px;color:#9A988F}
    .cin b{width:42px;height:42px;border-radius:12px;background:#D97757;color:#fff;display:flex;align-items:center;justify-content:center;font-size:26px}""" % (390 if full else 8, H, 30 if not full else 34, 196 if not full else 220, 30 if not full else 36, 14 if not full else 22)
    js = '__ft(q("u"), {opacity:0, y:16}, {opacity:1, y:0, duration:0.35, ease:"power3.out"}, T(%s));' % t_user + "".join('__ft(q("l%d"), {opacity:0, y:12}, {opacity:1, y:0, duration:0.35, ease:"power3.out"}, T(%s));' % (i, t) for i, t in enumerate(t_lines))
    ac(t_user, "pop", -22)
    if r3d: js += R3D % ("cw", "cw", _vis(a, full))
    return scene(sid, a, b, full, body, css, js)

# ------------------------------------------------------------------ drawn line graph with a dot riding the front
def graph(sid, a, b, full, pts, t, dur, label="", ghost=None, marks=(), tags=(), col="@@ACCENT@@"):
    """pts/ghost in a 900 x 380 box. marks=[(x, y, t)] dots popping on the line. tags=[(text, right?, top, hot, t)]"""
    P = " ".join("%d,%d" % p for p in pts)
    body = """<div class="chart"><div class="de-label" style="position:absolute;right:0;top:400px;font-size:24px">%s</div>
      <svg width="900" height="380" viewBox="0 0 900 380" style="overflow:visible"><line x1="0" y1="380" x2="900" y2="380" stroke="rgba(255,255,255,.3)" stroke-width="3"/><line x1="0" y1="0" x2="0" y2="380" stroke="rgba(255,255,255,.3)" stroke-width="3"/>%s
        <polyline id="{ID}-ret" points="%s" fill="none" stroke="GCOL" stroke-width="10" stroke-linejoin="round" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/>%s
        <circle id="{ID}-fr" cx="%d" cy="%d" r="13" fill="@@PAPER@@"/></svg>%s</div>""" % (label,
        ('<polyline points="%s" fill="none" stroke="rgba(255,255,255,.34)" stroke-width="6" stroke-dasharray="12 14"/>' % " ".join("%d,%d" % p for p in ghost)) if ghost else "", P,
        "".join('<circle id="{ID}-d%d" cx="%d" cy="%d" r="12" fill="GCOL"/>' % (i, x, y) for i, (x, y, tt) in enumerate(marks)), pts[0][0], pts[0][1],
        "".join('<div id="{ID}-t%d" class="tag" style="%s:0;top:%dpx;%s">%s</div>' % (i, "right" if r else "left", tp, "color:#fff;border-color:GCOL" if hot else "", tx) for i, (tx, r, tp, hot, tt) in enumerate(tags)))
    css = """.chart{position:absolute;left:90px;top:%dpx;width:900px;height:380px;z-index:4}
    .tag{position:absolute;padding:8px 18px;border-radius:18px;border:1.5px solid rgba(255,255,255,.3);background:rgba(12,11,10,.8);font-family:"HelvB";font-size:26px;letter-spacing:.08em;color:var(--grey);opacity:0}""" % (500 if full else 60)
    js = """const PTS = %s, fr = document.getElementById(ID+"-fr"), PH = {x:PTS[0][0]};
    function yAt(x){ for (let k=1;k<PTS.length;k++){ if (x <= PTS[k][0]) { const a = PTS[k-1], b = PTS[k]; return a[1] + (b[1]-a[1])*(x-a[0])/(b[0]-a[0]); } } return PTS[PTS.length-1][1]; }
    __ft(q("ret"), {strokeDashoffset:1000}, {strokeDashoffset:0, duration:%s, ease:"power2.inOut"}, T(%s));
    __ft(PH, {x:PTS[0][0]}, {x:PTS[PTS.length-1][0], duration:%s, ease:"power2.inOut", onUpdate:function(){ fr.setAttribute("cx", PH.x.toFixed(1)); fr.setAttribute("cy", yAt(PH.x).toFixed(1)); }}, T(%s));""" % (json.dumps([list(p) for p in pts]), dur, t, dur, t)
    js += "".join('tl.set(q("d%d"), {scale:0, transformOrigin:"50%% 50%%"}, 0); __tt(q("d%d"), {scale:1, duration:0.35, ease:"back.out(1.2)"}, T(%s));' % (i, i, tt) for i, (x, y, tt) in enumerate(marks))
    js += "".join('__ft(q("t%d"), {opacity:0, y:8}, {opacity:1, y:0, duration:0.35, ease:"power2.out"}, T(%s));' % (i, tt) for i, (tx, r, tp, hot, tt) in enumerate(tags))
    return scene(sid, a, b, full, body.replace("GCOL", col), css, js)

# ================================================================== FACE-window overlays (behind the creator's head / below the caption word)
OVCSS = """
    .ov-reel{position:absolute;left:0;top:0;width:300px;height:532px;margin:-266px 0 0 -150px;border-radius:30px;overflow:hidden;border:5px solid rgba(255,255,255,.95);box-shadow:0 30px 70px rgba(0,0,0,.6);opacity:0;box-sizing:border-box} .ov-reel img{width:100%;height:100%;object-fit:cover;display:block}
    .hk1{position:absolute;left:0;width:1080px;top:204px;text-align:center;font-family:"HelvB",Helvetica,sans-serif;font-weight:700;font-size:84px;letter-spacing:-.045em;line-height:1;color:#fff;text-shadow:0 3px 16px rgba(0,0,0,.75),0 0 3px rgba(0,0,0,.6)}
    .hk2w{position:absolute;left:0;width:1080px;top:300px;text-align:center} #hk2{display:inline-block;background:#fff;color:#0A0A0A;padding:10px 28px 13px;font-family:"HelvB",Helvetica,sans-serif;font-weight:700;font-size:80px;letter-spacing:-.045em;line-height:1}
    .lp{position:absolute;left:270px;width:540px;height:88px;border-radius:44px;display:flex;align-items:center;justify-content:center;gap:12px;font-family:"HelvB",Helvetica,sans-serif;font-weight:700;font-size:40px;letter-spacing:-.04em;color:#fff;background:rgba(12,10,9,.9);border:3px solid rgba(255,255,255,.45);box-shadow:0 14px 34px rgba(0,0,0,.5);opacity:0;box-sizing:border-box;white-space:nowrap}
    .bp{font-size:48px;position:absolute;left:28px;width:480px;height:118px;border-radius:59px;display:flex;align-items:center;justify-content:flex-start;padding-left:30px;gap:14px;font-family:"HelvB",Helvetica,sans-serif;font-weight:700;letter-spacing:-.04em;color:#fff;background:rgba(12,10,9,.9);border:3px solid rgba(255,255,255,.45);box-shadow:0 14px 34px rgba(0,0,0,.5);opacity:0;box-sizing:border-box;white-space:nowrap}
    .bph{border:3px solid @@ACCENT@@;background:@@ACCENT@@;color:@@ON_ACCENT@@;box-shadow:0 0 46px rgba(@@ACCENT_RGB@@,.6),0 14px 34px rgba(0,0,0,.5)}
    .bpg{border:3px solid #2FA65A;background:#2FA65A;color:#06140B;box-shadow:0 0 46px rgba(47,166,90,.55),0 14px 34px rgba(0,0,0,.5)}
    .bpr{border:3px solid #B3261E;background:#B3261E;color:#fff;box-shadow:0 0 46px rgba(179,38,30,.6),0 14px 34px rgba(0,0,0,.5)}
    .bn{position:absolute;top:286px;width:190px;height:190px;border-radius:95px;display:flex;align-items:center;justify-content:center;font-family:"HelvB",Helvetica,sans-serif;font-weight:700;font-size:118px;letter-spacing:-.05em;color:#fff;background:rgba(12,10,9,.9);border:4px solid rgba(255,255,255,.5);box-shadow:0 18px 40px rgba(0,0,0,.5);opacity:0;box-sizing:border-box}
    .otile{position:absolute;width:250px;height:444px;border-radius:26px;overflow:hidden;border:5px solid rgba(255,255,255,.95);box-shadow:0 26px 60px rgba(0,0,0,.6);opacity:0;box-sizing:border-box} .otile img{width:100%;height:100%;object-fit:cover;display:block}
    .otile span{position:absolute;left:10px;bottom:10px;padding:5px 12px 6px;border-radius:14px;background:rgba(0,0,0,.72);font-family:"HelvB",Helvetica,sans-serif;font-size:27px;letter-spacing:-.02em;color:#fff;display:flex;align-items:center;gap:7px}
    .oshot{position:absolute;border-radius:26px;overflow:hidden;border:4px solid rgba(255,255,255,.95);box-shadow:0 26px 60px rgba(0,0,0,.6);opacity:0;box-sizing:border-box;background:#000} .oshot img{width:100%;height:100%;object-fit:cover;display:block}"""
def hook(l1, l2, out):
    OF.append('<div id="hk1" class="hk1">%s</div><div class="hk2w"><span id="hk2">%s</span></div>' % (l1, l2))
    OJ.append("tl.to(['#hk1', '#hk2'], {opacity:0, duration:0.3, ease:'power2.inOut'}, %s);" % out)
def bps(pre, out, items, top0=520):
    """Short pills BEHIND the creator's head, left stack. items: [(text, 'hot'|'red'|'' , t)] (max 3)."""
    for k, (tx, hot, t) in enumerate(items):
        OB.append('<div id="%s%d" class="bp%s" style="top:%dpx">%s</div>' % (pre, k, {"hot": " bph", "red": " bpr", "green": " bpg"}.get(hot, ""), top0 + round(k * 134.5), tx))
        OJ.append("opop('#%s%d', %s); oout('#%s%d', %s);" % (pre, k, t, pre, k, out))
def lps(pre, out, items):
    """Wide pills BELOW the caption word, centred. items: [(text, hot, t)] (max 3)."""
    for k, (tx, hot, t) in enumerate(items):
        OF.append('<div id="%s%d" class="lp%s" style="top:%dpx">%s</div>' % (pre, k, {"hot": " bph", "red": " bpr", "green": " bpg"}.get(hot, ""), 1200 + k * 100, tx))
        OJ.append("opop('#%s%d', %s); oout('#%s%d', %s);" % (pre, k, t, pre, k, out))
def word(i, text, t, out, top=300, size=128):
    OB.append('<div id="%s" class="ov-line ov-pi" style="top:%dpx;font-size:%dpx">%s</div>' % (i, top, size, text)); OJ.append("orise('#%s', %s, 30); oout('#%s', %s);" % (i, t, i, out))
def nums(pre, labels, t, out, hot=None, hot_t=None, step=0.1):
    n = len(labels); gap = (950 - n * 190) / max(1, n - 1) if n > 1 else 0; x0 = 65 if n > 1 else 445
    for i, lab in enumerate(labels):
        OB.append('<div id="%s%d" class="bn" style="left:%dpx">%s</div>' % (pre, i, x0 + i * (190 + gap), lab)); OJ.append("opop('#%s%d', %s); oout('#%s%d', %s);" % (pre, i, t + i * step, pre, i, out))
    if hot is not None:
        OJ.append("tl.to('#%s%d', {background:'@@ACCENT@@', color:'@@ON_ACCENT@@', borderColor:'@@ACCENT@@', scale:1.12, boxShadow:'0 0 60px rgba(@@ACCENT_RGB@@,.75)', duration:0.5, ease:'power2.inOut'}, %s);" % (pre, hot, hot_t))
        others = ",".join("'#%s%d'" % (pre, i) for i in range(n) if i != hot)
        if others: OJ.append("tl.to([%s], {opacity:0.4, duration:0.5, ease:'power2.inOut'}, %s);" % (others, hot_t))
def tiles(pre, items, out):
    """Reel covers BEHIND the creator's head (left and right of it). items: [(src, left, top, rot, label, t)]"""
    for i, (src, l, tp, rot, lab, t) in enumerate(items):
        OB.append('<div id="%s%d" class="otile" style="left:%dpx;top:%dpx;rotate:%sdeg"><img src="%s"/>%s</div>' % (pre, i, l, tp, rot, src, ('<span>&#9654; %s</span>' % lab) if lab else ""))
        OJ.append("opop('#%s%d', %s); oout('#%s%d', %s);" % (pre, i, t, pre, i, out))
def oshot(i, src, l, tp, w, h, rot, t, out, front=False):
    (OF if front else OB).append('<div id="%s" class="oshot" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx;rotate:%sdeg"><img src="%s"/></div>' % (i, l, tp, w, h, rot, src))
    OJ.append("opop('#%s', %s); oout('#%s', %s);" % (i, t, i, out))
def carousel(ids, dur=3.2, fade=2.9):
    """An opening option: 8 reel covers circle the creator (big in front, smaller behind the head). Needs assets/reels/rNN.jpg."""
    OB.append("".join('<div id="rb%d" class="ov-reel"><img src="%s"/></div>' % (i, R(n)) for i, n in enumerate(ids)))
    OF.append('<div id="rfw" style="position:absolute;inset:0">' + "".join('<div id="rf%d" class="ov-reel"><img src="%s"/></div>' % (i, R(n)) for i, n in enumerate(ids)) + '</div>')
    OJ.append("""(function () { const n = 8, P = { a: 0, k: 0, fade: 1, b: 1 }, f = [], b = [], bl = __blur('#rfw');
      for (let i = 0; i < n; i++) { f.push($o('#rf' + i)); b.push($o('#rb' + i)); }
      function place() { for (let i = 0; i < n; i++) { const th = (P.a + i * 360 / n + 200) * Math.PI / 180, s = Math.sin(th), c = Math.cos(th);
          const x = 540 + 455 * c, y = 965 + 325 * s, sc = (0.80 + 0.26 * s) * (0.35 + 0.65 * P.k);
          const tf = 'translate(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px) perspective(1300px) rotateY(' + (-c * 40).toFixed(1) + 'deg) scale(' + sc.toFixed(3) + ')';
          f[i].style.transform = tf; b[i].style.transform = tf; const o = Math.min(1, P.k * 1.6) * P.fade; f[i].style.opacity = s >= 0 ? o : 0; b[i].style.opacity = s < 0 ? o : 0; }
        bl.setAttribute('stdDeviation', (46 * P.b).toFixed(1) + ' 0'); }
      tl.fromTo(P, { a: -150 }, { a: 300, duration: %s, ease: 'power2.out', onUpdate: place }, 0);
      tl.to(P, { k: 1, duration: 0.4, ease: 'back.out(1.5)', onUpdate: place }, 0.0); tl.to(P, { b: 0, duration: 0.55, ease: 'power2.out', onUpdate: place }, 0.0);
      tl.to(P, { fade: 0, duration: 0.3, ease: 'power2.inOut', onUpdate: place }, %s); place(); })();""" % (dur, fade))
    ac(0.0, "swirl", -18)
    import math; last = -1
    for m in range(10):
        an = -110 + 45 * m; t = dur * (1 - math.sqrt(max(0, 1 - (an + 150) / 450)))
        if 0.12 < t < fade - 0.05 and t - last >= 0.13: ac(t, "dtext", -25); last = t
def obanner(i, title, body, t, out, top=1200, me=False):
    """An Instagram notification banner below the creator's caption word (face window)."""
    OF.append(banner("X", top, title, body, me).replace("{ID}-nX", i).replace("{ID}X", i))
    OJ.append("opop('#%s', %s); oout('#%s', %s);" % (i, t, i, out)); ac(t, "accept" if me else "pop", -21)
def ojs(js): OJ.append(js)
def flush(css=""):
    E.overlay(behind="".join(OB), front="".join(OF), css=OVCSS + NCSS + NBCSS + css, js="\n".join(OJ))
    json.dump({"glides": sorted(set(GL)), "accents": sorted(AC), "dur": E.DUR}, open(os.path.join(E.ROOT, "sfx.json"), "w"))

# ================================================================== captions: 2-4 words, split on natural breaks, exact words
WEAK = set("the a an to of and or your is that for in on at by with you've you're i've it's they will be but so if my the creator's their this from as we the creator".split())
def captions(words_path, out_path, merges=(), fix=None):
    """words.json ([[s,e,w],..] on the cut clock) -> captions.json [{text,start,end}]. merges: [("thirteen thousand", "13,000")] spoken -> shown as one token.
    fix: {heard: shown} for single words (ASR slips, names)."""
    import re
    W = [[float(w[0]), float(w[1]), str(w[2])] for w in json.load(open(words_path))]; fix = fix or {}
    norm = lambda x: re.sub(r"[^a-z0-9'-]", "", x.lower())
    for spoken, shown in merges:
        sp = spoken.lower().split(); i = 0
        while i <= len(W) - len(sp):
            if [norm(x[2]) for x in W[i:i + len(sp)]] == sp:
                tail = re.search(r"[.,?!]*$", W[i + len(sp) - 1][2]).group(0); W[i:i + len(sp)] = [[W[i][0], W[i + len(sp) - 1][1], shown + tail]]
            i += 1
    for x in W:
        k = re.sub(r"[.,?!\"]", "", x[2])
        if k in fix: x[2] = x[2].replace(k, fix[k])
    sents, cur = [], []
    for x in W:
        cur.append(x)
        if re.search(r"[.?!]\"?$", x[2]): sents.append(cur); cur = []
    if cur: sents.append(cur)
    k = 0
    while k < len(sents):          # a one-word sentence joins its neighbour
        if len(sents[k]) == 1 and len(sents) > 1:
            if k + 1 < len(sents): sents[k + 1] = sents[k] + sents[k + 1]
            else: sents[k - 1] = sents[k - 1] + sents[k]
            del sents[k]; continue
        k += 1
    caps = []
    for S_ in sents:
        n = len(S_); best = {0: (0, [])}
        for j in range(1, n + 1):
            for L in (2, 3, 4):
                i = j - L
                if i < 0 or i not in best: continue
                last = S_[j - 1][2]; c = {2: 1.0, 3: 0.0, 4: 0.6}[L]
                if j < n and norm(last) in WEAK: c += 2.5
                if j < n and last.endswith(","): c -= 1.2
                if j < n and S_[j][2][:1].isupper() and not last.endswith(","): c += 0.4
                tot = best[i][0] + c
                if j not in best or tot < best[j][0]: best[j] = (tot, best[i][1] + [(i, j)])
        parts = best[n][1] if n in best else [(0, n)]
        for i, j in parts: caps.append({"text": " ".join(re.sub(r"[.?!\"]|(?<!\d),|,(?!\d)", "", x[2]) for x in S_[i:j]), "start": round(S_[i][0], 3), "wend": round(S_[j - 1][1], 3)})
    for i, c in enumerate(caps): c["end"] = round(min(caps[i + 1]["start"] if i + 1 < len(caps) else c["wend"] + 0.5, c["wend"] + 0.5), 3)
    json.dump(caps, open(out_path, "w"), indent=0); return caps

# ================================================================== Notion page: a script being written (use when a hook / script line is QUOTED)
NDOC = '<svg viewBox="0 0 24 24" width="%d" height="%d"><path d="M5,2 H15 L20,7 V22 H5 Z" fill="#fff" stroke="#37352F" stroke-width="1.6" stroke-linejoin="round"/><path d="M8,11 H16 M8,14.5 H16 M8,18 H13" stroke="#37352F" stroke-width="1.5" stroke-linecap="round"/></svg>'
NCSS = """.np{position:absolute;border-radius:24px;background:#fff;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.6);font-family:-apple-system,"SF Pro Text","HelvR",Helvetica,sans-serif;color:#37352F;box-sizing:border-box}
    .nbar{height:58px;display:flex;align-items:center;gap:12px;padding:0 24px;font-size:21px;color:#787774;border-bottom:1.5px solid #EDECE9} .nbar b{font-weight:500;color:#37352F} .nbar u{margin-left:auto;text-decoration:none;font-size:20px}
    .nh{display:flex;align-items:center;gap:16px;padding:22px 44px 6px;font-size:46px;font-weight:700;letter-spacing:-.02em}
    .nr{padding:9px 44px} .nl{font-size:19px;font-weight:600;letter-spacing:.06em;color:#9B9A97;margin-bottom:5px} .nx{display:inline-block;font-size:35px;line-height:1.22;white-space:nowrap;position:relative;padding:2px 6px;margin-left:-6px;border-radius:5px}
    .nx i{position:absolute;left:0;right:0;top:54%;height:4px;background:#B3261E;transform:scaleX(0);transform-origin:0 50%}"""
def _nrows(pre, rows): return "".join('<div class="nr"><div class="nl">%s</div><span id="%s%d" class="nx">%s<i id="%sx%d"></i></span></div>' % (lab, pre, i, tx, pre, i) for i, (lab, tx, *_) in enumerate(rows))
def _njs(sel, rows, ft, tt, T):
    js = ""
    for i, (lab, tx, t, eff, te) in enumerate(rows):
        n = max(6, len(__import__("re").sub(r"&[a-z]+;", "x", tx))); d = round(min(1.3, n * 0.04), 2)
        js += '%s(%s, {clipPath:"inset(0 100%% 0 0)"}, {clipPath:"inset(0 0%% 0 0)", duration:%s, ease:"steps(%d)"}, %s);' % (ft, sel("", i), d, n, T(t)); ac(t, "dtext", -24)
        if eff == "strike": js += '%s(%s, {scaleX:0}, {scaleX:1, duration:0.3, ease:"power2.out"}, %s); %s(%s, {color:"#9B9A97", duration:0.3}, %s);' % (ft, sel("x", i), T(te), tt, sel("", i), T(te))
        if eff == "hl": js += '%s(%s, {backgroundColor:"#C9EBD3", duration:0.3}, %s);' % (tt, sel("", i), T(te))
    return js
def notion(sid, a, b, full, title, rows, crumb="Content", r3d=False):
    """rows: [(label, text, t_typed, effect 'strike'|'hl'|None, t_effect)] - each line is typed on at t."""
    top, H = (400, 190 + 118 * len(rows)) if full else (8, 548)
    body = '<div id="{ID}-np" class="np" style="left:60px;top:%dpx;width:960px;height:%dpx"><div class="nbar">%s<span>%s /</span><b>%s</b><u>Share &nbsp;&#9734; &nbsp;&middot;&middot;&middot;</u></div><div class="nh">%s%s</div>%s</div>' % (top, H, NDOC % (26, 26), crumb, title, NDOC % (50, 50), title, _nrows("{ID}-r", rows))
    js = _njs(lambda k, i: 'q("r%s%d")' % (k, i), rows, "__ft", "__tt", lambda t: "T(%s)" % t) + (R3D % ("np", "np", _vis(a, full)) if r3d else "")
    return scene(sid, a, b, full, body, NCSS, js)
def scriptcard(i, title, rows, out, t_in, top=1196):
    """The same Notion page as a card BELOW the creator's caption word in a face window. rows as in notion()."""
    OF.append('<div id="%s" class="np" style="left:110px;top:%dpx;width:860px;opacity:0;padding-bottom:16px"><div class="nbar">%s<b>%s</b></div>%s</div>' % (i, top, NDOC % (26, 26), title, _nrows(i + "r", rows)))
    OJ.append("opop('#%s', %s); oout('#%s', %s);" % (i, t_in, i, out) + _njs(lambda k, n: "'#%sr%s%d'" % (i, k, n), rows, "tl.fromTo", "tl.to", lambda t: str(t)))

# ================================================================== AGENDA: a squared box at the top of the screen while a mechanism is being walked through (the creator's ask, 4 Oct)
def agenda(rows, t_in, t_out, top=44):
    """rows: [(lead, label, t_active)] - the row lights when its part starts; earlier rows get ticked, later rows stay dim (name hidden until reached)."""
    n = len(rows); H = 24 + n * 60
    html = '<div id="agd" class="agd" style="top:%dpx;height:%dpx">' % (top, H) + "".join(
        '<div id="agr%d" class="agr"><b>%s</b><span class="agq">&middot; &middot; &middot;</span><span id="agl%d" class="agl">%s</span><i id="agc%d">&#10003;</i></div>' % (i, ld, i, lb, i) for i, (ld, lb, t) in enumerate(rows)) + '</div>'
    css = """.agd{position:absolute;left:330px;width:420px;border-radius:10px;background:rgba(10,9,8,.86);border:2px solid rgba(255,255,255,.26);box-shadow:0 18px 44px rgba(0,0,0,.5);padding:12px 0;box-sizing:border-box;opacity:0;font-family:"HelvB",Helvetica,sans-serif}
    .agr{position:relative;height:60px;display:flex;align-items:center;gap:16px;padding:0 24px;font-size:33px;letter-spacing:-.035em;color:rgba(255,255,255,.34)} .agr b{width:54px;font-weight:700} .agl{position:absolute;left:94px;opacity:0;white-space:nowrap}
    .agr i{position:absolute;right:22px;font-style:normal;font-size:28px;color:#2FA65A;opacity:0}"""
    js = "tl.fromTo('#agd', {opacity:0, y:-20, filter:'blur(10px)'}, {opacity:1, y:0, filter:'blur(0px)', duration:0.5, ease:'power3.out'}, %s); tl.to('#agd', {opacity:0, duration:0.3, ease:'power2.inOut'}, %s);" % (t_in, t_out)
    for i, (ld, lb, t) in enumerate(rows):
        js += "tl.to('#agr%d', {color:'#FFFFFF', backgroundColor:'rgba(@@ACCENT_RGB@@,.22)', duration:0.3}, %s); tl.to('#agr%d b', {color:'@@ACCENT@@', duration:0.3}, %s); tl.to('#agr%d .agq', {opacity:0, duration:0.15}, %s); tl.to('#agl%d', {opacity:1, duration:0.3}, %s);" % (i, t, i, t, i, t, i, t)
        if i + 1 < n:
            t2 = rows[i + 1][2]
            js += "tl.to('#agr%d', {color:'rgba(255,255,255,.6)', backgroundColor:'rgba(@@ACCENT_RGB@@,0)', duration:0.3}, %s); tl.to('#agr%d b', {color:'rgba(255,255,255,.6)', duration:0.3}, %s); tl.to('#agc%d', {opacity:1, duration:0.3}, %s);" % (i, t2, i, t2, i, t2)
    E.top(html, css, js)

# ================================================================== real footage: a muted clip of the person being talked about (cut it to length first)
_vn = [0]
def clip(src, t, dur, style):
    """A timed, muted <video> for a scene body. t = SCENE-LOCAL seconds it starts playing; style = css position/size. Wrap it in a rounded card yourself."""
    _vn[0] += 1
    return '<video id="rv%d" class="clip" src="%s" muted playsinline data-start="%s" data-duration="%s" data-track-index="%d" style="%s;object-fit:cover"></video>' % (_vn[0], src, round(max(0, t), 3), round(dur, 3), 40 + _vn[0], style)

# ================================================================== a person: UNCROPPED footage in a rounded card + a simple YouTube channel card (the creator's notes, 4 Oct)
VCSS = """.vc{position:absolute;border-radius:28px;overflow:hidden;border:3px solid rgba(255,255,255,.9);box-shadow:0 30px 70px rgba(0,0,0,.65);background:#000;z-index:5}
    .vt{position:absolute;left:12px;bottom:12px;padding:6px 14px 7px;border-radius:16px;background:rgba(0,0,0,.72);font-family:"HelvB";font-size:24px;letter-spacing:-.02em;color:#fff;z-index:2}"""
def pcard(src, t, dur, left, top, h, tag="", ratio=9 / 16):
    """A real clip shown WHOLE (never crop the person): a portrait card h px tall. t = scene-local start, dur = seconds it plays."""
    w = round(h * ratio); body = clip(src, t, dur, "position:absolute;left:0;top:0;width:100%;height:100%") if src.endswith(".mp4") else '<img src="%s" style="width:100%%;height:100%%;object-fit:cover;display:block"/>' % src
    return '<div class="vc" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx">%s%s</div>' % (left, top, w, h, body, ('<span class="vt">%s</span>' % tag) if tag else "")
YCSS = """.ych{position:absolute;border-radius:34px;background:#0F0F0F;border:2px solid rgba(255,255,255,.16);box-shadow:0 30px 70px rgba(0,0,0,.6);z-index:5;font-family:-apple-system,"SF Pro Text","HelvR",Helvetica,sans-serif;color:#F1F1F1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.5em;box-sizing:border-box;padding:1.1em}
    .yav{width:5em;height:5em;border-radius:50%;background:#3A3A3C center/cover;overflow:hidden;flex:none} .yav svg{width:100%;height:100%;display:block}
    .yn{font-size:1.75em;font-weight:700;display:flex;align-items:center;gap:.3em;white-space:nowrap} .yh{font-size:.95em;color:#AAA;margin-top:-.35em}
    .ys{font-size:1.25em;color:#AAA} .ys b{color:#F1F1F1;font-weight:700;font-variant-numeric:tabular-nums}
    .yb{width:100%;height:2.5em;border-radius:1.25em;background:#F1F1F1;color:#0F0F0F;display:flex;align-items:center;justify-content:center;font-size:1.15em;font-weight:600;margin-top:.2em} .yb.on{background:#272727;color:#F1F1F1}"""
YTICK = '<svg viewBox="0 0 24 24" width="1em" height="1em" style="font-size:.6em"><circle cx="12" cy="12" r="11" fill="#AAA"/><path d="M7,12.5 L10.5,16 L17,9" fill="none" stroke="#0F0F0F" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
def ytchannel(name, handle, subs, left, top, w, h, fs=30, avatar=None, subscribed=False, sub_color=None):
    """A simple YouTube channel card built by hand: picture, name, handle, subscriber count, button. NO banner. avatar=None -> the default grey profile picture
    (the name still identifies them). The count is #{ID}-num."""
    av = ('<div class="yav" style="background-image:url(%s)"></div>' % avatar) if avatar else '<div class="yav">' + ANON.replace('width="112" height="112"', '') + '</div>'
    return ('<div id="{ID}-ych" class="ych" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx;font-size:%dpx">%s<div class="yn">%s %s</div><div class="yh">%s</div><div class="ys"><b id="{ID}-num"%s>%s</b> subscribers</div><div class="yb%s">%s</div></div>'
            % (left, top, w, h, fs, av, name, YTICK, handle, (' style="color:%s"' % sub_color) if sub_color else "", subs, " on" if subscribed else "", "Subscribed" if subscribed else "Subscribe"))
