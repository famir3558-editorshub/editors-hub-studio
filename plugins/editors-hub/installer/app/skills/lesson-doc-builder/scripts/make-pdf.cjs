// Usage: node make-pdf.cjs <doc.html> <out.pdf>
// A 960x1280 paged PDF for reading or presenting from a tablet: every h2 section starts a new page, nothing is split mid-block.
const path=require('path'),{open}=require('./browser.cjs');
(async()=>{
  const {b,p}=await open(path.resolve(process.argv[2]),1,1280);
  await p.addStyleTag({content:`
    @page{size:960px 1280px;margin:44px 0}
    .page{padding:20px 70px 20px}
    figure,.bar,.proof,.model,li,svg,img{break-inside:avoid}
    h2,h3,h4,.runin{break-after:avoid}
    h2{break-before:page;margin-top:0} .proof .shot{height:175px} .proof{gap:22px 30px;margin-top:18px} .model{margin:14px 150px 6px}
  `});
  await p.pdf({path:path.resolve(process.argv[3]),printBackground:true,preferCSSPageSize:true});
  await b.close(); console.log(path.resolve(process.argv[3]));
})();
