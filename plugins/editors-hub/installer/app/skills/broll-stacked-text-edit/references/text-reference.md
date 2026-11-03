# The text treatment

This is the treatment `07_text.py` reproduces. It comes from a short vertical reel the style was modelled on (text
treatment only; its footage is never used).

What the reference does:
- Most phrases are plain small captions. For selected phrases (a named idea, a turn of the argument) the small line
  moves to open space beside the speaker and a much larger bold line appears directly beneath it. Only two such stacks
  in 26 s.
- Small line: light sans, tight tracking, about 4.5% of the frame height. Large line: bold, about 2.7x the small
  line, tight tracking, its top almost touching the small line. Both left-aligned; the small line sits a few pixels
  in from the large line's left edge. White with a soft shadow.
- Timing: the small line appears on its words; about 0.5 s later the large line focuses in (blurred and faint to
  sharp over ~8 frames, with a slight settle). The complete block holds roughly 0.7-1 s and then is simply gone
  (a hard clear on the next phrase or shot), nothing lingers into the next idea.
- Position: lower-left open space, beside the speaker, never over the face; it changes with the shot.

How the skill reproduces it (`07_text.py`): the whole video is captioned in the plain style (the caption font,
tracking -50) below the speaker's chin; for selected phrases the caption becomes a left-aligned stack revealed line by
line on the speaker's words (fade + small move up or down, no blur), the last line large and in the main bold,
cleared when the next phrase starts. The addition to the reference is an optional key word inside the large line in
the emphasis font and the accent colour, larger than the words around it. Output is always 9:16; 16:9 footage inside
the frame carries its captions in the lower half of the picture.
