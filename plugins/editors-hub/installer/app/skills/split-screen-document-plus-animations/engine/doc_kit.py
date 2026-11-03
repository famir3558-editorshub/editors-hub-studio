"""doc_kit.py - interface pieces for the "split screen document plus animations" format.
Import as D next to the engine and kit:   import yt_engine as E, yt_kit as K, doc_kit as D

The rule for this format: a graphic ILLUSTRATES what the creator is describing (an interface, an object, a real asset).
It never restates their words as a text card. Everything here returns HTML for a K.custom(...) body, or a finished piece.
Figures inside these pieces are placeholders for the picture: pass real numbers for real people and real channels.
Colours come from the engine's CSS variables (--o accent, --paper, --grey, --good, --bad); the interface pieces use the
platforms' own neutral colours (white card, dark card, YouTube red) on purpose, so they read as the real thing.

  D.win(t)                      the full-screen window [a, b] that time t sits in (from windows.json). Graphics live inside these.
  D.views_card(...)             a number climbing while the thing the creator actually wants stays at 0 (returns a piece)
  D.ig_card(sid, lines, name)   Instagram-style profile header whose bio lines can be swapped (the creator's profile picture
                                from setup is used when there is one, otherwise a neutral person icon)
  D.chan(cid, top, avatar, name, meta, sid, tag)   YouTube channel card with a REAL avatar and REAL figures
  D.vrow(rid, w, h, duration, html)                one YouTube video row (thumbnail block + whatever sits beside it)
  D.note(nid, top, bg, icon, title, sub)           iOS-style notification on glass
  D.playlist(sid, n, labels)    a YouTube playlist / mini-series panel
  D.drop(sel, t, sound)         the notification drop-in entrance
  Icons: D.PLAY, D.CAL, D.CARD, D.MAIL, D.DOC, D.CUR (cursor).  .format(size, colour) on PLAY / MAIL / DOC.
Classes worth knowing: .xc dark card, .xw white card, .xy YouTube-dark card, .xk small caps label, .xn big number, .chip green pill,
.tile icon tile, .dsh dashboard tile, .yl / .yl.s grey text lines (use these instead of made-up titles), .xpill, .xlab, .xar."""
import json
import yt_engine as E, yt_kit as K
M = "assets/media/"
CSS = """
.xc{position:absolute;inset:14px;border-radius:28px;background:#14110f;border:1px solid var(--line);box-shadow:var(--sh);padding:34px 38px}
.xk{font-family:"HelvB";font-size:22px;letter-spacing:.2em;text-transform:uppercase;color:var(--grey)}
.xn{font-family:"HelvB";font-size:128px;letter-spacing:-.06em;line-height:.95;color:var(--paper);font-variant-numeric:tabular-nums;margin-top:6px}
.xdiv{height:1px;background:var(--line);margin:26px 0 24px}
.xup{display:inline-block;font-family:"HelvB";font-size:26px;color:var(--good);margin-left:14px;letter-spacing:-.02em;vertical-align:middle}
.xw{position:absolute;inset:14px;border-radius:28px;background:#fff;color:#111;box-shadow:var(--sh);padding:34px 36px;font-family:var(--sf)}
.xav{width:118px;height:118px;border-radius:50%;background:#DBDBDB;color:#fff;overflow:hidden;flex:none;padding:14px 14px 0}
.xst{display:flex;gap:34px;font-size:22px;color:#111;text-align:center}.xst b{display:block;font-size:30px;font-weight:700;letter-spacing:-.02em}
.xbio{position:relative;margin-top:14px;height:84px}.xbio div{position:absolute;left:0;top:0;right:0;font-size:31px;line-height:1.3;letter-spacing:-.015em}
.xbt{display:flex;gap:12px;margin-top:22px}.xbt span{flex:1;text-align:center;border-radius:12px;padding:15px 0;font-size:25px;font-weight:600;background:#EFEFEF;color:#111}.xbt span.f{background:#0095F6;color:#fff}
.xy{position:absolute;left:14px;right:14px;border-radius:24px;background:#0F0F0F;border:1px solid rgba(255,255,255,.14);box-shadow:var(--sh);padding:28px 32px;font-family:var(--sf);color:#F1F1F1}
.xy u{display:block;text-decoration:none;font-size:22px;color:#AAA;margin-bottom:10px}.xy p{margin:0;font-size:29px;line-height:1.32;letter-spacing:-.01em}
.xpill{position:absolute;height:104px;border-radius:999px;background:rgba(18,15,13,.94);border:2px solid rgba(242,240,236,.22);display:flex;align-items:center;justify-content:center;font-family:"HelvB";font-size:40px;letter-spacing:-.035em;color:var(--paper);box-shadow:0 18px 44px rgba(0,0,0,.45);padding:0 40px;white-space:nowrap}
.xlab{position:absolute;font-family:"HelvB";font-size:21px;letter-spacing:.22em;text-transform:uppercase;color:var(--grey);text-align:center}
.xar{position:absolute;font-family:"HelvB";font-size:44px;color:var(--o)}

.yrow{position:relative;display:flex;gap:22px;align-items:center;padding:14px;border-radius:20px;border:2px solid transparent}
.yth{position:relative;flex:none;border-radius:14px;background:linear-gradient(135deg,#3a332d,#191512);overflow:hidden}
.yth b{position:absolute;right:8px;bottom:8px;background:rgba(0,0,0,.82);border-radius:6px;padding:2px 8px;font:600 21px var(--sf);color:#fff}
.yl{height:16px;border-radius:8px;background:rgba(255,255,255,.34)}.yl.s{background:rgba(255,255,255,.16);height:13px;margin-top:12px}
.ymeta{font:400 25px var(--sf);color:#AAA;margin-top:12px}.ybig{font:700 40px var(--sf);letter-spacing:-.03em;color:#F1F1F1}
.nt{position:absolute;left:14px;right:14px;border-radius:32px;padding:24px 28px;display:flex;gap:22px;align-items:center;font-family:var(--sf)}
.nt .ic{width:92px;height:92px;border-radius:22px;display:flex;align-items:center;justify-content:center;flex:none}
.nt b{display:block;color:#fff;font-size:31px;font-weight:600;letter-spacing:-.01em}.nt span{display:block;color:rgba(255,255,255,.78);font-size:26px;margin-top:3px}
.chip{display:inline-flex;align-items:center;gap:10px;border-radius:999px;background:rgba(47,166,90,.2);border:2px solid #2FA65A;color:#fff;font:600 24px var(--sf);padding:8px 16px;margin-right:10px}
.tile{position:absolute;border-radius:24px;background:rgba(18,15,13,.95);border:2px solid rgba(242,240,236,.2);box-shadow:0 18px 44px rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center}
.dsh{border-radius:20px;background:#1b1714;border:1px solid var(--line);padding:22px 26px}
"""
_FULL = []


def _css():
    if CSS not in E.XCSS: E.css(CSS)


def win(t):
    """The full-screen window a time sits in. Fails loudly if the time is inside a document section."""
    if not _FULL: _FULL.extend(json.load(open(f"{E.ROOT}/windows.json"))["full"])
    for a, b in _FULL:
        if a - 0.02 <= t < b: return a, b
    raise SystemExit(f"D.win({t}): that time is inside a document section. Full-screen windows: {[(round(a, 1), round(b, 1)) for a, b in _FULL]}")


PLAY = '<svg width="{0}" height="{0}" viewBox="0 0 24 24"><path d="M8 5.5v13l11-6.5z" fill="{1}"/></svg>'
CAL = '<svg width="54" height="54" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="5" width="17" height="15" rx="3"/><path d="M3.5 10h17M8 3v4M16 3v4M8.5 15l2.3 2.3L15.5 13"/></svg>'
CARD = '<svg width="54" height="54" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"><rect x="2.5" y="5.5" width="19" height="13" rx="3"/><path d="M2.5 10h19M6.5 15h4"/></svg>'
MAIL = '<svg width="{0}" height="{0}" viewBox="0 0 24 24" fill="none" stroke="{1}" stroke-width="2" stroke-linejoin="round"><rect x="2.5" y="5" width="19" height="14" rx="3"/><path d="M3.5 7l8.5 6.5L20.5 7"/></svg>'
DOC = '<svg width="{0}" height="{0}" viewBox="0 0 24 24" fill="none" stroke="{1}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/></svg>'
CUR = '<svg width="54" height="54" viewBox="0 0 24 24"><path d="M5 3l14 8-6 1.6L10 19z" fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>'



def views_card(sid, a, b, t_views, t_zero, label2="Booked calls", v_from=1240, v_to=12480):
    """The signature: views keep climbing, the thing the creator actually wants stays at 0."""
    _css()
    body = (f'<div id="{sid}-c" class="xc h"><div class="xk">Views</div><div class="xn"><span id="{sid}-v">{v_from:,}</span><span id="{sid}-u" class="xup h">&#9650; rising</span></div>'
            f'<div class="xdiv"></div><div id="{sid}-r" class="h"><div class="xk">{label2}</div><div id="{sid}-z" class="xn">0</div></div></div>')
    E.enter(f"#{sid}-c", a, "focus"); E.sfx(a - 0.25, "woosh")
    E.count(f"#{sid}-v", t_views, v_from, v_to, max(1.6, t_zero - t_views + 1.0)); E.enter(f"#{sid}-u", t_views + 0.5, "fade"); E.sfx(t_views, "data", -27)
    E.tw(f"#{sid}-v", t_views + 0.9, 0.4, {"color": "#2FA65A"}, None, "power2.out")
    E.enter(f"#{sid}-r", t_zero, "rise"); E.tw(f"#{sid}-z", t_zero + 0.25, 0.35, {"color": "#B3261E"}, None, "power2.out"); E.sfx(t_zero, "pop", -25)
    return K.custom(sid, a, b, body, (600, 520), name="views-vs-calls", text=f"Views {label2}")


def ig_card(sid, lines, follow=True, name="Coach"):
    """A plain Instagram-style profile header (illustrative, not a real account). lines = [(id suffix, html)] stacked for swapping.
    name = the line under the counts. The creator's profile picture (assets/avatar.jpg, from setup) fills the circle when it exists."""
    _css()
    bio = "".join(f'<div id="{sid}-{k}" class="h">{t}</div>' for k, t in lines)
    av = E.brand_asset("avatar")
    face = f'<img src="{av}" style="width:100%;height:100%;object-fit:cover;display:block">' if av else K.PERSON
    return (f'<div id="{sid}-ig" class="xw h" style="bottom:auto;height:446px"><div style="display:flex;align-items:center;gap:34px"><div class="xav" style="{"padding:0" if av else ""}">{face}</div>'
            f'<div class="xst"><div><b>128</b>posts</div><div><b>2,341</b>followers</div><div><b>412</b>following</div></div></div>'
            f'<div style="font-size:27px;font-weight:700;margin-top:22px;letter-spacing:-.01em">{name}</div><div class="xbio">{bio}</div>'
            f'<div class="xbt"><span id="{sid}-fo" class="f">Follow</span><span>Message</span></div></div>')


def note(nid, top, bg, icon, title, sub):
    _css()
    return f'<div id="{nid}" class="nt glass h" style="top:{top}px"><div class="ic" style="background:{bg}">{icon}</div><div><b>{title}</b><span>{sub}</span></div></div>'


def chan(cid, top, av, name, meta, sid, tag=""):
    """av = file name inside assets/media (a real channel avatar). name / meta = exactly as the channel shows them."""
    _css()
    t = f'<div class="xk" style="color:var(--o);font-size:20px">{tag}</div>' if tag else ""
    return (f'<div id="{cid}" class="xy h" style="top:{top}px;display:flex;align-items:center;gap:28px;padding:26px 30px">'
            f'<div style="position:relative;width:150px;height:150px;border-radius:50%;overflow:hidden;flex:none">{E.img(M + av, 150, 150, sid=sid)}</div>'
            f'<div>{t}<div style="font-size:44px;font-weight:700;letter-spacing:-.03em">{name}</div><div style="font-size:25px;color:#AAA;margin-top:6px">{meta}</div></div></div>')


def vrow(rid, tw_, th_, dur, top_html, cls="h"):
    _css()
    return (f'<div id="{rid}" class="yrow {cls}"><div class="yth" style="width:{tw_}px;height:{th_}px"><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;opacity:.5">{PLAY.format(44, "#fff")}</div>'
            f'{f"<b>{dur}</b>" if dur else ""}</div><div style="flex:1;min-width:0">{top_html}</div></div>')


def drop(sel, t, sound="pop"):
    E.tw(sel, t - 0.1, 0.55, {"opacity": 1, "y": 0}, {"opacity": 0, "y": -44}, "back.out(1.2)"); E.sfx(t - 0.05, sound, -25)


def playlist(sid, n, labels=None):
    _css()
    rows = ""
    for i in range(n):
        lab = f'<div id="{sid}-l{i}" class="h ybig" style="font-size:34px">{labels[i]}</div>' if labels else '<div class="yl" style="width:%d%%"></div>' % (84 - i * 7)
        rows += vrow(f"{sid}-r{i}", 170, 96, "", f'<div class="ymeta" style="margin:0 0 8px">Episode {i + 1}</div>{lab}')
    return (f'<div id="{sid}-c" class="xy h" style="top:14px;padding:16px"><div style="display:flex;justify-content:space-between;align-items:center;margin:6px 10px 8px">'
            f'<div style="font:700 32px var(--sf);letter-spacing:-.02em">Your mini-series</div><div style="font:600 24px var(--sf);color:#AAA"><span id="{sid}-n">0</span> / {n}</div></div>{rows}</div>')
