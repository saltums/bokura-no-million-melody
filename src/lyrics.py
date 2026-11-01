# -*- coding: utf-8 -*-
"""歌詞の一節を作る(すべて新規の文言)。テーマごとの行バンクから、作品IDで決定的に選ぶ。
{t}=時間 {p}=場所 {x}=小物 {me}=一人称"""
import random
import gen_vocab, lyr_rich, hashlib, eraword
from lyrics_extra import EXTRA, ERA_SCENE, FAMILY_SCENE, FAMILY_HOOK_SUFFIX

B = {
"失恋": dict(
  a=["{t}の{p}で、まだ{x}を捨てられない", "最後の手紙だけが、引き出しに残ってる", "同じ曲を聴いても、もう同じ顔はできない"],
  b=["おやすみの一言が、いちばん遠くなった", "{me}ばかりが、あの日に住んでいる", "返事のないまま、季節だけが進んだ"],
  h=["好きだったのは、{me}のほうだけでよかった", "さよならより先に、朝が来てしまう", "忘れたふりが、上手になっていく"]),
"応援歌": dict(
  a=["{t}の{p}、肩で息をしている君へ", "ポケットの{x}は、まだ捨てなくていい", "転んだ数だけ、靴の跡がついてる"],
  b=["うまくいかない日も、一日には変わりない", "誰も見ていなくても、今日は走った", "{me}だって、さっきまで下を向いていた"],
  h=["もう一回だけ、あと一歩だけ", "ここから先は、君の足で行け", "夜が明けるまで、止まらなくていい"]),
"上京と故郷": dict(
  a=["{p}で見送った背中が、小さくなった", "{x}ひとつ持って、知らない街に着いた", "電話の向こうの声が、少し老けていた"],
  b=["帰る場所があるから、帰れないでいる", "方言だけが、ポケットに残っていた", "{t}になると、{p}の匂いを思い出す"],
  h=["ここで勝ってから、笑って帰るよ", "ふるさとは、いつも片道切符の向こう", "{me}の名前を、呼んでくれた町へ"]),
"家族への感謝": dict(
  a=["台所の灯りが、{t}までついていた", "{x}の古い傷は、あの日のまま", "小言の数だけ、愛されていたと知った"],
  b=["ありがとうを、言いそびれたまま大人になった", "背中が思ったより小さくて、目をそらした", "{me}の好物を、まだ覚えていてくれた"],
  h=["ただいまを言える場所が、ここにある", "ありがとうは、まだ言い足りない", "あなたの子でよかったと、今は思う"]),
"社会への怒り": dict(
  a=["{t}の{p}で、誰かが静かに潰れていく", "声の大きい方が、正しいことになる", "数字にならない人間は、そこにいないことになる"],
  b=["黙っていることが、賛成にされていく", "{me}は、{x}を投げる代わりに歌う", "笑ってみせたら、それで終わりだと思ったか"],
  h=["おかしいものを、おかしいと言う", "この声は、お前らの耳のためじゃない", "従わない夜が、いちばん明るい"]),
"日常のぼやき": dict(
  a=["{t}の{p}で、ただぼんやりしている", "冷蔵庫の中身が、今日の全てだった", "{x}をなくして、一日が終わった"],
  b=["大事件は起きない、それがいちばん困る", "{me}の予定は、昼寝と洗濯くらい", "天気がよすぎて、少し腹が立った"],
  h=["今日もなにもなかった、よかったね", "どうでもいい日々に、どうでもいい歌を", "あしたも、たぶんこんな感じ"]),
"夏と青春": dict(
  a=["{t}の{p}、自転車で追いかけた背中", "{x}を振り回して、笑って転んだ", "サイダーの泡みたいに、一日が消えていく"],
  b=["あのころは、終わりがあるなんて知らなかった", "{me}たちだけの夏が、確かにあった", "汗も涙も、区別がつかなかった"],
  h=["夏はまた来るけど、あの夏は戻らない", "どこまでも行けると、本気で思ってた", "ずっと終わらない気がしていた、あの日"]),
"孤独と夜": dict(
  a=["{t}、{p}の灯りだけがついている", "眠れないのは、{me}だけじゃないと思いたい", "{x}の影が、壁で長くなった"],
  b=["誰にも言えないことを、空に預けた", "静かすぎて、自分の鼓動が聞こえる", "明かりを消すと、少しだけ楽になる"],
  h=["ひとりでいる夜を、ひとりで歌おう", "朝が来るまで、ここにいるよ", "この静けさは、誰のものでもない"]),
"喪失と再生": dict(
  a=["{p}に残った{x}を、ようやく片づけた", "{t}の風が、少しだけ優しくなった", "泣き方を忘れるくらい、時間が過ぎた"],
  b=["失ったものの形を、{me}はまだ覚えている", "終わりだと思った場所に、芽が出ていた", "空いたところに、新しい朝が入ってくる"],
  h=["失くしたぶんだけ、強くなくていい", "もう一度、ここから始めてもいい", "痛みごと連れて、歩いていく"]),
"自己否定と肯定": dict(
  a=["鏡の中の{me}が、こっちを睨んでる", "{t}の{p}で、自分の悪口を数えていた", "{x}みたいに、役に立たない夜がある"],
  b=["比べるたびに、{me}は小さくなった", "ダメな日も、{me}の一日に違いなかった", "好きになれなくても、嫌いきらなくていい"],
  h=["こんな{me}でも、まだ息をしている", "ありのままは無理でも、そのままでいい", "それでも明日を、迎えにいこう"]),
"地元愛": dict(
  a=["{p}を曲がれば、いつもの匂いがした", "{t}の{p}、顔なじみが手を振る", "地図に載らない町が、{me}の全部だった"],
  b=["何もない町だと、言われるたびに笑った", "{x}ひとつにも、思い出が貼りついてる", "出ていった奴も、ここの空を覚えてる"],
  h=["おれたちの町を、おれたちが歌う", "ここが世界の真ん中だと言い張る", "どこへ行っても、この町の人間だ"]),
"恋のはじまり": dict(
  a=["{t}の{p}で、目が合ってしまった", "{x}を渡す手が、少し震えていた", "名前を呼ぶだけで、世界が少し変わった"],
  b=["まだ何も始まっていないのに、胸が忙しい", "{me}の知らない顔を、もっと見たくなる", "連絡先を聞くだけで、一日使い果たした"],
  h=["これが恋なら、もう戻れない", "好きって言う前から、好きだった", "はじまりの音が、胸で鳴っている"]),
"時代風刺": dict(
  a=["みんな同じ顔で、同じ流行を着ている", "{t}の{p}、誰かが正義を売っている", "便利になるほど、{me}たちは忙しくなる"],
  b=["流れに乗れなきゃ、居場所がないらしい", "叩く手だけが、いつも早く動く", "{x}みたいに、時代は使い捨てられる"],
  h=["笑えないなら、いっそ笑い飛ばそう", "この世は、よくできた冗談だ", "流されて、流されて、どこへ行く"]),
"ナンセンスと言葉遊び": dict(
  a=["{x}が{p}で、踊りだしました", "{t}にカレーを煮込む、理由はまだない", "あいうえおの順に、世界が崩れていく"],
  b=["意味はいらない、リズムがあればいい", "{me}は今日、{x}の親戚になった", "ことばの裏の裏は、表のとなり"],
  h=["ナンセンスで、いいじゃないか", "とんとんとん、と、言ってみる", "意味がなくて、最高だ"]),
"人工物への違和感": dict(
  a=["完璧な声が、{t}の部屋に響いている", "{x}の中で、誰かの真似が育っている", "正しさだけでできた歌に、体温はなかった"],
  b=["作られたものを、{me}は愛せるだろうか", "指先の迷いが、いちばん人間らしい", "出力される優しさに、返事を書けない"],
  h=["機械の夢にも、揺らぎはあるのか", "本物か偽物か、決めないで聴いて", "人間らしさって、何でできてる"]),
"推しとファンへの手紙": dict(
  a=["画面の向こうの君に、{t}は届くだろうか", "{x}を握って、ステージの光を見ていた", "名前を呼ばれた{p}の景色を、忘れない"],
  b=["{me}の毎日は、君の更新で回っている", "声援の数だけ、明日が増えていった", "会えない時間も、同じ空の下にいる"],
  h=["君がいたから、ここまで来られた", "ありがとうは、ステージの上から", "ずっと一緒に、夢を見よう"]),
"お金と仕事": dict(
  a=["{t}の{p}、領収書の山に埋もれている", "{x}より重いのは、月末の請求書だった", "好きなことを仕事にしたら、好きじゃなくなった"],
  b=["夢で飯は食えないが、飯だけで夢は育たない", "{me}の時給は、いくらで売れる", "締切と家賃が、交互にやってくる"],
  h=["稼げなくても、歌わずにいられない", "安い夢を、高く売ってやる", "働いて、歌って、また働く"]),
"旅立ちと別れの春": dict(
  a=["{p}の桜が、{t}を待たずに散った", "{x}を詰めた鞄が、ひどく軽かった", "最後の日は、いつも普通に始まる"],
  b=["またねと言うのが、いちばん難しかった", "{me}たちは、それぞれの道に分かれた", "約束だけが、手のひらに残った"],
  h=["さよならは、始まりの別の呼び方", "春が来るたび、思い出してくれ", "それぞれの空で、また会おう"]),
}

RAP = ("ラップ", "ヒップホップ", "トラップ")
FOLK = ("フォーク", "弾き語り", "ニューミュージック")


VG = None


def pick_me(fam, r):
    vg = (VG or '')[:1]
    if vg == 'm':
        return '俺' if fam == 'rap' else ('ぼく' if fam == 'folk' else r.choice(['僕', '僕', '俺']))
    if vg == 'f':
        return r.choice(['あたし', '私']) if fam == 'rap' else ('わたし' if fam == 'folk' else r.choice(['私', 'わたし', 'あたし']))
    return '俺' if fam == 'rap' else ('ぼく' if fam == 'folk' else r.choice(['僕', '私', 'わたし']))


def _seed(*a):
    return int(hashlib.md5("|".join(map(str, a)).encode()).hexdigest()[:8], 16)


def _pick_words(premise, TIME, PLACE, THING):
    t = next((w for w in TIME if w in premise), None)
    p = next((w for w in PLACE if w in premise), None)
    x = next((w for w in THING if w in premise), None)
    return t, p, x


def family(genre):
    g = genre
    if any(k in g for k in ("パンク", "ハードコア", "ジャパメタ", "マスロック")): return "punk"
    if any(k in g for k in RAP) or "ポエトリー" in g or "ヒップホップ" in g: return "rap"
    if any(k in g for k in FOLK): return "folk"
    if any(k in g for k in ("シティポップ", "R&B", "AOR")): return "citypop"
    if any(k in g for k in ("シューゲイズ", "ポストロック", "アンビエント", "スロウコア", "轟音")): return "gaze"
    if any(k in g for k in ("歌謡", "演歌")): return "kayo"
    if any(k in g for k in ("テクノ", "ハウス", "トランス", "ドラムンベース", "エレクトロ", "ダンス", "ハイパー", "チップ")): return "dance"
    if g.startswith("AI"): return "ai"
    return None


def make(theme, genre, premise, title, year, words, early, era=2, used=None):
    bank = B.get(theme)
    if not bank:
        return None
    ex = EXTRA.get(theme, {})
    gl = gen_vocab.lines(theme, random.Random(_seed(title, year, theme, "gv")), 16)
    _gr = lyr_rich.lines(theme, family(genre), random.Random(_seed(title, year, theme, "gr")), 24)
    for _k in gl: gl[_k] = gl[_k] + _gr[_k]
    A = bank["a"] + ex.get("a", []) + gl["a"]; Bb = bank["b"] + ex.get("b", []) + gl["b"]; H = bank["h"] + ex.get("h", []) + gl["h"]; C = ex.get("c", []) + gl["c"]
    r = random.Random(_seed(title, year, theme))
    TIME, PLACE, THING = words
    t0, p0, x0 = _pick_words(premise, *words)
    t = t0 or r.choice(TIME); p = p0 or r.choice(PLACE); x = x0 or r.choice(THING)
    fam = family(genre)
    me = pick_me(fam, r)
    fmt = lambda s: s.format(t=t, p=p, x=x, me=me)
    # 1行目: 時代の場面 / 系統の場面 / テーマの場面
    scenes = [(1.0, A)]
    pool_a = list(A)
    roll = r.random()
    if roll < 0.28 and ERA_SCENE.get(era):
        pool_a = ERA_SCENE[era]
    elif roll < 0.55 and fam:
        pool_a = FAMILY_SCENE[fam]
    # SNS系の語は era>=3 限定のテーマ行以外で出さない
    bad = ("SNS", "いいね", "タイムライン", "スマホ", "画面", "ペンライト", "ライブ配信", "メッセージ", "返信", "炎上", "通知", "既読")
    if era <= 2:
        pool_a = [z for z in pool_a if not any(k in z for k in bad)] or A
        Bb = [z for z in Bb if not any(k in z for k in bad)] or bank["b"]
    if era <= 1:
        pool_a = [z for z in pool_a if not any(k in z for k in ("ケータイ", "メール", "ネット", "MD", "iPod", "サブスク", "動画", "SNS", "アルゴリズム"))] or A
    a = fmt(r.choice(pool_a)); b = fmt(r.choice(Bb)); h = fmt(r.choice(H))
    lines = [a, b]
    if C and r.random() < 0.55:
        lines = [a, b, fmt(r.choice(C))]
    suf = FAMILY_HOOK_SUFFIX.get(fam, "")
    if suf:
        h = h.rstrip("。") + suf
    lab = "バース" if fam == "rap" else "サビ"
    return {"l": lines, "h": h, "hl": lab}


def make_full(theme, genre, premise, title, year, words, early, era=2):
    """フルコーラス風: 1番・2番・Cメロ・ラスサビ。返り値 s は節ごとの行。"""
    bank = B.get(theme)
    if not bank:
        return None
    ex = EXTRA.get(theme, {})
    gl = gen_vocab.lines(theme, random.Random(_seed(title, year, theme, "gv")), 16)
    _gr = lyr_rich.lines(theme, family(genre), random.Random(_seed(title, year, theme, "gr")), 24)
    for _k in gl: gl[_k] = gl[_k] + _gr[_k]
    A = bank["a"] + ex.get("a", []) + gl["a"]; Bb = bank["b"] + ex.get("b", []) + gl["b"]; H = bank["h"] + ex.get("h", []) + gl["h"]; C = ex.get("c", []) + gl["c"]
    r = random.Random(_seed(title, year, theme, "full"))
    TIME, PLACE, THING = words
    t0, p0, x0 = _pick_words(premise, *words)
    t = t0 or r.choice(TIME); p = p0 or r.choice(PLACE); x = x0 or r.choice(THING)
    fam = family(genre)
    me = pick_me(fam, r)
    fmt = lambda s: s.format(t=t, p=p, x=x, me=me)
    bad = ("SNS", "いいね", "タイムライン", "スマホ", "画面", "ペンライト", "ライブ配信", "メッセージ", "返信", "炎上", "通知", "既読")
    old = ("ケータイ", "メール", "ネット", "MD", "iPod", "サブスク", "動画", "アルゴリズム")
    def ok(z):
        if era <= 2 and any(k in z for k in bad): return False
        if era <= 1 and any(k in z for k in old): return False
        return eraword.ok(z, year)
    if not ok(t): t = r.choice([z for z in TIME if ok(z)] or TIME)
    if not ok(p): p = r.choice([z for z in PLACE if ok(z)] or PLACE)
    if not ok(x): x = r.choice([z for z in THING if ok(z)] or THING)
    H = [z for z in H if ok(z)] or bank["h"]; C = [z for z in C if ok(z)] or C
    Af = [z for z in A if ok(z)] or bank["a"]; Bf = [z for z in Bb if ok(z)] or bank["b"]
    S = list(ERA_SCENE.get(era, [])) + (list(FAMILY_SCENE[fam]) if fam else [])
    S = [z for z in S if ok(z)]
    a = r.sample(Af, min(3, len(Af)))
    open1 = fmt(r.choice(S)) if S and r.random() < 0.7 else fmt(a[0])
    pa = [fmt(z) for z in a]
    b = [fmt(z) for z in r.sample(Bf, min(2, len(Bf)))]
    h = [fmt(z) for z in r.sample(H, min(8, len(H)))]
    while len(h) < 8: h.append(h[len(h) - 4])
    s = {}
    s["A1"] = [open1, pa[1] if len(pa) > 1 else pa[0]]
    s["B1"] = [b[0]]
    suf = FAMILY_HOOK_SUFFIX.get(fam, "")
    hook = h[3].rstrip("。") + suf if suf else h[3]
    s["S"] = [h[0], h[4], h[5], hook]
    s["A2"] = [pa[2] if len(pa) > 2 else pa[0], pa[0] if open1 != pa[0] else pa[1]]
    s["B2"] = [b[1] if len(b) > 1 else b[0]]
    s["Sb"] = [h[1], h[6], h[7], hook]
    if C:
        cs = [fmt(z) for z in r.sample(C, min(2, len(C)))]
        s["C"] = cs
        s["S2"] = [h[2], h[0], h[4], hook, hook]
    return {"s": s, "h": hook, "hl": "バース" if fam == "rap" else "サビ"}
