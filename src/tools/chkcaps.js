const fs=require('fs');const MOD=/CD|ライブハウス|テレビ|アリーナ|ドーム|駅前|ステージ|ライブ|スタジオ|放送|ネット|スマホ|ツアー|マイク/;
for(const f of fs.readdirSync('/home/claude/eras').filter(x=>/^scene_.*\.js$/.test(x))){
 const SCENES={};const P_=()=>{};const g=null;
 try{ new Function('SCENES','vgrad','glow','P_','PO','OL','CLOTHS',fs.readFileSync('/home/claude/eras/'+f,'utf8'))(SCENES,()=>{},()=>{},()=>{},()=>{},'#000',[]);}catch(e){console.log(f,'ERR',e.message);continue}
 const S=Object.values(SCENES)[0]; const c=S.caps; let bad=[];
 if(!c){console.log(f,'NO CAPS');continue}
 for(const m of [0,1,2]){ if(!c[m]||c[m].length!==5) bad.push('mood'+m+' len '+(c[m]&&c[m].length)); else c[m].forEach((t,i)=>{ if(t.length>25) bad.push(m+','+i+' long '+t.length); if(MOD.test(t)) bad.push(m+','+i+' modern '+t); }); }
 console.log(f,bad.length?bad:'ok');
}
