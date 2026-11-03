#!/usr/bin/env python3
"""Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.

Component sheet: most components once, across the first 80 s of a sample video (genuine split, punch-in, face-safe
crops). NOT an edit and not a pacing reference: far too dense on purpose (the audit says so). Read it for how scenes
are declared. The media file names are stand-ins; put your own files in assets/media/ to run it."""
import yt_engine as E, yt_kit as K
E.init(__file__)
M = "assets/media/"
E.float_(K.title("hook", 0.2, 4.6, "A promise in *five* words or so"), why="curiosity", score=5, zone="bottom")
E.punch(2.2, 4.8, "the promise lands here")
E.full(K.preview("five", 5.0, 10.6, 5, variant="docs", labels=["First one"], reveal=1, t_split=5.9), why="curiosity", score=5)
# t = E.w("a word that is said", 9)          # times normally come from the words: see templates/build.py
E.split(K.frame("client", 11.0, 15.4, M + "client-result.jpg", variant="tilt", tag="Client name"), why="evidence", score=4, tier=1)
E.split(K.stat("subs", 15.6, 19.4, 100000, "subscribers in four weeks", frm=4000, variant="count"), why="evidence", score=4)
E.float_(K.term("proof", 20.0, 23.6, "Second client", "the result in one short line"), why="evidence", score=3, side="left")
E.full(K.flow("chain", 24.0, 30.2, ["Attention", "Trust", "Demand", "*Sales*"], [24.3, 25.5, 26.7, 27.9], variant="down"), why="explain", score=5)
E.panel(K.rows("list", 30.8, 36.0, [("Step one", "a short sub-line"), ("Step two", "a short sub-line"), ("Step three", "a short sub-line")], [31.0, 32.4, 33.8], variant="checks"), why="memory", score=3)
E.split(K.browser("site", 36.6, 41.6, M + "profile-after.png", "instagram.com/example", variant="float", hl=(8, 10, 50, 30, 38.6)), why="example", score=4, side="right", tier=2)
E.full(K.collage("thumbs", 42.0, 46.6, [M + f for f in ("thumb-1.jpg", "thumb-2.jpg", "client-result.jpg", "thumb-3.jpg", "thumb-4.jpg")], variant="scatter"), why="example", score=4, tier=1)
E.full(K.framework("fw", 47.0, 51.4, ["Research", "Script", "Film", "Edit", "Publish"], times=[47.2, 47.9, 48.6, 49.3, 50.0], active=2, variant="cards"), why="memory", score=5)
E.float_(K.tracker("fw-t3", 52.0, 56.0, ["Research", "Script", "Film", "Edit", "Publish"], 2), why="memory", score=2, zone="top")
E.float_(K.frame("stage", 52.4, 56.0, M + "on-stage.jpg", variant="polaroid", ratio=1, w=420), why="example", score=3, side="right", tier=3)
E.full(K.compare("vs", 56.6, 61.6, ("Option A", ["First point", "Second point"]), ("Option B", ["First point", "Second point"]), 56.8, 58.2, variant="columns", win="right", t_win=59.6), why="simplify", score=4)
E.split(K.emph("swap", 62.0, 65.6, ["Views", "*Trust*"], [62.2, 63.8], variant="swap"), why="emphasis", score=4)
E.full(K.funnel("fun", 66.0, 71.4, ["Stage one", "Stage two", "Stage three", "Stage four"], [1, .5, .2, .08], [66.2, 67.5, 68.8, 70.1]), why="demonstrate", score=4)
E.full(K.crowd("crowd", 71.8, 75.6, 73.4), why="simplify", score=4)
E.full(K.grow("grow", 76.0, 79.6, [76.3, 77.1, 77.9]), why="demonstrate", score=4)
E.build()
