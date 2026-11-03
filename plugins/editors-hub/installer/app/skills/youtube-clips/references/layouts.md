# Composing the two versions

Both versions use the same verified cut and the same words. They are two separate edits: the vertical is never a
centre crop of the horizontal, and a graphic that sits beside the speaker in 16:9 will usually become a split or a
full-screen animation in 9:16.

Shared by both (exact values are in `style.md`):

- **Captions**: one line in the caption font, bold, tight tracking, white, soft shadow, changing on the word; the
  word that carries the point in the emphasis font and the accent colour (about 3-6 a minute, never two captions
  running); figures stay in the caption font and take the accent colour. Every spoken word appears once, in order.
- **Graphics**: real assets before drawn ones; never crop a person; one idea on screen at a time; each element
  lands on the word that names it and leaves when the speaker moves on; text inside graphics stays modest and is
  labels only (the caption carries the sentence); positive green, negative red, the accent colour for the one focal
  element; no 3D, no bounce, no whip slides.
- **Motion**: focus pull in, soft fade out, lines draw, counters tick as plain numbers, text types, a light sweep on
  the item that becomes active.
- **Real interfaces**: a comment or DM is a phone notification; a document is a real-looking document window; a
  website is the real page in a simple browser frame; a post is the real post, uncropped.
- **Sound**: the original audio. Music and effects only as the setup answer says.

## What to show (decide per sentence)

| The speaker says | Show |
|---|---|
| A website, tool, page | The real page (screenshot or short scroll capture) |
| A post, reel, creator | The real post or cover, uncropped, with its own handle visible |
| A framework or named steps | The parts appearing one at a time as they are named; a small agenda box if they are walked through for a while |
| A comparison, a before/after | Two sides, the bad one red, the good one green |
| A number | The number, ticking up, large |
| A process, A → B → C | Nodes and drawn links, built in order |
| A real result | The real screenshot |
| A quoted line, a hook, a script | Typed into a document window |
| An opinion, a punchline, an emotional moment | Nothing. Stay on the speaker and let it breathe. |

A change on screen needs a reason: a new concept, an example, a number, a turn in the story, proof, or a key phrase.
"It has been four seconds" is not a reason.

If the full video already showed something at this point (a page, a post, a diagram), that is the first candidate:
rebuild it from the real asset rather than cropping it out of the published picture.

---

## Version 1: horizontal 16:9 (1920x1080)

The feeling: the sharpest minute of a longer video, finished to the same standard as the creator's short-form
videos. Modern business content + visual explanation, with the speaker as the main picture.

**Frame.** Keep the recorded composition. In most videos the speaker is centred and looking at the camera; some use
a screen layout (the face in a card beside a document, a tablet or a whiteboard). Read from the contact sheet and a
still at the clip's time:

- where the speaker sits (centred, or which third) and whether they are looking at the camera
- anything already burned into the picture (captions, graphics, a layout): graphics and captions never go over it
- the largest clean area of the frame (the *graphic zone*), as a rectangle in pixels
- what is behind that area (plain wall = graphics sit directly on it; busy background = graphics sit on glass cards
  or a soft dark gradient that fades in with them and out again)

When the speaker is centred there is no clean zone until the picture is re-framed: the engine's `side` / `sidep`
shots enlarge the picture and move the speaker right, which opens the left of the frame for the graphic. When they
sit to one side already, the zone is the open side.

**Three sizes of graphic** (pick per moment):

1. *Beside the speaker*: a card, list, number or small diagram inside the graphic zone, with the picture re-framed
   by a `side` shot so the zone opens up. The default.
2. *Takeover*: the graphic grows to about 60-70% of the frame; the speaker stays visible at their side of it, pushed
   across by the tighter `sidep` shot. For screenshots and pages that need room to be read.
3. *Full screen* (`full`): the graphic alone on the brand background, about 3-5 s. For a framework reveal, a dense
   real example, or to cover a join.

**The speaker's face is a protected zone.** Detect where the face and head are for the whole clip (`04_faces.py`),
and place every graphic around that area, never over or against it. The engine checks this and warns; see the main
skill. Graphics go beside the speaker, in the open side of the frame, or alone on screen. Avoid their hands too
when they are gesturing at the thing being shown.

**Captions.** Bottom centre of the frame, one line of 1-4 words (the wider frame can take one more word than the
vertical), about 68 px, baseline about 110-130 px above the bottom edge and at least 120 px in from the sides. They
stay in the same place when a graphic is up, including full screen, so the eye never hunts for them. If a takeover
graphic needs the bottom of the frame, the graphic moves up, not the caption.

**Opening.** First frame is the speaker mid-thought on the hook line, caption already on. No title card, no logo
sting, no written hook. (Option: a small tag with the full video's title, lower left, for the first 3 s, so the clip
points back to it. Use it only when the setup answer about pointing back to the full video says so.)

**Hiding cuts.** There are no mode switches to hide behind, so:

- a join gets a punch-in or punch-out (100% ↔ about 112%, hard cut, re-centred so the eyes stay at the same height)
- or it sits under a takeover or full-screen graphic
- small tightening cuts inside a sentence are acceptable when a caption change lands on them
- never two different punch levels within about 3 s; never a slow zoom *and* punch-ins in the same clip

**Pacing.** Expect the speaker alone on screen for a third to a half of the clip. Graphics arrive for the example,
the framework and the number, and leave.

**Safe margins.** Text and graphics at least 96 px from the left and right edges and 72 px from the top.

---

## Version 2: vertical 9:16 (1080x1920)

Follow `style.md` section 2 for the structure: three modes (the speaker full screen, split with the animation above
and the speaker below, full-screen animation), every mode switch on a real cut, no visible jump inside a block of
the speaker, blocks of about 3-7 s, opening full screen on the speaker with a two-line text hook above their head
from frame one.

What to check for YouTube footage:

**Crop.** When the speaker is looking at the camera, centre the face (`for m in E.V.values(): m["X"] = 540` after
`E.init`; `K.start` does it; the bare engine default is off-centre). If a stretch has them turned to a screen or a
whiteboard, give them looking room for that block: face off-centre by roughly 8-12% of the frame width, away from
the direction they are looking. If the source is a screen layout, the face is inside a small card: check a still at
full crop, and if it is too soft, build the vertical as split / animation with the speaker in the lower half, or ask
for the raw.

**Head room for the hook.** The text hook sits above the head; set the crop from stills of this video, not from
defaults.

**Captions.** Placed as `style.md` says: under the chin when the speaker is full screen, on the seam above the head
in split, under the graphic in a full-screen animation. Never across the jaw, and never over captions already
burned into the picture.

**Behind-the-head graphics** need a clean cut-out, which this engine does not make. Put the graphic above or beside
the speaker on a glass card instead.

**Mode choice follows the content**, not a rotation:

- speaker full screen: the hook, opinions, punchlines, the emotional moment, the last line
- split: they are explaining and there is something to look at while they do
- full-screen animation: the framework, the real example that needs the whole screen, or a join that needs covering

A typical run: full-screen speaker (hook) → split with the example → full-screen graphic (framework) → speaker →
real screenshot as proof → speaker with one supporting graphic → speaker (payoff). Use fewer modes when the clip is
simple. Do not force every technique into every clip.

**The moved hook's join** always lands on the first mode switch.
