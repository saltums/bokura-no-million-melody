# -*- coding: utf-8 -*-
"""もじり名メンバー名簿を適用する。rosters/out*.json と、各 arcs の members フィールド。"""
import glob, json, copy, re
import tracks
ROSTER = {}
for _f in sorted(glob.glob('/home/claude/rosters/out*.json')):
    try:
        ROSTER.update(json.load(open(_f)))
    except Exception as _e:
        print('ROSTER SKIP', _f, _e)
# 実名・実名とほぼ同じ(同音・一字違い)のメンバー名の差し替え {k: {旧: 新}}。検査は realname_scan.py
try:
    REALFIX = json.load(open('/home/claude/rosters/realfix.json'))
except Exception as _e:
    REALFIX = {}; print('REALFIX SKIP', _e)
# 元ネタの結成時メンバーと後年のメンバー交代 {k: {start, mc}}(lineup / lineup_tree)
try:
    LINEUP = {k: v for k, v in json.load(open('/home/claude/rosters/lineup.json')).items() if not k.startswith('_')}
except Exception as _e:
    LINEUP = {}; print('LINEUP SKIP', _e)

_INST = re.compile(r'ギター|ベース|ドラム|キーボード|鍵盤|ピアノ|スティック|弦|ピック|サックス|ラッパ|歌|声|マイク|ターンテーブル|リリック|ラップ|ビート|譜面')


def apply(a, mm, seed):
    R = ROSTER.get(a.get('k')) or a.get('members')
    if not R:
        return dedupe(mm, seed)
    fx = REALFIX.get(a.get('k')) or {}
    out = []
    # 名簿の並びが roles と違うことがあるので、癖(t)などは同じ担当の元メンバーから引き継ぐ
    used = set(); rest = [x.get('r') for x in R]
    for j, x in enumerate(R):
        r = x.get('r'); rest = rest[1:]
        i = next((i for i, m in enumerate(mm) if i not in used and r and m.get('r') == r), None)
        if i is None:  # 同じ担当がいなければ、後ろの名簿で使われない担当の元メンバー
            i = next((i for i, m in enumerate(mm) if i not in used and m.get('r') not in rest), None)
        if i is not None:
            used.add(i); b = dict(mm[i])
            if b.get('r') != r and _INST.search(b.get('t') or ''): b['t'] = ''  # 他の楽器の話をする癖は外す
        else:
            b = dict(tracks.newcomer(seed, r or 'Gt', {m['n'] for m in mm}))
        b['n'] = fx.get(x['n'], x['n']); b['r'] = r or b.get('r', ''); b['g'] = x.get('g') or b.get('g', 'm')
        b['k'] = tracks.nick_fit(b.get('k'), b['g'])  # 名簿で性別が替わったら愛称も合わせる(女性に「おやっさん」を付けない)
        out.append(b)
    return dedupe(out, seed, keep={b['n'] for b in out})  # 名簿の名前(別担当)は変えない。癖の重なりだけ直す


def _given(n):
    n = str(n or '').replace('　', ' ')
    return n.rsplit(' ', 1)[1] if ' ' in n and n.split(' ', 1)[0] in tracks.FAM else None


def dedupe(mm, seed, keep=(), pool=None):
    """一座・バンドの中で、同じ下の名前(「レン」が三人)・同じ癖(特徴文)が重ならないようにする。
    生成した名前(姓+カタカナの下の名前)だけ下の名前を差し替える(keep の名前・名簿の名前は変えない)。
    癖は2人目以降を pool(既定は tracks.TRAIT)の未使用のものに。重なりが無ければ元のまま返す"""
    if not mm or len(mm) < 2: return mm
    import random as _rd, hashlib as _hl
    r = _rd.Random(int(_hl.md5(('dedupe|' + str(seed)).encode()).hexdigest()[:8], 16))
    out = [dict(m) for m in mm]
    gv = [_given(m.get('n')) for m in out]
    seen = set()
    for i, m in enumerate(out):
        g0 = gv[i]
        if not g0: continue
        if g0 in seen and m.get('n') not in keep:
            src = tracks.GIV_F if m.get('g') == 'f' else tracks.GIV_M
            c = [x for x in src if x not in seen and x not in gv]
            if c:
                nw = r.choice(c); fam = m['n'].replace('　', ' ').split(' ', 1)[0]
                if fam + ' ' + nw not in {x.get('n') for x in out}: m['n'] = fam + ' ' + nw; g0 = nw
        seen.add(g0)
    tp = list(pool or tracks.TRAIT); ts = set()
    allt = {m.get('t') for m in out}
    for m in out:
        t = m.get('t')
        if not t: continue
        if t in ts:
            c = [x for x in tp if x not in ts and x not in allt]
            m['t'] = r.choice(c) if c else ''
            t = m['t']
        if t: ts.add(t)
    return out


# ---- ソロ扱い(solo/beat/rap/dj)の人に付いた名簿: 本人をメンバー一覧から外し、残りはサポートにする ----
_SUP = {'Gt': 'サポートギター', 'Ba': 'サポートベース', 'Dr': 'サポートドラム', 'Key': 'サポート鍵盤', 'Pf': 'サポートピアノ', 'Syn': 'サポートシンセ', 'Per': 'サポートパーカッション',
        'Sax': 'サポートサックス', 'Tp': 'サポートトランペット', 'Tb': 'サポートトロンボーン', 'Vn': 'サポートバイオリン', 'Vo': 'ゲストボーカル', 'Cho': 'サポートコーラス', 'DJ': 'サポートDJ',
        'MC': 'ゲストMC', 'Track': 'トラック担当', 'Prog': 'トラック担当', 'Illust': 'イラスト担当'}


def is_group(st, mm):
    """グループとして扱うか。band/duo/inst と、MC・DJが二人以上いるラップ(ヒップホップグループ)"""
    if st in ('band', 'duo', 'inst'): return True
    return st in ('rap', 'dj') and sum(1 for m in mm or [] if not str(m.get('r', '')).startswith(('サポート', 'マネージャー', '録音'))) >= 2


def self_idx(st, mm):
    """ソロ扱いの名簿で、本人(主人公)にあたる人の位置"""
    rs = [str(m.get('r', '')) for m in mm]
    pri = {'beat': (r'Prog|Track', r'^Vo'), 'rap': (r'^MC', r'^Vo'), 'dj': (r'^DJ',)}.get(st, (r'^Vo', r'^MC'))
    for p in pri:
        i = next((i for i, r in enumerate(rs) if re.search(p, r)), None)
        if i is not None: return i
    return 0


def solo_side(a, st, mm, seed):
    """ソロ扱いなのに名簿(roles/members)がある人: 本人は一覧に出さない(主人公と同じ人が別人・別の出身で並ばないように)。
    残りの人の担当はサポート表記に。誰も残らなければ通常のソロの周りの人(サポート・マネージャー・録音担当)"""
    if not (a.get('roles') or ROSTER.get(a.get('k')) or a.get('members')) or not mm: return mm
    i = self_idx(st, mm)
    rest = [dict(m) for j, m in enumerate(mm) if j != i]
    for m in rest:
        r0 = str(m.get('r', '')); base = re.split(r'[/・]', r0)[0]
        m['r'] = _SUP.get(base, r0 if r0.startswith('サポート') else 'サポート' + r0)
    return rest or tracks.people(seed, 'solo')


_TR_HEAD = re.compile(r'^(ドラム|ベース|ギター|キーボード|鍵盤|サックス|トランペット)が、?')
_TR_SND = re.compile(r'(泣く|鳴る|歪む|唸る|光る|うねる|響く|揺らす|歌う|跳ねすぎ|走る|踊る|彩る|切り込む|地を這う|鳴らす|食う|動く|揺れる)$')


def trait(t):
    """メンバーの癖(その人の名前の下に出る)。「ドラムが叩きながら喋る」のように担当名が主語の文は、担当名を外す(楽器の音の話はそのまま)"""
    if not isinstance(t, str) or _TR_SND.search(t): return t
    return _TR_HEAD.sub('', t, count=1) or t


def lineup(a, mm):
    """名簿(後年の顔ぶれ)を元ネタの結成時メンバーに組み替える(mm をその場で書き換え。出身地などはその席の人を引き継ぐ)。
    返り値: 後年の交代 [(年, 'out'|'in', メンバー, 文 or None)](rosters/lineup.json の mc の順)"""
    L = LINEUP.get(a.get('k'))
    if not L or not mm: return []
    fx = REALFIX.get(a.get('k')) or {}
    held = {}
    for raw, fm in (L.get('start') or {}).items():
        fn = fx.get(raw, raw); j = next((i for i, m in enumerate(mm) if m and m.get('n') == fn), None)
        if j is None: continue
        held[raw] = mm[j]
        mm[j] = dict(mm[j], n=fx.get(fm['n'], fm['n']), r=fm.get('r', mm[j].get('r', '')), g=fm.get('g', mm[j].get('g', 'm'))) if fm else None
        if mm[j]: mm[j]['k'] = tracks.nick_fit(mm[j].get('k'), mm[j].get('g'))
    mm[:] = [m for m in mm if m]
    cur = {m['n']: m for m in mm}; out = []
    for c in L.get('mc') or []:
        o = cur.pop(fx.get(c['out'], c['out']), None) if c.get('out') else None  # 名簿の元の名前で書いてあるので realfix を当てて探す
        if o: out.append((c['y'], 'out', o, c.get('tx_out')))
        i_ = c.get('in')
        nw = held.get(i_) if isinstance(i_, str) else (dict(o or {}, n=fx.get(i_['n'], i_['n']), r=i_.get('r', (o or {}).get('r', '')), g=i_.get('g', 'm')) if i_ else None)
        if nw: nw['k'] = tracks.nick_fit(nw.get('k'), nw.get('g')); cur[nw['n']] = nw; out.append((c['y'], 'in', nw, c.get('tx_in')))
    return out


_RW = {'Vo': 'ボーカル', 'Gt': 'ギター', 'Ba': 'ベース', 'Dr': 'ドラム', 'Key': 'キーボード', 'Pf': 'ピアノ', 'Sax': 'サックス'}


def lineup_tree(tree, mm, ch):
    """人生の木に、後年の交代を「転機」として差し込む(その年以降の最初の作品の前)。各結末の mm はその道の最後の顔ぶれに"""
    ch = sorted(ch, key=lambda c: c[0])

    def ev(c):
        y, kd, m, tx = c; w = _RW.get(re.split(r'[/・]', str(m.get('r') or ''))[0], 'メンバー')
        return {'t': 'e', 'tx': tx or (('%s担当のメンバーが、バンドを離れた。' if kd == 'out' else '新しい%s担当が加わり、顔ぶれが変わった。') % w), 'mb': {kd: m}}

    def walk(n, cur, i):
        s = []
        for it in n.get('s', []):
            while i < len(ch) and it.get('t') == 'r' and it.get('y', 0) >= ch[i][0]:
                c = ch[i]; s.append(ev(c)); cur = [x for x in cur if x['n'] != c[2]['n']] + ([c[2]] if c[1] == 'in' else []); i += 1
            s.append(it)
        n['s'] = s
        if 'e' in n: n['e']['mm'] = cur
        for k in n.get('n', []): walk(k, list(cur), i)
    walk(tree, list(mm), 0)
    return tree
