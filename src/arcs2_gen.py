# -*- coding: utf-8 -*-
"""着想型の人生 v2。分かれ道の数(3〜5)・追加イベント・時代ちがいの版に対応。
各アーティストの仕様は arcs_new/*.py の ARCS(リスト)と PT(曲名の辞書)で与える。仕様はagent_brief.mdを参照。"""
import copy, random, glob, os, re, importlib.util
import roster as _ro0
import ongaku_storyline_gen as g
import lyrics, lyrics_struct, tracks, bio, eraword
from arcs_gen import H, cl, era_of, pr_of, HIT, FLOP, FORM, KIND, ORD, WORDS, THEME, wk
from parody_titles import PT as PT0

ERA_WORDS = {"動画サイト": 2005, "SNS": 2008, "配信": 2006, "ストリーミング": 2012, "サブスク": 2014, "ショート動画": 2018, "ハッシュタグ": 2010, "ネット": 1998, "ホームページ": 1996, "ブログ": 2002, "関連欄": 2008, "ガラケー": 1997, "着うた": 2002, "ボカロ": 2007, "海外の動画": 2005, "バズ": 2008, "拡散": 2008, "リール": 2018, "インディーズ": 1980, "CD": 1982, "カセット": 1968}
BRIDGE = re.compile(r"解散|活動を休止|休止す|休む|引退|区切り")
BRIDGE_TX = ["しばらくの空白があった。それでも、また音を鳴らす日が来た。", "離れていた時間を経て、ふたたび歩き出した。", "何もしない季節が過ぎ、気がつくと楽器に手が伸びていた。"]


def era_ok(tx, year):
    return all(year >= y for w, y in ERA_WORDS.items() if w in tx) and eraword.ok(tx, year)


_KN = "一二三四五六七八九十"
_CNT_RX = re.compile(r"(?<![一-龥])([二三四五六七八九])人(?=[はがでのとも全揃だ、。]|$)")
_CNT_SKIP = re.compile(r"客|観客|世代|若い|子|娘|息子|兄弟|姉妹|(?<!駆け)抜け|去|加わ|増え|減|残|新し|なくなった|人のまま|かつて|元の|二人組|三人組|がかり|ボーカル|声|男|女|仲間|DJ|顔を描")


_PART = [(r"管楽器|ホーン|吹奏", r"Tp|Tb|Sax|Hr|Fl|Cl|Tu|管"), (r"弦楽器|弦", r"Vn|Va|Vc|Cb|弦"), (r"ギター", r"Gt"), (r"MC|ラッパー", r"MC"),
         (r"歌い手|ボーカル", r"^Vo|Vo$|/Vo"), (r"演奏者|奏者", r"^(?!Vo$)"), (r"太鼓|打楽器", r"Dr|Per|太鼓")]
_PART_SKIP = re.compile(_CNT_SKIP.pattern.replace("客|観客|", ""))  # 一部の担当の人数: 客の話の文でも合わせる(編成替え・仲間の話は触らない)
_PART_RX = re.compile(r"(?<![一-龥])([一二三四五六七八九])人の(" + "|".join(p for p, _ in _PART) + ")")


def fix_count(s, n, roles=None):
    """本文の「四人は」などを実際の人数に合わせる(編成替え・客・他人の話の文は触らない)。
    「三人の管楽器」のような一部の担当の人数は、roles(担当の並び)のその担当の数に合わせる(数えられなければそのまま)"""
    if not isinstance(s, str) or not 2 <= n <= 9: return s
    def part(m):
        rx = next(r for p, r in _PART if re.fullmatch(p, m.group(2)))
        c = sum(1 for r in roles or [] if re.search(rx, str(r)))
        return (_KN[c - 1] if 1 <= c <= 9 else m.group(1)) + "人の" + m.group(2)
    if not _PART_SKIP.search(s): s = _PART_RX.sub(part, s)
    if _CNT_SKIP.search(s): return s
    out, last = [], 0
    for m in _CNT_RX.finditer(s):
        if _PART_RX.match(s, m.start()): continue  # 一部の担当の人数は上で済み
        out.append(s[last:m.start()] + _KN[n - 1] + "人"); last = m.end()
    return "".join(out) + s[last:]


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
    import realtitles; pt = {k: realtitles.fix_list(v, k) for k, v in pt.items()}  # 実在曲名そのまま(末尾の(…)を外して同じも含む)はもじりに差し替え、残りは外す
    return arcs, pt


_BPT = []
def _bank_pt():
    if not _BPT:
        try:
            import json as _j; _BPT.extend(_j.load(open('/home/claude/namebank.json', encoding='utf-8')).get('pt') or [])
        except Exception: _BPT.append("")
    return [t for t in _BPT if t]


def _nth(n): return "%d%s" % (n, "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))


def kind_of(pos): return "EP" if pos == 0 else ("アルバム" if pos % 2 else "シングル")


def ord_of(pos):
    """0=自主制作盤, 以降アルバムとシングルが交互。番号は種類ごとに数える(7thアルバムが何枚も出ないように)"""
    return "自主制作盤" if pos == 0 else _nth((pos + 1) // 2) + kind_of(pos)


def rel(a, pool, seen, pos, y, tier, th, lb, dev, era):
    r = random.Random(H(a["k"], "rel", pos, dev, era))
    ti = pool[(pos * 3 + dev * 2) % len(pool)]
    n = 0
    while (ti in seen or not eraword.ok(ti, y)) and n < len(pool): ti = pool[(pool.index(ti) + 1) % len(pool)]; n += 1
    if n >= len(pool):  # 時代に合う曲名が尽きたら、時代違いでも未使用のものを使う
        ti = next((t for t in pool if t not in seen), None)
        if ti is None:  # QA10: そのアーティストのもじりが尽きたら、汎用のもじりプールから(同じ題名を二度出さない)
            fb = [t for t in PT0.get("misc", []) + _bank_pt() if t not in seen]
            fb2 = [t for t in fb if eraword.ok(t, y)] or fb
            ti = fb2[H(a["k"], "fb", pos, dev, era) % len(fb2)] if fb2 else pool[(pos * 3 + dev * 2) % len(pool)]
    seen.append(ti)
    pr = pr_of(r, th); k = kind_of(pos)
    h = dict(kind=k, ord="", title=ti, year=y, tier=tier, theme=th, premise=pr, label=lb)
    st = a["st"] if a["st"] in ("band", "duo", "rap", "solo", "beat") else "band"
    tk = tracks.tracklist(h, st, era, th, list(seen), extra=__import__('ptover').deep(a['k'], pool, seen))
    seen.extend(x['t'] for x in tk if x['t'] not in seen)
    _ins = a["st"] == "inst"  # インストは歌詞なし(展開の構成)・ボーカルなし
    lyrics.VG = "inst" if _ins else a["vg"]
    ly = lyrics_struct.make_struct(th, a["ge"], pr, ti, y, WORDS, era <= 1, era, inst=_ins)
    if ly: ly["vg"] = "inst" if _ins else a["vg"]
    t = THEME[th]; rs = r.choice(t["hit"]) if tier >= 2 else r.choice(FLOP)
    return {"t": "r", "y": y, "o": ord_of(pos), "ti": ti, "lb": lb, "tr": tier, "pr": pr, "th": th, "rs": rs if tier < 2 else r.choice(HIT), "fm": r.choice(FORM), "tk": tk, "ly": ly}


def _bg(s):
    s = re.sub(r"[、。「」!?!?・\s]", "", s); return {s[i:i + 2] for i in range(len(s) - 1)}


def real_of(a, j):
    """分かれ道 j で本家の経歴に沿う側(0=A / 1=B)。real が無ければ A。"""
    r = a.get("real") or []
    return 1 if j < len(r) and r[j] == 1 else 0


# 本家の筋から外れた後、本家固有の転機の代わりに出す文
OFF_TX = ["選んだ道の先は、どこの地図にも載っていなかった。", "答え合わせのできない日々が続いた。それでも音は鳴らしていた。",
          "あの日の選択が、少しずつ毎日の形を変えていった。", "手探りのまま、次の作品に取りかかった。",
          "予定表は白紙のまま。それでも、音を鳴らさない日はなかった。", "誰かの真似ではない一日が、静かに積み重なっていった。",
          "正解かどうかは、まだ誰にも分からなかった。練習だけは、いつもどおり続いた。", "選ばなかった道のことは、夜中にだけ少し考えた。朝には忘れていた。",
          "小さな会場の空気が、少しずつ自分たちの音に慣れていった。", "新しい曲が一つ、机の上のノートに書き足された。", "機材車の走行距離だけが、確実に伸びていった。",
          "お客の顔ぶれが、気づけば少し入れ替わっていた。", "打ち上げの話題は、次に何を作るかに変わっていった。", "どこにも載らない日々の中で、音だけが前に進んだ。",
          "褒められもけなされもしない季節が、しばらく続いた。", "前と同じ場所に立っているのに、見える景色が違っていた。", "一曲ごとに、少しだけ遠くへ投げられるようになった。", "誰に頼まれたわけでもない作業が、朝まで続いた。"]
EV_FILL = "活動は、少しずつ、確かな形になっていった。"
OFF_EX = re.compile(r"解散|休止|脱退|再結成|再始動|メジャー|海外|上京|移籍|独立|復帰|引退")


def start_age(meta, key):
    """人生の開始年齢(既存の bio.ag。無ければ 18〜24 で決定的に)"""
    ag = (meta.get("bio") or {}).get("ag")
    return ag if isinstance(ag, int) else 18 + H(key, "age") % 7


def end_text(a, path):
    """選んだ道(path: 各分かれ道で 0=A / 1=B)に合う結末。real(本家側)と違う側を選んだ分かれ道を「外れ」とする。
    ea の各文を「どの分かれ道の別選択を書いた文か」に割り当て、実際に別選択をした分かれ道の文だけを使う。
    合う文がなければ、最後に外れた分かれ道の結果文を結末にする(選ばなかった選択を語らない)。"""
    D = a["d"]; alts = [i for i, x in enumerate(path) if i < len(D) and x != real_of(a, i)]
    if not alts: return a["eh"]
    best = None
    for e in a.get("ea") or []:
        sc = [len(_bg(e) & _bg((d[1] + d[3]) if real_of(a, j) else (d[2] + d[4]))) for j, d in enumerate(D)]
        o = max(range(len(D)), key=lambda i: sc[i]); s2 = sorted(sc)[-2] if len(sc) > 1 else 0
        if sc[o] >= 3 and sc[o] > s2 and o in alts and (best is None or o > best[0]): best = (o, e)
    if best: return best[1]
    i = alts[-1]; return D[i][3] if real_of(a, i) else D[i][4]


NEWVO = re.compile(r'新しい(?:声|ボーカル|歌い手|歌姫)を(?:迎え|入れ|探)|ボーカルを(?:替え|交代|入れ替え)|新ボーカル')
NEWVO_N = re.compile(r'守る|せず|しない|断')
# QA9: 担当の入れ替え・脱退を顔ぶれに反映するための語
PART_OF = {"ドラマー": "Dr", "ドラム": "Dr", "太鼓": "Dr", "打ち手": "Dr", "ギタリスト": "Gt", "ギター": "Gt", "ベーシスト": "Ba", "ベース": "Ba", "低音": "Ba", "キーボーディスト": "Key", "キーボード": "Key", "鍵盤": "Key", "ピアノ": "Key", "サックス": "Sax", "トランペット": "Tp", "DJ": "DJ", "ラッパー": "MC", "MC": "MC"}
PART_RX = {"Dr": re.compile(r"Dr|Per|太鼓"), "Gt": re.compile(r"Gt|ギター"), "Ba": re.compile(r"Ba|ベース"), "Key": re.compile(r"Key|Pf|Syn|鍵盤|ピアノ"), "Sax": re.compile(r"Sax"), "Tp": re.compile(r"Tp"), "DJ": re.compile(r"DJ"), "MC": re.compile(r"MC|Rap")}
NEWPART = re.compile(r"(?:新しい|若い|新たな|別の|次の)(" + "|".join(sorted(PART_OF, key=len, reverse=True)) + r")を(?:迎え|入れ|探|誘|呼)|(" + "|".join(sorted(PART_OF, key=len, reverse=True)) + r")を(?:替え|交代|入れ替え)")
LEAVE = re.compile(r"抜け|降り|離れ|辞め|やめる|やめたい|帰ってこい|帰れ|裏方|移りたい|終わりだ|専念したい|やれない|継ぐ|就職|出ていく|去る|もうできない|もう無理|限界だ|他の道|別の道|別の仕事|家業")
KEEPGO = re.compile(r"[二三四五六七八九]人(?:で|のまま|になって|に戻)|なしで続け|抜きで続け|いない(?:まま|形)で|欠けたまま|埋めずに|送り出す|見送る|引き留めない|引き止めない|残った(?:メンバー|仲間|者)で|穴を埋めず|そのまま続け")
KEEPGO_N = re.compile(r"新しい|迎え|探し|代わり|補充|入れ|引き留め(?!ない)|引き止め(?!ない)|止める|やめる|解散|幕|区切り|終わ")


# QA10: 分かれ道の問い・選択肢から、誰が抜けるか(担当名・人数)と、代わりを迎えるかを読み取って顔ぶれの出入り(mb)を決める
_LV_Q = re.compile(r"(?<!駆け)(?<!力の)(?<!力が)(?<!手を)抜け(?!ば|駆け|道|目|穴|殻|ない)|降り(?:る|たい|させ)|(?:やめ|辞め)(?:たい|る|させて)(?!てきた)|家業を継ぐ|実家(?:の仕事|の店)?を継ぐ|店を継ぐ|就職(?:する|が決まった|して|します)|会社員になる|脱退|裏方に回|(?<!しばらく)(?<!しばらく、)(?<!少し)(?<!少し、)(?<!一度)離れたい|もうできない|もう無理|限界だ|別の仕事|他の道を|別の道を|専念したい|帰ってこい|帰れ|出ていく|去る|移りたい|終わりだ|バンドを離れ|グループを離れ")
_LV_PAST = re.compile(r"(?<!駆け)(?<!力の)(?<!力が)抜け(?:た|ていった|てしまった)|脱退した|辞めた|やめた|去った|降りた|いなくなった|(?:バンド|グループ)を離れた")
_KEEP_L = re.compile(r"引き止め|引き留め|説得|残ってもら|思いとどま|止まらず|考え直|もう一度話|話し合|立て直す|全員で|誰も欠け|このメンバー|待つ|戻るのを待|休む|休み|休止|走り続け|いったん|一旦")
_DISB_L = re.compile(r"終わりにする|終える|解散|幕を引|幕を下ろ|区切りをつけ|名前を置く|やめる|辞める|それぞれの道")
_REPL_L = re.compile(r"迎え|新しい(?:仲間|メンバー|声|顔|人)|代わり|代役|補充|探す|探して|募集|誘う|正式メンバー|入れる")
_REPL_N = re.compile(r"せず|しない|探さない|補充せず|迎えず|入れず|なしで|抜きで")
_QUOTE = re.compile(r"([^。『』「」]{0,24}?)(?:が|は)(、?[^『』「」]{0,16}?)[『「]([^』」]*)[』」]")
_CNTW = {"ひとり": 1, "一人": 1, "誰か": 1, "二人": 2, "ふたり": 2, "三人": 3, "次々": 2}


def _mb_outs(mb): return ([mb["out"]] if mb and mb.get("out") else []) + list((mb or {}).get("xo") or [])
def _mb_ins(mb): return ([mb["in"]] if mb and mb.get("in") else []) + list((mb or {}).get("xi") or [])


def _roles_in(s):
    hits = sorted(((s.find(w), w) for w in PART_OF if w in s), key=lambda z: (z[0], -len(z[1])))
    out = []; used = []
    for p, w in hits:
        if any(p >= q and p < q + len(v) for q, v in used): continue
        used.append((p, w)); out.append(PART_OF[w])
    return out


def lineup_leavers(prompt):
    """問いの文から (抜ける担当のリスト, 担当が分からない人数, 既に抜けたか) を返す。誰も抜けないなら (None, 0, False)"""
    parts = []; cnt = 0; found = False
    for m_ in _QUOTE.finditer(prompt):
        who, mid, q = m_.group(1), m_.group(2), m_.group(3)
        if not _LV_Q.search(q): continue
        rs = _roles_in(who)
        if rs: parts += rs; found = True
        else:
            k = next((v for w, v in _CNTW.items() if w in who + mid), 0)
            if k or re.search(r"メンバー|仲間|一人|ひとり", who): cnt += k or 1; found = True
    outside = re.sub(r"『[^』]*』|「[^」]*」", "", prompt)
    past = bool(_LV_PAST.search(outside))
    if past:
        for s_ in re.split(r"[。、]", outside):
            if not _LV_PAST.search(s_): continue
            rs = _roles_in(s_)
            if rs: parts += rs
            else: cnt += next((v for w, v in _CNTW.items() if w in s_), 1)
            found = True
    if not found: return None, 0, False
    return parts, cnt, past


def lineup_mb(prompt, label, restx, cur, seed_, taken):
    """選んだ選択肢 label のときの顔ぶれの出入り。{out, in, xo, xi} か None"""
    parts, cnt, past = lineup_leavers(prompt)
    if parts is None:  # 問いに脱退の話がなくても「新しい声を迎える」「ドラマーを替える」なら、その担当を入れ替える
        if NEWVO.search(label) and not NEWVO_N.search(label): parts, cnt, past, label = ["Vo"], 0, False, label + " 迎え"
        else:
            mi = NEWPART.search(label)
            if mi and not NEWVO_N.search(label) and PART_OF.get(mi.group(1) or mi.group(2)): parts, cnt, past, label = [PART_OF[mi.group(1) or mi.group(2)]], 0, False, label + " 迎え"
            else: return None
    if not past and _KEEP_L.search(label): return None
    if _DISB_L.search(label) and not re.search(r"続け|迎え|探", label): return None
    repl = bool(_REPL_L.search(label)) and not _REPL_N.search(label)
    isvo = lambda m_: "Vo" in str(m_.get("r", "")) or str(m_.get("r", "")).startswith("ボーカル")
    pool = list(cur); outs = []
    def take(part):
        rx = PART_RX.get(part) or (re.compile(r"Vo|ボーカル") if part == "Vo" else None)
        if not rx: return None
        m_ = next((x for x in pool if rx.search(str(x.get("r", ""))) and not isvo(x)), None) or (next((x for x in pool if rx.search(str(x.get("r", "")))), None) if part == "Vo" or repl else None)
        if m_: pool.remove(m_); outs.append(m_)
        return m_
    for p in parts: take(p)
    if cnt:
        # 担当が分からない「ひとり」は、結果文・選択肢に出る担当(「新しい低音が加わった」)を優先し、なければボーカル以外から
        pref = _roles_in(restx + label)
        for p in pref:
            if cnt <= 0: break
            if take(p): cnt -= 1
        while cnt > 0 and pool:
            m_ = next((x for x in pool if not isvo(x)), None) or next((x for x in reversed(pool) if not str(x.get("r", "")).startswith("Vo")), None) or (pool[-1] if len(pool) >= 2 else None)  # 声だけのグループは最後の人
            if not m_: break
            pool.remove(m_); outs.append(m_); cnt -= 1
    if not outs: return None
    if not repl and len(cur) - len(outs) < 2: outs = outs[:max(0, len(cur) - 2)]
    if not outs: return None
    if not repl and all(isvo(x) for x in outs) and not any(isvo(x) for x in pool): return None  # 唯一の歌い手が抜けて代わりもいない形は出さない
    ins = []
    if repl:
        tk = set(taken) | {x["n"] for x in cur}
        for j, x in enumerate(outs):
            nw = tracks.newcomer(seed_ + j, x["r"], tk); nw["r"] = x["r"]; tk.add(nw["n"]); ins.append(nw)
    mb = {"out": outs[0]}
    if len(outs) > 1: mb["xo"] = outs[1:]
    if ins: mb["in"] = ins[0]
    if len(ins) > 1: mb["xi"] = ins[1:]
    return mb


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
            if j < len(a.get("tr", [])): m_["t"] = _ro0.trait(a["tr"][j])
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
    top = "グループ" if _ro.is_group(st, mm) else "ソロ"
    if top == "ソロ": mm = _ro.solo_side(a, st, mm, seed)  # ソロ/ボカロPの本人がメンバー一覧に別人として並ばないように
    solo_inst = st == "inst" and not roles and not (a.get('members') or _ro0.ROSTER.get(a['k']))
    if solo_inst:  # トランペット奏者など「一人の名前」のインスト: 本人+バックの奏者(Gt/Gt/Ba/Drのバンドにしない)
        lead = next((v for w, v in (("トランペット", "Tp"), ("サックス", "Sax"), ("ピアノ", "Pf"), ("ギター", "Gt"), ("ベース", "Ba"), ("ドラム", "Dr")) if w in a["tx"]), "Gt")
        back = [r_ for r_ in ("Pf", "Ba", "Dr", "Gt") if r_ != lead][:3]
        mm = [dict(m_, r="サポート" + {"Pf": "ピアノ", "Ba": "ベース", "Dr": "ドラム", "Gt": "ギター"}[r_]) for m_, r_ in zip(tracks.people(seed, "band"), back)]
        top = "ソロ"
    E = g.ERAS[era]
    name = nm or a["nm"]
    meta = {"id": seed, "a": name, "pun": None, "top": top, "st": st if st != "dj" else "solo", "sn": STN.get(st, "シンガーソングライター"), "pe": ["まじめ", "明るい", "頑固", "気分屋", "人たらし", "繊細", "天然", "野心家", "まじめ", "暗い"][H(a["k"], "pe") % 10], "era": era, "en": E["name"], "es": E["short"], "sa": a["sa"], "ge": a["ge"],
            "tx": a["tx"], "ai": None, "mm": mm, "vg": "inst" if st == "inst" else a["vg"], "bio": bio.make(seed, st if st != "dj" else "solo", era, None, top == "グループ", year=y0), "real": True, "histTx": a["eh"], "cp": a.get("cp", [])}
    bio.localize(a, meta["bio"], mm, seed)  # 出身地・結成地を国と「始まりの場所」に合わせる
    _mc = _ro.lineup(a, mm) if top == "グループ" else []  # 元ネタの結成時メンバーに。後年の加入・脱退は年で転機に差し込む(下の lineup_tree)
    if solo_inst: meta["sn"] = "インスト奏者"
    if st == "rap" and top == "グループ": meta["sn"] = "ヒップホップグループ"
    th = a["th"]; D = a["d"]; N = len(D); cv = a["cv"]; ev = list(a["ev"]); ex = list(a.get("ex") or [])
    _yy = y0 + 2
    ex = [x for x in ex if era_ok(x, _yy)]
    ev = [x if era_ok(x, _yy) else EV_FILL for x in ev]
    if st == "beat" and y0 >= 2016:  # 配信時代のボカロP・トラックメイカーに「CDにして売るか」は出さない
        _cd = lambda z: re.sub(r"CD(にして|として)売", "有料で配信して売", z).replace("CDを出し", "有料配信で出し").replace("CDを", "音源を") if isinstance(z, str) else z
        ev = [_cd(x) for x in ev]; ex = [_cd(x) for x in ex]; D = [tuple(_cd(z) for z in d_) for d_ in D]
    if top == "グループ":  # 人数語を実際のメンバー数に
        _n = len(mm); _rl = [x.get("r") for x in mm]; ev = [fix_count(x, _n, _rl) for x in ev]; ex = [fix_count(x, _n, _rl) for x in ex]; meta["histTx"] = fix_count(meta["histTx"], _n, _rl)
        D = [tuple(fix_count(z, _n, _rl) if j_ < 3 else z for j_, z in enumerate(d_)) for d_ in D]  # 結果文(3,4)は X() で出入り後の人数に合わせる
    _b = meta["bio"]  # 出来事・紹介文の地名語(古都・津軽・港町など)が出身・結成地に合わなければ地名を外す
    ev = [bio.fit_text(x, _b) for x in ev]; ex = [bio.fit_text(x, _b) for x in ex]; D = [tuple(bio.fit_text(z, _b) for z in d_) for d_ in D]
    meta["histTx"] = bio.fit_text(meta["histTx"], _b); meta["sa"] = bio.fit_text(meta["sa"], _b); meta["tx"] = bio.fit_text(meta["tx"], _b)
    rr = random.Random(H(a["k"], "ex", era)); rr.shuffle(ex)
    counter = [0]

    # QA10: 「メジャーへ進む」の分かれ道より前の作品に「メジャー」の看板を付けない(メジャー1stが分かれ道より先に出ないように)。断った側の後の作品も同じ
    MJ_L = re.compile(r"メジャー(?:へ|に)(?:進|行|出|移|挑|乗)|メジャーで|メジャーと契約|メジャー契約|メジャーデビュー|大きなレーベル|大手(?:と|に|の)|メジャーの話を受け")
    MJ_N = re.compile(r"断|残る|せず|しない|のまま|自主|インディーズ|様子を見")
    _mj = [(j_, (0 if (MJ_L.search(d_[1]) and not MJ_N.search(d_[1])) else 1)) for j_, d_ in enumerate(D) if any(MJ_L.search(d_[s_]) and not MJ_N.search(d_[s_]) for s_ in (1, 2))]
    jM = _mj[0][0] if _mj else None; sideM = _mj[0][1] if _mj else None

    def stage(si, eff, dv, seen, path=()):
        out = []
        lb_ = a["lb"][min(si, len(a["lb"]) - 1)]
        if jM is not None and "メジャー" in lb_:
            if si <= jM: lb_ = "インディーズ"
            elif len(path) > jM and path[jM] != sideM and not any(j2 > jM and j2 < len(path) and path[j2] == s2 for j2, s2 in _mj[1:]): lb_ = "インディーズ"
        for k, bt in enumerate(cv[min(si, len(cv) - 1)]):
            pos = counter[0] + k
            y = y0 + a["yr"][min(pos, len(a["yr"]) - 1)]
            out.append(rel(a, pool, seen, pos, y, cl(bt + eff), th[(pos + dv) % len(th)], lb_, dv, era))
        return out

    def evs(si, off=False, path=()):
        """off: 本家の筋から外れた後。本家固有の転機(ev)は出さず中立の文にし、出さなかった ev を返す"""
        e0 = ev[min(si, len(ev) - 1)]
        if off:
            o = [{"t": "e", "tx": OFF_TX[(H(a["k"], "off", path[:1], era) + si * 5) % len(OFF_TX)], "fl": 1}]  # QA10: つなぎ文は人生ごとに違う組み合わせ(1人生に同じ文は1回まで)
            xs = [x_ for x_ in ex if not OFF_EX.search(x_)]
        else:
            o = [{"t": "e", "tx": e0}]; xs = ex
        if xs and si >= 1: o.append({"t": "e", "tx": xs[(si - 1) % len(xs)]})
        return o, ([e0] if off else [])

    def X(d, alt, gone=()):
        o = {"t": "x", "c": d[2] if alt else d[1], "ok": (d[6] if alt else d[5]) >= 0, "tx": d[4] if alt else d[3]}
        if top != "グループ": return o
        cur = [m_ for m_ in mm if m_["n"] not in gone]
        mb = lineup_mb(d[0], o["c"], o["tx"], cur, seed + 91 + len(gone), {m_["n"] for m_ in mm})
        if mb: o["mb"] = mb
        # QA10: 結果文の人数語は、出入りのあとの人数に合わせる(「三人で続けた」が四人にならないように)
        n2 = len(cur) - len(_mb_outs(mb)) + len(_mb_ins(mb))
        rl2 = [m_.get("r") for m_ in cur if m_["n"] not in {x["n"] for x in _mb_outs(mb)}] + [x.get("r") for x in _mb_ins(mb)]
        o["tx"] = fix_count(o["tx"], n2, rl2)
        if mb and mb.get("out") and not mb.get("in"):
            o["c"] = re.sub(r"(?<![一-龥])[二三四五六七八九]人(?=で|のまま|になって|に戻)", _KN[n2 - 1] + "人", o["c"])
        return o

    ag0 = start_age(meta, a["k"])

    def q(d, works):
        # 年齢はリーダー/ボーカル(=bio)の、問いの直前の作品の年での年齢
        y = works[-1]["y"] if works else y0
        fy = works[0]["y"] if works else y0
        return {"prompt": "%d歳。" % (ag0 + max(0, y - fy)) + d[0], "labels": [d[1], d[2]], "h": 0}

    def node(si, eff, dv, seen, pos0, prior_works, path=(), off=False, hon=(), hc=(), gone=()):
        # si: 次に控える分かれ道の番号。この関数が返すのは「分かれ道siの子ノード群」
        kids = []
        for x in (0, 1):
            sn = copy.deepcopy(seen); counter[0] = pos0
            e2 = eff + D[si][6 if x else 5]; dv2 = dv + x
            lab_ = D[si][2 if x else 1]
            dev = x != real_of(a, si); off2 = off or dev
            hc2 = hc + ((D[si][2 if real_of(a, si) else 1],) if dev else ())
            ev_, miss = evs(si + 1, off2, path + (x,))
            x0 = X(D[si], x, gone); gone2 = gone + tuple(x["n"] for x in _mb_outs(x0.get("mb")))
            seg = [x0] + ([{"t": "e", "tx": BRIDGE_TX[(si + x) % len(BRIDGE_TX)]}] if BRIDGE.search(lab_) else []) + ev_ + stage(si + 1, e2, dv2, sn, path + (x,))
            hon2 = hon + tuple(miss)
            pos1 = pos0 + len(cv[min(si + 1, len(cv) - 1)])
            works = prior_works + [w for w in seg if w["t"] == "r"]
            if si + 1 < N:
                kids.append({"s": seg, "q": q(D[si + 1], works), "n": node(si + 1, e2, dv2, sn, pos1, works, path + (x,), off2, hon2, hc2, gone2)})
            else:
                tx = end_text(a, path + (x,))
                if top == "グループ": tx = fix_count(tx, len(mm), [x.get("r") for x in mm])
                tx = bio.fit_text(tx, meta["bio"])
                e_ = {"tx": tx.rstrip("。"), "w": [wk(w) for w in works], "mm": mm}
                if off2:  # 本家の道: 外れた分かれ道で本家が選んだ側(hc)と、出なかった本家の転機(hon)。本家の結末は m.histTx
                    e_["hon"] = [h_ for h_ in dict.fromkeys(hon2) if h_ != EV_FILL]; e_["hc"] = list(hc2)
                kids.append({"s": seg, "e": e_})
        return kids

    seen0 = []; counter[0] = 0
    s0 = evs(0)[0][:1] + stage(0, 0, 0, seen0)
    pos1 = len(cv[0]); w0 = [w for w in s0 if w["t"] == "r"]
    tree = {"s": s0, "q": q(D[0], w0), "n": node(0, 0, 0, seen0, pos1, w0)}
    cap_fives(tree)
    if _mc: _ro.lineup_tree(tree, mm, [(y_ - a["y0"] + y0, k_, m_, t_) for y_, k_, m_, t_ in _mc])
    return {"m": meta, "t": tree}


def build_all(dirpath='/home/claude/arcs_new', variants=True):
    arcs, pt = load_specs(dirpath); out = []
    for i, a in enumerate(arcs):
        try:
            pool = pt.get(a["par"]) or PT0.get(a["par"]) or PT0["misc"]
            pool = list(dict.fromkeys(pool))
            out.append(build(a, i, pool))
            if variants:
                real_era = era_of(a["y0"]); alts = [e for e in a.get("eras", []) if e != real_era and e in ERA_Y]
                names = a.get("alt") or []
                for vi, e in enumerate(alts[:2]):
                    if vi < len(names): out.append(build(a, i, pool, era=e, nm=names[vi]))
        except Exception as ex:
            print('BUILD FAIL', a.get("k"), repr(ex))
    return out
