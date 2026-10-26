import json, glob
p = '/home/claude/namebank.json'
b = json.load(open(p, encoding='utf-8'))
# events
seen = {e['t'] for e in b['ev']}; n0 = len(b['ev'])
for f in sorted(glob.glob('/home/claude/add_ev/ev_*.json')):
    try: d = json.load(open(f, encoding='utf-8'))
    except Exception as ex: print('SKIP', f, ex); continue
    for e in d:
        if not isinstance(e, dict) or not e.get('t') or e['t'] in seen: continue
        if e.get('k') not in ('a', 'g', 's') or e.get('m') not in ('any', 'up', 'down') or e.get('e') not in ('all', 'old', 'mid', 'new'): continue
        e.setdefault('f', 'x_' + e['t'][:3]); seen.add(e['t']); b['ev'].append({k: e[k] for k in ('t', 'k', 'm', 'e', 'f')})
print('ev', n0, '->', len(b['ev']))
# titles
for f in sorted(glob.glob('/home/claude/add_t/t_*.json')):
    try: d = json.load(open(f, encoding='utf-8'))
    except Exception as ex: print('SKIP', f, ex); continue
    ps = set(b['pt']); b['pt'] += [x for x in dict.fromkeys(d.get('pt', [])) if x not in ps]
    for e in ('old', 'mid', 'new'):
        s = set(b['t'][e]); b['t'][e] += [x for x in dict.fromkeys(d.get(e, [])) if x not in s and 1 < len(x) <= 24]
print('pt', len(b['pt']), {e: len(v) for e, v in b['t'].items()})
# 曲名+サビ(テーマ別)
b['tt'] = {}
for f in sorted(glob.glob('/home/claude/add_tt/tt_*.json')):
    try: d = json.load(open(f, encoding='utf-8'))
    except Exception as ex: print('SKIP', f, ex); continue
    th = d.get('theme'); seen = set(); L = b['tt'].setdefault(th, [])
    for x in d.get('items', []):
        try:
            t = x['t'].strip(); h1 = x['h1'].strip(); h2 = x.get('h2', '').strip(); e = x.get('e', 'all')
            if not t or t in seen or len(t) > 24 or e not in ('all', 'old', 'mid', 'new') or not (4 <= len(h1) <= 34): continue
            seen.add(t); L.append([t, e, h1, h2])
        except Exception: continue
print('tt', {k: len(v) for k, v in b['tt'].items()})
# artist names
for f in sorted(glob.glob('/home/claude/add_a/a_*.json')):
    try: d = json.load(open(f, encoding='utf-8'))
    except Exception as ex: print('SKIP', f, ex); continue
    for st, cells in d.items():
        if st not in b['a'] or not isinstance(cells, dict): continue
        for e in ('old', 'mid', 'new'):
            s = set(b['a'][st].get(e, [])); b['a'][st].setdefault(e, []); b['a'][st][e] += [x for x in dict.fromkeys(cells.get(e, [])) if x not in s]
print('a', {st: {e: len(v) for e, v in d.items()} for st, d in list(b['a'].items())[:3]})
json.dump(b, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
# side choices
import glob as _g
sd = []; seen2 = set()
for f in sorted(_g.glob('/home/claude/add_sd/sd_*.json')):
    try: d = json.load(open(f, encoding='utf-8'))
    except Exception as ex: print('SKIP', f, ex); continue
    for x in d:
        try:
            if x['pr'] in seen2 or x['k'] not in ('a', 'g', 's') or x['e'] not in ('all', 'old', 'mid', 'new'): continue
            os_ = [o for o in x['o'] if o.get('l') and o.get('ok') is not None and 0 < float(o['p']) <= 1 and 0 < float(o['g']) <= .2]
            if len(os_) < 2: continue
            x['pr'] = x['pr'].replace('さて、どうする。', '').strip(); seen2.add(x['pr']); sd.append({'k': x['k'], 'e': x['e'], 'lab': x.get('lab', '寄り道')[:8], 'pr': x['pr'], 'o': [dict({'l': o['l'], 'p': float(o['p']), 'g': float(o['g']), 'ok': o['ok'], 'ng': o.get('ng', '')}, **({'gs': 1, 'fu_ok': o.get('fu_ok', ''), 'fu_ng': o.get('fu_ng', '')} if o.get('gs') else {})) for o in os_]})
        except Exception: continue
b['sd'] = sd; print('sd', len(sd))
import nb_sanitize; nb_sanitize.sanitize(b)  # 実名に近すぎるもじり・「a:」ラベル・グループ文の人数語
json.dump(b, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
