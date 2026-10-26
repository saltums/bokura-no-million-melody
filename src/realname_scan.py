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
try:
    PERSON = [l.strip() for l in open('/home/claude/rosters/realnames.txt', encoding='utf-8') if l.strip() and not l.startswith('#')]
except OSError:
    PERSON = []
PN = [(p, norm(p)) for p in PERSON]
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
for a in arcs:
    k = a['k']; R = roster.ROSTER.get(k) or L(a.get('members')) or []
    fx = roster.REALFIX.get(k) or {}
    for x in R:
        n = fx.get(x['n'], x['n'])
        for p in name_hits(n): hits.append(('member', k, n, p))
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
