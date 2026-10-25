# -*- coding: utf-8 -*-
"""もじり名メンバー名簿を適用する。rosters/out*.json と、各 arcs の members フィールド。"""
import glob, json, copy
import tracks
ROSTER = {}
for _f in sorted(glob.glob('/home/claude/rosters/out*.json')):
    try:
        ROSTER.update(json.load(open(_f)))
    except Exception as _e:
        print('ROSTER SKIP', _f, _e)


def apply(a, mm, seed):
    R = a.get('members') or ROSTER.get(a.get('k'))
    if not R:
        return mm
    out = []
    for j, x in enumerate(R):
        if j < len(mm):
            b = dict(mm[j])
        else:
            b = dict(tracks.newcomer(seed, x.get('r', 'Gt'), {m['n'] for m in mm}))
        b['n'] = x['n']; b['r'] = x.get('r') or b.get('r', ''); b['g'] = x.get('g') or b.get('g', 'm')
        out.append(b)
    return out
