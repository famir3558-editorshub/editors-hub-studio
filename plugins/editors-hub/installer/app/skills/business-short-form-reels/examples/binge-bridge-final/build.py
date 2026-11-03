#!/usr/bin/env python3
"""Binge Bridge - a Business Short Form reel.   python3 build.py
Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.
Edit THIS file, not the generated html.
All times are GLOBAL seconds on the cut; switch times are exact frame times minus 2 ms (scripts/cut_times.py)."""
import os
import reel_engine as E
import kit as K

ROOT = os.path.dirname(os.path.abspath(__file__))
DUR = 51.605
# Style notes: emphasis font on key words, no 3D, fewer text pills. This reel's own graphic is an actual BRIDGE between the three platforms:
# it gets drawn, cracks (red) when it is weak, and carries people across (green) when it is strong.
FACE = [[0, 3.1678], [14.6376, 18.1411], [26.9416, 30.3200], [35.8672, 42.7490]]
FULL = [[9.4241, 14.6376], [22.3537, 26.9416], [32.6556, 35.8672], [46.5445, DUR]]
K.captions(ROOT + "/words.json", ROOT + "/captions.json", merges=[("seven-day", "7-day")])
E.init(ROOT, DUR, FACE, FULL, title="Binge Bridge", words="words.json",
       emph={"clients", "mistake", "best", "reliable", "lead", "magnets", "quick", "easy", "second", "longer", "in-depth", "free", "training"}, keep={"Instagram", "YouTube"}, hide=[])
GRN = "#2FA65A"; RED = "#B3261E"; PR = "assets/proof/"
TX = [105, 465, 825]          # the three towers (icon tiles), 150 px wide, in a 1080 x 420 box
def bridge(sid, a, b, full, js, hide_icons=False, extra=""):
    ic = [K.ig(110, "{ID}b"), K.yt(118), K.mail(110)]; nm = ["INSTAGRAM", "YOUTUBE", "EMAIL"]; h = ""
    for i in range(3):
        h += '<div id="{ID}-t%d" class="tw" style="left:%dpx"><span id="{ID}-i%d" style="opacity:%d">%s</span><b id="{ID}-q%d" style="opacity:%d">?</b></div><div id="{ID}-n%d" class="tn" style="left:%dpx;opacity:%d">%s</div>' % (
            i, TX[i], i, 0 if hide_icons else 1, ic[i], i, 1 if hide_icons else 0, i, TX[i] - 45, 0 if hide_icons else 1, nm[i])
    svg = ""
    for k in range(2):
        x0, x1 = TX[k] + 150, TX[k + 1]; hang = "".join('<line x1="%d" y1="%d" x2="%d" y2="236" class="hg"/>' % (x0 + 35 + j * 35, 150 + int(52 * (1 - ((j - 2) / 3.0) ** 2)), x0 + 35 + j * 35) for j in range(5))
        svg += ('<g id="{ID}-g%d"><path d="M%d,150 Q%d,256 %d,150" class="cb"/>%s</g><path id="{ID}-d%d" d="M%d,240 L%d,240" class="dk" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/>'
                % (k, x0, (x0 + x1) // 2, x1, hang, k, x0, x1))
    body = '<div class="bw" style="top:%dpx"><svg width="1080" height="420" viewBox="0 0 1080 420" style="position:absolute;left:0;top:0;overflow:visible">%s<path d="M40,330 q25,-16 50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0" class="wv"/><circle id="{ID}-p0" r="15" cx="0" cy="240" class="pp"/><circle id="{ID}-p1" r="15" cx="0" cy="240" class="pp"/><circle id="{ID}-p2" r="15" cx="0" cy="240" class="pp"/></svg>%s%s</div>' % (470 if full else 60, svg, h, extra)
    css = """.bw{position:absolute;left:0;width:1080px;height:420px;z-index:5}
    .tw{position:absolute;top:120px;width:150px;height:150px;border-radius:38px;background:#1B1917;border:3px solid rgba(255,255,255,.3);box-shadow:0 24px 50px rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;box-sizing:border-box}
    .tw span{display:flex} .tw b{position:absolute;font-family:"HelvB";font-size:92px;color:rgba(255,255,255,.3)} .tn{position:absolute;top:286px;width:240px;text-align:center;font-family:"HelvB";font-size:22px;letter-spacing:.1em;color:var(--grey)}
    .cb{fill:none;stroke:rgba(242,240,236,.55);stroke-width:5} .hg{stroke:rgba(242,240,236,.4);stroke-width:4} .dk{fill:none;stroke:@@PAPER@@;stroke-width:14;stroke-linecap:round}
    .wv{fill:none;stroke:rgba(255,255,255,.12);stroke-width:5} .pp{fill:#fff;opacity:0}"""
    return K.raw(sid, a, b, full, body, css, """function cross(p, k, g, d, col){ const x0 = [%d,%d][k], x1 = [%d,%d][k], el = document.getElementById(ID+"-p"+p), o = {x:x0};
      tl.set(el, {opacity:1, attr:{fill:col || "#fff"}}, T(g)); __ft(o, {x:x0}, {x:x1, duration:d, ease:"power1.inOut", onUpdate:function(){ el.setAttribute("cx", o.x.toFixed(1)); }}, T(g)); tl.set(el, {opacity:0}, T(g) + d); }
    """ % (TX[0] + 150, TX[1] + 150, TX[1], TX[2]) + js)

# 01 Proof (split): real client wins
K.shots("s01-proof", 2.92, 9.4241, False, [(PR + "win-38k-month.jpg", 50, 12, 600, 252, -2, 3.3), (PR + "win-7500-coaching.jpg", 440, 150, 590, 274, 2, 5.0), (PR + "win-10k-plan.jpg", 110, 296, 520, 258, -1.5, 7.5)])
K.ac(5.0, "pop", -23); K.ac(7.5, "pop", -23)

# 02 The Binge Bridge (FULL): the bridge is drawn between three unknown towers, then the three ways in appear
bridge("s02-name", 9.4241, 18.1411 - 0.25, True, """draw(tl, "d0", 9.9, 0.7); draw(tl, "d1", 10.3, 0.7);
    tl.fromTo(q("sg"), {opacity:0, y:-24}, {opacity:1, y:0, duration:0.5}, T(10.2));
    [11.5, 11.9, 12.3].forEach(function(g, i){ __tt(q("q"+i), {opacity:0, duration:0.15}, T(g)); __ft(q("i"+i), {opacity:0, scale:0.6}, {opacity:1, scale:1, duration:0.35, ease:"back.out(1.6)"}, T(g)); __tt(q("n"+i), {opacity:1, duration:0.3}, T(g)); });""",
    hide_icons=True, extra='<div id="{ID}-sg" class="sg">BINGE BRIDGE</div><style>.sg{position:absolute;left:350px;top:-20px;width:380px;height:80px;border-radius:12px;background:@@ACCENT@@;color:@@ON_ACCENT@@;display:flex;align-items:center;justify-content:center;font-family:"HelvB";font-size:40px;letter-spacing:-.03em;box-shadow:0 0 50px rgba(@@ACCENT_RGB@@,.55);opacity:0}</style>')
K.ac(9.9, "slide", -22); K.ac(10.2, "shine2", -22); [K.ac(t, "pop", -22) for t in (11.5, 11.9, 12.3)]

# 04 Your bridge is weak (split): someone sets off across, the deck cracks red and they never arrive
bridge("s04-weak", 18.1411 - 0.25, 22.3537, False, """tl.set([q("d0"), q("d1")], {strokeDashoffset:0}, 0);
    cross(0, 0, 19.4, 1.6); __tt(q("p0"), {attr:{cy:330}, opacity:0, duration:0.5, ease:"power2.in"}, T(21.0));
    tl.set([q("d0"), q("d1")], {strokeDasharray:"150 90", stroke:"#B3261E"}, T(20.95)); __tt([q("g0"), q("g1")], {opacity:0.25, duration:0.3}, T(20.95));
    __tt([q("d0"), q("d1")], {opacity:0.35, duration:0.24, yoyo:true, repeat:3, ease:"sine.inOut"}, T(21.3));""")
K.ac(20.95, "access", -21)

# 05 Strengthen it (FULL): the deck goes solid green and people cross both spans
bridge("s05-strong", 22.3537, 30.3200 - 0.25, True, """tl.set([q("d0"), q("d1")], {stroke:"#2FA65A"}, 0); draw(tl, "d0", 23.0, 0.6); draw(tl, "d1", 23.5, 0.6);
    cross(0, 0, 24.2, 1.0, "#7BE0A0"); cross(1, 1, 25.0, 1.0, "#7BE0A0"); cross(2, 0, 25.6, 1.0, "#7BE0A0");
    [0,1,2].forEach(function(i){ __tt(q("t"+i), {borderColor:"#2FA65A", boxShadow:"0 0 50px rgba(47,166,90,.5)", duration:0.4}, T(26.0 + i*0.12)); });""")
K.ac(23.0, "slide", -22); K.ac(26.0, "shine")

# 07 In exchange for their email (split): the free resource and the email address swap places
K.raw("s07-swap", 30.3200 - 0.25, 32.6556, False, '<div id="{ID}-a" class="sw" style="left:230px"><svg viewBox="0 0 48 64" width="120" height="160">' + K.DOCI.split(">", 1)[1] + '</div><div id="{ID}-b" class="sw" style="left:630px">' + K.mail(150) + '</div>',
    """.sw{position:absolute;top:150px;width:220px;height:220px;border-radius:50px;background:#1B1917;border:3px solid rgba(255,255,255,.3);box-shadow:0 24px 50px rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;box-sizing:border-box;z-index:5}""",
    """__tt(q("a"), {x:400, duration:0.9, ease:"power2.inOut"}, T(30.75)); __tt(q("a"), {y:-70, duration:0.45, ease:"power2.out", yoyo:true, repeat:1}, T(30.75));
    __tt(q("b"), {x:-400, duration:0.9, ease:"power2.inOut"}, T(30.75)); __tt(q("b"), {y:70, duration:0.45, ease:"power2.out", yoyo:true, repeat:1}, T(30.75));
    __tt(q("b"), {borderColor:"#2FA65A", boxShadow:"0 0 60px rgba(47,166,90,.6)", duration:0.4}, T(31.7));""")
K.ac(30.75, "swish", -23); K.ac(31.7, "shine")

# 08 YouTube or Instagram -> email (FULL): people cross the bridge to the email tower
bridge("s08-toemail", 32.6556, 42.7490 - 0.25, True, """tl.set([q("d0"), q("d1")], {stroke:"#2FA65A", strokeDashoffset:0}, 0);
    cross(0, 1, 33.4, 0.9, "#7BE0A0"); cross(1, 0, 34.1, 0.7, "#7BE0A0"); cross(2, 1, 34.8, 0.7, "#7BE0A0");
    __tt(q("t2"), {borderColor:"#2FA65A", boxShadow:"0 0 70px rgba(47,166,90,.6)", scale:1.12, duration:0.4}, T(35.3));""")
K.ac(33.4, "slide", -22); K.ac(35.3, "shine")

# 10 Instagram / email -> the long YouTube video (split 42.75-46.54): a YouTube card with two sources feeding it
K.raw("s10-toyt", 42.7490 - 0.25, 46.5445, False, """
    <div id="{ID}-s0" class="mc src" style="top:96px">%s<span class="mw">INSTAGRAM</span></div><div id="{ID}-s1" class="mc src" style="top:300px">%s<span class="mw">EMAIL LIST</span></div>
    <svg class="ar" width="1080" height="560" viewBox="0 0 1080 560"><path id="{ID}-a0" d="M452,161 C520,161 510,250 566,256" fill="none" stroke="#2FA65A" stroke-width="10" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/>
      <path id="{ID}-a1" d="M452,365 C520,365 510,300 566,292" fill="none" stroke="#2FA65A" stroke-width="10" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/></svg>
    <div id="{ID}-yt" class="ytc"><div class="yth"><img src="assets/proof/aj-yt.jpg"/><span class="ytd">24:16</span><i></i></div>
      <div class="ytm"><span class="yta"></span><div><div class="ytt">The Binge Bridge: full breakdown</div><div class="yts">@@CREATOR_NAME@@ &middot; Free training</div></div></div></div>""" % (K.ig(58, "{ID}s"), K.mail(58)),
    """.mc{position:absolute;display:flex;align-items:center;justify-content:center;gap:18px;box-sizing:border-box;z-index:5;opacity:0} .src{left:56px;width:392px;height:130px;border-radius:65px} .mw{font-family:"HelvB";font-size:34px;letter-spacing:-.04em;white-space:nowrap}
    .ar{position:absolute;left:0;top:0;z-index:6}
    .ytc{position:absolute;left:574px;top:40px;width:456px;height:470px;border-radius:26px;background:#0F0F0F;border:2px solid rgba(255,255,255,.16);box-shadow:0 30px 70px rgba(0,0,0,.6);overflow:hidden;z-index:5;font-family:-apple-system,"SF Pro Text","HelvR",Helvetica,sans-serif;opacity:0}
    .yth{position:relative;margin:14px;height:241px;border-radius:16px;overflow:hidden} .yth img{width:100%;height:100%;object-fit:cover;display:block} .ytd{position:absolute;right:10px;bottom:14px;padding:3px 8px;border-radius:6px;background:rgba(0,0,0,.82);color:#fff;font-size:20px;font-weight:600}
    .yth i{position:absolute;left:0;bottom:0;height:6px;width:38%;background:#FF0000}
    .ytm{display:flex;gap:16px;padding:6px 18px} .yta{flex:none;width:56px;height:56px;border-radius:28px;background:url(assets/proof/avatar.jpg) center/cover}
    .ytt{font-size:29px;font-weight:600;line-height:1.2;color:#F1F1F1} .yts{font-size:22px;color:#AAA;margin-top:8px}""",
    """tl.fromTo(q("yt"), {opacity:0, y:30}, {opacity:1, y:0, duration:0.5}, T(42.6));
    tl.fromTo(q("s0"), {opacity:0, y:30}, {opacity:1, y:0, duration:0.5}, T(43.7)); draw(tl, "a0", 44.0, 0.45);
    tl.fromTo(q("s1"), {opacity:0, y:30}, {opacity:1, y:0, duration:0.5}, T(45.3)); draw(tl, "a1", 45.6, 0.45);
    tl.to(q("yt"), {borderColor:"#2FA65A", boxShadow:"0 0 60px rgba(47,166,90,.55)", duration:0.4}, T(46.0));""")
K.ac(44.0, "slide", -22); K.ac(45.6, "slide", -22)


# 11 The guide (FULL): the real Google Docs window, then the notifications
K.gdoc("s11-doc", 46.5445, 49.4, "7-Day Personal Brand Guide", "Day 1: Pick your positioning", "Day 7: Sign your first client", [47.4, 48.1, 48.5, 48.9], full=True)
K.notifs("s12-cta", 49.4, DUR, True, [("Instagram", "<b>jess.creates</b> commented: GUIDE", False, None), ("Instagram", "<b>mark.builds</b> commented: GUIDE", False, 50.0), ("@@HANDLE@@".lstrip("@"), "Your 7-day guide is here", True, 50.75)])

K.agenda([("1", "LEAD MAGNETS", 27.3), ("2", "LONG-FORM", 36.2)], 22.6, 46.3)

# ---------------------------------------------------------------- on him
K.hook("Content isn&rsquo;t", "getting you clients?", 2.85)
K.tiles("hv", [(K.R(4), 30, 450, -7, "48.2K", 0.0), (K.R(11), 800, 480, 6, "112K", 0.22)], 2.85)
K.lps("zc", 2.85, [("0 CLIENTS", "red", 0.95)]); K.ac(0.0, "whip"); K.ac(0.22, "pop", -24); K.ac(0.95, "access", -21)
# the three platforms as their app icons, below the caption (no text pills)
for i, (ic, t) in enumerate([(K.ig(120, "ovA"), 16.1), (K.yt(128), 16.75), (K.mail(120), 17.6)]):
    K.OF.append('<div id="pic%d" style="position:absolute;left:%dpx;top:1210px;width:170px;height:170px;border-radius:44px;background:#1B1917;border:3px solid rgba(255,255,255,.4);box-shadow:0 18px 40px rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;opacity:0;box-sizing:border-box">%s</div>' % (i, 245 + i * 210, ic))
    K.ojs("opop('#pic%d', %s); oout('#pic%d', 17.85);" % (i, t, i)); K.ac(t, "pop", -23)
K.lps("lm", 30.0, [("LEAD MAGNET", "hot", 27.5)]); K.ac(27.5, "shine")
ic = lambda s, t: s + '<span style="margin-left:6px">' + t + '</span>'
K.lps("ft", 42.45, [(ic(K.yt(64), "LONG-FORM"), "", 37.1), ("FREE TRAINING", "green", 41.9)]); K.ac(37.1, "pop"); K.ac(41.9, "shine")
K.flush()
E.build()
