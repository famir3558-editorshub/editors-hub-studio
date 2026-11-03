"""check_doc_frames.py "<final.mp4>" <project>/assets/cam.mp4      (run from the project folder: it reads windows.json)
Compares the rendered final with the base video on the first and last two frames of every document section and every
2.5 s inside. Zero mismatches is the bar. A difference near 100 is a one-frame flash of the wrong layout; one near 15 is a
document section left zoomed. takeovers.json (optional) lists full-screen takeovers the creator asked for on purpose."""
import json, subprocess, sys, numpy as np
F, cam = sys.argv[1], sys.argv[2]
W = json.load(open('windows.json'))
_r = subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=r_frame_rate','-of','csv=p=0',F],text=True).strip().split('/'); FPS = int(_r[0]) / int(_r[1])   # the video's own frame rate (24p cameras exist)
want = {}
for a,b in W['doc']:
    na, nb = round(a*FPS), round(b*FPS)
    for label, n in (('doc first',na),('doc 2nd',na+1),('doc last',nb-1),('doc 2nd last',nb-2)):
        if n>=0: want[n]=label
    for n in range(na + 30, nb - 30, 75): want[n] = 'doc inside'
import os
TK = json.load(open('takeovers.json')) if os.path.exists('takeovers.json') else []     # full-screen takeovers the creator asked for: the document is deliberately covered there
want = {n: l for n, l in want.items() if not any(a - 0.05 <= n / FPS <= b + 0.05 for a, b in TK)}
ns = sorted(want)
def grab(path):
    out = {}
    for k in range(0, len(ns), 60):
        part = ns[k:k+60]; sel = '+'.join(f'eq(n\\,{n})' for n in part)
        p = subprocess.run(['ffmpeg','-nostdin','-v','error','-i',path,'-vf',f"select='{sel}',scale=480:270,format=gray",'-vsync','0','-f','rawvideo','-'],capture_output=True).stdout
        a = np.frombuffer(p,np.uint8).astype(int).reshape(-1,270*480)
        for n, fr in zip(part, a): out[n] = fr
    return out
A, B = grab(F), grab(cam); bad = 0
for n in ns:
    if n in A and n in B:
        d = np.abs(A[n]-B[n]).mean()
        if d > 2.5: bad += 1; print(f'  !! {want[n]} frame {n} ({n/FPS:.2f}s) differs from the base by {d:.1f}')
print(f'{len(ns)} document frames checked (edges + every 2.5 s inside), {bad} do not match the base video')
