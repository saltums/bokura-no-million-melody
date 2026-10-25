import sys,glob,os,importlib,json
sys.path.insert(0,'/home/claude'); sys.path.insert(0,'/home/claude/eras'); import rare_gen
JP=['神社','着物','畳','侍','お寺','寺','鳥居','提灯','縁側','三味線','琵琶','尺八','太鼓','盆踊り','長屋','旅籠','藩','殿様','城下','障子','襖','お茶','茶会','長屋','下駄','草履','屋敷','御簾','几帳']
WEST=['リュート','チェンバロ','オルガン','教会','修道院','ワイン','葡萄','神殿','劇場','ヴァイオリン','アーメン','貴族','伯爵','騎士','ドラゴン','竜','魔法']
E={11:'jp',12:'jp',13:'jp',14:'jp',15:'jp',16:'jp',17:'west',18:'west',19:'west',20:'any',21:'any',22:'any'}
for f in sorted(glob.glob('/home/claude/eras/era_*.py')):
    m=importlib.import_module(os.path.basename(f)[:-3]); P=dict(m.P); P['title']=m.title; P['lyr']=m.lyr
    T=json.dumps(m.P,ensure_ascii=False,default=str)+''.join(json.dumps(rare_gen.tree(P,7000+k,group=k%2==0),ensure_ascii=False) for k in range(12))
    e=m.P['era']; kind=E[e]
    if kind=='west': h={w:T.count(w) for w in JP if w in T}
    elif kind=='jp' and e in (15,16): h={w:T.count(w) for w in WEST if w in T}
    elif e in (11,12,13,14): h={w:T.count(w) for w in ['ドラゴン','竜','魔法','騎士','伯爵','神殿','修道院'] if w in T}
    else: h={}
    if e in (21,22): h={w:T.count(w) for w in JP+WEST if w in T and w not in ('劇場',)}
    print(m.P['es'],e,h)
