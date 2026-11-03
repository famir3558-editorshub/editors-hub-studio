#!/usr/bin/env python3
"""Listen Live Look - a Business Short Form reel.   python3 build.py
Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.
Edit THIS file, not the generated html.
All times are GLOBAL seconds on the cut; switch times are exact frame times minus 2 ms (scripts/cut_times.py)."""
import os
import reel_engine as E
import kit as K

ROOT = os.path.dirname(os.path.abspath(__file__))
DUR = 62.528
# Style notes: emphasis font on key words, no 3D, the real client (their testimonial video) when they are mentioned, fewer text pills.
# This reel's own graphic is the three SENSES: an ear, a heartbeat and an eye for Listen / Live / Look.
FACE = [[0, 3.4181], [11.8849, 15.9723], [27.3170, 30.7787], [40.5385, 42.9576], [46.3777, 50.4234]]
FULL = [[9.2990, 11.8849], [15.9723, 18.5999], [22.3537, 27.3170], [30.7787, 35.3250], [42.9576, 46.3777], [54.1771, 57.9309]]
K.captions(ROOT + "/words.json", ROOT + "/captions.json", fix={"closed": "Claude", "guild": "skill"})
E.init(ROOT, DUR, FACE, FULL, title="Listen Live Look", words="words.json",
       emph={"never", "ideas", "listen", "repeatedly", "stories", "wins", "failures", "outlier", "topics", "formats", "styles"}, keep=set(), hide=[])
GRN = "#2FA65A"; RL = "assets/proof/"; FILL = "position:absolute;left:0;top:0;width:100%;height:100%"
EAR = '<svg viewBox="0 0 64 64" width="100%" height="100%"><path d="M20,30 C18,14 30,6 40,8 C52,10 56,24 50,34 C46,41 40,42 40,50 C40,58 30,60 25,54" fill="none" stroke="currentColor" stroke-width="5.5" stroke-linecap="round"/><path d="M29,30 C28,22 34,18 39,20 C45,23 44,30 39,34" fill="none" stroke="currentColor" stroke-width="5.5" stroke-linecap="round"/></svg>'
BEAT = '<svg viewBox="0 0 64 64" width="100%" height="100%"><path d="M32,54 C8,38 6,22 14,14 C21,8 29,11 32,18 C35,11 43,8 50,14 C58,22 56,38 32,54 Z" fill="none" stroke="currentColor" stroke-width="5.5" stroke-linejoin="round"/><path d="M12,33 H24 L28,24 L34,42 L38,33 H52" fill="none" stroke="currentColor" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
EYE = '<svg viewBox="0 0 64 64" width="100%" height="100%"><path d="M4,32 C14,16 24,12 32,12 C40,12 50,16 60,32 C50,48 40,52 32,52 C24,52 14,48 4,32 Z" fill="none" stroke="currentColor" stroke-width="5.5" stroke-linejoin="round"/><circle cx="32" cy="32" r="10" fill="currentColor"/></svg>'
def senses(sid, a, b, full, js):
    sz, gap, top = (250, 70, 500) if full else (230, 60, 60); x0 = (1080 - 3 * sz - 2 * gap) // 2
    body = "".join('<div id="{ID}-s%d" class="sn" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx"><span>%s</span></div><div id="{ID}-l%d" class="sl" style="left:%dpx;top:%dpx;width:%dpx">%s</div>' % (
        i, x0 + i * (sz + gap), top, sz, sz, ic, i, x0 + i * (sz + gap) - 30, top + sz + 22, sz + 60, nm) for i, (ic, nm) in enumerate([(EAR, "LISTEN"), (BEAT, "LIVE"), (EYE, "LOOK")]))
    return K.raw(sid, a, b, full, body, """.sn{position:absolute;border-radius:64px;background:#1B1917;border:3px solid rgba(255,255,255,.3);box-shadow:0 26px 54px rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;box-sizing:border-box;color:@@PAPER@@;z-index:5;opacity:0}
    .sn span{display:block;width:58%;height:58%} .sl{position:absolute;text-align:center;font-family:"HelvB";font-size:38px;letter-spacing:-.04em;z-index:5;opacity:0}""",
    """function show(i, g){ tl.fromTo(q("s"+i), {opacity:0, y:30}, {opacity:1, y:0, duration:0.5}, T(g)); tl.fromTo(q("l"+i), {opacity:0}, {opacity:1, duration:0.5}, T(g + 0.1)); }
    function lit(i, g){ tl.to(q("s"+i), {borderColor:"@@ACCENT@@", color:"@@ACCENT@@", boxShadow:"0 0 70px rgba(@@ACCENT_RGB@@,.55)", scale:1.1, duration:0.4, ease:"power2.inOut"}, T(g)); tl.to(q("l"+i), {color:"@@ACCENT@@", duration:0.3}, T(g));
      [0,1,2].forEach(function(k){ if (k !== i) tl.to([q("s"+k), q("l"+k)], {opacity:0.35, duration:0.4}, T(g)); }); }
    """ + js)

# 01 A client, every week for two years (split): the real client shown whole, and 104 week boxes filling green
wk = "".join('<i id="{ID}-w%d" style="left:%dpx;top:%dpx"></i>' % (i, (i % 26) * 19, (i // 26) * 21) for i in range(104))
K.raw("s01-client", 3.17, 9.2990, False, K.pcard(RL + "client_full.mp4", 0.2, 6.0, 110, 12, 536, "Client name") + '<div class="wkn"><b id="{ID}-num">0</b><span>weeks in a row</span></div><div class="wkb">' + wk + '</div>',
    K.VCSS + """.wkb{position:absolute;left:478px;top:370px;width:494px;height:84px;z-index:5} .wkb i{position:absolute;width:15px;height:17px;border-radius:4px;background:rgba(255,255,255,.2)}
    .wkn{position:absolute;left:470px;top:150px;width:510px;text-align:center;font-family:"HelvB";letter-spacing:-.04em;z-index:5} .wkn b{display:block;font-size:128px;line-height:1;color:#2FA65A;font-variant-numeric:tabular-nums} .wkn span{display:block;font-size:34px;margin-top:8px}""",
    """const n = {v:0}, el = document.getElementById(ID+"-num"), W = []; for (let i=0;i<104;i++) W.push(document.getElementById(ID+"-w"+i));
    __ft(n, {v:0}, {v:104, duration:3.6, ease:"power1.inOut", onUpdate:function(){ const k = Math.round(n.v); el.textContent = k; for (let i=0;i<104;i++) W[i].style.background = i < k ? "#2FA65A" : "rgba(255,255,255,.2)"; }}, T(5.2));""")
K.ac(5.2, "data", -24); K.ac(8.8, "shine")

# 02 Listen, Live, Look (FULL): an ear, a heartbeat, an eye
senses("s02-frame", 9.2990, 15.9723, True, "show(0, 10.7); show(1, 11.15); show(2, 11.6);")
[K.ac(t, "pop", -22) for t in (10.7, 11.15, 11.6)]

# 03 Your comments (FULL 15.97-18.60): Instagram notifications
K.notifs("s03-comments", 15.9723, 18.5999 - 0.25, True, [("Instagram", "<b>sarah.coach</b> commented: how do you plan a week?", False, None),
    ("Instagram", "<b>dan.fit</b> commented: what do I post first?", False, 16.7), ("Instagram", "<b>maya.designs</b> commented: do a video on this", False, 17.5)])

# 04 Your competitor's comments (split 18.60-22.35): their reel, their comment section
row = lambda i, top, name, txt: '<div id="{ID}-r%d" class="cmr" style="top:%dpx"><span class="cav">%s</span><div><b>%s</b>%s</div><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#8e8e93" stroke-width="1.8"><path d="M12 20.5s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.6a4.3 4.3 0 0 1 7.5 2.7c0 5.6-7.5 10.2-7.5 10.2z"/></svg></div>' % (i, top, K.PERSON, name, txt)
K.raw("s04-comp", 18.5999 - 0.25, 22.3537, False, '<div id="{ID}-tile" class="de-tile ct"><img src="%s"/><span class="ctl">COMPETITOR</span></div>' % K.R(9)
    + row(0, 46, "jay.builds", "How do you price this?") + row(1, 196, "kim.creates", "Can you show your process?") + row(2, 346, "leo.media", "What tools do you use?"),
    """.ct{left:86px;top:20px;width:290px;height:516px;border-radius:26px;z-index:5} .ctl{position:absolute;left:12px;top:12px;padding:6px 14px;border-radius:14px;background:rgba(0,0,0,.72);font-family:"HelvB";font-size:22px;letter-spacing:.12em;color:#fff}
    .cmr{position:absolute;left:416px;width:600px;height:126px;border-radius:34px;background:rgba(38,38,40,.94);border:2px solid rgba(255,255,255,.12);box-shadow:0 20px 50px rgba(0,0,0,.5);display:flex;align-items:center;gap:20px;padding:0 26px;box-sizing:border-box;z-index:6;opacity:0;font-family:-apple-system,"SF Pro Text","HelvR",Helvetica,sans-serif;font-size:29px;color:#fff}
    .cmr > div{flex:1;line-height:1.25} .cmr b{display:block;font-weight:600;font-size:25px;color:rgba(235,235,245,.7)} .cav{flex:none;width:66px;height:66px;border-radius:33px;background:#3A3A3C;color:#8E8E93;overflow:hidden;display:block}""",
    """tl.fromTo(q("tile"), {opacity:0, y:30}, {opacity:1, y:0, duration:0.5}, T(18.4));
    [20.0, 20.7, 21.4].forEach(function(g,i){ tl.fromTo(q("r"+i), {opacity:0, y:26}, {opacity:1, y:0, duration:0.5}, T(g)); });
    tl.to(q("r1"), {borderColor:"@@ACCENT@@", boxShadow:"0 0 46px rgba(@@ACCENT_RGB@@,.5)", duration:0.3}, T(21.9));""")
[K.ac(t, "pop", -23) for t in (20.0, 20.7, 21.4)]


# 05 The second part: Live (FULL): the heartbeat lights
senses("s05-live", 22.3537, 30.7787, True, """[0,1,2].forEach(function(i){ tl.set([q("s"+i), q("l"+i)], {opacity:1}, 0); }); lit(1, 23.9);
    tl.to(q("l1"), {text:"LIVED EXPERIENCES"}, T(26.2));""".replace('tl.to(q("l1"), {text:"LIVED EXPERIENCES"}, T(26.2));', 'tl.call(function(){ document.getElementById(ID+"-l1").innerHTML = "LIVED<br>EXPERIENCES"; }, null, T(26.2));'))
K.ac(23.9, "shine"); K.ac(26.2, "pop")

# 07 More experiences, higher ceiling (FULL): the line climbs, in green
K.graph("s07-ceiling", 30.7787, 35.3250 - 0.25, True, [(0, 350), (150, 318), (300, 270), (450, 205), (600, 150), (750, 84), (900, 20)], 31.0, 3.4, label="YOUR PERSONAL BRAND",
        marks=[(300, 270, 32.5), (600, 150, 33.0), (900, 20, 34.3)], tags=[("BIGGER", False, 190, False, 32.45), ("BETTER", False, 96, False, 32.85), ("HIGHER CEILING", False, 0, True, 33.4)], col=GRN)
K.ac(31.0, "slide", -22); K.ac(34.3, "shine2", -22)

# 08 The third one: Look (split): the eye lights
senses("s08-look", 35.3250 - 0.25, 42.9576, False, """[0,1,2].forEach(function(i){ tl.set([q("s"+i), q("l"+i)], {opacity:1}, 0); }); lit(2, 38.1);""")
K.ac(38.1, "shine")

# 10 What worked for competitors (FULL 42.96-46.38): three of their reels, the outlier lights up
tl3 = "".join('<div id="{ID}-t%d" class="de-tile ot" style="left:%dpx"><img src="%s"/><span class="vw">&#9654; %s</span></div>' % (i, 96 + i * 306, K.R(n), v) for i, (n, v) in enumerate([(3, "8.1K"), (12, "1.2M"), (6, "9.4K")]))
K.raw("s10-outlier", 42.9576, 54.1771 - 0.25, True, tl3 + '<div id="{ID}-chip" class="och">OUTLIER</div>',
    """.ot{top:420px;width:276px;height:490px;border-radius:26px;z-index:5} .vw{position:absolute;left:10px;bottom:10px;padding:5px 12px 6px;border-radius:14px;background:rgba(0,0,0,.72);font-family:"HelvB";font-size:28px;color:#fff}
    .och{position:absolute;left:402px;top:950px;width:276px;height:84px;border-radius:42px;background:@@ACCENT@@;color:@@ON_ACCENT@@;display:flex;align-items:center;justify-content:center;font-family:"HelvB";font-size:30px;letter-spacing:-.02em;opacity:0;z-index:6;box-shadow:0 0 46px rgba(@@ACCENT_RGB@@,.6)}""",
    """[0,1,2].forEach(function(i){ tl.fromTo(q("t"+i), {opacity:0, y:40}, {opacity:1, y:0, duration:0.5}, T(42.7)); });
    tl.to(q("t1"), {scale:1.14, borderColor:"@@ACCENT@@", boxShadow:"0 0 70px rgba(@@ACCENT_RGB@@,.6)", duration:0.45, ease:"power2.inOut"}, T(44.3)); tl.to([q("t0"), q("t2")], {opacity:0.4, duration:0.45}, T(44.3));
    tl.fromTo(q("chip"), {opacity:0, y:-20}, {opacity:1, y:0, duration:0.5}, T(44.9));""")
K.ac(44.3, "shine")


# 12 Never run out (split): the idea bank fills
K.count("s12-bank", 50.4234 - 0.25, 54.1771, False, 0, 312, 51.6, "IDEAS IN THE BANK", dur=2.0, tone=GRN)

# 13 The skill (FULL 54.18-57.93): a Claude-style chat window running the interview
K.chat("s13-chat", 54.1771, 57.9309, True, "Idea Extractor", "Run my weekly idea interview", [
    "<b>Listen</b> &nbsp;What did clients ask this week?", "<b>Live</b> &nbsp;What happened to you this week?", "<b>Look</b> &nbsp;Which post did best last month?", "<em>&rarr; 12 new ideas extracted</em>"], 54.3, [55.6, 56.2, 56.8, 57.3])
K.ac(57.3, "shine")

# 14 CTA (split 57.93-end): Instagram notifications
K.notifs("s14-cta", 57.9309, DUR, False, [("Instagram", "<b>jess.creates</b> commented: IDEA", False, None), ("@@HANDLE@@".lstrip("@"), "Your Idea Extractor skill is here", True, 60.9)])


K.agenda([("1", "LISTEN", 12.5), ("2", "LIVE", 23.9), ("3", "LOOK", 38.2)], 11.95, 50.3)

# ---------------------------------------------------------------- on him
K.hook("Never run out of", "content ideas again", 3.08)
K.carousel([4, 9, 2, 13, 7, 11, 5, 16], dur=3.4, fade=3.1)
K.scriptcard("cc", "Client call notes", [("ASKED 6 TIMES THIS MONTH", "&ldquo;How do I plan a week of content?&rdquo;", 13.3, "hl", 15.1)], 15.65, 12.6)
K.lps("lv", 30.45, [("STORIES", "", 27.42), ("WINS", "green", 28.6), ("FAILURES", "red", 29.2)]); K.ac(28.6, "pop"); K.ac(29.2, "pop")
K.tiles("ot", [(K.R(12), 30, 450, -7, "1.2M", 40.6), (K.R(3), 800, 480, 6, "8.1K", 40.8)], 42.65); K.ac(40.6, "pop")
K.lps("tf", 50.1, [("TOPICS", "", 47.1), ("FORMATS", "", 47.55), ("STYLES", "", 48.1)]); K.ac(47.1, "pops")
K.flush()
E.build()
