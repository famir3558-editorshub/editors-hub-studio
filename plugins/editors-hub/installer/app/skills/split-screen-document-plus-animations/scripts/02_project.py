#!/usr/bin/env python3
"""Step 5 - the graphics project.   02_project.py <slug> "<Title>" [--refresh]
Run after the dialogue cut is rendered (educational-youtube-editor scripts 01-05 on the split-screen base).
Scaffolds <projects root>/<slug>-yt with the educational-youtube-editor's 06_new_project.py, then swaps in THIS skill's
engine (the document guard), adds doc_kit.py, sets the creator's face position from the gaze data, maps the full-screen
windows through the cut and measures every layout switch from the base video itself."""
import json, os, shutil, subprocess, sys
import numpy as np
slug, title = sys.argv[1], sys.argv[2]; HERE = os.path.dirname(os.path.abspath(__file__)); SK = os.path.dirname(HERE)
ED = os.path.expanduser("~/.claude/skills/educational-youtube-editor/scripts")
WORK_ROOT = os.path.expanduser("@@WORK_ROOT@@"); PROJECTS_ROOT = os.path.expanduser("@@PROJECTS_ROOT@@")     # the same folders the educational-youtube-editor uses
if "@" * 2 in WORK_ROOT + PROJECTS_ROOT: sys.exit("This skill has not been set up yet: run the setup interview (setup/SETUP.md), then python3 setup/apply_profile.py")
os.path.exists(f"{ED}/06_new_project.py") or sys.exit("The educational-youtube-editor skill is not installed: its cut, render and review scripts are used as they are. Install it, set it up, then run this again.")
os.path.exists(f"{ED}/../.configured") or sys.exit("The educational-youtube-editor skill has not been set up yet (its scripts hold the creator's folders and cut settings). Run its setup, or `creator-setup`, then run this again.")
W = f"{WORK_ROOT}/{slug}"; PJ = f"{PROJECTS_ROOT}/{slug}-yt"
g = f"{W}/split/gaze.txt"; face = "980,440"
if os.path.exists(g):                             # the creator is centred in the full-screen shot; the nose sits a little under the face-box centre
    r = np.array([[float(x) for x in l.split()[1:4]] for l in open(g) if len(l.split()) > 3]); face = f"{round(float(np.median(r[:, 0])) * 1920 - 18)},{round(float(np.median(r[:, 1])) * 1080 - 12)}"
cmd = [sys.executable, f"{ED}/06_new_project.py", slug, title, "--face", face] + (["--refresh"] if "--refresh" in sys.argv or os.path.exists(PJ) else [])
subprocess.run(cmd, check=True)
for f in ("yt_engine.py", "doc_kit.py"): shutil.copy(f"{SK}/engine/{f}", f"{PJ}/{f}")
subprocess.run([sys.executable, f"{HERE}/windows.py", slug], check=True)
subprocess.run([sys.executable, f"{HERE}/snap_windows.py", slug, f"{PJ}/assets/cam.mp4"], check=True)
shutil.copy(f"{W}/windows.json", f"{PJ}/windows.json")
b = f"{PJ}/build.py"; s = open(b).read()
if "doc_kit" not in s:
    open(b, "w").write(s.replace("import yt_engine as E, yt_kit as K", "import yt_engine as E, yt_kit as K, doc_kit as D        # D = this format's interface pieces (references/illustration-patterns.md)"))
print(f"\nproject {PJ} | face {face} (open face-check.jpg at a full-screen moment to confirm) | windows.json measured.\n"
      f"Now: print what the creator says in each full-screen window, plan, and write build.py. Graphics ONLY inside the full-screen windows.")
