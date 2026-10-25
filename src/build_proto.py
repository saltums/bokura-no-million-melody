#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""プロトタイプ用: 分かれ道ごとに全選択肢を先に走らせ、物語の木(JSON)を作る。"""
import json, sys, random
sys.path.insert(0, '/home/claude')
import ongaku_storyline_gen as g
import lyrics
import lyrics_struct
import tracks, bio, gender, rare_gen, real_gen, arcs_gen
import copy
WORDS = (g.TIME, g.PLACE, g.THING)

MAXDEC = 3
QUOTA = {"band": 14, "inst": 6, "duo": 8, "solo": 12, "rap": 8, "beat": 8, "dj": 6, "ai_pure": 8, "ai_collab": 8}


VI = [("自分の言葉のままCM", "自分たちの音のままCM"), ("そのまま言葉にした歌", "そのまま音にした曲"), ("ただ疲れたとつぶやくだけの歌", "ただ疲れ切った空気だけを鳴らす曲"), ("完璧すぎる音と言葉に", "完璧すぎる音に"),
      ("本人の言葉で語られ", "本人の音で語られ"), ("合言葉のように歌詞が", "合言葉のように曲名が"), ("愛唱歌", "愛聴曲"), ("言葉の響きだけで", "音の響きだけで"),
      ("歌詞の題材", "曲の題材"), ("歌詞をSNSに", "曲名をSNSに"), ("歌った曲", "描いた曲"), ("が歌う", "が奏でる"), ("歌う", "奏でる"),
      ("歌詞", "曲の世界観"), ("サビが最後まで来ず", "山場が最後まで来ず"), ("歌", "曲")]


def _vi(t):
    if not isinstance(t, str): return t
    for a, b in VI: t = t.replace(a, b)
    return t


def ser(item, c=None, st=None):
    if item[0] == 'release':
        h = dict(item[1])
        if c is not None and c['style'] == 'inst':
            h['premise'] = _vi(h['premise']); h['reason'] = _vi(h['reason']); h['form'] = _vi(h['form'])
        out = {"t": "r", "y": h['year'], "o": h['ord'] + h['kind'], "ti": h['title'], "lb": h['label'], "tr": h['tier'],
               "pr": h['premise'], "th": h['theme'], "rs": h['reason'], "fm": h['form']}
        if st is not None:
            out["tk"] = tracks.tracklist(h, c['style'], c['era'], h['theme'], list(st['seen']))
            st['seen'].append(h['title'])
        if c is not None:
            vg = gender.vocal(c, st['mem'] if st is not None else tracks.people(c['seed'], c['style']))
            lyrics.VG = vg
            ly = lyrics_struct.make_struct(h['theme'], c['genre'], h['premise'], h['title'], h['year'], WORDS, c['era'] <= 1, c['era'], inst=(c['style'] == 'inst'))
            if ly:
                ly['vg'] = vg
                out["ly"] = ly
        return out
    if item[0] == 'dec':
        d = item[1]
        out = {"t": "x", "c": d['labels'][d['chosen']], "ok": d['ok'], "tx": _vi(d['text']) if c is not None and c['style'] == 'inst' else d['text']}
        if st is not None and c['style'] in ('band', 'inst', 'duo'):
            lab = out['c']
            if lab == "新メンバーを探して続ける" and st['vac']:
                role = st['vac'].pop(0); nw = tracks.newcomer(c['seed'], role, {m['n'] for m in st['mem']}); st['mem'].append(nw); out['mb'] = {"in": nw}
            elif lab == "少人数で形を変えて続ける":
                st['vac'] = []; out['mb'] = {"note": "少人数編成に"}
        return out
    out = {"t": "e", "tx": _vi(item[2]) if c is not None and c['style'] == 'inst' else item[2]}
    if st is not None and c['style'] in ('band', 'inst', 'duo'):
        tx = item[2]
        if tx.startswith("メンバーが脱退") and len(st['mem']) >= 2:
            k = (c['seed'] + len(st['seen'])) % len(st['mem']); gone = st['mem'].pop(k); st['vac'].append(gone['r']); out['mb'] = {"out": gone}
        elif (tx.startswith("新しく入ったメンバー") or tx.startswith("新メンバーとの呼吸")) and st['vac']:
            role = st['vac'].pop(0); nw = tracks.newcomer(c['seed'], role, {m['n'] for m in st['mem']}); st['mem'].append(nw); out['mb'] = {"in": nw}
    return out


def node(seed, script, start, st0=None):
    c = g.generate(seed, script=list(script), maxdec=MAXDEC)
    st = copy.deepcopy(st0) if st0 else {"mem": tracks.people(seed, c['style']), "vac": [], "seen": []}
    seg = [ser(i, c, st) for i in c['log'][start:]]
    if c.get('pending'):
        L = len(c['log'])
        kids = [node(seed, script + [k], L, st) for k in range(len(c['pending']['labels']))]
        return {"s": seg, "q": c['pending'], "n": kids}
    works = [{"y": h['year'], "ti": h['title'], "tr": h['tier'], "th": h['theme'], "pr": h['premise'],
              "o": h['ord'] + h['kind']} for h in c['hist']]
    return {"s": seg, "e": {"tx": c['ending'], "w": works, "mm": st['mem']}}


def count_leaves(n):
    return 1 if 'e' in n else sum(count_leaves(k) for k in n['n'])


def meta(c):
    sc = c['start_choice']
    start_txt = g.AI_START[c['ai_mode']] if c['ai_mode'] else g.START[(c['start'], c['era'])]
    return {"id": c['seed'], "a": c['artist'], "pun": c['pun_src'], "top": sc['top'], "st": c['style'],
            "sn": g.style_name(c), "pe": c['P']['n'], "era": c['era'], "en": g.ERAS[c['era']]['name'],
            "es": g.ERAS[c['era']]['short'], "sa": c['start'], "ge": c['genre'], "tx": start_txt, "ai": c['ai_mode'],
            "mm": tracks.people(c['seed'], c['style']), "vg": gender.vocal(c, tracks.people(c['seed'], c['style'])), "bio": bio.make(c['seed'], c['style'], c['era'], c['ai_mode'], c['start_choice']['top'] == "グループ")}


def main():
    pool = []
    for style, quota in QUOTA.items():
        used = set(); got = 0
        for seed in range(0, 60000):
            if got >= quota:
                break
            c = g.generate(seed, script=[], maxdec=MAXDEC)
            if c['style'] != style:
                continue
            key = (c['P']['n'], c['era'])
            if key in used:
                continue
            if not c.get('pending') or len(c['hist']) < 2:
                continue
            m = meta(c)
            tree = node(seed, [], 0)
            if count_leaves(tree) > 90:
                continue
            used.add(key); got += 1
            pool.append({"m": m, "t": tree})
        print(style, got)
    # 人数ちがいのバンド(カスタム用)
    _R0 = dict(tracks.ROLES)
    for _n, _roles in ((3, ["Vo/Gt", "Ba", "Dr"]), (5, ["Vo", "Gt", "Key", "Ba", "Dr"]), (6, ["Vo", "Gt", "Gt", "Key", "Ba", "Dr"])):
        tracks.ROLES["band"] = _roles
        _used = set(); _got = 0
        for seed in range(100000, 220000):
            if _got >= 7: break
            c = g.generate(seed, script=[], maxdec=MAXDEC)
            if c['style'] != 'band': continue
            key = c['era']
            if key in _used: continue
            if not c.get('pending') or len(c['hist']) < 2: continue
            m = meta(c); tree = node(seed, [], 0)
            if count_leaves(tree) > 14: continue
            _used.add(key); _got += 1
            m["np"] = _n
            pool.append({"m": m, "t": tree})
        print("band", _n, _got)
    tracks.ROLES.clear(); tracks.ROLES.update(_R0)
    pool += rare_gen.trees(4)
    pool.append(real_gen.build())
    pool += arcs_gen.build_all()
    import arcs2_gen
    _a2 = arcs2_gen.build_all(); [x['m'].__setitem__('_lz', 1) for x in _a2]; pool += _a2
    import random as _r
    def _fixvg(n, vg):
        for it in n.get('s', []):
            if it.get('t') == 'r' and it.get('ly'): it['ly']['vg'] = vg
        for c in n.get('n', []) or []: _fixvg(c, vg)
    for _e in pool:
        _m = _e['m']; _vo = [x for x in (_m.get('mm') or []) if str(x.get('r', '')).startswith('Vo') and x.get('g') in ('m', 'f')]
        if _vo and _m.get('vg') in ('m', 'f') and _vo[0]['g'] != _m['vg'] and _e.get('t'):
            _m['vg'] = _vo[0]['g']; _fixvg(_e['t'], _m['vg'])
    for _e in pool:
        _b = _e["m"].get("bio") or {}
        if _b.get("fd") and _e["m"].get("mm"):
            _c = [_b.get("hm")] + [x.get("h") for x in _e["m"]["mm"]]
            _c = [x for x in _c if x]
            if _c and _b["fd"] not in _c:
                _b["fd"] = _r.Random(str(_e["m"]["id"])).choice(_c)
    def _shq(n, rng):
        ks = n.get('n') or []
        if len(ks) > 1 and n.get('q') and len(n['q'].get('labels', [])) == len(ks):
            idx = list(range(len(ks))); rng.shuffle(idx)
            n['n'] = [ks[i] for i in idx]; n['q']['labels'] = [n['q']['labels'][i] for i in idx]
            for k2 in ('ok',):
                if isinstance(n['q'].get(k2), list) and len(n['q'][k2]) == len(idx): n['q'][k2] = [n['q'][k2][i] for i in idx]
        for c in n.get('n') or []: _shq(c, rng)
    import json as _j
    _EV = _j.load(open('/home/claude/endvars.json'))
    def _vend(n, rng):
        for c in n.get('n') or []: _vend(c, rng)
        e = n.get('e')
        if isinstance(e, dict) and e.get('tx') in _EV and not n.get('n'):
            e['tx'] = rng.choice([e['tx']] + _EV[e['tx']])
    for _e in pool:
        if _e.get('t'): _vend(_e['t'], _r.Random('vend%s' % _e['m']['id']))
    for _e in pool:
        if _e.get('t') and not _e['m'].get('rare'): _shq(_e['t'], _r.Random('shq%s' % _e['m']['id']))
    import os
    os.makedirs('/home/claude/dshards', exist_ok=True)
    for _f in os.listdir('/home/claude/dshards'): os.remove('/home/claude/dshards/' + _f)
    ids = [e['m']['id'] for e in pool]; import collections as _c; _d = [k for k, v in _c.Counter(ids).items() if v > 1]; print('DUPS', _d[:20])
    _pk = {}; _n = 0
    for _e in pool:
        _e['m'].pop('_lz', None)
        if not _e['m'].get('rare'):
            _g = _n // 3; _n += 1; _pk.setdefault(_g, {})[str(_n - 1)] = _e['t']; _e['m']['lk'] = str(_n - 1)
            _e['m']['lz'] = 'd/p' + str(_g) + '.json'; _e['t'] = None
    for _g, _o in _pk.items():
        open('/home/claude/dshards/p' + str(_g) + '.json', 'w', encoding='utf-8').write(json.dumps(_o, ensure_ascii=False, separators=(',', ':')))
    out = json.dumps(pool, ensure_ascii=False, separators=(',', ':'))
    open('/home/claude/proto_data.json', 'w', encoding='utf-8').write(out)
    print("trees", len(pool), "bytes", len(out.encode('utf-8')))


main()
