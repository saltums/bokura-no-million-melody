import json,re,os,glob,hashlib,shutil
s=open('/home/claude/proto_template.html',encoding='utf-8').read()
sc='const SCENES = {};\n'+'\n'.join(open(f,encoding='utf-8').read() for f in sorted(glob.glob('/home/claude/eras/scene_*.js')))
s=s.replace('/*__ERA_SCENES__*/',sc)
# DATA / BANK はページに埋め込まず、別ファイル(data.json / bank.json)で後読みする。DV はキャッシュよけの版番号
SRC={'data.json':'/home/claude/proto_data.json','bank.json':'/home/claude/namebank.json'}
hs=hashlib.md5()
for k,p in SRC.items():
    json.load(open(p,encoding='utf-8'))  # 壊れたJSONを出さない
    shutil.copyfile(p,'/home/claude/'+k); hs.update(open(p,'rb').read())
h=s.replace('__DV__',hs.hexdigest()[:10])
open('/home/claude/proto_music5.html','w',encoding='utf-8').write(h)
m=re.findall(r'<script>(.*?)</script>',h,re.S)
open('/tmp/chk.js','w').write('new Function('+json.dumps(m[-1])+');console.log("syntax ok")')
print(os.path.getsize('/home/claude/proto_music5.html')/1e6,'MB')
