#!/usr/bin/env python3
"""Check the edit plan BEFORE building anything.   plan_check.py <slug>
Reads <project>/content_map.json and edit_plan.json and prints the plan as a table with every problem it can see:
a visual with no reason, a low-priority line given a big treatment (or a key moment given nothing), a thin intro,
density that does not follow the sections' energy, the same treatment used again too soon, too much text,
assets still to find, and entities / statistics / frameworks from the content map that the plan never shows."""
import json, sys
from common import pj
PJ = pj(sys.argv[1])
C = json.load(open(f"{PJ}/content_map.json")); PL = json.load(open(f"{PJ}/edit_plan.json")); P = json.load(open(f"{PJ}/project.json"))
WHY = ("explain", "demonstrate", "evidence", "example", "simplify", "curiosity", "emphasis", "momentum", "memory")
BIG = ("split", "full"); STATES = ("float", "panel", "split", "full", "punch"); TEXT = ("title", "emph", "rows", "quote", "term"); TARGET = {"high": (5, 12), "medium": (2.5, 7), "low": (0, 3)}
mo = sorted(PL["moments"], key=lambda m: m["t"]); issues = []; warn = issues.append; DUR = P["dur"]
print(f"{'time':>7}  {'len':>4}  {'sc':>2}  {'state':6} {'component':11} {'why':11} id / what")
last = {}
for i, m in enumerate(mo):
    print(f"{m['t']:7.1f}  {m['end'] - m['t']:4.1f}  {m['score']:2d}  {m['state']:6} {m['component']:11} {m['why']:11} {m['id']}: {m.get('communicates', '')[:70]}")
    if m["why"] not in WHY: warn(f"{m['id']}: why '{m['why']}' is not a reason from the list {WHY}")
    if m["score"] <= 2 and m["state"] in BIG: warn(f"{m['id']}: score {m['score']} but a {m['state']} treatment. Spend that on something that matters more")
    if m["score"] >= 5 and m["state"] == "float" and m["component"] not in ("title", "tracker") and m["t"] > 45: warn(f"{m['id']}: a top-priority moment with only a float. Would a split or a full-screen explanation land it better?")
    if m["component"] in TEXT and m["why"] in ("explain", "demonstrate", "simplify"): warn(f"{m['id']}: explaining with text ({m['component']}). Can it be SHOWN (flow, diagram, metaphor, real example)?")
    key = (m["component"], m.get("variant", "auto"))
    if m["component"] not in ("tracker", "title", "term", "framework") and key in last and m.get("variant", "auto") != "auto" and m["t"] - last[key] < 150:
        warn(f"{m['id']}: {key[0]}/{key[1]} again only {m['t'] - last[key]:.0f}s after the last one")
    last[key] = m["end"]
    a = m.get("asset")
    if a and not a.get("file"): warn(f"{m['id']}: asset still to find (tier {a.get('tier', '?')}): {a.get('want', '')}")
    if a and a.get("tier") == 6: warn(f"{m['id']}: stock imagery planned. Is there a specific real example?")
    if i and m["t"] < mo[i - 1]["end"] - 0.3 and not {m["component"], mo[i - 1]["component"]} & {"tracker", "title"}: warn(f"{m['id']} overlaps {mo[i - 1]['id']}")
print()
for s in C.get("sections", []):
    d = max(1e-6, (s["b"] - s["a"]) / 60); ms = [m for m in mo if s["a"] <= m["t"] < s["b"]]; lo, hi = TARGET.get(s.get("energy", "medium"), (2.5, 7)); per = len(ms) / d
    flag = "" if lo <= per <= hi else ("  <- thin" if per < lo else "  <- heavy")
    print(f"section {s['id']:8} {s.get('kind', ''):10} energy {s.get('energy', '?'):6} {s['b'] - s['a']:6.0f}s  {len(ms):3d} moments  {per:4.1f}/min (aim {lo}-{hi}){flag}")
    if flag and not (s.get("kind") in ("story", "nuance") and per < lo): warn(f"section {s['id']} ({s.get('energy')}) has {per:.1f} moments/min, outside {lo}-{hi}")
    if s.get("kind") == "story" and any(m["state"] == "full" and m["end"] - m["t"] > 6 for m in ms): warn(f"section {s['id']} is a story: a long full-screen graphic takes their face away at the emotional moment")
intro = [m for m in mo if m["t"] < 45]
if len(intro) < 5: warn(f"intro has {len(intro)} moments in the first 45 s: it should be the densest, most designed part of the video (6-10)")
real = [m["t"] for m in mo if m["component"] not in ("title", "tracker")]
if not real or min(real) > 3.0: warn("no meaningful visual change in the first 3 s: open talking head -> motion graphic / split / punch-in that supports the line -> back")
ev = sorted({0.0} | {x for m in mo for x in (m["t"], m["end"]) if x <= 30}) + [30.0]
for x, y in zip(ev, ev[1:]):
    if y - x > 5.2: warn(f"opening: {y - x:.1f}s with no visual development ({x:.1f}s -> {y:.1f}s); the first 30 s should change every 2-5 s (a punch-in or reframing counts when no graphic genuinely helps)")
if C.get("learn") and len(C["learn"]) > 1 and not any(m["component"] == "preview" for m in intro): warn("the creator previews what the viewer will learn, but the intro has no `preview` (structure shown, answers held back)")
shown = " ".join(json.dumps(m).lower() for m in mo)
for e in C.get("entities", []):
    if e.get("name") and e["name"].lower() not in shown: warn(f"entity never shown: {e['name']} ({e.get('type')}) at {e.get('t')}s. Deliberate? If not, find the real thing")
for f in C.get("frameworks", []):
    n = sum(1 for m in mo if m["component"] in ("framework", "tracker", "flow") and f.get("id", "~") in json.dumps(m))
    if f.get("name") and n < 1 + len(f.get("returns", [])): warn(f"framework '{f['name']}' is introduced and returned to {len(f.get('returns', []))} time(s) but the plan shows its map {n} time(s) (tag those moments with \"{f.get('id')}\")")
for st in C.get("statistics", []):
    if st.get("value") and str(st["value"]).lower() not in shown: warn(f"statistic never shown: {st['value']} at {st.get('t')}s")
tx = sum(1 for m in mo if m["component"] in TEXT)
if mo and tx / len(mo) > 0.4: warn(f"{100 * tx // len(mo)}% of the plan is text-led")
cov = sum(m["end"] - m["t"] for m in mo if m["state"] == "full")
print(f"\n{len(mo)} moments over {DUR / 60:.1f} min ({len(mo) / (DUR / 60):.1f}/min) | the creator is off screen {100 * cov / DUR:.0f}% | signature: {PL.get('signature', '')[:90]}")
print(f"\n{len(issues)} thing(s) to look at:" if issues else "\nplan is clean"); [print("  ! " + x) for x in issues]
