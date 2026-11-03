#!/usr/bin/env python3
"""Step 7 - captions and stacks.   07_text.py <slug>
Builds the whole text layer of the finished 9:16 video (one transparent 1080x1920 PNG per frame, <work>/layer/):
  CAPTIONS  every spoken word, in short phrases, timed to the speech (from cut_words.json), one simple style
  STACKS    the few important phrases listed in plan.json "text": the caption becomes a left-aligned stack whose
            lines are revealed one by one as the speaker says them (gentle fade + a small move up or down)
and writes <work>/layer.json, <work>/captions.txt (every caption with its time: READ IT) and
<work>/text/preview_<id>.jpg for each stack. Run it again after ANY change to plan.json (text, captions, broll, frame).

plan.json:
  "captions": {"y": 1250,                        centre line of the captions when the footage fills the frame:
                                                 set it below the speaker's chin, per video (frames.py shows the pixel grid)
               "zones": [{"from": 12.4, "to": 18.0, "y": 1180}],   a different height for one shot / stretch
               "fix": {"acme": "Acme"},      spelling of names and brand words (matched without case or punctuation)
               "size": 54, "max_chars": 18, "max_words": 4}        optional
     When 16:9 footage sits INSIDE the vertical frame ("mode": "fit" on the main video or a b-roll clip) captions go
     in the lower half of that picture automatically, never in the black above or below it.
  "text": [{"id": "s1", "at": 12.4,              roughly when the phrase starts (cut-timeline seconds)
            "lines": ["when it comes", "to *marketing*"],    the speaker's exact words; last line large; *word* = key word
            "move": "up",                        up | down (default up)
            "anchor": [90, 1180]}]               optional: top-left of the block; default = at the caption position
     Each line is revealed as its first word is spoken; the stack clears when the next phrase starts.
Typography, all from the creator's profile: captions and small lines use the caption font (`font_caption`, else the regular
weight of the main font), large lines the main bold, tracking -50, white. *Key word*: the emphasis font (`font_accent`; the
shipped Playfair Display Italic when none is saved), in the accent colour, larger than the words around it (a figure stays
in the sans, in the accent colour). A font that cannot be found is reported as a FALLBACK: tell the creator, do not ship it.
Optional "style": {"accent": "#RRGGBB", "white": "#FFFFFF", "stack_size": 132}  (stack_size and captions.size default to the
creator's answers)."""
import hashlib, html, json, os, re, shutil, subprocess, sys
from fractions import Fraction
import numpy as np
from PIL import Image
import stt
from common import work, load, save, font_face, norm, base_frame, sheet, library, placed, frame_mode, num, ACCENT, CW, CH

W = work(sys.argv[1]); M = load(W, "meta.json"); plan = load(W, "plan.json") or sys.exit("no plan.json")
"cut" in M or sys.exit("render the cut first (05_render_cut.py)")
T = f"{W}/text"; os.makedirs(T, exist_ok=True); cw = load(W, "cut_words.json"); st = plan.get("style", {}); cap = plan.get("captions", {})
FPS = float(Fraction(M["fps"])); TOT = M["cut_dur"]; SIZE = cap.get("size", round(num("caption_size", 54))); BIG = st.get("stack_size", round(num("stack_size", 132)))
CHROME = next((c for c in (os.environ.get("CHROME_PATH"), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                           shutil.which("google-chrome"), shutil.which("chromium")) if c and os.path.exists(c)), None) or sys.exit("Google Chrome not found (set CHROME_PATH)")

P = stt.profile()
DEFAULT_KEY = {"file": "PlayfairDisplay-Italic.ttf"}                      # open-licence emphasis font shipped in assets/fonts
cap_src, cap_desc, cap_ok = font_face(P.get("font_caption") or P.get("font_main_regular") or P.get("font_main_bold"), "caption font")
big_src, big_desc, big_ok = font_face(P.get("font_main_bold"), "main bold font")
key_src, key_desc, key_ok = font_face(P.get("font_accent") or DEFAULT_KEY, "emphasis font")
SANS_FALLBACK = 'local("Arial"), local("Helvetica Neue"), local("Helvetica")'
BOLD_FALLBACK = SANS_FALLBACK.replace("Arial", "Arial Bold")
KEY_FALLBACK = 'local("Georgia Italic"), local("Georgia")'
faces = (f'@font-face{{font-family:"Sans";font-weight:400;src:{cap_src or SANS_FALLBACK}}}'
         f'@font-face{{font-family:"Sans";font-weight:700;src:{big_src or BOLD_FALLBACK}}}'
         f'@font-face{{font-family:"Key";src:{key_src or KEY_FALLBACK}}}')
sans_name = f"{cap_desc} | {big_desc}"; key_name = key_desc
for ok, d in ((cap_ok, cap_desc), (big_ok, big_desc), (key_ok, key_desc)):
    if not ok:
        print(f"FALLBACK {d}. Tell the creator; do not ship the fallback as final (see setup/SETUP.md, fonts).")
print(f"sans: {sans_name} | key word: {key_name}")
CSS = """<!doctype html><meta charset="utf-8"><style>%s
html,body{margin:0;background:transparent;overflow:hidden}
.l{white-space:nowrap;font-family:"Sans",Arial,sans-serif;letter-spacing:-0.05em;padding-right:0.06em;color:%s;font-kerning:normal}
.s{font-weight:400;line-height:1.0}
.g{font-weight:700;line-height:0.94}
.k{font-family:"Key",serif;font-weight:400;font-size:1.2em;line-height:0;letter-spacing:-0.015em;color:%s;padding:0 0.05em 0 0.02em}
.n{color:%s}
.row{height:%dpx;width:%dpx;display:flex;align-items:center;justify-content:center}
#b{position:absolute;left:80px;top:80px;display:flex;flex-direction:column;align-items:flex-start}
</style>""" % (faces, st.get("white", "#FFFFFF"), st.get("accent", st.get("orange", ACCENT)), st.get("accent", st.get("orange", ACCENT)), 140, CW)
SHADOW = lambda B: f"text-shadow:0 0 {B * 0.3:.1f}px rgba(0,0,0,.45),0 {B * 0.03:.1f}px {B * 0.09:.1f}px rgba(0,0,0,.5)"
READY = "document.fonts.load('400 100px \"Sans\"').then(()=>document.fonts.load('700 100px \"Sans\"')).then(()=>document.fonts.load('100px \"Key\"')).then(()=>document.fonts.ready)"


def chrome(w, h, *a):
    return subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                           f"--window-size={w},{h}", "--default-background-color=00000000", "--virtual-time-budget=4000",
                           "--allow-file-access-from-files", *a], capture_output=True, text=True).stdout


def markup(t):
    out = ""
    for k, part in enumerate(re.split(r"\*(.+?)\*", t)):
        out += (f'<span class="{"n" if any(c.isdigit() for c in part) else "k"}">{html.escape(part)}</span>' if k % 2 else html.escape(part))
    return out


plain = lambda t: t.replace("*", "")
FIX = {norm(k): v for k, v in cap.get("fix", {}).items()}
def spell(word):
    core = norm(word)
    if core in FIX:
        m = re.match(r"^(\W*)(.*?)(\W*)$", word); return m.group(1) + FIX[core] + m.group(3)
    return word

# ---- 1. stacks: find each one's exact words in the transcript -------------------------------------------------------
cards = []
for c in plan.get("text", []):
    lines = [{"t": l} if isinstance(l, str) else dict(l) for l in c["lines"]]
    toks = [norm(w) for l in lines for w in plain(l["t"]).split()]; toks = [t for t in toks if t]
    i0 = next((i for i in range(len(cw)) if cw[i][1] >= c["at"] - 0.4 and [norm(x[0]) for x in cw[i:i + len(toks)]] == toks), None)
    if i0 is None or cw[i0][1] > c["at"] + 3:
        near = " ".join(x[0] for x in cw if c["at"] - 0.5 <= x[1] <= c["at"] + 4)
        sys.exit(f"stack {c['id']}: the lines must be the speaker's exact words in order. Around {c['at']:.2f}s they say: \"{near}\"")
    i1 = i0 + len(toks) - 1; k = i0
    for n_, l in enumerate(lines):
        l["at"] = round(max(0, cw[k][1] - 0.04), 3); k += len([w for w in plain(l["t"]).split() if norm(w)])
        l.setdefault("big", (n_ == len(lines) - 1 and len(lines) > 1) or "*" in l["t"])
    if any("*" in l["t"] and not l["big"] for l in lines):
        sys.exit(f"stack {c['id']}: the *key word* belongs in a large line")
    nxt = cw[i1 + 1][1] if i1 + 1 < len(cw) else TOT
    end = min(nxt - 0.02, cw[i1][2] + 1.0) if nxt - cw[i1][2] < 1.2 else cw[i1][2] + 0.9
    cards.append({"id": c["id"], "i0": i0, "i1": i1, "at": lines[0]["at"], "end": round(min(TOT, end), 3), "lines": lines,
                  "move": c.get("move", "up"), "anchor": c.get("anchor")})
cards.sort(key=lambda c: c["i0"])
for p, q in zip(cards, cards[1:]):
    q["i0"] > p["i1"] or sys.exit(f"stacks {p['id']} and {q['id']} use the same words")

# ---- 2. captions: every other word, in short phrases -----------------------------------------------------------------
MAXC, MAXW = cap.get("max_chars", 18), cap.get("max_words", 4); taken = {i for c in cards for i in range(c["i0"], c["i1"] + 1)}; caps = []
def clause(idx):
    """Split one clause into phrases of similar length (no single stray word left at the end)."""
    if not idx:
        return
    L = [len(cw[i][0]) + 1 for i in idx]; n = max(-(-sum(L) // MAXC), -(-len(idx) // MAXW)); target = sum(L) / n; groups = [[]]; acc = 0
    for k, i in enumerate(idx):
        left = len(idx) - k
        if groups[-1] and len(groups) < n and (acc + L[k] / 2 > target * len(groups) or len(groups[-1]) >= MAXW) and left >= n - len(groups):
            groups.append([])
        groups[-1].append(i); acc += L[k]
    for g in groups:
        txt = " ".join(spell(cw[i][0]) for i in g).rstrip(".,;:")
        caps.append({"i0": g[0], "i1": g[-1], "t": txt, "at": round(max(0, cw[g[0]][1] - 0.03), 3)})
cur = []
for i, x in enumerate(cw):
    if i in taken:
        clause(cur); cur = []; continue
    if cur and x[1] - cw[cur[-1]][2] > 0.35:
        clause(cur); cur = []
    cur.append(i)
    if x[0][-1] in ".?!,;:":
        clause(cur); cur = []
clause(cur)
events = sorted([("cap", c) for c in caps] + [("card", c) for c in cards], key=lambda e: e[1]["at"])
for (k, e), nx in zip(events, events[1:] + [None]):
    if k == "cap":
        last = cw[e["i1"]][2]; e["end"] = round(min(nx[1]["at"] if nx else TOT, last + 0.6), 3)
    elif nx:
        e["end"] = round(min(e["end"], nx[1]["at"]), 3)
covered = sorted([i for c in caps for i in range(c["i0"], c["i1"] + 1)] + list(taken))
covered == list(range(len(cw))) or sys.exit("internal error: not every word is captioned")

# ---- 3. where the text sits at each moment -------------------------------------------------------------------------
lib = {str(c["id"]): c for c in library()} | {c["clip"]: c for c in library()} | {os.path.basename(c["clip"]): c for c in library()}
mode, focus = frame_mode(M, plan); regions = []     # (from, to, picture top, picture height) where footage sits INSIDE the frame
if mode == "fit":
    sw, sh, x, y = placed(M["w"], M["h"], "fit"); regions.append((0, TOT, y, sh))
for b in plan.get("broll", []):
    c = lib.get(str(b["clip"]))
    if c:
        bm = b.get("mode", "fit" if c["w"] > c["h"] else "fill"); sw, sh, x, y = placed(c["w"], c["h"], bm)
        regions.insert(0, (b["at"], b["at"] + b["dur"], y, sh) if bm == "fit" else (b["at"], b["at"] + b["dur"], 0, CH))
def where(t):
    """(caption centre y, lowest allowed y for text) at time t."""
    for z in cap.get("zones", []):
        if z["from"] <= t < z["to"]:
            return z["y"], CH - 300
    for a, b_, top, h in regions:
        if a <= t < b_ and h < CH:
            return round(top + h * 0.76), top + h - 24          # lower half of the actual picture
        if a <= t < b_:
            break
    return cap.get("y", 1250), CH - 300

# ---- 4. render the words (headless Chrome) --------------------------------------------------------------------------
RH = 140; sprites = []
for s0 in range(0, len(caps), 50):
    part = caps[s0:s0 + 50]; page = f"{T}/caps_{s0}.html"
    open(page, "w").write(CSS + "".join(f'<div class="row"><span class="l s" style="font-size:{SIZE}px;{SHADOW(SIZE)}">{html.escape(c["t"])}</span></div>' for c in part)
                          + f"<script>{READY}</script>")
    png = f"{T}/caps_{s0}.png"; chrome(CW, RH * len(part), f"--screenshot={png}", f"file://{page}"); im = Image.open(png).convert("RGBA")
    for k, c in enumerate(part):
        row = im.crop((0, k * RH, CW, (k + 1) * RH)); bb = row.getbbox() or sys.exit(f"caption \"{c['t']}\" rendered empty")
        c["w"] = bb[2] - bb[0]; sprites.append((row.crop(bb), bb[0], bb[1] - RH // 2))
    os.remove(png)
    if max(c["w"] for c in part) > CW - 130:
        print("WARNING a caption is wider than the safe width; lower captions.max_chars")
for c in cards:
    spans = "".join(f'<div class="l {"g" if l["big"] else "s"}">{markup(spell(l["t"]) if "*" not in l["t"] else l["t"])}</div>' for l in c["lines"])
    js = ("const SIZE=%d,MAXW=%d;let B=%d;function lay(){const b=document.getElementById('b'),L=[...b.children];"
          "const set=B=>L.forEach(e=>{const big=e.classList.contains('g');const s=big?B:SIZE;e.style.fontSize=s+'px';e.style.marginLeft=(big?0:B*0.035)+'px';"
          "e.style.marginTop=(big?B*0.05:SIZE*0.12)+'px';e.style.textShadow=`0 0 ${s*0.3}px rgba(0,0,0,.45),0 ${s*0.03}px ${s*0.09}px rgba(0,0,0,.5)`});"
          "set(B);let w=b.getBoundingClientRect().width;if(w>MAXW){B=B*MAXW/w;set(B)}"
          "const h=location.hash.slice(1);if(h!=='all')L.forEach((e,i)=>{if(String(i)!==h)e.style.visibility='hidden'});const q=b.getBoundingClientRect();"
          "document.getElementById('o').textContent=JSON.stringify({w:q.width,h:q.height,big:B});}%s.then(lay);") % (SIZE, CW - 180, BIG, READY)
    page = f"{T}/{c['id']}.html"; open(page, "w").write(CSS + f'<div id="b">{spans}</div><pre id="o" style="display:none"></pre><script>{js}</script>')
    dom = chrome(CW + 200, 1000, "--dump-dom", f"file://{page}#all")
    try:
        info = json.loads(html.unescape(dom.split('<pre id="o" style="display:none">')[1].split("</pre>")[0]))
    except Exception:
        sys.exit(f"{c['id']}: Chrome did not lay the stack out\n{dom[-300:]}")
    c["w"], c["h"], c["big_px"] = round(info["w"]), round(info["h"]), round(info["big"]); c["imgs"] = []
    for i in range(len(c["lines"])):
        png = f"{T}/{c['id']}_{i}.png"; chrome(CW + 200, 1000, f"--screenshot={png}", f"file://{page}#{i}")
        im = Image.open(png).convert("RGBA"); os.remove(png); im.getbbox() or sys.exit(f"{c['id']} line {i} rendered empty")
        c["imgs"].append(im.crop((0, 0, min(im.width, c["w"] + 160), min(im.height, c["h"] + 160))))     # block sits at (80,80) in this crop
    yc, low = where(c["at"] + 0.05)
    x, y = c["anchor"] if c["anchor"] else ((CW - c["w"]) // 2, round(yc - SIZE * 0.62))
    if not c["anchor"]:
        y = min(y, low - c["h"])
    c["x"], c["y"] = int(x), int(y)
    if c["x"] < 60 or c["x"] + c["w"] > CW - 60 or c["y"] < 200 or c["y"] + c["h"] > CH - 250:
        print(f"WARNING stack {c['id']} at ({c['x']},{c['y']}) size {c['w']}x{c['h']} is outside the safe area")

# ---- 5. compose every frame ------------------------------------------------------------------------------------------
D = f"{W}/layer"; shutil.rmtree(D, ignore_errors=True); os.makedirs(D); N = round(TOT * FPS); held = {}; REV, OUT, MOVE = 0.3, 0.08, 26
def fade(im, a, dy):
    if a >= 0.999 and dy == 0:
        return im, 0
    arr = np.asarray(im).copy(); arr[..., 3] = (arr[..., 3].astype(np.float32) * a).astype(np.uint8); return Image.fromarray(arr, "RGBA"), dy
for f in range(N):
    t = f / FPS; key = None; ops = []
    c = next((c for c in cards if c["at"] <= t < c["end"]), None)
    if c:
        ex = min(1.0, (c["end"] - t) / OUT); st_ = []
        for l, im in zip(c["lines"], c["imgs"]):
            p = min(1.0, (t - l["at"]) / REV); e = 1 - (1 - p) ** 3 if p > 0 else 0; st_.append(round(e, 3))
            if e > 0:
                ops.append((im, e * ex, round((1 - e) * MOVE * (1 if c["move"] == "up" else -1)), c["x"] - 80, c["y"] - 80))
        key = ("card", c["id"], tuple(st_), round(ex, 2))
    else:
        k = next((k for k, c_ in enumerate(caps) if c_["at"] <= t < c_["end"]), None)
        if k is not None:
            yc, _ = where(t); sp, sx, sy = sprites[k]; ops.append((sp, 1.0, 0, sx, yc + sy)); key = ("cap", k, yc)
    fp = f"{D}/f_{f:05d}.png"
    if key in held:
        os.link(held[key], fp); continue
    fr = Image.new("RGBA", (CW, CH))
    for im, a, dy, x, y in ops:
        g, dy = fade(im, a, dy); fr.alpha_composite(g, (max(0, x), max(0, y + dy)))
    fr.save(fp, compress_level=1); held[key] = fp

# ---- 6. report -------------------------------------------------------------------------------------------------------
sig = hashlib.md5(json.dumps([plan.get("text"), plan.get("captions"), plan.get("broll"), plan.get("frame"), plan.get("style"), cw], sort_keys=True).encode()).hexdigest()
out_cards = [{k: v for k, v in c.items() if k != "imgs"} for c in cards]
save(W, "layer.json", {"sig": sig, "frames": N, "seq": f"{D}/f_%05d.png", "captions": caps, "cards": out_cards})
rows = [f"{e['at']:7.2f}-{e['end']:7.2f}  " + (e["t"] if k == "cap" else "STACK " + e["id"] + ": " + " / ".join(plain(l["t"]) for l in e["lines"])) for k, e in events]
open(f"{W}/captions.txt", "w").write("\n".join(rows) + "\n"); print("\n".join(rows))
print(f"\n{len(caps)} captions + {len(cards)} stacks cover all {len(cw)} words ({len(cards) / TOT * 60:.1f} stacks a minute). Read the list above for wrong words or names (captions.fix).")
for c in cards:
    vis = c["end"] - c["lines"][-1]["at"]
    if vis < 0.6:
        print(f"WARNING stack {c['id']}: the last line is on screen only {vis:.2f}s before the next words. End the stack on a phrase followed by a pause, or put more words in the last line.")
    tiles = []; acc = Image.new("RGBA", c["imgs"][0].size)
    for n_, (l, im) in enumerate(zip(c["lines"], c["imgs"])):
        acc.alpha_composite(im); nxt = c["lines"][n_ + 1]["at"] if n_ + 1 < len(c["lines"]) else c["end"]
        fr = base_frame(M, plan, min(TOT - 0.1, (l["at"] + 0.3 + nxt) / 2)).convert("RGBA"); fr.alpha_composite(acc, (max(0, c["x"] - 80), max(0, c["y"] - 80)))
        tiles.append((fr.convert("RGB"), f"{c['id']} line {n_ + 1}  {l['at']:.2f}s"))
    pv = f"{T}/preview_{c['id']}.jpg"; sheet(tiles, pv, len(tiles), 460); print("preview:", pv, "(shown over the main video; b-roll is not in the preview)")
