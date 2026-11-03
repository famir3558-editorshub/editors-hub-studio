# Analysis guide: how to watch a clip and fill its record

The goal is not a caption. It is an editor's understanding of the clip: what is literally on
screen, what ideas it can stand for, which seconds are good, and when it would be the wrong choice.

## Before writing anything

1. Read **every** contact sheet for the clip (long clips have several). Frames are spread across
   the full length and labelled with their timestamp, so you can see how the clip changes.
2. Read the audio profile from `extract`:
   - `level: active` -> sound most of the time. Combine with the frames: mouth moving and facing
     camera -> `talking to camera`; headset / laptop call -> `on a call`; otherwise music or ambience.
   - `ambient` / `silent` -> treat as visual-only B-roll.
3. If something matters and the sheet is ambiguous (is that a phone or a remote? are they talking?),
   extract more frames: `broll extract --id <id> --frames 24`, or grab one frame yourself with
   ffmpeg into the scratchpad. Never write into the footage folder.
4. The person in the footage is assumed to be the creator (@@CREATOR_FIRST_NAME@@) unless clearly
   someone else. If another person appears, describe them by role ("a client on a video call",
   "a friend") and never guess names.
5. Check the clip against the creator's never-use list: **@@NEVER_SHOW@@**. If a clip shows any of it
   (a person, a place, a private screen), write that in `issues` and add "anything published" (or the
   narrower case) to `avoid_for`, so it is never placed in an edit by accident. When you are not sure
   whether something counts, record it as an issue and ask.

## Field by field

| Field | How to fill it |
|---|---|
| `summary` | One line, under 15 words, the way you'd describe it to an editor. "@@CREATOR_FIRST_NAME@@ typing on a MacBook at their home office desk". |
| `description` | 2-4 sentences: who, doing what, where, how it's shot, how it changes over the clip, the feeling. |
| `people` | e.g. `"@@CREATOR_FIRST_NAME@@ (subject, upper body)"`, `"@@CREATOR_FIRST_NAME@@ (hands only)"`, `"client on screen"`. |
| `speaking` | One of: `none`, `talking to camera`, `talking off camera`, `on a call`, `background voices`. |
| `location` / `environment` / `time_of_day` / `setting_details` | "home office", "indoor", "day", "white desk, plant, window light from left". |
| `objects` / `devices` | Everything an editor could cut on: MacBook, iPhone, ring light, mug, notebook, Premiere timeline on screen. |
| `activity` / `actions` | Main activity ("editing a video"), then the actions you see ("scrubbing timeline", "leaning back", "smiling"). |
| `shot_type` | One of: extreme wide, wide, medium wide, medium, medium close-up, close-up, extreme close-up, insert, POV, over-the-shoulder, top-down, screen recording. |
| `camera_angle` | eye level, high, low, side, three-quarter, top-down, behind. |
| `camera_movement` | static, handheld, pan, tilt, push in, pull out, tracking, gimbal, zoom, slider. |
| `subject_movement` | How much the subject moves and the direction (useful for cut matching). |
| `lighting` / `colour` | "soft window light", "dark room lit by screen", "warm golden hour", "cool blue tones". |
| `mood` | 2-4 words: focused, calm, energetic, frustrated, reflective, confident, playful. |
| `tags_literal` | 8-20 lowercase tags for what is visible or happening. |
| `tags_conceptual` | 8-20 lowercase ideas the shot can represent. This is what makes script matching work. |
| `editorial_uses` | 3-6 sentences starting "Sections about..." or "When talking about...". |
| `avoid_for` | When this clip would be wrong: "upbeat hype moments", "talking about rest", "anything client-facing (messy desk)". |
| `segments` | Time ranges covering the clip, each with description, `usable` true/false and quality 1-5. |
| `best_section` | The strongest continuous run, `start`/`end`/`why`. Usually 3-8 seconds. |
| `quality` | 1-5 technical: focus, exposure, stability, framing. |
| `usefulness` | 1-5 editorial: how often this will genuinely help an edit. |
| `issues` | Anything an editor must know: "shaky first 2s", "logo visible", "messy background", "phone screen shows private DMs". |

## Segments: the most important part

Most recordings have bad edges. Mark them so they never get used:

- **Setup**: walking into frame, adjusting the camera, looking at the lens before acting, the
  first second after pressing record.
- **Exit**: reaching toward the camera, standing up to stop recording, walking out.
- **Breaks in the action**: laughing out of character, checking the shot, someone walking past,
  focus hunting, a sudden exposure jump.

Mark those `usable: false`. Split the usable remainder where the action changes (typing ->
leaning back -> sipping coffee); each can serve a different line of a script.

Cover the whole clip with segments, in order, without gaps. On a contact sheet you only see
sample frames, so place boundaries at the nearest frame time and stay conservative: if 0.2s
looks fine and 2.5s looks fine but the setup could be in between, start the usable part at 2.5s.

## Literal vs conceptual tags

Literal is what a viewer sees. Conceptual is what a viewer would understand while hearing
something. Think: "if the creator said ___ over this clip, would it make sense?"

Example, desk + MacBook typing:

- literal: desk, macbook, laptop, typing, home office, keyboard, hands, working, screen, chair
- conceptual: productivity, deep work, focus, business, entrepreneurship, content creation,
  research, writing scripts, working from home, building something, discipline, consistency

Example, scrolling a phone on the couch:

- literal: phone, iphone, scrolling, couch, sofa, hands, thumb, living room, lying down
- conceptual: procrastination, distraction, doom scrolling, social media, consumption over
  creation, wasting time, comparison, dopamine, avoiding work

Example, walking alone outdoors with headphones:

- literal: walking, outside, street, park, headphones, trees, pavement, wide shot
- conceptual: thinking, clarity, mindset, reflection, freedom, routine, getting away from the
  desk, processing ideas, morning walk, lifestyle

Use the creator's world when it fits. What they do: @@NICHE@@. What their videos are about:
@@VIDEO_TOPICS@@. Conceptual tags in their own vocabulary are the ones a script search will hit, so
prefer the words they would say out loud over generic ones. Do not invent concepts the shot cannot
carry (a messy desk is not "luxury").

## A complete record (example)

```json
{
  "clip_id": "c_39cdd491d2c2",
  "summary": "@@CREATOR_FIRST_NAME@@ typing on a MacBook at their home office desk",
  "description": "@@CREATOR_FIRST_NAME@@ sits at their desk in their home office working on a MacBook, typing steadily and glancing at the screen. Medium side-angle shot on a static tripod with soft window light. Calm, focused, getting-it-done feel.",
  "people": ["@@CREATOR_FIRST_NAME@@ (subject, upper body)"],
  "speaking": "none",
  "location": "home office", "environment": "indoor", "time_of_day": "day",
  "setting_details": "white desk, plant, window light from left",
  "objects": ["desk", "MacBook", "mug", "notebook"], "devices": ["MacBook"],
  "activity": "typing on a laptop", "actions": ["typing", "reading the screen", "small nod"],
  "shot_type": "medium", "camera_angle": "side, eye level", "camera_movement": "static",
  "subject_movement": "minimal, hands only",
  "lighting": "soft natural window light", "colour": "neutral, bright",
  "mood": ["focused", "calm"],
  "tags_literal": ["desk", "macbook", "laptop", "typing", "home office", "keyboard", "working", "screen", "plant"],
  "tags_conceptual": ["productivity", "deep work", "focus", "business", "entrepreneurship", "content creation", "research", "writing scripts", "working from home", "consistency"],
  "editorial_uses": [
    "Sections about building a business through focused work",
    "When talking about writing scripts, emails or content",
    "Showing the unglamorous daily work behind results",
    "Working from home / laptop lifestyle points"
  ],
  "avoid_for": ["high-energy hype moments", "talking about rest or switching off"],
  "segments": [
    {"start": 0.0, "end": 1.5, "description": "reaching away from camera after pressing record", "usable": false, "quality": 1},
    {"start": 1.5, "end": 12.5, "description": "steady typing, glances at screen", "usable": true, "quality": 4},
    {"start": 12.5, "end": 14.0, "description": "stands up to stop the camera", "usable": false, "quality": 1}
  ],
  "best_section": {"start": 3.0, "end": 9.0, "why": "steady typing, nothing distracting, good light"},
  "quality": 4, "usefulness": 5,
  "issues": [],
  "notes": ""
}
```

## Quality scale

| | quality (technical) | usefulness (editorial) |
|---|---|---|
| 5 | sharp, well exposed, stable, intentional framing | fits many common topics, will be used often |
| 4 | good, minor flaws | clearly useful for several topics |
| 3 | usable, noticeable flaws | useful for a narrow set of topics |
| 2 | weak: soft, noisy, shaky | rarely the right choice |
| 1 | unusable except in an emergency | test shot / mistake |
