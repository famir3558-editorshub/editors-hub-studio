#!/usr/bin/env python3
"""Step 3 - check the chosen clips as scripts, then cut each one out of the call.
    03_clips.py <slug>                      print every clip in clips.json as a script with estimated timings
    03_clips.py <slug> --extract <id>|all   write "<out>/<id>/<id> - source.mov" for the cut pipeline (scripts/cut) to work from

clips.json:  {"clips": [{"id": "01-short-name", "title": "Working title", "segments": [[i, j], [i, j], ...]}]}
A segment is an inclusive range of word indexes from transcript.txt / words.json. Segments are in PLAY order: to open
on a line said later in the call, put that segment first. Leave words out of every segment to remove them.

The source file keeps a little air round each piece and keeps short removed bits (a filler, a repeated word) in place;
they are listed in "<id> - source.json" as `secs` in the clip's own time, ready for the tight cut's drops.json. So the
cut pipeline treats the file as an ordinary raw recording, and the reordering is already done before it starts."""
import json, os, subprocess, sys
from callcommon import work, load, mmss, fps_float
CONSENT = "@@CLIP_CONSENT@@".strip().lower()   # setup answer: have the people on the calls agreed to be clipped?
W = work(sys.argv[1]); a = sys.argv[2:]
pad = float(a[a.index("--pad") + 1]) if "--pad" in a else 0.25
M = load(W, "meta.json") or sys.exit("run 01_call_prep.py first")
words = load(W, "words.json") or sys.exit("run 02_call_transcribe.py first")
clips = (load(W, "clips.json") or sys.exit(f"write {W}/clips.json first"))["clips"]
GAP, JOIN, MERGE = 0.2, 0.12, 1.0   # longest pause kept inside a segment / pause at a join / removed bits shorter than this stay in the source file


def est(seg):
    i, j = seg
    return sum(min(words[k + 1][1], words[k][2] + GAP) - words[k][1] for k in range(i, j)) + words[j][2] - words[j][1]


def check(c):
    """Words may be used twice only when the first segment (a hook moved to the front) is heard again later."""
    seen = set(); c["_rep"] = set()
    for n, (i, j) in enumerate(c["segments"]):
        (0 <= i <= j < len(words)) or sys.exit(f"{c['id']}: segment [{i}, {j}] is outside the transcript (0-{len(words) - 1})")
        r = set(range(i, j + 1)); a, b = c["segments"][0]
        if seen & r:
            (seen & r) <= set(range(a, b + 1)) or sys.exit(f"{c['id']}: segment [{i}, {j}] repeats words that are not the opening hook")
            c["_rep"].add(n)
        seen |= r


def show(c):
    segs = c["segments"]; t = 0.0
    main = max({w[3] for w in words}, key=lambda s: sum(w[3] == s for w in words))
    total = sum(est(s) for s in segs) + JOIN * (len(segs) - 1)
    flag = "  OVER 90s: tighten or split" if total > 90 else "  over 60s: only if the idea needs it" if total > 60 else ""
    print(f"\n=== {c['id']}  {c.get('title', '')}   est. {total:.0f}s{flag}")
    for n, (i, j) in enumerate(segs):
        d = est((i, j)); notes = []
        if n == 0 and any(i > s[0] for s in segs[1:]):
            notes.append("MOVED TO THE FRONT (said later in the call): check it does not change the meaning")
        elif n and i < segs[n - 1][0] and n != 1:
            notes.append("OUT OF ORDER")
        if n and 0 < i - segs[n - 1][1] - 1 and i > segs[n - 1][1]:
            k = i - segs[n - 1][1] - 1
            notes.append(f"{k} word{'s' if k > 1 else ''} removed before this ({words[i][1] - words[segs[n - 1][1]][2]:.1f}s)")
        if n in c["_rep"]:
            notes.append("the opening hook is heard again here: listen to it; it must feel like a landing, not a glitch")
        others = sorted({w[3] for w in words[i:j + 1]} - {main})
        if others:
            notes.append(f"includes {', '.join(others)} (not the main speaker): another person's voice: flag it in the clip list")
            if not CONSENT.startswith("yes"):
                notes.append("NOT CLEARED: setup says not everyone on these calls has agreed to be clipped. Cut these words, or get a clear yes for this call first")
        print(f"  [{n + 1}] call {mmss(words[i][1])}-{mmss(words[j][2])} (w{i}-{j})  ->  clip {t:5.1f}-{t + d:5.1f}s" + "".join(f"\n      ! {x}" for x in notes))
        print("      " + " ".join(w[0] for w in words[i:j + 1]))
        t += d + JOIN
    return total


def pieces(c):
    """Group segments into pieces to pull from the call: neighbours with under MERGE seconds removed between them stay
    one piece (the removed bit becomes a `secs` drop); anything else is a real join."""
    out = []
    for i, j in c["segments"]:
        if out and i > out[-1]["j"] and words[i][1] - words[out[-1]["j"]][2] < MERGE:
            if i > out[-1]["j"] + 1:
                out[-1]["drops"].append((words[out[-1]["j"]][2], words[i][1]))
            out[-1]["j"] = j
        else:
            out.append({"i": i, "j": j, "drops": []})
    for p in out:
        i, j = p["i"], p["j"]
        prev_end = words[i - 1][2] if i else 0.0
        next_start = words[j + 1][1] if j + 1 < len(words) else M["dur"]
        p["a"] = max(0.0, words[i][1] - pad, min(words[i][1], (prev_end + words[i][1]) / 2))
        p["b"] = min(M["dur"], words[j][2] + pad, max(words[j][2], (words[j][2] + next_start) / 2))
    return out


def extract(c):
    P = pieces(c); d = f"{M['out']}/{c['id']}"; os.makedirs(d, exist_ok=True)
    dst = f"{d}/{c['id']} - source.mov"
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for p in P:
        cmd += ["-ss", f"{p['a']:.3f}", "-t", f"{p['b'] - p['a']:.3f}", "-i", M["src"]]
    fc = "".join(f"[{k}:v:0][{k}:a:0]" for k in range(len(P))) + f"concat=n={len(P)}:v=1:a=1[v][a]"
    tail = ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-fps_mode", "cfr", "-r", M["fps"], "-c:a", "pcm_s16le", "-ar", "48000"]
    rate = "60M" if M["w"] * M["h"] > 2200 * 1300 else "24M"
    for enc in (["-c:v", "hevc_videotoolbox", "-b:v", rate, "-tag:v", "hvc1"], ["-c:v", "libx264", "-crf", "15", "-preset", "fast"]):
        if subprocess.run(cmd + tail + enc + [dst]).returncode == 0:
            break
    else:
        sys.exit("ffmpeg failed")
    fr = 1 / fps_float(M["fps"]); t = 0.0; info = {"clip": c["id"], "title": c.get("title", ""), "call": M["src"], "pieces": [], "joins": [], "secs": []}
    for n, p in enumerate(P):
        if n:
            info["joins"].append({"t": round(t, 3), "before": words[P[n - 1]["j"]][0], "after": words[p["i"]][0]})
        info["pieces"].append({"clip_start": round(t, 3), "call_start": round(p["a"], 3), "call_end": round(p["b"], 3),
                               "call_time": f"{mmss(p['a'])}-{mmss(p['b'])}", "words": [p["i"], p["j"]]})
        info["secs"] += [[round(t + x - p["a"], 3), round(t + y - p["a"], 3)] for x, y in p["drops"]]
        t += round((p["b"] - p["a"]) / fr) * fr
    json.dump(info, open(f"{d}/{c['id']} - source.json", "w"), indent=1)
    print(f"\n{c['id']}: {t:.1f}s of source in {len(P)} piece{'s' if len(P) > 1 else ''} -> {dst}")
    for jn in info["joins"]:
        print(f"  JOIN at {jn['t']:.2f}s  \"{jn['before']}\" | \"{jn['after']}\"   (a jump the viewer sees: put a switch, a punch-in or a full-screen graphic on it)")
    if info["secs"]:
        print(f"  removed bits still in the file, for drops.json: \"secs\": {info['secs']}")


for c in clips:
    check(c)
if "--extract" in a:
    want = a[a.index("--extract") + 1]
    todo = [c for c in clips if want in ("all", c["id"])] or sys.exit(f"no clip called {want}")
    for c in todo:
        extract(c)
else:
    tot = [show(c) for c in clips]
    print(f"\n{len(clips)} clips, {sum(tot):.0f}s in total. Read each one aloud as a script: it has to make sense to someone who never heard the call.")
