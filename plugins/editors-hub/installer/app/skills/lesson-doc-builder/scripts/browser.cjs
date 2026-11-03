// Shared by render.cjs and make-pdf.cjs: finds puppeteer-core and a Chromium-family browser on this computer.
// puppeteer-core is installed once at setup:  npm install --prefix ~/.claude/creator-profile/tools puppeteer-core
// Override the browser with LESSON_DOC_BROWSER=/full/path/to/browser
const path=require('path'),fs=require('fs'),os=require('os');
function puppeteer(){
  const tools=path.join(process.env.CREATOR_PROFILE_DIR||path.join(os.homedir(),'.claude/creator-profile'),'tools/node_modules/puppeteer-core');
  for(const m of [tools,'puppeteer-core','puppeteer']){try{return require(m)}catch(e){}}
  console.error('puppeteer-core is not installed. Run once:\n  npm install --prefix ~/.claude/creator-profile/tools puppeteer-core');process.exit(1);
}
function browser(){
  const c=[process.env.LESSON_DOC_BROWSER,
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser','/Applications/Chromium.app/Contents/MacOS/Chromium','/Applications/Arc.app/Contents/MacOS/Arc',
    'C:/Program Files/Google/Chrome/Application/chrome.exe','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    '/usr/bin/google-chrome','/usr/bin/chromium','/usr/bin/chromium-browser'].filter(Boolean);
  const hit=c.find(p=>fs.existsSync(p));
  if(!hit){console.error('No Chrome, Edge, Brave or Chromium found. Install Google Chrome, or set LESSON_DOC_BROWSER to the browser\'s full path.');process.exit(1);}
  return hit;
}
async function open(file,dpr=1,h=1080){
  const b=await puppeteer().launch({executablePath:browser(),headless:'new'});
  const p=await b.newPage(); await p.setViewport({width:960,height:h,deviceScaleFactor:dpr});
  await p.goto('file://'+file,{waitUntil:'networkidle0'});
  await p.evaluate(()=>Promise.all([...document.images].map(i=>i.complete?0:new Promise(r=>{i.onload=i.onerror=r}))));
  await p.evaluate(()=>document.fonts.ready);
  return {b,p};
}
module.exports={open};
