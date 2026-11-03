#!/usr/bin/env python3
"""psf.py - Personal Short Form. A thin layer over reel_engine.py + kit.py (the Business Short Form Reels engine) that gives this format's
look in a few calls, so a reel's build.py stays short.

    import reel_engine as E, kit as K, psf as P
    P.setup(ROOT, DUR, FACE, FULL, "Title", emph={...}, keep={"Claude"})     # one-word captions for the whole video + engine init
    P.broll("b01", a, b, [("assets/broll/b1.mp4", 77, 21), ...])             # FULL window: the creator's own footage, whole frame, hard cuts
    P.screen("s01", a, b, [("assets/screen/s1.mp4", 163, 98)], zooms=[...])   # SPLIT window: screen recording on top, the creator on the bottom
    K.hook("line one", "line two", out)                                       # 2-line hook on the opening (kit)
    P.comments([(user, text, t), ...], out)                                   # Instagram notification stack below the caption
    P.logos("lg", [("assets/logos/notion.png", 4.1), ...], out)              # real brand logos on white tiles below the caption
    K.OF.append(html); K.ojs(js)                                              # any one-off graphic on the creator (frame coords, opacity:0, GLOBAL seconds)
    P.finish()

MODES (the remainder of the timeline that is in neither FACE nor FULL is SPLIT):
  FACE  = the creator full screen (slow zoom out built in) + a small motion graphic below the caption word
  FULL  = B-roll over the whole frame (the camera is hidden; the creator's voice carries on)
  SPLIT = screen recording in a card on the top half, the creator on the bottom half
All times are GLOBAL seconds on the cut. Use P.sw(frame) for every mode switch: frame / 23.976 - 0.002 (a time rounded up lands one frame late).

CAPTIONS: ONE WORD AT A TIME, the caption font (bold), lower-case, white; key words in the accent colour and the emphasis font; NO pop-in
animation; each word stays on screen until the next word starts (through pauses and through every mode switch); the last word holds to the end."""
import json, os, re
import reel_engine as E
import kit as K

FPS = 24000 / 1001
sw = lambda f: round(f * 1001 / 24000 - 0.002, 4)          # exact switch time for a frame of the cut
fr = lambda t: int(round((t + 0.002) * 24000 / 1001))      # the frame a switch time sits on
ST = dict(cap_y=1085, split_cap_y=905, split=[])
LOWER_KEEP = ("I", "I'm", "I've", "I'll", "I'd")


def setup(root, dur, face, full, title, emph=(), keep=(), fix=None, merge=(("et cetera", "etc"),), cap_y=1085, split_cap_y=905):
    """Writes captions.json (one entry per spoken word, end = the next word's start) from the cut's words.json and starts the engine.
    emph : words set in the accent colour and the emphasis font (2-5 per ~5 s, the words that carry the point). A figure in emph takes the accent colour but stays in the caption font.
    keep : words that keep their capitals (names, brands: "Claude", "Notion"). Everything else is lower-case, except I / I'm / I've...
    fix  : {heard: shown} for mis-heard words. merge: spoken phrases shown as one caption (("et cetera", "etc"), ("thirteen thousand", "13,000")).
    cap_y: top of the caption line when the creator is full screen or under B-roll (about 95 px under the creator's chin, never on the creator's face).
    split_cap_y: caption top in SPLIT windows (the gap between the recording card and the creator's head)."""
    emph = {x.lower() for x in emph}; fix = dict(fix or {}); keep = set(keep)
    W = [[float(a), float(b), str(t)] for a, b, t, *_ in json.load(open(os.path.join(root, "words.json")))]
    norm = lambda x: re.sub(r"[^a-z0-9']", "", x.lower())
    for spoken, shown in merge:
        sp = spoken.lower().split(); i = 0
        while i <= len(W) - len(sp):
            if [norm(x[2]) for x in W[i:i + len(sp)]] == sp: W[i:i + len(sp)] = [[W[i][0], W[i + len(sp) - 1][1], shown]]
            i += 1
    caps = []
    for j, (a, b, t) in enumerate(W):
        txt = re.sub(r"[.!?;:\"]|(?<!\d),|,(?!\d)", "", t); txt = fix.get(txt, txt); key = txt.lower()
        if not txt: continue
        if txt not in keep and txt not in LOWER_KEEP and not any(c.isdigit() for c in txt): txt = key
        shown = txt.replace("'", "&rsquo;")
        if key in emph: shown = ('<i class="nu">%s</i>' if any(c.isdigit() for c in txt) else '<i class="em">%s</i>') % shown
        caps.append({"text": shown, "start": round(a, 3), "end": round(W[j + 1][0] if j + 1 < len(W) else dur, 3)})
    json.dump(caps, open(os.path.join(root, "captions.json"), "w"), indent=0)
    E.init(root, dur, face, full, title=title, words=None, emph=set(), keep=set(), hide=[])       # words=None: every caption comes from captions.json, so nothing drops at a switch
    t, sp = 0.0, []
    for a, b in sorted(face + full):
        if a > t + 0.01: sp.append([t, a])
        t = max(t, b)
    if t < dur - 0.01: sp.append([t, dur])
    ST.update(cap_y=cap_y, split_cap_y=split_cap_y, split=sp)
    return caps


# ---------------------------------------------------------------- FULL window: B-roll over the whole frame
BCSS = """#{ID}-in{opacity:1 !important;transform:none !important;filter:none !important} #{ID}-in2{transform:none !important;filter:none !important}
    #{ID}-box .de-grid, #{ID}-box .lg-orbs{display:none} #{ID}-box{background:#000}"""
def _clips(a, b, clips, style, z0=5):
    """clips: [(file, start_frame, n_frames)] in order, frames on the CUT's clock. Each clip overlaps the next by 2 frames (the next sits above) so no black frame can show."""
    body = ""
    for k, (src, f0, nf) in enumerate(clips):
        t = max(0, f0 * 1001 / 24000 - 0.002 - a); last = k == len(clips) - 1
        d = min(b - a - t, nf * 1001 / 24000 + (0 if last else 0.07))
        body += K.clip(src, t, d, style + ";z-index:%d" % (z0 + k))
    return body
def broll(sid, a, b, clips):
    """Their own footage over the whole frame, hard cuts, no glass / grid / focus pull. The files are 1080x1920, video only, cut to exact frame counts
    (scripts/cut_clips.py); horizontal footage is already letterboxed in the file. a and b come from P.sw(frame); a window STARTS or ENDS on an edit cut."""
    return K.raw(sid, a, b, True, _clips(a, b, clips, "position:absolute;left:0;top:0;width:1080px;height:1920px"), BCSS, "")


# ---------------------------------------------------------------- SPLIT window: screen recording on top, the creator on the bottom
SCSS = """#{ID}-in{opacity:1 !important;transform:none !important;filter:none !important} #{ID}-in2{filter:none !important}
    .scard{position:absolute;border-radius:26px;overflow:hidden;background:#0B0B0C;border:2px solid rgba(255,255,255,.22);box-shadow:0 26px 70px rgba(0,0,0,.65);z-index:5}
    .szw{position:absolute;inset:0}"""
def screen(sid, a, b, clips, zooms=(), ratio=16 / 9):
    """A screen recording in a rounded card on the top half while the creator talks on the bottom half. The window is whatever is in neither FACE nor FULL:
    leave [a, b] out of both lists. clips as in broll() but cut with fit "screen" (no letterbox). ratio = the recording's width / height (16/9 for a
    desktop, 9/19.5 for a phone): the card is sized to it inside the 1000 x 600 space, never cropped.
    zooms: [(t, scale, ox, oy, dur)] - at GLOBAL second t the picture eases to `scale`, zooming toward the point (ox %, oy %) of the recording; (t, 1) zooms
    back out. Use them to land on the button / field / number the creator is naming as the creator says it (a 1.5-2.2x zoom reads well on a phone)."""
    bw, bh = 1000, 600; w = bw if bw / ratio <= bh else round(bh * ratio); h = round(w / ratio)
    body = '<div class="scard" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx"><div id="{ID}-zw" class="szw">%s</div></div>' % (
        (1080 - w) // 2, 34 + (bh - h) // 2, w, h, _clips(a, b, clips, "position:absolute;left:0;top:0;width:100%;height:100%", 1))
    js = ""
    for z in zooms:
        t, sc = z[0], z[1]; ox, oy = (z[2], z[3]) if len(z) > 3 else (50, 50); d = z[4] if len(z) > 4 else 0.5
        if t <= a + 0.02: js += 'tl.set(q("zw"), {scale:%s, transformOrigin:"%s%% %s%%"}, 0);' % (sc, ox, oy)
        else: js += '__tt(q("zw"), {scale:%s, transformOrigin:"%s%% %s%%", duration:%s, ease:"power2.inOut"}, T(%s));' % (sc, ox, oy, d, t)
    return K.raw(sid, a, b, False, body, SCSS, js)


# ---------------------------------------------------------------- on the creator (FACE windows): graphics BELOW the caption word
def comments(items, out, top=1200, scale=0.8, keep=2):
    """Instagram notification banners dropping in below the caption, newest on top pushing the pile down; only `keep` on screen at once.
    items: [(username, text, t)] oldest first. Wording is invented unless the creator supplied real comments: list it in the report."""
    n = len(items)
    K.OF.append('<div style="position:absolute;inset:0;transform:scale(%s);transform-origin:540px %dpx">' % (scale, top) + "".join(
        K.banner("X", top, ti, bo).replace("{ID}-nX", "pc%d" % i).replace("{ID}X", "pc%d" % i) for i, (ti, bo, t) in enumerate(items)) + '</div>')
    js = ""
    for i, (ti, bo, t) in enumerate(items):
        js += "opop('#pc%d', %s); oout('#pc%d', %s);" % (i, t, i, out); K.ac(max(t, 0.06), "pop", -22)
        for k in range(i): js += "tl.to('#pc%d', {y:%d, duration:0.45, ease:'power3.out'}, %s);" % (k, 226 * (i - k), t)
        if i >= keep: js += "tl.to('#pc%d', {opacity:0, duration:0.3, ease:'power2.inOut'}, %s);" % (i - keep, t)
    K.ojs(js)

def logos(pre, items, out, top=1212, size=150, gap=26):
    """REAL brand logos (official files, transparent PNG or SVG in assets/logos/) on white rounded tiles in a centred row below the caption, each landing
    on the word that names the brand. items: [(src, t)] or [(src, t, label)]. Never redraw a logo by hand; never recolour or stretch it."""
    n = len(items); x0 = (1080 - (n * size + (n - 1) * gap)) // 2
    for i, it in enumerate(items):
        src, t = it[0], it[1]; lab = it[2] if len(it) > 2 else ""
        K.OF.append('<div id="%s%d" style="position:absolute;left:%dpx;top:%dpx;width:%dpx;height:%dpx;border-radius:%dpx;background:#fff;box-shadow:0 16px 40px rgba(0,0,0,.5);opacity:0;display:flex;align-items:center;justify-content:center;box-sizing:border-box;padding:%dpx">'
                    '<img src="%s" style="max-width:100%%;max-height:100%%;object-fit:contain;display:block"/>%s</div>' % (pre, i, x0 + i * (size + gap), top, size, size, round(size * 0.24), round(size * 0.16), src,
                    ('<span style="position:absolute;left:0;right:0;top:%dpx;text-align:center;font-family:SFB,HelvB,sans-serif;font-weight:700;font-size:28px;letter-spacing:-.02em;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.8)">%s</span>' % (size + 10, lab)) if lab else ""))
        K.ojs("opop('#%s%d', %s); oout('#%s%d', %s);" % (pre, i, t, pre, i, out)); K.ac(t, "pop", -23)


# ---------------------------------------------------------------- finish: the look, then build
def finish(css=""):
    cy, sy = ST["cap_y"], ST["split_cap_y"]
    base = """
    @font-face { font-family: "SFB"; src: @@FONT_CAPTION_SRC@@; font-weight: 700; }
    #camTop { opacity: 0; }                                     /* the bottom-half camera shows only inside SPLIT windows (the engine switches it on there) */
    .cap span, .cap-f span, .cap-a span, .cap-s span { top: %dpx; font-family: "SFB", "SF Pro Display", -apple-system, "HelvB", Helvetica, sans-serif; font-weight: 700; font-size: 92px; letter-spacing: -0.03em; line-height: 1; color: #fff;
      text-shadow: 0 4px 22px rgba(0,0,0,.7), 0 0 3px rgba(0,0,0,.6); transform: none !important; opacity: 1 !important; filter: none !important; }      /* no pop-in */
    .cap span:has(i.em) { top: %dpx; }
    .cap span i.em { font-family: "PlayIt", serif; font-style: normal; font-weight: 500; font-size: 112px; letter-spacing: -0.04em; color: @@ACCENT@@; text-shadow: 0 4px 26px rgba(0,0,0,.8), 0 0 4px rgba(0,0,0,.7); }
    .cap span i.nu { font-style: normal; color: @@ACCENT@@; }
    .cap-s span { top: %dpx; font-size: 84px; } .cap-s span:has(i.em) { top: %dpx; } .cap-s span i.em { font-size: 102px; }
    .hk1, #hk2 { font-family: "SFB", "SF Pro Display", -apple-system, "HelvB", Helvetica, sans-serif; letter-spacing: -0.035em; }
    """ % (cy, cy - 13, sy, sy - 11)
    if ST["split"] and ST["split"][0][0] <= 0.001: K.ojs("tl.set('#camTop', {opacity:1}, 0);")       # a reel that opens on SPLIT
    K.flush(css=base + css)
    E.build()
