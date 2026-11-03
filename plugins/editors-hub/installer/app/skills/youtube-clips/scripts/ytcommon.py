"""Shared helpers for youtube-clips. Everything lives inside this skill: the work-folder, probe and transcription
helpers come from scripts/cut/common.py, so the video scripts and the per-clip cut pipeline never disagree about where
files live or how the transcriber is chosen."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "cut"))
from common import work, load, save, run, probe, el_key, scribe, grab, norm, WORK_ROOT, PROJECTS_ROOT, SKILL  # noqa: F401,E402


def mmss(t):
    return f"{int(t // 60):02d}:{t % 60:04.1f}"


def fps_float(r):
    a, b = r.split("/") if "/" in r else (r, "1")
    return float(a) / float(b)
