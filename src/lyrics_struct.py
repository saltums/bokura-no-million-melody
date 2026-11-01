# -*- coding: utf-8 -*-
"""曲の構成パターン(王道・サビだけ・語りだけ・歌詞なし...)。make_struct が構成名・節の並び・AI用タグを返す。"""
import random
import lyrics as L
import eraword
from lyrics_extra import EXTRA, ERA_SCENE, FAMILY_SCENE, FAMILY_HOOK_SUFFIX

EN = ["I'm still here", "One more night", "Don't let go", "Tell me why", "We're alive", "Say it again", "Just let it burn", "Hold on"]
KANSUU = ["ひとつ", "ふたつ", "みっつ", "よっつ", "いつつ", "むっつ"]

# (key, 表示名, 重み)
KINDS = [("full", "王道(1番・2番・Cメロ)", 34), ("chorus_only", "サビだけ", 9), ("sabi_start", "サビ始まり", 8), ("one_line", "ひとつの言葉のくり返し", 5),
         ("spoken", "語りだけ(歌わない)", 6), ("instr", "歌詞なし(ハミングだけ)", 4), ("chant", "曲名の連呼", 4), ("count", "数え歌", 4),
         ("letter", "手紙の形", 4), ("dialog", "会話の形(掛け合い)", 5), ("reverse", "終わりから始まる", 3), ("silence", "無音をはさむ", 3),
         ("bilingual", "日英ちゃんぽん", 4), ("noise", "ノイズと一言だけ", 2), ("medley", "途中で曲調が変わる組曲", 3), ("voices", "語り手がどんどん変わる", 3),
         ("call", "コール&レスポンス", 3)]
NAME = {k: n for k, n, w in KINDS}


def _ctx(theme, genre, premise, title, year, words, era, seed_tag):
    bank = L.B[theme]; ex = EXTRA.get(theme, {})
    _gl = L.gen_vocab.lines(theme, random.Random(L._seed(title, year, theme, "gv")), 16)
    _gr = L.lyr_rich.lines(theme, L.family(genre), random.Random(L._seed(title, year, theme, "gr")), 24)
    A = bank["a"] + ex.get("a", []) + _gl["a"] + _gr["a"]; Bb = bank["b"] + ex.get("b", []) + _gl["b"] + _gr["b"]; H = bank["h"] + ex.get("h", []) + _gl["h"] + _gr["h"]; C = ex.get("c", []) + _gl["c"] + _gr["c"]
    r = random.Random(L._seed(title, year, theme, seed_tag))
    TIME, PLACE, THING = words
    t0, p0, x0 = L._pick_words(premise, *words)
    t = t0 or r.choice(TIME); p = p0 or r.choice(PLACE); x = x0 or r.choice(THING)
    if not eraword.ok(t, year): t = r.choice([z for z in TIME if eraword.ok(z, year)] or TIME)
    if not eraword.ok(p, year): p = r.choice([z for z in PLACE if eraword.ok(z, year)] or PLACE)
    if not eraword.ok(x, year): x = r.choice([z for z in THING if eraword.ok(z, year)] or THING)
    fam = L.family(genre)
    me0 = L.pick_me(fam, r)
    bad = ("SNS", "いいね", "タイムライン", "スマホ", "画面", "ペンライト", "ライブ配信", "メッセージ", "返信", "炎上", "通知", "既読")
    old = ("ケータイ", "メール", "ネット", "MD", "iPod", "サブスク", "動画", "アルゴリズム")
    ok = lambda z: not ((era <= 2 and any(k in z for k in bad)) or (era <= 1 and any(k in z for k in old))) and eraword.ok(z, year)
    Af = [z for z in A if ok(z)] or bank["a"]; Bf = [z for z in Bb if ok(z)] or bank["b"]
    S = [z for z in (list(ERA_SCENE.get(era, [])) + (list(FAMILY_SCENE[fam]) if fam else [])) if ok(z)]
    H = [z for z in H if ok(z)] or bank["h"]; C = [z for z in C if ok(z)] or C  # サビ・Cメロも時代違いの語を除く
    return dict(r=r, A=Af, B=Bf, H=H, C=C, S=S, t=t, p=p, x=x, fam=fam, me=me0, suf=FAMILY_HOOK_SUFFIX.get(fam, ""))


PATTERNS = [
    ("静→轟音→余韻", [("Intro", "Intro - quiet clean guitar arpeggio, sparse", "静かなクリーンギターの導入", "ゆっくり音数が増えていく"),
                  ("Build", "Build - layered guitars, crescendo, drums enter", "ドラムが入り、ギターが重なっていく", "じわじわ熱が上がる"),
                  ("Climax", "Climax - wall of distorted guitars, full band, huge", "轟音の壁。バンド全員が全力", "ここがこの曲の山"),
                  ("Outro", "Outro - fading feedback, ringing guitars", "フィードバックが鳴り響いて消えていく", "余韻")]),
    ("いきなり轟音", [("Climax", "Intro - full band hits immediately, loud and heavy", "冒頭から轟音。説明なしで始まる", "息つく暇がない"),
                  ("Break", "Break - drops to bass and drums only, tense", "ベースとドラムだけに落ちる", "嵐の前の静けさ"),
                  ("Climax2", "Final Climax - all instruments return, even bigger", "全楽器が戻ってくる。さらに大きく", "最後の山"),
                  ("Outro", "Outro - abrupt stop", "ぶつっと止まる", "余韻なし")]),
    ("ひたすら反復", [("Loop", "Intro - repeating guitar riff, hypnotic, minimal", "短いリフを延々くり返す", "少しずつ音を足す"),
                  ("Swell", "Build - same riff, gradually louder and denser", "同じリフのまま、音量と密度だけが増える", "気づくと大音量"),
                  ("Climax", "Climax - riff at full volume with crashing cymbals", "最大音量。シンバルが崩れ落ちる", "トランス状態"),
                  ("Outro", "Outro - riff fades out slowly", "リフがゆっくり遠ざかる", "")]),
    ("組曲(3部)", [("P1", "Part 1 - acoustic guitar, gentle, intimate", "第1部 アコースティックの静かな始まり", ""),
                 ("P2", "Part 2 - heavy distorted riff, driving drums, fast", "第2部 一転して重いリフと疾走", "テンポが変わる"),
                 ("P3", "Part 3 - slow, spacious, ambient guitars and piano", "第3部 広がりのあるゆったりした終章", "")]),
    ("短いインスト", [("Climax", "Short instrumental - tight riff, drums and bass, energetic, 40 seconds", "短くタイトに駆け抜ける", "30〜40秒で終わる"),
                  ("Outro", "Outro - single final chord rings out", "最後の一音を鳴らして終わる", "")]),
    ("静かなままで", [("Intro", "Intro - soft tremolo guitar, reverb, calm", "トレモロの静かなギター", ""),
                  ("Build", "Middle - slow bass line and brushed drums, gentle swell", "ゆっくりしたベースとブラシのドラム", "あくまで静か"),
                  ("Outro", "Outro - quiet ending, no climax", "盛り上がらないまま終わる", "あえて山場なし")]),
]


LAB = {"Intro": "導入", "Build": "展開", "Climax": "山場", "Climax2": "最後の山場", "Break": "間", "Outro": "終わり", "Loop": "導入", "Swell": "展開", "P1": "第1部", "P2": "第2部", "P3": "第3部"}


def inst_struct(theme, genre, premise, title, year, words, era):
    c = _ctx(theme, genre, premise, title, year, words, era, "inst")
    r = c["r"]
    name, secs = r.choice(PATTERNS)
    scene = c["S"][0] if c["S"] else ""
    s = {}; o = []
    for i, (k, en, ja, note) in enumerate(secs):
        lines = [ja]
        if note: lines.append("(" + note + ")")
        if i == 0: lines.append("曲の情景:" + premise.replace("描く歌", "描く曲").rstrip("。"))
        s[k] = lines
        o.append([k, LAB.get(k, k), en, 1 if "Climax" in k else 0])
    n1 = len(o)
    tg = "instrumental, no vocals, no lyrics, loud guitar-driven band"
    return {"st": "インスト(" + name + ")", "k": "inst", "s": s, "o": o, "n1": n1, "h": premise.replace("描く歌", "描く曲"), "hl": "山場", "tg": tg}


def make_struct(theme, genre, premise, title, year, words, early, era=2, inst=False):
    if theme not in L.B:
        return None
    if inst:
        return inst_struct(theme, genre, premise, title, year, words, era)
    c = _ctx(theme, genre, premise, title, year, words, era, "struct")
    r = c["r"]
    kind = r.choices([k for k, _, _ in KINDS], [w for _, _, w in KINDS])[0]
    fam = c["fam"]; sab = "バース" if fam == "rap" else "サビ"
    fmt = lambda s, me=None: s.format(t=c["t"], p=c["p"], x=c["x"], me=me or c["me"])
    pickn = lambda pool, n: r.sample(pool, min(n, len(pool)))
    pa = [fmt(z) for z in pickn(c["A"], 5)]; pb = [fmt(z) for z in pickn(c["B"], 3)]
    ph = [fmt(z) for z in pickn(c["H"], 8)]
    while len(ph) < 8: ph.append(ph[len(ph) - 4])
    pc = [fmt(z) for z in pickn(c["C"], 2)] if c["C"] else pa[3:5]
    hook = ph[3].rstrip("。") + c["suf"] if c["suf"] else ph[3]
    scene = fmt(r.choice(c["S"])) if c["S"] else pa[0]
    SB = lambda k, lab, tag, hit=0: [k, lab, tag, hit]
    s = {}; o = []; n1 = 3; tg = ""
    if kind == "full":
        f = L.make_full(theme, genre, premise, title, year, words, early, era)
        s = f["s"]; hook = f["h"]
        o = [SB("A1", "1番 Aメロ", "Verse"), SB("B1", "Bメロ", "Pre-Chorus"), SB("S", sab, "Chorus", 1), SB("A2", "2番 Aメロ", "Verse"), SB("B2", "Bメロ", "Pre-Chorus"),
             SB("Sb", sab, "Chorus", 1), SB("C", "Cメロ", "Bridge"), SB("S2", "最後の" + sab, "Chorus", 1)]
        o = [e for e in o if e[0] in s]
    elif kind == "chorus_only":
        s = {"S": [ph[0], ph[1], ph[2], hook], "Sb": [ph[3], ph[4], ph[5], hook], "S2": [ph[6], ph[0], ph[1], hook, hook]}
        o = [SB("S", sab, "Chorus", 1), SB("Sb", sab, "Chorus", 1), SB("S2", "最後の" + sab, "Chorus", 1)]; n1 = 2
        tg = "chorus-only song, no verses, catchy hook from the first second, about 30 seconds"
    elif kind == "sabi_start":
        s = {"S": [ph[0], ph[1], hook], "A1": [scene, pa[1]], "B1": [pb[0]], "S2": [ph[2], ph[3], ph[4], hook]}
        o = [SB("S", "いきなり" + sab, "Chorus", 1), SB("A1", "Aメロ", "Verse"), SB("B1", "Bメロ", "Pre-Chorus"), SB("S2", sab, "Chorus", 1)]; n1 = 4
        tg = "starts with the chorus immediately, no intro"
    elif kind == "one_line":
        v = [hook, hook + "、", hook, hook + "…", hook, hook + "!"]
        s = {"M": v[:4] + [ph[0]] + v[4:]}
        o = [SB("M", "ひとつの言葉", "Chorus", 1)]; n1 = 1
        tg = "hypnotic, single repeated line, minimalist arrangement"
    elif kind == "spoken":
        s = {"P": [pa[0], pa[1], pb[0], pb[1], pc[0], hook]}
        o = [SB("P", "語り", "Spoken Word", 0)]; n1 = 1
        tg = "spoken word, no singing, minimal backing, intimate"
    elif kind == "instr":
        s = {"I": ["♪ ラ ラ ラ ……(ハミング)", "(歌詞はありません)", "曲の情景:" + premise]}
        o = [SB("I", "ハミングだけ", "Instrumental", 0)]; n1 = 1; hook = premise
        tg = "instrumental with wordless humming, no lyrics"
    elif kind == "chant":
        ti = title
        s = {"M": [ti + "、" + ti, ti + "!", "ねえ、" + ti, pa[0], ti + "、" + ti, hook]}
        o = [SB("M", "曲名の連呼", "Chorus", 1)]; n1 = 1
        tg = "chanting the song title repeatedly, shouty, repetitive"
    elif kind == "count":
        lines = [KANSUU[0] + "、" + pa[0], KANSUU[1] + "、" + pa[1], KANSUU[2] + "、" + pb[0], KANSUU[3] + "、" + pb[1], KANSUU[4] + "、" + ph[0], "そして、" + hook]
        s = {"M": lines}; o = [SB("M", "数え歌", "Verse", 0)]; n1 = 1
        tg = "counting song, playful, simple melody"
    elif kind == "letter":
        s = {"L": ["拝啓、" + c["t"] + "の" + c["p"] + "より。", pa[0], pb[0], "追伸 ― " + hook, "敬具"]}
        o = [SB("L", "手紙", "Spoken Word", 0)]; n1 = 1
        tg = "letter reading, spoken then softly sung, piano"
    elif kind == "dialog":
        me2 = "僕" if c["me"] != "僕" else "私"
        lines = [c["me"] + "「" + pa[0] + "」", "君「" + pb[0] + "」", c["me"] + "「" + pa[1] + "」", "君「" + ph[0] + "」", "二人「" + hook + "」"]
        s = {"M": lines}; o = [SB("M", "掛け合い", "Verse", 0)]; n1 = 1
        tg = "call-and-answer duet, two voices"
    elif kind == "reverse":
        f = L.make_full(theme, genre, premise, title, year, words, early, era)["s"]
        s = {"S": f["S"], "B1": f["B1"], "A1": f["A1"]}
        o = [SB("S", "終わり(サビ)", "Chorus", 1), SB("B1", "さかのぼる", "Pre-Chorus"), SB("A1", "はじまり", "Verse")]; hook = f["S"][-1]
        tg = "reverse structure, begins with the climax and unwinds"
    elif kind == "silence":
        s = {"A1": [pa[0], pa[1]], "G1": ["(無音 8秒)"], "S": [ph[0], ph[1], ph[2], hook], "G2": ["(無音)"]}
        o = [SB("A1", "Aメロ", "Verse"), SB("G1", "間", "Silence"), SB("S", sab, "Chorus", 1), SB("G2", "間", "Silence")]; n1 = 4
        tg = "long silent gaps, sparse, dynamic contrast"
    elif kind == "bilingual":
        en = pickn(EN, 3)
        s = {"A1": [pa[0], en[0], pa[1]], "B1": [pb[0], en[1]], "S": [ph[0], ph[1], hook, en[2]]}
        o = [SB("A1", "Aメロ", "Verse"), SB("B1", "Bメロ", "Pre-Chorus"), SB("S", sab, "Chorus", 1)]
        tg = "bilingual Japanese and English lyrics"
    elif kind == "noise":
        s = {"N": ["(ノイズ)", hook, "(ノイズ)"]}
        o = [SB("N", "ノイズと一言", "Noise", 1)]; n1 = 1
        tg = "wall of noise and distortion, only one sung line"
    elif kind == "medley":
        s = {"P1": [pa[0], pb[0]], "P2": [ph[0], ph[1], ph[2], hook], "P3": [pc[0]]}
        o = [SB("P1", "第1部 弾き語り", "Intro", 0), SB("P2", "第2部 轟音", "Chorus", 1), SB("P3", "第3部 静寂", "Outro", 0)]; n1 = 3
        tg = "multi-part suite, acoustic opening, loud middle, quiet ending, tempo changes"
    elif kind == "voices":
        pron = r.sample(["僕", "私", "俺", "あたし", "うち", "ぼく", "おれ"], 3)
        raw = lambda pool: r.choice(pool)
        s = {"A1": [fmt(raw(c["A"]), pron[0]), fmt(raw(c["A"]), pron[0])], "B1": [fmt(raw(c["B"]), pron[1])], "S": [fmt(raw(c["H"]), pron[2]), fmt(raw(c["H"]), pron[2]), fmt(raw(c["H"]), pron[2]), hook]}
        o = [SB("A1", "語り手A(" + pron[0] + ")", "Verse"), SB("B1", "語り手B(" + pron[1] + ")", "Pre-Chorus"), SB("S", "語り手C(" + pron[2] + ")", "Chorus", 1)]
        tg = "different singers trade verses, shifting perspectives"
    elif kind == "call":
        s = {"S": [hook, "(客)ヘイ!", ph[0], "(客)ヘイ!", hook, "(客)ヘイ!ヘイ!"]}
        o = [SB("S", "コール&レスポンス", "Chorus", 1)]; n1 = 1
        tg = "call and response with crowd shouts, live feel"
    return {"st": NAME[kind], "k": kind, "s": s, "o": o, "n1": n1, "h": hook, "hl": sab, "tg": tg}
