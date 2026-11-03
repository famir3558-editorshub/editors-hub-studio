#!/usr/bin/env python3
"""youtube-clips engine: one HyperFrames project per clip, built for either ratio from the same verified cut.

    import clip_engine as E
    E.init(ROOT, "16x9" | "9x16", face=(cx, cy))      # face centre in SOURCE pixels (04_faces.py prints it)
    E.shots([(0, "wide"), (1.877, "punch"), ...])      # 16x9: wide | punch | full (graphic alone)
    E.shots([(0, "him"), (1.877, "anim"), (4.463, "split"), ...])   # 9x16: him (the speaker full screen) | him2 (the same, tighter) | split | anim
    E.hook(0, 1.877, "Line one", "Line two")           # 9x16 text hook above the speaker's head
    E.scrim([(0, 12.9), ...])                          # 16x9: darken the graphic side while graphics are up
    st = E.stage(a, b, x, y, scale)                    # a 680x540 design surface placed in the frame
    st.add(html, css, js)                              # ids inside must be unique; animate with fin/fout/draw/typeText/counter on `tl`
    E.build()
Captions come from captions.json: one line in the caption font (bold, -0.05em), the emphasis word in the emphasis font
and the accent colour, figures in the caption font and the accent colour. The rules are in references/style.md.
Font files and colours are filled in from the creator profile by setup/apply_profile.py.
All times are seconds on the cut timeline. Switch times are snapped to frames."""
import html as _html, json, os, re

ROOT = None; P = {}; R = "16x9"; W = H = 0; FACE = (960, 540); SHOTS = []; CAPS = []; CUTS = []
_H, _C, _J, WARN = [], [], [], []
O, GREEN, RED, PAPER, GREY = "@@ACCENT@@", "#2FA65A", "#B3261E", "@@PAPER@@", "@@GREY@@"
SW, SH = 1920, 1080                 # source size
PUNCH = 1.12                        # 16x9 punch-in
SIDE, SIDEP = 1.2, 1.34            # 16x9 "graphics" framings: enlarged and anchored to the LEFT edge, so the speaker moves right and the left opens up
CAP = {"16x9": {"size": 68, "wide": 958, "punch": 958, "side": 958, "sidep": 958, "full": 958},
       "9x16": {"size": 66, "him": 1450, "him2": 1450, "split": 916, "anim": 1250}}
V = {"him": {"z": 1.78, "X": 640, "Y": 960}, "him2": {"z": 1.98, "X": 640, "Y": 960}, "split": {"z": 1.07, "X": 640, "Y": 430}}   # 9x16 placement of the speaker's face
FACES = []; STAGES = []
HEAD = (0.32, 0.65, 0.55, 0.30)       # how far the protected head box extends past the detected face box: left, top, right, bottom (in face widths / heights)
MARGIN = 28                         # clear space kept between a graphic and the head box
EARLY = 0.15
EM_SCALE = 1.12                     # emphasis words are set this much larger than the caption font so a lighter serif reads the same size; 1.0 if the emphasis font IS the caption font


def init(root, ratio, face=(960, 540), src=(1920, 1080)):
    global ROOT, P, R, W, H, FACE, CAPS, CUTS, SW, SH
    ROOT, R, FACE = root, ratio, face; SW, SH = src
    W, H = (1920, 1080) if ratio == "16x9" else (1080, 1920)
    P = json.load(open(os.path.join(root, "project.json")))
    CAPS = json.load(open(os.path.join(root, "captions.json")))
    cu = os.path.join(root, "cuts.json"); CUTS = json.load(open(cu)) if os.path.exists(cu) else []
    fa = os.path.join(root, "faces.json"); FACES[:] = json.load(open(fa)) if os.path.exists(fa) else []
    for L in (_H, _C, _J, WARN, SHOTS, STAGES): L.clear()
    stage.n = 0
    if ratio == "16x9" and not FACES: WARN.append("no faces.json: run 04_faces.py on the cut, or graphics cannot be checked against the speaker's face")


def fr(t):
    return round(round(t * P["fps"]) / P["fps"] - 0.002, 4) if t > 0.01 else 0.0


def shots(seq):
    SHOTS[:] = [(fr(t), m) for t, m in seq]
    edges = [t for t, _ in SHOTS[1:]]
    for c in CUTS:
        if c.get("big") and min([abs(c["t"] - e) for e in edges] or [9]) > 1.5 / P["fps"]:
            m = mode_at(c["t"])
            if m not in ("anim", "full"): WARN.append(f"big jump cut at {c['t']:.2f}s is visible on the speaker ({m}): put a switch on it")
    for (a, m), (b, _) in zip(SHOTS, SHOTS[1:] + [(P["dur"], "")]):
        if b - a < 0.9: WARN.append(f"{m} block {a:.2f}-{b:.2f} is under 0.9s: it will read as a flash")


def mode_at(t):
    m = SHOTS[0][1]
    for a, mm in SHOTS:
        if a <= t + 1e-4: m = mm
    return m


def _xf(mode):
    """16x9: (scale, left, top) of the video for a mode."""
    fx, fy = FACE
    z = {"punch": PUNCH, "side": SIDE, "sidep": SIDEP}.get(mode, 1.0)
    left = 0.0 if mode in ("side", "sidep") else fx - fx * z
    top = min(0.0, max(H - SH * z, fy - fy * z))
    return z, left, top


def head_at(t):
    """Protected head box (l, t, r, b) in FRAME pixels at time t for the shot on screen then; None when the speaker is not on screen."""
    if R != "16x9" or not FACES: return None
    m = mode_at(t)
    if m == "full": return None
    f = min(FACES, key=lambda q: abs(q["t"] - t)); z, left, top = _xf(m); a, b, c, d = HEAD
    return (left + (f["x"] - a * f["w"]) * z, top + (f["y"] - b * f["h"]) * z, left + (f["x"] + (1 + c) * f["w"]) * z, top + (f["y"] + (1 + d) * f["h"]) * z)


def clear_left(a, b):
    """The x a graphic's right edge must stay left of between a and b (the head box, less the margin)."""
    xs = [head_at(f["t"])[0] for f in FACES if a - 0.3 <= f["t"] <= b + 0.3 and head_at(f["t"])]
    return (min(xs) - MARGIN) if xs else W


def fit(a, b, x, content_w=680, max_scale=1.3):
    """Largest scale for a stage at left edge x whose content is content_w wide, so it never reaches the speaker's head."""
    return round(min(max_scale, (clear_left(a, b) - x) / content_w), 3)


def hook(a, b, l1, l2, top=92):
    _H.append(f'<div id="hook" style="top:{top}px"><div class="h1">{_html.escape(l1)}</div><div class="h2"><span>{_html.escape(l2)}</span></div></div>')
    _J.append(f'tl.set("#hook",{{opacity:1}},{a}); tl.set("#hook",{{opacity:0}},{fr(b)});')


def scrim(windows):
    for a, b in windows:
        _J.append(f'tl.fromTo("#scrim",{{opacity:0}},{{opacity:1,duration:0.35,immediateRender:{"true" if a <= 0 else "false"}}},{max(0, a - 0.2)}); tl.to("#scrim",{{opacity:0,duration:0.35}},{b});' if a > 0
                  else f'tl.set("#scrim",{{opacity:1}},0); tl.to("#scrim",{{opacity:0,duration:0.35}},{b});')


class stage:
    """A 680x540 design surface placed at (x, y) with a scale. Everything left on it is hidden at b."""
    n = 0

    def __init__(self, a, b, x, y, scale=1.0, cut_in=False, cut_out=False, box=(0, 0, 680, 540)):
        """box = the part of the 680x540 surface that actually holds content (l, t, r, b), for the face check."""
        stage.n += 1; self.id = f"st{stage.n}"; self.a, self.b = a, b
        STAGES.append((a, b, x + box[0] * scale, y + box[1] * scale, x + box[2] * scale, y + box[3] * scale, self.id))
        _H.append(f'<div id="{self.id}" class="stage" style="left:{x}px;top:{y}px;transform:scale({scale})">')
        self._open = len(_H)
        _J.append(f'tl.set("#{self.id}",{{opacity:1}},{fr(a) if cut_in else max(0, a - 0.3)});'
                  + (f' tl.set("#{self.id}",{{opacity:0}},{fr(b)});' if cut_out else f' tl.to("#{self.id}",{{opacity:0,filter:"blur(8px)",duration:0.25,ease:"power2.in"}},{round(b - 0.25, 3)});' if b < P["dur"] - 0.05 else ""))

    def add(self, htm, css="", js=""):
        _H.append(htm); _C.append(css); _J.append(js); return self

    def close(self):
        _H.append("</div>")

    def __enter__(self): return self
    def __exit__(self, *a): self.close()


JS = r"""
function fin(sel, t, o) { o = o || {}; tl.fromTo(sel, { opacity: 0, scale: o.s == null ? 1.08 : o.s, filter: 'blur(16px)' }, { opacity: 1, scale: 1, filter: 'blur(0px)', duration: o.d || 0.5, ease: 'power3.out' }, Math.max(0, t - EARLY)); }
function fout(sel, t, d) { tl.to(sel, { opacity: 0, filter: 'blur(8px)', duration: d || 0.25, ease: 'power2.in' }, t); }
function draw(sel, t, d) { tl.set(sel, { visibility: 'visible' }, t); tl.fromTo(sel, { strokeDashoffset: 1000 }, { strokeDashoffset: 0, duration: d || 0.5, ease: 'power2.inOut' }, t); }
function typeText(sel, s, t, d) { const el = document.querySelector(sel), p = { n: 0 }; tl.fromTo(p, { n: 0 }, { n: s.length, duration: d, ease: 'none', onUpdate: function () { el.textContent = s.slice(0, Math.round(p.n)); } }, t); }
function counter(sel, a, b, t, d, pre, suf) { const el = document.querySelector(sel), p = { n: a }; tl.fromTo(p, { n: a }, { n: b, duration: d, ease: 'power2.inOut', onUpdate: function () { el.textContent = (pre || '') + Math.round(p.n).toLocaleString('en-US') + (suf || ''); } }, t); }
function counterD(sel, a, b, t, d, dec, suf) { const el = document.querySelector(sel), p = { n: a }; tl.fromTo(p, { n: a }, { n: b, duration: d, ease: 'power2.inOut', onUpdate: function () { el.textContent = p.n.toFixed(dec) + (suf || ''); } }, t); }
function sweep(sel, t) { tl.to(sel, { '--sw': 140, duration: 0.7, ease: 'power2.out' }, t); }
"""


def _vid(mode):
    """CSS box of the clip window and of the video inside it for a mode."""
    fx, fy = FACE
    if R == "16x9":
        z, left, top = _xf(mode)
        return (0, 0, W, H), (round(left, 1), round(top, 1), round(SW * z, 1), round(SH * z, 1))
    v = V[mode if mode in V else "him"]; z = v["z"] * (1080 / SH if False else 1)
    box = (0, 960, 1080, 960) if mode == "split" else (0, 0, 1080, 1920)
    vw, vh = SW * z, SH * z
    left = min(0, max(box[2] - vw, v["X"] - fx * z)); top = min(0, max(box[3] - vh, v["Y"] - fy * z))
    return box, (round(left, 1), round(top, 1), round(vw, 1), round(vh, 1))


def build():
    D, FPS = P["dur"], P["fps"]; cam = []
    for k, (t, m) in enumerate(SHOTS):
        box, v = _vid(m); cover = m in ("anim", "full")
        s = (f'tl.set("#clip",{{left:{box[0]},top:{box[1]},width:{box[2]},height:{box[3]}}},{t}); '
             f'tl.set("#vid",{{left:{v[0]},top:{v[1]},width:{v[2]},height:{v[3]}}},{t}); tl.set("#cover",{{opacity:{1 if cover else 0}}},{t});')
        if R == "9x16":
            s += f' tl.set("#top",{{opacity:{1 if m == "split" else 0}}},{t});'
            if m in ("him", "him2"):                                   # barely noticeable eased zoom out on full-screen blocks
                e = SHOTS[k + 1][0] if k + 1 < len(SHOTS) else D; fx, fy = FACE
                s += f' tl.fromTo("#vid",{{scale:1.05,transformOrigin:"{round(100 * fx / SW)}% {round(100 * fy / SH)}%"}},{{scale:1,duration:{round(e - t, 3)},ease:"sine.out",immediateRender:{"true" if k == 0 else "false"}}},{t});'
            else:
                s += f' tl.set("#vid",{{scale:1}},{t});'
        cam.append(s)
    for a, b, l, t0, r, b0, sid in STAGES:                     # 16x9: no graphic may touch the speaker's head
        worst = 0
        for f in FACES:
            if a + 0.05 <= f["t"] <= b - 0.05 and head_at(f["t"]):
                hl, ht, hr, hb = head_at(f["t"])
                if l < hr + MARGIN and r > hl - MARGIN and t0 < hb + MARGIN and b0 > ht - MARGIN: worst = max(worst, r - (hl - MARGIN))
        if worst > 1: WARN.append(f"FACE: stage {sid} ({a:.1f}-{b:.1f}s) reaches {worst:.0f}px into the protected head zone: move it, shrink it (E.fit) or use a side shot")
    edges = [t for t, _ in SHOTS[1:]]; caps = ""; n = 0
    for c in CAPS:
        a, b = c["start"], min(c["end"], D)
        ks = [a] + [e for e in edges if a + 0.04 < e < b - 0.04] + [b]
        for x, y in zip(ks, ks[1:]):
            m = mode_at((x + y) / 2)
            inner = "".join((f'<em class="{"nu" if any(ch.isdigit() for ch in p["t"]) else "iv"}">{_html.escape(p["t"], quote=False)}</em>' if p.get("em") else _html.escape(p["t"], quote=False)) for p in c["parts"])
            caps += f'<div id="cap{n}" class="clip cap" data-layout-allow-overlap data-start="{round(x, 3)}" data-duration="{round(y - x, 3)}" data-track-index="30"><span data-layout-allow-overlap style="top:{CAP[R][m]}px{";color:#d9d4cb" if c.get("other") else ""}">{inner}</span></div>\n'; n += 1
    fonts = """
      @font-face { font-family: "SFB"; src: @@FONT_CAPTION_SRC@@; font-weight: 700; }
      @font-face { font-family: "SFS"; src: @@FONT_CAPTION_SRC@@; font-weight: 600; }
      @font-face { font-family: "SFM"; src: @@FONT_MAIN_REGULAR_SRC@@; font-weight: 500; }
      @font-face { font-family: "HelvB"; src: @@FONT_MAIN_BOLD_SRC@@; font-weight: 700; }
      @font-face { font-family: "Ivy"; src: @@FONT_ACCENT_SRC@@; font-style: normal; font-weight: 400; }"""
    scr = ('<div id="scrim"></div>' if R == "16x9" else '<div id="top"><i></i><i></i></div>')
    index = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>{_html.escape(P["title"])} - {R}</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>{fonts}
      :root {{ --o: {O}; --g: {GREEN}; --r: {RED}; --p: {PAPER}; --gy: {GREY}; }}
      body {{ margin: 0; background: #000; }}
      #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: @@BG@@; font-family: "SFB", "HelvB", sans-serif; color: #fff; letter-spacing: -0.04em; }}
      #clip {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; overflow: hidden; z-index: 1; }}
      #vid {{ position: absolute; display: block; }}
      #cover, #top {{ position: absolute; z-index: 2; background: @@BG@@; overflow: hidden; opacity: 0; }}
      #cover {{ inset: 0; }} #top {{ left: 0; top: 0; width: 1080px; height: 960px; }}
      #cover i, #top i {{ position: absolute; border-radius: 50%; filter: blur(70px); }}
      #cover i:nth-child(1), #top i:nth-child(1) {{ left: 8%; top: 22%; width: 420px; height: 420px; background: rgba(@@ACCENT_RGB@@,.38); }}
      #cover i:nth-child(2), #top i:nth-child(2) {{ right: 6%; top: 48%; width: 360px; height: 360px; background: rgba(@@ACCENT_RGB@@,.22); }}
      #scrim {{ position: absolute; inset: 0; z-index: 3; opacity: 0; background: linear-gradient(90deg, rgba(@@BG_RGB@@,.78) 0%, rgba(@@BG_RGB@@,.62) 30%, rgba(@@BG_RGB@@,0) 50%); }}
      .stage {{ position: absolute; width: 680px; height: 540px; transform-origin: 0 0; z-index: 5; opacity: 0; }}
      .stage > * {{ position: absolute; }}
      .glass {{ border-radius: 28px; background: linear-gradient(180deg, rgba(255,255,255,.20), rgba(255,255,255,.05) 55%, rgba(255,255,255,.11)), rgba(12,11,10,.50); -webkit-backdrop-filter: blur(22px) saturate(180%); backdrop-filter: blur(22px) saturate(180%); border: 1.5px solid rgba(255,255,255,.24); box-shadow: inset 0 1px 0 rgba(255,255,255,.32), 0 26px 60px rgba(0,0,0,.5); box-sizing: border-box; }}
      .pill {{ --sw: -40; height: 84px; border-radius: 42px; display: flex; align-items: center; gap: 18px; padding: 0 34px 0 22px; font-size: 38px; white-space: nowrap; box-sizing: border-box; overflow: hidden; }}
      .pill::after {{ content: ""; position: absolute; inset: 0; background: linear-gradient(105deg, transparent calc(var(--sw) * 1% - 18%), rgba(255,255,255,.34) calc(var(--sw) * 1%), transparent calc(var(--sw) * 1% + 18%)); pointer-events: none; }}
      .dot {{ width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex: none; }}
      .ln {{ position: absolute; left: 0; top: 0; overflow: visible; pointer-events: none; }}
      .ln [stroke-dashoffset="1000"] {{ visibility: hidden; }}
      em.iv {{ font-family: "Ivy", serif; font-style: normal; font-weight: 400; color: var(--o); letter-spacing: -0.03em; font-size: {EM_SCALE}em; line-height: 0.9; }}
      em.nu {{ font-style: normal; color: var(--o); }}
      #hook {{ position: absolute; left: 0; width: 1080px; text-align: center; z-index: 12; opacity: 0; font-family: "HelvB", sans-serif; letter-spacing: -0.045em; line-height: 1.12; }}
      #hook .h1 {{ font-size: 84px; text-shadow: 0 4px 22px rgba(0,0,0,.6); }}
      #hook .h2 span {{ display: inline-block; font-size: 80px; color: #000; background: #fff; padding: 2px 22px 6px; margin-top: 6px; }}
      .cap {{ z-index: 20; pointer-events: none; }}
      .cap span {{ position: absolute; left: 60px; right: 60px; display: block; text-align: center; white-space: nowrap; font-family: "SFB", "HelvB", sans-serif; font-weight: 700; font-size: {CAP[R]["size"]}px; letter-spacing: -0.05em; line-height: 1; color: #fff; transform: translateY(-50%); text-shadow: 0 3px 16px rgba(0,0,0,.8), 0 0 3px rgba(0,0,0,.7); }}
      {chr(10).join(_C)}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{D}" data-fps="{round(FPS)}">
      <div id="clip"><video id="vid" src="assets/cam.mp4" playsinline data-has-audio="true" data-start="0" data-duration="{D}" data-track-index="0"></video></div>
      <div id="cover"><i></i><i></i></div>
      {scr}
{chr(10).join(_H)}
{caps}    </div>
    <script>
      const EARLY = {EARLY};
      const tl = gsap.timeline({{ paused: true }});
      {JS}
      {chr(10).join(cam)}
      {chr(10).join(_J)}
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    # a zero-duration tl.set at 0 does not render on frame 0: make those immediate
    index = re.sub(r'tl\.set\(("[^"]+",\{[^}]*\}),0(?:\.0)?\);', r'gsap.set(\1);', index)
    open(os.path.join(ROOT, "index.html"), "w").write(index)
    print(f"{R}: {n} caption pieces, {len(SHOTS)} shots, {stage.n} stages over {D:.1f}s")
    for w in WARN: print("WARN", w)
