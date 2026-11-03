"""Shared graphic pieces for coaching clips (the default look: glass cards, pills, drawn lines, ticking figures).
Everything is drawn on the engine's 680x540 stage. Ids must be unique per stage: pass a prefix."""
import coach_engine as E

AV = '<svg viewBox="0 0 100 100" width="100%" height="100%"><rect width="100" height="100" fill="#3a3a3c"/><circle cx="50" cy="40" r="17" fill="#8e8e93"/><path d="M18 100c0-22 14-32 32-32s32 10 32 32z" fill="#8e8e93"/></svg>'
LINK = '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1.2 1.2"/><path d="M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1.2-1.2"/></svg>'
TICK = '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
CROSS = '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>'
CAL = '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="5" width="17" height="15" rx="3"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>'
MAIL = '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#fff" stroke-width="2.2" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="M3.5 7l8.5 6 8.5-6" stroke-linecap="round"/></svg>'
PLAY = '<svg viewBox="0 0 24 24" width="100%" height="100%"><path d="M8 5.5v13l11-6.5z" fill="#fff"/></svg>'

CSS = """
.lab { font: 500 26px "SFM", sans-serif; letter-spacing: -0.01em; color: var(--gy); white-space: nowrap; }
.bar { background: rgba(255,255,255,.22); border-radius: 8px; }
.fig { font-size: 84px; line-height: 1; letter-spacing: -0.045em; font-variant-numeric: tabular-nums; white-space: nowrap; }
.t38 { font-size: 38px; white-space: nowrap; } .t32 { font-size: 32px; white-space: nowrap; }
.pl-o .dot { background: var(--o); } .pl-g .dot { background: var(--g); } .pl-r .dot { background: var(--r); } .pl-w .dot { background: rgba(255,255,255,.22); }
.solid { background: rgba(14,13,12,.9); border: 1.5px solid rgba(255,255,255,.2); box-shadow: 0 16px 40px rgba(0,0,0,.5); }
.av { border-radius: 50%; overflow: hidden; }
.row { --x: 0; position: absolute; height: 76px; border-radius: 20px; box-sizing: border-box; display: flex; align-items: center; padding: 0 22px; font-size: 36px; white-space: nowrap; border: 1.5px solid rgba(255,255,255,.26); background: rgba(255,255,255,.05); }
.row::after { content: ""; position: absolute; left: 18px; right: 18px; top: 50%; height: 4px; border-radius: 2px; background: var(--r); transform-origin: 0 50%; transform: scaleX(var(--x)); }
.slot { --bad: 0; --good: 0; position: absolute; border-radius: 14px; box-sizing: border-box; border: 1.5px solid color-mix(in srgb, var(--r) calc(var(--bad) * 100%), color-mix(in srgb, var(--g) calc(var(--good) * 100%), rgba(255,255,255,.3))); background: color-mix(in srgb, var(--r) calc(var(--bad) * 55%), color-mix(in srgb, var(--g) calc(var(--good) * 70%), rgba(255,255,255,.06))); }
.tag { height: 48px; border-radius: 24px; padding: 0 20px; font-size: 26px; line-height: 48px; white-space: nowrap; }
.tg { background: var(--g); box-shadow: 0 0 26px color-mix(in srgb, var(--g) 60%, transparent); } .tr { background: var(--r); } .to { background: var(--o); box-shadow: 0 0 26px color-mix(in srgb, var(--o) 60%, transparent); }
"""


def card(i, l, t, w, h, inner="", o=0):
    return f'<div id="{i}" class="glass" style="left:{l}px;top:{t}px;width:{w}px;height:{h}px;opacity:{o}">{inner}</div>'


def pill(i, cls, icon, text, l, t, w, extra="", solid=False):
    return f'<div id="{i}" class="pill {"solid" if solid else "glass"} {cls}" style="left:{l}px;top:{t}px;width:{w}px;opacity:0"><span class="dot">{icon}</span><span>{text}</span>{extra}</div>'


def vline(i, x, y1, y2):
    return f'<svg class="ln" viewBox="0 0 680 540" width="680" height="540"><line id="{i}" x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="#fff" stroke-width="3.5" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/></svg>'


def avatars(p, n, l, t, size=64, gap=14, o=0):
    return "".join(f'<div id="{p}{k}" class="av" style="position:absolute;left:{l + k * (size + gap)}px;top:{t}px;width:{size}px;height:{size}px;opacity:{o}">{AV}</div>' for k in range(n))


def text(i, s, l, t, cls="t38", style="", o=0):
    return f'<div id="{i}" class="{cls}" style="left:{l}px;top:{t}px;opacity:{o};{style}">{s}</div>'


def on(sel, t, prop="--on", v=1, d=0.3):
    return f'tl.to("{sel}",{{"{prop}":{v},duration:{d},ease:"power2.out"}},{t});'


def show(sel, t):
    return f'tl.set("{sel}",{{opacity:1}},{t});'


def build(ratio, shots, stages, hook=None, scrim=None, side="right"):
    """stages: [(a, b, html, js, box, mode)] where box = (l, t, r, b) of the content on the 680x540 stage and mode is
    'split' / 'anim' / 'him' for 9:16 (ignored in 16:9). Placement is automatic: in 16:9 against the open side of the
    frame at the largest scale that stays clear of the speaker's head; in 9:16 centred in the top half (split) or the frame (anim)."""
    E.shots(shots)
    if hook: E.hook(*hook)
    if ratio == "16x9" and scrim: E.scrim(scrim, side=side)
    first = True
    for a, b, htm, js, box, mode in stages:
        if ratio == "16x9":
            if mode == "full":
                sc = 1.6; x = round((1920 - (box[0] + box[2]) * sc) / 2); y = round(470 - (box[1] + box[3]) * sc / 2)
            elif side == "right":
                x, sc = E.place_right(a, b, box)
                y = round(430 - (box[1] + box[3]) * sc / 2)
            else:
                x = 44 - box[0]; sc = E.fit(a, b, 44, box[2] - box[0]); x = round(44 - box[0] * sc); y = round(430 - (box[1] + box[3]) * sc / 2)
            cut = mode == "full"
        else:
            sc = 1.45; x = round((1080 - (box[0] + box[2]) * sc) / 2)
            y = round(455 - (box[1] + box[3]) * sc / 2) if mode == "split" else round(1470 - (box[1] + box[3]) * sc / 2) if mode == "him" else round(700 - (box[1] + box[3]) * sc / 2)
            cut = mode != "him"
        with E.stage(a, b, x, y, sc, cut_in=cut, cut_out=cut, box=box) as s:
            s.add(htm, CSS if first else "", js); first = False
    E.build()
