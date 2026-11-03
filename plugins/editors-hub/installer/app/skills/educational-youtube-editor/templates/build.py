#!/usr/bin/env python3
"""__TITLE__ - long-form YouTube edit. Edit this file, never index.html.
   python3 build.py            audit + page for chunk 0        python3 build.py --list     chunk table
   python3 build.py --chunk N  page for chunk N (the render script does this for you)
Times are seconds on the cut timeline. Get them from the words that are said:  t = E.w("exact words", after_seconds).
The creator's logo / wordmark / profile picture, when they gave one at setup:  E.brand_asset("logo" | "wordmark" | "avatar") -> path or None."""
import yt_engine as E, yt_kit as K
E.init(__file__)
M = "assets/media/"

# ───────── INTRO (0-45 s): highest density. Confirm the click, show the structure, keep the answers back ─────────
# t = E.w("...", 0)
# E.float_(K.title("hook", 0.2, 4.8, "The promise, in *the* words said"), why="curiosity", score=5, zone="bottom")
# t5 = E.w("five", 5)
# E.full(K.preview("five", t5 - 0.3, t5 + 5.2, 5, labels=["First one"], reveal=1, t_split=t5 + 0.5), why="curiosity", score=5)

# ───────── SECTION 1 ─────────

# ───────── SECTION 2 ─────────

E.build()
