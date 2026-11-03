// Usage: node render.cjs <doc.html> [--stops 0,1500,3000]
// Writes <dir>/preview/full-page.png, view-N.png (960x1080 scroll stops), view-N@4k.png and split-screen-1080p.png (needs ffmpeg).
// Also prints which fonts really rendered, so a silent fallback is caught.
const path=require('path'),fs=require('fs'),{execSync}=require('child_process'),{open}=require('./browser.cjs');
const file=path.resolve(process.argv[2]); const dir=path.dirname(file); const out=path.join(dir,'preview');
const si=process.argv.indexOf('--stops');
const DOC_SIDE='@@DOC_SIDE@@';   // which half of the frame the document sits on while recording
(async()=>{
  fs.mkdirSync(out,{recursive:true});
  const {b,p}=await open(file);
  await p.screenshot({path:path.join(out,'full-page.png'),fullPage:true});
  const h=await p.evaluate(()=>document.body.scrollHeight);
  const fonts=await p.evaluate(()=>['DocMain','DocTitle','DocAccent'].map(f=>f+': '+([...document.fonts].filter(x=>x.family.replace(/"/g,'')===f&&x.status==='loaded').length?'loaded':'NOT LOADED (fallback font in use)')));
  const stops=si>0?process.argv[si+1].split(',').map(Number):Array.from({length:Math.ceil(h/1300)},(_,i)=>i*1300);
  for(const [i,y] of stops.entries()){await p.evaluate(y=>window.scrollTo(0,y),y);await new Promise(r=>setTimeout(r,300));await p.screenshot({path:path.join(out,`view-${i}.png`)});}
  // 4K stills of each stop for the edit (DPR 2 = 1920x2160, one half of a 4K frame)
  await p.setViewport({width:960,height:1080,deviceScaleFactor:2});
  for(const [i,y] of stops.entries()){await p.evaluate(y=>window.scrollTo(0,y),y);await new Promise(r=>setTimeout(r,300));await p.screenshot({path:path.join(out,`view-${i}@4k.png`)});}
  await b.close();
  const order=DOC_SIDE.trim().toLowerCase()==='right'?'[1][0]hstack':'[0][1]hstack';
  try{execSync(`ffmpeg -loglevel error -y -i "${out}/view-${Math.min(1,stops.length-1)}.png" -f lavfi -i "color=c=#1a1a1a:s=960x1080" -filter_complex "${order}" -frames:v 1 "${out}/split-screen-1080p.png"`);}catch(e){console.error('split-screen mock skipped (ffmpeg not found or failed):',e.message.split('\n')[0])}
  console.log(`height ${h}px · ${stops.length} stops · ${out}\n${fonts.join('\n')}`);
})();
