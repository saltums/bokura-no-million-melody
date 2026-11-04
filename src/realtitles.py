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


def _too_close(x, y, own=False):
    """x(もじり)と y(実曲名)が近すぎるか。どちらも tnorm 済み・x != y。
    新基準(2026-11): 元曲が一瞬で分かる1〜2字・1語の差し替えは「可」(天体観光 / 春よ、濃い / Let It Bee / 涙のリクルート)。
    不可は (1) 同じ音で字・かなだけ替えた(鯉/恋・さくら/桜・ステイション/ステーション)、(2) 実曲名そのまま+語の付け足し(天体観光ツアー型の「元曲+一語」)。
    同じ音は漢字の駄洒落でも不可(真夜中すぎの鯉)。例外はユーザーが可と明示した ALLOW(春よ、濃い)だけ。"""
    ly = len(y)
    # (2) 実曲名をそのまま頭か尻に含み、2字以上付け足しただけ(Let It Bee-keeper / 神田川の増水)。元ネタ本人の曲(own)は英字4字・和文2字から、
    #     ほかの実曲名は英字8字・和文5字から(「さよなら」「Emotion」のような短いありふれた曲名は語として使ってよい)
    if len(x) - ly >= 2 and (x.startswith(y) or x.endswith(y)) and ly >= ((4, 2) if own else (8, 5))[0 if _LAT.fullmatch(y) else 1]: return True
    # (1) 同じ音
    if _LAT.fullmatch(x) and _LAT.fullmatch(y):
        return _cons(x) == _cons(y)  # 英字どうし: 子音の重ねだけ違う(Lemmon/Lemon)は同じ音。Let It Bee は可
    rx, ry = trd2(x), trd2(y)
    return bool(rx and ry and len(ry) >= 2 and rx == ry and x not in ALLOW)


# 同じ音でもユーザーが「可」と明示した例(2026-11 指示)
ALLOW = {tnorm(_t) for _t in ('春よ、濃い',)}


_RD2 = {}


def trd2(x):
    """読み(ひらがな)。濁点は区別し、長音・「う」・小書きだけならす(音が変わったかを見る)"""
    if x in _RD2: return _RD2[x]
    kk, jc = _kk(); s = x
    if jc and re.fullmatch(r'[a-z]+', s or '-'): s = jc.alphabet2kana(s)
    h = ''.join(w['hira'] for w in kk.convert(s)) if kk else s
    h = ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in h)
    h = unicodedata.normalize('NFC', h).translate(_SM)
    h = re.sub(r'[ーう]', '', h) if re.search(r'[ぁ-ゖ]', h) else h
    _RD2[x] = h
    return h


def _cons(s):
    return re.sub(r'([b-df-hj-np-tv-z])\1+', r'\1', s)


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
    """t が実在曲名に近すぎるなら、その実曲名を返す(新基準: 同じ読み / 実曲名そのまま+付け足し)。
    1〜2字・1語の差し替えで音が変わるもじりは通す。key があれば元ネタ本人の曲([key])と [*]、key なしは全曲名(ありふれた言葉を除く)と照合。"""
    x = tnorm(t)
    if not x or hit(t, key, pool): return None
    if key:
        own = set(RT_SEC.get(key, ())); cands = (own | set(RT_SEC.get('*', ()))) - RT_GEN
        for y in cands:
            if y != x and _too_close(x, y, y in own): return y
        return None
    # key なし: 頭・尻の部分一致と読みの一致を索引で引く
    for n in range(5, len(x) - 1):
        for y in (x[:n], x[-n:]):
            if y in _NG_ALL and _too_close(x, y): return y
    rx = ('#' + _cons(x)) if _LAT.fullmatch(x) else trd2(x)
    for y in _rdi().get(rx, ()):
        if y != x and _too_close(x, y): return y
    return None


_NG_ALL = RT_ALL - RT_GEN
_RDI = None


def _rdi():
    global _RDI
    if _RDI is None:
        _RDI = {}
        for y in _NG_ALL:
            if not _LAT.fullmatch(y): _RDI.setdefault(trd2(y), []).append(y)
            else: _RDI.setdefault('#' + _cons(y), []).append(y)
    return _RDI
