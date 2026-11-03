# Illustration patterns for the full-screen windows

Read this before planning the graphics pass. The rule of the format: a graphic **illustrates** what the creator is
describing. It is a thing the viewer recognises (an interface, an object, a diagram, a real asset), never the creator's
sentence set as text. Words appear only as labels inside the thing. If nothing illustrates a line, use a punch-in or
leave the creator alone: a clean full-screen shot is a fine answer.

## What worked (reuse the idea, not the exact graphic)

The pairs below are a menu of ideas for a lesson about growing a business on video platforms. Translate each to
the creator's own subject: the right-hand column is a *kind* of illustration.

| The creator is describing | Shown |
|---|---|
| A channel or platform growing the business | A video card with a "New call booked" notification landing on it |
| "N new rules / steps / ideas" | N hidden cards with the contents blurred (a preview of the count, never the items) |
| A metric that pays little | A studio card: views counting up, revenue stuck at a small number in red |
| A named creator, client or company | A channel or profile card with the real avatar and the real follower count; the real plaque photo; the real testimonial |
| A low-performing piece that sells more | Three video rows ranked by views; the smallest one collects "Call booked" chips |
| A viewer choosing between options | Search results with durations and a cursor clicking the long one |
| A path a viewer takes | Icon tiles joined by arrows: video, video, video, lead magnet, email |
| Ways to word a title or headline | One video card whose title swaps through the patterns |
| Buyers taking action | Payment, booking and "watched 4 videos" notifications stacking |
| A length limit | The title field with its character counter filling |
| Links in the description | The description box with the links lighting in turn (as a split, graphic on the left) |
| Viewers leaving | An "Up next" list of other channels with a cursor clicking away |
| A series | A playlist panel filling with episodes and an "N / total" counter |
| Metrics that matter | A dashboard where the vanity number fades and opt-ins, emails and booked calls count up |
| A free download | The checklist page. Mock it only if the real file does not exist, and say so in the report |

Figures inside illustrations are invented for the picture. Real people and real channels get real numbers. The
delivery report lists which is which.

## The interface kit (`engine/doc_kit.py`, imported as `D`)

| Piece | What it gives you |
|---|---|
| `D.win(t)` | The full-screen window `[a, b]` that time `t` sits in; fails loudly if `t` is inside a document section |
| `D.views_card(sid, a, b, t_views, t_zero, ...)` | A number climbing while the wanted result stays at 0 (returns a finished piece) |
| `D.ig_card(sid, lines, name=...)` | An Instagram-style profile header whose bio lines can be swapped; uses the creator's profile picture when setup saved one |
| `D.chan(cid, top, avatar_file, name, meta, sid, tag)` | A YouTube channel card with a real avatar (a file in `assets/media/`) and real figures |
| `D.vrow(rid, w, h, duration, html)` | One video row: thumbnail block plus whatever sits beside it |
| `D.note(nid, top, bg, icon, title, sub)` | An iOS-style notification on glass |
| `D.drop(sel, t, sound)` | The notification drop-in entrance |
| `D.playlist(sid, n, labels)` | A mini-series / playlist panel |
| `D.PLAY / CAL / CARD / MAIL / DOC / CUR` | Icons (`.format(size, colour)` on PLAY, MAIL, DOC) |

Classes: `.xc` dark card, `.xw` white card, `.xy` video-platform dark card, `.xk` small caps label, `.xn` big number,
`.chip` green pill, `.tile` icon tile, `.dsh` dashboard tile, `.yl` and `.yl.s` grey text lines (use these instead of
made-up titles), `.xpill`, `.xlab`, `.xar`. Everything else comes from the educational-youtube-editor kit (`K`:
`K.custom`, `K.preview`, `K.frame`, `K.chart`-style pieces) and its engine (`E.float_`, `E.split`, `E.full`,
`E.punch`, `E.enter`, `E.tw`, `E.count`, `E.sfx`).

## Rules that keep it readable

- Interface text is **about 28 px or more at 1080p**; anything smaller is invisible on a phone. Snapshot every scene
  and read the sheets.
- A graphic inside a full-screen window sits beside the creator (`E.float_`) or as a clean half (`E.split`) with the
  graphic on the **left** and the creator on the **right**, so the creator never jumps sides against the document layout.
- A split or panel that touches a document section is `cut=True`: its glide would otherwise run into the document.
- Windows under about 6 seconds usually get nothing.
- Time everything from the words: `E.w("exact words", after)`. Never from a stopwatch.
- Real over drawn: a named channel, client, person or product is shown with the real avatar, plaque, screenshot or
  card from the asset hunt (the creator's own folders first, then the web if setup allows it). Check every fetched
  image against the "never show" list.
