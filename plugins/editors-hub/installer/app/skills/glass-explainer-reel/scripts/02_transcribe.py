#!/usr/bin/env python3
"""Step 2 - transcribe with the transcriber chosen at setup (stt.py).   02_transcribe.py <slug>
Writes el.json (raw), words.json [[text,start,end],...], words.txt (one numbered word per line, for choosing
what to drop) and prints the timed script plus a list of likely mistakes to check."""
import sys
from common import work, save, scribe, el_words, norm
W = work(sys.argv[1])
J = scribe(f"{W}/a16.flac"); save(W, "el.json", J)
words = el_words(J); save(W, "words.json", words)
FILL = {"um", "uh", "erm", "er", "ah", "hmm", "mm", "uhm", "umm"}
with open(f"{W}/words.txt", "w") as f:
    line = []
    for i, (t, s, e) in enumerate(words):
        gap = s - words[i - 1][2] if i else s
        f.write(f"{i:5d}  {s:8.2f} {e:8.2f}  {t}{f'    <- {gap:.1f}s pause before' if gap > 0.6 else ''}\n")
print(f"{len(words)} words, {words[-1][2]:.1f}s. Script (word index and time at the start of each line):\n")
start = 0
for i, (t, s, e) in enumerate(words):
    last = i == len(words) - 1
    if last or t[-1] in ".?!" or words[i + 1][1] - e > 0.7:
        print(f"[{start:4d} {words[start][1]:7.2f}] " + " ".join(w[0] for w in words[start:i + 1]))
        start = i + 1
print("\nCHECK THESE (hints only; read the script yourself as well):")
n = [norm(w[0]) for w in words]
for i, x in enumerate(n):
    if x in FILL:
        print(f"  filler      word {i} at {words[i][1]:.2f}: {words[i][0]}")
    if i and x == n[i - 1]:
        print(f"  repeat      words {i - 1}-{i} at {words[i - 1][1]:.2f}: {words[i - 1][0]} {words[i][0]}")
for i in range(len(n) - 2):
    for j in range(i + 1, min(i + 25, len(n) - 2)):
        if n[i:i + 3] == n[j:j + 3]:
            print(f"  restart?    words {i}-{j - 1} at {words[i][1]:.2f}: \"{' '.join(w[0] for w in words[i:i + 3])}\" is said again at word {j} ({words[j][1]:.2f})")
            break
