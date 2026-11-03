#!/usr/bin/env python3
"""Image-cluster reel: the speaker in the lower half of a 9:16 frame, clusters of found images above his head, tiny
left-aligned captions beside his chin. Nothing animates: images hard-pop on and each cluster is replaced on a hard cut.

  cluster_reel.py sheet   --plan plan.json --words words.json --work W [--video V]            one tile per cluster -> W/sheet.png
  cluster_reel.py preview --plan plan.json --words words.json --work W [--video V] --out O    720p review preview
  cluster_reel.py final   --plan plan.json --words words.json --work W  --video V  --out O    full-size final (after approval)
No --video = grey silhouette placeholder on a dark background (for testing a script). --audio A = use this sound.
Caption font and default caption size / position come from the creator profile (~/.claude/creator-profile/profile.json: font_caption,
font_main_regular or font_main_bold; skills.image-cluster-reel.caption_size / caption_x / caption_y). plan.json 'caption' overrides them.
Chrome: $CHROME, else Google Chrome / Chromium in the usual places.

plan.json = {"duration": 24.6, "caption": {"x": 92, "y": 1196, "size": 30, "lead": 0.10},
  "captions": ["I recently turned 26", "here are five things\\nI wish I knew sooner", ...],        # blocks; \\n = line break
  "clusters": [{"t": 0.0, "images": [{"file": "images/cake.jpg", "t": 0.10, "x": 150, "y": 330, "w": 360, "z": 1}, ...]}, ...]}
  cluster t = the cut where the previous cluster disappears; image t = when that image pops on; x, y, w in px on 1080x1920.
words.json = word timings of the edited video: [[start, end, "word"], ...] or [{"w","s","e"}, ...]. Captions are timed from it."""
import json, subprocess, os, sys, re, shutil, argparse, html as H
from concurrent.futures import ThreadPoolExecutor
ap=argparse.ArgumentParser(); ap.add_argument('mode',choices=['sheet','preview','final'])
for a in ('plan','words','work'): ap.add_argument('--'+a,required=True)
for a in ('video','audio','out'): ap.add_argument('--'+a)
A=ap.parse_args(); MODE=A.mode; W=os.path.abspath(A.work); os.makedirs(W,exist_ok=True)
# ---- the creator's profile: caption font + caption defaults (nothing brand-specific lives in this file) ----
SKILL_NAME='image-cluster-reel'
PDIR=os.path.expanduser(os.environ.get('CREATOR_PROFILE_DIR','~/.claude/creator-profile'))
try: PROF=json.load(open(PDIR+'/profile.json'))
except (OSError,ValueError): PROF={}
MINE=PROF.get('skills',{}).get(SKILL_NAME,{})
def font_face(spec):
    """profile font spec -> CSS src list. {"file": "X.ttf"} is looked up in the profile assets/fonts folder (or this skill's assets/fonts);
    {"local": ["Full Name", "PostScript-Name"]} uses the installed font."""
    if isinstance(spec,str): spec={'file':spec}
    parts=[]
    for n in spec.get('local',[]): parts.append("local('%s')"%n.replace("'",""))
    fn=spec.get('file')
    if fn:
        for d in (PDIR+'/assets/fonts',os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'assets','fonts')):
            f=os.path.join(d,os.path.basename(fn))
            if os.path.exists(f): parts.append("url('file://%s')"%f); break
        else: print('WARNING caption font file %s not found in %s/assets/fonts - falling back'%(fn,PDIR))
    return ', '.join(parts)
CAPFONT=''
for k in ('font_caption','font_main_regular','font_main_bold'):        # the caption is small and medium weight: a regular / medium cut reads best
    if PROF.get(k): CAPFONT=font_face(PROF[k])
    if CAPFONT: break
FACE_SRC=CAPFONT or "local('Helvetica Neue'), local('Arial')"
if not CAPFONT: print('WARNING: no caption font in the profile (run setup) - using the system sans')
P=json.load(open(A.plan)); BASE=os.path.dirname(os.path.abspath(A.plan))
CAP=dict(x=int(MINE.get('caption_x',92)),y=int(MINE.get('caption_y',1196)),size=int(MINE.get('caption_size',30)),lead=0.10); CAP.update(P.get('caption',{}))
SAFE_TOP,SAFE_BOTTOM=P.get('imageTop',270),P.get('imageBottom',830)
def norm(w): return re.sub(r"[^\w']",'',w.lower())
raw=json.load(open(A.words)); raw=raw.get('words',raw) if isinstance(raw,dict) else raw; words=[]
for x in raw:
    if isinstance(x,dict):
        if x.get('type','word')!='word' or x.get('event'): continue
        w,s,e=x.get('w',x.get('word',x.get('text'))),x.get('s',x.get('start')),x.get('e',x.get('end'))
    else: s,e,w=x[0],x[1],x[2]
    if norm(str(w)): words.append([float(s),float(e),str(w)])
def vprobe(f,e): return subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries',e,'-of','csv=p=0',f],capture_output=True,text=True).stdout.strip().split('\n')[0].rstrip(',')
if A.video:
    num,den=vprobe(A.video,'stream=r_frame_rate').split('/'); FPS=float(num)/float(den); RATE=f'{num}/{den}'
    VW,VH=[int(v) for v in vprobe(A.video,'stream=width,height').split(',')[:2]]
    VD=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',A.video],capture_output=True,text=True).stdout.strip())
    if abs(VW/VH-9/16)>0.01: raise SystemExit(f'video is {VW}x{VH}: this style is 9:16')
else: FPS=30.0; RATE='30/1'; VW,VH=1080,1920; VD=None
DUR=float(P.get('duration') or VD or words[-1][1]+0.3); DUR=min(DUR,VD) if VD else DUR
words=[w for w in words if w[0]<DUR-0.01]
# ---- captions: house rules + timing from the transcript ----
CAPS=[c.replace(',','') for c in P['captions']]; problems=[]; n=0; cap_t=[]
flat=[w for c in CAPS for w in c.split()]
if [norm(w) for w in flat]!=[norm(w[2]) for w in words]:
    a=[norm(w) for w in flat]; b=[norm(w[2]) for w in words]; i=next((i for i,(x,y) in enumerate(zip(a,b)) if x!=y),min(len(a),len(b)))
    raise SystemExit(f'captions do not match the transcript at word {i}: plan {a[i:i+4]} vs transcript {b[i:i+4]} ({len(a)} vs {len(b)} words up to {DUR:.1f}s)')
for i,c in enumerate(CAPS):
    cap_t.append(max(0.0,words[n][0]-CAP['lead'])); n+=len(c.split()); ls=c.split('\n')
    if len(ls)>3: problems.append(f'caption {i}: {len(ls)} lines (wants 1-3)')
    if any(len(l.split())>5 for l in ls): problems.append(f'caption {i}: a line has more than 5 words: {c!r}')
    if re.search(r'[.?!]',c): problems.append(f'caption {i}: has punctuation (this style has none): {c!r}')
# ---- images ----
CL=sorted(P['clusters'],key=lambda c:c['t'])
for ci,c in enumerate(CL):
    if not 1<=len(c['images'])<=3: problems.append(f"cluster {ci} at {c['t']}s has {len(c['images'])} images (wants 1-3)")
    nxt=CL[ci+1]['t'] if ci+1<len(CL) else DUR
    if nxt-c['t']>6.5: problems.append(f"cluster {ci} stays {nxt-c['t']:.1f}s (this style changes the cluster every 3-5s)")
    for im in c['images']:
        f=im['file'] if os.path.isabs(im['file']) else os.path.join(BASE,im['file']); im['_f']=f
        if not os.path.exists(f): raise SystemExit('missing image '+f)
        iw,ih=[int(v) for v in vprobe(f,'stream=width,height').split(',')[:2]]; h=im['w']*ih/iw
        if im['y']<SAFE_TOP-1 or im['y']+h>SAFE_BOTTOM+1: problems.append(f"{im['file']}: y {im['y']:.0f}-{im['y']+h:.0f} is outside the image band {SAFE_TOP}-{SAFE_BOTTOM}")
        if im['x']<40 or im['x']+im['w']>1040: problems.append(f"{im['file']}: too close to the frame edge")
        if not c['t']<=im['t']<nxt: problems.append(f"{im['file']}: pops at {im['t']}s, outside its cluster ({c['t']}-{nxt:.2f}s)")
for p in problems: print('CHECK:',p)
def state(t):
    cl=[c for c in CL if c['t']<=t+1e-6]; imgs=[i for i in cl[-1]['images'] if i['t']<=t+1e-6] if cl else []
    ci=[i for i,ct in enumerate(cap_t) if ct<=t+1e-6]; return imgs,(CAPS[ci[-1]] if ci else '')
def page(t):
    imgs,cap=state(t); placeholder=not A.video
    im=''.join(f'<img src="file://{i["_f"]}" style="left:{i["x"]}px;top:{i["y"]}px;width:{i["w"]}px;z-index:{i.get("z",1)}">' for i in imgs)
    sil='''<svg width=1080 height=1920><g fill="#6e6e6e"><ellipse cx="590" cy="1050" rx="165" ry="205"/><rect x="525" y="1200" width="130" height="130"/>
<path d="M150 1920 C150 1560 300 1380 525 1300 L655 1300 C880 1380 1030 1560 1030 1920 Z"/></g></svg>''' if placeholder else ''
    bg='linear-gradient(#3a3a3a,#2a2a2a)' if placeholder else 'transparent'
    return f"""<meta charset=utf-8><style>@font-face{{font-family:CapFont;src:{FACE_SRC}}}
html,body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:{bg}}} img{{position:absolute;display:block}} svg{{position:absolute;left:0;top:0}}
.cap{{position:absolute;left:{CAP['x']}px;top:{CAP['y']}px;font-family:CapFont,'Helvetica Neue',Arial,sans-serif;font-size:{CAP['size']}px;line-height:1.14;letter-spacing:-0.01em;color:#fff;white-space:pre;z-index:9;text-shadow:0 1px 6px rgba(0,0,0,.45)}}
</style>{sil}{im}<div class=cap>{H.escape(cap)}</div>"""
CHROME=next((c for c in [os.environ.get('CHROME'),'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','/Applications/Chromium.app/Contents/MacOS/Chromium',
    shutil.which('google-chrome'),shutil.which('chromium'),shutil.which('chromium-browser')] if c and os.path.exists(c)),None)
if not CHROME: raise SystemExit('Google Chrome (or Chromium) is needed to draw the frames: install it, or set CHROME=<path to the browser binary>')
def shot(job):
    name,htm=job; open(f'{W}/{name}.html','w').write(htm)
    cmd=[CHROME,'--headless=new','--disable-gpu','--hide-scrollbars','--force-device-scale-factor=1','--virtual-time-budget=3000','--allow-file-access-from-files',
         '--default-background-color=00000000','--window-size=1080,1920',f'--user-data-dir={W}/prof_{name}',f'--screenshot={W}/{name}.png',f'file://{W}/{name}.html']
    for _ in range(4):                                    # headless Chrome occasionally exits 2 on launch
        if subprocess.run(cmd,capture_output=True).returncode==0 and os.path.exists(f'{W}/{name}.png'): break
    else: raise SystemExit('chrome failed '+name)
    subprocess.run(['rm','-rf',f'{W}/prof_{name}'])
def run(c): subprocess.run(c,check=True)
if MODE=='sheet':
    ts=[max(i['t'] for i in c['images'])+0.01 for c in CL]; jobs=[(f'cl{i:02d}',page(t)) for i,t in enumerate(ts)]
    with ThreadPoolExecutor(4) as ex: list(ex.map(shot,jobs))
    for part in range(0,len(jobs),8):
        js=jobs[part:part+8]; ins=[]; fc=''
        for k,(j,t) in enumerate(zip(js,ts[part:part+8])):
            if A.video: ins+=['-ss',f'{t:.3f}','-i',A.video,'-i',f'{W}/{j[0]}.png']; fc+=f'[{2*k}:v]scale=1080:1920[b{k}];[b{k}][{2*k+1}:v]overlay,scale=270:-1[s{k}];'
            else: ins+=['-i',f'{W}/{j[0]}.png']; fc+=f'[{k}:v]scale=270:-1[s{k}];'
        fc+=''.join(f'[s{k}]' for k in range(len(js)))+(f'hstack=inputs={len(js)}' if len(js)>1 else 'null')+'[v]'
        o=f'{W}/sheet{"" if part==0 else part//8+1}.png'; run(['ffmpeg','-v','error','-y']+ins+['-filter_complex',fc,'-map','[v]','-frames:v','1',o]); print(o)
    sys.exit()
if not A.out: raise SystemExit('--out is required')
if MODE=='final' and not A.video: raise SystemExit('final needs --video (the placeholder is only for previews)')
if MODE=='final' and problems: raise SystemExit('fix the CHECK lines above before the final')
times=sorted(set([0.0]+[round(t,3) for t in cap_t]+[c['t'] for c in CL]+[i['t'] for c in CL for i in c['images']])); times=[t for t in times if t<DUR]
jobs=[(f's{i:03d}',page(t)) for i,t in enumerate(times)]
with ThreadPoolExecutor(4) as ex: list(ex.map(shot,jobs))
lst='ffconcat version 1.0\n'
for i,(t,nx) in enumerate(zip(times,times[1:]+[DUR+1])):
    fa,fb=round(t*FPS),round(nx*FPS)
    if fb>fa: lst+=f"file '{W}/s{i:03d}.png'\nduration {(fb-fa)/FPS:.5f}\n"
lst+=f"file '{W}/s{len(times)-1:03d}.png'\n"; open(W+'/list.txt','w').write(lst)
ev=[dict(id='img_'+os.path.splitext(os.path.basename(i['file']))[0],type='image',t0=i['t'],t1=round(CL[ci+1]['t'] if ci+1<len(CL) else DUR,3),text=os.path.basename(i['file'])) for ci,c in enumerate(CL) for i in c['images']]
ev+=[dict(id=f'cap{i:02d}',type='caption',t0=round(t,3),t1=round((cap_t+[DUR])[i+1],3),text=CAPS[i].replace('\n',' ')) for i,t in enumerate(cap_t)]
json.dump(ev,open(W+'/review_events.json','w'),indent=1)
sc=',scale=720:1280' if MODE=='preview' else ''
enc=['-c:v','libx264','-b:v','3M','-preset','veryfast','-c:a','aac','-b:a','128k'] if MODE=='preview' else ['-c:v','libx264','-crf','16','-preset','slow','-c:a','aac','-b:a','256k']
caps=['-f','concat','-safe','0','-i',W+'/list.txt']
if A.video:
    run(['ffmpeg','-v','error','-y','-i',A.video]+caps+(['-i',A.audio] if A.audio else [])+
        ['-filter_complex',f'[1:v]fps={RATE},format=rgba,scale={VW}:{VH}[c];[0:v][c]overlay=0:0:eof_action=repeat{sc}[v]','-map','[v]','-map','2:a' if A.audio else '0:a?','-t',f'{DUR:.3f}']+enc+['-pix_fmt','yuv420p','-movflags','+faststart',A.out])
else:
    run(['ffmpeg','-v','error','-y']+caps+(['-i',A.audio] if A.audio else [])+['-vf',f'fps={RATE}{sc}','-map','0:v']+(['-map','1:a'] if A.audio else [])+['-t',f'{DUR:.3f}']+enc+['-pix_fmt','yuv420p','-movflags','+faststart',A.out])
print('done',A.out,len(times),'states;',len(CL),'clusters,',sum(len(c['images']) for c in CL),'images,',len(CAPS),'captions; review events:',W+'/review_events.json')
