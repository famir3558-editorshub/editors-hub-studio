#!/usr/bin/env python3
"""visual-essay-reel engine: one HyperFrames project (a single index.html) per video.
A visual essay around a talking-head presenter: their CUT-OUT sits in the lower half of a 9:16 frame on a matte black
backdrop lit by a controlled glow in the brand accent colour, and the space above them is an evidence wall that changes on
hard cuts.

Layers, bottom to top (1080x1920):
  #bg (near-black + charcoal falloff) -> #glow (accent light, movable) -> #grain -> #vig
  -> #back (full-bleed backdrops / collages, fade into the black) -> #wall (evidence cards, cut-outs, stats, labels)
  -> #me (the presenter's cut-out, bottom-anchored; hard moves and punch-ins) -> #front (titles; anything that must cover the presenter)
  -> captions.  #camSrc (the uncut-out crop) carries the sound and is only visible when the cut-out is missing.

Use from a project's build.py (all times are GLOBAL seconds on the cut timeline):
    import essay_engine as E
    E.init(ROOT)
    E.glow(0, "bottom")                                    # where the accent light comes from (hard-set on a cut)
    E.title(0.0, 2.6, "Borrowed *Proof*", "Why Results Sell")
    with E.scene(0.0, 2.6) as s:                            # one idea; everything in it is cut away at the end
        s.card("assets/media/tweet.png", E.slot("hero"), t=0.2, origin="https://x.com/...")
    with E.scene(2.6, 6.1) as s:
        a, b = E.slot("pair")
        s.card("assets/media/before.jpg", a, t=2.6, label="Before", origin="client folder: ...")
        s.card("assets/media/after.jpg", b, t=3.9, label="After", origin="client folder: ...")
    E.me(6.1, "left"); E.punch(8.4, 1.1, hold=1.6)
    E.build()
`*word*` inside any text = emphasis: the emphasis font in the accent colour (a figure stays in the caption font, in the accent colour).
A slot / box is (cx, top, w, h) in frame pixels: the largest area an asset may take; the card takes the asset's own shape inside it.
"""
import colorsys, html as _html, json, os, re, subprocess

ROOT = None; P = {}; BR = {}; CAPS = []; CUTS = []; PAL = {}
_B, _H, _F, _C, _J, BEATS, WARN = [], [], [], [], [], [], []     # backdrop html, wall html, front html, css, js
SFX, ASSETS, WORDS = [], [], []
_ME, _SOLO, _CHG, _SCN = [], [], [], []                          # presenter states, direct-to-camera windows, change times, scenes
SOUND = True            # sound cues are only written when asked for (sound=True on an element, or E.sfx)
GRAIN = 0.34            # strength of the film grain over the backdrop (0 = none)
GLOW = 1.0              # overall strength of the accent light (the frame must stay mostly black: keep <= 1.2)
DRIFT = 1.03            # slow push on a card while it is on screen (1.0 = still)
EARLY = 0.08            # entrances start this long before their time so they have landed on the word
SAFE_TOP = 270          # nothing that must be read above this (platform UI)
ZONE = (65, 200, 1015, 1060)      # evidence wall: x0, y0, x1, y1 (the bottom tucks behind the presenter's head)
GAP = 20
MAX_QUIET = 4.5         # seconds without anything new on screen before the build warns
_n = [0]

GLOWS = {               # where the light enters: centre x, centre y, width, height of the main bloom (frame px)
    "bottom": (540, 1900, 2300, 1500), "low-left": (140, 1760, 2100, 1500), "low-right": (940, 1760, 2100, 1500),
    "left": (-120, 1150, 1700, 1900), "right": (1200, 1150, 1700, 1900), "behind": (540, 1330, 1700, 1300),
    "top": (540, -80, 2100, 1100), "top-left": (60, 40, 1800, 1300), "top-right": (1020, 40, 1800, 1300), "off": (540, 2600, 800, 800)}
POSES = {               # presenter presets: scale, dx, dy (transform origin = bottom centre of the presenter's cut-out)
    "center": (1.0, 0, 0), "left": (1.08, -170, 0), "right": (1.08, 170, 0), "big": (1.16, 0, 0), "close": (1.32, 0, 0), "low": (0.86, 0, 0),
    "corner-left": (0.62, -250, -610), "corner-right": (0.62, 250, -610), "hidden": None}


TITLE_FONT = "@@TITLE_FONT@@"     # setup answer: "emphasis" (line 1 of a title in the emphasis font) or "main" (the caption / main font)
GLOW_DEFAULT = "@@GLOW_DEFAULT@@"  # setup answer: where the light enters when a build does not say (a key of GLOWS)


# ----------------------------------------------------------------------------------------------- set-up
def _hex(rgb): return "#%02X%02X%02X" % tuple(max(0, min(255, round(v * 255))) for v in rgb)


def palette(accent):
    """Every colour of the look, derived from ONE brand accent so a new HEX re-skins the whole system."""
    r, g, b = (int(accent[i:i + 2], 16) / 255 for i in (1, 3, 5)); h, l, s = colorsys.rgb_to_hls(r, g, b)
    mk = lambda hh, ll, ss: _hex(colorsys.hls_to_rgb(hh % 1, max(0, min(1, ll)), max(0, min(1, ss))))
    return {"o": accent.upper(), "o_dark": mk(h - 0.012, l * 0.62, s), "o_deep": mk(h - 0.022, l * 0.30, s * 0.92),
            "o_light": mk(h + 0.008, l + (1 - l) * 0.28, s), "o_hi": mk(h + 0.02, l + (1 - l) * 0.56, min(1, s * 1.05)),
            "o_glow": mk(h - 0.006, min(l, 0.50), min(s, 0.86)),          # the light itself: never neon
            "nb": mk(h, 0.024, 0.22), "ch": mk(h, 0.088, 0.09)}           # near-black and charcoal carry a trace of the hue


def init(root):
    global ROOT, P, BR, CAPS, CUTS, PAL
    ROOT = root
    P = json.load(open(os.path.join(root, "project.json")))
    BR = json.load(open(os.path.join(root, "assets", "brand.json")))
    PAL = palette(BR["accent"]); PAL.update(BR.get("palette") or {})      # brand.json "palette" overrides any derived value
    cp = os.path.join(root, "captions.json"); CAPS = json.load(open(cp)) if os.path.exists(cp) else []
    cu = os.path.join(root, "cuts.json"); CUTS = json.load(open(cu)) if os.path.exists(cu) else []
    for L in (_B, _H, _F, _C, _J, BEATS, WARN, SFX, ASSETS, WORDS, _ME, _SOLO, _CHG, _SCN, _GL): L.clear()
    _n[0] = 0
    if not CAPS: WARN.append("no captions.json in the project: the video would render WITHOUT captions (run 07_captions.py)")


def fr(t):
    """Snap a time to the exact frame boundary (2 ms early, so a hard cut never lands one frame late)."""
    return round(round(t * P["fps"]) / P["fps"] - 0.002, 4) if t > 0.01 else 0.0


def nid(p="e"):
    _n[0] += 1; return f"{p}{_n[0]}"


def tx(s):
    """Escape text; *word* -> emphasis (emphasis font, accent colour); figures keep the sans; newline -> <br>."""
    out = []
    for k, part in enumerate(re.split(r"\*([^*]+)\*", s)):
        e = _html.escape(part.replace("'", "’"), quote=False).replace("\n", "<br>")
        out.append(e if k % 2 == 0 else (f'<em class="nu">{e}</em>' if any(c.isdigit() for c in part) else f'<em class="iv">{e}</em>'))
    return "".join(out)


def _wrap(i, cx, top, inner, extra=""):
    """A 1080-wide flex row centred on cx; the inner element is the one that gets animated (never the wrapper's position)."""
    return f'<div id="{i}w" class="w" style="left:{round(cx - 540)}px;top:{round(top)}px;{extra}">{inner}</div>'


def _size(src):
    """Pixel size of an image or video in the project."""
    p = os.path.join(ROOT, src)
    if not os.path.exists(p): WARN.append(f"missing asset {src}"); return 16, 9
    if p.lower().endswith((".mp4", ".mov", ".webm", ".m4v")):
        o = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", p]).decode().strip().split(",")
        return int(o[0]), int(o[1])
    from PIL import Image
    return Image.open(p).size


def _isvid(src): return src.lower().endswith((".mp4", ".mov", ".webm", ".m4v"))


def sfx(t, name, level=-21):
    """A quiet sound on a KEY moment. name: woosh / swish / swoosh, pop, accept, shine, shine2, dtext, data."""
    if SOUND: SFX.append([round(max(0, t), 3), name, level])


def asset(src, origin, note="", mock=False):
    """Record where an asset came from (a file path, a URL). mock=True = a stand-in the creator should replace."""
    ASSETS.append({"src": src, "origin": origin, "note": note, "mock": bool(mock)}); return src


def wording(text, why="my wording"):
    WORDS.append({"text": text, "why": why}); return text


def _rec(src, origin, mock=False):
    if origin: asset(src, origin, mock=mock)
    elif not any(x["src"] == src for x in ASSETS):
        ASSETS.append({"src": src, "origin": "NOT RECORDED - pass origin= (the path or URL it came from) so the report can say", "note": "", "mock": False})


# ----------------------------------------------------------------------------------------------- layout
def slot(name="hero", n=None, cols=None, box=None):
    """Deliberate arrangements inside the evidence wall. Returns one box or a list of boxes (cx, top, w, h).
    hero (one large asset) | pair (side by side: comparison, before/after) | trio | stack (two rows) |
    hero+side (large + smaller supporting) | grid (n items, cols columns) | wide (short banner above the presenter's head)."""
    x0, y0, x1, y1 = box or ZONE; W, H = x1 - x0, y1 - y0; cx = (x0 + x1) / 2
    if name == "hero": return (cx, y0, W, H)
    if name == "wide": return (cx, y0 + H * 0.28, W, H * 0.5)
    if name == "pair": w = (W - GAP) / 2; return [(x0 + w / 2, y0, w, H), (x1 - w / 2, y0, w, H)]
    if name == "trio": w = (W - 2 * GAP) / 3; return [(x0 + w / 2 + k * (w + GAP), y0, w, H) for k in range(3)]
    if name == "stack": h = (H - GAP) / 2; return [(cx, y0, W, h), (cx, y0 + h + GAP, W, h)]
    if name == "hero+side": w = W * 0.64; return [(x0 + w / 2, y0, w, H), (x1 - (W - w - GAP) / 2, y0 + H * 0.16, W - w - GAP, H * 0.62)]
    if name == "grid":
        cols = cols or (2 if n <= 4 else 3); rows = -(-n // cols); w = (W - (cols - 1) * GAP) / cols; h = (H - (rows - 1) * GAP) / rows
        return [(x0 + w / 2 + (k % cols) * (w + GAP), y0 + (k // cols) * (h + GAP), w, h) for k in range(n)]
    raise ValueError(f"unknown slot {name}")


def _fit(src, box, fit="contain", valign="center"):
    cx, top, w, h = box
    if fit == "cover": return cx, top, round(w), round(h)
    aw, ah = _size(src); s = min(w / aw, h / ah); cw, ch = round(aw * s), round(ah * s)
    y = top + (h - ch) * {"top": 0, "center": 0.5, "bottom": 1}[valign]
    return cx, round(y), cw, ch


# ----------------------------------------------------------------------------------------------- backdrop light
_GL = []


def glow(t, where="bottom", strength=1.0, dur=0):
    """Where the accent light enters the black studio. Hard-set at t (put it on a cut / a change of idea) or, with
    dur, drift there slowly. where: bottom (default) | low-left | low-right | left | right | behind | top | top-left |
    top-right | off, or (cx, cy, w, h). The frame stays mostly black whatever you pick."""
    _GL.append((fr(t), where, strength, dur))


# ----------------------------------------------------------------------------------------------- presenter
def me(t, pose="center", scale=None, dx=None, dy=None):
    """Move / resize the presenter's cut-out with a HARD change at t (it reads as a cut, so put it on an edit cut or an evidence
    change). pose: center | left | right | big | close (straight-to-camera lines) | low | corner-left | corner-right | hidden. The presenter is the anchor: change
    them only when the composition needs it (a full-bleed backdrop, a wall that needs the centre), never for variety."""
    base = POSES[pose]
    st = {"t": fr(t), "hide": base is None}
    if base: st.update(s=scale or base[0], dx=base[1] if dx is None else dx, dy=base[2] if dy is None else dy)
    _ME.append(st); _CHG.append(st["t"]); BEATS.append({"t": st["t"], "kind": "switch"})


def punch(t, to=1.1, hold=None, ease=0):
    """A punch-in on the presenter for ONE line that deserves it (a strong claim, a punchline, the conclusion). Hard by default
    (reads as a cut); ease=0.3 makes it a quick push. hold = seconds until they return (default: until the next me())."""
    _ME.append({"t": fr(t), "punch": to, "ease": ease}); _CHG.append(fr(t))
    if hold: _ME.append({"t": fr(t + hold), "punch": 1.0, "ease": 0})
    BEATS.append({"t": round(t + 0.2, 3), "kind": "punch"})


def solo(a, b):
    """A stretch where the presenter talks straight to camera with nothing on the wall (a direct statement, the call to action).
    Only tells the build not to warn about the empty wall; combine with me(a, 'big') for a close framing."""
    _SOLO.append((a, b))


# ----------------------------------------------------------------------------------------------- full-bleed layers
def backdrop(src, a, b, mode="top", tint=0.0, dim=0.0, focus="50% 30%", origin=None, video=None):
    """Footage or a photo BEHIND the presenter, bleeding into the black (no card): b-roll, a place, a scene.
    mode: top (fills the upper ~62% and fades out behind them) | full (the whole frame; pair with me(a, 'hidden' or a
    corner pose) when it deserves full attention) | bottom (lower half, the presenter stands in front of it).
    tint 0-1 washes it toward the brand accent (a duotone silhouette at 1); dim 0-1 darkens it."""
    i = nid("bd"); a, b = fr(a), fr(b); _rec(src, origin); video = _isvid(src) if video is None else video
    geo = {"top": "left:0;top:0;width:1080px;height:1230px", "full": "inset:0", "bottom": "left:0;top:860px;width:1080px;height:1060px"}[mode]
    mask = {"top": "linear-gradient(180deg,#000 0%,#000 66%,transparent 100%)", "full": "none", "bottom": "linear-gradient(0deg,#000 0%,#000 72%,transparent 100%)"}[mode]
    flt = f"grayscale({tint:.2f}) contrast({1 + tint * 0.15:.2f}) brightness({1 - dim:.2f})"
    media = (f'<video id="{i}v" src="{src}" muted playsinline data-start="{a}" data-duration="{round(b - a, 3)}" data-track-index="{40 + _n[0]}" style="width:100%;height:100%;object-fit:cover;object-position:{focus};filter:{flt}"></video>'
             if video else f'<img src="{src}" style="width:100%;height:100%;object-fit:cover;object-position:{focus};filter:{flt};display:block">')
    wash = f'<div style="position:absolute;inset:0;background:linear-gradient(180deg,var(--o-deep),var(--o-glow));mix-blend-mode:color;opacity:{tint:.2f}"></div>' if tint else ""
    _B.append(f'<div id="{i}" class="bd" style="{geo};-webkit-mask-image:{mask};mask-image:{mask}">{media}{wash}</div>')
    _J.append(f'tl.set("#{i}",{{opacity:1}},{a});' + (f' tl.set("#{i}",{{opacity:0}},{b});' if b < P["dur"] - 0.05 else ""))
    _CHG.append(a); BEATS.append({"t": round(a + 0.2, 3), "kind": "element", "id": i, "text": os.path.basename(src)}); _SCN.append((a, b))
    return i


def collage(srcs, a, b, cols=2, tint=0.25, dim=0.1, origin=None):
    """A wall of images filling the whole frame behind the presenter (a trend, 'everyone', many examples at once). Opening and
    closing a reel on the same collage makes a bookend. origin = one string, or a list matching srcs."""
    i = nid("cg"); a, b = fr(a), fr(b); rows = -(-len(srcs) // cols); w, h = 1080 / cols, 1920 / rows; cells = ""
    for k, s in enumerate(srcs):
        _rec(s, origin[k] if isinstance(origin, (list, tuple)) else origin)
        cells += f'<img src="{s}" style="position:absolute;left:{(k % cols) * w:.1f}px;top:{(k // cols) * h:.1f}px;width:{w + 1:.1f}px;height:{h + 1:.1f}px;object-fit:cover;object-position:50% 25%;filter:grayscale({tint:.2f}) brightness({1 - dim:.2f})">'
    wash = f'<div style="position:absolute;inset:0;background:linear-gradient(180deg,var(--o-deep),var(--o-glow));mix-blend-mode:color;opacity:{tint:.2f}"></div>'
    _B.append(f'<div id="{i}" class="bd" style="inset:0">{cells}{wash}<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.25),transparent 30%,rgba(0,0,0,.35))"></div></div>')
    _J.append(f'tl.set("#{i}",{{opacity:1}},{a});' + (f' tl.set("#{i}",{{opacity:0}},{b});' if b < P["dur"] - 0.05 else ""))
    _CHG.append(a); BEATS.append({"t": round(a + 0.2, 3), "kind": "element", "id": i, "text": "collage"}); _SCN.append((a, b))
    return i


def title(a, b, line1, line2=None, y=None, size=118):
    """The opening title, IN FRONT of the presenter: line 1 in the emphasis font (white; an *emphasised* word turns
    to the accent colour), line 2 small in the caption font. Two to four words a line. Only for the hook or a chapter turn.
    The setup answer "title font" can put line 1 in the main font instead."""
    i = nid("tt"); a, b = fr(a), fr(b); y = y if y is not None else P["me"]["head_y"] + 250
    l2 = f'<div class="tt2" data-layout-allow-overlap>{tx(line2)}</div>' if line2 else ""
    _F.append(f'<div id="{i}" class="tt" style="top:{round(y)}px"><div class="tt1" data-layout-allow-overlap style="font-size:{size}px">{tx(line1)}</div>{l2}</div>')
    _J.append(f'pop("#{i}",{a},0.22);' + (f' tl.set("#{i}",{{opacity:0}},{b});' if b < P["dur"] - 0.05 else ""))
    BEATS.append({"t": round(a + 0.4, 3), "kind": "heading", "text": line1 + (" / " + line2 if line2 else "")})
    WORDS.append({"text": (line1 + (" / " + line2 if line2 else "")).replace("*", ""), "why": "title"}); _CHG.append(a)
    for ln in (line1, line2 or ""):
        if len(ln.replace("*", "")) > 22: WARN.append(f'title line "{ln}" is long: keep it to two to four words')
    return i


# ----------------------------------------------------------------------------------------------- scenes (the wall)
class scene:
    """One idea on the evidence wall between a and b. Every element takes t = the start of the word that names it.
    Everything still up at b is CUT (not faded): the next idea replaces it."""

    def __init__(self, a, b):
        self.a, self.b, self.ids, self.gone = fr(a), fr(b), [], set(); _SCN.append((self.a, self.b))

    def _add(self, i, htm, t, how="pop", sound=False, text="", front=False):
        (_F if front else _H).append(htm); self.ids.append(i)
        if not (self.a - 0.3 <= t <= self.b): WARN.append(f"element {i} enters at {t}s, outside its scene {self.a}-{self.b}")
        t = fr(t) if how == "cut" else t
        _J.append({"pop": f'pop("#{i}",{t});', "cut": f'tl.set("#{i}",{{opacity:1}},{t});', "rise": f'rise("#{i}",{t});'}[how])
        _CHG.append(t); BEATS.append({"t": round(t + 0.3, 3), "kind": "element", "id": i, "text": text})
        if sound: sfx(t - EARLY, ("woosh", "swish", "swoosh")[len(SFX) % 3], -21)
        return i

    # -- evidence
    def card(self, src, box, t, frame="auto", fit="contain", valign="center", label=None, source=None, how="pop",
             origin=None, mock=False, radius=18, video=None, drift=True, sound=False):
        """THE evidence element: a screenshot, post, article, product shot, photo or clip, at the asset's own shape inside
        box (never crop a person or a screenshot's text: fit='cover' is for scenery only).
        frame: 'auto' = none for screenshots that carry their own edge, 'white' = a white mat (screen recordings, app
        footage, photos that need lifting off the black), 'hair' = a thin light edge, None.
        label = a small tag on the top edge (Before / After, a name); source = a small credit line under the card
        (publication, author + year, @handle) so the viewer can tell what they are looking at."""
        i = nid(); _rec(src, origin, mock); video = _isvid(src) if video is None else video
        mat = 12 if frame == "white" else 0; cx, top, w, h = box
        so = 44 if source and not label else 0                  # the source line sits ABOVE the card (below it, the presenter's head would cover it)
        cx, y, cw, ch = _fit(src, (cx, top + so, w - 2 * mat, h - 2 * mat - so), fit, valign)
        if y < SAFE_TOP - 70: WARN.append(f"card {os.path.basename(src)} starts at y {y}: anything to be read must sit below y {SAFE_TOP}")
        if y + ch + 2 * mat > ZONE[3] + 60: WARN.append(f"card {os.path.basename(src)} runs to y {y + ch + 2 * mat}: the presenter's head will cover its lower part")
        if video:
            d = round(min(self.b, P["dur"]) - max(0, t - EARLY), 3)
            media = f'<video id="{i}v" src="{src}" muted playsinline data-start="{round(max(0, t - EARLY), 3)}" data-duration="{d}" data-track-index="{40 + _n[0]}" style="width:100%;height:100%;object-fit:{fit};display:block"></video>'
        else:
            media = f'<img src="{src}" style="width:100%;height:100%;object-fit:{fit};display:block">'
        cls = "card" + {"white": " mat", "hair": " hair"}.get(frame, "")
        lab = f'<div class="tag" style="position:absolute;left:50%;top:-20px;transform:translateX(-50%)">{tx(label)}</div>' if label else ""
        srcl = f'<div class="src" style="{"bottom" if label else "top"}:-40px">{tx(source)}</div>' if source else ""
        if label: WORDS.append({"text": label, "why": "label"})
        if source: WORDS.append({"text": source, "why": "source line"})
        r_in = max(0, radius - mat)
        htm = _wrap(i, cx, y, f'<div id="{i}" class="{cls}" style="width:{cw}px;height:{ch}px;border-radius:{radius}px;{"padding:%dpx;" % mat if mat else ""}">'
                              f'<div style="width:100%;height:100%;border-radius:{r_in}px;overflow:hidden">{media}</div>{lab}{srcl}</div>')
        self._add(i, htm, t, how, sound, os.path.basename(src))
        if drift and DRIFT != 1.0 and self.b - t > 1.2:
            _J.append(f'tl.fromTo("#{i}w",{{scale:1,transformOrigin:"50% {ch // 2}px"}},{{scale:{DRIFT},duration:{round(self.b - t, 3)},ease:"none"}},{t});')
        return i

    def cutout(self, src, box, t, how="pop", valign="bottom", label=None, origin=None, sound=False):
        """A transparent PNG with no card (a person's head, a product, a logo), sitting straight on the backdrop with a
        soft shadow. For 'this versus that' reveal them one after the other in a pair slot."""
        i = nid(); _rec(src, origin); cx, y, cw, ch = _fit(src, box, "contain", valign)
        lab = f'<div class="tag" style="position:absolute;left:50%;bottom:-22px;transform:translateX(-50%)">{tx(label)}</div>' if label else ""
        if label: WORDS.append({"text": label, "why": "label"})
        return self._add(i, _wrap(i, cx, y, f'<div id="{i}" class="cut" style="width:{cw}px;height:{ch}px"><img src="{src}" style="width:100%;height:100%;display:block">{lab}</div>'), t, how, sound, os.path.basename(src))

    def logo(self, src, cx, top, w, t, plate=True, origin=None):
        """A company logo, on a small white plate by default so any logo reads on black."""
        i = nid(); _rec(src, origin); aw, ah = _size(src); h = round(w * ah / aw)
        st = "background:#fff;padding:26px 34px;border-radius:16px;box-shadow:0 24px 60px rgba(0,0,0,.6)" if plate else ""
        return self._add(i, _wrap(i, cx, top, f'<div id="{i}" class="cut" style="{st}"><img src="{src}" style="width:{w}px;height:{h}px;display:block"></div>'), t, text=os.path.basename(src))

    # -- built graphics (only when there is no real thing to show)
    def stat(self, value, label, box, t, count=None, dur=1.0, source=None, size=220, sound=False):
        """A statistic as a graphic: the figure large in the caption font (accent colour), one short line under it, the source small.
        count=(from, to) ticks the number (value is then a template with {} for the number, e.g. '{}%')."""
        i = nid("st"); cx, top, w, h = box; shown = value.format(f"{count[0]:,}") if count else value
        srcl = f'<div class="stsrc">{tx(source)}</div>' if source else ""
        WORDS.append({"text": f"{value.format(count[1]) if count else value} - {label}" + (f" ({source})" if source else ""), "why": "statistic graphic"})
        htm = _wrap(i, cx, top + h * 0.22, f'<div id="{i}" class="stat" style="width:{round(w)}px"><div id="{i}n" class="stn" style="font-size:{size}px">{_html.escape(shown)}</div><div class="stl">{tx(label)}</div>{srcl}</div>')
        self._add(i, htm, t, "pop", sound, value)
        if count:
            pre, suf = value.split("{}"); _J.append(f'counter("#{i}n",{count[0]},{count[1]},{round(t + 0.05, 3)},{dur},{json.dumps(pre)},{json.dumps(suf)});')
            if sound: sfx(t + 0.05, "data", -24)
        return i

    def quote(self, text, who, box, t, size=54):
        """Words someone actually said or wrote, when there is no screenshot of them: a dark card, the line in white,
        the name small. Never for the speaker's own words (the caption carries those)."""
        i = nid("qt"); cx, top, w, h = box; WORDS.append({"text": f'"{text}" - {who}', "why": "quote card"})
        return self._add(i, _wrap(i, cx, top + h * 0.2, f'<div id="{i}" class="quote" style="width:{round(w - 40)}px;font-size:{size}px"><p>{tx(text)}</p><span>{tx(who)}</span></div>'), t, text=who)

    def tag(self, text, cx, top, t, how="pop"):
        """A small label on the wall (a name, a year, a category): dark chip, thin accent edge."""
        i = nid(); WORDS.append({"text": text, "why": "label"})
        return self._add(i, _wrap(i, cx, top, f'<div id="{i}" class="tag">{tx(text)}</div>'), t, how, text=text)

    def text(self, text, cx, top, t, size=64, w=900, how="pop", front=False):
        """A key phrase or number in type. Short (one to four words), and never a repeat of the spoken caption."""
        i = nid(); WORDS.append({"text": text.replace("*", ""), "why": "key phrase"})
        return self._add(i, _wrap(i, cx, top, f'<div id="{i}" class="txt" style="font-size:{size}px;max-width:{w}px">{tx(text)}</div>'), t, how, text=text, front=front)

    def raw(self, htm, css="", js="", ids=(), front=False):
        """Escape hatch for a one-off diagram: your own HTML (absolute, frame coordinates, opacity:0 to start), CSS and
        GSAP calls on `tl` in global seconds (helpers: pop, rise, counter). List its ids so the scene clears them."""
        (_F if front else _H).append(htm); _C.append(css); _J.append(js); self.ids += list(ids)

    # -- changes over time
    def out(self, i, t):
        for x in (i if isinstance(i, (list, tuple)) else [i]): _J.append(f'tl.set("#{x}",{{opacity:0}},{fr(t)});'); self.gone.add(x)

    def move(self, i, t, dx=0, dy=0, scale=1, dur=0.3):
        """Slide / resize something already up, to make room (hero image steps aside for a supporting one)."""
        _J.append(f'tl.to("#{i}",{{x:{dx},y:{dy},scale:{scale},duration:{dur},ease:"power3.out"}},{t});'); _CHG.append(t)

    def dim(self, i, t, to=0.35):
        for x in (i if isinstance(i, (list, tuple)) else [i]): _J.append(f'tl.to("#{x}",{{opacity:{to},duration:0.2}},{t});')

    def end(self):
        left = [x for x in self.ids if x not in self.gone]
        if left and self.b < P["dur"] - 0.05: _J.append(f'tl.set("{",".join("#" + x for x in left)}",{{opacity:0}},{self.b});')

    def __enter__(self): return self
    def __exit__(self, *a): self.end()


# ----------------------------------------------------------------------------------------------- build
JS_HELPERS = r"""
function pop(sel, t, d) { tl.fromTo(sel, { opacity: 0, scale: 0.94 }, { opacity: 1, scale: 1, duration: d || 0.18, ease: 'power3.out' }, Math.max(0, t - EARLY)); }
function rise(sel, t, d) { tl.fromTo(sel, { opacity: 0, y: 34 }, { opacity: 1, y: 0, duration: d || 0.22, ease: 'power3.out' }, Math.max(0, t - EARLY)); }
function counter(sel, a, b, t, d, pre, suf) { const el = document.querySelector(sel), p = { n: a }; tl.fromTo(p, { n: a }, { n: b, duration: d, ease: 'power2.out', onUpdate: function () { el.textContent = pre + Math.round(p.n).toLocaleString('en-US') + suf; } }, t); }
"""


def _in(t, wins): return any(a - 0.01 <= t < b for a, b in wins)


def build():
    D, FPS = P["dur"], P["fps"]; M, cap = P["me"], P["cap"]
    sans = "HelvB" if BR.get("sans") == "main" else "SFB"       # SFB = the caption font, HelvB = the main bold (internal aliases)
    title_face = "HelvB" if TITLE_FONT.strip().lower() == "main" else "Ivy"
    tt1em = 'font-family: "HelvB", sans-serif; font-weight: 700;' if title_face == "HelvB" else ""
    # ---- presenter states
    has_fg = os.path.exists(os.path.join(ROOT, "assets", "cam_fg.webm"))
    if not has_fg: WARN.append("assets/cam_fg.webm is missing: the presenter will show in a rounded panel with their real background instead of as a cut-out (run 06_cutout.py)")
    mejs, base, pz, capy = [], (1.0, 0, 0), 1.0, [(0.0, cap["y"])]
    foot = M["y"] + M["h"]
    for st in sorted(_ME, key=lambda s: s["t"]):
        if "punch" in st: pz = st["punch"]
        elif st["hide"]: mejs.append(f'tl.set("#me",{{opacity:0}},{st["t"]});'); capy.append((st["t"], cap["y"])); continue
        else: base, pz = (st["s"], st["dx"], st["dy"]), 1.0
        tgt = f'opacity:1,scale:{round(base[0] * pz, 4)},x:{base[1]},y:{base[2]}'
        mejs.append(f'tl.to("#me",{{{tgt},duration:{st["ease"]},ease:"power2.out"}},{st["t"]});' if st.get("ease") else f'tl.set("#me",{{{tgt}}},{st["t"]});')
        top = foot - (foot - M["head_y"]) * base[0] * pz + base[2]              # where the top of the head is now
        capy.append((st["t"], round(top - (cap["y_gap"] if "y_gap" in cap else M["head_y"] - cap["y"])) if abs(base[1]) < 200 and top > 420 else cap["y"]))
    # ---- captions: one line just above the head, following the presenter when they are moved or punched in
    caps, pieces = "", []
    for k, c in enumerate(CAPS):
        a, b = c["start"], min(c["end"], D); y = [v for t, v in capy if t <= a + 0.02][-1]
        inner = "".join((f'<em class="{"nu" if any(ch.isdigit() for ch in p["t"]) else "iv"}">{_html.escape(p["t"], quote=False)}</em>' if p.get("em") else _html.escape(p["t"], quote=False)) for p in c["parts"])
        caps += f'<div id="cap{k}" class="clip cap" data-layout-allow-overlap data-start="{round(a, 3)}" data-duration="{round(b - a, 3)}" data-track-index="30"><span id="capt{k}" data-layout-allow-overlap style="top:{y}px">{inner}</span></div>\n'
        pieces.append((round(a, 3), round(b, 3), "e"))
    npunch = sum(1 for s in _ME if s.get("punch", 1.0) != 1.0)
    if npunch > max(2, D / 7): WARN.append(f"{npunch} punch-ins in {D:.0f}s: a punch-in is for the few lines that deserve it, not a rhythm")
    # ---- light
    gd = GLOW_DEFAULT if GLOW_DEFAULT in GLOWS else "bottom"
    gl = sorted(_GL) or [(0.0, gd, 1.0, 0)]
    if gl[0][0] > 0.01: gl.insert(0, (0.0, gd, 1.0, 0))
    gjs = []
    for t, where, strength, dur in gl:
        cx, cy, w, h = GLOWS[where] if isinstance(where, str) else where
        tgt = f'left:{cx - w / 2},top:{cy - h / 2},width:{w},height:{h},opacity:{round(min(1.2, strength * GLOW), 3)}'
        gjs.append(f'tl.to("#glow",{{{tgt},duration:{dur},ease:"sine.inOut"}},{t});' if dur else f'tl.set("#glow",{{{tgt}}},{t});')
    cam_css = (f'#camSrc {{ position:absolute; left:{M["x"]}px; top:{M["y"]}px; width:{M["w"]}px; height:{M["h"]}px; opacity:0; z-index:1; }}' if has_fg else
               f'#camSrc {{ position:absolute; left:60px; top:{M["y"] + M["head_in"] - 60}px; width:960px; height:{1920 - (M["y"] + M["head_in"] - 60)}px; z-index:6; overflow:hidden; border-radius:36px 36px 0 0; box-shadow:0 0 0 1.5px rgba(255,255,255,.14),0 30px 80px rgba(0,0,0,.6); }} #camSrc video {{ margin-left:-60px; margin-top:{-(M["head_in"] - 60)}px; }}')
    fade = f'-webkit-mask-image:linear-gradient(0deg,transparent 0,#000 {M["fade"]}px);mask-image:linear-gradient(0deg,transparent 0,#000 {M["fade"]}px);' if M.get("fade") else ""
    fg = f'<div id="me" style="{fade}"><video id="vFg" src="assets/cam_fg.webm" muted playsinline data-start="0" data-duration="{D}" data-track-index="2"></video></div>' if has_fg else ""
    fonts = """
      @font-face { font-family: "SFB"; src: @@FONT_CAPTION_SRC@@; font-weight: 700; }
      @font-face { font-family: "SFS"; src: @@FONT_CAPTION_SRC@@; font-weight: 600; }
      @font-face { font-family: "SFM"; src: @@FONT_MAIN_REGULAR_SRC@@; font-weight: 500; }
      @font-face { font-family: "HelvB"; src: @@FONT_MAIN_BOLD_SRC@@; font-weight: 700; }
      @font-face { font-family: "Ivy"; src: @@FONT_ACCENT_SRC@@; font-style: normal; font-weight: 400; }"""
    pv = "; ".join(f"--{k.replace('_', '-')}: {v}" for k, v in PAL.items())
    index = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>{_html.escape(P["title"])} - 9x16</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>{fonts}
      :root {{ {pv}; }}
      body {{ margin: 0; background: #000; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: var(--nb); font-family: "{sans}", "HelvB", sans-serif; color: #fff; letter-spacing: -0.05em; }}
      /* matte black studio: near-black base, charcoal falloff from above, never a flat #000 */
      #bg {{ position: absolute; inset: 0; z-index: 0; background: radial-gradient(130% 62% at 50% -6%, var(--ch) 0%, transparent 70%), radial-gradient(90% 40% at 12% 34%, color-mix(in srgb, var(--ch) 60%, transparent) 0%, transparent 75%), var(--nb); }}
      /* the accent light: a wide ember halo with a brighter core, soft enough that no edge of the gradient can be seen */
      #glow {{ position: absolute; z-index: 0; border-radius: 50%; filter: blur(46px); background: radial-gradient(closest-side, color-mix(in srgb, var(--o-hi) 46%, transparent) 0%, color-mix(in srgb, var(--o-glow) 74%, transparent) 20%, color-mix(in srgb, var(--o-dark) 52%, transparent) 43%, color-mix(in srgb, var(--o-deep) 30%, transparent) 68%, transparent 100%); }}
      #grain {{ position: absolute; inset: 0; z-index: 1; background-image: url("assets/grain.png"); background-size: 512px 512px; mix-blend-mode: overlay; opacity: {GRAIN}; pointer-events: none; }}
      #vig {{ position: absolute; inset: 0; z-index: 1; background: radial-gradient(120% 78% at 50% 56%, transparent 52%, rgba(0,0,0,.5) 100%); pointer-events: none; }}
      #back {{ position: absolute; inset: 0; z-index: 2; }}
      .bd {{ position: absolute; opacity: 0; overflow: hidden; }}
      #wall {{ position: absolute; inset: 0; z-index: 3; }}
      #front {{ position: absolute; inset: 0; z-index: 8; pointer-events: none; }}
      .w {{ position: absolute; width: 1080px; display: flex; justify-content: center; pointer-events: none; }}
      em.iv {{ font-family: "Ivy", serif; font-style: normal; font-weight: 400; color: var(--o); letter-spacing: -0.03em; font-size: 1.12em; line-height: 0.9; }}
      em.nu {{ font-style: normal; color: var(--o); }}
      /* evidence keeps its own look; the system only lifts it off the black */
      .card {{ position: relative; box-sizing: content-box; opacity: 0; background: #0b0b0b; box-shadow: 0 30px 80px rgba(0,0,0,.62), 0 6px 18px rgba(0,0,0,.45); }}
      .card.mat {{ background: #fff; }}
      .card.hair {{ box-shadow: 0 0 0 1.5px rgba(255,255,255,.22), 0 30px 80px rgba(0,0,0,.62), 0 6px 18px rgba(0,0,0,.45); }}
      .cut {{ position: relative; opacity: 0; filter: drop-shadow(0 22px 34px rgba(0,0,0,.6)); }}
      .tag {{ box-sizing: border-box; padding: 8px 18px 10px; font-family: "SFS", "HelvB", sans-serif; font-size: 30px; line-height: 1; letter-spacing: -0.03em; white-space: nowrap; color: #fff; background: color-mix(in srgb, var(--nb) 88%, transparent); border: 1.5px solid var(--o); border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,.55); opacity: 0; }}
      .card .tag, .cut .tag {{ opacity: 1; }}
      .src {{ position: absolute; left: 0; right: 0; text-align: center; font-family: "SFM", "HelvB", sans-serif; font-size: 25px; letter-spacing: -0.02em; color: rgba(255,255,255,.62); white-space: nowrap; }}
      .stat {{ text-align: center; opacity: 0; }}
      .stn {{ line-height: 0.95; font-variant-numeric: tabular-nums; letter-spacing: -0.06em; color: var(--o); text-shadow: 0 0 70px color-mix(in srgb, var(--o-glow) 50%, transparent); }}
      .stl {{ margin-top: 14px; font-family: "SFS", "HelvB", sans-serif; font-size: 46px; line-height: 1.08; letter-spacing: -0.04em; }}
      .stsrc {{ margin-top: 16px; font-family: "SFM", "HelvB", sans-serif; font-size: 25px; letter-spacing: -0.02em; color: rgba(255,255,255,.58); }}
      .quote {{ box-sizing: border-box; padding: 40px 44px; border-radius: 18px; background: color-mix(in srgb, var(--ch) 86%, transparent); border-left: 6px solid var(--o); box-shadow: 0 30px 80px rgba(0,0,0,.6); opacity: 0; }}
      .quote p {{ margin: 0; font-family: "SFS", "HelvB", sans-serif; line-height: 1.14; letter-spacing: -0.04em; }} .quote span {{ display: block; margin-top: 22px; font-family: "SFM", "HelvB", sans-serif; font-size: 28px; letter-spacing: -0.02em; color: rgba(255,255,255,.62); }}
      .txt {{ text-align: center; line-height: 1.02; opacity: 0; text-shadow: 0 4px 24px rgba(0,0,0,.7); }}
      .tt {{ position: absolute; left: 0; width: 1080px; text-align: center; opacity: 0; }}
      .tt1 {{ font-family: "{title_face}", "Ivy", serif; font-weight: {400 if title_face == "Ivy" else 700}; letter-spacing: -0.035em; line-height: 0.95; text-shadow: 0 6px 30px rgba(0,0,0,.75); }} .tt1 em.iv {{ font-size: 1em; {tt1em} }}
      .tt2 {{ margin-top: 10px; font-size: 52px; line-height: 1; text-shadow: 0 4px 20px rgba(0,0,0,.8); }}
      #me {{ position: absolute; left: {M['x']}px; top: {M['y']}px; width: {M['w']}px; height: {M['h']}px; z-index: 6; transform-origin: 50% 100%; filter: drop-shadow(0 0 46px rgba(0,0,0,.5)); }}
      #me video {{ width: 100%; height: 100%; display: block; }}
      {cam_css}
      #camSrc video {{ width: {M['w']}px; height: {M['h']}px; display: block; }}
      .cap {{ z-index: 20; pointer-events: none; }}
      .cap span {{ position: absolute; left: 65px; right: 65px; top: {cap['y']}px; display: block; text-align: center; white-space: nowrap; font-family: "{sans}", "HelvB", sans-serif; font-weight: 700; font-size: {cap['size']}px; letter-spacing: -0.05em; line-height: 1; color: #fff; transform: translateY(-50%); text-shadow: 0 0 3px rgba(0,0,0,.95), 0 2px 5px rgba(0,0,0,.9), 0 4px 22px rgba(0,0,0,.8); }}
      {chr(10).join(_C)}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{D}" data-fps="{round(FPS)}">
      <div id="bg"></div><div id="glow"></div><div id="grain"></div><div id="vig"></div>
      <div id="back">
{chr(10).join(_B)}
      </div>
      <div id="wall">
{chr(10).join(_H)}
      </div>
      <div id="camSrc"><video id="vSrc" src="assets/cam.mp4" playsinline data-has-audio="true" data-start="0" data-duration="{D}" data-track-index="0"></video></div>
      {fg}
      <div id="front">
{chr(10).join(_F)}
      </div>
{caps}    </div>
    <script>
      const EARLY = {EARLY};
      const tl = gsap.timeline({{ paused: true }});
      {JS_HELPERS}
      {chr(10).join(gjs)}
      {chr(10).join(mejs)}
      {chr(10).join(_J)}
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    open(os.path.join(ROOT, "index.html"), "w").write(index)
    # ---- editorial checks: is the viewer SEEING what the speaker is talking about, and is every change motivated?
    chg = sorted(set(round(t, 3) for t in _CHG)); pts = [0.0] + chg + [D]
    for x, y in zip(pts, pts[1:]):
        if y - x > MAX_QUIET and not any(a <= x + 0.2 and b >= y - 0.2 for a, b in _SOLO):
            WARN.append(f"nothing new on screen between {x:.1f}s and {y:.1f}s ({y - x:.1f}s): is there something they mention here that can be SHOWN? (or mark it E.solo if it is a straight-to-camera line)")
    covered = sum(min(b, D) - a for a, b in _SCN)
    for c in CUTS:
        if c.get("big") and chg and min(abs(c["t"] - t) for t in chg) > 2.5 / FPS:
            WARN.append(f"big jump cut at {c['t']:.2f}s with nothing changing on it: put an evidence change, a me() move or a punch-in on that frame so the jump reads as intended")
    real = [x for x in ASSETS if not x["mock"]]
    if not real: WARN.append("no real assets recorded: this style is evidence-driven. Find the real post / person / page / product before drawing anything")
    json.dump({"beats": sorted(BEATS, key=lambda x: x["t"]), "captions": pieces, "palette": PAL}, open(os.path.join(ROOT, "beats.json"), "w"), indent=1)
    cues, last = [], -9
    for t, n, lv in sorted(SFX):
        if t > D - 0.8 or t - last < 0.3: continue
        cues.append([t, n, lv]); last = t
    json.dump({"dur": D, "cues": cues}, open(os.path.join(ROOT, "sfx.json"), "w"), indent=1)
    seen, assets = set(), []
    for x in ASSETS:
        if (x["src"], x["origin"]) not in seen: seen.add((x["src"], x["origin"])); assets.append(x)
    json.dump({"assets": assets, "wording": WORDS, "sounds": cues}, open(os.path.join(ROOT, "review.json"), "w"), indent=1)
    nel = sum(1 for x in BEATS if x["kind"] == "element")
    print(f"{len(pieces)} captions | {nel} visuals in {D:.1f}s = one every {D / max(1, nel):.1f}s (this style: a visual about every 2s when the script names something that often) | wall in use {100 * min(covered, D) / D:.0f}% of the time | {npunch} punch-ins")
    print(f"palette from {PAL['o']}: " + ", ".join(f"{k} {v}" for k, v in PAL.items() if k != "o"))
    print(f"{len(cues)} sound cues | {len(assets)} assets ({len(real)} real) and {len(WORDS)} wording choices recorded in review.json")
    for x in assets:
        if x["mock"] or x["origin"].startswith("NOT RECORDED"): print("REVIEW", "MOCK-UP " if x["mock"] else "", x["src"], "<-", x["origin"], x["note"])
    for w in WARN: print("WARN", w)
