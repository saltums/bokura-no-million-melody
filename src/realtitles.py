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


def fix_list(v, key=None, pool='wide'):
    out = []
    for t in v:
        t = fix(t)
        if t and not hit(t, key, pool) and t not in out: out.append(t)
    return out
