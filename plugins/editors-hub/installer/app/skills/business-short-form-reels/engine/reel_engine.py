#!/usr/bin/env python3
"""Business Short Form Reels - HyperFrames reel engine.

A reel = one 1080x1920 HyperFrames project:
  black base -> scene sub-compositions (split scenes paint only y>=960; `full` scenes paint the whole frame)
  -> #camTop (cam_top.mp4, 1080x960, carries the audio) -> #camFull (cam_full.mp4, 1080x1920, muted) -> captions.
The main timeline hard-cuts the camera between the three modes:
  split      = not in FACE and not in FULL   (face top half, animation bottom half)
  face       = inside a FACE window          (full-screen face; overlay() graphics sit over the creator and behind the creator's head)
  animation  = inside a FULL window          (full-screen animation, camera hidden)
Captions (captions.json: [{text,start,end}]) are split at every mode edge so each piece sits under the
chin for its mode (split y640/56px, face y1079/62px, animation y1180/62px - all inside the safe zone, see SAFE_* below).

Use from a project's build.py:
    import reel_engine as E
    from reel_engine import scene
    E.init(ROOT, DUR, FACE, FULL, title="My Reel")
    scene("s01-hook", 0, 3.8, False, BODY_HTML, CSS, JS)     # JS uses GLOBAL seconds through T(g)
    ...
    E.build()
Scene JS helpers (see HELPERS): T(g), q(id), rise, pop, out, draw, words, note, floaty.

FACE-WINDOW OVERLAYS: a full-screen face window may carry graphics
over the creator AND behind the creator's head. Layers inside #camFull: cam_full.mp4 -> #fBehind -> cam_fg.webm (the creator's cut-out,
from `07_crops.sh` / `hyperframes remove-background`) -> #fFront. Everything in them shows only in FACE windows.
    E.init(ROOT, DUR, FACE, FULL, words="words.json", emph={"change", "selfish"}, keep={"Black", "Bezos"})
    E.overlay(behind=HTML, front=HTML, css=CSS, js=JS)     # JS runs on the MAIN timeline `tl`, GLOBAL seconds
Overlay JS helpers (see FX): slide(sel,dx,dy,t,dur) with real directional motion blur, opop, orise, oout,
counter(sel,from,to,t,dur), orbit({front:[..],back:[..],cx,cy,rx,ry,t,dur,deg,stagger}).
With `words=` set, captions inside FACE windows become ONE WORD AT A TIME (lower-case, the main bold font), and any
word in `emph` is set in the accent colour and the emphasis font. Tokens with a digit stay in the main font (accent colour). Split and
full-animation captions are unchanged (2-4 word phrases).
"""
import json, os

ROOT = None; DUR = 0.0; FACE = []; FULL = []; CAPS = []; TITLE = "Reel"; S = []
WORDS = []; EMPH = set(); KEEP = set(); FIX = {}; HIDE = []; OV = []; TOP = []
ZOOM_FACE = 1.05      # full-screen footage: start scale of the slow zoom out
ZOOM_ANIM = 1.04      # full-screen animations: the same drift on the animation layer (captions and the agenda are above it and do not move)

# ---- Instagram / TikTok safe zone on the 1080x1920 frame. Meta's published Reels zone is top 14% / bottom 35% / sides 6%; the organic feed UI covers about
# the top 250 px and bottom 420 px plus the button rail on the right.
SAFE_TOP = 270        # nothing that matters above this (handle, audio, Following/For You tabs)
SAFE_BOTTOM = 1500    # aim to keep graphic content above this (caption, audio row, buttons)
SOFT_BOTTOM = 1585    # ...but is allowed ~20% into the bottom zone ("don't be too strict, especially at the bottom"): hard stop
CAP_BOTTOM = 1250     # captions aim to END above this (Meta's 35% line); up to ~1330 is acceptable
# The TOP has no such slack ("at the top you don't have much room"): hold SAFE_TOP.
SAFE_SIDE = 65        # left/right margin
RAIL_X = 950          # right of this, between y 1000 and SAFE_BOTTOM, sit the like/comment/share buttons
GUIDE = bool(os.environ.get("SAFE"))   # SAFE=1 python3 build.py -> draws the zones for snapshots. NEVER render with it on.

def init(root, dur, face, full, caps="captions.json", title="Reel", words=None, emph=(), keep=(), fix=None, hide=()):
    """root: project dir; dur: cut length (s); face/full: [[start,end],...] windows; caps: captions.json path.
    words: the cut's words.json ([[s,e,word,..]] or [{s,e,w}]) -> one-word captions in FACE windows.
    emph: words set in the accent colour and the emphasis font. keep: words that keep their capitals (names). fix: {heard: shown}.
    hide: [[start,end],...] spans with NO face caption (a headline or counter on screen already says the words)."""
    global ROOT, DUR, FACE, FULL, CAPS, TITLE, WORDS, EMPH, KEEP, FIX, HIDE
    ROOT, DUR, FACE, FULL, TITLE = root, dur, face, full, title
    p = caps if os.path.isabs(caps) else os.path.join(root, caps)
    CAPS = json.load(open(p)); S.clear(); OV.clear(); TOP.clear(); WORDS = []
    if words:
        wp = words if os.path.isabs(words) else os.path.join(root, words)
        if not os.path.exists(wp): print("WARNING: no", wp, "- face windows fall back to phrase captions"); wp = None
        for w in (json.load(open(wp)) if wp else []):
            if isinstance(w, dict):
                if w.get("event"): continue
                WORDS.append((float(w["s"]), float(w["e"]), str(w["w"])))
            else: WORDS.append((float(w[0]), float(w[1]), str(w[2])))
    EMPH = {x.lower() for x in emph}; KEEP = set(keep); FIX = dict(fix or {}); HIDE = [list(x) for x in hide]

def overlay(behind="", front="", css="", js=""):
    """Graphics for FACE windows. behind: HTML drawn BEHIND the creator's head (needs assets/cam_fg.webm); front: HTML over the creator.
    Coordinates are the 1080x1920 frame. js runs on the main timeline `tl` in GLOBAL seconds with the FX helpers.
    Give every element opacity:0 in css and bring it in with a helper; take it out before the window ends."""
    OV.append(dict(behind=behind, front=front, css=css, js=js))

def top(html="", css="", js=""):
    """A layer above everything, in every mode (e.g. the agenda box at the top of the screen). js runs on the main timeline, GLOBAL seconds, FX helpers available."""
    TOP.append(dict(html=html, css=css, js=js))

FX = r"""
const $o = (s) => document.querySelector(s);
let __fxn = 0;
function __blur(sel) { const id = 'mb' + (++__fxn), d = $o('#fxdefs');
  d.insertAdjacentHTML('beforeend', '<filter id="' + id + '" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="0 0"/></filter>');
  $o(sel).style.filter = 'url(#' + id + ')'; return d.lastElementChild.firstElementChild; }
// slide in from (dx,dy) with real directional motion blur that settles as it lands
function slide(sel, dx, dy, t, dur) { dur = 0.62; const node = __blur(sel), p = { b: 1 }, bx = Math.abs(dx) / 9, by = Math.abs(dy) / 9;
  gsap.set(sel, { opacity: 0 });
  tl.fromTo(sel, { x: dx * 0.45, y: dy * 0.45 }, { x: 0, y: 0, duration: dur, ease: 'power2.inOut' }, t);
  tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: 0.1, ease: 'none', immediateRender: false }, t);
  tl.fromTo(p, { b: 1 }, { b: 0, duration: dur * 0.75, ease: 'power3.out', onUpdate: function () { node.setAttribute('stdDeviation', (bx * p.b).toFixed(2) + ' ' + (by * p.b).toFixed(2)); } }, t); }
function opop(sel, t, from) { tl.fromTo(sel, { scale: 0.86, opacity: 0, filter: 'blur(10px)' }, { scale: 1, opacity: 1, filter: 'blur(0px)', duration: 0.5, ease: 'power2.inOut' }, t); }
function orise(sel, t, dy) { tl.fromTo(sel, { y: dy == null ? 28 : dy, opacity: 0, filter: 'blur(10px)' }, { y: 0, opacity: 1, filter: 'blur(0px)', duration: 0.5, ease: 'power2.inOut' }, t); }
function oout(sel, t, dur) { tl.to(sel, { opacity: 0, duration: dur || 0.3, ease: 'power2.inOut' }, t); }
// count from a to b; put the element in `behind` so the number tucks behind the creator's head
function counter(sel, a, b, t, dur) { const c = { n: a }, el = $o(sel); el.textContent = Math.round(a).toLocaleString('en-US');
  tl.fromTo(c, { n: a }, { n: b, duration: dur || 0.95, ease: 'power2.inOut', onUpdate: function () { el.textContent = Math.round(c.n).toLocaleString('en-US'); } }, t); }
// objects orbit the creator: each object needs TWO copies with the same content, one in `front`, one in `behind`.
// o = { front:[sel..], back:[sel..], cx, cy, rx, ry, t, dur, deg (travel), start (deg), stagger }
function orbit(o) { const n = o.front.length, P = { a: 0, fade: 1 }, K = o.front.map(function () { return { k: 0 }; });
  function place() { for (let i = 0; i < n; i++) { const th = (P.a + i * 360 / n + (o.start == null ? 200 : o.start)) * Math.PI / 180, s = Math.sin(th);
      const x = o.cx + o.rx * Math.cos(th), y = o.cy + o.ry * s, k = K[i].k * P.fade, sc = (0.86 + 0.16 * s) * (0.6 + 0.4 * K[i].k);
      const f = $o(o.front[i]), b = $o(o.back[i]), tf = 'translate(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px) scale(' + sc.toFixed(3) + ')';
      f.style.transform = tf; b.style.transform = tf; f.style.opacity = s >= 0 ? k : 0; b.style.opacity = s >= 0 ? 0 : k * 0.9; } }
  tl.fromTo(P, { a: 0 }, { a: o.deg || 150, duration: o.dur, ease: 'power1.out', onUpdate: place }, o.t);
  K.forEach(function (kk, i) { tl.fromTo(kk, { k: 0 }, { k: 1, duration: 0.3, ease: 'back.out(2)', onUpdate: place }, o.t + 0.06 + i * (o.stagger || 0.18)); });
  tl.to(P, { fade: 0, duration: 0.12, ease: 'none', onUpdate: place }, o.t + o.dur - 0.12); place(); }
"""

HELPERS = r"""
const T = (g) => g - START;
const q = (s) => "#" + ID + "-" + s;
function rise(tl, s, g, o) { o = o || {}; tl.fromTo(q(s), { opacity: 0, y: o.y == null ? 30 : o.y, filter: "blur(10px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: o.d || 0.42, ease: o.e || "power3.out" }, T(g)); }
function pop(tl, s, g, o) { o = o || {}; tl.fromTo(q(s), { opacity: 0, scale: o.from == null ? 0.55 : o.from, rotation: o.r || 0 }, { opacity: 1, scale: 1, rotation: 0, duration: o.d || 0.45, ease: o.e || "back.out(2.2)" }, T(g)); }
function out(tl, s, g, d) { tl.to(q(s), { opacity: 0, filter: "blur(8px)", duration: d || 0.3, ease: "power2.in" }, T(g)); }
function draw(tl, s, g, d, e) { tl.fromTo(q(s), { strokeDashoffset: 1000 }, { strokeDashoffset: 0, duration: d || 0.6, ease: e || "power2.inOut" }, T(g)); }
function words(tl, s, list) { list.forEach(function (w, i) { tl.fromTo(q(s + "-w" + i), { opacity: 0, y: 26, filter: "blur(8px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.36, ease: "power3.out" }, T(w)); }); }
function note(tl, s, g, until) { tl.fromTo(q(s), { opacity: 0, scale: 0.86, rotation: -8 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.4, ease: "back.out(2)" }, T(g)); if (until) tl.to(q(s), { opacity: 0, duration: 0.25 }, T(until)); }
function sweep(tl, s, g) { const el = document.querySelector(q(s)); if (!el) return; const m = document.createElement("div");
  m.style.cssText = "position:absolute;inset:0;border-radius:inherit;pointer-events:none;mix-blend-mode:screen;opacity:0;background:linear-gradient(115deg, rgba(255,255,255,0) 35%, rgba(255,255,255,.55) 50%, rgba(255,255,255,0) 65%);background-size:260% 100%;background-position:130% 0";
  el.style.overflow = "hidden"; el.appendChild(m); const P = { p: 130 };
  __tt(m, { opacity: 1, duration: 0.15, ease: "none" }, T(g)); __ft(P, { p: 130 }, { p: -40, duration: 1.1, ease: "power2.inOut", onUpdate: function () { m.style.backgroundPosition = P.p.toFixed(1) + "% 0"; } }, T(g)); __tt(m, { opacity: 0, duration: 0.2, ease: "none" }, T(g) + 0.95); }
function floaty(tl, s, amp, per, from, dur) { const n = Math.max(1, Math.floor(dur / per)); tl.fromTo(q(s), { y: -amp }, { y: amp, duration: per / 2, ease: "sine.inOut", yoyo: true, repeat: n * 2 - 1 }, T(from)); }
"""

def head(sid, lines, top, size, extra=""):
    """lines: [[(text, accent?), ...], ...] -> spans id sid-wN in order"""
    k, html = 0, []
    for ln in lines:
        segs = []
        for txt, o in ln:
            segs.append(f'<span id="{{ID}}-{sid}-w{k}" class="w{" de-o" if o else ""}">{txt}</span>')
            k += 1
        html.append("<div>" + "".join(segs) + "</div>")
    return f'<div id="{{ID}}-{sid}" class="de-head" style="top:{top}px;font-size:{size}px;{extra}">{"".join(html)}</div>'

def scene(cid, start, end, full, body, css, js):
    dur = round(end - start, 3)
    box = "de-full" if full else "de-panel"
    # MOTION-BLUR ENTRANCE: the whole graphic slides in with directional blur on the frame the scene becomes visible
    vis = next((b for a, b in FACE if a - 0.001 <= start < b), start) if not full else start     # split scenes may start early, hidden under a face window
    k = len(S) % 3
    oy = 0 if not full else 330      # light orbs the glass refracts (they drift slowly); full-screen graphics live around y 330-1100
    orbs = ('<div class="lg-orbs"><i id="{ID}-o0" style="left:110px;top:%dpx;width:400px;height:400px;background:rgba(@@ACCENT_RGB@@,.40)"></i>'
            '<i id="{ID}-o1" style="left:600px;top:%dpx;width:440px;height:440px;background:rgba(255,190,130,.24)"></i>'
            '<i id="{ID}-o2" style="left:380px;top:%dpx;width:300px;height:300px;background:rgba(255,255,255,.10)"></i></div>') % (oy + 40, oy + (200 if not full else 420), oy + (-40 if not full else 640))
    dx, dy = ((0, -80), (90, 0), (-90, 0))[k] if not full else ((0, 90), (-90, 0), (90, 0))[k]      # SOFT GLIDE: short travel
    wins = sorted(FACE + FULL)
    vend = next((b for a, b in FULL if a - 0.001 <= vis < b), end) if full else next((a for a, b in wins if a > vis + 0.01), DUR)
    fade = '__tt("#" + ID + "-in", { opacity: 0, duration: 0.3, ease: "power2.inOut" }, %s - START - 0.3);' % vend if vend < DUR - 0.05 else ''      # SOFT FADE OUT before the switch
    small = 'transform:scale(.84);transform-origin:540px 730px;' if full else ''      # full-screen graphics: smaller, centred
    wrap = 'class="de-shift"' if not full else 'class="de-in" style="position:absolute;inset:0;z-index:1"'
    body = ('<svg width="0" height="0" style="position:absolute"><filter id="{ID}-mb" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur id="{ID}-mbn" stdDeviation="0 0"/></filter></svg>'
            '<div id="{ID}-in" ' + wrap + '><div id="{ID}-in2" style="position:absolute;inset:0;' + small + 'filter:url(#{ID}-mb)">' + orbs + body + '</div></div>')
    js = js + """
          __ft("#" + ID + "-o0", { x: -60, y: 20 }, { x: 90, y: -30, duration: DUR, ease: "sine.inOut" }, 0); __ft("#" + ID + "-o1", { x: 50, y: -30 }, { x: -110, y: 40, duration: DUR, ease: "sine.inOut" }, 0); __ft("#" + ID + "-o2", { x: -40, y: 30 }, { x: 70, y: -20, duration: DUR, ease: "sine.inOut" }, 0);
          (function () { const node = document.getElementById(ID + "-mbn"), V = %s - START, DX = %d, DY = %d, p = { b: 1 };
            __ft("#" + ID + "-in", { opacity: 0, scale: 1.07, filter: "blur(18px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.55, ease: "power3.out", immediateRender: false }, V);      // FOCUS PULL: the whole graphic resolves from a heavy blur
            %s })();""" % (vis, dx, dy, fade)
    if full:      # SLOW ZOOM OUT on the animation layer too, so a full-screen animation feels alive. Whole scene box (background + graphic) drifts from ZOOM_ANIM to 100%.
        js += '\n          __ft("#" + ID + "-box", { scale: %s, transformOrigin: "50%% 42%%" }, { scale: 1, duration: %s, ease: "sine.out" }, 0);' % (ZOOM_ANIM, round(max(0.5, min(end, vend) - start), 3))
    body = body.replace("{ID}", cid)
    css = css.replace("{ID}", cid)
    html = f"""<!doctype html>
<html lang="en">
  <head><meta charset="UTF-8" /></head>
  <body>
    <template>
      <link rel="stylesheet" href="assets/brand.css" />
      <style>
        @font-face {{ font-family: "HelvB"; src: @@FONT_MAIN_BOLD_SRC@@; font-weight: 700; }}
        @font-face {{ font-family: "HelvR"; src: @@FONT_MAIN_REGULAR_SRC@@; font-weight: 400; }}
        @font-face {{ font-family: "PlayIt"; src: @@FONT_ACCENT_SRC@@; font-style: normal; font-weight: 400 900; }}
        @font-face {{ font-family: "Hand"; src: url("assets/fonts/Caveat.ttf") format("truetype"); }}
        #root {{ position: absolute; inset: 0; width: 100%; height: 100%; overflow: hidden; }}
        {css}
        /* LIQUID GLASS: animation pills and cards only. Translucent, blurs the light orbs behind it, bright top rim. */
        .lg-orbs {{ position: absolute; inset: 0; z-index: 0; pointer-events: none; }}
        .lg-orbs i {{ position: absolute; border-radius: 50%; filter: blur(64px); }}
        #root .mc, #root .pl1, #root .yp, #root .rp3, #root .fill, #root .sv, #root .tp, #root .gp, #root .sc, #root .mk, #root .bb, #root .rw3.de-glass {{
          background: linear-gradient(180deg, rgba(255,255,255,.20), rgba(255,255,255,.05) 55%, rgba(255,255,255,.11)), rgba(12,11,10,.46); -webkit-backdrop-filter: blur(22px) saturate(180%); backdrop-filter: blur(22px) saturate(180%);
          border: 1.5px solid rgba(255,255,255,.44); box-shadow: inset 0 2px 1px rgba(255,255,255,.55), inset 0 -2px 2px rgba(255,255,255,.10), inset 0 0 26px rgba(255,255,255,.07), 0 22px 54px rgba(0,0,0,.45); }}
        #root .de-hot, #root .fill, #root .rp3, #root .sc.hot {{ border-color: rgba(245,170,110,.95); background: linear-gradient(180deg, rgba(@@ACCENT_RGB@@,.26), rgba(@@ACCENT_RGB@@,.06) 55%, rgba(@@ACCENT_RGB@@,.16)), rgba(12,11,10,.52);
          box-shadow: inset 0 2px 1px rgba(255,225,200,.6), inset 0 0 26px rgba(@@ACCENT_RGB@@,.14), 0 0 46px rgba(@@ACCENT_RGB@@,.45), 0 22px 54px rgba(0,0,0,.45); }}
        #root .tp.nw, #root .yp.pc2 {{ background: @@ACCENT@@; border-color: @@ACCENT_LIGHT@@; }}
      </style>
      <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920" data-duration="{dur}" data-layout-allow-overflow>
        <div id="{cid}-box" class="{box}">
          <div class="de-grid"></div>
          {body}
          {'' if full else '<div class="de-seam"></div>'}
        </div>
      </div>
      <script>
        (function () {{
          const ID = "{cid}", START = {start}, DUR = {dur}; let __ft, __tt;
          {HELPERS}
          const tl = gsap.timeline({{ paused: true }});
          // entrances authored before the scene start (pre-built for hard cuts): finish them by local 0
          __ft = tl.fromTo.bind(tl); __tt = tl.to.bind(tl);
          ["fromTo", "to"].forEach(function (m) {{ const orig = tl[m].bind(tl); tl[m] = function () {{ const a = Array.prototype.slice.call(arguments); const pi = m === "fromTo" ? 3 : 2; let p = a[pi];
            if (m === "fromTo" && a[1] && a[2] && a[1].opacity === 0 && a[2].opacity > 0 && a[1].filter == null && a[2].filter == null && a[2].duration > 0.1) {{ a[1] = Object.assign({{}}, a[1], {{ filter: "blur(16px)" }}); a[2] = Object.assign({{}}, a[2], {{ filter: "blur(0px)" }});
              if (a[1].scale == null) {{ a[1].scale = 1.08; a[2].scale = 1; }} if (a[1].y != null) a[1].y = a[1].y * 0.25; if (a[1].x != null) a[1].x = a[1].x * 0.25; if (a[1].rotation != null && a[2].rotation == null) a[2].rotation = 0; }}
            // v6: smooth ease in-out everywhere (no bounce); entrances are calmer (>= 0.5 s) and start 0.6 s early so they have landed just AHEAD of the word
            if (a[pi - 1] && typeof a[pi - 1] === "object") {{ const v = Object.assign({{}}, a[pi - 1]); if (v.ease && v.ease !== "none" && !/sine/.test(v.ease)) v.ease = "power2.inOut";
              if (m === "fromTo" && a[1] && a[1].opacity === 0 && v.opacity > 0) {{ v.duration = 0.52; v.ease = "power3.out"; if (typeof a[pi] === "number") a[pi] = a[pi] - 0.6; }} a[pi - 1] = v; p = a[pi]; }}
            if (typeof p === "number" && p < 0) {{ const vars = Object.assign({{}}, a[pi - 1]); const d = (vars.duration == null ? 0.5 : vars.duration) + (vars.stagger ? 0.4 : 0); if (d + p <= 0) {{ delete vars.duration; delete vars.ease; delete vars.stagger; delete vars.yoyo; delete vars.repeat; gsap.set(a[0], vars); return tl; }} vars.duration = d + p; a[pi - 1] = vars; a[pi] = 0; }} return orig.apply(null, a); }}; }});
          {js}
          window.__timelines["{cid}"] = tl;
        }})();
      </script>
    </template>
  </body>
</html>
"""
    os.makedirs(os.path.join(ROOT, "compositions"), exist_ok=True)
    open(os.path.join(ROOT, "compositions", cid + ".html"), "w").write(html)
    d = dict(id=cid, start=start, end=end, full=full)
    for k, s in enumerate(S):          # same id again = replace in place (variants)
        if s["id"] == cid: S[k] = d; return d
    S.append(d); return d

def inwin(t, W): return any(a <= t < b for a, b in W)

def build():
    """Write index.html (camera, scene hosts, captions, mode cuts)."""
    blocks_html = ""
    scenes_html = "".join(f'    <div id="host-{s["id"]}" class="clip scene" data-composition-id="{s["id"]}" data-composition-src="compositions/{s["id"]}.html" data-start="{s["start"]}" data-duration="{round(s["end"]-s["start"],3)}" data-track-index="10" data-width="1080" data-height="1920"></div>\n' for s in S)
    caps_html = ""
    EDGES = sorted(set(x for w in FACE + FULL for x in w))
    PIECES = []  # (text, start, end, mode, first?)
    for c in CAPS:
        a, b = c["start"], min(c["end"], DUR)
        cuts_ = [a] + [e for e in EDGES if a + 0.04 < e < b - 0.04] + [b]
        for k in range(len(cuts_) - 1):
            mid = (cuts_[k] + cuts_[k + 1]) / 2
            mode = "f" if inwin(mid, FACE) else ("a" if inwin(mid, FULL) else "s")
            if mode == "f" and WORDS: continue          # FACE windows get one-word captions below
            PIECES.append((c["text"], round(cuts_[k], 3), round(cuts_[k + 1], 3), mode, k == 0))
    for i, (txt, a, b, mode, first) in enumerate(PIECES):
        caps_html += f'    <div id="cap{i}" class="clip cap cap-{mode}" data-layout-allow-overlap data-start="{a}" data-duration="{round(b - a, 3)}" data-track-index="30"><span id="capt{i}" data-layout-allow-overlap>{txt}</span></div>\n'

    # one word at a time inside FACE windows; `emph` words in the emphasis font, digits stay in the main font
    import re as _re
    wcap_js = []
    for j, (ws, we, raw) in enumerate(WORDS):
        win = next(([a, b] for a, b in FACE if a - 0.03 <= ws < b - 0.05), None)
        if not win or any(a <= ws < b for a, b in HIDE): continue
        txt = FIX.get(raw, raw); txt = _re.sub(r"[.,!?;:\u2026\"]", "", txt)
        if not txt: continue
        key = txt.lower()
        if txt not in KEEP and not any(ch.isdigit() for ch in txt) and txt not in ("I", "I'm", "I've", "I'll", "I'd"): txt = key
        a = max(ws, win[0]); nxt = WORDS[j + 1][0] if j + 1 < len(WORDS) else DUR
        b = min(nxt, we + 0.45, win[1])
        if b - a < 0.04: continue
        cls = "it" if key in EMPH else ("num" if any(ch.isdigit() for ch in txt) else "")
        caps_html += f'    <div id="capw{j}" class="clip cap cap-w {cls}" data-layout-allow-overlap data-start="{round(a, 3)}" data-duration="{round(b - a, 3)}" data-track-index="31"><span id="captw{j}" data-layout-allow-overlap>{txt}</span></div>\n'
        if cls == "it": wcap_js.append(f"tl.fromTo('#captw{j}', {{opacity:0, filter:'blur(6px)'}}, {{opacity:1, filter:'blur(0px)', duration:0.12, ease:'power2.out'}}, {round(a, 3)});")

    # FACE-window overlays (behind the creator's head / in front of the creator)
    has_fg = os.path.exists(os.path.join(ROOT, "assets", "cam_fg.webm"))
    ov_behind = "".join(o["behind"] for o in OV); ov_front = "".join(o["front"] for o in OV)
    ov_css = "\n".join(o["css"] for o in OV); ov_js = "\n".join(o["js"] for o in OV)
    if ov_behind and not has_fg: print("WARNING: overlay(behind=...) used but assets/cam_fg.webm is missing - run 07_crops.sh (matte step); behind-layer will draw OVER the creator")
    fg_video = f'<video id="vFg" src="assets/cam_fg.webm" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="2"></video>' if (has_fg and OV) else ""
    ov_html = f'<svg width="0" height="0" style="position:absolute"><defs id="fxdefs"></defs></svg><div id="fBehind">{ov_behind}</div>{fg_video}<div id="fFront">{ov_front}</div>' if OV else ""

    guide_html = (f'<div id="safeguide"><div style="left:0;top:0;width:1080px;height:{SAFE_TOP}px"></div>'
                  f'<div style="left:0;top:{SAFE_BOTTOM}px;width:1080px;height:{SOFT_BOTTOM - SAFE_BOTTOM}px;background:rgba(255,140,0,.20);outline:2px dashed rgba(255,140,0,.9)"></div>'
                  f'<div style="left:0;top:{SOFT_BOTTOM}px;width:1080px;height:{1920 - SOFT_BOTTOM}px"></div>'
                  f'<div style="left:0;top:{CAP_BOTTOM}px;width:1080px;height:0;outline:2px dashed rgba(255,200,0,.95);background:none"></div>'
                  f'<div style="left:{RAIL_X}px;top:1000px;width:{1080 - RAIL_X}px;height:{SAFE_BOTTOM - 1000}px;background:rgba(255,200,0,.22);outline:2px solid rgba(255,200,0,.9)"></div>'
                  f'<div style="left:0;top:0;width:{SAFE_SIDE}px;height:1920px;background:rgba(255,0,60,.12);outline:none"></div>'
                  f'<div style="left:{1080 - SAFE_SIDE}px;top:0;width:{SAFE_SIDE}px;height:1920px;background:rgba(255,0,60,.12);outline:none"></div></div>\n') if GUIDE else ""
    if GUIDE: print("SAFE GUIDE IS ON - for snapshots only; rebuild without SAFE=1 before rendering")

    # camera visibility windows
    split_w, t = [], 0.0
    cuts = sorted(FACE + FULL)
    for a, b in cuts:
        if a > t: split_w.append([t, a])
        t = b
    if t < DUR - 0.01: split_w.append([t, DUR])      # reel ends on split
    cam_js = []
    for a, b in split_w:
        if a > 0: cam_js.append(f"tl.set('#camTop', {{opacity:1}}, {a});")
        cam_js.append(f"tl.set('#camTop', {{opacity:0}}, {b});")
    for a, b in FACE: cam_js.append(f"tl.set('#camFull', {{opacity:1}}, {a}); tl.set('#camFull', {{opacity:0}}, {b});")
    # SLOW ZOOM OUT on every full-screen face window:
    # the footage starts ZOOM_FACE enlarged and eases back to 100% over the window. Only the camera and the creator's cut-out move; captions, pills, the hook
    # and the agenda box sit on other layers and stay fixed.
    for k, (a, b) in enumerate(FACE): cam_js.append(f"tl.fromTo(['#vFull', '#vFg'], {{scale:{ZOOM_FACE}, transformOrigin:'50% 40%'}}, {{scale:1, duration:{round(b - a, 4)}, ease:'sine.out', immediateRender:{'true' if k == 0 else 'false'}}}, {a});")

    cap_js = "\n".join(wcap_js) + "".join(f"tl.fromTo('#capt{i}', {{scale:0.9, opacity:0.4}}, {{scale:1, opacity:1, duration:0.09, ease:'power2.out'}}, {a});" for i, (txt, a, b, mode, first) in enumerate(PIECES) if first)

    index = f"""<!doctype html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=1080, height=1920" />
        <title>{TITLE} — 9x16 (HyperFrames)</title>
        <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
        <link rel="stylesheet" href="assets/brand.css" />
        <style>
          @font-face {{ font-family: "HelvB"; src: @@FONT_MAIN_BOLD_SRC@@; font-weight: 700; }}
            @font-face {{ font-family: "HelvR"; src: @@FONT_MAIN_REGULAR_SRC@@; font-weight: 400; }}
            @font-face {{ font-family: "PlayIt"; src: @@FONT_ACCENT_SRC@@; font-style: normal; font-weight: 400 900; }}
            @font-face {{ font-family: "Hand"; src: url("assets/fonts/Caveat.ttf") format("truetype"); }}
          body {{ margin: 0; background: @@BG@@; }}
          #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: @@BG@@; }}
          #base {{ position: absolute; inset: 0; background: @@BG@@; z-index: 0; }}
          .blk {{ position: absolute; width: 1920px; height: 1080px; z-index: 1; }}
          .blk > .clip {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; }}
          .scene {{ z-index: 2; }}
          #camTop {{ position: absolute; left: 0; top: 960px; width: 1080px; height: 960px; z-index: 5; overflow: hidden; }}
          #camFull {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 6; overflow: hidden; opacity: 0; }}
          #camTop video, #camFull video {{ width: 100%; height: 100%; display: block; object-fit: cover; }}
          .cap {{ z-index: 20; pointer-events: none; }}
          .cap span {{ position: absolute; left: 70px; right: 70px; display: block; text-align: center; font-family: "HelvB", Helvetica, sans-serif; font-weight: 700; letter-spacing: -0.045em; line-height: 1; color: #FFFFFF;
            text-shadow: 0 3px 14px rgba(0,0,0,.7), 0 0 2px rgba(0,0,0,.6); }}
          .cap-s span {{ top: 874px; font-size: 56px; }}
          .cap-f span {{ top: 1079px; font-size: 62px; }}
          .cap-a span {{ top: 1180px; font-size: 62px; }}
          #safeguide {{ position: absolute; inset: 0; z-index: 99; pointer-events: none; }}
          #safeguide div {{ position: absolute; background: rgba(255,0,60,.28); outline: 2px solid rgba(255,0,60,.9); }}
          .cap-w span {{ top: 1085px; font-size: 92px; letter-spacing: -0.05em; text-shadow: 0 4px 22px rgba(0,0,0,.7), 0 0 3px rgba(0,0,0,.6); }}
          .cap-w.it span {{ top: 1072px; font-family: "PlayIt", serif; font-style: normal; font-weight: 500; font-size: 112px; letter-spacing: -0.04em; color: @@ACCENT@@; text-shadow: 0 4px 26px rgba(0,0,0,.8), 0 0 4px rgba(0,0,0,.7); }}
          .cap-w.num span {{ color: @@ACCENT@@; }}
          #camFull video {{ position: absolute; left: 0; top: 0; }}
          #vFull {{ z-index: 1; }} #fBehind {{ position: absolute; inset: 0; z-index: 2; }} #vFg {{ z-index: 3; }} #fFront {{ position: absolute; inset: 0; z-index: 4; }}
          .ov-hb {{ font-family: "HelvB", Helvetica, sans-serif; font-weight: 700; letter-spacing: -0.05em; color: #fff; line-height: 1; text-shadow: 0 4px 22px rgba(0,0,0,.55), 0 0 3px rgba(0,0,0,.5); }}
          .ov-pi {{ font-family: "PlayIt", serif; font-style: normal; font-weight: 500; color: @@ACCENT@@; letter-spacing: -0.04em; line-height: 1; text-shadow: 0 4px 22px rgba(0,0,0,.55), 0 0 3px rgba(0,0,0,.5); }}
          .ov-line {{ position: absolute; left: 0; width: 1080px; text-align: center; opacity: 0; white-space: nowrap; }}
          .ov-cm {{ position: absolute; width: 580px; padding: 20px 78px 16px 30px; border-radius: 28px; background: #fff; box-shadow: 0 22px 60px rgba(0,0,0,.45); opacity: 0; box-sizing: border-box; }}
          .ov-cm b {{ display: block; font-family: "HelvR", Helvetica, sans-serif; font-weight: 400; font-size: 36px; letter-spacing: -0.02em; color: #111; line-height: 1.12; }}
          .ov-cm i {{ display: block; margin-top: 8px; font-family: "HelvR", Helvetica, sans-serif; font-style: normal; font-size: 22px; color: #8e8e8e; }}
          .ov-cm svg {{ position: absolute; right: 26px; top: 22px; }}
          .ov-pill {{ position: absolute; left: 0; top: 0; width: 168px; height: 82px; margin: -41px 0 0 -84px; border-radius: 41px; background: rgba(12,10,9,.88); border: 2px solid @@ACCENT@@; box-shadow: 0 0 34px rgba(@@ACCENT_RGB@@,.45), 0 12px 30px rgba(0,0,0,.5); display: flex; align-items: center; justify-content: center; font-family: "HelvB", Helvetica, sans-serif; font-weight: 700; font-size: 46px; letter-spacing: -0.04em; color: #fff; opacity: 0; }}
          {ov_css}
          {chr(10).join(t["css"] for t in TOP)}
        </style>
      </head>
      <body>
        <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{DUR}" data-fps="24">
          <div id="base"></div>
    {blocks_html}{scenes_html}      <div id="camTop"><video id="vTop" src="assets/cam_top.mp4" playsinline data-has-audio="true" data-start="0" data-duration="{DUR}" data-track-index="0"></video></div>
          <div id="camFull"><video id="vFull" src="assets/cam_full.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="1"></video>{ov_html}</div>
    {caps_html}<div id="topLayer" style="position:absolute;inset:0;z-index:25;pointer-events:none">{"".join(t["html"] for t in TOP)}</div>{guide_html}    </div>
        <script>
          const tl = gsap.timeline({{ paused: true }});
          {chr(10).join(cam_js)}
          {cap_js}
          {(FX + ov_js) if (OV or TOP) else ""}
          {chr(10).join(t["js"] for t in TOP)}
          window.__timelines["main"] = tl;
        </script>
      </body>
    </html>
    """
    open(os.path.join(ROOT, "index.html"), "w").write(index)
    print(len(S), "scenes,", len(CAPS), "captions ->", len(PIECES), "pieces")


def comment(cid, left, top, text, meta="2h &nbsp; Reply"):
    """An Instagram-style comment card for overlay(front=...). Bring it in with slide('#<cid>', +-420, 0, t).
    One-line cards are ~98 px tall: three stack at top = 1196, 1294, 1392 and stay above SAFE_BOTTOM."""
    heart = '<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#8e8e8e" stroke-width="1.8"><path d="M12 20.5s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.6a4.3 4.3 0 0 1 7.5 2.7c0 5.6-7.5 10.2-7.5 10.2z"/></svg>'
    return f'<div id="{cid}" class="ov-cm" style="left:{left}px;top:{top}px"><b>{text}</b><i>{meta}</i>{heart}</div>'
