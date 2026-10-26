/* ---- 新キャラエンジン(3頭身・はっきり色) ---- */
const CH = (() => {


function mix(a,b,t){const A=[1,3,5].map(i=>parseInt(a.slice(i,i+2),16)),B=[1,3,5].map(i=>parseInt(b.slice(i,i+2),16));return '#'+A.map((v,i)=>Math.round(v+(B[i]-v)*t).toString(16).padStart(2,'0')).join('')}
function gen(V,o,pose,fr){
 const hw=V.hw,hh=V.hh,bw=V.bw,bh=V.bh,lh=V.lh,W=hw+12,hy=3,H=hy+hh+1+bh+lh+4,cx=W/2;
 const B=new Array(W*H).fill(null);const R=(x,y,w,h,c)=>{for(let j=0;j<h;j++)for(let i=0;i<w;i++){const xx=Math.round(x+i),yy=Math.round(y+j);if(xx>=0&&yy>=0&&xx<W&&yy<H)B[yy*W+xx]=c}};
 let sk=o.skin,hr=o.hair,cl=o.cloth,pn=o.pants;
 if(V.mono){const h=V.mono;sk='#e8e2d4';hr='#2a2a3a';cl=h;pn='#2a2a3a'}
 if(V.pastel){const Q=c=>mix(mix(c,'#ffffff',.16),'#f4dcc8',.07);sk=Q(sk);hr=Q(hr);cl=Q(cl);pn=Q(pn)}
 let skS=mix(sk,'#7a3a2a',.22),skL=mix(sk,'#ffffff',.25),hrL=mix(hr,'#ffffff',V.pastel?.55:.32),hrD=mix(hr,V.pastel?'#5a3a78':'#000000',V.pastel?.3:.35),clL=mix(cl,'#ffffff',.3),clD=mix(cl,V.pastel?'#4a3a78':'#000000',V.pastel?.28:.3),pnD=mix(pn,V.pastel?'#3a2a68':'#000000',.3);
 const sing=pose==='sing',Y=(sing&&fr%2)?-1:(pose==='slump'?1:0),sh=V.shade;
 const ty=hy+hh+1+Y,ly=ty+bh,lw=Math.max(2,Math.floor(bw/2)-(V.slim?1:0));
 // legs
 R(cx-lw,ly,lw,lh,pn);R(cx,ly,lw,lh,pn);if(sh)R(cx-1,ly,1,lh,pnD),R(cx+lw-1,ly,1,lh,pnD);
 const sw=lw+1;R(cx-sw,ly+lh,sw,2,V.shoe||'#f4f4fa');R(cx,ly+lh,sw,2,V.shoe||'#f4f4fa');R(cx-sw,ly+lh+2,sw,1,'#3a3350');R(cx,ly+lh+2,sw,1,'#3a3350');
 // torso
 const tx=cx-bw/2;R(tx,ty,bw,bh,cl);if(sh){R(tx,ty,1,bh,clL);R(tx+bw-1,ty,1,bh,clD);R(tx,ty+bh-2,bw,2,sh>1?pnD:clD)}
 if(sh>1)for(let k=1;k<bw-2;k+=3)R(tx+k+1,ty+2+(k%2),1,bh-5,mix(cl,'#000',.12));
 R(cx-1,ty,2,2,skS);
 // arms
 const aw=V.aw||2,ah=bh-2;const up=pose==='cheer';if(up){R(tx-aw,ty-4+(fr%2),aw,7,cl);R(tx-aw,ty-6+(fr%2),aw,2,sk)}else{R(tx-aw,ty+1,aw,ah,cl);R(tx-aw,ty+1+ah,aw,2,sk)}
 if(up){R(tx+bw,ty-4+((fr+1)%2),aw,7,cl);R(tx+bw,ty-6+((fr+1)%2),aw,2,sk)}else if(sing){R(tx+bw,ty+1,aw,ah-2,cl);R(tx+bw,ty-1,aw,3,sk);R(tx+bw+aw-1,ty-5,1,5,'#a9b0c2');R(tx+bw+aw-2,ty-7,3,3,'#3a3a4c')}
 else{R(tx+bw,ty+1,aw,ah,cl);R(tx+bw,ty+1+ah,aw,2,sk)}
 if(sh){R(tx+bw+aw-1,ty+1,1,ah,clD)}
 // neck
 R(cx-1,hy+hh+Y,2,1,skS);
 // back hair
 const hyy=hy+Y;
 if(o.style==='long')R(cx-hw/2-1,hyy+3,hw+2,hh+1,hrD);
 if(o.style==='pony')R(cx+hw/2,hyy+3,3,hh-2,hr);
 // head
 for(let i=0;i<hh;i++){const ins=(i===0||i===hh-1)?(V.round||2):(i===1||i===hh-2)?1:0;const x0=cx-hw/2+ins,ww=hw-ins*2;R(x0,hyy+i,ww,1,sk);if(sh){R(x0+ww-2,hyy+i,2,1,skS);if(i>hh-4)R(x0,hyy+i,ww,1,skS)}}
 // hair cap
 const cap=Math.round(hh*(V.cap||.38));
 if(o.style==='spike'){for(let k=0;k<5;k++){const sx=cx-hw/2+k*(hw/5);R(sx,hyy-2-(k%2),hw/5+1,4,hr)}}
 R(cx-hw/2-1,hyy+1,hw+2,cap,hr);R(cx-hw/2+1,hyy-1,hw-2,2,hr);R(cx-hw/2+2,hyy-2,hw-4,1,hr);
 if(sh){R(cx-hw/2+2,hyy-1,Math.floor(hw/3),1,hrL);R(cx-hw/2-1,hyy+cap,hw+2,1,hrD)}
 [[0,3],[Math.floor(hw/3),2],[Math.floor(hw*.55),4],[hw-3,2]].forEach(([dx,l],i)=>R(cx-hw/2+dx,hyy+cap,Math.min(3,hw-dx),l-(i%2),hr));
 const sideL=(o.style==='long'||o.style==='bob')?hh-1:Math.round(hh*.55);
 R(cx-hw/2-1,hyy+2,2,sideL,hr);R(cx+hw/2-1,hyy+2,2,sideL,sh?hrD:hr);
 // face
 const ex=Math.round(hw*.27),ey=hyy+Math.round(hh*.56),eh=V.eye==='big'?4:V.eye==='dot'?2:1,ew=V.eye==='big'?3:2;
 if(V.eye!=='none'){const EC=V.pastel?'#3a2a58':'#1d1626',IR=V.pastel?mix(hr,'#8fd0ff',.55):'#6a5aa8';R(cx-ex-1,ey,ew,eh,EC);R(cx+ex-ew+1,ey,ew,eh,EC);if(V.eye==='big'){R(cx-ex-1,ey,1,1,'#fff');R(cx+ex-ew+1,ey,1,1,'#fff');R(cx-ex,ey+eh-2,2,2,IR);R(cx+ex-ew+2,ey+eh-2,2,2,IR);R(cx-ex-1,ey+eh-1,1,1,mix(IR,'#fff',.4));R(cx+ex-ew+1,ey+eh-1,1,1,mix(IR,'#fff',.4))}else if(V.eye==='dot'){R(cx-ex-1,ey,1,1,'#fff');R(cx+ex-ew+1,ey,1,1,'#fff')}}
 else{R(cx-ex,ey,1,1,'#1d1626');R(cx+ex,ey,1,1,'#1d1626')}
 if(V.blush)R(cx-ex-2,ey+eh,2,1,'#f0928e'),R(cx+ex+1,ey+eh,2,1,'#f0928e');
 const my=hyy+hh-3;if(sing&&fr%2===0)R(cx-1,my,3,2,'#6a2030');else R(cx-1,my+1,3,1,'#8a3a3a');
 if(o.blink){R(cx-ex-1,ey,ew,eh,sk);R(cx+ex-ew+1,ey,ew,eh,sk);R(cx-ex-1,ey+eh-1,ew,1,'#3a2a52');R(cx+ex-ew+1,ey+eh-1,ew,1,'#3a2a52')}
 if(pose==='slump'){R(cx-1,my,3,2,sk);R(cx-1,my+1,3,1,'#7a4a4a');R(cx-2,my+2,1,1,'#7a4a4a');R(cx+2,my+2,1,1,'#7a4a4a');R(cx+ex+1,ey+eh,1,4,'#8ad0ff');R(cx+ex+1,ey+eh+4,1,1,'#d8f0ff')}
 if(o.glasses&&V.eye!=='none'){const gc='#2a2a3a';R(cx-ex-2,ey-1,5,1,gc);R(cx-ex-2,ey+eh,5,1,gc);R(cx-ex-2,ey-1,1,eh+2,gc);R(cx-ex+2,ey-1,1,eh+2,gc);R(cx+ex-3,ey-1,5,1,gc);R(cx+ex-3,ey+eh,5,1,gc);R(cx+ex-3,ey-1,1,eh+2,gc);R(cx+ex+1,ey-1,1,eh+2,gc)}

 if(V.sfc){
  // hair strands & highlight band
  for(let k=0;k<hw;k+=3)R(cx-hw/2+k,hyy+1,1,cap-1,hrD);
  R(cx-hw/2+1,hyy+1,hw-2,1,hrL);R(cx-hw/2+2,hyy,Math.floor(hw/2),1,hrL);
  // belt, collar, boots
  R(tx,ty+bh-2,bw,1,'#3a2a20');R(cx-1,ty+bh-2,2,1,'#e8c860');
  R(tx+1,ty,bw-2,1,clL);
  R(cx-lw,ly+lh-2,lw,2,'#5a3a2a');R(cx,ly+lh-2,lw,2,'#5a3a2a');R(cx-lw,ly+lh-3,lw,1,'#8a6040');R(cx,ly+lh-3,lw,1,'#8a6040');
  if(V.pad){R(tx-1,ty,3,3,clL);R(tx+bw-2,ty,3,3,clD);R(tx-1,ty+2,3,1,clD)}
  if(V.cape){R(tx-1,ty+2,1,bh+lh-2,mix(o.cloth,'#000',.45));R(tx+bw,ty+2,1,bh+lh-2,mix(o.cloth,'#000',.55))}
  // face: lid line
  if(V.eye!=='big'){R(cx-ex-1,ey-1,ew,1,skS);R(cx+ex-ew+1,ey-1,ew,1,skS)}
 }

 const E=o.era,fl=(c)=>R(tx-2,ty,bw+4,bh+lh+1,c);
 if(E==='prim'||E==='paleo'){const fu='#8a6a44';R(tx,ty,bw,bh,fu);R(tx,ty,bw,2,'#a98a5c');for(let k=0;k<bw;k+=2)R(tx+k,ty+bh,1,3,fu);R(tx,ty+bh-2,bw,1,'#5a4630');R(cx-lw,ly+3,lw*2,lh-3,sk);R(cx-lw,ly+lh-4,lw*2,1,'#5a4630');R(cx-sw,ly+lh,sw*2,3,sk);R(cx+hw/2-4,hyy-1,5,1,'#f4f0e0');R(cx+hw/2-1,hyy-2,1,3,'#f4f0e0')}
 if(E==='edo'){R(tx,ty,bw,bh,cl);R(tx,ty+bh-4,bw,3,'#f0e8d0');R(cx-2,ty,1,4,'#f0e8d0');R(cx+1,ty,1,4,'#f0e8d0');R(cx-lw-1,ly,lw*2+2,lh,mix(pn,'#ffffff',.18));R(cx,ly,1,lh,pnD);R(cx-sw,ly+lh,sw*2,2,'#e8d8b0')}
 if(E==='s70'){R(tx,ty,bw,bh,cl);R(tx+1,ty+2,3,bh-3,mix(cl,'#5a3a1a',.55));R(tx+bw-4,ty+2,3,bh-3,mix(cl,'#5a3a1a',.55));R(tx,ty,3,2,'#fff');R(tx+bw-3,ty,3,2,'#fff');R(cx-lw-2,ly+lh-5,lw+2,5,pn);R(cx,ly+lh-5,lw+2,5,pn);R(cx-hw/2,hyy+Math.round(hh*.3),hw,1,'#e8604a')}
 if(E==='s80'){R(tx-1,ty,bw+2,3,clL);R(tx,ty+3,bw,bh-3,cl);R(tx,ty+bh-3,bw,1,'#ff5ad0');R(cx-hw/2+2,hyy-4,hw-4,3,hr);R(cx-hw/2+4,hyy-5,hw-8,1,hr);R(cx-hw/2-1,hyy+Math.round(hh*.28),hw+2,2,'#ff5ad0');R(cx-lw,ly+lh-6,lw*2,3,'#ff9ae0')}
 if(E==='s90'){R(tx-1,ty,bw+2,bh,cl);R(tx-1,ty+bh-3,bw+2,3,'#b04a4a');R(cx-lw-1,ly,lw*2+2,lh,mix(pn,'#6a8ab8',.5));R(cx-lw-1,ly+lh-3,lw*2+2,1,'#4a6a98');R(tx+bw,ty+bh-2,1,5,'#c0c0d0')}
 if(E==='y00'){R(tx,ty,bw,bh,cl);R(cx-2,ty+4,4,3,'#fff');R(cx-hw/2-2,hyy+Math.round(hh*.4),2,6,'#2a2a34');R(cx+hw/2,hyy+Math.round(hh*.4),2,6,'#2a2a34');R(cx-hw/2,hyy-1,hw,1,'#2a2a34')}
 if(E==='y10'){R(tx-1,ty,bw+2,bh,cl);R(cx-3,ty-1,6,2,clL);R(cx-3,ty+bh-4,6,2,clD);R(cx-hw/2-1,hyy-2,hw+2,6,'#c04a4a');R(cx-hw/2-1,hyy+3,hw+2,1,'#8a2a2a');R(cx-1,hyy-4,2,2,'#c04a4a')}
 if(E==='y20'){R(tx-1,ty,bw+2,bh,mix(cl,'#fff',.1));R(cx-hw/2-2,hyy+Math.round(hh*.35),2,7,'#2a2a34');R(cx-hw/2-2,hyy+Math.round(hh*.35)+6,5,1,'#2a2a34');R(cx-hw/2+2,hyy+Math.round(hh*.35)+7,2,2,'#7ae8ff');R(cx-hw/2,hyy-1,hw,1,'#2a2a34')}
 if(E==='ai'){R(tx,ty,bw,bh,'#2a2a44');R(tx,ty+3,bw,1,'#7ae8ff');R(cx-1,ty,2,bh,'#7ae8ff');R(cx-lw,ly,lw*2,lh,'#2a2a44');R(cx-lw,ly+lh-4,lw*2,1,'#ff7ad0');R(cx-hw/2+2,hyy+Math.round(hh*.42),hw-4,4,'rgba(122,232,255,.85)');R(cx-hw/2+3,hyy+Math.round(hh*.42),3,1,'#fff')}
 if(E==='fut'||E==='space'){R(tx,ty,bw,bh,'#dfe6f0');R(tx,ty+3,bw,1,'#7ae8ff');R(cx-1,ty,2,bh,'#7ae8ff');R(cx-3,ty-1,6,1,'#7ae8ff');R(cx-lw,ly,lw*2,lh,'#dfe6f0');R(cx-lw,ly+lh-3,lw*2,1,'#7ae8ff');R(cx+hw/2-2,hyy-6,1,5,'#9aa8b8');R(cx+hw/2-3,hyy-8,3,3,'#7ae8ff')}
 if(E==='s20'){R(tx,ty,bw,bh,'#3a3a4a');R(cx,ty+1,1,6,'#c04a4a');R(cx-lw,ly,lw*2,lh,'#2a2a34');R(cx-hw/2-3,hyy+2,hw+6,1,'#2a2a30');R(cx-hw/2+1,hyy-3,hw-2,5,'#2a2a30');R(cx-hw/2+1,hyy+1,hw-2,1,'#c04a4a')}
 if(E==='meiji'){R(tx,ty,bw,bh,cl);R(cx-lw-2,ly-3,lw*2+4,lh+3,'#2a2a44');R(cx-lw-2,ly-3,lw*2+4,1,'#6a6a84');R(cx-hw/2,hyy-2,hw,4,'#1a1a2a');R(cx-hw/2-1,hyy+2,hw+2,1,'#1a1a2a')}
 if(E==='post'){R(tx,ty,bw,bh,'#d8d0b8');R(tx+2,ty,1,bh,'#6a4a2a');R(tx+bw-3,ty,1,bh,'#6a4a2a');R(cx-lw,ly,lw*2,lh,'#5a5a4a');R(cx-hw/2-1,hyy-1,hw+2,4,'#6a6a5a');R(cx-hw/2-2,hyy+2,hw+4,1,'#4a4a3a')}
 if(E==='s60'){R(tx,ty,bw,bh,'#2a2a34');R(cx-1,ty,2,bh,'#f4f4f8');R(cx-lw,ly,lw*2,lh,'#2a2a34');R(cx-hw/2-1,hyy+Math.round(hh*.2),hw+2,Math.round(hh*.28),hr);R(cx-hw/2-1,hyy+Math.round(hh*.4),2,5,hr);R(cx+hw/2-1,hyy+Math.round(hh*.4),2,5,hrD)}
 if(E==='heian'){fl(cl);R(tx-2,ty+bh,bw+4,2,clD);R(tx+2,ty,bw-4,2,'#f4f0e0');R(cx-sw,ly+lh,sw*2,2,'#2a2a2a');R(cx-3,hyy-6,6,6,'#1a1a2a');R(cx-1,hyy-8,2,3,'#1a1a2a');R(cx+hw/2,hyy,1,12,'#1a1a2a')}
 if(E==='sengoku'){R(tx,ty,bw,bh,'#3a3a4a');R(tx+1,ty+1,bw-2,bh-4,'#6a6a7a');for(let k=0;k<bh-4;k+=3)R(tx+1,ty+1+k,bw-2,1,'#c04a4a');R(cx-lw,ly,lw*2,lh,'#4a3a3a');R(cx-hw/2-1,hyy-3,hw+2,5,'#3a3a44');R(cx-1,hyy-6,2,4,'#e8c860');R(cx-hw/2,hyy+2,hw,1,'#c04a4a');R(tx-aw,ty+1,aw,ah,'#5a5a6a')}
 if(E==='med'){R(tx,ty,bw,bh,cl);R(tx,ty+bh-3,bw,1,'#6a4a2a');R(cx-1,ty+bh-3,2,1,'#e8c860');R(cx-lw,ly,lw*2,lh,'#5a4a3a');R(cx-lw,ly+lh-5,lw*2,5,'#3a2a1a');R(cx-3,ty-1,6,2,clL)}
 if(E==='baroque'){R(cx-hw/2-2,hyy-3,hw+4,Math.round(hh*.6),'#f0f0f4');R(cx-hw/2-3,hyy+Math.round(hh*.4),3,Math.round(hh*.4),'#f0f0f4');R(cx+hw/2,hyy+Math.round(hh*.4),3,Math.round(hh*.4),'#e4e4ec');R(tx,ty,bw,bh,cl);R(cx-3,ty,6,4,'#fff');R(cx-lw,ly,lw*2,lh,'#f0e8e0');R(cx-sw,ly+lh,sw*2,2,'#2a2a2a');R(cx-sw,ly+lh-1,sw*2,1,'#e8c860')}
 if(E==='greek'){R(tx,ty,bw,bh+3,'#f4f0e8');R(tx,ty+3,bw,1,'#d8d0c0');R(tx+bw-3,ty,3,bh+3,'#e0d8c8');R(cx-lw,ly+3,lw*2,lh-3,sk);R(cx-sw,ly+lh,sw*2,2,'#a87a4a');R(cx-hw/2,hyy+1,hw,1,'#58a858');for(let k=0;k<hw;k+=3)R(cx-hw/2+k,hyy,1,1,'#58a858')}
 if(E==='isekai'){R(tx-1,ty,bw+2,bh+lh-3,'#4a2a7a');R(tx,ty,bw,bh,cl);R(cx-2,ty,4,2,'#e8c860');R(cx-hw/2-1,hyy-5,hw+2,2,'#4a2a7a');R(cx-hw/2+3,hyy-9,hw-6,4,'#4a2a7a');R(cx-1,hyy-11,2,3,'#4a2a7a');R(cx-1,hyy-7,2,2,'#ffe27a')}
 if(E==='cosmic'){R(tx-1,ty,bw+2,bh+lh,'#2a1a5a');for(let k=0;k<12;k++)R(tx+((k*7)%bw),ty+((k*5)%(bh+lh-2)),1,1,'#fff6c8');R(cx-hw/2-1,hyy-5,hw+2,1,'#ffe27a');R(cx-hw/2,hyy-6,hw,1,'rgba(255,226,122,.6)');R(tx,ty,bw,2,'#7a5ad0')}
 if(E==='classic'){R(tx,ty,bw,bh,'#2a2a5a');R(cx-2,ty,4,bh-2,'#f4f4f8');R(cx-1,ty,2,3,'#c04a4a');R(cx-lw,ly,lw*2,lh,'#f0e8d8');R(tx,ly-2,bw,5,'#2a2a5a');R(cx-sw,ly+lh-3,sw*2,3,'#2a2a2a');R(cx+hw/2-1,hyy+2,2,10,hr)}
 if(o.prop==='guitar'){const q=V.hi?2:1;R(cx-5*q,ty+bh-5*q,8*q,6*q,'#b8683a');R(cx-5*q,ty+bh-5*q,8*q,q,'#e89a68');R(cx-3*q,ty+bh-3*q,3*q,3*q,'#3a2418');R(cx+2*q,ty+bh-4*q,10*q,q,'#6a4a2a');R(cx+12*q,ty+bh-5*q,2*q,3*q,'#3a2418')}
 if(o.prop==='drum'){R(cx-6,ty+bh-4,12,6,'#a86a30');R(cx-6,ty+bh-4,12,2,'#d8a060');R(cx-5,ty+bh-1,10,1,'#6a3c18')}
 if(o.prop==='bone'){R(cx+5,ty+bh-5,8,2,'#efe6d0');R(cx+4,ty+bh-6,2,4,'#efe6d0');R(cx+12,ty+bh-6,2,4,'#efe6d0')}
 if(o.prop==='lute'){R(cx-5,ty+bh-5,8,6,'#a86a30');R(cx-3,ty+bh-3,3,3,'#2a1408');R(cx+2,ty+bh-4,10,1,'#6a4a2a');R(cx+12,ty+bh-6,3,3,'#6a3a14')}
 if(o.prop==='sham'){R(cx-4,ty+bh-4,8,7,'#e8d8b8');R(cx-3,ty+bh-3,6,5,'#f0e8d0');R(cx+4,ty+bh-5,9,1,'#6a4a2a');R(cx+12,ty+bh-7,2,4,'#3a2418')}
 if(o.prop==='harp'){R(cx-6,ty+bh-8,2,12,'#a86a30');R(cx-6,ty+bh-8,8,2,'#a86a30');for(let k=0;k<5;k++)R(cx-4+k*1,ty+bh-6,1,9,'#e8e0c0')}
 if(o.prop==='dj'){R(cx-14,ty+bh-3,28,7,'#3a3a4a');R(cx-14,ty+bh-3,28,1,'#7a7a8e');R(cx-11,ty+bh-1,9,5,'#0e0e16');R(cx+3,ty+bh-1,9,5,'#0e0e16');R(cx-7+(fr%3),ty+bh+1,1,1,'#ff7ab0');R(cx+7-(fr%3),ty+bh+1,1,1,'#7ae0ff')}
 if(o.prop==='pc'){R(cx+4,ty+bh-8,14,10,'#d0d8e4');R(cx+5,ty+bh-7,12,7,fr%2?'#7ae0ff':'#3fa7d6');R(cx+5,ty+bh-7,12,1,'#c8f4ff');R(cx+2,ty+bh+2,18,2,'#98a2b2');for(let q=0;q<5;q++)R(cx+6+q*2,ty+bh-5+((q+fr)%3),1,2,'#fff')}
 // outline
 let P=B.slice();
 if(V.outline!=='none'){for(let y=0;y<H;y++)for(let x=0;x<W;x++){if(B[y*W+x])continue;let nb=null;for(const[dx,dy]of[[1,0],[-1,0],[0,1],[0,-1]]){const xx=x+dx,yy=y+dy;if(xx>=0&&yy>=0&&xx<W&&yy<H&&B[yy*W+xx])nb=B[yy*W+xx]}if(nb)P[y*W+x]=V.outline==='soft'?mix(nb,'#4a3a70',.5):(V.outline==='tint'?mix(nb,'#10081e',.6):'#1a1226')}}
 return{P,W,H}
}

  const LV = { hw: 16, hh: 14, bw: 10, bh: 13, lh: 11, eye: 'big', outline: 'tint', shade: 2, blush: 1, cap: .44, sfc: 1, round: 3, slim: 1, aw: 2 };
  const EK = { '-2': 'prim', '-3': 'edo', '-1': 's70', 0: 's80', 1: 's90', 2: 'y00', 3: 'y10', 4: 'y20', 5: 'ai', 6: 'fut', 11: 's20', 12: 'meiji', 13: 'post', 14: 's60', 15: 'heian', 16: 'sengoku', 17: 'med', 18: 'baroque', 19: 'greek', 20: 'isekai', 21: 'paleo', 22: 'cosmic', 23: 'classic' };
  const cache = new Map();
  function look(o, fr) {
    const ek = EK[o.era]; let pr = o.prop, pose = o.pose || 'idle';
    if (pr === 'gtr') pr = ({ '-3': 'sham', 15: 'lute', 17: 'lute', 18: 'harp', 19: 'harp', 23: 'harp' })[o.era] || 'guitar';
    if (pr === 'bone') pr = 'bone';
    if (pr === 'mic') { if (pose === 'idle' || pose === 'cheer') pose = 'sing'; pr = null; }
    const sty = o.style === 'spiky' ? 'spike' : (o.style || 'short');
    return { key: [o.skin[0], o.hair[0], o.cloth[0], o.pants, sty, ek, pr, pose, (pose === 'sing' || pose === 'cheer') ? (fr & 1) : 0, (fr % 9 === 4 && pose !== 'slump') ? 1 : 0, (pr === 'dj' || pr === 'pc') ? (fr & 3) : 0].join('|'), o2: { skin: o.skin[0], hair: o.hair[0], cloth: o.cloth[0], pants: o.pants, style: sty, era: ek, prop: pr, blink: (fr % 9 === 4 && pose !== 'slump') ? 1 : 0 }, pose };
  }
  function sprite(o, fr) {
    const L = look(o, fr); let c = cache.get(L.key);
    if (!c) {
      const S = gen(LV, L.o2, L.pose, fr); c = document.createElement('canvas'); c.width = S.W; c.height = S.H; const g = c.getContext('2d');
      for (let y = 0; y < S.H; y++) for (let x = 0; x < S.W; x++) { const k = S.P[y * S.W + x]; if (k) { g.fillStyle = k; g.fillRect(x, y, 1, 1); } }
      if (cache.size > 600) cache.clear(); cache.set(L.key, c);
    }
    return c;
  }
  return { sprite, W: 28, H: 46 };
})();
function drawChar(g, x, y, o) {
  const fr = o.fr | 0; const c = CH.sprite(o, fr); let sc = 1; try { sc = g.getTransform().a || 1; } catch (_) {}
  g.save(); g.imageSmoothingEnabled = false;
  if (sc >= 1.5) { g.scale(1 / sc, 1 / sc); g.drawImage(c, Math.round((x + 8) * sc - c.width / 2), Math.round(y * sc + 24 * sc - (c.height - 4))); }
  else if (g.canvas && g.canvas.height <= 30) { g.drawImage(c, Math.round(x + 8 - c.width / 2 - 6), Math.round(y)); }
  else { g.drawImage(c, Math.round(x + 8 - c.width / 2), Math.round((g.canvas ? g.canvas.height : 46) - c.height + y)); }
  g.restore();
}
