import os, reel_engine as E
from reel_engine import scene, comment
ROOT=os.path.dirname(os.path.abspath(__file__)); DUR=16.55
FACE=[[3.9,13.0]]; FULL=[]
E.init(ROOT,DUR,FACE,FULL,title="engine test",words="words.json",emph={"grow","matrix","change","selfish"},keep={"C"},hide=[[5.38,6.02],[6.9,7.56]])
scene("s01-hook",0,DUR,False,'<div id="{ID}-card" class="card de-glass"></div>',".card{position:absolute;left:240px;top:300px;width:600px;height:360px;background:rgba(20,20,20,.92)}",'pop(tl,"card",0.0);')
E.overlay(
 behind='<div id="cnt" class="ov-line ov-hb" style="top:306px;font-size:214px;letter-spacing:-0.065em">13,000</div><div id="lb" class="ov-line ov-pi" style="top:304px;font-size:122px">change</div><div id="pb1" class="ov-pill">C1</div><div id="pb2" class="ov-pill">C2</div><div id="pb3" class="ov-pill">C3</div>',
 front='<div id="prof"></div><div id="pf1" class="ov-pill">C1</div><div id="pf2" class="ov-pill">C2</div><div id="pf3" class="ov-pill">C3</div>'+comment("cm1",80,1196,"ok but what's in it for me?")+comment("cm2",360,1294,"will this get me more views?"),
 css='#prof{position:absolute;left:90px;top:1214px;width:700px;height:236px;border-radius:34px;background:#000 url("assets/img/client-profile.jpg") no-repeat;background-size:700px auto;background-position:0 -12px;opacity:0}',
 js="""slide('#prof',520,0,4.14,0.46); orise('#cnt',5.36,40); counter('#cnt',13000,500000,6.48,0.95); oout('#prof',7.48); oout('#cnt',7.48);
orbit({front:['#pf1','#pf2','#pf3'],back:['#pb1','#pb2','#pb3'],cx:540,cy:1100,rx:400,ry:150,t:7.6,dur:1.66});
orise('#lb',10.22,30); slide('#cm1',-420,0,10.8); slide('#cm2',460,0,11.14); oout('#cm1',12.86); oout('#cm2',12.86); oout('#lb',12.86);""")
E.build()
