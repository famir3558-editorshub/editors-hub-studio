"""yt_engine.py - the 16:9 long-form engine for the split-screen-document-plus-animations skill.

This is the educational-youtube-editor engine plus a DOCUMENT GUARD: the base video already switches between the speaker
full screen and a document split, windows.json lists the document stretches ("doc"), and the engine refuses any scene that
touches one, resets drift and punch-ins on the exact frame a layout switches, and carries the render fixes noted in SKILL.md.

The cut plays untouched underneath; build.py declares what goes over it. One HyperFrames page is generated per CHUNK
of the video (a few minutes each, split where nothing is on screen) so a 40-minute video renders in manageable parts.

Five visual states (the talking head is the default; everything else is declared):
  head    the speaker full screen. Nothing to declare. A very slow camera drift (3-6%, in or out, one move per stretch) keeps
          the shot alive; E.punch() adds an occasional motivated punch-in.
  float   the speaker full screen + a designed element in the empty space beside them, or along the bottom / top.
  panel   a side panel slides in and the speaker slides across.
  split   a GENUINE 50/50 split: the frame divides cleanly down the middle. The real footage, cropped naturally around the speaker,
          fills one half edge to edge (never a card, rounded box or frame); the branded side holds the graphic.
  full    a full-screen visual explanation on the backdrop. The voice carries on.

    import yt_engine as E, yt_kit as K
    E.init(__file__)
    t = E.w("apple", 61)                                   # when the word is said (cut timeline)
    E.split(K.browser("apple", t, t + 6, "assets/media/apple.jpg", "apple.com"), why="evidence", score=4)
    E.build()                                              # -> index.html for the chunk in argv, plus audit.json

Every scene carries `why` (one of WHY) and `score` (1-5). E.report() audits density, variety, how much the speaker is seen,
intro strength, text load and cut alignment. All times are seconds on the CUT timeline.
"""
import json, os, re, sys

W, H, FPS_DEFAULT = 1920, 1080, 24
WHY = ("explain", "demonstrate", "evidence", "example", "simplify", "curiosity", "emphasis", "momentum", "memory")

# ---- design system: one place, so every video shares the same corners, shadows, spacing and motion --------------
RADIUS, RADIUS_S = 28, 16
LEAD = 0.35                          # elements start this long before the word so they land on it
DRIFT = (0.03, 0.06)                 # slow camera drift on them while nothing covers them: 3% on a short stretch, up to 6% on a long one. (0, 0) = off
DRIFT_SECONDS = 45                   # one move takes at most this long, then holds: never in-and-out
OPEN = "in"                          # the video opens on a subtle zoom "in" or "out"; later stretches alternate
def _num(v, d):
    try: return float(v)
    except ValueError: return d


PUNCH = _num("@@PUNCH_PERCENT@@", 112) / 100     # default punch-in scale on the speaker (a hard cut-in, used rarely and only with a reason); a setup answer
DEPTH = "@@DEPTH_3D@@".strip().lower() not in ("off", "no", "none", "flat", "false")   # setup answer. Off = every graphic stays flat: no Z movement, no 3D tilt
RET = 30                             # the opening: something meaningful changes within 3 s, then every 2-5 s until here
PANEL_W, PANEL_SHIFT = 800, 400
REGION = {"full": (160, 90, 1600, 900), "panel": (70, 60, 660, 960)}
SAME_LOOK_GAP = 150                  # seconds before the same component+variant may come back
INTRO = 45                           # seconds treated as the intro (highest density)

DOCS = []                            # [a, b] stretches where the base video is already the document split: protected (no scene, punch-in or drift)
ROOT = None; P = {}; DUR = 0.0; FPS = 24.0; FPS_STR = "24"; FACE = (960, 400); WORDS = []; CUTS = []; SECTIONS = []
SC = []; TW = []; CN = []; SFX = []; XCSS = []; ASSETS = {}; PU = []; USES = []; _FACES = {}
_3D = ("z", "rotationX", "rotationY"); WM = {}
_trk = [0]


def init(build_file):
    """Call first. Reads project.json, cut_words.json and cuts.json next to build.py."""
    global ROOT, P, DUR, FPS, FPS_STR, FACE, WORDS, CUTS, SECTIONS, FACES_SRC
    ROOT = os.path.dirname(os.path.abspath(build_file)); P = json.load(open(f"{ROOT}/project.json"))
    DUR = float(P["dur"]); FPS = float(P.get("fps", 24)); FPS_STR = P.get("fps_str", "24"); FACE = tuple(P.get("face", (960, 400)))
    ld = lambda n, d: json.load(open(f"{ROOT}/{n}")) if os.path.exists(f"{ROOT}/{n}") else d
    if P.get("skill"): FACES_SRC = f"{P['skill']}/scripts/faces.swift"      # wherever the skill is installed
    WORDS = ld("cut_words.json", []); CUTS = ld("cuts.json", []); SECTIONS = (ld("content_map.json", {}) or {}).get("sections", [])
    ASSETS.update({a["file"]: a for a in ld("assets.json", [])})
    for L in (SC, TW, CN, SFX, XCSS, PU, USES): L.clear()
    WM.clear()
    DOCS.clear(); DOCS.extend((ld("windows.json", {}) or {}).get("doc", []))
    _FACES.clear(); _FACES.update(ld("faces.json", {}))


# ---------------------------------------------------------------- timing helpers
def _n(s): return re.sub(r"[^a-z0-9]", "", s.lower())


def w(token, after=0.0, end=False):
    """Time the creator says `token` (a word, or several words) at or after `after`. Fails loudly with the nearby script."""
    toks = [_n(x) for x in token.split()]
    for i, x in enumerate(WORDS):
        if x[1] >= after - 0.01 and all(i + k < len(WORDS) and _n(WORDS[i + k][0]).startswith(tk) for k, tk in enumerate(toks)):
            return round(WORDS[i + len(toks) - 1][2] if end else x[1], 3)
    near = " ".join(x[0] for x in WORDS if after - 1 <= x[1] <= after + 14)
    raise SystemExit(f"E.w: {token!r} not found after {after}s. The creator says: {near}")


def fr(t): return round(round(t * FPS) / FPS, 4)


def snap(t, tol=0.7, big=False):
    """Nearest edit cut within tol seconds (so a state switch can hide the jump), else t."""
    c = [j["t"] for j in CUTS if (j["big"] or not big) and abs(j["t"] - t) <= tol]
    return fr(min(c, key=lambda x: abs(x - t)) - 0.002) if c else t


# ---------------------------------------------------------------- declaring animation (used by the kit)
def _flat(v):
    """With depth switched off at setup, 3D properties are dropped so a graphic keeps its position, scale and fade but stays flat."""
    return v if DEPTH or v is None else {k: x for k, x in v.items() if k not in _3D}


def tw(sel, t, d, to, frm=None, ease="power3.out"): TW.append([sel, round(t, 3), round(d, 3), _flat(to), _flat(frm), ease])
def setp(sel, t, to): TW.append([sel, round(t, 3), 0, _flat(to), None, "none"])
def count(sel, t, frm, to, d=1.2, pre="", suf="", dec=0): CN.append([sel, round(t, 3), frm, to, d, pre, suf, dec])
def sfx(t, name, lv=-21): SFX.append([round(t, 3), name, lv])
def css(s): XCSS.append(s)


def enter(sel, t, fx="focus", d=None, lead=LEAD, stagger=0):
    """Standard entrances. focus = the focus pull (blurred and slightly large -> sharp). Others exist for variety, not decoration."""
    F = {"focus": ({"opacity": 0, "scale": 1.08, "filter": "blur(16px)"}, {"opacity": 1, "scale": 1, "filter": "blur(0px)"}, 0.5, "power3.out"),
         "rise": ({"opacity": 0, "y": 30}, {"opacity": 1, "y": 0}, 0.6, "power3.out"),
         "left": ({"opacity": 0, "x": -60}, {"opacity": 1, "x": 0}, 0.65, "power3.out"),
         "right": ({"opacity": 0, "x": 60}, {"opacity": 1, "x": 0}, 0.65, "power3.out"),
         "depth": ({"opacity": 0, "z": -700, "rotationY": 16, "filter": "blur(10px)"}, {"opacity": 1, "z": 0, "rotationY": 0, "filter": "blur(0px)"}, 0.85, "power3.out"),
         "settle": ({"opacity": 0, "scale": 0.9}, {"opacity": 1, "scale": 1}, 0.55, "back.out(1.25)"),
         "fade": ({"opacity": 0}, {"opacity": 1}, 0.4, "power2.out")}[fx if DEPTH or fx != "depth" else "focus"]
    to = dict(F[1]);
    if stagger: to["stagger"] = stagger
    tw(sel, max(0, t - lead), d or F[2], to, dict(F[0]), F[3])


def leave(sel, t, d=0.3): tw(sel, t - d, d, {"opacity": 0}, None, "power2.in")


def vid(src, t, dur, media_start=0, style=""):
    """A video inside a scene (real footage of a person, a screen recording). Shown whole, muted."""
    return f'<video class="clip" src="{src}" muted playsinline data-start="%%{t:.3f}%%" data-duration="{dur:.3f}" data-media-start="{media_start}" data-track-index="%%TRK%%" style="{style}"></video>'


# ---------------------------------------------------------------- people in pictures: find the faces, crop around them, never through them
FACES_BIN = os.path.expanduser("@@WORK_ROOT@@/.bin/faces")
FACES_SRC = os.path.expanduser("~/.claude/skills/educational-youtube-editor/scripts/faces.swift")


def faces(src):
    """{"w","h","faces":[[x,y,w,h],...]} for an image in the project (normalised, origin top-left). Apple Vision; cached in faces.json."""
    if src in _FACES: return _FACES[src]
    import subprocess
    path = os.path.join(ROOT, src); info = {"w": 0, "h": 0, "faces": []}
    try:
        if not os.path.exists(FACES_BIN):
            os.makedirs(os.path.dirname(FACES_BIN), exist_ok=True); subprocess.run(["swiftc", "-O", FACES_SRC, "-o", FACES_BIN], check=True, capture_output=True)
        got = json.loads(subprocess.check_output([FACES_BIN, os.path.realpath(path)], timeout=60)); info = next(iter(got.values()), info)
    except Exception as e:
        print(f"  ! face detection failed for {src} ({e}): LOOK at this image's crop yourself")
    if not info["w"]:
        try:
            from PIL import Image; info["w"], info["h"] = Image.open(path).size
        except Exception: pass
    _FACES[src] = info; json.dump(_FACES, open(f"{ROOT}/faces.json", "w")); return info


def ratio_of(src, lo=0.5, hi=2.4):
    """The image's own shape (so a frame can match the picture instead of cropping it)."""
    f = faces(src); return min(hi, max(lo, f["w"] / f["h"])) if f["w"] and f["h"] else 16 / 9


def fit(src, w, h, pos=None, sid=""):
    """How an image may sit in a w x h box without cutting anyone's face. Returns (mode, css object-position).
    cover   the box is filled and the crop window is moved so every face (with headroom) is inside it
    contain the faces cannot all fit a filling crop: show the WHOLE image, with a blurred copy of itself behind it.
    Every use is recorded for the crop review (review/crops-*.jpg)."""
    f = faces(src); iw, ih = f["w"] or w, f["h"] or h; sc = max(w / iw, h / ih); vw, vh = min(1, w / (iw * sc)), min(1, h / (ih * sc))
    mode, x0, y0 = "cover", (1 - vw) / 2, (1 - vh) / 2
    if pos:
        px, py = [float(v.strip("%")) / 100 for v in pos.split()]; x0, y0 = (1 - vw) * px, (1 - vh) * py
    if f["faces"]:
        L = min(a - 0.35 * c for a, b, c, d in f["faces"]); R = max(a + 1.35 * c for a, b, c, d in f["faces"])
        T = min(b - 0.55 * d for a, b, c, d in f["faces"]); B = max(b + 1.4 * d for a, b, c, d in f["faces"])
        L, T, R, B = max(0, L), max(0, T), min(1, R), min(1, B)
        if R - L <= vw + 1e-6 and B - T <= vh + 1e-6:
            x0 = min(max(0, (L + R) / 2 - vw / 2), 1 - vw); x0 = min(x0, L); x0 = max(x0, R - vw)
            y0 = min(max(0, (T + B) / 2 - vh / 2), 1 - vh); y0 = min(y0, T); y0 = max(y0, B - vh)
        else: mode, x0, y0, vw, vh = "contain", 0, 0, 1, 1
    ok = all(a >= x0 - 1e-3 and b >= y0 - 1e-3 and a + c <= x0 + vw + 1e-3 and b + d <= y0 + vh + 1e-3 for a, b, c, d in f["faces"])
    USES.append({"scene": sid, "src": src, "box": [round(w), round(h)], "mode": mode, "window": [round(x0, 4), round(y0, 4), round(vw, 4), round(vh, 4)], "faces": len(f["faces"]), "ok": ok})
    px = 50 if vw >= 1 - 1e-6 else 100 * x0 / (1 - vw); py = 50 if vh >= 1 - 1e-6 else 100 * y0 / (1 - vh)
    return mode, f"{px:.1f}% {py:.1f}%"


def img(src, w, h, pos=None, sid="", extra=""):
    """An <img> for a w x h box with faces protected (use this, never a bare object-fit:cover on a photo of people)."""
    mode, op = fit(src, w, h, pos, sid)
    if mode == "cover": return f'<img src="{src}" style="display:block;width:100%;height:100%;object-fit:cover;object-position:{op};{extra}">'
    return (f'<img src="{src}" style="position:absolute;inset:-6%;width:112%;height:112%;object-fit:cover;filter:blur(28px) brightness(.55) saturate(1.1)">'
            f'<img src="{src}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:contain;{extra}">')


def brand_asset(name):
    """The creator's own brand image, if they gave one at setup: "logo" (square logo), "wordmark" (wide wordmark for dark
    backgrounds) or "avatar" (profile picture). Returns the path to use in a scene ("assets/logo.png") or None, so a build
    can do:  logo = E.brand_asset("logo");  if logo: ...   Nothing in the engine or the kit needs these files."""
    f = {"logo": "logo.png", "wordmark": "wordmark.png", "avatar": "avatar.jpg"}.get(name, name)
    return f"assets/{f}" if ROOT and os.path.exists(f"{ROOT}/assets/{f}") else None


def watermark(which="logo", corner="tr", size=56, opacity=0.8, margin=44):
    """A small brand mark in one corner for the WHOLE video. Only when the creator's setup asks for a constant watermark
    (the pack default is none). Call once in build.py. corner = tl | tr | bl | br. Does nothing when they gave no logo."""
    src = brand_asset(which)
    if not src: print(f"  note: no {which} file in assets/ (none given at setup), so no watermark is drawn"); return
    WM.update(src=src, corner=corner, size=size, opacity=opacity, margin=margin)


def punch(a, b, why, scale=None):
    """An occasional punch-in on the speaker: a hard cut-in at `a`, back out at `b`. Only with a reason: an important statement,
    a strong opinion, a reveal, a change of thought, an emotional moment, a key takeaway. Put `a` on a cut or the first
    word of the line (E.snap / E.w). The speaker must be full screen for the whole of it."""
    why or sys.exit("E.punch needs its reason (important statement / strong opinion / reveal / change of thought / emotional moment / key takeaway)")
    b - a >= 1.2 or sys.exit(f"punch at {a:.1f}s is {b - a:.1f}s long: too short to read as intentional")
    PU.append({"a": fr(a), "b": fr(b), "why": why, "scale": scale or PUNCH})


# ---------------------------------------------------------------- geometry
def cam_rect(kind, side="left", style="edge"):
    """Where the speaker sits: (window x, y, w, h, radius, video x, y, scale). side = the side the GRAPHIC is on.
    split = the real footage fills its half of the frame edge to edge, cropped naturally around the face. No card, no rounding, no frame."""
    if kind == "split":
        ww = 640 if style == "portrait" else W // 2          # portrait = a near 9:16 column (the speaker's own footage, edge to edge, no card), the graphic gets the rest
        x = (W - ww if side == "left" else 0) if style == "portrait" else (W // 2 if side == "left" else 0)
        vx = min(0, max(ww - W, ww / 2 - FACE[0]))
        return x, 0, ww, H, 0, round(vx, 1), 0, 1
    if kind == "panel": return 0, 0, W, H, 0, (PANEL_SHIFT if side == "left" else -PANEL_SHIFT), 0, 1
    return 0, 0, W, H, 0, 0, 0, 1


def region(kind, side="left", style="edge", zone=None):
    """The rectangle a piece may use in each state: (x, y, w, h)."""
    if kind == "split":
        if style == "portrait": return (40 if side == "left" else 640 + 40), 60, W - 640 - 80, 960
        return (50 if side == "left" else 1010), 60, 860, 960
    if kind == "panel": x, y, ww, hh = REGION["panel"]; return (x if side == "left" else W - PANEL_W + x), y, ww, hh
    if kind == "float":
        z = zone or side
        if z == "bottom": return 160, 770, 1600, 250
        if z == "top": return 160, 36, 1600, 110
        x0, x1 = (70, FACE[0] - 300) if z == "left" else (FACE[0] + 300, W - 70)
        if x1 - x0 < 400:
            raise SystemExit(f"float on the {z}: only {x1 - x0}px beside them (face x {FACE[0]}). Use E.panel or E.split for this moment, or float on the other side.")
        return x0, 120, x1 - x0, 840
    return REGION["full"]


# ---------------------------------------------------------------- scenes
FILL = {"full": 0.84, "split": 0.9, "panel": 1.0, "float": 1.0}      # how much of its region a piece may fill (full-screen graphics sit at ~84%, never edge to edge)
CAP = {"full": 2.2, "split": 1.5, "panel": 1.25, "float": 1.15}      # and how far it may be enlarged beyond its design size


def _scene(kind, piece, why, score, side="left", style="edge", zone=None, cut=False, dim=0.0, cap=None, fill=None, tier=None, over_doc=False):
    why in WHY or sys.exit(f"scene {piece['id']}: why must be one of {WHY} (every visual needs a reason to exist)")
    any(s["id"] == piece["id"] for s in SC) and sys.exit(f"duplicate scene id {piece['id']}")
    a, b = piece["a"], min(piece["b"], DUR)
    b - a >= 0.8 or sys.exit(f"scene {piece['id']} is {b - a:.2f}s long: too short to read")
    SC.append(dict(piece, kind=kind, a=a, b=b, why=why, score=score, side=side, style=style, zone=zone, cut=cut, dim=dim, cap=cap or CAP[kind], fill=fill or FILL[kind], tier=tier, over_doc=over_doc))


def float_(piece, why, score=3, side="left", zone=None, dim=0.0, **k): _scene("float", piece, why, score, side=side, zone=zone, dim=dim, **k)
def panel(piece, why, score=3, side="left", **k): _scene("panel", piece, why, score, side=side, **k)
def split(piece, why, score=4, side="left", cut=False, style="edge", **k):
    style in ("edge", "portrait") or sys.exit("split: the speaker is never placed in a card, rounded box or frame. The split is a 50/50 division, or style='portrait' (a near 9:16 column), edge to edge.")
    _scene("split", piece, why, score, side=side, style=style, cut=cut, **k)
def full(piece, why, score=5, cut=False, **k): _scene("full", piece, why, score, cut=cut, **k)


def piece(sid, a, b, body, size, comp, variant="", text="", css_=""):
    """What a kit component returns. size = its design size; the engine scales it to fit the state's region."""
    if css_: css(css_)
    return {"id": sid, "a": a, "b": b, "body": body, "size": size, "comp": comp, "variant": variant, "text": text}


# ---------------------------------------------------------------- chunks
def _busy(t, pad=1.2): return any(s["a"] - pad <= t <= s["b"] + pad for s in SC)


def chunks(target=None):
    """Split points where nothing is on screen (the speaker is simply talking), about every `target` seconds, on whole frames."""
    target = target or float(P.get("chunk", 240)); pts = [0.0]
    while DUR - pts[-1] > target * 1.4:
        want = pts[-1] + target; best = None
        for pad in (1.2, 0.12):                      # first a real pause in the graphics; failing that, any instant between two scenes
            for k in range(0, int(target * 0.45 * 8)):
                for t in (want + k / 8, want - k / 8):
                    if pts[-1] + 20 < t < DUR - 20 and not _busy(t, pad): best = t; break
                if best: break
            if best: break
        pts.append(fr(best if best else want))
    return [(pts[i], pts[i + 1] if i + 1 < len(pts) else fr(DUR)) for i in range(len(pts))]


# ---------------------------------------------------------------- build
BASE_CSS = r"""
@font-face{font-family:"HelvB";src:@@FONT_MAIN_BOLD_SRC@@;font-weight:700}
@font-face{font-family:"HelvR";src:@@FONT_MAIN_REGULAR_SRC@@;font-weight:400}
@font-face{font-family:"Ivy";src:@@FONT_ACCENT_SRC@@;font-style:italic;font-weight:400 700}
:root{--o:__ACCENT__;--ink:@@BG@@;--paper:@@PAPER@@;--grey:@@GREY@@;--line:rgba(242,240,236,.14);--good:#2FA65A;--bad:#B3261E;--r:__R__px;--rs:__RS__px;
--sh:0 34px 90px rgba(0,0,0,.55),0 8px 24px rgba(0,0,0,.35);--sf:-apple-system,"SF Pro Display","SF Pro Text","HelvR",Helvetica,sans-serif}
*{box-sizing:border-box}
html,body{margin:0;padding:0;width:100%;height:100%;overflow:hidden;background:#000;font-family:"HelvR",Helvetica,Arial,sans-serif;color:var(--paper)}
#stage{position:relative;width:1920px;height:1080px;overflow:hidden;background:#000}
#bg,#fgbg{position:absolute;inset:0;background:radial-gradient(90% 70% at 22% 118%,rgba(@@ACCENT_RGB@@,.42) 0%,rgba(@@ACCENT_RGB@@,.15) 36%,rgba(@@BG_RGB@@,0) 72%),radial-gradient(60% 50% at 96% -8%,rgba(@@ACCENT_RGB@@,.16),rgba(@@BG_RGB@@,0) 70%),@@BG@@}
#bg::after,#fgbg::after{content:"";position:absolute;inset:0;opacity:.05;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='1.1' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .9 0'/></filter><rect width='220' height='220' filter='url(%23n)'/></svg>")}
#fgbg{opacity:0}
#cam{position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:hidden;background:#000}
#camv{position:absolute;left:0;top:0;width:1920px;height:1080px;transform-origin:0 0}
#camp{width:1920px;height:1080px;transform-origin:__FX__px __FY__px}
#camz{width:1920px;height:1080px;transform-origin:__FX__px __FY__px}
#camz video{display:block;width:1920px;height:1080px;object-fit:cover}
#dim{position:absolute;inset:0;background:@@BG@@;opacity:0}
#panelL,#panelR{position:absolute;top:0;width:800px;height:1080px;background:var(--ink);overflow:hidden;box-shadow:0 0 90px rgba(0,0,0,.5)}
#panelL{left:0;transform:translateX(-860px)}#panelR{right:0;transform:translateX(860px)}
#panelL::before,#panelR::before{content:"";position:absolute;inset:0;background:radial-gradient(110% 60% at 30% 112%,rgba(@@ACCENT_RGB@@,.46) 0%,rgba(@@ACCENT_RGB@@,.16) 36%,rgba(@@BG_RGB@@,0) 78%)}
.sc{position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none}
.sc .in{position:absolute;inset:0;opacity:0}
.pc{position:absolute;transform-origin:50% 50%}
.pc>.box{position:relative;width:100%;height:100%}
.h{opacity:0}
.p3{perspective:1700px;transform-style:preserve-3d}.p3 *{transform-style:preserve-3d}
.btgrad{position:absolute;left:0;right:0;bottom:0;height:520px;background:linear-gradient(to top,rgba(@@BG_RGB@@,.92) 0%,rgba(@@BG_RGB@@,.66) 36%,rgba(@@BG_RGB@@,.22) 70%,rgba(@@BG_RGB@@,0) 100%)}
.B{font-family:"HelvB";letter-spacing:-.04em}
i.a{font-family:"Ivy",serif;font-style:italic;font-weight:400;color:var(--o);letter-spacing:-.02em}
.lbl{font-family:"HelvB";font-size:21px;letter-spacing:.22em;text-transform:uppercase;color:var(--grey)}
.card{border-radius:var(--r);background:#14110f;border:1px solid var(--line);box-shadow:var(--sh);overflow:hidden}
.glass{border-radius:var(--r);background:linear-gradient(160deg,rgba(255,255,255,.14),rgba(255,255,255,.04));-webkit-backdrop-filter:blur(26px) saturate(150%);backdrop-filter:blur(26px) saturate(150%);border:1px solid rgba(255,255,255,.2);box-shadow:inset 0 1px 0 rgba(255,255,255,.34),var(--sh)}
"""

RUNTIME = r"""
(function(){
  const tl = gsap.timeline({paused:true});              // inner clock: starts PRE seconds before this chunk
  const root = gsap.timeline({paused:true});            // what HyperFrames seeks: 0 .. chunk length
  const PRE = __PRE__, D = __D__;
  const TW = __TW__, CN = __CN__;
  TW.forEach(([sel,t,d,to,from,ease]) => {
    const els = document.querySelectorAll(sel); if(!els.length) return;
    if(d === 0){ tl.set(els, to, t); return; }
    const v = Object.assign({}, to, {duration:d, ease:ease});
    if(from) tl.fromTo(els, from, Object.assign(v, {immediateRender:false}), t); else tl.to(els, v, t);
  });
  CN.forEach(([sel,t,from,to,d,pre,suf,dec]) => {
    const el = document.querySelector(sel); if(!el) return; const o = {v:from};
    const f = (x) => pre + Number(x).toLocaleString("en-US",{minimumFractionDigits:dec,maximumFractionDigits:dec}) + suf;
    tl.to(o, {v:to, duration:d, ease:"power2.out", onUpdate:() => { el.textContent = f(o.v); }}, t);
  });
  tl.set({}, {}, PRE + D);
  root.fromTo(tl, {time: PRE}, {time: PRE + D, duration: D, ease: "none", immediateRender: true}, 0);
  window.__timelines = window.__timelines || {}; window.__timelines["__ID__"] = root;
})();
"""


def _cam_tweens():
    """The speaker glides between states: the camera window and the footage inside it move together."""
    blocks = sorted([s for s in SC if s["kind"] in ("split", "panel")], key=lambda s: s["a"]); runs = []
    for s in blocks:
        g = (s["kind"], s["side"], s["style"])
        if runs and runs[-1]["g"] == g and s["a"] - runs[-1]["b"] < 1.0: runs[-1]["b"] = max(runs[-1]["b"], s["b"])
        else: runs.append({"g": g, "a": s["a"], "b": s["b"], "cut": s["cut"]})
    home = cam_rect("head")
    for i, r in enumerate(runs):
        x, y, ww, hh, rad, vx, vy, sc = cam_rect(*r["g"]); hx = home
        nxt = runs[i + 1] if i + 1 < len(runs) and runs[i + 1]["a"] - r["b"] < 1.0 else None
        if r["cut"]:
            setp("#cam", max(0, r["a"] - 0.004), {"left": x, "top": y, "width": ww, "height": hh, "borderRadius": rad}); setp("#camv", max(0, r["a"] - 0.004), {"x": vx, "y": vy, "scale": sc})
        else:
            t0 = max(0, r["a"] - 0.4)
            tw("#cam", t0, 0.8, {"left": x, "top": y, "width": ww, "height": hh, "borderRadius": rad}, None, "power3.inOut")
            tw("#camv", t0, 0.8, {"x": vx, "y": vy, "scale": sc}, None, "power3.inOut")
        if r["g"][0] == "panel":
            pid = "#panelL" if r["g"][1] == "left" else "#panelR"; off = -860 if r["g"][1] == "left" else 860
            tw(pid, max(0, r["a"] - 0.4), 0.8, {"x": 0}, {"x": off}, "power3.inOut"); tw(pid, r["b"] - 0.1, 0.75, {"x": off}, None, "power3.inOut")
        if not nxt:
            if r["cut"]:
                setp("#cam", r["b"] - 0.004, {"left": 0, "top": 0, "width": W, "height": H, "borderRadius": 0}); setp("#camv", r["b"] - 0.004, {"x": 0, "y": 0, "scale": 1})
            else:
                tw("#cam", r["b"] - 0.1, 0.75, {"left": 0, "top": 0, "width": W, "height": H, "borderRadius": 0}, None, "power3.inOut")
                tw("#camv", r["b"] - 0.1, 0.75, {"x": 0, "y": 0, "scale": 1}, None, "power3.inOut")
    for s in SC:
        if s["kind"] == "full":
            if s["cut"]: setp("#fgbg", max(0, s["a"] - 0.004), {"opacity": 1}); setp("#fgbg", s["b"] - 0.004, {"opacity": 0})
            else: tw("#fgbg", max(0, s["a"] - 0.15), 0.4, {"opacity": 1}, None, "power2.out"); tw("#fgbg", s["b"] - 0.3, 0.4, {"opacity": 0}, None, "power2.inOut")
        if s["kind"] == "float" and s["dim"]:
            tw("#dim", max(0, s["a"] - 0.2), 0.5, {"opacity": s["dim"]}, None, "power2.out"); tw("#dim", s["b"] - 0.35, 0.45, {"opacity": 0}, None, "power2.inOut")
    for s in SC:
        for da, db in DOCS:
            if s.get("over_doc"): break      # an explicit takeover the creator asked for (for example a full-screen preview of what the video covers)
            if s["a"] < db - 0.02 and s["b"] > da + 0.02: sys.exit(f"scene {s['id']} ({s['a']:.2f}-{s['b']:.2f}s) overlaps the document section {da:.2f}-{db:.2f}s: graphics only go where the speaker is full screen")
            if s["kind"] in ("split", "panel") and not s["cut"] and (da - 0.75 < s["b"] <= da + 0.001 or db - 0.001 <= s["a"] < db + 0.45):
                sys.exit(f"scene {s['id']}: a split / panel that touches a document section must use cut=True (its glide would run into the document at {da:.2f}-{db:.2f}s)")
    covers = []
    items = [{"a": x["a"], "b": x["b"], "full": x["kind"] == "full", "hard": False} for x in SC if x["kind"] in ("split", "panel", "full")] + [{"a": da, "b": db, "full": True, "hard": True} for da, db in DOCS]
    for x in sorted(items, key=lambda s: s["a"]):
        if covers and x["a"] - covers[-1]["b"] < 1.0:
            if x["b"] >= covers[-1]["b"]: covers[-1].update(b=x["b"], full_out=x["full"], hard_b=x["hard"])
        else: covers.append({"a": x["a"], "b": x["b"], "full": x["full"], "full_out": x["full"], "hard_a": x["hard"], "hard_b": x["hard"]})
    edges = [None] + covers + [None]; GAPS.clear(); k = 0
    for prev, nxt in zip(edges, edges[1:]):
        ga = prev["b"] if prev else 0.0; gb = nxt["a"] if nxt else DUR
        if gb - ga < 4.0: continue
        GAPS.append((ga, gb))
        if not DRIFT[1]: continue
        L = gb - ga; amt = round(min(DRIFT[1], max(DRIFT[0], 0.0015 * L)), 4); d = min(L, DRIFT_SECONDS)
        way = OPEN if k % 2 == 0 else ("out" if OPEN == "in" else "in"); k += 1
        if way == "out":                                # arrive already slightly in (set while the creator is hidden or mid-glide), then ease out over the stretch
            if not prev: setp("#camz", 0, {"scale": 1 + amt})
            elif prev["hard_b"]: setp("#camz", prev["b"] - 0.004, {"scale": 1 + amt})     # on the exact frame the document section ends
            elif prev["full_out"]: setp("#camz", prev["b"] - 0.4, {"scale": 1 + amt})
            else: tw("#camz", prev["b"] - 0.1, 0.75, {"scale": 1 + amt}, None, "power3.inOut")
            tw("#camz", ga + (0.7 if prev and not prev["full_out"] else 0), d - (0.7 if prev and not prev["full_out"] else 0), {"scale": 1}, None, "sine.inOut")
        else:
            tw("#camz", ga, d - (0.1 if nxt and nxt["hard_a"] else 0), {"scale": 1 + amt}, None, "sine.inOut")
            if nxt and nxt["hard_a"]: setp("#camz", nxt["a"] - 0.004, {"scale": 1})          # back to 100% on the exact frame the document section starts
            elif nxt and nxt["full"]: setp("#camz", nxt["a"] + 0.3, {"scale": 1})
            elif nxt: tw("#camz", nxt["a"] - 0.4, 0.8, {"scale": 1}, None, "power3.inOut")
    for p in PU:
        hit = next((c for c in covers if p["a"] < c["b"] + (0 if c["full_out"] else 0.7) - 0.02 and p["b"] > c["a"] - (0 if c["full"] else 0.4) + 0.02), None)
        if hit: sys.exit(f"punch {p['a']:.1f}-{p['b']:.1f}s runs into the split / panel / full-screen scene at {hit['a']:.1f}-{hit['b']:.1f}s: punch-ins are for when the creator is full screen")
        setp("#camp", max(0, p["a"] - 0.004), {"scale": p["scale"]}); setp("#camp", p["b"] - 0.004, {"scale": 1})   # just ahead of the frame time, so a punch that meets a document section switches on the same frame


GAPS = []


def _scene_html(s, off, trk):
    rx, ry, rw, rh = region(s["kind"], s["side"], s["style"], s["zone"]); w_, h_ = s["size"]; k = min(min(rw / w_, rh / h_) * s["fill"], s["cap"])
    body = re.sub(r"%%([\d.]+)%%", lambda m: f"{float(m.group(1)) - off:.3f}", s["body"])
    while "%%TRK%%" in body: _trk[0] += 1; body = body.replace("%%TRK%%", str(40 + _trk[0]), 1)
    grad = '<div class="btgrad"></div>' if s["kind"] == "float" and s["zone"] == "bottom" else ""
    return (f'<div class="clip sc k-{s["kind"]}" id="sc-{s["id"]}" data-start="{s["a"] - off:.3f}" data-duration="{s["b"] - s["a"]:.3f}" data-track-index="{trk}">'
            f'<div class="in" id="in-{s["id"]}">{grad}<div class="pc" style="left:{rx + rw / 2 - w_ / 2:.0f}px;top:{ry + rh / 2 - h_ / 2:.0f}px;width:{w_}px;height:{h_}px;transform:scale({k:.4f})"><div class="box">{body}</div></div></div></div>\n')


def build(chunk=None, quiet=False):
    """python3 build.py            -> audit + writes index.html for chunk 0
       python3 build.py --chunk 2  -> index.html for chunk 2 (the render script loops over them)
       python3 build.py --list     -> prints the chunk table"""
    if "--chunk" in sys.argv: chunk = int(sys.argv[sys.argv.index("--chunk") + 1])
    SC.sort(key=lambda s: s["a"])
    for s in SC:
        o, c = s["body"].count("<div"), s["body"].count("</div>")
        o == c or sys.exit(f"unbalanced divs in scene {s['id']}: {o} open, {c} close")
        tw(f"#in-{s['id']}", max(0, s["a"] - 0.004) if s["cut"] else max(0, s["a"] - 0.05), 0.001 if s["cut"] else 0.35, {"opacity": 1}, None, "power2.out")
        if not s["cut"]: tw(f"#in-{s['id']}", s["b"] - 0.3, 0.28, {"opacity": 0}, None, "power2.in")
        else: setp(f"#in-{s['id']}", s["b"] - 0.004, {"opacity": 0})
    _cam_tweens(); CH = chunks()
    json.dump({"chunks": CH, "sfx": sorted(SFX), "dur": DUR}, open(f"{ROOT}/render.json", "w"), indent=1)
    rep = report(quiet=quiet or "--chunk" in sys.argv)
    if "--list" in sys.argv:
        for i, (a, b) in enumerate(CH): print(f"chunk {i}: {a:8.2f} -> {b:8.2f}  ({b - a:.1f}s, {sum(1 for s in SC if a <= s['a'] < b)} scenes)")
        return rep
    ci = chunk or 0; a0, a1 = CH[ci]; d = round(a1 - a0, 4); _trk[0] = 0
    inside = [s for s in SC if s["a"] < a1 and s["b"] > a0]; ends = {}; html = ""
    for s in inside:
        trk = next(t for t in range(10, 40) if ends.get(t, -1) <= s["a"]); ends[trk] = s["b"] + 0.02
        html += _scene_html(dict(s, a=max(s["a"], a0), b=min(s["b"], a1)), a0, trk)
    pre = min(3.0, a0); off = a0 - pre             # the page's clock starts `pre` seconds before the chunk, so a move that is under way at the join carries on mid-flight
    carry = {}                                       # state left behind by everything that finished before that
    for sel, t, dd, to, frm, ease in sorted(TW, key=lambda x: x[1] + x[2]):
        if t + dd <= off: carry.setdefault(sel, {}).update({k: v for k, v in to.items() if k != "stagger"})
    T = [[sel, 0, 0, to, None, "none"] for sel, to in carry.items() if sel.startswith(("#cam", "#fgbg", "#dim", "#panel")) or any(sel.startswith(f"#{x['id']}-") or sel == f"#in-{x['id']}" for x in inside)]
    # a move already under way when the page clock starts runs only its REMAINING time (starting it at 0 with its full length makes it overrun its true end: a camera drift then leaks into the next document section)
    T += sorted([[sel, round(max(0, t - off), 3), (dd if t >= off else round(max(0.001, dd - (off - t)), 3)), to, (frm if t >= off else None), ease] for sel, t, dd, to, frm, ease in TW if t + dd > off and t < a1], key=lambda x: x[1])
    C = [[sel, round(t - off, 3), *rest] for sel, t, *rest in CN if off <= t < a1]
    cid = f"{P.get('slug', 'yt')}-{ci}"
    cssx = (BASE_CSS.replace("__ACCENT__", P.get("accent", "@@ACCENT@@")).replace("__R__", str(RADIUS)).replace("__RS__", str(RADIUS_S))
            .replace("__FX__", str(FACE[0])).replace("__FY__", str(FACE[1])) + "\n".join(dict.fromkeys(XCSS)))
    js = RUNTIME.replace("__TW__", json.dumps(T)).replace("__CN__", json.dumps(C)).replace("__ID__", cid).replace("__PRE__", f"{pre:.4f}").replace("__D__", f"{d:.4f}")
    wm = ""
    if WM:
        v, h_ = ("top" if WM["corner"][0] == "t" else "bottom"), ("left" if WM["corner"][1] == "l" else "right")
        wm = f'  <img id="wm" src="{WM["src"]}" style="position:absolute;{v}:{WM["margin"]}px;{h_}:{WM["margin"]}px;height:{WM["size"]}px;opacity:{WM["opacity"]};z-index:60;pointer-events:none">\n'
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><style>{cssx}</style></head>
<body>
<div id="stage" data-composition-id="{cid}" data-start="0" data-duration="{d}" data-fps="{round(FPS)}" data-width="1920" data-height="1080">
  <div id="bg"></div>
  <div id="cam"><div id="camv"><div id="camp"><div id="camz"><video id="camvid" class="clip" src="assets/cam.mp4" muted playsinline data-start="0" data-duration="{d}" data-media-start="{a0 + (0.3 / FPS if a0 else 0):.4f}" data-track-index="1"></video></div></div></div></div>
  <div id="dim"></div><div id="fgbg"></div><div id="panelL"></div><div id="panelR"></div>
{html}{wm}  <script src="assets/gsap.min.js"></script>
  <script>{js}</script>
</div>
</body></html>
"""
    open(f"{ROOT}/index.html", "w").write(page)
    if not quiet: print(f"index.html = chunk {ci} of {len(CH)} ({a0:.2f} -> {a1:.2f}, {len(inside)} scenes). Snapshot times are chunk-local: t - {a0:.2f}")
    return rep


# ---------------------------------------------------------------- the audit (the quality check, as numbers)
def report(quiet=False):
    out = []; warn = lambda m: out.append("  ! " + m); mins = max(DUR / 60, 0.01)
    t_of = lambda kinds: sum(s["b"] - s["a"] for s in SC if s["kind"] in kinds)
    covered = t_of(("full",)); seen = 100 * (1 - covered / DUR); share = {k: 100 * t_of((k,)) / DUR for k in ("float", "panel", "split", "full")}
    head = 100 - sum(share.values())
    intro = [s for s in SC if s["a"] < INTRO]; rest = [s for s in SC if s["a"] >= INTRO]
    di = len(intro) / (min(INTRO, DUR) / 60); dr = len(rest) / max((DUR - INTRO) / 60, 0.01) if DUR > INTRO else 0
    real = [s["a"] for s in SC if s["comp"] not in ("title", "tracker")] + [p["a"] for p in PU]
    if not real or min(real) > 3.0: warn(f"no meaningful visual change in the first 3 s (first is at {min(real):.1f}s): cut to a motion graphic, a split or a punch-in that supports what the creator is saying" if real else "no visual change at all in the video")
    ev = sorted({0.0} | {x for s in SC for x in ([s["a"]] + ([s["b"]] if s["kind"] != "float" else []))} | {x for p in PU for x in (p["a"], p["b"])}
                | {round(t + LEAD, 2) for sel, t, dd, to, frm, ease in TW for s in SC if s["a"] < RET and sel.startswith((f"#{s['id']}-", f".{s['id']}-")) and dd > 0})   # a graphic that keeps building counts as development
    ev = [x for x in ev if x <= min(RET, DUR)] + [min(RET, DUR)]
    for x, y in zip(ev, ev[1:]):
        if y - x > 5.2: warn(f"opening: nothing changes on screen for {y - x:.1f}s ({x:.1f}s -> {y:.1f}s). In the first {RET}s something should develop every 2-5 s: a graphic if one helps, otherwise a punch-in or a change of composition")
    for p, q in zip(PU, PU[1:]):
        if q["a"] - p["b"] < 8 and q["a"] > RET: warn(f"punch-ins at {p['a']:.0f}s and {q['a']:.0f}s are back to back: they stop feeling motivated")
    if len([p for p in PU if p["a"] > RET]) > 1.5 * max(1, (DUR - RET) / 60): warn(f"{len(PU)} punch-ins is more than about 1.5 a minute: use them for the lines that matter")
    for u in USES:
        if not u["ok"]: warn(f"{u['scene']}: {u['src']} is cropped THROUGH A FACE. Change the frame's shape, scale it down or use another image")
        elif u["mode"] == "contain": out.append(f"    note {u['scene']}: {u['src']} shown whole on a blurred extension (its faces do not fit a {u['box'][0]}x{u['box'][1]} crop). A frame in the image's own shape may look better")
    if len(intro) < 5 and DUR > INTRO: warn(f"only {len(intro)} scenes in the first {INTRO}s: the intro gets the highest density (aim for 6-10)")
    if dr and di < dr * 1.3: warn(f"intro density ({di:.1f}/min) is not clearly above the body ({dr:.1f}/min)")
    if seen < 62: warn(f"the creator is on screen only {seen:.0f}% of the time: long-form needs their face for connection (aim for 70%+)")
    if dr > 9: warn(f"body density {dr:.1f} scenes/min reads like a reel: let it breathe (roughly 3-7/min, in waves)")
    if DUR > 120 and dr < 1.5: warn(f"body density {dr:.1f} scenes/min: long stretches may be under-edited")
    last = {}
    for i, s in enumerate(SC):
        key = (s["comp"], s["variant"])
        if key in last and s["a"] - last[key] < SAME_LOOK_GAP and s["comp"] not in ("tracker", "term", "section"):
            warn(f"{s['id']} at {s['a']:.0f}s repeats {s['comp']}/{s['variant']} used {s['a'] - last[key]:.0f}s earlier: pick another variant or component")
        last[key] = s["b"]
        if i >= 2 and s["kind"] == SC[i - 1]["kind"] == SC[i - 2]["kind"] and s["kind"] != "float" and s["a"] - SC[i - 2]["a"] < 60:
            warn(f"three {s['kind']} scenes in a row around {s['a']:.0f}s: vary the state")
        if "—" in s["body"] or "–" in s["body"]: warn(f"{s['id']}: em/en dash in on-screen text (it reads as machine-written). Use a comma, full stop or middle dot")
        nw = len(s.get("text", "").split())
        if nw > 14 and s["comp"] not in ("quote", "social", "browser", "doc"): warn(f"{s['id']}: {nw} words of text on screen. Show the idea; do not repeat the narration")
        if s["score"] <= 2 and s["kind"] in ("full", "split"): warn(f"{s['id']}: low-priority moment (score {s['score']}) given a {s['kind']} treatment: a float or nothing may be enough")
        if s["tier"] == 6: warn(f"{s['id']}: stock imagery. Is there a specific real example instead?")
    gaps = []; cur = 0.0
    for s in SC:
        if s["a"] - cur > 75: gaps.append((cur, s["a"]))
        cur = max(cur, s["b"])
    for a, b in gaps: warn(f"{b - a:.0f}s with nothing on screen ({a:.0f}s -> {b:.0f}s). Fine for a story or a nuanced point; otherwise check for a missed example or framework")
    vis = [j for j in CUTS if j.get("big") and not any(s["kind"] == "full" and s["a"] - 0.05 <= j["t"] <= s["b"] for s in SC)
           and not any(abs(j["t"] - x) < 0.09 for s in SC if s["kind"] in ("split", "full") for x in (s["a"], s["b"]))
           and not any(abs(j["t"] - x) < 0.09 for p in PU for x in (p["a"], p["b"]))]
    comps = sorted({s["comp"] for s in SC}); texty = sum(1 for s in SC if s["comp"] in ("emph", "rows", "quote", "term"))
    if SC and texty / len(SC) > 0.4: warn(f"{100 * texty // len(SC)}% of scenes are text-led: more diagrams, real examples and illustrations")
    realn = sum(1 for s in SC if s["tier"] in (1, 2, 3))
    head_line = (f"{DUR / 60:.1f} min | {len(SC)} scenes ({len(SC) / mins:.1f}/min; intro {di:.1f}/min, body {dr:.1f}/min) | the creator is visible {seen:.0f}% | "
                 f"head {head:.0f}% float {share['float']:.0f}% panel {share['panel']:.0f}% split {share['split']:.0f}% full {share['full']:.0f}% | "
                 f"{len(comps)} component types | {realn} real-world assets | {len(PU)} punch-ins | {sum(1 for u in USES if u['faces'])} images with people ({sum(1 for u in USES if not u['ok'])} cut) | {len(vis)} big jump cuts left visible on the creator")
    A = {"summary": head_line, "warnings": [o[4:] for o in out], "crops": USES, "punches": PU, "visible_big_cuts": [j["t"] for j in vis][:60],
         "scenes": [{k: s[k] for k in ("id", "a", "b", "kind", "comp", "variant", "why", "score", "tier")} for s in SC]}
    json.dump(A, open(f"{ROOT}/audit.json", "w"), indent=1)
    if not quiet:
        print("AUDIT  " + head_line); print("\n".join(out) if out else "  no warnings")
    return A
