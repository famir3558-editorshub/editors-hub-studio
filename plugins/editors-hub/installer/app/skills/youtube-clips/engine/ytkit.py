"""youtube-clips build kit: the per-video set-up and the small components the YouTube clip builds share.
Sits beside clip_engine.py in each project. Graphics are drawn once on the engine's 680x540 stage; show() places
them for the ratio being built (beside the speaker in 16:9 at the scale the face check allows; centred in the top half
or the frame in 9:16)."""
import json
import clip_engine as E

AV = '<svg viewBox="0 0 100 100" width="100%" height="100%"><circle cx="50" cy="40" r="17" fill="rgba(0,0,0,.38)"/><path d="M18 100c0-22 14-32 32-32s32 10 32 32z" fill="rgba(0,0,0,.38)"/></svg>'
TICK = '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
CROSS = '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>'
DOC = '<svg viewBox="0 0 24 24" width="100%" height="100%" fill="none" stroke="#fff" stroke-width="2" stroke-linejoin="round"><rect x="4" y="3" width="16" height="18" rx="2.5"/><path d="M8 8h8M8 12h8M8 16h5" stroke-linecap="round"/></svg>'

CSS = """
.bar { background: rgba(255,255,255,.22); border-radius: 8px; }
.pl-o .dot { background: var(--o); } .pl-g .dot { background: var(--g); } .pl-r .dot { background: var(--r); } .pl-w .dot { background: rgba(255,255,255,.22); }
.num { font: 700 120px/1 "SFB", sans-serif; letter-spacing: -0.05em; font-variant-numeric: tabular-nums; white-space: nowrap; }
.lab { font: 500 30px/1.1 "SFM", sans-serif; letter-spacing: -0.01em; color: var(--gy); white-space: nowrap; }
.tx { font: 600 36px/1.15 "SFS", sans-serif; letter-spacing: -0.02em; white-space: nowrap; }
.tag { height: 50px; border-radius: 25px; padding: 0 22px; font: 600 28px/50px "SFS", sans-serif; letter-spacing: -0.02em; white-space: nowrap; }
.tag.r { background: var(--r); box-shadow: 0 0 26px color-mix(in srgb, var(--r) 60%, transparent); } .tag.g { background: var(--g); }
.node { width: 150px; height: 150px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font: 700 60px "SFB", sans-serif; }
"""
_css = [False]; _scrim = []


def start(root, ratio, face):
    """The usual direct-to-camera set-up: centred, looking at the camera, sitting high in the frame. 9:16 captions just under the chin. Check frame 0 and adjust E.V / E.CAP when the framing differs."""
    E.init(root, ratio, face=face)
    for m in E.V.values(): m["X"] = 540
    for k in ("him", "him2"): E.V[k]["Y"] = 1110
    E.CAP["9x16"]["him"], E.CAP["9x16"]["him2"] = 1240, 1380
    E.V["himd"] = dict(E.V["him"]); E.CAP["9x16"]["himd"] = 1420   # "himd": a full-screen shot where the speaker is looking down (chin lower): caption lower
    _css[0] = False; _scrim.clear()


def hook(a, b, l1, l2):
    E.hook(a, b, l1, l2, top=62)


def show(a, b, html, js, box=(40, 20, 640, 520), css=""):
    """Put one stage of graphics on screen from a to b. box = where the content sits on the 680x540 surface."""
    c = css + ("" if _css[0] else CSS); _css[0] = True
    if E.R == "16x9":
        sc = E.fit(a, b, 40, box[2]); st = E.stage(a, b, 40, 110, sc, box=box); _scrim.append([a - 0.1, b])
    else:
        cy = 435 if E.mode_at(a + 0.05) == "split" else 800; SC = 1.45
        st = E.stage(a, b, round(540 - (box[0] + box[2]) / 2 * SC), round(cy - (box[1] + box[3]) / 2 * SC), SC, cut_in=True, cut_out=b < E.P["dur"] - 0.05)
    with st as s: s.add(html, c, js)


def finish():
    if E.R == "16x9" and _scrim:
        w = [_scrim[0][:]]
        for a, b in _scrim[1:]:
            if a - w[-1][1] < 1.2: w[-1][1] = b
            else: w.append([a, b])
        E.scrim([(max(0, a), b) for a, b in w])
    E.build()


# ---- HTML pieces (all start hidden; bring them in with fin / setp)
def pill(i, cls, icon, text, left, top, w, extra=""):
    return f'<div id="{i}" class="pill glass {cls}" style="left:{left}px;top:{top}px;width:{w}px;opacity:0"><span class="dot">{icon}</span><span>{text}</span>{extra}</div>'


def line(i, x1, y1, x2, y2, color="#fff", w=3.5):
    return f'<svg class="ln" viewBox="0 0 680 540" width="680" height="540"><line id="{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/></svg>'


def path(i, d, color="#fff", w=6):
    return f'<svg class="ln" viewBox="0 0 680 540" width="680" height="540"><path id="{i}" d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/></svg>'


def div(i, cls, style, inner="", hidden=True):
    return f'<div id="{i}" class="{cls}" style="{style}{";opacity:0" if hidden else ""}">{inner}</div>'


# ---- JS pieces
def fin(sel, t, s=None, d=None):
    o = {k: v for k, v in (("s", s), ("d", d)) if v is not None}
    return f'fin("{sel}",{t}{"," + json.dumps(o) if o else ""});'


def to(sel, props, t): return f'tl.to("{sel}",{json.dumps(props)},{t});'
def setp(sel, props, t): return f'tl.set("{sel}",{json.dumps(props)},{t});'
def draw(sel, t, d=0.4): return f'draw("{sel}",{t},{d});'
def counter(sel, a, b, t, d, pre="", suf=""): return f'counter("{sel}",{a},{b},{t},{d},{json.dumps(pre)},{json.dumps(suf)});'
def typ(sel, s, t, d): return f'typeText("{sel}",{json.dumps(s)},{t},{d});'
def sweep(sel, t): return f'sweep("{sel}",{t});'
