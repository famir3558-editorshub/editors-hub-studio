// Dot-grid helper. Markup: <svg ...><g data-dots="78" data-accent="11,40,67" data-y="44" data-cols="26"></g></svg>
//   data-accent = the indexes of the dots drawn in the accent colour; the rest are neutral grey.
// Bar helper:            <svg ...><g data-mix="10" data-split="5"></g></svg>  (first `split` light, rest #111)
const NS='http://www.w3.org/2000/svg';
document.querySelectorAll('[data-dots]').forEach(g=>{
  const n=+g.dataset.dots, cols=+(g.dataset.cols||26), y0=+(g.dataset.y||20);
  const ac=(g.dataset.accent||'').split(',').filter(Boolean).map(Number);
  for(let i=0;i<n;i++){const c=document.createElementNS(NS,'circle');
    c.setAttribute('cx',12+(i%cols)*29.5);c.setAttribute('cy',y0+Math.floor(i/cols)*28);c.setAttribute('r',9);
    c.setAttribute('class',ac.includes(i)?'af':'nf');g.appendChild(c);}
});
document.querySelectorAll('[data-mix]').forEach(g=>{
  const n=+g.dataset.mix, s=+g.dataset.split, w=780/n;
  for(let i=0;i<n;i++){const r=document.createElementNS(NS,'rect');
    r.setAttribute('x',i*w+(i>=s?6:0));r.setAttribute('y',10);r.setAttribute('width',w-8);r.setAttribute('height',54);r.setAttribute('rx',8);
    r.setAttribute('fill',i<s?'#F6F4F1':'#111');if(i<s)r.setAttribute('stroke','#E6E1DA');g.appendChild(r);}
});
