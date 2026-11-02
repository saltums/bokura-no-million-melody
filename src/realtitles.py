# -*- coding: utf-8 -*-
"""実在の有名曲名そのままを出さないための照合と差し替え。
  rosters/realtitles.txt : 実在曲名の一覧([*] どこでも / [キー] 元ネタ本人の曲 / 行頭 = ありふれた言葉)
  rosters/titlefix.json  : {旧曲名: 新曲名}(もじり。"" は使わない)
fix_list() は差し替えたあと、まだ実在曲名に当たるものを外す。検査は realname_scan.py。
"""
import re, json, unicodedata

_D = '/home/claude/rosters/'


def tnorm(t):
    """全半角・大小・空白・記号を無視し、末尾の(…)を外した形"""
    t = unicodedata.normalize('NFKC', str(t)).strip()
    t = re.sub(r'\s*[\((][^()()]*[\))]\s*$', '', t) or t
    return re.sub(r"[\s・\.\-'’\"“”=＝!?！？、。,~〜*★☆「」『』&＆:/♪…]", '', t.lower())


RT_ALL, RT_SEC, RT_GEN = set(), {}, set()
try:
    _cur = '*'
    for _l in open(_D + 'realtitles.txt', encoding='utf-8'):
        _l = _l.strip()
        if not _l or _l.startswith('#'): continue
        if _l.startswith('[') and _l.endswith(']'): _cur = _l[1:-1]; continue
        _x = tnorm(_l.lstrip('='))
        if not _x: continue
        RT_SEC.setdefault(_cur, set()).add(_x); RT_ALL.add(_x)
        if _l.startswith('='): RT_GEN.add(_x)
except OSError:
    pass
# 一般の曲名プールでも照合するもの: [*] と、ありふれた言葉でない・ある程度長いもの
RT_WIDE = {x for x in RT_ALL if x not in RT_GEN and (x in RT_SEC.get('*', ()) or len(x) >= (6 if re.fullmatch(r'[ -~]+', x) else 4))}
try:
    FIX = json.load(open(_D + 'titlefix.json', encoding='utf-8'))
except Exception:
    FIX = {}


def hit(t, key=None, pool='wide'):
    """t が実在曲名そのままか。key: 元ネタのキー(その曲は長さによらず照合)。pool: 'parody'(もじり曲名プール。全件と照合) / 'wide'"""
    x = tnorm(t)
    if not x: return False
    if key and x in RT_SEC.get(key, ()): return True
    return x in (RT_ALL if pool == 'parody' else RT_WIDE)


def fix(t):
    return FIX.get(t, t)


def fix_list(v, key=None, pool='wide', near=True):
    """差し替えたあと、実在曲名そのまま(hit)と、近すぎるもじり(close: QA9)を外す"""
    out = []
    for t in v:
        t = fix(t)
        if t and not hit(t, key, pool) and t not in out and not (near and close(t, key, pool)): out.append(t)
    return out


# ---- 近すぎるもじり(QA: 「Let It Bee」「涙のリクルート」は甘い。元曲が分かる程度にははっきり変える)
_KK = None


def _kk():
    global _KK
    if _KK is None:
        import sys as _s
        _s.path.insert(0, '/home/claude/_pylib')
        try:
            import pykakasi as _pk, jaconv as _jc
            _KK = (_pk.kakasi(), _jc)
        except Exception:
            _KK = (None, None)
    return _KK


_RDC = {}
_SM = str.maketrans('ぁぃぅぇぉっゃゅょゎゕゖ', 'あいうえおつやゆよわかけ')


def trd(x):
    """正規化済み曲名の読み(ひらがな)。濁点・半濁点・長音・小書きをならす"""
    if x in _RDC: return _RDC[x]
    kk, jc = _kk(); s = x
    if jc and re.fullmatch(r'[a-z]+', s or '-'): s = jc.alphabet2kana(s)
    h = ''.join(w['hira'] for w in kk.convert(s)) if kk else s
    h = ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in h)
    h = ''.join(c for c in unicodedata.normalize('NFD', h) if c not in '゙゚')
    h = unicodedata.normalize('NFC', h).translate(_SM)
    h = re.sub(r'[ーう]', '', h) if re.search(r'[ぁ-ゖ]', h) else h
    _RDC[x] = h
    return h


def _lev(a, b, cap):
    if abs(len(a) - len(b)) > cap: return cap + 1
    p = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        c = [i]; m = i
        for j, cb in enumerate(b, 1):
            v = min(p[j] + 1, c[j - 1] + 1, p[j - 1] + (ca != cb)); c.append(v); m = min(m, v)
        if m > cap: return cap + 1
        p = c
    return p[-1]


def _too_close(x, y):
    """x(もじり)と y(実曲名)が近すぎるか。どちらも tnorm 済み・x != y"""
    ly = len(y)
    if ly < 2: return False
    # QA9: 実曲名(5字以上)をそのまま頭か尻に含む(サイレントマジョリティー・ミール / Shout Baby Corn / IGNITE ME / MEMORIA 2)
    if ly >= 5 and len(x) > ly and (x.startswith(y) or x.endswith(y)): return True
    cap = 2
    sx = set(x)
    if sum(c not in sx for c in y) <= cap: d = _lev(x, y, cap)
    else: d = cap + 1
    if d <= 1 and ly >= 3: return True  # 1字(1文字・1語の綴り1字)だけの違い: 春よ、濃い / Let It Bee / 天体観測所
    if d == 2 and len(x) == ly and ly >= 6: return True  # 同じ長さで2字だけ差し替え: 涙のリクルート
    if d == 2 and ly >= 10: return True  # 長い曲名の綴り2字だけ: Tomorrow never shows
    if _LAT.fullmatch(x) and _LAT.fullmatch(y): return False  # 英字どうしは綴りで比べる(英字の読みは粗い)
    rx, ry = trd(x), trd(y)
    if rx and ry and len(ry) >= 2 and abs(len(rx) - len(ry)) <= 1 and sum(c not in set(rx) for c in ry) <= 1:
        if rx == ry: return True  # 同じ読み(字だけ替えた・濁点/長音だけ替えた): 鯉/恋
        if len(ry) >= 4 and len(rx) == len(ry) and _lev(rx, ry, 1) <= 1 and not (_LAT.search(x) or _LAT.search(y)): return True  # 読みが1音だけ違う
    return False


_LAT = re.compile(r'[a-z0-9]+')
_BYLEN = None


def _bylen():
    global _BYLEN
    if _BYLEN is None:
        _BYLEN = {}
        for y in RT_ALL:
            if y not in RT_GEN: _BYLEN.setdefault(len(y), []).append(y)
    return _BYLEN


def close(t, key=None, pool='wide'):
    """t が実在曲名に近すぎる(そのままではないが、1字・1音・同じ読みの違いしかない)なら、その実曲名を返す。
    key があれば元ネタ本人の曲([key])と [*] と照合。key なし(もじり曲名プール)は全曲名(ありふれた言葉を除く)と照合。"""
    x = tnorm(t)
    if not x or hit(t, key, pool): return None
    if key:
        cands = set(RT_SEC.get(key, ())) | set(RT_SEC.get('*', ()))
    else:
        bl = _bylen(); cands = []
        for n in range(max(1, len(x) - 3), len(x) + 4): cands += bl.get(n, [])
    for y in cands:
        if y != x and abs(len(y) - len(x)) <= 3 and _too_close(x, y): return y
    # QA9: 実曲名(5字以上・ありふれた言葉を除く)をそのまま頭か尻に含む(長さの差は問わない)
    pool_ = (set(RT_SEC.get(key, ())) | set(RT_SEC.get('*', ()))) if key else RT_ALL
    for y in pool_:
        if 5 <= len(y) < len(x) and y not in RT_GEN and (x.startswith(y) or x.endswith(y)): return y
    return None
