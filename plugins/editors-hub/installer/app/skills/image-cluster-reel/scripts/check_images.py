#!/usr/bin/env python3
"""Tile the CHOSEN images large (about 470 px each) so watermarks, stock logos and photographer credits can be seen.
  check_images.py out.jpg img1 img2 ...     Look at out.jpg and replace anything that carries a mark."""
import sys,subprocess
out,fs=sys.argv[1],sys.argv[2:]; ins=[];fc='';lay=[]
for n,f in enumerate(fs):
    ins+=['-i',f]; fc+=f'[{n}:v]scale=470:470:force_original_aspect_ratio=decrease,pad=476:476:(ow-iw)/2:(oh-ih)/2:gray[t{n}];'; lay.append(f'{(n%4)*476}_{(n//4)*476}')
fc+=''.join(f'[t{i}]' for i in range(len(fs)))+(f'xstack=inputs={len(fs)}:layout='+'|'.join(lay)+':fill=black' if len(fs)>1 else 'null')+'[v]'
subprocess.run(['ffmpeg','-v','error','-y']+ins+['-filter_complex',fc,'-map','[v]','-frames:v','1',out],check=True); print(out)
