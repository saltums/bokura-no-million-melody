# -*- coding: utf-8 -*-
import glob, json
PTO = {}
for _f in sorted(glob.glob('/home/claude/ptfix/out*.json')):
    try:
        for k, v in json.load(open(_f)).items():
            v = [t for t in dict.fromkeys(x.strip() for x in v if isinstance(x, str) and x.strip())]
            if len(v) >= 8: PTO[k] = v
    except Exception as e:
        print('PTO SKIP', _f, e)
def apply(arcs, pt):
    return pt  # 2026-10: arcs_new の PT(精査済み)を正とする。旧 ptfix の上書きは無効化
    for a in arcs:
        if a['k'] in PTO: pt[a.get('par') or a['k']] = PTO[a['k']]
    return pt

PTX = {}
for _f in sorted(glob.glob('/home/claude/ptfix/x_*.json')):
    try:
        for k, v in json.load(open(_f)).items():
            PTX[k] = [t for t in dict.fromkeys(x.strip() for x in v if isinstance(x, str) and x.strip())]
    except Exception as e:
        print('PTX SKIP', _f, e)
def deep(k, main, seen):
    """アルバム曲用: 深い曲 + 表題に使われなかった代表曲"""
    ex = list((main or [])[12:])  # 旧 PTX は実曲名が混ざるため不使用
    return [t for t in dict.fromkeys(ex) if t not in seen]
