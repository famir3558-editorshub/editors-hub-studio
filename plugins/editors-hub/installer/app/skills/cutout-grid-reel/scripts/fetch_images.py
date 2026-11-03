#!/usr/bin/env python3
"""Find candidate images for each beat (Bing image search, stock / print-shop sites excluded so results are not watermarked).
  fetch_images.py queries.txt OUTDIR [--n 5]
queries.txt: one "key|search words" per line. Saves OUTDIR/<key>_<i>.img (original) and writes OUTDIR/sheet_<n>.jpg contact
sheets (small, for choosing) - then ALWAYS run check_images.py on the ones you pick: watermarks do not show at sheet size."""
import sys,re,html,subprocess,os,urllib.parse
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
BAD=('istock','shutterstock','alamy','getty','dreamstime','123rf','depositphotos','stock.adobe','ftcdn','freepik','vecteezy','etsy','etsystatic',
     'redbubble','society6','amazon','vectorstock','pngtree','bigstock','canstock','fineartamerica','pixers','stablediffusionweb','lookaside','zazzle','teepublic')
qf,out=sys.argv[1],sys.argv[2]; N=int(sys.argv[sys.argv.index('--n')+1]) if '--n' in sys.argv else 5; os.makedirs(out,exist_ok=True)
def search(q):
    r=subprocess.run(['curl','-sL','-A',UA,'https://www.bing.com/images/search?q='+urllib.parse.quote(q)+'&form=HDRSC2&first=1'],capture_output=True,text=True,errors='ignore').stdout
    return [u for u in (html.unescape(m) for m in re.findall(r'murl&quot;:&quot;(.*?)&quot;',r)) if not any(b in u.lower() for b in BAD)][:N*3]
keys=[]
for line in open(qf):
    if '|' not in line: continue
    key,q=line.strip().split('|',1); keys.append(key); got=0
    for u in search(q):
        if got>=N: break
        f=f'{out}/{key}_{got}.img'; subprocess.run(['curl','-sL','-m','12','-A',UA,'-o',f,u])
        ok=os.path.exists(f) and os.path.getsize(f)>8000 and subprocess.run(['ffmpeg','-v','error','-y','-i',f,'-vf','scale=360:-2','-frames:v','1',f'{out}/{key}_{got}.thumb.jpg'],capture_output=True).returncode==0
        if ok: got+=1
        else:
            for x in (f,f'{out}/{key}_{got}.thumb.jpg'):
                if os.path.exists(x): os.remove(x)
    print(key,got,flush=True)
for part in range(0,len(keys),8):
    ins=[];fc='';lay=[];n=0
    for r,k in enumerate(keys[part:part+8]):
        for c in range(N):
            f=f'{out}/{k}_{c}.thumb.jpg'
            if not os.path.exists(f): continue
            ins+=['-i',f]; fc+=f'[{n}:v]scale=230:230:force_original_aspect_ratio=decrease,pad=236:236:(ow-iw)/2:(oh-ih)/2:black[t{n}];'; lay.append(f'{c*236}_{r*236}'); n+=1
    if not n: continue
    fc+=''.join(f'[t{i}]' for i in range(n))+(f'xstack=inputs={n}:layout='+'|'.join(lay)+':fill=black' if n>1 else 'null')+'[v]'
    o=f'{out}/sheet_{part//8}.jpg'; subprocess.run(['ffmpeg','-v','error','-y']+ins+['-filter_complex',fc,'-map','[v]','-frames:v','1',o],check=True); print(o,'rows:',keys[part:part+8])
