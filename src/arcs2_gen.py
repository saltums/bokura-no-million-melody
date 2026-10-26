# -*- coding: utf-8 -*-
"""着想型の人生 v2。分かれ道の数(3〜5)・追加イベント・時代ちがいの版に対応。
各アーティストの仕様は arcs_new/*.py の ARCS(リスト)と PT(曲名の辞書)で与える。仕様はagent_brief.mdを参照。"""
import copy, random, glob, os, re, importlib.util
import roster as _ro0
import ongaku_storyline_gen as g
import lyrics, lyrics_struct, tracks, bio
from arcs_gen import H, cl, era_of, pr_of, HIT, FLOP, FORM, KIND, ORD, WORDS, THEME, wk
from parody_titles import PT as PT0

ERA_WORDS = {"動画サイト": 2005, "SNS": 2008, "配信": 2006, "ストリーミング": 2012, "サブスク": 2014, "ショート動画": 2018, "ハッシュタグ": 2010, "ネット": 1998, "ホームページ": 1996, "ブログ": 2002, "関連欄": 2008, "ガラケー": 1997, "着うた": 2002, "ボカロ": 2007, "海外の動画": 2005, "バズ": 2008, "拡散": 2008, "リール": 2018, "インディーズ": 1980, "CD": 1982, "カセット": 1968}
BRIDGE = re.compile(r"解散|活動を休止|休止す|休む|引退|区切り")
BRIDGE_TX = ["しばらくの空白があった。それでも、また音を鳴らす日が来た。", "離れていた時間を経て、ふたたび歩き出した。", "何もしない季節が過ぎ、気がつくと楽器に手が伸びていた。"]


def era_ok(tx, year):
    return all(year >= y for w, y in ERA_WORDS.items() if w in tx)


def cap_fives(tree, cap=2):
    def walk(n, k):
        for it in n["s"]:
            if it.get("t") == "r":
                if it["tr"] >= 5:
                    k += 1
                    if k > cap: it["tr"] = 4
        if n.get("n"):
            for c in n["n"]: walk(c, k)
        elif n.get("e"):
            # 葉の作品リストは、経路上の作品と同じ順で並んでいる
            pass
    # 経路ごとに「作品の当たり具合」を揃える: 葉のw[].trを再計算
    def leaf_fix(n, path):
        path = path + [it for it in n["s"] if it.get("t") == "r"]
        if n.get("n"):
            for c in n["n"]: leaf_fix(c, path)
        elif n.get("e"):
            for w, r in zip(n["e"]["w"], path):
                if isinstance(w, dict) and "tr" in w: w["tr"] = r["tr"]
    walk(tree, 0); leaf_fix(tree, [])


ERA_Y = {-1: 1974, 0: 1983, 1: 1996, 2: 2004, 3: 2013, 4: 2021}
STN = {"band": "バンド", "duo": "2人組ユニット", "solo": "シンガーソングライター", "rap": "ラッパー", "beat": "ボカロP・トラックメイカー", "dj": "DJ", "inst": "インストバンド"}


def load_specs(dirpath='/home/claude/arcs_new'):
    arcs, pt = [], {}
    for f in sorted(glob.glob(os.path.join(dirpath, 'arcs_*.py'))):
        if os.environ.get('SKIP_B') and os.path.basename(f).startswith('arcs_b'): continue
        spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f); m = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(m)
        except Exception as e:
            print('SKIP', f, e); continue
        arcs += getattr(m, 'ARCS', []); pt.update(getattr(m, 'PT', {}))
    _seen = set(); _u = []
    for _a in arcs:
        if _a['nm'] in _seen: print('DUP-NM skip', _a['k'], _a['nm']); continue
        _seen.add(_a['nm']); _u.append(_a)
    arcs = _u
    pt = {k: list(dict.fromkeys(t.split('→')[-1].strip() for t in v)) for k, v in pt.items()}
    import ptover; pt = ptover.apply(arcs, dict(pt))
    return arcs, pt


def rel(a, pool, seen, pos, y, tier, th, lb, dev, era):
    r = random.Random(H(a["k"], "rel", pos, dev, era))
    ti = pool[(pos * 3 + dev * 2) % len(pool)]
    n = 0
    while ti in seen and n < len(pool): ti = pool[(pool.index(ti) + 1) % len(pool)]; n += 1
    seen.append(ti)
    pr = pr_of(r, th); k = KIND[min(pos, len(KIND) - 1)]
    h = dict(kind=k, ord="", title=ti, year=y, tier=tier, theme=th, premise=pr, label=lb)
    st = a["st"] if a["st"] in ("band", "duo", "rap", "solo", "beat") else "band"
    tk = tracks.tracklist(h, st, era, th, list(seen), extra=__import__('ptover').deep(a['k'], pool, seen))
    seen.extend(x['t'] for x in tk if x['t'] not in seen)
    lyrics.VG = a["vg"]
    ly = lyrics_struct.make_struct(th, a["ge"], pr, ti, y, WORDS, era <= 1, era)
    if ly: ly["vg"] = a["vg"]
    t = THEME[th]; rs = r.choice(t["hit"]) if tier >= 2 else r.choice(FLOP)
    return {"t": "r", "y": y, "o": ORD[min(pos, len(ORD) - 1)], "ti": ti, "lb": lb, "tr": tier, "pr": pr, "th": th, "rs": rs if tier < 2 else r.choice(HIT), "fm": r.choice(FORM), "tk": tk, "ly": ly}


def build(a, i, pool, era=None, nm=None):
    st = a["st"]; real_era = era_of(a["y0"]); era = real_era if era is None else era
    y0 = a["y0"] if era == real_era else ERA_Y[era] - 2 + (a["y0"] % 3)
    seed = 300000 + i * 10 + (0 if era == real_era else 1 + (era + 1))
    mm = tracks.people(seed, st if st in ("band", "duo", "inst") else "solo")
    roles = a.get("roles") or []
    if roles:
        mm = mm[:len(roles)]
        while len(mm) < len(roles):
            nw = tracks.newcomer(seed, roles[len(mm)], {x["n"] for x in mm}); mm.append(nw)
        for j, m_ in enumerate(mm):
            m_["r"] = roles[j]
            if j < len(a.get("tr", [])): m_["t"] = a["tr"][j]
        G = a.get("vg")
        if G in ("m", "f"):
            import re as _re, random as _rd
            INSTR = _re.compile(r"^(Gt|Ba|Dr|Key|Pf|Sax|Tp|Vn|Vc|Cho|Tb|Per|DJ|Syn|Gu|Ag|Eg|Mp|Fl|Hr|Cl)", _re.I)
            taken = {x["n"] for x in mm}
            for j, m_ in enumerate(mm):
                r0 = m_["r"]; isvo = r0.startswith("Vo") or not INSTR.match(r0)
                if isvo and m_["g"] != G and not (a.get('members') or _ro0.ROSTER.get(a['k'])):
                    rr = _rd.Random(H(a["k"], "vgfix", j, era))
                    for _ in range(60):
                        nm2 = rr.choice(tracks.FAM) + " " + rr.choice(tracks.GIV_M if G == "m" else tracks.GIV_F)
                        if nm2 not in taken: break
                    taken.discard(m_["n"]); taken.add(nm2); m_["n"] = nm2; m_["g"] = G
    import roster as _ro
    mm = _ro.apply(a, mm, seed)
    top = "グループ" if st in ("band", "duo", "inst") else "ソロ"
    E = g.ERAS[era]
    name = nm or a["nm"]
    meta = {"id": seed, "a": name, "pun": None, "top": top, "st": st if st != "dj" else "solo", "sn": STN.get(st, "シンガーソングライター"), "pe": "まじめ", "era": era, "en": E["name"], "es": E["short"], "sa": a["sa"], "ge": a["ge"],
            "tx": a["tx"], "ai": None, "mm": mm, "vg": a["vg"], "bio": bio.make(seed, st if st != "dj" else "solo", era, None, top == "グループ"), "real": True, "histTx": a["eh"], "cp": a.get("cp", [])}
    th = a["th"]; D = a["d"]; N = len(D); cv = a["cv"]; ev = list(a["ev"]); ex = list(a.get("ex") or [])
    _yy = y0 + 2
    ex = [x for x in ex if era_ok(x, _yy)]
    ev = [x if era_ok(x, _yy) else "活動は、少しずつ、確かな形になっていった。" for x in ev]
    rr = random.Random(H(a["k"], "ex", era)); rr.shuffle(ex)
    counter = [0]

    def stage(si, eff, dv, seen):
        out = []
        for k, bt in enumerate(cv[min(si, len(cv) - 1)]):
            pos = counter[0] + k
            y = y0 + a["yr"][min(pos, len(a["yr"]) - 1)]
            out.append(rel(a, pool, seen, pos, y, cl(bt + eff), th[(pos + dv) % len(th)], a["lb"][min(si, len(a["lb"]) - 1)], dv, era))
        return out

    def evs(si):
        o = [{"t": "e", "tx": ev[min(si, len(ev) - 1)]}]
        if ex and si >= 1: o.append({"t": "e", "tx": ex[(si - 1) % len(ex)]})
        return o

    def X(d, alt):
        return {"t": "x", "c": d[2] if alt else d[1], "ok": (d[6] if alt else d[5]) >= 0, "tx": d[4] if alt else d[3]}

    def q(d): return {"prompt": d[0], "labels": [d[1], d[2]], "h": 0}

    def node(si, eff, dv, seen, pos0, prior_works):
        # si: 次に控える分かれ道の番号。この関数が返すのは「分かれ道siの子ノード群」
        kids = []
        for x in (0, 1):
            sn = copy.deepcopy(seen); counter[0] = pos0
            e2 = eff + D[si][6 if x else 5]; dv2 = dv + x
            lab_ = D[si][2 if x else 1]
            seg = [X(D[si], x)] + ([{"t": "e", "tx": BRIDGE_TX[(si + x) % len(BRIDGE_TX)]}] if BRIDGE.search(lab_) else []) + evs(si + 1) + stage(si + 1, e2, dv2, sn)
            pos1 = pos0 + len(cv[min(si + 1, len(cv) - 1)])
            works = prior_works + [w for w in seg if w["t"] == "r"]
            if si + 1 < N:
                kids.append({"s": seg, "q": q(D[si + 1]), "n": node(si + 1, e2, dv2, sn, pos1, works)})
            else:
                tx = a["eh"] if dv2 == 0 else a["ea"][min(dv2 - 1, len(a["ea"]) - 1)]
                kids.append({"s": seg, "e": {"tx": tx.rstrip("。"), "w": [wk(w) for w in works], "mm": mm}})
        return kids

    seen0 = []; counter[0] = 0
    s0 = evs(0)[:1] + stage(0, 0, 0, seen0)
    pos1 = len(cv[0]); w0 = [w for w in s0 if w["t"] == "r"]
    tree = {"s": s0, "q": q(D[0]), "n": node(0, 0, 0, seen0, pos1, w0)}
    cap_fives(tree)
    return {"m": meta, "t": tree}


def build_all(dirpath='/home/claude/arcs_new', variants=True):
    arcs, pt = load_specs(dirpath); out = []
    for i, a in enumerate(arcs):
        try:
            pool = pt.get(a["par"]) or PT0.get(a["par"]) or PT0["misc"]
            pool = list(dict.fromkeys(pool + PT0["misc"][:6]))
            out.append(build(a, i, pool))
            if variants:
                real_era = era_of(a["y0"]); alts = [e for e in a.get("eras", []) if e != real_era and e in ERA_Y]
                names = a.get("alt") or []
                for vi, e in enumerate(alts[:2]):
                    if vi < len(names): out.append(build(a, i, pool, era=e, nm=names[vi]))
        except Exception as ex:
            print('BUILD FAIL', a.get("k"), repr(ex))
    return out
