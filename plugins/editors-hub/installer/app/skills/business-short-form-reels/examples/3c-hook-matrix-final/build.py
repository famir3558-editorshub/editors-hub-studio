#!/usr/bin/env python3
"""3C Hook Matrix - a Business Short Form reel.   python3 build.py
Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.
Edit THIS file, not the generated html.
All times are GLOBAL seconds on the cut; switch times are exact frame times minus 2 ms (scripts/cut_times.py)."""
import os
import reel_engine as E
import kit as K

ROOT = os.path.dirname(os.path.abspath(__file__))
DUR = 63.872
# Style notes: emphasis font on key words, NO 3D, real footage of the people named (a client's testimonial clip from the proof folder),
# fewer text pills - each idea gets a graphic that shows it. Three modes, in whatever order fits. Agenda box stays.
FACE = [[0, 3.7517], [12.7190, 16.4311], [23.7300, 27.7340], [34.1988, 38.2028], [43.2495, 45.5018], [50.0897, 56.4711]]
FULL = [[9.1738, 12.7190], [20.8939, 23.7300], [31.4878, 34.1988], [45.5018, 50.0897], [61.1424, DUR]]
K.captions(ROOT + "/words.json", ROOT + "/captions.json", merges=[("thirteen thousand", "13,000"), ("five hundred thousand", "500,000"), ("three c", "3C")], fix={"Close": "Claude"})
E.init(ROOT, DUR, FACE, FULL, title="3C Hook Matrix", words="words.json",
       emph={"stuck", "three", "gain", "lose", "scrolling", "typical", "avatar", "recognize", "topic", "pique", "interest", "secret", "loops", "reward"}, keep={"Claude"}, fix={"Close": "Claude"}, hide=[])
GRN = "#2FA65A"; RL = "assets/proof/"; P_ = K.PERSON
FILL = "position:absolute;left:0;top:0;width:100%;height:100%"

# 01 A client result (split): the client (their testimonial video) next to their real profile, before then after
K.raw("s01-bb", 3.5, 9.1738, False, '<div class="vc" style="left:120px;top:14px;width:300px;height:533px">' + K.clip(RL + "client.mp4", 0.2, 5.6, FILL) + '<span class="vt">Client name &middot; handle</span></div>'
    '<div id="{ID}-p0" class="pf"><img src="assets/proof/bb-before.png"/></div><div id="{ID}-p1" class="pf" style="opacity:0"><img src="assets/proof/bb-after.png"/></div>',
    """.vc{position:absolute;border-radius:28px;overflow:hidden;border:3px solid rgba(255,255,255,.9);box-shadow:0 30px 70px rgba(0,0,0,.65);background:#000;z-index:5}
    .vt{position:absolute;left:12px;bottom:12px;padding:6px 14px 7px;border-radius:16px;background:rgba(0,0,0,.72);font-family:"HelvB";font-size:24px;letter-spacing:-.02em;color:#fff;z-index:2}
    .pf{position:absolute;left:500px;top:14px;width:426px;height:533px;border-radius:28px;overflow:hidden;border:3px solid rgba(255,255,255,.25);box-shadow:0 30px 70px rgba(0,0,0,.65);background:#111;z-index:5} .pf img{width:100%;height:100%;object-fit:cover;display:block}""",
    """__ft(q("p1"), {opacity:0, scale:1.06}, {opacity:1, scale:1, duration:0.5, ease:"power3.out"}, T(6.35));
    __tt(q("p1"), {borderColor:"#2FA65A", boxShadow:"0 0 70px rgba(47,166,90,.6)", duration:0.4}, T(6.7));""")
K.ac(6.35, "swish", -23); K.ac(6.7, "shine")

# 02 First C, change (FULL): a before/after slider sweeps across - the same person, changed
K.raw("s02-c1", 9.1738, 16.18, True, """<div class="ba"><div class="half bf"><span class="ic">""" + P_ + """</span><em>BEFORE</em></div>
      <div id="{ID}-af" class="half af"><span class="ic">""" + P_ + """</span><em>AFTER</em></div><i id="{ID}-hd" class="hd"><b></b></i></div>""",
    """.ba{position:absolute;left:140px;top:440px;width:800px;height:520px;border-radius:48px;overflow:hidden;border:3px solid rgba(255,255,255,.3);box-shadow:0 34px 70px rgba(0,0,0,.6);z-index:5}
    .half{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px} .half em{font-style:normal;font-family:"HelvB";font-size:38px;letter-spacing:-.03em}
    .bf{background:#1B1917;color:rgba(242,240,236,.35);padding-right:400px;box-sizing:border-box} .af{background:linear-gradient(180deg,#174A2A,#0E2A19);color:#7BE0A0;padding-left:400px;box-sizing:border-box} .ic{width:220px;height:220px;display:block}
    .hd{position:absolute;top:0;bottom:0;left:0;width:8px;margin-left:-4px;background:#fff;box-shadow:0 0 30px rgba(255,255,255,.7)} .hd b{position:absolute;left:-32px;top:226px;width:72px;height:72px;border-radius:36px;background:#fff;box-shadow:0 10px 30px rgba(0,0,0,.5)}""",
    """const S = {x:100}, af = document.getElementById(ID+"-af"), hd = document.getElementById(ID+"-hd");
    function put(){ af.style.clipPath = "inset(0 0 0 " + S.x.toFixed(2) + "%)"; hd.style.left = S.x.toFixed(2) + "%"; } put();
    __ft(S, {x:96}, {x:6, duration:1.5, ease:"power2.inOut", onUpdate:put}, T(9.45)); __tt(S, {x:50, duration:1.2, ease:"power2.inOut", onUpdate:put}, T(11.2));""")
K.ac(9.45, "slide", -22)

# 04 Will they even stop (split): the feed streams past; one reel stands still
fcol = lambda k, ids: '<div id="{ID}-c%d" class="fc" style="left:%dpx">' % (k, k * 275) + "".join('<div class="ft"><img src="%s"/></div>' % K.R(i) for i in ids) + '</div>'
K.raw("s04-feed", 16.18, 20.8939, False, """<svg width="0" height="0" style="position:absolute"><filter id="{ID}-vb" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="0 9"/></filter></svg>
    <div class="feed">""" + fcol(0, [1, 5, 9, 13, 3, 7]) + fcol(1, [2, 6, 10, 14, 4, 8]) + fcol(2, [11, 15, 12, 16, 1, 6]) + """</div><div id="{ID}-pick" class="pick de-tile"><img src="assets/reels/r07.jpg"/></div>""",
    """.feed{position:absolute;left:140px;top:6px;width:800px;height:540px;overflow:hidden;border-radius:34px;z-index:3}
    .fc{position:absolute;top:0;width:250px;filter:url(#{ID}-vb)} .ft{width:250px;height:444px;margin-bottom:20px;border-radius:20px;overflow:hidden} .ft img{width:100%;height:100%;object-fit:cover;display:block;filter:brightness(.7)}
    .pick{left:400px;top:28px;width:280px;height:498px;border-radius:24px;z-index:6;opacity:0;border:4px solid #2FA65A;box-shadow:0 0 60px rgba(47,166,90,.6)}""",
    """__ft(q("c0"), {y:60}, {y:-1900, duration:4.6, ease:"none"}, T(16.3)); __ft(q("c1"), {y:-1900}, {y:60, duration:4.6, ease:"none"}, T(16.3)); __ft(q("c2"), {y:-140}, {y:-2100, duration:4.6, ease:"none"}, T(16.3));
    tl.fromTo(q("pick"), {opacity:0, scale:0.6}, {opacity:1, scale:1, duration:0.4}, T(18.85));""")
K.ac(18.85, "pop")

# 05 Second C, clarity (FULL): a blurred crowd; the lens finds exactly ONE person - who the video is for (circle one, never a group)
cw = "".join('<span class="cp" id="{ID}-p%d" style="left:%dpx;top:%dpx">%s</span>' % (i, 150 + (i % 5) * 160, 420 + (i // 5) * 180, P_) for i in range(15))
K.raw("s05-c2", 20.8939, 27.48, True, cw + '<i id="{ID}-ring" class="ring"></i>',
    """.cp{position:absolute;width:130px;height:130px;color:rgba(242,240,236,.4);filter:blur(7px);z-index:4}
    .ring{position:absolute;left:0;top:0;width:210px;height:210px;margin:-105px 0 0 -105px;border-radius:50%;border:8px solid @@ACCENT@@;box-shadow:0 0 50px rgba(@@ACCENT_RGB@@,.6), inset 0 0 40px rgba(@@ACCENT_RGB@@,.2);z-index:6;opacity:0}""",
    """__ft(q("ring"), {opacity:0, x:230, y:500, scale:1.5}, {opacity:1, x:860, y:560, scale:1.2, duration:0.7, ease:"power2.inOut"}, T(20.9));
    __tt(q("ring"), {x:535, y:665, scale:1, duration:0.6, ease:"power3.inOut"}, T(21.7));
    __tt(q("p7"), {filter:"blur(0px)", color:"@@ACCENT@@", scale:1.2, duration:0.4, ease:"power2.out"}, T(22.25));
    [0,1,2,3,4,5,6,8,9,10,11,12,13,14].forEach(function(i){ __tt(q("p"+i), {opacity:0.35, duration:0.4}, T(22.25)); });""")
K.ac(21.7, "swish", -23); K.ac(22.25, "shine")

# 07 Bottom of funnel (split): solid funnel, never glass
K.stack("s07-funnel", 27.48, 31.4878, False, ["TOP OF FUNNEL", "MIDDLE", "BOTTOM"], [27.6, 28.2, 28.7], widths=[780, 580, 400], solid=True, light=[(2, 30.1)], dim=[([0, 1], 30.1)])
K.ac(30.1, "shine")

# 08 Name the subject (FULL): the two hooks typed into a Notion script page
K.notion("s08-vs", 31.4878, 37.95, True, "Reel script", [("HOOK V1 &middot; NAMES THE AVATAR", "&ldquo;Hey coaches, listen up&hellip;&rdquo;", 31.0, "strike", 32.0),
    ("HOOK V2 &middot; NAMES THE SUBJECT", "&ldquo;Your hook is missing one of these&rdquo;", 32.2, "hl", 33.4)])


# 10 Last C (split): videos live or die on it - a heartbeat that keeps going (green) against one that flatlines (red), then the question mark
K.raw("s10-c3", 37.95, 45.5018, False, """<svg class="ek" width="940" height="430" viewBox="0 0 940 430">
      <polyline id="{ID}-lv" points="0,120 150,120 185,120 205,40 235,200 260,120 420,120 455,120 475,40 505,200 530,120 690,120 725,120 745,40 775,200 800,120 940,120" fill="none" stroke="#2FA65A" stroke-width="10" stroke-linejoin="round" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/>
      <polyline id="{ID}-dd" points="0,320 150,320 185,320 205,250 235,390 260,320 420,320 940,320" fill="none" stroke="#B3261E" stroke-width="10" stroke-linejoin="round" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/></svg>
    <div id="{ID}-q" class="qm">?</div>""",
    """.ek{position:absolute;left:70px;top:60px;z-index:5;overflow:visible;filter:drop-shadow(0 0 16px rgba(47,166,90,.35))}
    .qm{position:absolute;left:465px;top:175px;width:150px;height:150px;border-radius:75px;background:@@ACCENT@@;color:@@ON_ACCENT@@;display:flex;align-items:center;justify-content:center;font-family:"HelvB";font-size:104px;box-shadow:0 0 80px rgba(@@ACCENT_RGB@@,.7);opacity:0;z-index:7}""",
    """__ft(q("lv"), {strokeDashoffset:1000}, {strokeDashoffset:0, duration:3.0, ease:"none"}, T(38.3)); __ft(q("dd"), {strokeDashoffset:1000}, {strokeDashoffset:0, duration:2.2, ease:"none"}, T(39.3));
    __ft(q("q"), {opacity:0, scale:0.5}, {opacity:1, scale:1, duration:0.45, ease:"back.out(1.6)"}, T(42.3)); __tt("#"+ID+"-in2 .ek", {opacity:0.35, duration:0.3}, T(42.3));""")
K.ac(38.3, "slide", -22); K.ac(42.3, "shine2", -22)

# 12 Open a loop, close it (FULL): the ring opens, then closes green
K.raw("s12-loop", 45.5018, 56.22, True, """
    <svg class="lp1" width="560" height="560" viewBox="0 0 560 560"><circle cx="280" cy="280" r="240" fill="none" stroke="rgba(255,255,255,.2)" stroke-width="14" stroke-dasharray="6 22" stroke-linecap="round"/>
      <circle id="{ID}-ring" cx="280" cy="280" r="240" fill="none" stroke="@@ACCENT@@" stroke-width="26" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000" transform="rotate(-90 280 280)"/></svg>
    <div id="{ID}-o" class="lw">OPEN</div><div id="{ID}-c" class="lw" style="color:#2FA65A">CLOSED</div><div class="de-label ll">LOOP</div>""",
    """.lp1{position:absolute;left:260px;top:440px;z-index:5;overflow:visible;filter:drop-shadow(0 0 30px rgba(@@ACCENT_RGB@@,.45))}
    .lw{position:absolute;left:0;width:1080px;top:676px;text-align:center;font-family:"HelvB";font-size:70px;letter-spacing:-.05em;opacity:0;z-index:6} .ll{position:absolute;left:0;width:1080px;top:768px;text-align:center;font-size:24px}""",
    """__ft(q("ring"), {strokeDashoffset:1000}, {strokeDashoffset:260, duration:1.0, ease:"power2.inOut"}, T(46.6));
    __ft(q("o"), {opacity:0, scale:0.9}, {opacity:1, scale:1, duration:0.35, ease:"power3.out"}, T(46.85));
    __tt(q("ring"), {strokeDashoffset:0, stroke:"#2FA65A", duration:0.55, ease:"power2.inOut"}, T(49.2)); __tt(q("o"), {opacity:0, duration:0.15}, T(49.55));
    __ft(q("c"), {opacity:0, scale:1.15}, {opacity:1, scale:1, duration:0.3, ease:"power3.out"}, T(49.62));""")
K.ac(46.6, "slide", -22); K.ac(49.6, "accept")

# 14 The skill (split): a Claude-style chat window, swung up in 3D
K.chat("s14-chat", 56.22, 61.1424, False, "3C Hook Rewriter", "Rewrite my hook: &ldquo;Here are my content tips&rdquo;", [
    "<b>Change</b> &nbsp;<s>no gain or loss for the viewer</s>", "<b>Clarity</b> &nbsp;<s>no subject named</s>", "<b>Curiosity</b> &nbsp;<s>no open loop</s>",
    "<em>&rarr; &ldquo;Stuck on 300 views? Your hook is missing this&rdquo;</em>"], 56.7, [58.2, 58.75, 59.3, 60.1])
K.ac(60.1, "shine")
K.notifs("s15-cta", 61.1424, DUR, True, [("Instagram", "<b>jess.creates</b> commented: HOOKS", False, None), ("Instagram", "<b>mark.builds</b> commented: HOOKS", False, 62.2), ("@@HANDLE@@".lstrip("@"), "Your 3C Hook skill is here", True, 63.05)])


# ---------------------------------------------------------------- the AGENDA: a squared box at the top while each C is being covered
K.agenda([("C1", "CHANGE", 10.0), ("C2", "CLARITY", 21.1), ("C3", "CURIOSITY", 42.5)], 9.3, 56.2)

# ---------------------------------------------------------------- on the creator: other people's reels behind the head; below the caption, a graphic where one says it better than a pill
K.hook("Stuck on a few", "hundred views?", 3.42)
P = "assets/proof/low%d.jpg"
K.tiles("lv", [(P % 1, 30, 450, -7, "312", 0.0), (P % 3, 800, 480, 6, "204", 0.22), (P % 4, 14, 930, 5, "187", 0.44), (P % 8, 815, 960, -5, "451", 0.66)], 3.42)
K.ac(0.0, "whip"); [K.ac(t, "pop", -24) for t in (0.22, 0.44, 0.66)]
K.lps("gl", 16.1, [("GAIN", "green", 13.75), ("LOSE", "red", 14.3)]); K.ac(13.75, "pop")
K.scriptcard("av", "Reel script", [("HOOK &middot; NAMES THE AVATAR", "&ldquo;Hey coaches, listen up&hellip;&rdquo;", 24.9, "strike", 26.9)], 27.4, 24.1)
K.lps("fm", 37.9, [("THIS IS FOR ME", "green", 36.9)]); K.ac(36.9, "pop")
# the secret: loops opening and closing along the whole video - a timeline with arcs, each one closing green as the playhead passes
arcs = "".join('<path id="lpa%d" d="M%d,120 C%d,%d %d,%d %d,120" fill="none" stroke="@@ACCENT@@" stroke-width="9" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/>' % (i, 30 + i * 175, 60 + i * 175, 10 + (i % 2) * 22, 150 + i * 175, 10 + (i % 2) * 22, 180 + i * 175) for i in range(4))
K.OF.append('<div id="lpg" style="position:absolute;left:170px;top:1200px;width:740px;height:170px;opacity:0"><svg width="740" height="170" viewBox="0 0 740 170" style="overflow:visible"><rect x="0" y="114" width="740" height="14" rx="7" fill="rgba(255,255,255,.3)"/><rect id="lpf" x="0" y="114" width="0" height="14" rx="7" fill="@@PAPER@@"/>' + arcs + '<circle id="lph" cx="0" cy="121" r="18" fill="#fff"/></svg></div>')
K.ojs("opop('#lpg', 50.4); oout('#lpg', 56.15); (function(){ const H = {x:0}, f = $o('#lpf'), h = $o('#lph'); tl.fromTo(H, {x:0}, {x:740, duration:5.2, ease:'none', onUpdate:function(){ f.setAttribute('width', H.x.toFixed(1)); h.setAttribute('cx', H.x.toFixed(1)); }}, 50.7);"
      " [0,1,2,3].forEach(function(i){ const t0 = 50.9 + i*1.22; tl.fromTo('#lpa'+i, {strokeDashoffset:1000}, {strokeDashoffset:0, duration:1.0, ease:'none'}, t0); tl.to('#lpa'+i, {stroke:'#2FA65A', duration:0.2}, t0 + 1.0); }); })();")
K.ac(50.9, "slide", -23); [K.ac(51.9 + i * 1.22, "pop", -24) for i in range(4)]
K.flush()
E.build()
