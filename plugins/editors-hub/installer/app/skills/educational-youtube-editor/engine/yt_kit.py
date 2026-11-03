"""yt_kit.py - the reusable, parameterised component library for long-form 16:9 educational edits.

Every component:  K.<name>(sid, a, b, ...) -> a piece. Hand it to a state:  E.float_/E.panel/E.split/E.full(piece, why=..., score=...).
  sid      unique id for the scene (letters, digits, dashes)
  a, b     on-screen window in seconds on the cut timeline (use E.w("word", after) for the times)
  variant  every component has several looks. Leave it "auto" and the kit picks the one used least recently in THIS
           video, so the same idea never gets the same treatment twice in a row. Name one when the content calls for it.
Pieces are designed at a fixed size and scaled by the engine to fit whichever state they are placed in.
Text marked *like this* is set in the emphasis font and the accent colour (whole words only; anything with a digit stays in the main font).
See references/component-library.md for when to use what."""
import math, re
import yt_engine as E

VARIANTS = {
    "frame": ["float", "tilt", "lift", "polaroid"], "browser": ["float", "tilt"], "collage": ["fan", "scatter", "grid", "stack"],
    "preview": ["cards", "pills", "tiles", "docs", "orbs"], "flow": ["down", "across", "loop"], "framework": ["rail", "cards", "ring"],
    "stat": ["count", "ring", "bar"], "compare": ["versus", "columns", "beforeafter"], "timeline": ["line", "steps"],
    "emph": ["swap", "stack"], "quote": ["card", "big"], "rows": ["rows", "checks", "numbered"], "section": ["number", "card", "rail"],
    "graph": ["line", "bars"], "person": ["portrait", "circle"],
}


def pick(comp, variant, t):
    """'auto' -> the variant of this component used least recently in this video."""
    if variant != "auto": return variant
    opts = [o for o in VARIANTS[comp] if E.DEPTH or o != "tilt"]; last = {}      # depth switched off at setup: "auto" never picks the 3D rest angle
    for s in E.SC:
        if s["comp"] == comp: last[s["variant"]] = s["b"]
    new = [o for o in opts if o not in last]
    return new[0] if new else min(opts, key=lambda o: last[o])


def acc(t):
    def f(m): return m.group(1) if re.search(r"\d", m.group(1)) else f'<i class="a">{m.group(1)}</i>'
    return re.sub(r"\*(.+?)\*", f, t)


def plain(t): return re.sub(r"<[^>]+>|\*", "", t)
PERSON = '<svg viewBox="0 0 24 24" width="100%" height="100%"><circle cx="12" cy="7.6" r="4.3" fill="currentColor"/><path d="M3.2,22 C4.2,15.2 19.8,15.2 20.8,22 Z" fill="currentColor"/></svg>'
CHECK = '<svg viewBox="0 0 24 24" width="38" height="38"><circle cx="12" cy="12" r="11" fill="#2FA65A"/><path d="M7 12.4l3.2 3.2L17 8.8" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CROSS = '<svg viewBox="0 0 24 24" width="38" height="38"><circle cx="12" cy="12" r="11" fill="#B3261E"/><path d="M8 8l8 8M16 8l-8 8" fill="none" stroke="#fff" stroke-width="2.3" stroke-linecap="round"/></svg>'

# ------------------------------------------------------------------ images, screenshots, people
FR_CSS = """.fr{position:absolute;border-radius:var(--r);overflow:hidden;box-shadow:var(--sh);border:1px solid rgba(255,255,255,.16);background:#111}
.fr video{display:block;width:100%;height:100%;object-fit:cover}.fr>.mw{position:absolute;inset:0;overflow:hidden}
.fr.pol{border:14px solid #F6F4EF;border-bottom-width:46px;border-radius:10px}
.tg{position:absolute;left:18px;bottom:18px;padding:10px 20px;border-radius:999px;background:rgba(10,9,8,.82);border:1px solid rgba(255,255,255,.18);font-family:"HelvB";font-size:24px;letter-spacing:-.02em;color:var(--paper)}"""


def _media(src, a, b, video, w, h, pos=None, sid=""):
    """Footage plays whole in its frame. A still goes through E.img, which finds the faces and crops around them (or shows the
    whole picture on a blurred extension when a filling crop would cut someone)."""
    if video is not None: return E.vid(src, a, b - a, video, "object-fit:cover" + (f";object-position:{pos}" if pos else ""))
    return f'<div class="mw">{E.img(src, w, h, pos, sid)}</div>'


def frame(sid, a, b, src, variant="auto", tag="", ratio=None, w=None, pos=None, video=None):
    """One real image / screenshot / clip presented as a designed object: rounded corners, soft shadow, gentle life.
    float = flat with a slow drift | tilt = arrives from depth and rests at a slight 3D angle | lift = rises in |
    polaroid = photo print (people, places, memories in a story).
    The frame takes the IMAGE'S OWN SHAPE by default, so nothing is cropped. Pass ratio only when the layout needs another
    shape: faces are then detected and the crop is placed around them, never through them."""
    v = pick("frame", variant, a); ratio = ratio or (16 / 9 if video is not None else E.ratio_of(src))
    w = w or (860 if ratio >= 1.2 else 700 if ratio >= 0.9 else 520); h = round(w / ratio); f = f"#{sid}-f"
    body = (f'<div class="p3" style="width:100%;height:100%"><div id="{sid}-f" class="fr h{" pol" if v == "polaroid" else ""}" style="left:40px;top:40px;width:{w}px;height:{h}px">'
            f'{_media(src, a, b, video, w, h, pos, sid)}{f"<span class=tg>{tag}</span>" if tag else ""}</div></div>')
    if v == "tilt":
        E.tw(f, a - E.LEAD, 0.9, {"opacity": 1, "z": 0, "rotationY": -9, "rotationX": 3, "filter": "blur(0px)"}, {"opacity": 0, "z": -600, "rotationY": -26, "rotationX": 8, "filter": "blur(10px)"})
        E.tw(f, a + 0.6, b - a - 0.9, {"rotationY": -4, "rotationX": 1.5}, None, "sine.inOut")
    elif v == "lift": E.enter(f, a, "rise"); E.tw(f, a + 0.3, b - a - 0.6, {"y": -10}, None, "sine.inOut")
    elif v == "polaroid": E.tw(f, a - E.LEAD, 0.6, {"opacity": 1, "scale": 1, "rotation": -2.5}, {"opacity": 0, "scale": 1.12, "rotation": 4}, "power3.out")
    else: E.enter(f, a, "focus")
    E.tw(f"{f} .mw, {f} video", a - E.LEAD, b - a + E.LEAD, {"scale": 1.045}, {"scale": 1}, "none")
    E.sfx(a - 0.25, "woosh")
    return E.piece(sid, a, b, body, (w + 80, h + 80), "frame", v, text=tag, css_=FR_CSS)


BR_CSS = """.br{position:absolute;border-radius:22px;overflow:hidden;box-shadow:var(--sh);border:1px solid rgba(255,255,255,.18);background:#fff}
.brb{height:58px;background:#ECEAE6;display:flex;align-items:center;gap:10px;padding:0 20px;border-bottom:1px solid #D8D5CF}
.brb b{width:14px;height:14px;border-radius:50%;background:#FF5F57}.brb b+b{background:#FEBC2E}.brb b+b+b{background:#28C840}
.brb span{margin-left:18px;flex:1;height:34px;border-radius:17px;background:#fff;display:flex;align-items:center;padding:0 18px;font-family:var(--sf);font-size:19px;color:#4a4744;max-width:620px}
.brv{position:relative;overflow:hidden;background:#fff}.brv img{display:block;width:100%}
.hlb{position:absolute;border:5px solid var(--o);border-radius:14px;box-shadow:0 0 0 6px rgba(@@ACCENT_RGB@@,.22)}"""


def browser(sid, a, b, src, url, variant="auto", scroll=0, scroll_t=None, hl=None, w=1100, vh=620):
    """A real website / page in a floating browser window. scroll = px the page scrolls (at scroll_t) to reach what is being
    talked about. hl = (x%, y%, w%, h%, t) draws an accent-colour box round the exact thing on the page at time t."""
    v = pick("browser", variant, a); f = f"#{sid}-f"
    hlh = f'<div id="{sid}-hl" class="hlb h" style="left:{hl[0]}%;top:{hl[1]}%;width:{hl[2]}%;height:{hl[3]}%"></div>' if hl else ""
    body = (f'<div class="p3" style="width:100%;height:100%"><div id="{sid}-f" class="br h" style="left:40px;top:40px;width:{w}px"><div class="brb"><b></b><b></b><b></b><span>{url}</span></div>'
            f'<div class="brv" style="height:{vh}px"><div id="{sid}-pg" style="position:relative"><img src="{src}">{hlh}</div></div></div></div>')
    if v == "tilt":
        E.tw(f, a - E.LEAD, 0.9, {"opacity": 1, "z": 0, "rotationY": 8, "rotationX": 2.5, "filter": "blur(0px)"}, {"opacity": 0, "z": -600, "rotationY": 24, "rotationX": 7, "filter": "blur(10px)"})
        E.tw(f, a + 0.6, b - a - 0.9, {"rotationY": 3, "rotationX": 1}, None, "sine.inOut")
    else: E.enter(f, a, "focus")
    if scroll: E.tw(f"#{sid}-pg", scroll_t if scroll_t is not None else a + 1.0, 1.6, {"y": -scroll}, None, "power2.inOut")
    if hl: E.enter(f"#{sid}-hl", hl[4], "settle", lead=0.15); E.sfx(hl[4], "pop", -24)
    E.sfx(a - 0.25, "woosh")
    return E.piece(sid, a, b, body, (w + 80, vh + 58 + 80), "browser", v, text="", css_=FR_CSS + BR_CSS)


def collage(sid, a, b, srcs, times=None, variant="auto", ratio=None, tags=None):
    """Several real examples at once (a channel's thumbnails, a product range, a set of posts). They arrive one by one on `times`.
    fan = overlapping spread | scatter = layered at different depths | grid = neat rows | stack = each lands on the last."""
    v = pick("collage", variant, a); n = len(srcs); times = times or [a + 0.28 * i for i in range(n)]; tags = tags or [""] * n
    ratio = ratio or sorted(E.ratio_of(x) for x in srcs)[n // 2]            # the set's typical shape; each picture is then cropped around its faces
    Wd, Hd = (1500, 640) if v in ("fan", "grid") and ratio > 1 else (1100, 760); out = ""
    cw = {"fan": min(460, 1900 / max(n, 3)), "scatter": 400, "grid": (Wd - 120) / (3 if n > 4 else 2), "stack": 640}[v]
    if ratio < 1: cw = min(cw, 300)
    cw = round(cw); ch = round(cw / ratio)
    for i, s in enumerate(srcs):
        u = (i - (n - 1) / 2) / max(1, (n - 1) / 2) if n > 1 else 0
        if v == "fan": x, y, rot, z = Wd / 2 - cw / 2 + u * (Wd - cw - 60) / 2, Hd / 2 - ch / 2 + abs(u) * 46, u * 9, -abs(u) * 60
        elif v == "scatter":
            per = 3 if n > 4 else 2 if n > 2 else n; rws = -(-n // per); r_, j = i // per, i % per; m = min(per, n - r_ * per)
            x = Wd / 2 - cw / 2 + (j - (m - 1) / 2) * cw * 0.86 + (14 if r_ % 2 else -14); y = Hd / 2 - ch / 2 + (r_ - (rws - 1) / 2) * ch * 0.92 + [10, -16, 12][j % 3]
            rot = [-4, 3, -2, 5, -3, 2][i % 6]; z = [-120, 40, -40, 60, -160, 0][i % 6]
        elif v == "grid":
            cols = 3 if n > 4 else 2; rws = -(-n // cols); gx = (Wd - cols * cw) / (cols + 1); gy = (Hd - rws * ch) / (rws + 1)
            x, y, rot, z = gx + (i % cols) * (cw + gx), gy + (i // cols) * (ch + gy), 0, 0
        else: x, y, rot, z = Wd / 2 - cw / 2 + (i - (n - 1) / 2) * 34, Hd / 2 - ch / 2 + (i - (n - 1) / 2) * 26, (i - (n - 1) / 2) * 2.2, 0
        tg = f'<span class="tg">{tags[i]}</span>' if tags[i] else ""
        out += f'<div id="{sid}-c{i}" class="fr h" style="left:{x:.0f}px;top:{y:.0f}px;width:{cw}px;height:{ch}px;z-index:{i + 1}"><div class="mw">{E.img(s, cw, ch, None, sid)}</div>{tg}</div>'
        E.tw(f"#{sid}-c{i}", times[i] - E.LEAD, 0.7, {"opacity": 1, "z": z, "rotation": rot, "scale": 1, "filter": "blur(0px)"}, {"opacity": 0, "z": z - 500, "rotation": rot * 2.2, "scale": 1.1, "filter": "blur(12px)"})
        if i < 5: E.sfx(times[i] - 0.2, "swish" if i else "woosh", -24)
    return E.piece(sid, a, b, f'<div class="p3" style="width:100%;height:100%">{out}</div>', (Wd, Hd), "collage", v, text=" ".join(tags), css_=FR_CSS)


def person(sid, a, b, src, name, role="", variant="auto", ratio=None, video=None):
    """A named person: their real photo or clip, WHOLE (card matches the picture's shape), with their name on it."""
    v = pick("person", variant, a); ratio = ratio or (9 / 16 if video is not None else E.ratio_of(src, 0.56, 1.8)); w = 560 if ratio < 1.2 else 760; h = round(w / ratio) if v == "portrait" else w
    E.css(FR_CSS + """.pn{position:absolute;left:0;right:0;text-align:center;font-family:"HelvB";font-size:40px;letter-spacing:-.035em}.pn span{display:block;font-family:"HelvR";font-size:25px;color:var(--grey);letter-spacing:-.01em;margin-top:6px}""")
    rad = "border-radius:50%;" if v == "circle" else ""
    body = (f'<div id="{sid}-f" class="fr h" style="left:60px;top:20px;width:{w}px;height:{h}px;{rad}">{_media(src, a, b, video, w, h, None, sid)}</div>'
            f'<div id="{sid}-n" class="pn h" style="top:{h + 44}px">{name}<span>{role}</span></div>')
    E.enter(f"#{sid}-f", a, "focus"); E.enter(f"#{sid}-n", a + 0.25, "rise"); E.sfx(a - 0.25, "woosh")
    return E.piece(sid, a, b, body, (w + 120, h + 150), "person", v, text=name)


SOC_CSS = """.so{position:absolute;inset:30px;border-radius:26px;background:#fff;color:#0F1419;box-shadow:var(--sh);padding:34px 38px;font-family:var(--sf)}
.soh{display:flex;align-items:center;gap:18px}.soh img,.soh .av{width:76px;height:76px;border-radius:50%;object-fit:cover;background:#CFD9DE;color:#8B98A5;overflow:hidden;flex:none}
.soh b{display:block;font-size:30px;font-weight:700;letter-spacing:-.02em}.soh span{display:block;font-size:25px;color:#536471}
.sot{font-size:36px;line-height:1.28;letter-spacing:-.015em;margin-top:22px}.som{margin-top:22px;border-radius:18px;overflow:hidden;border:1px solid #CFD9DE}.som img{display:block;width:100%}
.sos{margin-top:20px;font-size:23px;color:#536471}
.yv{position:absolute;inset:30px;font-family:var(--sf);color:#F1F1F1}.yv .th{border-radius:20px;overflow:hidden;box-shadow:var(--sh);border:1px solid rgba(255,255,255,.14)}
.yv b{display:block;font-size:34px;font-weight:600;line-height:1.2;letter-spacing:-.02em;margin-top:22px}.yv span{display:block;font-size:25px;color:#AAA;margin-top:8px}"""


def social(sid, a, b, name, handle, text, avatar=None, media=None, stats="", w=820):
    """A real post, quoted exactly, as the post itself (not a text card). Use the real avatar and real wording."""
    av = f'<img src="{avatar}">' if avatar else f'<div class="av">{PERSON}</div>'
    hh = 250 + 46 * (len(text) // 38 + 1) + (round((w - 76) * 9 / 16) + 22 if media else 0) + (44 if stats else 0)
    body = (f'<div id="{sid}-f" class="so h"><div class="soh">{av}<div><b>{name}</b><span>{handle}</span></div></div><div class="sot">{text}</div>'
            f'{f"<div class=som><img src={chr(34)}{media}{chr(34)}></div>" if media else ""}{f"<div class=sos>{stats}</div>" if stats else ""}</div>')
    E.enter(f"#{sid}-f", a, "focus"); E.sfx(a - 0.25, "woosh")
    return E.piece(sid, a, b, body, (w + 60, hh), "social", "post", text=text, css_=SOC_CSS)


def ytvideo(sid, a, b, thumb, title, channel="", meta="", w=820):
    """A real YouTube video: its real thumbnail, title and channel (when YouTube is named, show YouTube)."""
    body = f'<div id="{sid}-f" class="yv h"><div class="th" style="position:relative;aspect-ratio:16/9;overflow:hidden">{E.img(thumb, w, round(w * 9 / 16), None, sid)}</div><b>{title}</b><span>{channel}{" · " if channel and meta else ""}{meta}</span></div>'
    E.enter(f"#{sid}-f", a, "focus"); E.tw(f"#{sid}-f .th img", a, b - a, {"scale": 1.04}, {"scale": 1}, "none"); E.sfx(a - 0.25, "woosh")
    return E.piece(sid, a, b, body, (w + 60, round(w * 9 / 16) + 210), "ytvideo", "card", text=title, css_=SOC_CSS)


# ------------------------------------------------------------------ "what you'll learn": show the structure, keep the curiosity
PV_CSS = """.pv{position:absolute;left:50%;top:50%;display:flex;flex-direction:column;align-items:flex-start;justify-content:space-between;padding:22px 24px;color:var(--paper)}
.pv .n{font-family:"HelvB";font-size:64px;letter-spacing:-.05em;line-height:1}.pv .t{font-family:"HelvB";font-size:34px;letter-spacing:-.03em;line-height:1.08}
.pv .bl{width:100%;display:flex;flex-direction:column;gap:10px;filter:blur(5px);opacity:.75}.pv .bl u{display:block;height:13px;border-radius:7px;background:rgba(242,240,236,.5)}.pv .bl u+u{width:64%}
.pv.pill{flex-direction:row;align-items:center;justify-content:flex-start;gap:22px;border-radius:999px;padding:0 34px}.pv.pill .n{font-size:44px}.pv.pill .bl{flex-direction:row;width:300px}
.pv.doc{background:#F6F4EF;color:#14110f;border-radius:14px;box-shadow:var(--sh)}.pv.doc .bl u{background:rgba(20,17,15,.45)}
.pv.orb{border-radius:50%;align-items:center;justify-content:center;padding:0}.pv.on{border-color:var(--o);box-shadow:0 0 0 3px var(--o),var(--sh)}"""


def preview(sid, a, b, n, variant="auto", labels=None, reveal=1, t_split=None, t_reveal=None):
    """The speaker says "there are N things": ONE object appears, duplicates, and the copies separate through depth into N.
    Only the first `reveal` show their label; the rest stay blurred so the structure is clear and the answer is not.
    cards = 3D arc of glass cards | pills = stack | tiles = row at alternating depths | docs = pages fanning out | orbs = ring.
    labels are optional even for revealed ones (pass None to show numbers only)."""
    v = pick("preview", variant, a); t_split = t_split if t_split is not None else a + 0.9; t_reveal = t_reveal if t_reveal is not None else t_split + 1.1
    labels = labels or []; Wd, Hd = (1500, 620) if v in ("cards", "tiles", "docs") else (1100, 760); out = ""
    dim = {"cards": (260, 360), "pills": (640, 100), "tiles": (230, 230), "docs": (250, 340), "orbs": (190, 190)}[v]; cw, ch = dim
    cls = {"cards": "glass", "pills": "glass pill", "tiles": "glass", "docs": "doc", "orbs": "glass orb"}[v]
    for i in range(n):
        u = (i - (n - 1) / 2); un = u / max(1, (n - 1) / 2) if n > 1 else 0
        if v == "cards": pos = {"x": u * min(290, 1260 / n), "y": abs(un) * 26, "z": -abs(un) * 200, "rotationY": -un * 22}
        elif v == "pills": pos = {"x": 0, "y": u * min(122, 700 / n), "z": 0}
        elif v == "tiles": pos = {"x": u * min(270, 1280 / n), "y": (-30 if i % 2 else 30), "z": (-160 if i % 2 else 60), "rotationX": 8}
        elif v == "docs": pos = {"x": u * min(260, 1240 / n), "y": abs(un) * 40, "rotation": un * 11, "z": -abs(un) * 80}
        else:
            ang = -math.pi / 2 + i * 2 * math.pi / n; pos = {"x": 400 * math.cos(ang), "y": 270 * math.sin(ang), "z": 120 * math.sin(ang)}
        shown = i < reveal and i < len(labels) and labels[i]
        inner = f'<div class="n">{i + 1}</div>' + (f'<div class="t">{labels[i]}</div>' if shown else ('' if v == "orbs" else '<div class="bl"><u></u><u></u></div>'))
        out += f'<div id="{sid}-p{i}" class="pv {cls} h" style="width:{cw}px;height:{ch}px;margin:{-ch / 2}px 0 0 {-cw / 2}px;z-index:{n - i}">{inner}</div>'
        if i == 0: E.enter(f"#{sid}-p0", a, "focus")
        else: E.setp(f"#{sid}-p{i}", t_split - 0.02, {"opacity": 1, "scale": 0.97})
        E.tw(f"#{sid}-p{i}", t_split + 0.06 * i, 0.95, dict(pos, scale=1), None, "power3.inOut")
        if i < reveal: E.setp(f"#{sid}-p{i}", t_reveal + 0.5 * i, {"className": f"pv {cls} on"})
    E.sfx(a - 0.25, "woosh"); E.sfx(t_split, "swoosh", -22); E.sfx(t_reveal, "shine", -24)
    return E.piece(sid, a, b, f'<div class="p3" style="width:100%;height:100%">{out}</div>', (Wd, Hd), "preview", v, text=" ".join(x for x in labels[:reveal] if x), css_=PV_CSS)


# ------------------------------------------------------------------ relationships: flows, frameworks, timelines
FL_CSS = """.nd{position:absolute;display:flex;align-items:center;justify-content:center;gap:16px;border-radius:999px;background:rgba(18,15,13,.92);border:2px solid rgba(242,240,236,.2);font-family:"HelvB";font-size:38px;letter-spacing:-.035em;color:var(--paper);box-shadow:0 18px 44px rgba(0,0,0,.45)}
.nd.cardv{border-radius:var(--r);flex-direction:column;gap:12px;font-size:30px;text-align:center;padding:0 16px}
.fsv{position:absolute;inset:0;overflow:visible}.fsv path,.fsv line{fill:none;stroke:var(--o);stroke-width:5;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1000;stroke-dashoffset:1000}"""
_ON = {"borderColor": "@@ACCENT@@", "backgroundColor": "rgba(@@ACCENT_RGB@@,.2)", "scale": 1.06}
_OFF = {"borderColor": "rgba(242,240,236,.2)", "backgroundColor": "rgba(18,15,13,.92)", "scale": 1}


def flow(sid, a, b, steps, times, variant="auto"):
    """A chain where each thing BECOMES the next (attention -> trust -> demand -> sales). Each node arrives on its word,
    the connector draws to it, and the live node is lit while the earlier ones settle back. down | across | loop."""
    v = pick("flow", variant, a); n = len(steps); out = ""; sv = ""
    if v == "down": Wd, Hd, nw, nh = 620, n * 104 + (n - 1) * 64, 520, 104; P = [(50, i * (nh + 64)) for i in range(n)]
    elif v == "across": nw, nh = 300, 110; Wd, Hd = n * nw + (n - 1) * 90, 200; P = [(i * (nw + 90), 45) for i in range(n)]
    else:
        nw, nh, R = 280, 96, 300; Wd, Hd = 2 * R + nw, 2 * R + nh + 20
        P = [(R + R * math.cos(-math.pi / 2 + i * 2 * math.pi / n), R + 10 + R * math.sin(-math.pi / 2 + i * 2 * math.pi / n)) for i in range(n)]
    for i, s in enumerate(steps):
        x, y = P[i]; out += f'<div id="{sid}-n{i}" class="nd h" style="left:{x:.0f}px;top:{y:.0f}px;width:{nw}px;height:{nh}px">{acc(s)}</div>'
        E.enter(f"#{sid}-n{i}", times[i], "focus"); E.tw(f"#{sid}-n{i}", times[i], 0.35, _ON, None, "power2.out")
        if i + 1 < n: E.tw(f"#{sid}-n{i}", times[i + 1] - 0.1, 0.4, _OFF, None, "power2.inOut")
        j = (i + 1) % n
        if i + 1 < n or v == "loop":
            x2, y2 = P[j]; cx, cy, cx2, cy2 = x + nw / 2, y + nh / 2, x2 + nw / 2, y2 + nh / 2
            if v == "down": d = f"M{cx} {y + nh + 8} L{cx} {y2 - 12} M{cx - 12} {y2 - 26} L{cx} {y2 - 12} L{cx + 12} {y2 - 26}"
            elif v == "across": d = f"M{x + nw + 10} {cy} L{x2 - 14} {cy} M{x2 - 28} {cy - 12} L{x2 - 14} {cy} L{x2 - 28} {cy + 12}"
            else:
                dx, dy = cx2 - cx, cy2 - cy; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; m = 0.34
                d = f"M{cx + ux * L * m:.0f} {cy + uy * L * m:.0f} L{cx2 - ux * L * m:.0f} {cy2 - uy * L * m:.0f}"
            sv += f'<path id="{sid}-a{i}" pathLength="1000" d="{d}"/>'
            ta = times[i + 1] if i + 1 < n else times[-1] + 0.8
            E.tw(f"#{sid}-a{i}", ta - 0.55, 0.5, {"strokeDashoffset": 0}, None, "power2.inOut")
        if i: E.sfx(times[i] - 0.1, "pop", -25)
    E.sfx(a - 0.2, "woosh")
    return E.piece(sid, a, b, f'<svg class="fsv" viewBox="0 0 {Wd} {Hd}">{sv}</svg>{out}', (Wd, Hd), "flow", v, text=" ".join(plain(s) for s in steps), css_=FL_CSS)


FW_CSS = """.fwl{position:absolute;height:5px;border-radius:3px;background:rgba(242,240,236,.18)}.fwl b{display:block;height:100%;border-radius:3px;background:var(--o);transform-origin:0 50%;transform:scaleX(0)}
.fwn{position:absolute;display:flex;flex-direction:column;align-items:center;gap:16px;width:220px;margin-left:-110px}
.fwn i{font-style:normal;width:100px;height:100px;border-radius:50%;background:#1b1714;border:2px solid rgba(242,240,236,.26);display:flex;align-items:center;justify-content:center;font-family:"HelvB";font-size:44px;color:var(--paper)}
.fwn span{font-family:"HelvB";font-size:34px;letter-spacing:-.03em;text-align:center;line-height:1.1;color:var(--paper)}
.fwc{position:absolute;border-radius:var(--r);padding:22px;display:flex;flex-direction:column;justify-content:space-between;font-family:"HelvB";color:var(--paper)}.fwc i{font-style:normal;font-size:44px;letter-spacing:-.05em}.fwc span{font-size:27px;letter-spacing:-.03em;line-height:1.1}
.trk{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:12px;font-family:"HelvB"}
.trk i{font-style:normal;width:46px;height:46px;border-radius:50%;background:rgba(10,9,8,.78);border:1.5px solid rgba(242,240,236,.24);display:flex;align-items:center;justify-content:center;font-size:21px;color:var(--grey)}
.trk i.on{background:var(--o);border-color:var(--o);color:@@ON_ACCENT@@}.trk span{margin-left:10px;padding:10px 22px;border-radius:999px;background:rgba(10,9,8,.78);border:1.5px solid rgba(242,240,236,.2);font-size:25px;letter-spacing:-.02em;color:var(--paper)}"""


def framework(sid, a, b, steps, active=None, times=None, variant="rail"):
    """THE map of a framework. Choose ONE variant per framework and reuse it every time the video returns to it
    (same sid prefix helps), with `active` = the stage being discussed (0-based) so the viewer knows where they are.
    First showing: pass `times` so the stages build one at a time. Later showings: no times, all present, one lit."""
    v = variant if variant != "auto" else "rail"; n = len(steps); out = ""
    Wd, Hd = max(900, n * 250), 330 if v != "ring" else 760
    for i, s in enumerate(steps):
        on = active == i; t = times[i] if times else a + 0.07 * i
        if v == "rail":
            x = 125 + i * (Wd - 250) / max(1, n - 1); out += f'<div id="{sid}-s{i}" class="fwn h" style="left:{x:.0f}px;top:70px"><i>{i + 1}</i><span>{acc(s)}</span></div>'
        elif v == "cards":
            cwd = (Wd - 40 - (n - 1) * 20) / n; out += f'<div id="{sid}-s{i}" class="fwc glass h" style="left:{20 + i * (cwd + 20):.0f}px;top:50px;width:{cwd:.0f}px;height:230px"><i>{i + 1}</i><span>{acc(s)}</span></div>'
        else:
            ang = -math.pi / 2 + i * 2 * math.pi / n; out += f'<div id="{sid}-s{i}" class="fwn h" style="left:{Wd / 2 + 270 * math.cos(ang):.0f}px;top:{Hd / 2 - 70 + 270 * math.sin(ang):.0f}px"><i>{i + 1}</i><span>{acc(s)}</span></div>'
        E.enter(f"#{sid}-s{i}", t, "focus" if times else "fade", lead=E.LEAD if times else 0)
        tgt = f"#{sid}-s{i} i" if v != "cards" else f"#{sid}-s{i}"
        if on:
            t_on = (times[-1] + 0.5) if times else a + 0.5
            E.tw(tgt, t_on, 0.45, {"backgroundColor": "@@ACCENT@@", "borderColor": "@@ACCENT@@", "color": "@@ON_ACCENT@@", "scale": 1.14}, None, "power2.out"); E.sfx(t_on, "shine", -25)
        elif active is not None: E.tw(f"#{sid}-s{i}", (times[-1] + 0.5) if times else a + 0.5, 0.4, {"opacity": 0.42}, None, "power2.out")
    line = ""
    if v == "rail":
        line = f'<div class="fwl" style="left:125px;top:118px;width:{Wd - 250}px"><b id="{sid}-ln"></b></div>'
        frac = 1 if active is None else active / max(1, n - 1)
        E.tw(f"#{sid}-ln", a + 0.1, (times[-1] - a + 0.3) if times else 0.9, {"scaleX": frac}, None, "power2.inOut")
    E.sfx(a - 0.2, "woosh")
    return E.piece(sid, a, b, line + out, (Wd, Hd), "framework", v, text=" ".join(plain(s) for s in steps), css_=FW_CSS)


def tracker(sid, a, b, steps, active):
    """The small 1 2 [3] 4 5 marker for the top of the frame while a stage is talked through: E.float_(K.tracker(...), zone="top")."""
    dots = "".join(f'<i class="{"on" if i == active else ""}">{i + 1}</i>' for i in range(len(steps)))
    body = f'<div id="{sid}-t" class="trk h">{dots}<span>{plain(steps[active])}</span></div>'
    E.enter(f"#{sid}-t", a, "rise", lead=0); E.leave(f"#{sid}-t", b)
    return E.piece(sid, a, b, body, (len(steps) * 58 + 420, 80), "tracker", "chips", text=plain(steps[active]), css_=FW_CSS)


def timeline(sid, a, b, items, times, variant="auto"):
    """Dates / stages in order. items = [(label, sub)]. line = a rail drawn left to right with dots | steps = vertical ladder."""
    v = pick("timeline", variant, a); n = len(items); out = ""
    E.css(FW_CSS + """.tli{position:absolute;width:260px;margin-left:-130px;text-align:center}.tli b{display:block;font-family:"HelvB";font-size:40px;letter-spacing:-.04em;color:var(--paper)}.tli span{display:block;font-size:24px;color:var(--grey);margin-top:8px;line-height:1.2}
.tld{position:absolute;width:26px;height:26px;margin:-13px 0 0 -13px;border-radius:50%;background:var(--o);box-shadow:0 0 0 8px rgba(@@ACCENT_RGB@@,.2)}.tls{position:absolute;left:60px;text-align:left}.tls b{font-family:"HelvB";font-size:38px;letter-spacing:-.04em;display:block}.tls span{font-size:24px;color:var(--grey)}""")
    if v == "line":
        Wd, Hd = max(1000, n * 290), 340; out = f'<div class="fwl" style="left:100px;top:90px;width:{Wd - 200}px"><b id="{sid}-ln"></b></div>'
        for i, (lab, sub) in enumerate(items):
            x = 100 + i * (Wd - 200) / max(1, n - 1)
            out += f'<div id="{sid}-d{i}" class="tld h" style="left:{x:.0f}px;top:92px"></div><div id="{sid}-i{i}" class="tli h" style="left:{x:.0f}px;top:140px"><b>{lab}</b><span>{sub}</span></div>'
            E.tw(f"#{sid}-ln", times[i] - 0.5, 0.5, {"scaleX": i / max(1, n - 1)}, None, "power2.inOut")
            E.enter(f"#{sid}-d{i}", times[i], "settle", lead=0.1); E.enter(f"#{sid}-i{i}", times[i], "rise", lead=0.1); E.sfx(times[i], "pop", -25)
    else:
        Wd, Hd = 700, n * 130 + 20; out = f'<div class="fwl" style="left:28px;top:30px;width:5px;height:{Hd - 60}px;background:rgba(242,240,236,.18)"></div>'
        for i, (lab, sub) in enumerate(items):
            out += f'<div id="{sid}-d{i}" class="tld h" style="left:30px;top:{40 + i * 130}px"></div><div id="{sid}-i{i}" class="tls h" style="top:{14 + i * 130}px;left:80px"><b>{lab}</b><span>{sub}</span></div>'
            E.enter(f"#{sid}-d{i}", times[i], "settle", lead=0.1); E.enter(f"#{sid}-i{i}", times[i], "left", lead=0.1); E.sfx(times[i], "pop", -25)
    return E.piece(sid, a, b, out, (Wd, Hd), "timeline", v, text=" ".join(l for l, _ in items))


# ------------------------------------------------------------------ numbers, graphs, comparisons
ST_CSS = """.stn{font-family:"HelvB";font-size:210px;letter-spacing:-.06em;line-height:.9;color:var(--paper);font-variant-numeric:tabular-nums;text-align:center}
.stl{font-family:"HelvR";font-size:34px;color:var(--grey);letter-spacing:-.01em;text-align:center;margin-top:18px}
.stw{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
.stb{width:100%;height:30px;border-radius:15px;background:rgba(242,240,236,.12);overflow:hidden;margin-top:30px}.stb b{display:block;height:100%;border-radius:15px;transform-origin:0 50%;transform:scaleX(0)}"""
TONE = {"o": "@@ACCENT@@", "good": "#2FA65A", "bad": "#B3261E", "paper": "@@PAPER@@"}


def stat(sid, a, b, value, label, t=None, frm=0, pre="", suf="", dec=0, variant="auto", tone="o", pct=None):
    """A number that matters. Counts up as a plain number on the word, then takes the tone colour (good = green, bad = red,
    o = the neutral focal accent colour). count = the number alone | ring = inside a progress ring (needs pct) | bar = with a filling bar (needs pct)."""
    v = pick("stat", variant, a) if pct is not None else "count"; t = t if t is not None else a + 0.3; col = TONE[tone]
    num = f'<div id="{sid}-n" class="stn">{pre}{frm:,.{dec}f}{suf}</div>'
    if v == "ring":
        body = (f'<div class="stw h" id="{sid}-w"><svg width="520" height="520" viewBox="0 0 520 520" style="position:absolute"><circle cx="260" cy="260" r="230" fill="none" stroke="rgba(242,240,236,.12)" stroke-width="22"/>'
                f'<circle id="{sid}-r" cx="260" cy="260" r="230" fill="none" stroke="{col}" stroke-width="22" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000" transform="rotate(-90 260 260)"/></svg>'
                f'<div style="position:relative">{num.replace("stn", "stn ring")}<div class="stl" style="max-width:340px">{label}</div></div></div>')
        E.css(".stn.ring{font-size:120px}"); E.tw(f"#{sid}-r", t, 1.3, {"strokeDashoffset": 1000 - 10 * pct}, None, "power2.out"); size = (640, 600)
    elif v == "bar":
        body = f'<div class="stw h" id="{sid}-w">{num}<div class="stl">{label}</div><div class="stb"><b id="{sid}-b" style="background:{col}"></b></div></div>'
        E.tw(f"#{sid}-b", t, 1.3, {"scaleX": pct / 100}, None, "power2.out"); size = (820, 520)
    else: body = f'<div class="stw h" id="{sid}-w">{num}<div class="stl">{label}</div></div>'; size = (900, 420)
    E.enter(f"#{sid}-w", a, "focus"); E.count(f"#{sid}-n", t, frm, value, 1.25, pre, suf, dec); E.tw(f"#{sid}-n", t + 1.15, 0.3, {"color": col}, None, "power2.out")
    E.sfx(a - 0.2, "woosh"); E.sfx(t, "data", -26)
    return E.piece(sid, a, b, body, size, "stat", v, text=label, css_=ST_CSS)


def graph(sid, a, b, pts, t=None, dur=1.8, label="", variant="auto", tone="o", xlabels=None):
    """A trend. pts = values in order. line draws on and ends on a dot | bars grow one by one. Use the real figures when they are given."""
    v = pick("graph", variant, a); t = t if t is not None else a + 0.3; col = TONE[tone]; Wd, Hd = 1000, 560; lo, hi = min(pts), max(pts); n = len(pts)
    X = lambda i: 60 + i * (Wd - 120) / max(1, n - 1); Y = lambda p: Hd - 110 - (p - lo) / max(1e-9, hi - lo) * (Hd - 220)
    E.css(""".gl{position:absolute;left:60px;top:0;font-family:"HelvB";font-size:40px;letter-spacing:-.035em;color:var(--paper)}.gx{position:absolute;bottom:26px;width:160px;margin-left:-80px;text-align:center;font-size:23px;color:var(--grey)}
.gb{position:absolute;bottom:90px;border-radius:12px 12px 4px 4px;transform-origin:50% 100%;transform:scaleY(0)}""")
    xl = "".join(f'<div class="gx" style="left:{X(i):.0f}px">{x}</div>' for i, x in enumerate(xlabels or []))
    if v == "line":
        d = f"M{X(0):.0f} {Y(pts[0]):.0f}" + "".join(f" C{(X(i - 1) + X(i)) / 2:.0f} {Y(pts[i - 1]):.0f} {(X(i - 1) + X(i)) / 2:.0f} {Y(pts[i]):.0f} {X(i):.0f} {Y(pts[i]):.0f}" for i in range(1, n))
        body = (f'<div id="{sid}-w" class="h" style="position:absolute;inset:0"><div class="gl">{label}</div><svg viewBox="0 0 {Wd} {Hd}" style="position:absolute;inset:0;overflow:visible"><line x1="60" y1="{Hd - 90}" x2="{Wd - 60}" y2="{Hd - 90}" stroke="rgba(242,240,236,.18)" stroke-width="3"/>'
                f'<path id="{sid}-p" d="{d}" fill="none" stroke="{col}" stroke-width="8" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/>'
                f'<circle id="{sid}-e" class="h" cx="{X(n - 1):.0f}" cy="{Y(pts[-1]):.0f}" r="15" fill="{col}"/></svg>{xl}</div>')
        E.tw(f"#{sid}-p", t, dur, {"strokeDashoffset": 0}, None, "power2.inOut"); E.setp(f"#{sid}-e", t + dur - 0.05, {"opacity": 1})
    else:
        bw = min(120, (Wd - 160) / n * 0.62); bars = ""
        for i, p in enumerate(pts):
            bars += f'<div id="{sid}-b{i}" class="gb" style="left:{X(i) - bw / 2:.0f}px;width:{bw:.0f}px;height:{40 + (p - lo) / max(1e-9, hi - lo) * (Hd - 260):.0f}px;background:{col if i == n - 1 else "rgba(242,240,236,.28)"}"></div>'
            E.tw(f"#{sid}-b{i}", t + i * dur / n, 0.6, {"scaleY": 1}, None, "power3.out")
        body = f'<div id="{sid}-w" class="h" style="position:absolute;inset:0"><div class="gl">{label}</div>{bars}{xl}</div>'
    E.enter(f"#{sid}-w", a, "focus"); E.sfx(a - 0.2, "woosh"); E.sfx(t, "data", -27)
    return E.piece(sid, a, b, body, (Wd, Hd), "graph", v, text=label)


CP_CSS = """.cp{position:absolute;top:20px;bottom:20px;border-radius:var(--r);padding:34px;display:flex;flex-direction:column;gap:20px;background:#14110f;border:2px solid var(--line);box-shadow:var(--sh);overflow:hidden}
.cp h4{margin:0 0 6px;font-family:"HelvB";font-size:50px;letter-spacing:-.04em;color:var(--paper);font-weight:700}.cp .li{display:flex;align-items:center;gap:16px;font-size:34px;letter-spacing:-.015em;color:var(--paper);line-height:1.15}
.cp .li svg{flex:none}"""


def compare(sid, a, b, left, right, tA=None, tB=None, variant="auto", win=None, t_win=None):
    """Two things against each other. left / right = (title, [points]) or, for beforeafter, (title, image path).
    versus = two cards, the second answers the first | columns = crosses on the left, ticks on the right |
    beforeafter = two real screenshots side by side (no arrow between them).
    win = "left" | "right": that side turns green and the other dims and goes red at t_win (positive = green, negative = red)."""
    v = variant if variant != "auto" else ("beforeafter" if isinstance(left[1], str) else pick("compare", "auto", a))
    if v == "beforeafter" and not isinstance(left[1], str): v = "versus"
    tA = tA if tA is not None else a + 0.1; tB = tB if tB is not None else a + 1.2; out = ""
    Wd, Hd = 1320, (660 if isinstance(left[1], str) else 190 + 66 * max(len(left[1]), len(right[1])))
    for k, (side, tt) in enumerate(((left, tA), (right, tB))):
        title, cont = side
        if isinstance(cont, str): inner = f'<div style="position:relative;flex:1;min-height:0;border-radius:var(--rs);overflow:hidden">{E.img(cont, Wd / 2 - 108, Hd - 190, None, sid)}</div>'
        else: inner = "".join(f'<div class="li">{(CROSS if k == 0 else CHECK) if v == "columns" else ""}<span>{acc(p)}</span></div>' for p in cont)
        out += f'<div id="{sid}-c{k}" class="cp h" style="left:{20 + k * (Wd / 2):.0f}px;width:{Wd / 2 - 40:.0f}px"><h4>{acc(title)}</h4>{inner}</div>'
        E.enter(f"#{sid}-c{k}", tt, "left" if k == 0 else "right")
    if win:
        tw_ = t_win if t_win is not None else tB + 1.0; wi = 0 if win == "left" else 1
        E.tw(f"#{sid}-c{wi}", tw_, 0.4, {"borderColor": "#2FA65A", "scale": 1.03}, None, "power2.out")
        E.tw(f"#{sid}-c{1 - wi}", tw_, 0.4, {"borderColor": "#B3261E", "opacity": 0.5, "scale": 0.97}, None, "power2.out"); E.sfx(tw_, "accept", -24)
    E.sfx(tA - 0.2, "woosh"); E.sfx(tB - 0.2, "swish", -24)
    txt = " ".join([left[0], right[0]] + ([] if isinstance(left[1], str) else list(left[1]) + list(right[1])))
    return E.piece(sid, a, b, out, (Wd, Hd), "compare", v, text=plain(txt), css_=CP_CSS)


# ------------------------------------------------------------------ words: emphasis, quotes, lists, titles, sections
EM_CSS = """.em{position:absolute;left:0;right:0;text-align:center;font-family:"HelvB";font-size:190px;letter-spacing:-.06em;line-height:1;color:var(--paper);text-transform:uppercase}
.em i.a{text-transform:none;font-size:1.06em}.em.st{position:relative;font-size:120px;line-height:1.02}
.em s{text-decoration:none;position:relative}.em s::after{content:"";position:absolute;left:-3%;top:52%;width:106%;height:12px;border-radius:6px;background:var(--bad);transform:scaleX(var(--sx,0));transform-origin:0 50%}"""


def emph(sid, a, b, words, times, variant="auto"):
    """The few words that carry the point, never the sentence (the sentence is already being said).
    swap = one word, struck out and replaced by the next (VIEWS -> TRUST) | stack = two or three words stacking up."""
    v = pick("emph", variant, a); out = ""; Wd, Hd = 1300, 420 if v == "swap" else 140 * len(words) + 40
    for i, wd in enumerate(words):
        last = i == len(words) - 1
        if v == "swap":
            out += f'<div id="{sid}-w{i}" class="em h" style="top:{Hd / 2 - 100:.0f}px">{acc(wd) if last else f"<s id={sid}-s{i}>{plain(wd)}</s>"}</div>'
            E.enter(f"#{sid}-w{i}", times[i], "focus")
            if not last:
                E.tw(f"#{sid}-s{i}", times[i + 1] - 0.75, 0.4, {"--sx": 1}, None, "power3.inOut")
                E.tw(f"#{sid}-w{i}", times[i + 1] - 0.35, 0.35, {"opacity": 0, "y": -60, "filter": "blur(14px)"}, None, "power2.in")
        else:
            out += f'<div id="{sid}-w{i}" class="em st h">{acc(wd)}</div>'; E.enter(f"#{sid}-w{i}", times[i], "rise")
        E.sfx(times[i] - 0.15, "dtext" if i else "woosh", -24)
    if v == "stack": out = f'<div style="position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center">{out}</div>'
    return E.piece(sid, a, b, out, (Wd, Hd), "emph", v, text=" ".join(plain(x) for x in words), css_=EM_CSS)


def quote(sid, a, b, text, who="", src=None, variant="auto"):
    """Someone's exact words (a study's finding, a customer, a named person). Keep it to the line that matters."""
    v = pick("quote", variant, a)
    E.css(""".qc{position:absolute;inset:30px;border-radius:var(--r);padding:54px 60px;display:flex;flex-direction:column;justify-content:center;gap:34px}
.qc p{margin:0;font-family:"HelvB";font-size:52px;line-height:1.14;letter-spacing:-.04em;color:var(--paper)}.qc.big{background:none;border:none;box-shadow:none;backdrop-filter:none;text-align:center;align-items:center}.qc.big p{font-size:66px}
.qw{display:flex;align-items:center;gap:18px;font-family:"HelvB";font-size:28px;color:var(--grey);letter-spacing:-.02em}.qw img{width:68px;height:68px;border-radius:50%;object-fit:cover}""")
    body = f'<div id="{sid}-q" class="qc {"glass" if v == "card" else "big"} h"><p>{acc(text)}</p>' + (f'<div class="qw">{f"<img src={chr(34)}{src}{chr(34)}>" if src else ""}{who}</div>' if who else "") + "</div>"
    E.enter(f"#{sid}-q", a, "focus"); E.sfx(a - 0.2, "woosh")
    return E.piece(sid, a, b, body, (1160, 240 + 66 * (len(plain(text)) // 30 + 1)), "quote", v, text=plain(text))


def rows(sid, a, b, items, times, variant="auto"):
    """A list that is walked through, one row landing per item as it is reached. items = [title] or [(title, sub)].
    rows = plain cards | checks = green ticks | numbered. Titles only: two to five words each."""
    v = pick("rows", variant, a); out = ""; n = len(items)
    E.css(""".rw{display:flex;align-items:center;gap:22px;width:100%;padding:26px 30px;border-radius:22px;background:rgba(242,240,236,.05);border:1px solid var(--line)}
.rw b{display:block;font-family:"HelvB";font-size:40px;letter-spacing:-.035em;color:var(--paper)}.rw span{display:block;font-size:25px;color:var(--grey);margin-top:6px}.rw em{font-style:normal;font-family:"HelvB";font-size:34px;color:var(--o);width:44px;flex:none}""")
    for i, it in enumerate(items):
        title, sub = (it, "") if isinstance(it, str) else it
        lead = CHECK if v == "checks" else (f"<em>{i + 1}</em>" if v == "numbered" else "")
        out += f'<div id="{sid}-r{i}" class="rw h">{lead}<div><b>{acc(title)}</b>{f"<span>{sub}</span>" if sub else ""}</div></div>'
        E.enter(f"#{sid}-r{i}", times[i], "rise"); E.sfx(times[i] - 0.1, "pop" if i else "woosh", -25)
    body = f'<div style="position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;gap:18px">{out}</div>'
    return E.piece(sid, a, b, body, (660, n * 134 + 20), "rows", v, text=" ".join(plain(i if isinstance(i, str) else i[0]) for i in items))


def title(sid, a, b, text, label=""):
    """Bottom-centre line over the speaker (the one text treatment used over footage): E.float_(K.title(...), zone="bottom").
    A handful of words, built word by word. Use for the promise in the intro and a key conclusion, not for subtitles."""
    E.css(""".bt{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:16px;padding-bottom:26px;text-align:center}
.bt .hd{font-family:"HelvB";font-size:78px;line-height:1.02;letter-spacing:-.048em;text-shadow:0 4px 40px rgba(0,0,0,.6);color:var(--paper)}.bt .hd span{display:inline-block}""")
    ws = "".join(f'<span class="h {sid}-w">{acc(x)}</span> ' for x in text.split(" "))
    body = f'<div class="bt">{f"<div class=lbl>{label}</div>" if label else ""}<div class="hd">{ws}</div></div>'
    E.tw(f".{sid}-w", a + 0.1, 0.6, {"opacity": 1, "y": 0, "stagger": 0.055}, {"opacity": 0, "y": 26}, "power3.out")
    return E.piece(sid, a, b, body, (1600, 250), "title", "bottom", text=plain(text))


def term(sid, a, b, text, sub=""):
    """A named idea pinned beside the speaker while it is defined (framework name, a key term): E.float_(K.term(...), side="left")."""
    E.css(""".tm{position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);padding:30px 34px;border-radius:var(--r);background:rgba(10,9,8,.86);border:1px solid rgba(255,255,255,.16);box-shadow:var(--sh)}.tm b{display:block;font-family:"HelvB";font-size:50px;letter-spacing:-.04em;line-height:1.05;color:var(--paper)}.tm span{display:block;font-size:26px;color:var(--grey);margin-top:12px;line-height:1.25}""")
    body = f'<div id="{sid}-t" class="tm h"><b>{acc(text)}</b>{f"<span>{sub}</span>" if sub else ""}</div>'
    E.enter(f"#{sid}-t", a, "focus"); E.sfx(a - 0.2, "swish", -24)
    return E.piece(sid, a, b, body, (520, 300), "term", "chip", text=plain(text + " " + sub))


def section(sid, a, b, n, name, total=None, variant="auto"):
    """A major topic change (use for some sections, not all, and prefer a transition that connects the ideas).
    number = a huge numeral behind the name | card = a card that opens from the centre | rail = progress rail n of total."""
    v = pick("section", variant, a)
    E.css(""".sn{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}.sn .nm{font-family:"HelvB";font-size:240px;letter-spacing:-.07em;line-height:.85;color:transparent;-webkit-text-stroke:3px rgba(242,240,236,.3)}
.sn .tt{font-family:"HelvB";font-size:84px;letter-spacing:-.05em;color:var(--paper);margin-top:-40px;text-align:center}.sn .cd{padding:50px 90px;border-radius:var(--r);text-align:center}.sn .cd .tt{margin-top:10px}
.sn .rl{display:flex;gap:12px;margin-top:34px}.sn .rl b{width:90px;height:8px;border-radius:4px;background:rgba(242,240,236,.2)}.sn .rl b.on{background:var(--o)}""")
    if v == "card":
        body = f'<div class="sn"><div id="{sid}-c" class="cd glass h"><div class="lbl">Part {n}</div><div class="tt">{acc(name)}</div></div></div>'
        E.tw(f"#{sid}-c", a - 0.1, 0.7, {"opacity": 1, "scaleX": 1, "scaleY": 1, "filter": "blur(0px)"}, {"opacity": 0, "scaleX": 0.3, "scaleY": 0.7, "filter": "blur(12px)"}, "power3.out")
    elif v == "rail" and total:
        rail = "".join(f'<b class="{"on" if i < n else ""}"></b>' for i in range(total))
        body = f'<div class="sn"><div id="{sid}-c" class="h"><div class="tt" style="margin-top:0">{acc(name)}</div><div class="rl" style="justify-content:center">{rail}</div></div></div>'; E.enter(f"#{sid}-c", a, "focus")
    else:
        v = "number"; body = f'<div class="sn"><div id="{sid}-n" class="nm h">{n}</div><div id="{sid}-c" class="tt h">{acc(name)}</div></div>'
        E.tw(f"#{sid}-n", a - 0.2, 0.9, {"opacity": 1, "scale": 1}, {"opacity": 0, "scale": 1.5}, "power3.out"); E.enter(f"#{sid}-c", a + 0.25, "rise")
    E.sfx(a - 0.2, "swoosh", -23)
    return E.piece(sid, a, b, body, (1300, 520), "section", v, text=plain(name))


# ------------------------------------------------------------------ explainer illustrations and visual metaphors
MT_CSS = """.dot{position:absolute;color:rgba(242,240,236,.75)}.dot.o{color:var(--o)}.blk{position:absolute;border-radius:12px;background:rgba(242,240,236,.16);border:1px solid rgba(242,240,236,.24)}
.blk.o{background:var(--o);border-color:var(--o)}.mlab{position:absolute;font-family:"HelvB";font-size:28px;letter-spacing:-.03em;color:var(--grey);text-align:center}
.fst{position:absolute;left:50%;height:92px;border-radius:999px;background:#1b1714;border:2px solid rgba(242,240,236,.22);display:flex;align-items:center;justify-content:space-between;padding:0 34px;font-family:"HelvB";font-size:32px;letter-spacing:-.03em;color:var(--paper)}
.fst em{font-style:normal;color:var(--grey);font-size:28px;font-variant-numeric:tabular-nums}"""


def funnel(sid, a, b, stages, keep, times):
    """A funnel as solid pills that narrow, with people visibly dropping out between stages (red) and the survivors carrying on.
    stages = names; keep = share still in at each stage (1, .4, .15, .05)."""
    n = len(stages); Wd, Hd = 1100, n * 150 + 10; out = ""; N = 24
    for i, s in enumerate(stages):
        ww = 420 + 520 * keep[i]; y = 20 + i * 150
        out += f'<div id="{sid}-s{i}" class="fst h" style="top:{y}px;width:{ww:.0f}px;margin-left:{-ww / 2:.0f}px"><span>{plain(s)}</span><em id="{sid}-e{i}">{round(100 * keep[i])}%</em></div>'
        E.enter(f"#{sid}-s{i}", times[i], "focus")
        if i:
            lost = max(1, round(N * (keep[i - 1] - keep[i])))
            for k in range(min(lost, 9)):
                sx = Wd / 2 + (k - min(lost, 9) / 2) * 50; did = f"{sid}-l{i}-{k}"
                out += f'<div id="{did}" class="dot h" style="left:{sx:.0f}px;top:{y - 56}px;width:46px;height:46px">{PERSON}</div>'
                E.tw(f"#{did}", times[i] - 0.9, 0.3, {"opacity": 1}, None, "power2.out")
                E.tw(f"#{did}", times[i] - 0.35 + k * 0.05, 1.0, {"x": (1 if k % 2 else -1) * (260 + 26 * k), "y": 70, "opacity": 0, "color": "#B3261E", "rotation": (1 if k % 2 else -1) * 40}, None, "power2.in")
            E.sfx(times[i] - 0.3, "swish", -25)
    E.sfx(a - 0.2, "woosh")
    return E.piece(sid, a, b, out, (Wd, Hd), "funnel", "pills", text=" ".join(stages), css_=MT_CSS)


def crowd(sid, a, b, t_hot, n=28, label=""):
    """A crowded market / everyone looks the same: a field of identical cards, then ONE lifts out and takes the colour."""
    cols = 7; Wd, Hd = 1100, 620; out = ""; hot = cols * 1 + 4
    for i in range(n):
        x, y = 40 + (i % cols) * 150, 40 + (i // cols) * 140
        out += f'<div id="{sid}-b{i}" class="blk h" style="left:{x}px;top:{y}px;width:120px;height:100px"></div>'
        E.tw(f"#{sid}-b{i}", a - 0.2 + 0.018 * i, 0.45, {"opacity": 1, "scale": 1}, {"opacity": 0, "scale": 0.7}, "power3.out")
        if i == hot: E.tw(f"#{sid}-b{i}", t_hot, 0.6, {"backgroundColor": "@@ACCENT@@", "borderColor": "@@ACCENT@@", "scale": 1.5, "z": 160, "zIndex": 5}, None, "back.out(1.3)")
        else: E.tw(f"#{sid}-b{i}", t_hot, 0.5, {"opacity": 0.28}, None, "power2.out")
    E.sfx(a - 0.2, "woosh"); E.sfx(t_hot, "shine", -23)
    lab = f'<div class="mlab" style="left:0;right:0;bottom:-6px">{label}</div>' if label else ""
    return E.piece(sid, a, b, f'<div class="p3" style="width:100%;height:100%">{out}{lab}</div>', (Wd, Hd + (50 if label else 0)), "metaphor", "crowd", text=label, css_=MT_CSS)


def compound(sid, a, b, times, label=""):
    """Things that compound (content, trust, skill): each piece lands on the pile and every column is taller than the last."""
    n = len(times); Wd, Hd = 1000, 600; out = ""; bw = min(110, (Wd - 80) / n - 16)
    for i in range(n):
        hgt = 46 + (i + 1) ** 1.55 / n ** 1.55 * 440; x = 40 + i * (Wd - 80) / n
        out += f'<div id="{sid}-b{i}" class="blk{" o" if i == n - 1 else ""} h" style="left:{x:.0f}px;bottom:60px;width:{bw:.0f}px;height:{hgt:.0f}px;transform-origin:50% 100%"></div>'
        E.tw(f"#{sid}-b{i}", times[i] - 0.25, 0.6, {"opacity": 1, "scaleY": 1, "y": 0}, {"opacity": 0, "scaleY": 0.2, "y": -120}, "power3.out")
        if i % 2 == 0: E.sfx(times[i] - 0.1, "pop", -26)
    lab = f'<div class="mlab" style="left:0;right:0;bottom:0">{label}</div>' if label else ""
    return E.piece(sid, a, b, out + lab, (Wd, Hd), "metaphor", "compound", text=label, css_=MT_CSS)


def spread(sid, a, b, t_split, n=7, label=""):
    """Spreading yourself too thin: one solid thing splits into many, each smaller and fainter the further it goes."""
    Wd, Hd = 900, 620; out = f'<div id="{sid}-c" class="blk o h" style="left:{Wd / 2 - 90}px;top:{Hd / 2 - 90}px;width:180px;height:180px;border-radius:50%"></div>'
    E.enter(f"#{sid}-c", a, "focus"); E.tw(f"#{sid}-c", t_split, 0.5, {"scale": 0.2, "opacity": 0}, None, "power2.in")
    for i in range(n):
        ang = i * 2 * math.pi / n; did = f"{sid}-p{i}"
        out += f'<div id="{did}" class="blk o h" style="left:{Wd / 2 - 40}px;top:{Hd / 2 - 40}px;width:80px;height:80px;border-radius:50%"></div>'
        E.setp(f"#{did}", t_split, {"opacity": 1})
        E.tw(f"#{did}", t_split, 1.4, {"x": 330 * math.cos(ang), "y": 240 * math.sin(ang), "scale": 0.42, "opacity": 0.32}, None, "power3.out")
    E.sfx(a - 0.2, "woosh"); E.sfx(t_split, "swoosh", -23)
    lab = f'<div class="mlab" style="left:0;right:0;bottom:0">{label}</div>' if label else ""
    return E.piece(sid, a, b, out + lab, (Wd, Hd), "metaphor", "spread", text=label, css_=MT_CSS)


def gap(sid, a, b, t_move, close=False, left="You", right="Audience"):
    """Distance between two parties (creator and audience, brand and buyer). close=False: they drift apart (no trust).
    close=True: the gap closes (trust built). The bridge line draws or breaks with it."""
    Wd, Hd = 1100, 460; d0, d1 = (140, 400) if not close else (400, 140)
    crowd_ = "".join(f'<div class="dot" style="left:{(k % 3) * 62}px;top:{(k // 3) * 66}px;width:54px;height:54px">{PERSON}</div>' for k in range(9))
    out = (f'<div id="{sid}-l" class="h" style="position:absolute;left:{Wd / 2 - 70}px;top:110px;width:140px"><div class="dot o" style="position:relative;width:140px;height:140px">{PERSON}</div><div class="mlab" style="position:relative;margin-top:14px">{left}</div></div>'
           f'<div id="{sid}-r" class="h" style="position:absolute;left:{Wd / 2 - 90}px;top:90px;width:186px"><div style="position:relative;height:198px">{crowd_}</div><div class="mlab" style="position:relative;margin-top:6px">{right}</div></div>'
           f'<div id="{sid}-b" style="position:absolute;left:50%;top:186px;height:6px;width:300px;margin-left:-150px;border-radius:3px;background:var(--o);transform:scaleX(0)"></div>')
    E.tw(f"#{sid}-l", a - E.LEAD, 0.6, {"opacity": 1, "x": -d0}, {"opacity": 0, "x": -d0 - 40}); E.tw(f"#{sid}-r", a - E.LEAD + 0.15, 0.6, {"opacity": 1, "x": d0}, {"opacity": 0, "x": d0 + 40})
    E.tw(f"#{sid}-l", t_move, 1.3, {"x": -d1}, None, "power2.inOut"); E.tw(f"#{sid}-r", t_move, 1.3, {"x": d1}, None, "power2.inOut")
    if close: E.tw(f"#{sid}-b", t_move + 0.9, 0.6, {"scaleX": 0.5}, None, "power2.out"); E.sfx(t_move + 1.1, "accept", -24)
    E.sfx(a - 0.2, "woosh"); E.sfx(t_move, "swish", -24)
    return E.piece(sid, a, b, out, (Wd, Hd), "metaphor", "gap-close" if close else "gap-open", text=f"{left} {right}", css_=MT_CSS)


def grow(sid, a, b, times, start=3, per=4, label=""):
    """Posting builds an audience: each content piece travels across to the audience, and the audience grows as it lands."""
    Wd, Hd = 1200, 560; out = ""; tot = start + per * len(times); cols = 7
    for k in range(tot):
        x, y = 660 + (k % cols) * 70, 80 + (k // cols) * 74; did = f"{sid}-u{k}"
        out += f'<div id="{did}" class="dot h" style="left:{x}px;top:{y}px;width:56px;height:56px">{PERSON}</div>'
        if k < start: E.enter(f"#{did}", a, "fade", lead=0)
        else:
            ti = times[(k - start) // per] + 0.55 + 0.05 * ((k - start) % per)
            E.tw(f"#{did}", ti, 0.4, {"opacity": 1, "scale": 1, "color": "@@ACCENT@@"}, {"opacity": 0, "scale": 0.4}, "back.out(1.4)"); E.tw(f"#{did}", ti + 0.5, 0.5, {"color": "rgba(242,240,236,.75)"}, None, "power2.out")
    for i, t in enumerate(times):
        did = f"{sid}-c{i}"; out += f'<div id="{did}" class="blk o h" style="left:60px;top:{Hd / 2 - 90}px;width:130px;height:180px;border-radius:16px"></div>'
        E.tw(f"#{did}", t - 0.2, 0.3, {"opacity": 1, "scale": 1}, {"opacity": 0, "scale": 0.7}); E.tw(f"#{did}", t + 0.1, 0.6, {"x": 520, "scale": 0.3, "opacity": 0}, None, "power2.in"); E.sfx(t, "swish", -25)
    lab = f'<div class="mlab" style="left:0;right:0;bottom:0">{label}</div>' if label else ""
    return E.piece(sid, a, b, out + lab, (Wd, Hd), "metaphor", "grow", text=label, css_=MT_CSS)


def custom(sid, a, b, body, size, name="custom", css_="", text=""):
    """A one-off graphic for the idea that IS this video (its signature). Write the HTML here, animate it with E.tw / E.enter,
    hide things until their entrance with class="h". Prefer a component when one fits; build custom when none tells the idea."""
    return E.piece(sid, a, b, body, size, "custom", name, text=text, css_=css_)
