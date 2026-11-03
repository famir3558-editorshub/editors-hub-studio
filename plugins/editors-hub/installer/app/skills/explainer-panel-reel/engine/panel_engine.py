#!/usr/bin/env python3
"""explainer-panel-reel engine: one HyperFrames project (a single index.html) per video.

Layers, bottom to top (1080x1920):
  black + dot grid -> #gfx (headings, sections, scene graphics) -> #panel (the speaker's video in a rounded panel at the
  bottom, original background kept) -> #panelFg (their cut-out, so head and hands may rise above the panel's top edge)
  -> #camFull (full-frame close-up, carries the audio; hard-cut on and off) -> watermark -> captions.
Brand values (accent colour, emphasis size, heading block, handle) come from assets/brand.json, which
08_new_project.py writes from the creator's profile. Fonts and the dark panel colour are filled in at setup.
Two modes: PANEL (default) and FULL (inside a full() window). Graphics keep building underneath a FULL window.

Use from a project's build.py (all times are GLOBAL seconds on the cut timeline):
    import panel_engine as E
    E.init(ROOT)
    E.full([[3.28, 5.28], [26.84, 29.48]])                      # full-frame close-up windows; everything else is panel
    E.heading(0.0, 5.2, "The Easiest Technique", "For Becoming A *Better Storyteller*")
    E.section(9.1, 19.6, "01", "Identity Labels")
    s = E.scene(5.3, 26.8)                                       # a group of graphics; whatever is left fades at the end
    a = s.node(540, 470, t=5.6, icon="?")
    b = s.box("New\nConcept", 190, 930, t=6.4)
    s.link((540, 540), (190, 930), t=6.1)
    s.out(a, 12.0)
    E.build()
`*word*` inside any text = emphasis: the emphasis font in the accent colour (a figure stays in the caption / main font, accent coloured).
Coordinates: cx = horizontal centre of the element, top = its top edge, in frame pixels. Graphics live in GFX_TOP..GFX_BOTTOM.
"""
import html as _html, json, os, re

ROOT = None; P = {}; BR = {}; CAPS = []; CUTS = []; FULL = []
_H, _C, _J, BEATS, WARN = [], [], [], [], []
_n = [0]
HEAD_TOP = 190          # top of the heading / section bar
GFX_TOP, GFX_BOTTOM = 380, 1190      # graphics stay between the heading and the caption line
SIDE = 65               # nothing readable closer to the left/right edge than this
EARLY = 0.15            # entrances start this long before their time so they have landed on the word
ZOOM_FULL = 1.0         # set to e.g. 1.04 for a slow, eased zoom out on every full-frame window (off by default)


# ----------------------------------------------------------------------------------------------- set-up
def init(root):
    global ROOT, P, BR, CAPS, CUTS, FULL, ZOOM_FULL
    ROOT = root
    P = json.load(open(os.path.join(root, "project.json")))
    BR = json.load(open(os.path.join(root, "assets", "brand.json")))
    ZOOM_FULL = float(BR.get("zoom_full", ZOOM_FULL))
    cp = os.path.join(root, "captions.json"); CAPS = json.load(open(cp)) if os.path.exists(cp) else []
    cu = os.path.join(root, "cuts.json"); CUTS = json.load(open(cu)) if os.path.exists(cu) else []
    FULL = []
    for L in (_H, _C, _J, BEATS, WARN): L.clear()
    _n[0] = 0
    if not CAPS: WARN.append("no captions.json in the project: the video would render WITHOUT captions (run 07_captions.py)")


def fr(t):
    """Snap a time to the exact frame boundary (2 ms early, so the switch never lands one frame late)."""
    return round(round(t * P["fps"]) / P["fps"] - 0.002, 4) if t > 0.01 else 0.0


def full(windows):
    """Full-frame close-up windows [[start, end], ...]. Edges are snapped to frames. Put the edges on edit cuts."""
    global FULL
    FULL = [[fr(a), min(fr(b), P["dur"])] for a, b in sorted(windows)]
    for a, b in FULL:
        for e in (a, b):
            if 0.05 < e < P["dur"] - 0.05:
                BEATS.append({"t": e, "kind": "switch"})
                if CUTS and min(abs(c["t"] - e) for c in CUTS) > 1.5 / P["fps"]:
                    WARN.append(f"mode switch at {e:.2f}s is not on an edit cut (fine when there is none nearby; a punch-in reads as a cut)")
        for c in CUTS:
            if c.get("big") and a + 0.08 < c["t"] < b - 0.08:
                WARN.append(f"big jump cut at {c['t']:.2f}s sits INSIDE the full-frame window {a:.2f}-{b:.2f}: move a switch onto it")
        if b - a < 0.9: WARN.append(f"full-frame window {a:.2f}-{b:.2f} is under 0.9s: it will read as a flash")
        if b - a > 8.5: WARN.append(f"full-frame window {a:.2f}-{b:.2f} is over 8.5s: this style keeps close-ups to about 1-8s")


def nid(p="e"):
    _n[0] += 1; return f"{p}{_n[0]}"


def tx(s):
    """Escape text; *word* -> emphasis (emphasis font, accent colour); figures keep the sans; newline -> <br>."""
    out = []
    for k, part in enumerate(re.split(r"\*([^*]+)\*", s)):
        e = _html.escape(part.replace("'", "\u2019"), quote=False).replace("\n", "<br>")
        out.append(e if k % 2 == 0 else (f'<em class="nu">{e}</em>' if any(c.isdigit() for c in part) else f'<em class="iv">{e}</em>'))
    return "".join(out)


def _wrap(i, cx, top, inner, extra=""):
    """A 1080-wide flex row centred on cx; the inner element is the one that gets animated (never the wrapper)."""
    return f'<div class="w" style="left:{round(cx - 540)}px;top:{round(top)}px;{extra}">{inner}</div>'


def _check(top, bottom, what):
    if top < GFX_TOP - 4 or bottom > GFX_BOTTOM + 4:
        WARN.append(f"{what}: y {round(top)}-{round(bottom)} is outside the graphics area {GFX_TOP}-{GFX_BOTTOM}")


# ----------------------------------------------------------------------------------------------- headings
def heading(a, b, line1, line2=None, block=None, size=54):
    """Two-line heading at the top, written on from the left as the speaker starts the point. line2 sits on a block of the accent
    colour (block=None takes the creator's setting), unless it holds an *emphasised* word (then, or with block=False,
    it is plain with a thin accent underline and the word is in the accent colour and emphasis font). Keep each line
    under ~34 characters."""
    i = nid("hd")
    if block is None: block = BR.get("heading_block", "block") != "underline"
    if line2 and "*" in line2: block = False          # an emphasised word must be in the accent colour: it cannot sit on the accent block
    l2 = f'<div class="hl"><span id="{i}b" class="{"blk" if block else "und"}">{tx(line2)}</span></div>' if line2 else ""
    _H.append(f'<div id="{i}" class="hd" style="top:{HEAD_TOP}px;font-size:{size}px"><div class="hl"><span id="{i}a">{tx(line1)}</span></div>{l2}</div>')
    _J.append(f'tl.set("#{i}",{{opacity:1}},{a}); wipe("#{i}a",{a},{0.42});' + (f' wipe("#{i}b",{round(a + 0.28, 3)},{0.45});' if line2 else "")
              + (f' fout("#{i}",{round(b - 0.25, 3)});' if b < P["dur"] - 0.05 else ""))
    BEATS.append({"t": round(a + 0.8, 3), "kind": "heading", "text": line1 + (" / " + line2 if line2 else "")})
    for ln in (line1, line2 or ""):
        if len(ln.replace("*", "")) > 36: WARN.append(f'heading line "{ln}" is long ({len(ln)} characters): check it fits inside the frame')
    return i


def section(a, b, num, title, w=730):
    """Numbered section bar at the top ("01  Identity Labels"): dark bar, accent left edge."""
    i = nid("sc")
    _H.append(_wrap(i, 540, HEAD_TOP, f'<div id="{i}" class="sbar" style="width:{w}px"><b>{_html.escape(str(num))}</b><span>{tx(title)}</span></div>'))
    _J.append(f'fin("#{i}",{a},{{s:0.96}});' + (f' fout("#{i}",{round(b - 0.25, 3)});' if b < P["dur"] - 0.05 else ""))
    BEATS.append({"t": round(a + 0.5, 3), "kind": "section", "text": f"{num} {title}"})
    return i


# ----------------------------------------------------------------------------------------------- scenes
class scene:
    """A group of graphics between a and b. Every element takes t = the moment (the word) it should be on screen.
    Anything not removed with out() fades just before b."""

    def __init__(self, a, b):
        self.a, self.b, self.ids, self.gone = a, b, [], set()

    def _add(self, i, htm, t, js="", o=""):
        _H.append(htm); self.ids.append(i)
        if not (self.a - 0.5 <= t <= self.b): WARN.append(f"element {i} enters at {t}s, outside its scene {self.a}-{self.b}")
        _J.append(f'fin("#{i}",{t}{"," + o if o else ""});' + js)
        BEATS.append({"t": round(t + 0.35, 3), "kind": "element", "id": i})
        return i

    # -- text and labels
    def box(self, text, cx, top, t, size=40, pad="16px 26px", fill=False):
        """Outlined label card (white hairline box, black inside). fill=True: solid accent colour."""
        i = nid(); n = text.count("\n") + 1; _check(top, top + n * size * 1.05 + 36, f"box '{text[:18]}'")
        return self._add(i, _wrap(i, cx, top, f'<div id="{i}" class="box{" fill" if fill else ""}" style="font-size:{size}px;padding:{pad}">{tx(text)}</div>'), t)

    def chip(self, text, cx, top, t, size=30):
        """Small solid accent-colour tag (a label on a card, a category name)."""
        i = nid(); return self._add(i, _wrap(i, cx, top, f'<div id="{i}" class="chip" style="font-size:{size}px">{tx(text)}</div>'), t)

    def term(self, text, cx, top, t, w=500, size=38):
        """Accent-colour gradient pill for a named term or example."""
        i = nid(); _check(top, top + 92, f"term '{text[:18]}'")
        return self._add(i, _wrap(i, cx, top, f'<div id="{i}" class="term" style="width:{w}px;font-size:{size}px">{tx(text)}</div>'), t)

    def text(self, text, cx, top, t, size=44, w=900, color="#fff"):
        """Plain text line(s), centred on cx. Use sparingly: the caption already carries the spoken words."""
        i = nid(); return self._add(i, _wrap(i, cx, top, f'<div id="{i}" class="txt" style="font-size:{size}px;max-width:{w}px;color:{color}">{tx(text)}</div>'), t)

    def node(self, cx, cy, t, r=62, icon="", img=None):
        """Glowing circle (accent ring): icon = a character / short text / inline <svg>; img = a picture inside it."""
        i = nid(); _check(cy - r, cy + r, "node")
        inner = f'<img src="{img}" style="width:100%;height:100%;object-fit:cover;border-radius:50%">' if img else icon
        return self._add(i, _wrap(i, cx, cy - r, f'<div id="{i}" class="node" style="width:{2 * r}px;height:{2 * r}px;font-size:{round(r * 0.9)}px">{inner}</div>'), t, o="{s:0.6}")

    # -- pictures
    def img(self, src, cx, top, w, h, t, radius=16, fit="cover", video=False, label=None):
        """A screenshot / photo / clip in a hairline card. Size the card to the asset's own shape (never crop a person:
        fit='contain' or a card of the same aspect). video=True plays the file from t (muted). label = accent chip on top."""
        i = nid(); _check(top, top + h, f"img {os.path.basename(src)}")
        if not os.path.exists(os.path.join(ROOT, src)): WARN.append(f"missing asset {src}")
        if video:
            d = round(min(self.b, P["dur"]) - max(0, t - EARLY), 3)
            media = f'<video id="{i}v" src="{src}" muted playsinline data-start="{round(max(0, t - EARLY), 3)}" data-duration="{d}" data-track-index="{40 + _n[0]}" style="width:100%;height:100%;object-fit:{fit}"></video>'
        else:
            media = f'<img src="{src}" style="width:100%;height:100%;object-fit:{fit};display:block">'
        lab = f'<div class="chip" style="position:absolute;left:50%;top:-18px;transform:translateX(-50%);font-size:26px;white-space:nowrap">{tx(label)}</div>' if label else ""
        return self._add(i, _wrap(i, cx, top, f'<div id="{i}" class="shot" style="width:{w}px;height:{h}px;border-radius:{radius}px"><div style="width:100%;height:100%;border-radius:{radius}px;overflow:hidden">{media}</div>{lab}</div>'), t)

    def grid(self, srcs, cx, top, t, cols=3, w=150, h=266, gap=18, stagger=0.09):
        """Thumbnails appearing one after another (reels, posts, examples). Returns the ids."""
        rows = -(-len(srcs) // cols); _check(top, top + rows * (h + gap) - gap, "grid"); ids = []
        for k, s in enumerate(srcs):
            c, r = k % cols, k // cols; n = min(cols, len(srcs) - r * cols)
            x = cx - (n * (w + gap) - gap) / 2 + c * (w + gap) + w / 2
            ids.append(self.img(s, x, top + r * (h + gap), w, h, round(t + k * stagger, 3), radius=10))
        return ids

    # -- diagrams
    def link(self, p1, p2, t, dur=0.45, dashed=False, dot=True, color="#fff", width=3):
        """A connecting line drawn from p1 to p2 (dashed = a looser relation). dot = an accent end marker at p2."""
        i = nid("ln"); (x1, y1), (x2, y2) = p1, p2
        if dashed:
            body = (f'<mask id="{i}m" maskUnits="userSpaceOnUse"><line id="{i}d" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#fff" stroke-width="{width + 8}" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/></mask>'
                    f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" stroke-dasharray="4 10" stroke-linecap="round" mask="url(#{i}m)"/>')
        else:
            body = f'<line id="{i}d" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/>'
        d = f'<circle id="{i}c" cx="{x2}" cy="{y2}" r="11" fill="var(--o)" stroke="#fff" stroke-width="3" opacity="0"/>' if dot else ""
        _H.append(f'<svg id="{i}" class="ln" viewBox="0 0 1080 1920" width="1080" height="1920">{body}{d}</svg>'); self.ids.append(i)
        _J.append(f'draw("#{i}d",{t},{dur});' + (f' tl.fromTo("#{i}c",{{opacity:0,scale:0.2,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:0.25,ease:"power2.out"}},{round(t + dur - 0.05, 3)});' if dot else ""))
        BEATS.append({"t": round(t + dur + 0.1, 3), "kind": "element", "id": i})
        return i

    def path(self, d, t, dur=0.9, color=None, width=5, fill="none"):
        """Any drawn SVG path in frame coordinates (a curve, a chart line, a bracket). color defaults to the accent colour."""
        i = nid("ph")
        _H.append(f'<svg id="{i}" class="ln" viewBox="0 0 1080 1920" width="1080" height="1920"><path id="{i}d" d="{d}" fill="{fill}" stroke="{color or "var(--o)"}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/></svg>')
        self.ids.append(i); _J.append(f'draw("#{i}d",{t},{dur});'); BEATS.append({"t": round(t + dur, 3), "kind": "element", "id": i}); return i

    def list(self, items, top, times, cx=540, w=640, show_at=None):
        """Numbered list: every row appears at show_at (default: the first time) with its title blurred; row k comes
        into focus and takes the active bar at times[k]. For 'here are the three things' followed by each in turn."""
        i = nid("li"); H, G = 96, 22; _check(top, top + len(items) * (H + G) - G, "list")
        rows = "".join(f'<div id="{i}r{k}" class="row" style="top:{k * (H + G)}px;width:{w}px;height:{H}px"><b>{k + 1:02d}</b><span id="{i}s{k}">{tx(it)}</span></div>' for k, it in enumerate(items))
        _H.append(_wrap(i, cx, top, f'<div id="{i}" style="position:relative;width:{w}px;height:{len(items) * (H + G)}px;opacity:0">{rows}</div>')); self.ids.append(i)
        t0 = times[0] - 0.5 if show_at is None else show_at
        js = f'fin("#{i}",{round(max(self.a, t0), 3)},{{s:0.97}});'
        for k, t in enumerate(times):
            js += f' tl.to("#{i}s{k}",{{filter:"blur(0px)",opacity:1,duration:0.35,ease:"power2.out"}},{t}); tl.to("#{i}r{k}",{{"--on":1,duration:0.3,ease:"power2.out"}},{t});'
            if k: js += f' tl.to("#{i}r{k - 1}",{{"--on":0,duration:0.3}},{t});'
            BEATS.append({"t": round(t + 0.4, 3), "kind": "element", "id": f"{i}r{k}"})
        _J.append(js); return i

    def typed(self, title, body, cx, top, w, h, t, dur=2.5, t_text=None):
        """A document / script card with text being typed (anything the speaker quotes: a hook, a script line, a prompt)."""
        i = nid("ty"); _check(top, top + h, "typed card")
        _H.append(_wrap(i, cx, top, f'<div id="{i}" class="doc" style="width:{w}px;height:{h}px"><i>{tx(title)}</i><p id="{i}p"></p></div>')); self.ids.append(i)
        ts = t + 0.35 if t_text is None else t_text
        _J.append(f'fin("#{i}",{t}); typeText("#{i}p",{json.dumps(body)},{ts},{dur});'); BEATS.append({"t": round(ts + dur, 3), "kind": "element", "id": i}); return i

    def count(self, cx, top, a, b, t, dur=1.2, prefix="", suffix="", size=120, color="#fff"):
        """A number ticking from a to b (plain counter, in the caption font)."""
        i = nid("ct"); _check(top, top + size, "counter")
        _H.append(_wrap(i, cx, top, f'<div id="{i}" class="cnt" style="font-size:{size}px;color:{color}">{prefix}{a:,}{suffix}</div>')); self.ids.append(i)
        _J.append(f'fin("#{i}",{t}); counter("#{i}",{a},{b},{round(t + 0.1, 3)},{dur},{json.dumps(prefix)},{json.dumps(suffix)});'); BEATS.append({"t": round(t + dur + 0.2, 3), "kind": "element", "id": i}); return i

    def raw(self, htm, css="", js="", ids=()):
        """Escape hatch for a one-off graphic: your own HTML (absolute, frame coordinates, opacity:0 to start), CSS and
        GSAP calls on `tl` in global seconds (helpers: fin, fout, draw, wipe, typeText, counter). List its ids so the scene clears them."""
        _H.append(htm); _C.append(css); _J.append(js); self.ids += list(ids)

    # -- changes over time
    def out(self, i, t, d=0.25):
        for x in (i if isinstance(i, (list, tuple)) else [i]):
            _J.append(f'fout("#{x}",{t},{d});'); self.gone.add(x)

    def move(self, i, t, dx=0, dy=0, scale=1, dur=0.5):
        """Slide / resize an element that is already on screen (to make room for the next one)."""
        _J.append(f'tl.to("#{i}",{{x:{dx},y:{dy},scale:{scale},duration:{dur},ease:"power2.inOut"}},{t});')

    def hot(self, i, t, on=True):
        """Light an element up in the accent colour (the one being talked about now); on=False returns it to normal."""
        _J.append(f'tl.to("#{i}",{{"--hot":{1 if on else 0},duration:0.3,ease:"power2.out"}},{t});')

    def dim(self, i, t, to=0.3):
        for x in (i if isinstance(i, (list, tuple)) else [i]): _J.append(f'tl.to("#{x}",{{opacity:{to},duration:0.3}},{t});')

    def end(self):
        left = [x for x in self.ids if x not in self.gone]
        if left and self.b < P["dur"] - 0.05:
            hidden = any(a - 0.3 <= self.b <= b for a, b in FULL)       # ends under a full-frame window: no fade needed
            sel = ",".join("#" + x for x in left)
            _J.append(f'tl.set("{sel}",{{opacity:0}},{self.b});' if hidden else f'fout("{sel}",{round(self.b - 0.25, 3)});')

    def __enter__(self): return self
    def __exit__(self, *a): self.end()


# ----------------------------------------------------------------------------------------------- build
JS_HELPERS = r"""
function fin(sel, t, o) { o = o || {}; tl.fromTo(sel, { opacity: 0, scale: o.s == null ? 0.92 : o.s, filter: 'blur(14px)' }, { opacity: 1, scale: 1, filter: 'blur(0px)', duration: o.d || 0.45, ease: 'power3.out' }, Math.max(0, t - EARLY)); }
function fout(sel, t, d) { tl.to(sel, { opacity: 0, filter: 'blur(8px)', duration: d || 0.25, ease: 'power2.in' }, t); }
function draw(sel, t, d) { tl.fromTo(sel, { strokeDashoffset: 1000 }, { strokeDashoffset: 0, duration: d || 0.5, ease: 'power2.inOut' }, t); }
function wipe(sel, t, d) { tl.fromTo(sel, { clipPath: 'inset(0% 100% 0% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: d || 0.45, ease: 'power2.out' }, t); }
function typeText(sel, s, t, d) { const el = document.querySelector(sel), p = { n: 0 }; tl.fromTo(p, { n: 0 }, { n: s.length, duration: d, ease: 'none', onUpdate: function () { el.textContent = s.slice(0, Math.round(p.n)); } }, t); }
function counter(sel, a, b, t, d, pre, suf) { const el = document.querySelector(sel), p = { n: a }; tl.fromTo(p, { n: a }, { n: b, duration: d, ease: 'power2.inOut', onUpdate: function () { el.textContent = pre + Math.round(p.n).toLocaleString('en-US') + suf; } }, t); }
"""

IG = ('<svg viewBox="0 0 48 48" width="46" height="46"><rect x="5" y="5" width="38" height="38" rx="11" fill="none" stroke="#fff" stroke-width="4"/>'
      '<circle cx="24" cy="24" r="8.5" fill="none" stroke="#fff" stroke-width="4"/><circle cx="34.5" cy="13.5" r="2.6" fill="#fff"/></svg>')


def _inwin(t): return any(a <= t < b for a, b in FULL)


def build():
    D, FPS = P["dur"], P["fps"]; pn, cap = P["panel"], P["cap"]; O = BR["accent"]; EMS = BR.get("emphasis_scale", 1.12)
    sans = "SFB"                                       # the caption font (the main bold when no separate caption font was chosen)
    # ---- captions: split at mode edges so each piece sits at the right height for its mode
    edges = sorted({x for w in FULL for x in w}); pieces = []
    for c in CAPS:
        a, b = c["start"], min(c["end"], D)
        ks = [a] + [e for e in edges if a + 0.04 < e < b - 0.04] + [b]
        for k in range(len(ks) - 1):
            pieces.append((c, round(ks[k], 3), round(ks[k + 1], 3), "f" if _inwin((ks[k] + ks[k + 1]) / 2) else "p"))
    caps = ""
    for k, (c, a, b, m) in enumerate(pieces):
        inner = "".join((f'<em class="{"nu" if any(ch.isdigit() for ch in p["t"]) else "iv"}">{_html.escape(p["t"], quote=False)}</em>' if p.get("em") else _html.escape(p["t"], quote=False)) for p in c["parts"])
        caps += f'<div id="cap{k}" class="clip cap cap-{m}" data-layout-allow-overlap data-start="{a}" data-duration="{round(b - a, 3)}" data-track-index="30"><span id="capt{k}" data-layout-allow-overlap>{inner}</span></div>\n'
    # ---- camera cuts
    cam = []
    if FULL and FULL[0][0] <= 0.001: cam.append("tl.set('#camFull',{opacity:1},0);")
    for k, (a, b) in enumerate(FULL):
        if a > 0.001: cam.append(f"tl.set('#camFull',{{opacity:1}},{a});")
        if b < D - 0.01: cam.append(f"tl.set('#camFull',{{opacity:0}},{b});")
        if ZOOM_FULL != 1.0: cam.append(f"tl.fromTo('#vFull',{{scale:{ZOOM_FULL},transformOrigin:'50% 40%'}},{{scale:1,duration:{round(b - a, 3)},ease:'sine.out',immediateRender:{'true' if k == 0 else 'false'}}},{a});")
    # ---- watermark (handle + platform glyph): only when the creator asked for one (brand.json then has a handle)
    wm = ""
    if BR.get("handle"):
        wm = f'<div id="wm"><div>{IG if BR.get("platform", "instagram") == "instagram" else ""}</div><span>{_html.escape(BR["handle"].upper())}</span></div>'
        for a, b in FULL:
            cam.append(f"tl.set('#wm',{{left:{1080 - SIDE - 250},top:440,textAlign:'right'}},{a}); tl.set('#wm',{{left:{pn['x'] + 6},top:{cap['panel_y'] - 150},textAlign:'left'}},{b});")
    has_fg = P.get("popout") and os.path.exists(os.path.join(ROOT, "assets", "cam_panel_fg.webm"))
    if P.get("popout") and not has_fg: WARN.append("popout is on but assets/cam_panel_fg.webm is missing: the head will be clipped by the panel's top edge (run 06_crops.py without --no-matte)")
    head = pn["head"]
    fg = f'<div id="panelFg"><video id="vFg" src="assets/cam_panel_fg.webm" muted playsinline data-start="0" data-duration="{D}" data-track-index="2"></video></div>' if has_fg else ""
    fonts = f"""
      @font-face {{ font-family: "SFB"; src: @@FONT_CAPTION_SRC@@; font-weight: 700; }}
      @font-face {{ font-family: "SFS"; src: @@FONT_CAPTION_SRC@@; font-weight: 600; }}
      @font-face {{ font-family: "HelvB"; src: @@FONT_MAIN_BOLD_SRC@@; font-weight: 700; }}
      @font-face {{ font-family: "Ivy"; src: @@FONT_ACCENT_SRC@@; font-style: normal; font-weight: 400; }}"""
    index = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>{_html.escape(P["title"])} - 9x16</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>{fonts}
      :root {{ --o: {O}; }}
      body {{ margin: 0; background: #000; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #000; font-family: "{sans}", "HelvB", sans-serif; color: #fff; letter-spacing: -0.05em; }}
      #dots {{ position: absolute; inset: 0; z-index: 0; background-image: radial-gradient(rgba(255,255,255,.085) 1.6px, transparent 2px); background-size: 34px 34px; }}
      #gfx {{ position: absolute; inset: 0; z-index: 2; }}
      .w {{ position: absolute; width: 1080px; display: flex; justify-content: center; pointer-events: none; }}
      em.iv {{ font-family: "Ivy", serif; font-style: normal; font-weight: 400; color: var(--o); letter-spacing: -0.03em; font-size: {EMS}em; line-height: 0.9; }}
      em.nu {{ font-style: normal; color: var(--o); }}
      .hd {{ position: absolute; left: 0; width: 1080px; text-align: center; opacity: 0; line-height: 1.12; }}
      .hl span {{ display: inline-block; padding: 1px 16px 3px; white-space: nowrap; }}
      .hl .blk {{ color: @@ON_ACCENT@@; background: var(--o); box-shadow: 0 0 34px color-mix(in srgb, var(--o) 55%, transparent); }}
      .hl .blk em.iv, .hl .blk em.nu {{ color: @@ON_ACCENT@@; }}
      .hl .und {{ border-bottom: 4px solid var(--o); }}
      .sbar {{ height: 108px; display: flex; align-items: center; gap: 0; box-sizing: border-box; border: 2px solid rgba(255,255,255,.55); border-left: 16px solid var(--o); background: linear-gradient(90deg, #0b0b0b, #3a3a3a); font-size: 46px; opacity: 0; }}
      .sbar b {{ width: 120px; text-align: center; font-weight: 700; }} .sbar span {{ flex: 1; text-align: center; padding-right: 60px; white-space: nowrap; }}
      .box {{ --hot: 0; border: 3px solid color-mix(in srgb, var(--o) calc(var(--hot) * 100%), #fff); background: @@BG@@; text-align: center; line-height: 1.02; white-space: nowrap; opacity: 0; box-shadow: 0 0 calc(var(--hot) * 40px) var(--o); }}
      .box.fill {{ background: var(--o); border-color: var(--o); color: @@ON_ACCENT@@; }}
      .chip {{ background: var(--o); color: @@ON_ACCENT@@; padding: 5px 16px 7px; line-height: 1; white-space: nowrap; opacity: 0; box-shadow: 0 0 24px color-mix(in srgb, var(--o) 50%, transparent); }}
      .shot .chip {{ opacity: 1; }}
      .term {{ height: 88px; display: flex; align-items: center; justify-content: center; border-radius: 8px; border: 2px solid rgba(255,255,255,.75); color: @@ON_ACCENT@@; background: linear-gradient(90deg, color-mix(in srgb, var(--o) 55%, #000), var(--o) 50%, color-mix(in srgb, var(--o) 55%, #000)); box-shadow: 0 0 30px color-mix(in srgb, var(--o) 45%, transparent); white-space: nowrap; opacity: 0; }}
      .txt {{ text-align: center; line-height: 1.08; opacity: 0; }}
      .node {{ --hot: 1; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-sizing: border-box; border: 3px solid rgba(255,255,255,.85); background: radial-gradient(circle at 50% 40%, color-mix(in srgb, var(--o) 55%, #000), #0a0a0a 75%); color: var(--o); box-shadow: 0 0 calc(var(--hot) * 46px) color-mix(in srgb, var(--o) 70%, transparent); opacity: 0; }}
      .shot {{ --hot: 0; position: relative; box-sizing: border-box; border: 2px solid color-mix(in srgb, var(--o) calc(var(--hot) * 100%), rgba(255,255,255,.8)); background: #0a0a0a; box-shadow: 0 0 calc(18px + var(--hot) * 30px) color-mix(in srgb, var(--o) calc(var(--hot) * 80%), rgba(255,255,255,.14)); opacity: 0; }}
      .ln {{ position: absolute; left: 0; top: 0; overflow: visible; pointer-events: none; }}
      .row {{ --on: 0; position: absolute; left: 0; display: flex; align-items: center; box-sizing: border-box; font-size: 42px; border: 2px solid rgba(255,255,255, calc(var(--on) * .55)); border-left: 14px solid color-mix(in srgb, var(--o) calc(var(--on) * 100%), transparent); background: linear-gradient(90deg, rgba(11,11,11,var(--on)), rgba(58,58,58,var(--on))); }}
      .row b {{ width: 110px; text-align: center; font-weight: 700; }} .row span {{ flex: 1; text-align: center; padding-right: 50px; white-space: nowrap; filter: blur(9px); opacity: .55; }}
      .doc {{ box-sizing: border-box; padding: 26px 34px; border: 2px solid rgba(255,255,255,.85); border-radius: 6px; background: #000; box-shadow: 0 0 34px rgba(255,255,255,.22); opacity: 0; }}
      .doc i {{ display: block; text-align: center; font-family: "Ivy", serif; font-style: normal; font-size: 44px; letter-spacing: -0.03em; margin-bottom: 18px; }}
      .doc p {{ margin: 0; font-family: "SFS", "HelvB", sans-serif; font-size: 34px; line-height: 1.22; letter-spacing: -0.04em; }}
      .cnt {{ line-height: 1; font-variant-numeric: tabular-nums; opacity: 0; }}
      #panel {{ position: absolute; left: {pn['x']}px; top: {pn['y']}px; width: {pn['w']}px; height: {pn['h']}px; z-index: 5; overflow: hidden; border-radius: {pn['r']}px {pn['r']}px 0 0; box-shadow: 0 0 0 1.5px rgba(255,255,255,.14), 0 0 40px rgba(255,255,255,.06); }}
      #panel video {{ position: absolute; left: 0; top: {-head}px; width: {pn['w']}px; height: {pn['h'] + head}px; display: block; }}
      #panelFg {{ position: absolute; left: {pn['x']}px; top: {pn['y'] - head}px; width: {pn['w']}px; height: {pn['h'] + head}px; z-index: 6; }}
      #panelFg video {{ width: 100%; height: 100%; display: block; }}
      #camFull {{ position: absolute; inset: 0; z-index: 8; overflow: hidden; opacity: 0; background: #000; }}
      #camFull video {{ width: 1080px; height: 1920px; display: block; }}
      #wm {{ position: absolute; left: {pn['x'] + 6}px; top: {cap['panel_y'] - 150}px; width: 250px; z-index: 15; font-family: "SFS", "HelvB", sans-serif; font-size: 21px; letter-spacing: 0.02em; opacity: .9; }}
      #wm span {{ display: block; margin-top: 6px; }}
      .cap {{ z-index: 20; pointer-events: none; }}
      .cap span {{ position: absolute; left: {SIDE}px; right: {SIDE}px; display: block; text-align: center; white-space: nowrap; font-family: "{sans}", "HelvB", sans-serif; font-weight: 700; font-size: {cap['size']}px; letter-spacing: -0.05em; line-height: 1; color: #fff; transform: translateY(-50%); text-shadow: 0 3px 16px rgba(0,0,0,.75), 0 0 2px rgba(0,0,0,.6); }}
      .cap-p span {{ top: {cap['panel_y']}px; }}
      .cap-f span {{ top: {cap['full_y']}px; }}
      {chr(10).join(_C)}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{D}" data-fps="{round(FPS)}">
      <div id="dots"></div>
      <div id="gfx">
{chr(10).join(_H)}
      </div>
      <div id="panel"><video id="vPanel" src="assets/cam_panel.mp4" muted playsinline data-start="0" data-duration="{D}" data-track-index="1"></video></div>
      {fg}
      <div id="camFull"><video id="vFull" src="assets/cam_full.mp4" playsinline data-has-audio="true" data-start="0" data-duration="{D}" data-track-index="0"></video></div>
      {wm}
{caps}    </div>
    <script>
      const EARLY = {EARLY};
      const tl = gsap.timeline({{ paused: true }});
      {JS_HELPERS}
      {chr(10).join(cam)}
      {chr(10).join(_J)}
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    open(os.path.join(ROOT, "index.html"), "w").write(index)
    # ---- report
    tf = sum(b - a for a, b in FULL); t = 0.0; panels = []
    for a, b in FULL:
        if a - t > 0.05: panels.append((t, a))
        t = b
    if D - t > 0.05: panels.append((t, D))
    for a, b in panels:
        if b - a > 22: WARN.append(f"panel block {a:.1f}-{b:.1f} runs {b - a:.0f}s without a close-up: this style breaks to full frame at least every ~20s")
    gaps = sorted(x["t"] for x in BEATS if x["kind"] in ("element", "heading", "section"))
    for a, b in panels:
        inside = [a] + [x for x in gaps if a <= x <= b] + [b]
        for x, y in zip(inside, inside[1:]):
            if y - x > 4.0: WARN.append(f"nothing new appears above the speaker between {x:.1f}s and {y:.1f}s ({y - x:.1f}s) while the speaker is in the panel: add a build or switch to full frame")
    json.dump({"full": FULL, "beats": sorted(BEATS, key=lambda x: x["t"]), "captions": [[a, b, m] for _, a, b, m in pieces]}, open(os.path.join(ROOT, "beats.json"), "w"), indent=1)
    print(f"{len(pieces)} caption pieces | {len(FULL)} full-frame windows = {100 * tf / D:.0f}% of {D:.1f}s (this style: 20-30%) | {sum(1 for x in BEATS if x['kind'] == 'element')} graphic beats")
    for w in WARN: print("WARN", w)
