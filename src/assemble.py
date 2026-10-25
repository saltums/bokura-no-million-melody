import json,re,os
s=open('/home/claude/proto_template.html',encoding='utf-8').read()
esc=lambda p: open(p,encoding='utf-8').read().replace('</','<\\/')
import glob
sc='const SCENES = {};\n'+'\n'.join(open(f,encoding='utf-8').read() for f in sorted(glob.glob('/home/claude/eras/scene_*.js')))
s=s.replace('/*__ERA_SCENES__*/',sc)
h=s.replace('__DATA__',esc('/home/claude/proto_data.json')).replace('__BANK__',esc('/home/claude/namebank.json'))
open('/home/claude/proto_music5.html','w',encoding='utf-8').write(h)
m=re.findall(r'<script>(.*?)</script>',h,re.S)
open('/tmp/chk.js','w').write('new Function('+json.dumps(m[-1])+');console.log("syntax ok")')
print(os.path.getsize('/home/claude/proto_music5.html')/1e6,'MB')
