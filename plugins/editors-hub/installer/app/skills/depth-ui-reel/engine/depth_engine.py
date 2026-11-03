"""Depth UI reel engine.
The creator full frame for the WHOLE reel. Layers, bottom to top:
  cam_full.mp4 -> dim -> BEHIND (graphics their head covers) -> cam_fg.webm (their cut-out) -> FRONT (graphics on their chest) -> captions.
A project's build.py does:   import depth_engine as D;  D.init(...);  D.behind(html); D.front(html); D.css(...); D.blur_in(...) ...;  D.write()
NO head sticker, NO cursor. Numbers are always in the main font, never the emphasis font. Positive = green, negative = red, accent = focal.

Brand values are filled into this file by setup/apply_profile.py (the @-tokens below). Missing real images (thumbnails, reel covers, the
avatar) degrade to plain placeholder tiles and are listed in placeholders.txt, so a build never breaks for want of a picture."""
import json, re, os, sys
ACCENT, ACCENT_RGB, ACCENT_LIGHT, ON_ACCENT = "@@ACCENT@@", "@@ACCENT_RGB@@", "@@ACCENT_LIGHT@@", "@@ON_ACCENT@@"
BG_RGB, PAPER, BRAND = "@@BG_RGB@@", "@@PAPER@@", "@@BRAND_NAME@@"
DIM_LEVEL, PUNCH_MAX = "@@DIM_LEVEL@@", "@@PUNCH_MAX@@"
if ACCENT.startswith("@") or PUNCH_MAX.startswith("@"):
    sys.exit("depth_engine: setup has not been run. In the skill folder: python3 setup/apply_profile.py (see setup/SETUP.md)")
DIM_LEVEL, PUNCH_MAX = float(DIM_LEVEL), float(PUNCH_MAX)
GREEN, RED = "#2FA65A", "#E5372B"      # positive / negative keep their meaning in every brand
MISSING = []                           # real images that were not found: shown as placeholder tiles, listed on write()
S = dict(J=[], EV=[], behind=[], front=[], css=[], caps="", capjs=[], root=".")

def init(root, words, dur, fps="30000/1001", title="Depth UI reel", emph=(), dim=True):
    """words = [[start, end, word], ...] of the CUT (cut/words.json). emph = lower-case words shown in the accent colour and emphasis font (2-5 per reel, never numbers)."""
    S.update(root=root, words=[w for w in words if w[0] < dur - 0.1], dur=dur, fps=fps, title=title, emph=set(emph), dim=dim)

def have(path):
    """True when a project-relative image exists. Pieces call this so a missing real image becomes a placeholder, not a broken build."""
    ok = os.path.exists(os.path.join(S["root"], path))
    if not ok and path not in MISSING: MISSING.append(path)
    return ok
def ev(i, typ, a, b, text): S["EV"].append({"id": i, "type": typ, "t0": round(a, 3), "t1": round(b, 3), "text": text})
def js(line): S["J"].append(line)
def behind(html): S["behind"].append(html)
def front(html): S["front"].append(html)
def css(text): S["css"].append(text)

# ---- motion (all seek-safe GSAP on the one root timeline `tl`)
def blur_in(sel, t, y=420, d=0.5, b=26): js(f"tl.fromTo('{sel}', {{opacity:0, y:{y}, filter:'blur({b}px)', scale:1.04}}, {{opacity:1, y:0, filter:'blur(0px)', scale:1, duration:{d}, ease:'power3.out'}}, {t});")
def blur_out(sel, t, y=-380, d=0.34, b=22): js(f"tl.to('{sel}', {{opacity:0, y:{y}, filter:'blur({b}px)', duration:{d}, ease:'power2.in'}}, {t});")
def pop(sel, t, d=0.3): js(f"tl.fromTo('{sel}', {{opacity:0, scale:0.55, filter:'blur(10px)'}}, {{opacity:1, scale:1, filter:'blur(0px)', duration:{d}, ease:'back.out(1.6)'}}, {t});")
def fade(sel, t, d=0.25): js(f"tl.to('{sel}', {{opacity:0, filter:'blur(8px)', duration:{d}, ease:'power2.in'}}, {t});")
def drift(sel, t, d, y=-200): js(f"tl.fromTo('{sel}', {{y:0}}, {{y:{y}, duration:{d}, ease:'none'}}, {t});")
def shake(sel, t): js(f"tl.to('{sel}', {{x:-9, duration:0.05, yoyo:true, repeat:5, ease:'sine.inOut'}}, {t});")
def counter(sel, to, t, d=1.25, suffix="", done=None, ease="power2.out"):
    """Plain number ticking up (no digit wheel); done = colour it turns on landing (GREEN for a win)."""
    col = f"el.style.color=c.n>{to - 0.5}?'{done}':'';" if done else ""
    js(f"(function(){{const c={{n:0}}, el=document.querySelector('{sel}'); tl.fromTo(c, {{n:0}}, {{n:{to}, duration:{d}, ease:'{ease}', onUpdate:function(){{el.textContent=Math.round(c.n)+'{suffix}';{col}}}}}, {t});}})();")
def camera(blocks):
    """blocks = [(start, end, scale_from, scale_to), ...] covering the reel. Step the scale on SENTENCE cuts (punch in ~1.07-1.09, back to 1.0),
    with a slow drift inside each block. Both camera layers move together; graphics and captions do not."""
    for k, (a, b, s0, s1) in enumerate(blocks):
        s0, s1 = min(s0, PUNCH_MAX), min(s1, PUNCH_MAX)     # the creator's punch-in strength is the ceiling
        js(f"tl.fromTo(['#vFull', '#vFg'], {{scale:{s0}, transformOrigin:'50% 38%'}}, {{scale:{s1}, duration:{b - a:.3f}, ease:'none', immediateRender:{'true' if k == 0 else 'false'}}}, {a});")
        if k: ev(f"zoom{k}", "zoom", a, b, f"punch {'in' if s0 > 1.04 else 'out'} ({s0:.2f})")

# ---- captions: 1-3 words, on their chest
def captions(max_chars=11, max_words=3):
    groups, cur = [], []
    def flush():
        if cur: groups.append(list(cur)); cur.clear()
    for w in S["words"]:
        txt = w[2]; clean = txt.rstrip(".,") if re.match(r"^[\d$£]", txt) else re.sub(r"[.,!?\"“”]", "", txt)
        if clean.lower() in S["emph"]: flush(); groups.append([(w[0], w[1], clean, True)]); continue
        if cur and (len(" ".join(c[2] for c in cur)) + len(clean) > max_chars or len(cur) >= max_words or w[0] - cur[-1][1] > 0.18): flush()
        cur.append((w[0], w[1], clean, False))
        if txt[-1] in ".,!?": flush()
    flush()
    for i, g in enumerate(groups):
        a = max(0, g[0][0] - 0.04); b = groups[i + 1][0][0] - 0.04 if i + 1 < len(groups) else min(S["dur"], g[-1][1] + 0.4)
        b = min(b, g[-1][1] + 0.5); txt = " ".join(c[2] for c in g); em = g[0][3]
        S["caps"] += f'<div id="cap{i}" class="clip cap{" em" if em else ""}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="30"><span id="capt{i}">{txt}</span></div>\n'
        S["capjs"].append(f"tl.fromTo('#capt{i}', {{opacity:0, filter:'blur(14px)', scale:1.12}}, {{opacity:1, filter:'blur(0px)', scale:1, duration:0.22, ease:'power3.out'}}, {a:.3f});" if em
                          else f"tl.fromTo('#capt{i}', {{opacity:0.35, scale:0.94}}, {{opacity:1, scale:1, duration:0.08, ease:'power2.out'}}, {a:.3f});")
        ev(f"cap{i}", "caption", a, b, txt)
    return [" ".join(c[2] for c in g) for g in groups]

# ---- pieces (HTML strings; pass them to behind() / front())
PERSON = '<svg viewBox="0 0 48 48"><circle cx="24" cy="18" r="8" fill="none" stroke="currentColor" stroke-width="3.6"/><path d="M9 41c1.5-9 7.5-13 15-13s13.5 4 15 13" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round"/></svg>'
YTLOGO = '<svg viewBox="0 0 28 20" width="34" height="24"><rect width="28" height="20" rx="5" fill="#FF0033"/><path d="M11 5.5 L19 10 L11 14.5 Z" fill="#fff"/></svg>'
IGTABS = ('<svg viewBox="0 0 24 24" width="34" height="34"><path d="M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z" fill="none" stroke="#fff" stroke-width="1.8"/></svg>'
          '<svg class="on" viewBox="0 0 24 24" width="34" height="34"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="#fff" stroke-width="1.8"/><path d="M10 8.5 L16 12 L10 15.5 Z" fill="#fff"/></svg>'
          '<svg viewBox="0 0 24 24" width="34" height="34"><circle cx="12" cy="9" r="3.4" fill="none" stroke="#fff" stroke-width="1.8"/><path d="M5 20c.8-4 3.6-6 7-6s6.2 2 7 6" fill="none" stroke="#fff" stroke-width="1.8"/></svg>')
def _tile(cls, f): return f'<div class="{cls}"><img src="{f}"/></div>' if have(f) else f'<div class="{cls} ph"></div>'
def thumbs(files): return "".join(_tile("th", f) for f in files)
def covers(files): return "".join(_tile("cv", f) for f in files)
def yt_grid(i, files, top=150, tabs=("Home", "Videos", "Shorts", "Playlists"), on="Videos"):
    """Dark YouTube 'Videos' tab: 3 columns of 16:9 thumbnails. Inner grid is #<i>-in (drift() it). REAL thumbnails only."""
    t = "".join(f'<span{" class=on" if x == on else ""}>{x}</span>' for x in tabs)
    return f'<div id="{i}" class="panel yt" style="top:{top}px"><div class="tabs">{YTLOGO}{t}</div><div id="{i}-in" class="grid3">{thumbs(files)}</div></div>'
def ig_grid(i, files, top=150):
    """Dark Instagram reels grid: 3 columns of covers, plus a red wash #<i>-red and a big X #<i>-x for 'not this'."""
    return f'<div id="{i}" class="panel ig" style="top:{top}px"><div class="tabs igt">{IGTABS}</div><div id="{i}-in" class="grid3 r">{covers(files)}</div><div id="{i}-red" class="redwash"></div><div id="{i}-x" class="bigx">&#10005;</div></div>'
def shelves(i, rows, top=150, awning=False):
    """YouTube channel home as shelves: rows = [(label, [3 thumbnails]), ...]. awning=True adds the striped shop awning (#<i>-awn)."""
    aw = f'<div id="{i}-awn" class="awn"></div>' if awning else ""
    return f'<div id="{i}" class="panel yt st" style="top:{top}px">{aw}' + "".join(f'<div class="shelf"><h5>{l}</h5><div class="row">{thumbs(f)}</div></div>' for l, f in rows) + '</div>'
def channel(i, name, handle, avatar, top=1272, count="0", unit="subscribers", button="Subscribe"):
    """YouTube channel card for the chest area. Count is #<i>-n, button #<i>-b, red X badge #<i>-x. Real name, handle, avatar and figure only
    (a missing avatar becomes a letter tile and is listed as a placeholder)."""
    av = f'<img class="av" src="{avatar}"/>' if have(avatar) else f'<div class="av ph">{name[:1]}</div>'
    return (f'<div id="{i}" class="chan" style="top:{top}px">{av}<div class="ci"><b>{name}</b><em>{handle}</em><span><i id="{i}-n">{count}</i> {unit}</span></div>'
            f'<div id="{i}-b" class="sub">{button}</div><div id="{i}-x" class="xb">&#10005;</div></div>')
def ring(i, x, y, label="seconds"):
    """Glowing accent-colour ring with a number (#<i>-n) and a stroke (#<i>-c, dashoffset 628.3 -> 0)."""
    return (f'<div id="{i}" class="ring" style="left:{x}px;top:{y}px"><svg viewBox="0 0 240 240"><circle cx="120" cy="120" r="100" fill="rgba(0,0,0,.55)" stroke="rgba(255,255,255,.16)" stroke-width="10"/>'
            f'<circle id="{i}-c" cx="120" cy="120" r="100" fill="none" stroke="{ACCENT}" stroke-width="10" stroke-linecap="round" stroke-dasharray="628.3" stroke-dashoffset="628.3" transform="rotate(-90 120 120)"/></svg><b id="{i}-n">0</b><em>{label}</em></div>')
def people(i, points, label=None, chosen=None):
    """Person icons round the head: points = [(x, y), ...] centres. #<i>0.. ; label sits under points[chosen] as #<i>l."""
    h = "".join(f'<div id="{i}{k}" class="pv" style="left:{x - 62}px;top:{y - 62}px">{PERSON}</div>' for k, (x, y) in enumerate(points))
    if label is not None: h += f'<div id="{i}l" class="pvl" style="left:{points[chosen][0] - 120}px;top:{points[chosen][1] + 96}px">{label}</div>'
    return f'<div id="{i}" style="inset:0">{h}</div>'
def light_up(sel, t): js(f"tl.to('{sel}', {{color:'{ON_ACCENT}', background:'{ACCENT}', borderColor:'{ACCENT_LIGHT}', scale:1.28, boxShadow:'0 0 60px rgba({ACCENT_RGB},.9)', duration:0.25, ease:'back.out(2)'}}, {t});")

BASE_CSS = """
@font-face { font-family: "SFD"; src: @@FONT_CAPTION_SRC@@; font-weight: 600; }
@font-face { font-family: "SFD"; src: @@FONT_MAIN_REGULAR_SRC@@; font-weight: 500; }
@font-face { font-family: "HelvB"; src: @@FONT_MAIN_BOLD_SRC@@; font-weight: 700; }
@font-face { font-family: "Ivy"; src: @@FONT_ACCENT_SRC@@; }
body { margin: 0; background: @@BG@@; }
#root { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: @@BG@@; font-family: "SFD", -apple-system, sans-serif; color: #fff; }
#root video { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; display: block; }
#vFull { z-index: 1; } #dim { position: absolute; inset: 0; z-index: 2; }
#fBehind { position: absolute; inset: 0; z-index: 3; } #vFg { z-index: 4; } #fFront { position: absolute; inset: 0; z-index: 5; }
#fBehind > *, #fFront > * { position: absolute; }
.cap { position: absolute; inset: 0; z-index: 20; pointer-events: none; }
.cap span { position: absolute; left: 60px; right: 60px; top: @@CAPTION_Y@@px; display: block; text-align: center; font-weight: 600; font-size: @@CAPTION_SIZE@@px; letter-spacing: -0.055em; line-height: 1; color: #fff; text-shadow: 0 3px 16px rgba(0,0,0,.75), 0 0 3px rgba(0,0,0,.6); }
.cap.em span { top: calc(@@CAPTION_Y@@px - 34px); font-family: "Ivy", serif; font-weight: 400; font-size: @@EMPH_SIZE@@px; letter-spacing: -0.04em; color: @@ACCENT@@; text-shadow: 0 6px 30px rgba(0,0,0,.8), 0 0 40px rgba(@@ACCENT_RGB@@,.35); }
.panel { left: 80px; width: 920px; height: 800px; border-radius: 30px; background: #0f0f0f; box-shadow: 0 30px 80px rgba(0,0,0,.6); overflow: hidden; opacity: 0; }
.panel.ig { background: #0b0d10; }
.tabs { height: 84px; display: flex; align-items: center; gap: 44px; padding: 0 30px; font-size: 30px; font-weight: 500; color: #9a9a9a; border-bottom: 2px solid #262626; position: relative; z-index: 2; background: inherit; }
.tabs .on { color: #fff; box-shadow: 0 31px 0 -27px #fff; } .tabs.igt { justify-content: space-around; } .tabs.igt svg { opacity: .5; box-shadow: none; } .tabs.igt svg.on { opacity: 1; }
.grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; padding: 16px; }
.th { aspect-ratio: 16/9; border-radius: 12px; overflow: hidden; background: #222; } .th img, .cv img { width: 100%; height: 100%; object-fit: cover; display: block; }
.grid3.r { gap: 6px; padding: 6px; } .cv { aspect-ratio: 9/14; overflow: hidden; background: #222; }
.redwash { position: absolute; inset: 84px 0 0 0; background: rgba(229,55,43,.34); opacity: 0; }
.bigx { position: absolute; right: 26px; top: 110px; width: 110px; height: 110px; border-radius: 50%; background: #E5372B; color: #fff; font-size: 62px; font-weight: 600; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 50px rgba(229,55,43,.8); opacity: 0; }
.awn { height: 74px; background: repeating-linear-gradient(90deg, @@ACCENT@@ 0 76.66px, @@PAPER@@ 76.66px 153.33px); clip-path: polygon(0 0, 100% 0, 100% 72%, 95.83% 100%, 91.66% 72%, 87.5% 100%, 83.33% 72%, 79.16% 100%, 75% 72%, 70.83% 100%, 66.66% 72%, 62.5% 100%, 58.33% 72%, 54.16% 100%, 50% 72%, 45.83% 100%, 41.66% 72%, 37.5% 100%, 33.33% 72%, 29.16% 100%, 25% 72%, 20.83% 100%, 16.66% 72%, 12.5% 100%, 8.33% 72%, 4.16% 100%, 0 72%); }
.shelf { padding: 14px 18px 0; } .shelf h5 { margin: 0 0 12px 4px; font-size: 30px; font-weight: 600; letter-spacing: -0.03em; } .shelf .row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.ring { width: 240px; height: 240px; opacity: 0; filter: drop-shadow(0 0 34px rgba(@@ACCENT_RGB@@,.75)); } .ring svg { position: absolute; inset: 0; }
.ring b { position: absolute; left: 0; right: 0; top: 58px; text-align: center; font-family: "HelvB", sans-serif; font-size: 96px; letter-spacing: -0.05em; line-height: 1; }
.th.ph, .cv.ph, .chan .av.ph { background: linear-gradient(135deg, #2a2a2a, #1b1b1b); } .chan .av.ph { display: flex; align-items: center; justify-content: center; font-size: 44px; font-weight: 600; color: #bdbdbd; }
.ring em { position: absolute; left: 0; right: 0; top: 156px; text-align: center; font-style: normal; font-size: 26px; font-weight: 500; color: #d8d2cb; }
.pv { position: absolute; width: 124px; height: 124px; border-radius: 50%; background: rgba(20,18,16,.82); border: 3px solid rgba(255,255,255,.5); color: #fff; opacity: 0; box-shadow: 0 10px 30px rgba(0,0,0,.5); }
.pv svg { position: absolute; inset: 22px; }
.pvl { position: absolute; width: 240px; text-align: center; font-size: 30px; font-weight: 600; letter-spacing: -0.04em; text-shadow: 0 2px 12px rgba(0,0,0,.9); opacity: 0; }
.chan { left: 150px; width: 780px; height: 132px; border-radius: 34px; background: rgba(15,15,15,.94); border: 1.5px solid rgba(255,255,255,.14); box-shadow: 0 18px 50px rgba(0,0,0,.55); opacity: 0; }
.chan .av { position: absolute; left: 20px; top: 20px; width: 92px; height: 92px; border-radius: 50%; object-fit: cover; }
.chan .ci { position: absolute; left: 132px; top: 17px; line-height: 1.14; } .chan .ci b { display: block; font-size: 33px; font-weight: 600; letter-spacing: -0.035em; }
.chan .ci em { display: block; font-style: normal; font-size: 23px; color: #a8a8a8; font-weight: 500; } .chan .ci span { display: block; font-size: 25px; color: #dcdcdc; font-weight: 500; }
.chan .ci i { font-style: normal; font-family: "HelvB", sans-serif; letter-spacing: -0.03em; }
.chan .sub { position: absolute; right: 22px; top: 36px; height: 60px; padding: 0 28px; border-radius: 30px; background: #fff; color: #0f0f0f; font-size: 27px; font-weight: 600; letter-spacing: -0.02em; line-height: 60px; }
.chan .xb { position: absolute; right: 2px; top: 6px; width: 54px; height: 54px; border-radius: 50%; background: #E5372B; color: #fff; font-size: 30px; font-weight: 600; text-align: center; line-height: 54px; box-shadow: 0 0 26px rgba(229,55,43,.8); opacity: 0; }
"""

def write():
    D = S["dur"]
    t, m = round(DIM_LEVEL + 0.10, 2), round(max(DIM_LEVEL - 0.06, 0), 2)
    S["css"].insert(0, f"#dim {{ background: linear-gradient(180deg, rgba({BG_RGB},{t}), rgba({BG_RGB},{m}) 60%, rgba({BG_RGB},{t})); }}")
    if S["dim"]: S["J"].insert(0, "tl.fromTo('#dim', {opacity:0}, {opacity:1, duration:0.5, ease:'power2.out'}, 0.05);")
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<title>{S['title']}</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{BASE_CSS}{chr(10).join(S['css'])}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{D}" data-fps="30">
  <video id="vFull" src="assets/cam_full.mp4" muted playsinline data-start="0" data-duration="{D}" data-track-index="1"></video>
  {'<div id="dim"></div>' if S['dim'] else ''}
  <div id="fBehind">{''.join(S['behind'])}</div>
  <video id="vFg" src="assets/cam_fg.webm" muted playsinline data-start="0" data-duration="{D}" data-track-index="2"></video>
  <div id="fFront">{''.join(S['front'])}</div>
  {S['caps']}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(S['J'])}
{chr(10).join(S['capjs'])}
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
    open(os.path.join(S["root"], "index.html"), "w").write(html)
    json.dump(S["EV"], open(os.path.join(S["root"], "review_events.json"), "w"), indent=1)
    json.dump([{"w": w[2], "s": w[0], "e": w[1]} for w in S["words"]], open(os.path.join(S["root"], "review_words.json"), "w"))
    open(os.path.join(S["root"], "placeholders.txt"), "w").write("\n".join(MISSING) + ("\n" if MISSING else ""))
    print(f"index.html written: {len(S['EV'])} events, {D}s")
    if MISSING: print(f"PLACEHOLDERS: {len(MISSING)} real images not found, plain tiles used (listed in placeholders.txt). Say so when handing over:", ", ".join(MISSING[:6]), "..." if len(MISSING) > 6 else "")
