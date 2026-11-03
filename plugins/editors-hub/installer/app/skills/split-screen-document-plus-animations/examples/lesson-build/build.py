#!/usr/bin/env python3
"""Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.

A split-screen lesson build: the base video already switches between the creator full screen and a document split, the
windows are in windows.json ("full" / "doc"), graphics go only inside the full-screen windows, and every graphic
ILLUSTRATES what is being described (an interface, an object, a real asset) instead of restating the words.

   python3 build.py            audit + page for chunk 0        python3 build.py --list     chunk table
   python3 build.py --chunk N  page for chunk N (the render script does this for you)
Times are seconds on the CUT timeline. Get them from the creator's words:  t = E.w("exact words", after_seconds).
Every string passed to E.w() below is a placeholder: use the exact words from cut_words.json for the video in hand."""
import yt_engine as E, yt_kit as K, doc_kit as D
E.init(__file__)
M = "assets/media/"                  # real assets (a channel's avatar, a plaque, a testimonial) are copied here by the asset hunt

# ───────── 1. the hook: a video card, then a notification lands on it ─────────
a, b = D.win(2.0)                                                   # the full-screen window this time sits in
t_topic = E.w("<words that name the platform>", 0); t_result = E.w("<words that name the result>", 0); t_end = E.w("<last word of the line>", 0, end=True)
body = ('<div id="hk-v" class="xy h" style="top:14px;padding:20px"><div class="yth" style="height:300px"><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center">'
        '<div style="width:112px;height:78px;border-radius:22px;background:#FF0033;display:flex;align-items:center;justify-content:center">' + D.PLAY.format(46, "#fff") + '</div></div><b>18:24</b></div>'
        '<div class="yl" style="width:78%;margin-top:22px"></div><div class="yl s" style="width:46%"></div></div>'
        + D.note("hk-n", 300, "linear-gradient(180deg,#34C759,#1E9E45)", D.CAL, "New call booked", "Found you on YouTube"))
E.enter("#hk-v", t_topic, "focus", lead=0.2); E.sfx(t_topic - 0.3, "woosh"); D.drop("#hk-n", t_result + 0.15, "accept")
E.float_(K.custom("hook", t_topic - 0.3, t_end + 0.15, body, (620, 470), name="video-to-call", text="New call booked"), why="curiosity", score=5, side="left")

# ───────── 2. a preview of N things: N hidden cards, never the contents (no early reveal) ─────────
t5 = E.w("<the words that announce the number>", 4); t5e = E.w("<last word of that sentence>", t5, end=True)
E.full(K.preview("count", t5 - 0.2, t5e + 0.25, 5, variant="cards", reveal=0, t_split=t5 + 0.35, t_reveal=t5 + 1.4), why="curiosity", score=5, fill=1.0)

# ───────── 3. a number climbs while the thing the creator wants stays at zero ─────────
a, b = D.win(30.0); t_views = E.w("<words about views or reach>", a); t_zero = E.w("<words about the missing result>", t_views)
E.float_(D.views_card("vw", a + 0.4, b - 0.3, t_views, t_zero, label2="Booked calls"), why="demonstrate", score=4, side="left")

# ───────── 4. a real person or channel: a real avatar, real figures, nothing invented ─────────
a, b = D.win(120.0); t_name = E.w("<the name they say>", a)
body = D.chan("ch", 14, "avatar-example.jpg", "<Channel name exactly as shown>", "@handle &middot; <real subscriber count>", "ch-av", tag="")
E.enter("#ch", t_name, "focus", lead=0.2); E.sfx(t_name - 0.3, "woosh")
E.float_(K.custom("channel", t_name - 0.3, b - 0.25, body, (660, 230), name="channel-card", text="channel"), why="example", score=4, side="left", tier=1)

# ───────── 5. a choice between videos: a search page with a cursor clicking the longest ─────────
a, b = D.win(210.0); t_long = E.w("<words about length>", a); t_click = E.w("<words about clicking>", a); t_after = E.w("<last word of the line>", a, end=True)
rows = "".join(D.vrow(f"sr-r{i}", 230, 129, d_, f'<div class="yl" style="width:{w1}%"></div><div class="yl s" style="width:{w2}%"></div>', cls="")
               for i, (d_, w1, w2) in enumerate((("0:42", 82, 50), ("26:08", 90, 64), ("7:15", 70, 44))))
body = (f'<div id="sr-c" class="xy h" style="top:14px;padding:16px">{rows}</div><div id="sr-cur" class="h" style="position:absolute;left:520px;top:470px">{D.CUR}</div>')
E.enter("#sr-c", a + 0.5, "focus"); E.sfx(a + 0.25, "woosh")
E.tw("#sr-c .yth b", t_long, 0.3, {"backgroundColor": "@@ACCENT@@", "scale": 1.18}, None, "back.out(2)"); E.sfx(t_long, "pop", -26)
E.setp("#sr-cur", t_click - 0.9, {"opacity": 1}); E.tw("#sr-cur", t_click - 0.9, 0.8, {"x": -330, "y": -190}, None, "power2.inOut")
E.tw("#sr-r1", t_click, 0.25, {"borderColor": "@@ACCENT@@", "backgroundColor": "rgba(@@ACCENT_RGB@@,.16)"}, None, "power2.out"); E.sfx(t_click, "accept", -25)
E.float_(K.custom("search", a + 0.35, t_after + 0.5, body, (660, 460), name="search-results", text="search"), why="demonstrate", score=4, side="left")

# ───────── 6. a sequence of steps as icon tiles that arrive on each spoken step ─────────
a, b = D.win(300.0); T = []; tt = a
for _ in range(3): tt = E.w("<the repeated word for each step>", tt + 0.05); T.append(tt)
body = ""
for i, x in enumerate([40, 330, 620]):
    body += f'<div id="bg-t{i}" class="tile h" style="left:{x}px;top:10px;width:220px;height:150px">{D.PLAY.format(70, "@@PAPER@@")}</div>'
    if i: body += f'<div id="bg-a{i}" class="xar h" style="left:{x - 62}px;top:50px">&rarr;</div>'
for i, t_ in enumerate(T):
    E.enter(f"#bg-t{i}", t_, "rise", lead=0.12); E.sfx(t_, "pop", -26)
    if i: E.enter(f"#bg-a{i}", t_, "fade", lead=0.12)
E.float_(K.custom("chain", T[0] - 0.3, T[-1] + 2.0, body, (1520, 180), name="step-chain", text=""), why="demonstrate", score=4, zone="bottom")

# ───────── 7. buyer notifications stacking in ─────────
a, b = D.win(380.0); t_a = E.w("<words about the purchase>", a); t_b = E.w("<words about the booking>", a); t_c = E.w("<words about the follow-up>", a)
body = (D.note("nf-0", 14, "linear-gradient(180deg,#7A5CFF,#4B32D6)", D.CARD, "Payment received", "$27 &middot; from your video")
        + D.note("nf-1", 160, "linear-gradient(180deg,#34C759,#1E9E45)", D.CAL, "New call booked", "Thursday, 2:00 pm")
        + D.note("nf-2", 306, "#FF0033", D.PLAY.format(52, "#fff"), "Watched 4 of your videos", "Same viewer, tonight"))
for i, t_ in enumerate((t_a, t_b, t_c)): D.drop(f"#nf-{i}", t_ + 0.1, "accept" if i == 1 else "pop")
E.float_(K.custom("notifs", t_a - 0.1, b - 0.2, body, (660, 450), name="notifications", text="Payment received New call booked"), why="demonstrate", score=4, side="right")

# ───────── 8. a split INSIDE a full-screen window: the graphic on the LEFT, the creator on the RIGHT, cut=True at the edges ─────────
a, b = D.win(450.0)
E.split(K.custom("links", a, b, '<div id="ln-c" class="xy" style="top:14px"><u>Description</u><p>link one</p><p>link two</p></div>', (820, 520), name="links", text="links"),
        why="explain", score=4, side="left", cut=True)

# ───────── 9. a mini-series panel filling with episodes ─────────
a, b = D.win(520.0); t_series = E.w("<words that name the series>", a)
E.enter("#pl-c", t_series, "focus", lead=0.3); E.sfx(t_series - 0.4, "woosh")
for i in range(4): E.enter(f"#pl-r{i}", t_series + 0.5 + i * 0.5, "rise", lead=0.1); E.sfx(t_series + 0.5 + i * 0.5, "pop", -27)
E.count("#pl-n", t_series + 0.5, 0, 4, 1.6)
E.float_(K.custom("playlist", t_series - 0.4, b - 0.25, D.playlist("pl", 4), (640, 600), name="playlist", text="mini-series"), why="demonstrate", score=4, side="left")

# ───────── 10. a motivated punch-in on a line that matters (only while the creator is full screen) ─────────
a, b = D.win(600.0); t = E.w("<the first word of the line that matters>", a)
E.punch(t - 0.05, b, "key takeaway: the viewer sees themselves in the point")

E.build()
