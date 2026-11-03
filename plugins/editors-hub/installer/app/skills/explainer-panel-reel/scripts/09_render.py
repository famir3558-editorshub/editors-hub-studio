#!/usr/bin/env python3
"""Step 9 - build, check, render.   09_render.py <slug> [--draft] [--tag v2]
--draft: fast low-quality render into the project's renders/ folder for the review pass.
Final : "<out>/<name> - 9x16[ tag].mp4" (master, H.264 high bitrate + AAC 320k) and a phone copy under 30 MB.
One render at a time when the output is on an external drive."""
import json, os, subprocess, sys
from common import PROJECTS_ROOT
slug = sys.argv[1]; PJ = f"{PROJECTS_ROOT}/{slug}-panel"; P = json.load(open(f"{PJ}/project.json")); draft = "--draft" in sys.argv
tag = (" " + sys.argv[sys.argv.index("--tag") + 1]) if "--tag" in sys.argv else ""
r = subprocess.run([sys.executable, "build.py"], cwd=PJ, capture_output=True, text=True); print(r.stdout, r.stderr)
r.returncode == 0 or sys.exit("build.py failed")
if "WARN no captions" in r.stdout: sys.exit("refusing to render without captions")
chk = subprocess.run(["npx", "hyperframes", "check"], cwd=PJ, capture_output=True, text=True)
print("\n".join(l for l in (chk.stdout + chk.stderr).splitlines() if any(s in l for s in ("✗", "error", "Error", "warn", "Check")))[:3000])
os.makedirs(f"{PJ}/renders", exist_ok=True)
out = f"{PJ}/renders/draft.mp4" if draft else f"{P['out']}/{P['stem']} - 9x16{tag}.mp4"
fps = P["fps_str"] if "/" in P["fps_str"] and not P["fps_str"].endswith("/1") else str(round(P["fps"]))
subprocess.run(["npx", "hyperframes", "render", "-o", out, "--fps", fps, "--quality", "draft" if draft else "high", "--skill", "general-video"], cwd=PJ, check=True)
print("wrote", out)
if not draft:
    D = P["dur"]; br = int(min(6000, 26 * 8000 / D - 170)); ph = out[:-4] + " (phone).mp4"; log = f"{PJ}/renders/pass"
    for n, extra in ((1, ["-an", "-f", "mp4", "/dev/null"]), (2, ["-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", ph])):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out, "-c:v", "libx264", "-preset", "slow", "-b:v", f"{br}k", "-maxrate", f"{br * 5 // 4}k", "-bufsize", "8000k",
                        "-pass", str(n), "-passlogfile", log, *extra], check=True)
    print("phone copy", ph)
print(f"next: python3 {os.path.dirname(os.path.abspath(__file__))}/10_review.py {slug} \"{out}\"")
