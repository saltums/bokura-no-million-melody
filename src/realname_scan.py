# -*- coding: utf-8 -*-
"""実名・人数語の横断スキャン(読むだけ。何も書き換えない)。
  python3 realname_scan.py            全部
  python3 realname_scan.py names      メンバー名・アーティスト名だけ
対象: arcs_new の nm/alt/members/本文、rosters(realfix 適用後)、PT 曲名、namebank.json
ブラックリスト: ongaku_storyline_gen.PUNS_RAW の元ネタ名, gender.SRC_G, rosters/realnames.txt(1行1名。手で足す)
"""
import sys, re, json, ast, unicodedata
sys.path.insert(0, '/home/claude')
import arcs2_gen as G, roster, gender
import ongaku_storyline_gen as OSG

ONLY = sys.argv[1] if len(sys.argv) > 1 else ''


def norm(s):
    return re.sub(r"[\s・\.\-'’=＝]", '', unicodedata.normalize('NFKC', s).lower())


def lev(a, b, cap=2):
    if abs(len(a) - len(b)) > cap: return cap + 1
    p = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        c = [i]
        for j, cb in enumerate(b, 1): c.append(min(p[j] + 1, c[j - 1] + 1, p[j - 1] + (ca != cb)))
        p = c
    return p[-1]


# --- ブラックリスト
ART = {t[1] for t in OSG.PUNS_RAW} | set(gender.SRC_G)
ART = {x for x in ART if len(norm(x)) >= (4 if re.fullmatch(r'[\x20-\x7e]+', x) else 3)}
PERSON, SECN = [], {}  # SECN: {arcs の k: [元ネタの実在メンバー]}([キー] の下)
try:
    _cur = None
    for l in open('/home/claude/rosters/realnames.txt', encoding='utf-8'):
        l = l.strip()
        if not l or l.startswith('#'): continue
        if l.startswith('[') and l.endswith(']'): _cur = SECN.setdefault(l[1:-1], []); continue
        (PERSON if _cur is None else _cur).append(l)
except OSError:
    pass
PN = [(p, norm(p)) for p in PERSON]


def _parts(n):
    n = unicodedata.normalize('NFKC', n).strip()
    p = [x for x in re.split(r"[\s・=＝·]+", n) if x]
    return [x.lower() for x in p]


def _kanji(s): return bool(s) and all('一' <= c <= '鿿' or c in '々' for c in s)


def _cpart(a, b):
    """名前の一語どうしが近い(同じ・一字程度の違い・並べ替え)"""
    return a == b or lev(a, b, 9) <= max(1, len(b) // 2) or (len(a) > 1 and sorted(a) == sorted(b))


def near_real(fake, real):
    """メンバー名が元ネタの実名に近すぎるか。どちらか一語を丸ごと置き換えていれば可(藤原基央→藤川基夫は不可)"""
    a, b = _parts(fake), _parts(real)
    fa, fb = norm(fake), norm(real)
    if fa == fb: return True
    if len(a) == len(b) and len(a) >= 2:
        if all(_cpart(x, y) for x, y in zip(a, b)): return True
        eq = [x == y for x, y in zip(a, b)]
        if any(eq) and all(e or (len(x) == len(y) and _kanji(x) and _kanji(y)) for e, x, y in zip(eq, a, b)): return True  # 片方同じ+同じ字数の漢字(同音の当て字のおそれ)
        return False
    if len(a) == 1 and len(b) == 1:
        return len(fb) >= 2 and (lev(fa, fb, 9) <= max(1, len(fb) // 3) or (len(fa) > 1 and sorted(fa) == sorted(fb)))
    return len(fb) >= 4 and lev(fa, fb, 9) <= max(1, len(fb) // 4)


# ---- 実在の曲名(rosters/realtitles.txt。照合の本体は realtitles.py)
import realtitles as RTM
tnorm = RTM.tnorm


def title_hits(t, key=None, pool='wide'):
    return RTM.hit(t, key, pool)
_ART_RX = [(a, re.compile((r'(?<![A-Za-z])' + re.escape(a) + r'(?![A-Za-z])') if re.fullmatch(r'[\x20-\x7e]+', a) else re.escape(a))) for a in ART]


def text_hits(s):
    out = [a for a, rx in _ART_RX if rx.search(s)]
    out += [p for p in PERSON if p in s]
    return out


def name_hits(n):
    """メンバー名: 実名と一致 or 1字違い(4字以上)"""
    x = norm(n); out = []
    for p, q in PN:
        if x == q or (len(q) >= 4 and lev(x, q, 1) <= 1): out.append(p)
    return out


arcs, PT = G.load_specs()
hits = []


def L(v):
    if isinstance(v, str):
        try: return ast.literal_eval(v)
        except Exception: return [v]
    return v


def flat(v):
    if isinstance(v, (list, tuple)):
        for y in v: yield from flat(y)
    elif isinstance(v, str): yield v


# --- 1) メンバー名
import arcs_gen as G1
for a in list(G1.ARCS) + arcs:
    k = a['k']; R = roster.ROSTER.get(k) or L(a.get('members')) or []
    fx = roster.REALFIX.get(k) or {}
    for x in R:
        n = fx.get(x['n'], x['n'])
        for p in name_hits(n): hits.append(('member', k, n, p))
        for p in SECN.get(k, []):
            if near_real(n, p) and p not in name_hits(n): hits.append(('member~', k, n, p))
    for nm in [a['nm']] + list(L(a.get('alt')) or []):
        for p in [x for x in ART if norm(x) == norm(nm)] + [x for x in PERSON if x in nm] + name_hits(nm):
            hits.append(('artist', k, nm, p))

# --- 2) 本文・曲名
if ONLY != 'names':
    for a in arcs:
        k = a['k']
        for f in ('tx', 'sa', 'ev', 'ex', 'd', 'eh', 'ea', 'tr'):
            for s in flat(L(a.get(f))):
                for p in text_hits(s): hits.append(('text:' + f, k, s[:40], p))
        for t in PT.get(k, []):
            for p in text_hits(t): hits.append(('title', k, t, p))
    nb = json.load(open('/home/claude/namebank.json', encoding='utf-8'))
    for st, d in nb['a'].items():
        for e, v in d.items():
            for n in v:
                for p in [a for a, rx in _ART_RX if norm(a) == norm(n)] + name_hits(n): hits.append(('nb.a', st, n, p))
    for e in nb['ev']:
        for p in text_hits(e['t']): hits.append(('nb.ev', e.get('f', ''), e['t'][:40], p))
        if re.match(r'^[a-z]{1,3}:', e['t']): hits.append(('nb.ev-label', e.get('f', ''), e['t'][:40], 'a:'))

# --- 2b) 実在の曲名そのまま(rosters/realtitles.txt と照合。末尾の(…)を外しても同じなら実曲名扱い)
if ONLY in ('', 'titles'):
    import parody_titles, ptover, tracks
    for k, v in PT.items():
        for t in v:
            if title_hits(t, k): hits.append(('rtitle:PT', k, t, tnorm(t)))
    _QT = re.compile(r'[『「]([^』」]{2,40})[』」]')
    for a in arcs:
        for f in ('tx', 'sa', 'ev', 'ex', 'd', 'eh', 'ea'):
            for s in flat(L(a.get(f))):
                for q in _QT.findall(s):
                    if title_hits(q, a.get('par') or a['k']): hits.append(('rtitle:text', a['k'], q, s[:30]))
    for k, v in parody_titles.PT.items():
        for t in v:
            if title_hits(t, None, 'parody'): hits.append(('rtitle:parody_titles', k, t, tnorm(t)))
    for k, v in ptover.PTO.items():
        if k not in {x['k'] for x in G1.ARCS}: continue  # 使われるのは arcs_gen の 20 組だけ
        for t in v:
            if title_hits(t, None, 'parody'): hits.append(('rtitle:ptfix', k, t, tnorm(t)))
    for t, _e in tracks.PARODY:
        if title_hits(t, None, 'parody'): hits.append(('rtitle:tracks.PARODY', '', t, tnorm(t)))
    for th, v in tracks.TT.items():
        for t in v:
            if title_hits(t): hits.append(('rtitle:tracks.TT', th, t, tnorm(t)))
    for t in tracks.GENERIC:
        if title_hits(t): hits.append(('rtitle:tracks.GENERIC', '', t, tnorm(t)))
    nb = json.load(open('/home/claude/namebank.json', encoding='utf-8'))
    for t in nb.get('pt', []):
        if title_hits(t, None, 'parody'): hits.append(('rtitle:nb.pt', '', t, tnorm(t)))
    for e, v in nb.get('t', {}).items():
        for t in v:
            if title_hits(t): hits.append(('rtitle:nb.t', e, t, tnorm(t)))
    for th, v in nb.get('tt', {}).items():
        for x in v:
            if title_hits(x[0]): hits.append(('rtitle:nb.tt', th, x[0], tnorm(x[0])))

# --- 3) 人数語(arcs 本文 vs 人数)
CNT = {'二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8}
cnt_bad = []
if ONLY != 'names':
    for a in arcs:
        k = a['k']; R = roster.ROSTER.get(k) or L(a.get('members')) or L(a.get('roles')) or []
        n = len(R)
        if a.get('st') == 'solo' or n == 0: continue
        for f in ('ev', 'ex', 'eh', 'ea', 'd', 'tx'):
            for s in flat(L(a.get(f))):
                for m in re.finditer(r'(あの|残りの|他の)?([二三四五六七八])人(?=[でははがとものだ組全揃]|$)', s):
                    c = CNT[m.group(2)] + (1 if m.group(1) in ('残りの', '他の') else 0)
                    if c != n and not re.search(r'客|観客|子|姉妹|兄弟|娘|息子|孫', s[max(0, m.start() - 6):m.end()]):
                        cnt_bad.append((k, n, f, s[:50]))

for h in hits: print('\t'.join(map(str, h)))
for c in cnt_bad: print('count\t%s\tmembers=%d\t%s\t%s' % c)
print('# hits', len(hits), 'count-mismatch', len(cnt_bad), file=sys.stderr)
