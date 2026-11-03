#!/usr/bin/env python3
"""Real interfaces and bigger graphics for the glass explainer reel, sized for the panel layout's graphics area
(y 380-1190, x 65-1015). Every call takes the scene first and uses the engine's timing (an element lands ON its word):

    import glass_engine as E, glass_kit as K
    with E.scene(12.0, 21.5) as s:
        K.person(s, "assets/media/guest.mp4", 300, 420, 560, t=12.4, tag="Guest name")     # real photo / clip, never cropped
        K.ytchannel(s, "Channel Name", "@channelhandle", 730, 470, t=13.1, avatar="assets/media/channel.jpg", count=(0, 400000, 14.0))
        K.notifs(s, [("Instagram", "sarah commented: sent!", 15.2, False)], top=430)       # real Instagram notifications
        K.gdoc(s, "Hook Bank", ["Curiosity hooks", "Proof hooks"], 400, t=17.0, hl=[(0, 17.9), (1, 18.8)])
        K.saved(s, "assets/media/reel-cover.jpg", 540, 400, t=19.0, t_tap=19.8)                   # a Reel being saved
        K.graph(s, [(0, 300), (300, 250), (600, 120), (820, 20)], 540, 430, t=20.0, dur=1.2, label="views")
        K.versus(s, ("Before", "A tip"), ("After", "A system"), 430, t_a=20.2, t_b=21.0)

Shapes: cards and chart frames are RECTANGULAR glass (corner radius 8). Only real interfaces keep their own shape
(an iOS notification is rounded because the real one is). No stacked oval pills.
Anything that is a stand-in is recorded as a mock-up (E.asset(..., mock=True)) and listed at the end of the build."""
import json, os, subprocess
import glass_engine as E

ANON = '<svg viewBox="0 0 24 24" width="100%" height="100%"><rect width="24" height="24" fill="#3A3A3C"/><circle cx="12" cy="9.4" r="4.2" fill="#8E8E93"/><path d="M3.4,24 C4.2,16.4 19.8,16.4 20.6,24 Z" fill="#8E8E93"/></svg>'
DOCI = '<svg viewBox="0 0 48 64" width="30" height="40"><path d="M4,0 H30 L48,18 V60 a4,4 0 0 1 -4,4 H4 a4,4 0 0 1 -4,-4 V4 a4,4 0 0 1 4,-4 Z" fill="#4285F4"/><path d="M30,0 L48,18 H34 a4,4 0 0 1 -4,-4 Z" fill="#A1C2FA"/><path d="M11,30 H37 M11,38 H37 M11,46 H29" stroke="#fff" stroke-width="3.4" stroke-linecap="round"/></svg>'
YTICK = '<svg viewBox="0 0 24 24" width="1em" height="1em" style="font-size:.6em"><circle cx="12" cy="12" r="11" fill="#AAA"/><path d="M7,12.5 L10.5,16 L17,9" fill="none" stroke="#0F0F0F" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
GREEN, RED = "#2FA65A", "#B3261E"
ME = "assets/proof/avatar.jpg"          # the creator's profile picture (copied into every project by 08_new_project.py; a neutral grey one if none was supplied)


def igicon(u, sz=38):
    return (f'<svg viewBox="0 0 48 48" width="{sz}" height="{sz}"><defs><radialGradient id="ig{u}" cx="30%" cy="107%" r="150%"><stop offset="0" stop-color="#FEDA75"/><stop offset=".25" stop-color="#FA7E1E"/>'
            f'<stop offset=".5" stop-color="#D62976"/><stop offset=".75" stop-color="#962FBF"/><stop offset="1" stop-color="#4F5BD5"/></radialGradient></defs><rect width="48" height="48" rx="12" fill="url(#ig{u})"/>'
            '<rect x="11" y="11" width="26" height="26" rx="8" fill="none" stroke="#fff" stroke-width="3"/><circle cx="24" cy="24" r="6.5" fill="none" stroke="#fff" stroke-width="3"/><circle cx="32.2" cy="15.8" r="1.9" fill="#fff"/></svg>')


def _css(key, css):
    if key not in E.KCSS: E.KCSS.add(key); E._C.append(css)


def _beat(s, i, t):
    E.BEATS.append({"t": round(t + 0.35, 3), "kind": "element", "id": i}); s.cue(t)


def size_of(src):
    """(width, height) of an image or video in the project, so a card can match the asset's own shape."""
    p = os.path.join(E.ROOT, src)
    if src.lower().endswith((".mp4", ".mov", ".webm", ".m4v")):
        w, h = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", p]).decode().strip().split(",")[:2]
        return int(w), int(h)
    from PIL import Image
    return Image.open(p).size


# ------------------------------------------------------------------ a glass card (a frame for your own content)
def card(s, cx, top, w, h, t, inner="", label=None, pad=24):
    """A rectangular glass card. inner = your HTML (laid out inside, relative). label = a small accent chip on its top edge."""
    i = E.nid("gc"); E._check(top, top + h, "card")
    lab = f'<div class="chip" style="position:absolute;left:50%;top:-18px;transform:translateX(-50%);font-size:26px;opacity:1">{E.tx(label)}</div>' if label else ""
    s._add(i, E._wrap(i, cx, top, f'<div id="{i}" class="gcard" style="width:{w}px;height:{h}px;padding:{pad}px">{inner}{lab}</div>'), t)
    if label: E.wording(label, "card label")
    return i


# ------------------------------------------------------------------ a real person: photo or clip shown WHOLE
def person(s, src, cx, top, h, t, tag=None, origin=None, hot=False):
    """A real photo or (muted) clip of the person being talked about, never cropped: the card takes the asset's own
    shape, h px tall. tag = their name on a small glass strip. origin = where the file came from (for the report)."""
    w0, h0 = size_of(src); w = round(h * w0 / h0)
    if origin: E.asset(src, origin)
    i = s.img(src, cx, top, w, h, t, radius=10, fit="cover", video=src.lower().endswith((".mp4", ".mov", ".webm", ".m4v")))
    if tag:
        j = E.nid("pt"); _css("ptag", '.ptag { position: absolute; padding: 6px 14px 8px; border-radius: 6px; font-size: 26px; line-height: 1; white-space: nowrap; opacity: 0; background: rgba(8,8,8,.62); -webkit-backdrop-filter: blur(14px); backdrop-filter: blur(14px); border: 1px solid rgba(255,255,255,.4); box-shadow: inset 0 1px 0 rgba(255,255,255,.4); z-index: 2; }')
        s.raw(f'<div id="{j}" class="ptag" style="left:{round(cx - w / 2 + 12)}px;top:{round(top + h - 52)}px">{E.tx(tag)}</div>', js=f'fin("#{j}",{round(t + 0.12, 3)});', ids=[j])
    if hot: s.hot(i, t + 0.4)
    return i


# ------------------------------------------------------------------ Instagram notification banners (iOS, dark). Newest on top, pile moves down.
NCSS = """.nfw { position: absolute; z-index: 1; }
      .nb { display: flex; align-items: center; gap: 22px; padding: 0 28px; box-sizing: border-box; border-radius: 40px; background: linear-gradient(180deg, rgba(255,255,255,.10), rgba(255,255,255,.02)), rgba(40,40,43,.74); -webkit-backdrop-filter: blur(26px) saturate(160%); backdrop-filter: blur(26px) saturate(160%); border: 1px solid rgba(255,255,255,.2); box-shadow: inset 0 1.5px 0 rgba(255,255,255,.28), 0 20px 50px rgba(0,0,0,.55); font-family: -apple-system, "SF Pro Text", "HelvR", Helvetica, sans-serif; letter-spacing: 0; color: #fff; opacity: 0; }
      .nav { width: 86px; height: 86px; border-radius: 43px; background-size: cover; background-position: center; position: relative; flex: none; } .nav > svg:first-child { border-radius: 43px; display: block; }
      .nig { position: absolute; right: -8px; bottom: -8px; width: 38px; height: 38px; border-radius: 10px; box-shadow: 0 0 0 3px rgba(40,40,43,1); } .nig svg { display: block; }
      .nt { flex: 1; min-width: 0; } .n1 { display: flex; justify-content: space-between; align-items: baseline; font-size: 29px; font-weight: 600; } .ntm { font-size: 23px; font-weight: 400; color: rgba(235,235,245,.6); }
      .n2 { font-size: 29px; font-weight: 400; color: rgba(255,255,255,.94); margin-top: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }"""


def notifs(s, items, top=420, w=880, mock=True):
    """Instagram notifications. items: [(title, body, t, me)] oldest first; me=True uses the creator's profile picture, otherwise
    the default grey one (or pass a picture path instead of True/False). Each lands on its word; the newest sits on
    top and the pile moves down. Up to 4 fit. mock=True records the wording as a mock-up for the report."""
    i = E.nid("nf"); H, G = 150, 16; n = len(items); E._check(top, top + n * (H + G) - G, "notifications"); _css("nb", NCSS); ids, htm, js = [], "", ""
    for k, (title, body, t, me) in enumerate(items):
        pic = ME if me is True else (me or None)
        av = f'<div class="nav" style="background-image:url({pic})">' if pic else f'<div class="nav">{ANON}'
        htm += (f'<div id="{i}w{k}" class="nfw" style="left:{540 - w // 2}px;top:{top}px;width:{w}px"><div id="{i}n{k}" class="nb" style="height:{H}px">{av}<span class="nig">{igicon(i + str(k))}</span></div>'
                f'<div class="nt"><div class="n1"><span>{E._html.escape(title)}</span><span class="ntm">now</span></div><div class="n2">{E._html.escape(body)}</div></div></div></div>')
        t0 = round(max(0, t - E.EARLY), 3)
        js += f'tl.fromTo("#{i}n{k}",{{opacity:0,y:-44,scale:0.96,filter:"blur(12px)"}},{{opacity:1,y:0,scale:1,filter:"blur(0px)",duration:0.45,ease:"power3.out"}},{t0});'
        for j in range(k): js += f' tl.to("#{i}w{j}",{{y:{(H + G) * (k - j)},duration:0.45,ease:"power3.out"}},{t0});'
        ids.append(f"{i}n{k}"); _beat(s, f"{i}n{k}", t)
        if k: E.sfx(t - E.EARLY, "accept" if me is True else "pop", -21)
        if mock: E.asset("Instagram notification", "drawn here (iOS banner mock-up)", f'wording invented: "{title}: {body}"', mock=True)
    s.raw(htm, js=js, ids=ids); return ids


# ------------------------------------------------------------------ Google Docs window: scrolls to and highlights the headings the speaker names
GCSS = """.gd { position: relative; border-radius: 14px; background: #F9FBFD; overflow: hidden; box-shadow: 0 0 0 1.5px rgba(255,255,255,.5), 0 24px 60px rgba(0,0,0,.6); font-family: "HelvR", Arial, Helvetica, sans-serif; letter-spacing: 0; color: #1F1F1F; opacity: 0; }
      .gtop { height: 76px; display: flex; align-items: center; gap: 14px; padding: 0 20px; } .gic { flex: none; display: flex; } .gtt { flex: 1; min-width: 0; }
      .gname { font-size: 24px; white-space: nowrap; } .gstar { color: #5F6368; font-size: 21px; margin-left: 6px; } .gmenu { display: flex; gap: 14px; font-size: 16px; color: #444746; margin-top: 4px; }
      .gshare { display: flex; align-items: center; gap: 8px; height: 46px; padding: 0 22px; border-radius: 23px; background: #C2E7FF; color: #001D35; font-family: "HelvB"; font-size: 18px; }
      .gav { width: 44px; height: 44px; border-radius: 22px; background: #BDC1C6 center/cover; flex: none; }
      .gbar { margin: 0 16px; height: 42px; border-radius: 21px; background: #EDF2FA; display: flex; align-items: center; gap: 16px; padding: 0 22px; font-size: 16px; color: #444746; } .gbar i { width: 1.5px; height: 20px; background: #C7C7C7; } .gbar b { font-family: "HelvB"; } .gbar u { text-underline-offset: 3px; }
      .gcanvas { position: absolute; left: 0; right: 0; top: 128px; bottom: 0; overflow: hidden; }
      .gpage { position: absolute; left: 12%; top: 12px; width: 76%; background: #fff; box-shadow: 0 1px 3px rgba(60,64,67,.3), 0 4px 8px rgba(60,64,67,.15); padding: 38px 50px 60px; box-sizing: border-box; }
      .gpage h1 { font-family: "HelvR"; font-weight: 400; font-size: 36px; margin: 0 0 18px; } .gpage h2 { font-family: "HelvR"; font-weight: 400; font-size: 26px; height: 32px; line-height: 32px; margin: 22px 0 14px; white-space: nowrap; } .gpage h2 span { padding: 2px 4px; margin-left: -4px; border-radius: 3px; }
      .gln { height: 10px; border-radius: 5px; background: #DADCE0; margin: 0 0 14px; }"""


def gdoc(s, title, headings, top, t, hl=(), cx=540, w=900, h=600, doc_title=None, me=True, mock=True):
    """A Google Docs window (white, real layout). headings = the section headings in the doc; hl = [(heading index, t)]:
    the page scrolls to that heading and highlights it when the speaker names it. doc_title = the big title on the page
    (default: the file name). Body lines are grey bars (no invented copy). No collaborator cursors."""
    i = E.nid("gd"); E._check(top, top + h, "Google Doc"); _css("gd", GCSS); bars = lambda ws: "".join(f'<p class="gln" style="width:{x}%"></p>' for x in ws)
    page = f'<h1>{E._html.escape(doc_title or title)}</h1>' + bars((96, 88, 92, 60))
    for k, hd in enumerate(headings): page += f'<h2><span id="{i}h{k}">{E._html.escape(hd)}</span></h2>' + bars(((94, 86, 90, 72), (92, 84, 95, 66), (90, 96, 82, 70))[k % 3])
    av = f'<div class="gav" style="background-image:url({ME})"></div>' if me else '<div class="gav"></div>'
    htm = (f'<div id="{i}" class="gd" style="width:{w}px;height:{h}px"><div class="gtop"><span class="gic">{DOCI}</span><div class="gtt"><div class="gname">{E._html.escape(title)} <span class="gstar">&#9734;</span></div>'
           '<div class="gmenu"><span>File</span><span>Edit</span><span>View</span><span>Insert</span><span>Format</span><span>Tools</span><span>Help</span></div></div>'
           f'<div class="gshare">Share</div>{av}</div><div class="gbar"><span>100%</span><i></i><span>Normal text</span><i></i><span>Arial</span><i></i><span>11</span><i></i><b>B</b><em>I</em><u>U</u></div>'
           f'<div class="gcanvas"><div id="{i}p" class="gpage">{page}</div></div></div>')
    js = ""
    for k, tt in hl:                      # page geometry: h1 block 38+54+4*24 = 188, each section 22+32+14+4*24 = 164
        y = max(0, 188 + k * 164 - 40)
        js += f' tl.to("#{i}p",{{y:{-y},duration:0.8,ease:"power2.inOut"}},{round(max(0, tt - 0.55), 3)}); tl.to("#{i}h{k}",{{backgroundColor:"#D3E3FD",duration:0.3,ease:"power2.out"}},{round(tt - 0.05, 3)});'
        E.BEATS.append({"t": round(tt + 0.35, 3), "kind": "element", "id": f"{i}h{k}"})
    s._add(i, E._wrap(i, cx, top, htm), t, js=js)
    E.asset(f'Google Doc "{title}"', "drawn here (Google Docs mock-up)" if mock else "the real document, rebuilt", "headings: " + " / ".join(headings) + "; body lines are grey bars", mock=mock)
    return i


# ------------------------------------------------------------------ a Reel being saved (phone, tap on the bookmark, "Saved")
SCSS = """.ph { position: relative; border-radius: 50px; background: #0B0B0C; border: 8px solid #2A2A2D; box-shadow: 0 0 0 2px #55555A, 0 30px 70px rgba(0,0,0,.7); overflow: hidden; box-sizing: border-box; font-family: -apple-system, "SF Pro Text", "HelvR", Helvetica, sans-serif; letter-spacing: 0; color: #fff; opacity: 0; }
      .ph img.pc { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block; } .psh { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,.45), rgba(0,0,0,0) 22%, rgba(0,0,0,0) 62%, rgba(0,0,0,.7)); }
      .prt { position: absolute; left: 20px; top: 52px; font-size: 26px; font-weight: 700; } .pisl { position: absolute; left: 50%; top: 13px; width: 100px; height: 28px; margin-left: -50px; border-radius: 14px; background: #000; }
      .prail { position: absolute; right: 13px; bottom: 124px; display: flex; flex-direction: column; gap: 24px; } .prail span { display: block; width: 38px; height: 38px; filter: drop-shadow(0 2px 6px rgba(0,0,0,.5)); }
      .pmeta { position: absolute; left: 18px; right: 70px; bottom: 28px; } .pmrow { display: flex; align-items: center; gap: 10px; font-size: 18px; } .pmav { width: 36px; height: 36px; border-radius: 18px; border: 2px solid #fff; background: #3A3A3C center/cover; overflow: hidden; }
      .pcap { font-size: 17px; line-height: 1.3; margin-top: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
      .ptc { position: absolute; width: 76px; height: 76px; border-radius: 38px; background: rgba(255,255,255,.55); border: 3px solid rgba(255,255,255,.9); box-shadow: 0 8px 24px rgba(0,0,0,.35); opacity: 0; z-index: 3; }
      .ptoast { position: absolute; height: 62px; padding: 0 26px; border-radius: 31px; background: rgba(38,38,40,.95); display: flex; align-items: center; gap: 10px; font-family: -apple-system, "HelvB", sans-serif; font-weight: 600; font-size: 25px; letter-spacing: 0; color: #fff; opacity: 0; z-index: 3; }"""
_IC = lambda d, i="": f'<span><svg viewBox="0 0 32 32" width="38" height="38"><path {i} d="{d}" fill="rgba(255,255,255,0)" stroke="#fff" stroke-width="2.6" stroke-linejoin="round"/></svg></span>'


def saved(s, cover, cx, top, t, t_tap, h=760, name="creator", caption="", avatar=None, origin=None):
    """An Instagram Reel in a phone; at t_tap a finger presses the bookmark, it fills, a "Saved" toast appears.
    cover = a real reel cover (9:16). name / caption = the account and caption shown (generic unless you have the real ones)."""
    i = E.nid("sv"); w = round(h * 0.513); E._check(top, top + h, "saved reel"); _css("ph", SCSS); x0 = round(cx - w / 2)
    if origin: E.asset(cover, origin)
    av = f'<span class="pmav" style="background-image:url({avatar})"></span>' if avatar else f'<span class="pmav">{ANON}</span>'
    rail = (_IC("M16,28 C4,19 3,11 8,7 C12,4 15,6 16,9 C17,6 20,4 24,7 C29,11 28,19 16,28 Z") + _IC("M16,4 A12,12 0 1 1 9,25.7 L4,27.5 L5.8,22.5 A12,12 0 0 1 16,4 Z")
            + _IC("M28,4 L3,13 L13,17.5 L17.5,28 Z M13,17.5 L28,4") + _IC("M7,3 H25 V29 L16,22 L7,29 Z", f'id="{i}bk"'))
    htm = (f'<div id="{i}" class="ph" style="width:{w}px;height:{h}px"><img class="pc" src="{cover}"/><div class="psh"></div><div class="prt">Reels</div><div class="prail">{rail}</div>'
           f'<div class="pmeta"><div class="pmrow">{av}<b>{E._html.escape(name)}</b></div><div class="pcap">{E._html.escape(caption)}</div></div><div class="pisl"></div></div>')
    bx, by = x0 + w - 13 - 8 - 19, top + h - 124 - 8 - 19            # centre of the bookmark (last icon in the rail)
    extra = (f'<div id="{i}tc" class="ptc" style="left:{bx - 38}px;top:{by - 38}px"></div>'
             f'<div id="{i}to" class="ptoast" style="left:{cx - 92}px;top:{round(top + h * 0.47)}px"><svg viewBox="0 0 32 32" width="24" height="24"><path d="M7,3 H25 V29 L16,22 L7,29 Z" fill="#fff"/></svg>Saved</div>')
    js = (f' tl.fromTo("#{i}tc",{{opacity:0,scale:1.5,x:90,y:120}},{{opacity:0.7,scale:1,x:0,y:0,duration:0.4,ease:"power2.out"}},{round(t_tap - 0.5, 3)});'
          f' tl.to("#{i}tc",{{scale:0.8,duration:0.1,ease:"power2.in"}},{round(t_tap - 0.1, 3)}); tl.set("#{i}bk",{{attr:{{fill:"#FFFFFF"}}}},{t_tap});'
          f' tl.to("#{i}tc",{{opacity:0,scale:1.2,duration:0.2,ease:"power2.in"}},{round(t_tap + 0.05, 3)});'
          f' tl.fromTo("#{i}to",{{opacity:0,y:12,filter:"blur(8px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.3,ease:"power3.out"}},{round(t_tap + 0.1, 3)});')
    s._add(i, E._wrap(i, cx, top, htm), t); s.raw(extra, js=js, ids=[f"{i}tc", f"{i}to"])
    E.BEATS.append({"t": round(t_tap + 0.5, 3), "kind": "element", "id": f"{i}to"}); E.sfx(t_tap, "pop", -21)
    E.asset("Instagram Reel in a phone", "drawn here (phone + Reels interface mock-up) around the cover " + cover, f'account "{name}", caption "{caption}"', mock=avatar is None)
    return i


# ------------------------------------------------------------------ a simple YouTube channel card (no banner): picture, name, handle, subscribers, button
YCSS = """.ych { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: .5em; box-sizing: border-box; padding: 1.1em; font-family: -apple-system, "SF Pro Text", "HelvR", Helvetica, sans-serif; letter-spacing: 0; color: #F1F1F1; }
      .yav { width: 4.6em; height: 4.6em; border-radius: 50%; background: #3A3A3C center/cover; overflow: hidden; flex: none; }
      .yn { font-size: 1.6em; font-weight: 700; display: flex; align-items: center; gap: .3em; white-space: nowrap; } .yh { font-size: .95em; color: #AAA; margin-top: -.35em; }
      .ys { font-size: 1.2em; color: #AAA; white-space: nowrap; } .ys b { color: #F1F1F1; font-weight: 700; font-variant-numeric: tabular-nums; }
      .yb { width: 100%; height: 2.3em; border-radius: 1.15em; background: #F1F1F1; color: #0F0F0F; display: flex; align-items: center; justify-content: center; font-size: 1.1em; font-weight: 600; margin-top: .2em; }"""


def ytchannel(s, name, handle, cx, top, t, subs="", w=440, h=430, fs=26, avatar=None, count=None, tone=None):
    """A YouTube channel as a simple glass card (rule: build it by hand, no banner). avatar = their real channel
    picture (default grey one if you cannot get it; the name still identifies them). subs = the count as text, or
    count=(from, to, t_start[, seconds]) ticks it up and turns it the accent colour (or tone, e.g. K.GREEN) on landing."""
    i = E.nid("yt"); E._check(top, top + h, "channel card"); _css("ych", YCSS)
    av = f'<div class="yav" style="background-image:url({avatar})"></div>' if avatar else f'<div class="yav">{ANON}</div>'
    first = f"{count[0]:,}" if count else subs
    htm = (f'<div id="{i}" class="gcard ych" style="width:{w}px;height:{h}px;font-size:{fs}px">{av}<div class="yn">{E._html.escape(name)} {YTICK}</div><div class="yh">{E._html.escape(handle)}</div>'
           f'<div class="ys"><b id="{i}n">{first}</b> subscribers</div><div class="yb">Subscribe</div></div>')
    js = ""
    if count:
        a, b, tc = count[:3]; d = count[3] if len(count) > 3 else 1.25; col = tone or "var(--o)"
        js = (f' counter("#{i}n",{a},{b},{tc},{d},"",""); tl.to("#{i}n",{{color:"{col}",duration:0.25}},{round(tc + d - 0.1, 3)}); sweep("#{i}",{round(tc + d - 0.15, 3)});')
        E.sfx(tc, "data", -24); E.sfx(tc + d, "shine", -21); E.BEATS.append({"t": round(tc + d + 0.2, 3), "kind": "element", "id": f"{i}n"})
    s._add(i, E._wrap(i, cx, top, htm), t, js=js)
    E.asset(f"YouTube channel card: {name} {handle}", "built here (simple channel card, no banner)", "picture: " + (avatar or "default grey profile picture"), mock=avatar is None)
    return i


# ------------------------------------------------------------------ a drawn graph in a glass chart frame, a dot riding the front of the line
def graph(s, pts, cx, top, t, dur=1.2, w=820, h=420, label="", ghost=None, col=None, marks=(), t_frame=None):
    """pts / ghost: points in a box (w - 80) x (h - 90), y down (0 = top). The frame arrives at t_frame (default: t - 0.3),
    the line draws from t over dur with a dot at its front. ghost = a dashed comparison line. marks = [(x, y, t)] dots
    that appear on the line. col = line colour (default the accent colour; K.GREEN / K.RED for good / bad)."""
    i = E.nid("gr"); E._check(top, top + h, "graph"); col = col or "var(--o)"; W, H = w - 80, h - 90
    _css("gr", '.grl { position: absolute; right: 22px; bottom: 12px; font-size: 24px; color: rgba(255,255,255,.6); white-space: nowrap; }')
    P = " ".join(f"{x},{y}" for x, y in pts)
    gh = f'<polyline points="{" ".join(f"{x},{y}" for x, y in ghost)}" fill="none" stroke="rgba(255,255,255,.34)" stroke-width="4" stroke-dasharray="10 12"/>' if ghost else ""
    mk = "".join(f'<circle id="{i}m{k}" cx="{x}" cy="{y}" r="10" fill="{col}" stroke="#fff" stroke-width="3" opacity="0"/>' for k, (x, y, _) in enumerate(marks))
    htm = (f'<div id="{i}" class="gcard" style="width:{w}px;height:{h}px"><svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:40px;top:34px;overflow:visible">'
           f'<line x1="0" y1="{H}" x2="{W}" y2="{H}" stroke="rgba(255,255,255,.3)" stroke-width="2.5"/><line x1="0" y1="0" x2="0" y2="{H}" stroke="rgba(255,255,255,.3)" stroke-width="2.5"/>{gh}'
           f'<polyline id="{i}l" points="{P}" fill="none" stroke="{col}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/>{mk}'
           f'<circle id="{i}f" cx="{pts[0][0]}" cy="{pts[0][1]}" r="11" fill="#fff" opacity="0"/></svg>' + (f'<div class="grl">{E.tx(label)}</div>' if label else "") + '</div>')
    js = (f' draw("#{i}l",{t},{dur}); (function () {{ const PT = {json.dumps([list(p) for p in pts])}, f = document.getElementById("{i}f"), q = {{ x: PT[0][0] }};'
          ' function yAt(x) { for (let k = 1; k < PT.length; k++) { if (x <= PT[k][0]) { const a = PT[k - 1], b = PT[k]; return a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]); } } return PT[PT.length - 1][1]; }'
          f' tl.set(f, {{ opacity: 1 }}, {t}); tl.fromTo(q, {{ x: PT[0][0] }}, {{ x: PT[PT.length - 1][0], duration: {dur}, ease: "power2.inOut", onUpdate: function () {{ f.setAttribute("cx", q.x.toFixed(1)); f.setAttribute("cy", yAt(q.x).toFixed(1)); }} }}, {t}); }})();')
    for k, (x, y, tm) in enumerate(marks): js += f' tl.fromTo("#{i}m{k}",{{opacity:0,scale:0.2,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:0.25,ease:"power2.out"}},{tm});'
    s._add(i, E._wrap(i, cx, top, htm), t - 0.3 if t_frame is None else t_frame, js=js); E.BEATS.append({"t": round(t + dur + 0.1, 3), "kind": "element", "id": f"{i}l"})
    if label: E.wording(label, "graph label")
    return i


# ------------------------------------------------------------------ comparison: two rectangular glass cards, good = green, bad = red
VCSS = """.vs { --tone: 0; position: relative; box-sizing: border-box; padding: 22px 30px 26px; opacity: 0; }
      .vs small { display: inline-block; padding: 5px 12px 6px; border-radius: 4px; font-size: 22px; letter-spacing: .08em; text-transform: uppercase; background: rgba(255,255,255,.1); color: rgba(255,255,255,.7); }
      .vs div { font-size: 42px; line-height: 1.05; margin-top: 16px; }
      .vs.bad small { background: rgba(179,38,30,.26); color: #FFB0A8; } .vs.good small { background: rgba(47,166,90,.24); color: #9BE8B8; }
      .vs.good { border-color: color-mix(in srgb, #2FA65A calc(var(--tone) * 100%), rgba(255,255,255,.44)); box-shadow: inset 0 1.5px 0 rgba(255,255,255,.55), 0 20px 50px rgba(0,0,0,.5), 0 0 calc(var(--tone) * 44px) rgba(47,166,90,.5); }"""


def versus(s, a, b, top, t_a, t_b, t_hot=None, w=430, h=250, gap=40, stacked=False):
    """Two rectangular glass cards: a = (tag, text) the weaker / "before" side (red tag), b = (tag, text) the stronger /
    "after" side (green tag; lights green with a sweep at t_hot, and a dims). Side by side, or stacked=True."""
    i = E.nid("vs"); _css("vs", VCSS); E._check(top, top + (2 * h + gap if stacked else h), "comparison")
    pos = [(540, top), (540, top + h + gap)] if stacked else [(540 - (w + gap) / 2, top), (540 + (w + gap) / 2, top)]
    ids = []
    for k, ((tag, text), cls, t) in enumerate(((a, "bad", t_a), (b, "good", t_b))):
        j = f"{i}{'ab'[k]}"; ids.append(j)
        s._add(j, E._wrap(j, pos[k][0], pos[k][1], f'<div id="{j}" class="gcard vs {cls}" style="width:{w}px;height:{h}px"><small>{E.tx(tag)}</small><div>{E.tx(text)}</div></div>'), t)
        E.wording(f"{tag}: {text}".replace("\n", " "), "comparison card")
    if t_hot is not None:
        s.raw("", js=f' tl.to("#{ids[1]}",{{"--tone":1,duration:0.3,ease:"power2.out"}},{t_hot}); sweep("#{ids[1]}",{t_hot}); tl.to("#{ids[0]}",{{opacity:0.4,duration:0.3}},{t_hot});'); E.sfx(t_hot, "shine2", -22)
    return ids
