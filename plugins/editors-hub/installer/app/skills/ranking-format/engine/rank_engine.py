"""Ranking format engine (tier-list reel). Run inside a project:  python3 rank_engine.py
Reads plan.json (title, items, table times), words.json ([[start, end, word], ...] of the CUT) and layout.json (written by scripts/layout.py:
table scale + top). Writes index.html (HyperFrames), review_events.json, review_words.json.
Brand values (accent, fonts, background) are filled in from the creator profile by setup/apply_profile.py (the placeholders just below and in the CSS).
plan.json may also set: title_y, captions (true/false, default from setup), card_char_w (width of one card-name character in em, default 0.58).
Layers: assets/cam_full.mp4 (presenter, full frame the whole reel) -> title -> tier table S..F -> item cards -> captions.
An item card pops up big over the table when the item is named and shrinks into its tier row on the verdict."""
import json, os, re, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
TIERS = [("S", "#FF7F7E"), ("A", "#FFBF7F"), ("B", "#FFFF7F"), ("C", "#7FFF7F"), ("D", "#7FBFFF"), ("E", "#807FFF"), ("F", "#FF7FFE")]
ACCENT = "@@ACCENT@@"                                    # topic title + the item name when it is spoken as a caption
CARD_NAME = "@@CARD_NAME_COLOUR@@"                       # item name printed on the card
TITLE_STYLE = "@@TITLE_STYLE@@"                          # italic | normal
TITLE_CASE = "@@TITLE_CASE@@"                            # uppercase | none
CAPTIONS_DEFAULT = "@@CAPTIONS@@"                        # on | off
TW, TH, ROW, PITCH, LBL = 760, 500, 68, 72, 72          # table geometry at scale 1
CW, CH = 560, 315                                        # big card (16:9), centred on the table
CAP_GAP = 78                                             # caption line sits this far above the table top

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")

def label_html(label, cw=0.58):
    words, lines, cur = label.upper().split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > 14: lines.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    lines.append(cur); longest = max(len(l) for l in lines)
    size = min(84 if len(lines) < 3 else 62, int(500 / (cw * longest)))
    return f'<div class="nm" style="font-size:{size}px">{"<br/>".join(esc(l) for l in lines)}</div>'

def caption_groups(words, items, max_chars=24, max_words=6):
    """3-6 words on one line. A group never straddles an item name; the name itself is its own (orange) caption."""
    names = [(it["t_in"] - 0.03, it.get("t_name_end", it["t_in"] + 0.8)) for it in items]
    def in_name(t): return next((k for k, (a, b) in enumerate(names) if a <= t < b), -1)
    groups, cur, cur_k = [], [], -2
    def flush():
        nonlocal cur
        if cur: groups.append((cur, cur_k >= 0)); cur = []
    for w in words:
        k = in_name(w[0]); txt = re.sub(r"[.,!?\"“”]", "", w[2]) if not re.match(r"^[\d$£]", w[2]) else w[2].rstrip(".,")
        if cur and (k != cur_k or len(" ".join(c[2] for c in cur)) + len(txt) > max_chars or len(cur) >= max_words or w[0] - cur[-1][1] > 0.35): flush()
        cur_k = k; cur.append((w[0], w[1], txt))
        if w[2][-1] in ".!?" or (w[2][-1] == "," and len(cur) >= 3): flush()
    flush(); return groups

def build():
    plan = json.load(open(os.path.join(ROOT, "plan.json"))); words = json.load(open(os.path.join(ROOT, "words.json")))
    lay = json.load(open(os.path.join(ROOT, "layout.json"))) if os.path.exists(os.path.join(ROOT, "layout.json")) else {"scale": 1.0, "top": 1000}
    cw_ = float(plan.get("card_char_w", 0.58)); caps_on = plan.get("captions", CAPTIONS_DEFAULT != "off") not in (False, "off", "no")
    s, top = float(lay["scale"]), float(lay["top"]); D = float(plan["duration"]); items = plan["items"]
    words = [w for w in words if w[0] < D - 0.05]
    t_in, t_out = float(plan.get("table_in", 0)), plan.get("table_out")
    left = 540 - TW * s / 2; cap_top = top - CAP_GAP
    idx = {t[0]: i for i, t in enumerate(TIERS)}; EV, J, cards = [], [], ""
    per = {}; [per.setdefault(it["tier"].upper(), []).append(it) for it in items]
    for tier, lst in per.items():
        if tier not in idx: sys.exit(f"unknown tier {tier!r} (use S A B C D E F)")
    rows = "".join(f'<div class="row" id="r{n}" style="top:{i * PITCH}px"><div class="fl"></div><div class="lb" style="background:{c}">{n}</div></div>' for i, (n, c) in enumerate(TIERS))
    for k, it in enumerate(items):
        tier = it["tier"].upper(); lst = per[tier]; n = len(lst); slot = lst.index(it)
        tw = min(107.0, (TW - LBL - 16 - 8 * (n - 1)) / n); sc = tw / CW                      # thumbs shrink when a row gets crowded
        if tw < 60: print(f"WARNING: {n} items in {tier} tier - thumbnails are down to {tw:.0f}px wide; consider a wider table or fewer items on screen")
        tx = LBL + 8 + tw / 2 + slot * (tw + 8); ty = idx[tier] * PITCH + ROW / 2
        dx, dy = tx - TW / 2, ty - TH / 2; a, v = float(it["t_in"]) - 0.05, float(it["t_rank"])
        if not os.path.exists(os.path.join(ROOT, it["image"])): print(f"WARNING: missing image {it['image']}")
        cards += f'<div class="item" id="it{k}"><img src="{it["image"]}"/><div class="sh"></div>{label_html(it["label"], cw_)}</div>'
        J += [f"tl.fromTo('#it{k}', {{opacity:0, scale:0.55}}, {{opacity:1, scale:1, duration:0.32, ease:'back.out(1.7)'}}, {a:.3f});",
              f"tl.to('#it{k}', {{scale:1.03, duration:{max(0.1, v - a - 0.4):.3f}, ease:'none'}}, {a + 0.32:.3f});",
              f"tl.to('#it{k}', {{x:{dx:.1f}, y:{dy:.1f}, scale:{sc:.4f}, duration:0.42, ease:'power3.inOut'}}, {v:.3f});",
              f"tl.fromTo('#r{tier} .fl', {{opacity:0.28}}, {{opacity:0, duration:0.5, ease:'power2.out', immediateRender:false}}, {v + 0.38:.3f});",
              f"tl.fromTo('#r{tier} .lb', {{scale:1.25}}, {{scale:1, duration:0.4, ease:'back.out(2)', immediateRender:false}}, {v + 0.38:.3f});"]
        EV += [{"id": f"item{k}", "type": "graphic", "t0": round(a, 3), "t1": round(v, 3), "text": f"{it['label']} card"},
               {"id": f"rank{k}", "type": "graphic", "t0": round(v, 3), "t1": round(v + 0.45, 3), "text": f"{it['label']} -> {tier} tier"}]
    J.insert(0, f"tl.fromTo(['#rank', '#title'], {{opacity:0}}, {{opacity:1, duration:0.3, ease:'power2.out'}}, {t_in});")
    if t_out is not None: J.append(f"tl.to(['#rank', '#title'], {{opacity:0, duration:0.3, ease:'power2.in'}}, {float(t_out):.3f});")
    EV.insert(0, {"id": "table", "type": "graphic", "t0": t_in, "t1": float(t_out) if t_out is not None else D, "text": f"tier table + title '{plan['title']}'"})
    caps, groups = "", (caption_groups(words, items) if caps_on else [])
    for i, (g, is_name) in enumerate(groups):
        a = max(0, g[0][0] - 0.04); b = groups[i + 1][0][0][0] - 0.04 if i + 1 < len(groups) else min(D, g[-1][1] + 0.4); b = max(a + 0.1, min(b, g[-1][1] + 0.5))
        txt = " ".join(c[2] for c in g)
        caps += f'<div class="clip cap{" nm" if is_name else ""}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="30"><span>{esc(txt)}</span></div>\n'
        EV.append({"id": f"cap{i}", "type": "caption", "t0": round(a, 3), "t1": round(b, 3), "text": txt})
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" /><title>{esc(plan['title'])}</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face {{ font-family: "MainF"; src: @@FONT_MAIN_BOLD_SRC@@; font-weight: 800; }}
@font-face {{ font-family: "CapF"; src: @@FONT_CAPTION_SRC@@; font-weight: 500; }}
@font-face {{ font-family: "CapF"; src: @@FONT_CAPTION_SRC@@; font-weight: 600; }}
body {{ margin: 0; background: @@BG@@; }}
#root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: @@BG@@; font-family: "CapF", -apple-system, sans-serif; color: @@PAPER@@; }}
#vFull {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; display: block; z-index: 1; }}
#title {{ position: absolute; left: 0; width: 1080px; top: {plan.get('title_y', 286)}px; text-align: center; font-family: "MainF", -apple-system, sans-serif; font-weight: 800; font-style: {TITLE_STYLE}; font-size: 58px; letter-spacing: -0.01em; line-height: 1; color: {ACCENT}; text-transform: {TITLE_CASE}; text-shadow: 0 3px 14px rgba(0,0,0,.6); z-index: 10; opacity: 0; }}
#rank {{ position: absolute; left: {left:.1f}px; top: {top:.1f}px; width: {TW}px; height: {TH}px; transform: scale({s}); transform-origin: 0 0; z-index: 12; opacity: 0; }}
#table {{ position: absolute; inset: 0; background: #000; box-shadow: 0 0 0 6px #000, 0 24px 60px rgba(0,0,0,.55); }}
.row {{ position: absolute; left: 0; width: {TW}px; height: {ROW}px; background: #1b1a1d; }}
.row .lb {{ position: absolute; left: 0; top: 0; width: {LBL}px; height: {ROW}px; display: flex; align-items: center; justify-content: center; font: 800 26px/1 "MainF", -apple-system, Arial, sans-serif; color: #141414; }}
.row .fl {{ position: absolute; left: {LBL}px; top: 0; right: 0; height: {ROW}px; background: #fff; opacity: 0; }}
.item {{ position: absolute; left: {(TW - CW) / 2}px; top: {(TH - CH) / 2}px; width: {CW}px; height: {CH}px; overflow: hidden; opacity: 0; background: #222; box-shadow: 0 0 0 3px rgba(255,255,255,.85), 0 20px 50px rgba(0,0,0,.6); }}
.item img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block; }}
.item .sh {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,0) 35%, rgba(0,0,0,.55) 100%); }}
.item .nm {{ position: absolute; left: 10px; right: 10px; bottom: 20px; text-align: center; font-family: "MainF", Impact, sans-serif; font-weight: 800; line-height: .92; letter-spacing: -0.01em; color: {CARD_NAME}; -webkit-text-stroke: 5px #111; paint-order: stroke fill; text-shadow: 0 5px 0 rgba(0,0,0,.55); }}
.cap {{ position: absolute; inset: 0; z-index: 20; pointer-events: none; }}
.cap span {{ position: absolute; left: 40px; right: 40px; top: {cap_top:.0f}px; display: block; text-align: center; white-space: nowrap; font-weight: 500; font-size: 46px; letter-spacing: -0.045em; line-height: 1.2; color: @@PAPER@@; text-shadow: 0 3px 14px rgba(0,0,0,.85), 0 0 4px rgba(0,0,0,.7); }}
.cap.nm span {{ color: {ACCENT}; font-weight: 600; }}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{D}" data-fps="30">
  <video id="vFull" src="assets/cam_full.mp4" muted playsinline data-start="0" data-duration="{D}" data-track-index="1"></video>
  <div id="title">{esc(plan['title'])}</div>
  <div id="rank"><div id="table">{rows}</div>{cards}</div>
  {caps}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
tl.set({{}}, {{}}, {D});
window.__timelines["main"] = tl;
</script>
</body></html>
"""
    open(os.path.join(ROOT, "index.html"), "w").write(html)
    json.dump(EV, open(os.path.join(ROOT, "review_events.json"), "w"), indent=1)
    json.dump([{"w": w[2], "s": w[0], "e": w[1]} for w in words], open(os.path.join(ROOT, "review_words.json"), "w"))
    print(f"index.html written: {len(items)} items, {len(groups)} captions, table scale {s} top {top:.0f} (bottom {top + TH * s:.0f}), {D}s")

if __name__ == "__main__": build()
