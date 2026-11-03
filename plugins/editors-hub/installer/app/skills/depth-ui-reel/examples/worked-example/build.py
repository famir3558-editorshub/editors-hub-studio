#!/usr/bin/env python3
"""Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.
A 15.6 s depth UI reel built from invented placeholder words (words.json here is synthetic, not a real recording). Copy it as a new
reel's build.py and replace the beats with the reel's own script, sentence by sentence.

Real images it expects (any missing one becomes a plain placeholder tile and is listed in placeholders.txt):
  assets/yt/t1.jpg ... t9.jpg   the channel's real video thumbnails
  assets/reels/r01.jpg ...      real reel covers (the creator's own, or other creators' in their space)
  assets/real/avatar.jpg        the channel's profile picture (new_reel.sh copies the creator's own from setup)"""
import json, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "..", "..", "engine"))   # runs from the skill folder; in a real reel project the engine sits beside build.py
import depth_engine as D
DUR = 15.6
D.init(ROOT, json.load(open(os.path.join(ROOT, "words.json"))), DUR, title="Depth UI reel - worked example", emph={"storefront"})
print("captions:", " | ".join(D.captions()))
YT = lambda ns: [f"assets/yt/t{n}.jpg" for n in ns]; RL = lambda ns: [f"assets/reels/r{n:02d}.jpg" for n in ns]
# The channel the cards show. Defaults to the creator's own; for a client's reel use the client's real name, handle and avatar.
CHANNEL = dict(name="@@BRAND_NAME@@", handle="@@HANDLE@@", avatar="assets/real/avatar.jpg")

# camera: punch in / out on the sentence cuts (scales above the creator's punch strength setting are clamped by the engine)
D.camera([(0, 3.66, 1.0, 1.035), (3.66, 6.09, 1.085, 1.11), (6.09, 8.03, 1.0, 1.03), (8.03, 11.62, 1.07, 1.10), (11.62, DUR, 1.0, 1.04)])

# 1  "a channel past 50,000 subscribers": the real video grid behind the head + the real channel card ticking up to the real figure
D.behind(D.yt_grid("ytg", YT([1, 2, 3, 4, 5, 6, 7, 8, 9, 2, 6, 1, 5, 3, 8])))
D.blur_in("#ytg", 0.12, y=520, d=0.6); D.drift("#ytg-in", 0.12, 3.6, -250); D.blur_out("#ytg", 3.52)
D.ev("ytg", "graphic", 0.12, 3.86, "YouTube videos grid behind the head (the channel's real thumbnails)")
D.front(D.channel("c1", top=1272, **CHANNEL))
D.blur_in("#c1", 1.5, y=60, d=0.4, b=18); D.counter("#c1-n", 50, 1.72, suffix="K", done=D.GREEN)
D.js("tl.to('#c1-b', {scale:0.9, duration:0.08, yoyo:true, repeat:1, ease:'power2.out'}, 2.87);")
D.js("tl.to('#c1-b', {background:'#2a2a2a', color:'#fff', duration:0.12}, 2.95); tl.call(function(){document.querySelector('#c1-b').textContent='Subscribed';}, null, 2.95); tl.call(function(){document.querySelector('#c1-b').textContent='Subscribe';}, null, 2.9);")
D.blur_out("#c1", 3.5, y=80, d=0.3); D.ev("c1", "graphic", 1.5, 3.8, "Channel card: count ticks up to the real figure")

# 2  "in just 60 seconds": ring beside the head
D.behind(D.ring("ring", 790, 150)); D.pop("#ring", 4.55, 0.35)
D.js("tl.to('#ring-c', {strokeDashoffset:0, duration:1.25, ease:'power1.inOut'}, 4.85);"); D.counter("#ring-n", 60, 4.85, ease="power1.inOut")
D.fade("#ring", 5.95, 0.2); D.ev("ring", "graphic", 4.55, 6.15, "60 seconds ring")

# 3  "know exactly who is watching": viewers round the head, one lights up
PTS = [(150, 470), (205, 700), (120, 905), (935, 430), (905, 640), (950, 880)]
D.behind(D.people("vw", PTS, label="Your viewer", chosen=4))
for k in range(6): D.pop(f"#vw{k}", round(6.18 + k * 0.07, 2), 0.26)
D.light_up("#vw4", 6.76); D.js("tl.to(['#vw0','#vw1','#vw2','#vw3','#vw5'], {opacity:0.28, scale:0.86, duration:0.25}, 6.86);")
D.js("tl.fromTo('#vwl', {opacity:0, y:14, filter:'blur(8px)'}, {opacity:1, y:0, filter:'blur(0px)', duration:0.25}, 7.1);")
D.fade("#vw", 7.9, 0.16); D.ev("vw", "graphic", 6.18, 8.06, "Viewer icons, one chosen: 'Your viewer'")

# 4  "not a social media feed": reel covers, grey + red wash, X
D.behind(D.ig_grid("igf", RL(range(1, 13))))
D.blur_in("#igf", 8.08, y=520, d=0.5); D.drift("#igf-in", 8.08, 2.1, -170)
D.js("tl.to('#igf-in', {filter:'grayscale(1) brightness(.6)', duration:0.3}, 8.72); tl.fromTo('#igf-red', {opacity:0}, {opacity:1, duration:0.3}, 8.72);")
D.pop("#igf-x", 8.8, 0.3); D.shake("#igf", 8.84); D.blur_out("#igf", 9.98, y=620, d=0.3)
D.ev("igf", "graphic", 8.08, 10.28, "Social feed grid (real reel covers) turns red, X")

# 5/6  "more like a storefront" ... "or they will not subscribe": shelves + awning behind the head, subscribe button in front
D.behind(D.shelves("store", [("Start here", YT([1, 4, 7])), ("Popular videos", YT([2, 5, 8])), ("Playlists", YT([3, 6, 9]))], awning=True))
D.blur_in("#store", 10.12, y=-520, d=0.55)
D.js("tl.fromTo('#store-awn', {scaleY:0, transformOrigin:'50% 0%'}, {scaleY:1, duration:0.4, ease:'back.out(2.2)'}, 11.05);")
for k in range(3): D.js(f"tl.fromTo('#store .shelf:nth-child({k + 2})', {{opacity:0, x:60, filter:'blur(12px)'}}, {{opacity:1, x:0, filter:'blur(0px)', duration:0.35, ease:'power3.out'}}, {10.3 + k * 0.14:.2f});")
D.js("tl.fromTo('#store', {y:0}, {y:-50, duration:5.2, ease:'none', immediateRender:false}, 10.7);")
D.ev("store", "graphic", 10.12, DUR, "Channel as a storefront: shelves + awning behind the head")
D.front(D.channel("c2", top=1372, count="50K", **CHANNEL)); D.blur_in("#c2", 12.05, y=70, d=0.4, b=18)
D.js("tl.to('#c2-b', {scale:1.07, boxShadow:'0 0 34px rgba(255,255,255,.55)', duration:0.3, yoyo:true, repeat:1, ease:'sine.inOut'}, 13.3);")
D.js("tl.to('#c2-b', {background:'#3a1512', color:'#ff8f86', duration:0.2}, 14.85);"); D.shake("#c2", 14.88); D.pop("#c2-x", 14.85, 0.28)
D.js("tl.to('#c2 .av, #c2 .ci', {filter:'grayscale(1)', opacity:0.6, duration:0.3}, 14.9);")
D.ev("c2", "graphic", 12.05, DUR, "Channel card: Subscribe button pulses, then goes red")
D.write()
