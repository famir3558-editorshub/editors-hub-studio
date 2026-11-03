#!/usr/bin/env python3
"""Fitted stacked captions. The emphasised word is the anchor - big, in the accent colour and the emphasis font - and
the other words (the caption font, bold) are fitted around its letter shapes. Words pop on one by one, LEAD seconds
before they are spoken. Captions without an emphasised word are one plain line in the caption font.

Brand values come from the creator's profile through the setup placeholders (accent colour, emphasis font, caption
font, sizes, timing); a plan can override them per video. Run `python3 setup/apply_profile.py` once before using this.

  fit_captions.py sheet   --plan plan.json --words words.json --work W                     layout check sheet (W/sheet.png)
  fit_captions.py preview --plan plan.json --words words.json --work W --video V --out O   720p review preview
  fit_captions.py final   --plan plan.json --words words.json --work W --video V --out O   full-size final (only after approval)
  fit_captions.py overlay --plan plan.json --words words.json --work W --out O.mov         transparent ProRes 4444 overlay only

plan.json = {"cy": 1125, "lead": 0.22, "captions": [{"id": "cap00", "pre": "The one thing that kept", "em": "clients",
             "post": "from signing up"}, {"id": "cap01", "pre": "was a price they"}, ...]}
  pre = words before the emphasised word, em = the emphasised word(s), post = words after. No "em" = plain one-line caption.
  Optional per plan: lead (s), em (anchor px), small (px), gap (px, 5), maxBottom (px), accent (hex), trackSmall /
  trackAnchor (letter-spacing in em, default -0.05 / -0.03). Optional per caption: "cy".
words.json = word timings of the EDITED video: [[start, end, "word"], ...] or [{"w"|"word"|"text", "s"|"start", "e"|"end"}, ...].
--audio A  use this audio instead of the video's own track.   Layout is always worked out on a 1080x1920 canvas."""
import json, subprocess, os, sys, glob, argparse, re, shutil
SKILL=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDIR=os.path.expanduser(os.environ.get('CREATOR_PROFILE_DIR','~/.claude/creator-profile'))
# Filled from the creator's profile by setup/apply_profile.py (a plan.json can override each per video).
ACCENT='@@ACCENT@@'
ANCHOR_SRC=r'''@@FONT_ACCENT_SRC@@'''      # emphasis font: the big anchor word
SMALL_SRC=r'''@@FONT_CAPTION_SRC@@'''      # caption font (the main bold when no separate caption font was chosen)
ANCHOR_NAME='@@FONT_ACCENT_NAME@@'; SMALL_NAME='@@FONT_CAPTION_NAME@@'
DEF=dict(lead='@@LEAD_SECONDS@@',em='@@ANCHOR_PX@@',small='@@SMALL_PX@@',maxBottom='@@BOTTOM_LIMIT@@')
def num(v,fallback):
    try: return float(v)
    except (TypeError,ValueError): return float(fallback)
from concurrent.futures import ThreadPoolExecutor
ap=argparse.ArgumentParser(); ap.add_argument('mode',choices=['sheet','preview','final','overlay'])
ap.add_argument('--plan',required=True); ap.add_argument('--words',required=True); ap.add_argument('--work',required=True)
ap.add_argument('--video'); ap.add_argument('--audio'); ap.add_argument('--out'); A=ap.parse_args()
MODE=A.mode; W=os.path.abspath(A.work); os.makedirs(W,exist_ok=True)
plan=json.load(open(A.plan)); STACKS=plan['captions']; LEAD=num(plan.get('lead'),num(DEF['lead'],0.22))
if '@@' in ACCENT: raise SystemExit('this skill has not been set up yet: run python3 setup/apply_profile.py (see setup/SETUP.md)')
CFG=dict(accent=plan.get('accent',plan.get('orange',ACCENT)),em=num(plan.get('em'),num(DEF['em'],195)),
         small=num(plan.get('small'),num(DEF['small'],48)),gap=plan.get('gap',5),cy=plan.get('cy',1125),
         maxBottom=num(plan.get('maxBottom'),num(DEF['maxBottom'],1250)),maxW=940,
         trackSmall=plan.get('trackSmall',-0.05),trackAnchor=plan.get('trackAnchor',-0.03))
# ---- fonts: the profile's font sources, made absolute for the headless page; a font given by name is also searched for as a file ----
def local_names(src): return re.findall(r'local\("([^"]+)"\)',src)
def find_font_file(names):
    """Look for an installed font file by full name, PostScript name or family: system fonts, then Adobe Fonts (CoreSync) files."""
    want={n.lower() for n in names}
    if not want: return None
    files=glob.glob(os.path.expanduser('~/Library/Application Support/Adobe/CoreSync/plugins/livetype/.?/.*.otf'))
    rows=[]
    if shutil.which('fc-list'):
        rows=[l.split('|') for l in subprocess.run(['fc-list','--format','%{family}|%{fullname}|%{postscriptname}|%{file}\n'],capture_output=True,text=True).stdout.splitlines()]
    for f in files:
        if shutil.which('fc-scan'):
            r=subprocess.run(['fc-scan','-f','%{family}|%{fullname}|%{postscriptname}|%{file}',f],capture_output=True,text=True).stdout
            rows.append(r.split('|'))
    for r in rows:
        if len(r)<4: continue
        for field in r[:3]:
            if any(x.strip().lower() in want for x in field.split(',')): return r[3].strip()
    return None
def font_css(src,label):
    names=local_names(src); out=src.replace('url("assets/fonts/','url("file://'+SKILL+'/assets/fonts/')
    if PDIR and os.path.isdir(PDIR+'/assets/fonts'):                                  # profile folder as a second place for a font file
        for fn in re.findall(r'url\("file://[^"]*/assets/fonts/([^"]+)"\)',out):
            if not os.path.exists(f'{SKILL}/assets/fonts/{fn}') and os.path.exists(f'{PDIR}/assets/fonts/{fn}'):
                out=out.replace(f'file://{SKILL}/assets/fonts/{fn}',f'file://{PDIR}/assets/fonts/{fn}')
    f=find_font_file(names) if names else None
    if f: out=(out+', ' if out else '')+f'url("file://{f}")'
    if not out.strip(): raise SystemExit(f'{label}: no font source in the profile. Run python3 setup/apply_profile.py after saving the font (setup/SETUP.md, A3).')
    return out
ANCHOR_CSS=font_css(ANCHOR_SRC,'emphasis font'); SMALL_CSS=font_css(SMALL_SRC,'caption font')
def norm(w): return re.sub(r"[^\w']",'',w.lower())
raw=json.load(open(A.words)); raw=raw.get('words',raw) if isinstance(raw,dict) else raw; words=[]
for x in raw:
    if isinstance(x,dict):
        if x.get('type','word')!='word' or x.get('event'): continue
        w=x.get('w',x.get('word',x.get('text'))); s=x.get('s',x.get('start')); e=x.get('e',x.get('end'))
    else: s,e,w=x[0],x[1],x[2]
    if norm(str(w)): words.append([float(s),float(e),str(w)])
# ---- house rules, enforced ----
KEYS=('pre','em','post'); problems=[]
for i,c in enumerate(STACKS):
    c.setdefault('id',f'cap{i:02d}')
    for k in KEYS:
        if c.get(k): c[k]=' '.join(c[k].replace(',','').split())          # no commas, ever (full stops stay)
    n=sum(len(c.get(k,'').split()) for k in KEYS)
    if not c.get('em') and not 3<=n<=5: problems.append(f"{c['id']}: plain caption has {n} words (wants 3-5): {c.get('pre')}")
    if c.get('em') and len(c['em'].split())>2: problems.append(f"{c['id']}: emphasis should be one word (two at most): {c['em']}")
    ws=[w for k in KEYS for w in c.get(k,'').split()]
    if len(ws)>1 and re.search(r'[.?!]$',ws[-2]): problems.append(f"{c['id']}: ends on the first word of the next sentence ('{ws[-1]}'): start the next caption with it")
flat=[w for c in STACKS for k in KEYS for w in c.get(k,'').split()]
if [norm(w) for w in flat]!=[norm(w[2]) for w in words]:
    a=[norm(w) for w in flat]; b=[norm(w[2]) for w in words]; i=next((i for i,(x,y) in enumerate(zip(a,b)) if x!=y),min(len(a),len(b)))
    raise SystemExit(f'caption text does not match the transcript at word {i}: plan has {a[i:i+4]}, transcript has {b[i:i+4]} ({len(a)} vs {len(b)} words)')
for p in problems: print('RULE:',p)
if problems and MODE in('final',): raise SystemExit('fix the rule problems above before the final')
PAGE=r"""<meta charset=utf-8><style>
@font-face{font-family:SFB;src:__SMALLSRC__}
@font-face{font-family:Ivy;src:__ANCHORSRC__}
html,body{margin:0;background:transparent;overflow:hidden} canvas{display:block}
.pre{font-family:SFB;position:absolute;visibility:hidden} .pre i{font-family:Ivy}
</style><div class=pre>a<i>a</i></div><canvas id=c width=1080 height=1920></canvas><script>
const S=__STACK__, N=__N__, C=__CFG__, WD=1080, HT=1920;
const sf=px=>`${px}px SFB`, ivy=px=>`${px}px Ivy`;
function meas(ctx,font,ls,t){ctx.font=font;ctx.letterSpacing=ls+'px';const m=ctx.measureText(t);
  return {w:m.width+ls*0, l:m.actualBoundingBoxLeft, r:m.actualBoundingBoxRight, a:m.actualBoundingBoxAscent, d:m.actualBoundingBoxDescent};}
function comps(ws,maxLines){const out=[];(function rec(i,acc){if(i==ws.length){out.push(acc);return;}
  for(let j=i+1;j<=ws.length;j++){if(acc.length+1>maxLines)break;rec(j,acc.concat([ws.slice(i,j).join(' ')]));}})(0,[]);return out;}
function layout(){
  const o=document.createElement('canvas');o.width=WD;o.height=900;const x=o.getContext('2d',{willReadFrequently:true});
  const sls=C.trackSmall*C.small, items=[];
  if(!S.em){const m=meas(x,sf(C.small+4),C.trackSmall*(C.small+4),S.pre);
    return [{t:S.pre,font:sf(C.small+4),ls:C.trackSmall*(C.small+4),x:WD/2-m.w/2,y:C.cy+ (m.a-m.d)/2,color:'#fff'}];}
  // the emphasised word: shrink only if it would not fit the frame
  let E=C.em, m; for(;;){m=meas(x,ivy(E),C.trackAnchor*E,S.em); if(m.l+m.r<=C.maxW||E<90)break; E-=4;}
  const els=C.trackAnchor*E, BL=450, ex=Math.round(WD/2-(m.r-m.l)/2);
  x.clearRect(0,0,WD,900);x.font=ivy(E);x.letterSpacing=els+'px';x.fillStyle='#000';x.textBaseline='alphabetic';x.fillText(S.em,ex,BL);
  const d=x.getImageData(0,0,WD,900).data, top=new Array(WD).fill(null), bot=new Array(WD).fill(null);
  for(let cx=0;cx<WD;cx++){for(let y=0;y<900;y++){if(d[(y*WD+cx)*4+3]>40){if(top[cx]===null)top[cx]=y;bot[cx]=y;}}}
  let L=top.findIndex(v=>v!==null), R=WD-1-[...top].reverse().findIndex(v=>v!==null);
  const xh=meas(x,ivy(E),els,'x').a;                       // empty columns (gaps between letters) sit at x-height / baseline
  for(let cx=0;cx<WD;cx++){if(top[cx]===null){top[cx]=BL-xh;bot[cx]=BL;}}
  function place(lines,sky,dir,tie){                       // dir -1: stack upward on the top skyline; +1: downward on the bottom
    const s=sky.slice(), res=[]; let over=0;
    for(const t of lines){const k=meas(x,sf(C.small),sls,t), w=k.l+k.r; let best=null;
      const lo=L-18, hi=R+18-w;
      const cand=[]; if(hi<lo){cand.push(Math.round(WD/2-w/2));over+=lo-hi;} else for(let a=lo;a<=hi;a+=3)cand.push(Math.round(a));
      for(const a of cand){let e=dir<0?1e9:-1e9;
        for(let cx=Math.max(0,a-4);cx<Math.min(WD,a+w+4);cx++){e=dir<0?Math.min(e,s[cx]):Math.max(e,s[cx]);}
        const depth=dir<0?e:-e, pref=tie=='left'?-a:tie=='right'?a:-Math.abs(a+w/2-WD/2);
        if(!best||depth>best.depth+3||(Math.abs(depth-best.depth)<=3&&pref>best.pref))best={a,e,depth,pref};}
      const edge=best.e-dir*C.gap*-1*(dir<0?1:-1);
      let base, far;
      if(dir<0){const inkBottom=best.e-C.gap; base=inkBottom-k.d; far=base-k.a;}
      else{const inkTop=best.e+C.gap; base=inkTop+k.a; far=base+k.d;}
      for(let cx=0;cx<WD;cx++)s[cx]=dir<0?Math.min(s[cx],far):Math.max(s[cx],far);   // the next line always clears this one, so it reads top to bottom
      res.push({t,x:best.a+k.l,y:base,far});}
    return {res,over,ext:res.length?(dir<0?Math.min(...res.map(r=>r.far)):Math.max(...res.map(r=>r.far))):null};}
  function bestSplit(text,sky,dir,tie){const ws=text.split(' ');let best=null;
    for(const c of comps(ws,3)){const order=dir<0?c.slice().reverse():c;      // nearest line to the word is placed first
      const p=place(order,sky,dir,tie); const compact=dir<0?p.ext:-p.ext;
      const lens=c.map(l=>l.length), ragged=Math.max(...lens)-Math.min(...lens);
      const score=compact-0.6*p.over-0.25*ragged; if(!best||score>best.score)best={score,p,c,order};}
    return best;}
  let preL=[],postL=[];
  if(S.pre){const b=bestSplit(S.pre,top,-1,'left'); preL=b.order.map((t,i)=>({...b.p.res[i]})).reverse();}
  if(S.post){const b=bestSplit(S.post,bot,+1,'right'); postL=b.p.res;}
  const all=[...preL.map(r=>({...r,font:sf(C.small),ls:sls,color:'#fff'})),{t:S.em,font:ivy(E),ls:els,x:ex,y:BL,color:C.accent,em:1},
             ...postL.map(r=>({...r,font:sf(C.small),ls:sls,color:'#fff'}))];
  let T=1e9,B=-1e9; for(const it of all){const k=meas(x,it.font,it.ls,it.t);T=Math.min(T,it.y-k.a);B=Math.max(B,it.y+k.d);}
  let dy=C.cy-(T+B)/2; if(B+dy>C.maxBottom)dy=C.maxBottom-B;
  for(const it of all)it.y+=dy; return all;}
function draw(items){const ctx=document.getElementById('c').getContext('2d');let n=0;
  const passes=[it=>it.em,it=>!it.em];                     // small words are drawn over the big word
  const plan=[];for(const it of items){let pref='';for(const w of it.t.split(' ')){plan.push({it,w,pref});pref+=w+' ';}}
  plan.forEach((p,i)=>p.on=i<N);
  for(const pass of passes)for(const p of plan){if(!p.on||!pass(p.it))continue;
    ctx.font=p.it.font;ctx.letterSpacing=p.it.ls+'px';ctx.textBaseline='alphabetic';ctx.fillStyle=p.it.color;
    ctx.shadowColor='rgba(0,0,0,.62)';ctx.shadowBlur=16;ctx.shadowOffsetY=3;
    const off=p.pref?ctx.measureText(p.pref).width:0; ctx.fillText(p.w,p.it.x+off,p.it.y);}}
document.fonts.load('40px SFB').then(()=>document.fonts.load('40px Ivy')).then(()=>{draw(layout());document.title='ok';});
</script>"""
CHROME=next((c for c in (os.environ.get('CHROME'),'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        shutil.which('google-chrome'),shutil.which('chromium'),shutil.which('chrome')) if c and os.path.exists(c)),None)
if not CHROME: raise SystemExit('Google Chrome not found (the layout is measured in headless Chrome). Install it, or set CHROME=/path/to/chrome.')
def preflight():
    """Headless Chrome silently swaps in another font when a face fails to load, which would ship the wrong look. Check both first."""
    page=f'{W}/fontcheck.html'
    css=f'@font-face{{font-family:SFB;src:{SMALL_CSS}}}@font-face{{font-family:Ivy;src:{ANCHOR_CSS}}}'
    open(page,'w').write('<meta charset=utf-8><style>'+css+'</style><body><script>Promise.all(["SFB","Ivy"].map(f=>document.fonts.load("40px "+f).then(a=>a.length,()=>0))).then(r=>{document.body.textContent="FONTS "+r.join(",")})</script>')
    r=subprocess.run([CHROME,'--headless=new','--disable-gpu','--virtual-time-budget=4000',f'--user-data-dir={W}/prof_fontcheck','--dump-dom',f'file://{page}'],capture_output=True,text=True).stdout
    subprocess.run(['rm','-rf',f'{W}/prof_fontcheck'])
    m=re.search(r'FONTS (\d),(\d)',r)
    if not m: print('note: could not verify the fonts (headless Chrome gave no answer); check the layout sheet by eye'); return
    if m.group(1)=='0': raise SystemExit(f'caption font "{SMALL_NAME}" did not load. Copy its file into ~/.claude/creator-profile/assets/fonts, save it with --set font_caption (or font_main_bold) and run python3 setup/apply_profile.py again. Never ship a fallback font.')
    if m.group(2)=='0': raise SystemExit(f'emphasis font "{ANCHOR_NAME}" did not load. Copy its file into ~/.claude/creator-profile/assets/fonts, save it with --set font_accent and run python3 setup/apply_profile.py again. An Adobe font needs Creative Cloud running. Never ship a fallback font.')
preflight()
def nwords(s): return sum(len(s.get(k,'').split()) for k in KEYS)
def shot(job):
    name,si,n=job; cfg=dict(CFG); cfg['cy']=STACKS[si].get('cy',CFG['cy'])
    open(f'{W}/{name}.html','w').write(PAGE.replace('__SMALLSRC__',SMALL_CSS).replace('__ANCHORSRC__',ANCHOR_CSS).replace('__STACK__',json.dumps(STACKS[si])).replace('__N__',str(n)).replace('__CFG__',json.dumps(cfg)))
    cmd=[CHROME,'--headless=new','--disable-gpu','--hide-scrollbars','--force-device-scale-factor=1','--virtual-time-budget=4000',
         '--default-background-color=00000000','--window-size=1080,1920',f'--user-data-dir={W}/prof_{name}',
         f'--screenshot={W}/{name}.png',f'file://{W}/{name}.html']
    for _ in range(4):                                       # headless Chrome occasionally exits 2 on launch
        if subprocess.run(cmd,capture_output=True).returncode==0 and os.path.exists(f'{W}/{name}.png'): break
    else: raise SystemExit('chrome failed on '+name)
    subprocess.run(['rm','-rf',f'{W}/prof_{name}'])
def run(c): subprocess.run(c,check=True)
if MODE=='sheet':
    jobs=[(f'final_{si:02d}',si,nwords(s)) for si,s in enumerate(STACKS)]
    with ThreadPoolExecutor(4) as ex: list(ex.map(shot,jobs))
    for part in range(0,len(jobs),16):                       # 16 captions per sheet
        js=jobs[part:part+16]; ins=[]
        for j in js: ins+=['-i',f'{W}/{j[0]}.png']
        fc=''.join(f'[{i}:v]crop=1080:520:0:{max(0,STACKS[j[1]].get("cy",CFG["cy"])-260)},format=rgba[c{i}];color=0x1a1512:s=1080x520[b{i}];[b{i}][c{i}]overlay=shortest=1[o{i}];' for i,j in enumerate(js))
        fc+=''.join(f'[o{i}]' for i in range(len(js)))+(f'xstack=inputs={len(js)}:layout='+'|'.join(f'{(i%4)*1090}_{(i//4)*530}' for i in range(len(js)))+':fill=black,' if len(js)>1 else '')+'scale=iw/2:-1[v]'
        out=f'{W}/sheet{"" if part==0 else part//16+1}.png'; run(['ffmpeg','-v','error','-y']+ins+['-filter_complex',fc,'-map','[v]','-frames:v','1',out]); print(out)
    sys.exit()
if not A.out or (MODE!='overlay' and not A.video): raise SystemExit('--out (and --video) are required')
def probe(f,e): return subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries',e,'-of','csv=p=0',f],capture_output=True,text=True).stdout.strip().split('\n')[0].rstrip(',')
if A.video:
    num,den=probe(A.video,'stream=r_frame_rate').split('/'); FPS=float(num)/float(den); RATE=f'{num}/{den}'
    DUR=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',A.video],capture_output=True,text=True).stdout.strip())
    VW,VH=[int(v) for v in probe(A.video,'stream=width,height').split(',')[:2]]
else: FPS=30.0; RATE='30/1'; DUR=words[-1][1]+1.0; VW,VH=1080,1920
jobs=[]; events=[]; wi=0; rev=[]
for si,s in enumerate(STACKS):
    t_first=None
    for n in range(1,nwords(s)+1):
        name=f'{si:03d}_{n:02d}'; t=max(0.0,words[wi][0]-LEAD); t_first=t if t_first is None else t_first
        jobs.append((name,si,n)); events.append([name,t]); wi+=1
    rev.append(dict(id=s['id'],type='caption',t0=round(t_first,3),text=' '.join(s.get(k,'') for k in KEYS).strip()))
with ThreadPoolExecutor(4) as ex: list(ex.map(shot,jobs))
for a,b in zip(events,events[1:]+[[None,DUR+1]]): a.append(b[1])        # every word holds until the next; a stack clears on the next caption's first word
for r,nx in zip(rev,rev[1:]+[dict(t0=DUR)]): r['t1']=round(nx['t0'],3)
json.dump(rev,open(W+'/review_events.json','w'),indent=1)
lst="ffconcat version 1.0\n"; blank=W+'/blank.png'
run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=black@0:s=1080x1920,format=rgba','-frames:v','1',blank])
segs=[(blank,0,events[0][1])]+[(f'{W}/{n}.png',a,b) for n,a,b in events]
for f,a,b in segs:
    fa,fb=round(a*FPS),round(b*FPS)
    if fb>fa: lst+=f"file '{f}'\nduration {(fb-fa)/FPS:.6f}\n"
lst+=f"file '{segs[-1][0]}'\n"; open(W+'/caps.txt','w').write(lst)
caps=['-f','concat','-safe','0','-i',W+'/caps.txt']
if MODE=='overlay':
    run(['ffmpeg','-v','error','-y']+caps+['-vf',f'fps={RATE},format=yuva444p10le','-t',f'{DUR:.3f}','-c:v','prores_ks','-profile:v','4444',A.out])
else:
    if abs(VW/VH-9/16)>0.01: raise SystemExit(f'video is {VW}x{VH}: this caption style is built for 9:16')
    sc=',scale=720:1280' if MODE=='preview' else ''
    enc=['-c:v','libx264','-b:v','3M','-preset','veryfast','-c:a','aac','-b:a','128k'] if MODE=='preview' else ['-c:v','libx264','-crf','16','-preset','slow','-c:a','aac','-b:a','256k']
    amap=['-map','2:a'] if A.audio else ['-map','0:a?']
    run(['ffmpeg','-v','error','-y','-i',A.video]+caps+(['-i',A.audio] if A.audio else [])+
        ['-filter_complex',f'[1:v]fps={RATE},format=rgba,scale={VW}:{VH}[c];[0:v][c]overlay=0:0:eof_action=repeat{sc}[v]','-map','[v]']+amap+
        ['-t',f'{DUR:.3f}']+enc+['-pix_fmt','yuv420p','-movflags','+faststart',A.out])
print('done',A.out,len(events),'word states,',len(STACKS),'captions; review events:',W+'/review_events.json')
