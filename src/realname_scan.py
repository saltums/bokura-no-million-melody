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


# 読み(ひらがな)。pykakasi/jaconv は /home/claude/_pylib(無ければ漢字の読みなしで比べる)
sys.path.insert(0, '/home/claude/_pylib')
try:
    import pykakasi as _pk, jaconv as _jc
    _KK = _pk.kakasi()
except Exception:
    _KK = _jc = None
_SMALL = str.maketrans('ぁぃぅぇぉっゃゅょゎ', 'あいうえおつやゆよわ')


def rd(s):
    s = re.sub(r"[\s・\.\-'’=＝_*()()0-9]", '', unicodedata.normalize('NFKC', s).lower())
    if _jc and re.fullmatch(r'[a-z]+', s or '-'): s = _jc.alphabet2kana(s)
    h = ''.join(x['hira'] for x in _KK.convert(s)) if _KK else s
    h = ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in h).translate(_SMALL)
    h = re.sub(r'([おこそとのほもよろごぞどぼぽ])[うお]', r'\1', re.sub(r'[ーぅ]', '', h))
    return re.sub(r'[^ぁ-ゔ]', '', h)  # ゔ(ヴ)も読みに残す


def _nd(h): return ''.join(c for c in unicodedata.normalize('NFD', h) if c not in '\u3099\u309a')


def _lv(a, b): return lev(a, b, 99)


# カナ表記ゆれをならした読み(海外の名前の「同じ語」判定用)。濁点の有無(ラース/ラーズ・ジェイムス/ジェイムズ・ハメッド/ハメット)、
# オ段とウ段(ジェイスン/ジェイソン)、ッヒ/ッチ(ウルリッヒ/ウルリッチ)、エイ/エー(ジェイムス/ジェームス)、ヴ/ブ は同じ語とみなす。
_OU = str.maketrans('おこそとのほもよろ', 'うくすつぬふむゆる')


def _canon(s):
    s = ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c)) if re.search(r'[À-ɏ]', s) else s
    if _isl(s):  # 英字どうし: 重ね字・有声/無声(g/k d/t b/p z/s v/f)・c/k・y/i・子音のあとの h をならす
        t = re.sub(r'[^a-z]', '', unicodedata.normalize('NFKC', s).lower()).replace('ck', 'k').replace('c', 'k').replace('y', 'i')
        t = re.sub(r'(?<=[^aeiou])h', '', t).translate(str.maketrans('gdbzv', 'ktpsf'))
        return re.sub(r'(.)\1+', r'\1', t)
    h = _nd(_rdc(s)).replace('ゔ', 'ふ')
    h = re.sub(r'つ[ひち]', 'つち', h).replace('えい', 'え').replace('てい', 'ち')
    return h.translate(_OU)


def _cspl(n):
    """区切りのない芸名を文字種の切れ目で分ける(ファンキー加藤 → ファンキー / 加藤)"""
    n = _PFX.sub('', unicodedata.normalize('NFKC', n).strip()).strip() or n
    return [x for x in re.findall(r'[ァ-ヶー]+|[一-鿿々]+|[ぁ-ゖ]+|[A-Za-z\'’.\-]+', n) if len(x.strip(".-'’")) >= 2 and x.lower().strip('.') not in _STOPT]


_STOPT = {'ちゃん', 'くん', 'さん', 'はん', 'jr', 'sr', 'dj', 'mc', 'ザ', 'the', 'ジュニア', 'ii', 'iii'}


_PFX = re.compile(r"^(dj|mc|ザ|the)(?=[\s・]|[^a-z]|$)\s*|\s*(sr|jr)\.?$", re.I)


def _np(n):
    n = unicodedata.normalize('NFKC', n).strip()
    n = _PFX.sub('', n).strip() or n  # DJ・MC などの肩書きは名前の語に数えない
    return [x for x in re.split(r"[\s・=＝·]+", n) if x]


def _sim(x, y):
    """名前の一語どうしが「同じ語」か(同じ・同じ読み・漢字の半分以上が共通・読みの大半が同じ)"""
    if x.lower() == y.lower(): return True
    rx, ry = rd(x), rd(y)
    if rx and rx == ry: return True
    if _kanji(x) and _kanji(y) and len(x) >= 2 and len(y) >= 2 and len(set(x) & set(y)) * 2 >= min(len(x), len(y)): return True
    if not rx or not ry: return False
    m = min(len(rx), len(ry)); bx, by = _nd(rx), _nd(ry)
    if m >= 2 and _lv(bx, by) <= max(1, max(len(bx), len(by)) // 3): return True
    nx, ny = norm(x), norm(y)
    if min(len(nx), len(ny)) >= 3 and _lv(nx, ny) * 2 <= max(len(nx), len(ny)) and not (_kanji(x) and _kanji(y)): return True
    pre = 0
    while pre < m and rx[pre] == ry[pre]: pre += 1
    return pre >= 2 and pre * 2 >= m and not (_kanji(x) and _kanji(y))


_RDC = {}


def _rdc(s):
    if s not in _RDC: _RDC[s] = rd(s)
    return _RDC[s]


def _lat(s): return re.sub(r'[^a-z]', '', unicodedata.normalize('NFKC', s).lower())


def _foreign(n):
    """海外勢(・区切り、または漢字・かなを含まない名前)"""
    n = unicodedata.normalize('NFKC', n)
    return '・' in n or '=' in n or not re.search(r'[぀-ヿ㐀-鿿々]', n)


def same_rd(x, y):
    """読みが同じ(英字は jaconv の読みが粗いので、英字部分も同じときだけ同じ読みとみなす)"""
    rx = _rdc(x)
    return bool(rx) and rx == _rdc(y) and _lat(x) == _lat(y)


def near_real(fake, real):
    """メンバー名が元ネタの実在メンバーに近すぎるか(方針: 藤原基央→藤川基夫 の水準の軽いもじり)。
    不可: 完全一致 / 姓名を通した読みが同じ / 姓だけ・名だけ同じ(片方完全一致)。
    可: 姓・名それぞれ1字か読み1音の違い(名は同じ読みの別の字でもよい。姓名の読みが全部同じになるのは不可)。
    海外勢(カタカナ・英字)も同じ基準: 名(最初の語)・姓(最後の語)のどちらかが同じなら不可
    (Mick Jagger→ミック・ジャガム は不可、ミッキ・ジャガム / ニック・ジャガム は可)。
    海外勢の語どうしは、カナと英字をまたいだ同じ読み・長音だけの違い(チャーリー/チャリー)も「同じ」とみなす。
    6回目QA: カナの表記ゆれ(濁点 ラース/ラーズ、ッチ/ッヒ、ソン/スン、エイ/エー)も「同じ」(_canon)。同じバンドの別人との名・姓の一致も不可。
    区切りのない芸名(ファンキー加藤)は文字種で分けて、芸名の語が残るものも不可。"""
    if norm(fake) == norm(real) or same_rd(fake, real) or _xrd(fake, real): return True
    a, b = _np(fake), _np(real)
    if len(a) == 1 and len(b) == 2 and _kanji(a[0]) and len(a[0]) >= 3 and _kanji(b[0]): a = [a[0][:len(b[0])], a[0][len(b[0]):]]
    if len(b) == 1 and len(a) == 2 and _kanji(b[0]) and len(b[0]) >= 3 and _kanji(a[0]): b = [b[0][:len(a[0])], b[0][len(a[0]):]]
    # 区切りのない芸名(ファンキー加藤)は文字種の切れ目で分ける。芸名の語(ファンキー)が残っていれば不可
    if len(a) < 2 and len(b) < 2: a, b = _cspl(fake), _cspl(real)
    elif len(b) < 2 and len(a) >= 2: b = _cspl(real)
    elif len(a) < 2 and len(b) >= 2: a = _cspl(fake)
    if len(a) < 2 or len(b) < 2: return False
    if _foreign(real) or _foreign(fake):
        # 海外勢: 名(最初の語)か姓(最後の語)のどちらかが、カナの表記ゆれ(濁点・オ/ウ段・ッヒ/ッチ)をならして同じなら不可。
        # 同じバンドの別人と名だけ同じ(ジョン・○○とジョン・ポール・ジョーンズ)も不可(6回目QA: ラース・ウルリッチ/ジェイスン)
        return _fpart(a[0], b[0]) or _fpart(a[-1], b[-1]) or _canon(a[0]) == _canon(b[0]) or _canon(a[-1]) == _canon(b[-1])
    return a[0].lower() == b[0].lower() or a[-1].lower() == b[-1].lower()


def _akin(x, y):
    """もう片方の語が元ネタの語らしい(似ている・読みの頭が同じ)"""
    return _sim(x, y) or (bool(_rdc(x)) and _rdc(x)[:1] == _rdc(y)[:1]) or (_lat(x)[:1] != '' and _lat(x)[:1] == _lat(y)[:1])


def _isl(s): return bool(re.fullmatch(r"[a-z\-'’.]+", unicodedata.normalize('NFKC', s).lower()))


def _fpart(x, y):
    """海外勢の名前の一語が「変わっていない」か。英字どうしは綴りが同じ、カナどうし・カナと英字は読みが同じ"""
    if x.lower() == y.lower(): return True
    if _isl(x) and _isl(y): return False
    return bool(_rdc(x)) and _rdc(x) == _rdc(y)


def _xrd(x, y):
    """カナと英字をまたいで姓名を通した読みが同じ(Mick Jagger / ミック・ジャガー)"""
    lx, ly = bool(_lat(x)), bool(_lat(y))
    if lx == ly: return False  # 同じ文字種どうしは same_rd に任せる
    return bool(_rdc(x)) and _rdc(x) == _rdc(y)


_PRD = {}
for _p in PERSON: _PRD.setdefault(_rdc(_p), []).append(_p)


def member_hits(n):
    """メンバー名: 実名(realnames.txt の全員)と一致 or 同じ読み。1字・1音違いは可"""
    x = norm(n)
    out = [p for p, q in PN if x == q]
    return out + [p for p in _PRD.get(_rdc(n), []) if p not in out and (same_rd(n, p) or _xrd(n, p))]


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
_MEMB = {}  # 正規化した名前 -> 使っている arcs(ゲーム内で他のメンバーと同名にしない)
for a in list(G1.ARCS) + arcs:
    k = a['k']; R = roster.ROSTER.get(k) or L(a.get('members')) or []
    fx = roster.REALFIX.get(k) or {}
    _LU = roster.LINEUP.get(k) or {}  # 結成時メンバー・後年の加入者(rosters/lineup.json)
    _LN = [v for v in (_LU.get('start') or {}).values() if v] + [c['in'] for c in _LU.get('mc') or [] if isinstance(c.get('in'), dict)]
    for x in list(R) + _LN:
        n = fx.get(x['n'], x['n'])
        _MEMB.setdefault(norm(n), []).append(k)
        mh = member_hits(n)
        for p in mh: hits.append(('member', k, n, p))
        for p in SECN.get(k, []):
            if near_real(n, p) and p not in mh: hits.append(('member~', k, n, p))
    for nm in [a['nm']] + list(L(a.get('alt')) or []):
        for p in [x for x in ART if norm(x) == norm(nm)] + [x for x in PERSON if x in nm] + name_hits(nm):
            hits.append(('artist', k, nm, p))
for _n, _ks in _MEMB.items():
    if len(_ks) > 1: hits.append(('member-dup', ','.join(_ks), _n, ''))

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
                    if G._PART_RX.match(s, m.start(2)): continue  # 「三人の管楽器」など一部の担当の人数(fix_count が担当数に合わせる)
                    c = CNT[m.group(2)] + (1 if m.group(1) in ('残りの', '他の') else 0)
                    if c != n and not re.search(r'客|観客|子|姉妹|兄弟|娘|息子|孫', s[max(0, m.start() - 6):m.end()]):
                        cnt_bad.append((k, n, f, s[:50]))

for h in hits: print('\t'.join(map(str, h)))
for c in cnt_bad: print('count\t%s\tmembers=%d\t%s\t%s' % c)
print('# hits', len(hits), 'count-mismatch', len(cnt_bad), file=sys.stderr)
