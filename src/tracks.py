# -*- coding: utf-8 -*-
"""収録曲(トラックリスト)とメンバーの生成。すべて決定的(作品名と年から決まる)。"""
import random
import gen_vocab, hashlib, bio, eraword

def _seed(*a):
    return int(hashlib.md5("|".join(map(str, a)).encode()).hexdigest()[:8], 16)

# テーマ別の曲名(歌詞のテーマと呼応する)
TT = {
"失恋": ["返しそびれた傘", "未読のまま", "三年目の合鍵", "ひとつ多いマグカップ", "さよならの練習", "元カノの好きな曲", "昨日までの住所", "こじらせ記念日"],
"応援歌": ["ラストスパートは今じゃない", "ポケットの勇気", "靴ひもを結び直して", "まだ途中だ", "三歩下がって四歩行く", "筋肉痛の歌", "ベンチの外から", "追い風を待たずに"],
"上京と故郷": ["片道切符", "実家からの荷物", "方言が出た日", "各駅停車の夜", "母の電話は長い", "家賃と夢", "帰省ラッシュを逆走", "ふるさと納税"],
"家族への感謝": ["お弁当の卵焼き", "父の背中は大きかった", "ただいまの音", "母の味噌汁", "兄貴の自転車", "おばあちゃんの小言", "反抗期の終わり", "実家の犬"],
"社会への怒り": ["満員電車に殺意", "ルールのためのルール", "忖度の国", "見て見ぬふりの天才", "ハンコの奴隷", "声がでかい奴が勝つ", "会議のための会議", "愛想笑い選手権"],
"日常のぼやき": ["月曜日が来る", "冷蔵庫の中身", "洗濯物が乾かない", "レジ袋有料", "寝坊のしかた", "アラームを止める右手", "今日もなにもなかった", "コンビニの新作"],
"夏と青春": ["ラムネの泡が消える前に", "二人乗りの坂道", "夏休み最終日", "蝉と入道雲", "花火大会の帰り道", "補習の窓から", "プールの匂い", "麦わら帽子と約束"],
"孤独と夜": ["午前三時の冷蔵庫", "眠れない人のための子守唄", "ひとり暮らしの夜景", "コンビニの灯り", "終電を見送って", "天井のしみ", "夜更かしの言い訳", "静かすぎる部屋"],
"喪失と再生": ["空っぽの手", "春を待つ土", "片付けた日", "雨のあとの匂い", "忘れ物の行方", "止まった時計を巻く", "芽吹き", "ありがとうの置き場所"],
"自己否定と肯定": ["自己採点", "鏡に謝る", "ダメな日の音楽", "せめてもの百点", "どうせ、の向こう側", "比べるのをやめた日", "不器用の才能", "それでも朝は来た"],
"地元愛": ["商店街のテーマ", "国道沿いのヒーロー", "ご当地の誇り", "町内放送", "田んぼ道フリーウェイ", "おらが町の応援歌", "駅前ロータリー", "地元のイオン"],
"恋のはじまり": ["目が合った", "名前を呼んでみた", "気になるあの子の自転車", "連絡先を聞くまで", "恋はまだ名前がない", "隣の席の特等席", "ときめきの前触れ", "既読がつく前に"],
"時代風刺": ["流行語大賞", "炎上のしかた", "タイパの国", "正義の味方は多すぎる", "マウントの山", "バズらないと死ぬ病", "令和の花見", "二度見の時代"],
"ナンセンスと言葉遊び": ["カバが傘をさした", "しりとり宇宙", "カレーの国から", "あいうえおの逆襲", "ピーマンの反乱", "三角形の言い訳", "ぐるぐるぽん", "無題(仮)"],
"人工物への違和感": ["完璧な声", "出力される優しさ", "学習データの夢", "揺らぎは残して", "偽物のぬくもり", "プロンプトの向こう", "ノイズ除去された孤独", "再生成"],
"推しとファンへの手紙": ["ペンライトの海", "ステージの向こうへ", "推しの名前を呼ぶ夜", "会えない日のエール", "ライブ帰りの夜風", "ありがとうは光る", "ファンレターの書き出し", "ずっと推してる"],
"お金と仕事": ["月末の請求書", "夢と家賃の板挟み", "副業は歌", "給料日は金曜日", "領収書の山", "時給ブルース", "バイト先の店長", "経費で落ちない夢"],
"旅立ちと別れの春": ["卒業式の前の日", "桜の下で泣いた", "寄せ書きの隅", "ボタンをひとつ", "最後のチャイム", "またねの意味", "春休みの空", "旅立ちの駅"],
}
# 曲名のもじり(作品名のみ・時代で解禁)
PARODY = [("天体観察", -1), ("世界に一つだけの傘", 2), ("終わりなき残業", 1), ("木綿のティッシュ", -1), ("春よ、遅れて来い", 1),
          ("なごり雨", -1), ("チェリーパイ", 1), ("Tomorrow never comes", 1), ("夜に駆けたい", 4), ("ぬるいレモン", 3), ("さくらぼん", 2), ("ハナミズ", 2),
          ("守ってあげたいけど", 0), ("勝手にシンドバッド屋", 0), ("世界でいちばん暑い夏", 0), ("君がいない夏の終わりに", 0), ("乾杯と見せかけて", 2),
          ("めざせポケット", 1), ("涙そうそうそう", 2), ("負けないで、とは言えない", 1), ("アジアの純真さ", 1), ("粉雪と砂利", 2), ("糸くず", 3)]
GENERIC = ["夜行バス", "週末の遠回り", "冷たい炭酸", "三日月の下", "言い訳の天才", "ひとりぼっちの合唱", "電柱の影", "雨宿り", "窓際の席", "残り香", "うたかた", "遠雷"]

try:
    import json as _j, os as _o
    _f = '/home/claude/ptfix/gen_titles.json'
    if _o.path.exists(_f):
        _g = _j.load(open(_f))
        for _k, _v in (_g.get('TT') or {}).items():
            TT.setdefault(_k, [])
            TT[_k] = list(dict.fromkeys(TT[_k] + [x for x in _v if isinstance(x, str) and x.strip()]))
        GENERIC = list(dict.fromkeys(GENERIC + [x for x in (_g.get('GENERIC') or []) if isinstance(x, str) and x.strip()]))
except Exception as _e:
    print('gen_titles skip', _e)

def _titles(r, theme, era, n, avoid, extra=None, year=None):
    out = []
    if extra:
        ex = [t for t in extra if t not in avoid and eraword.ok(t, year)]
        r.shuffle(ex)
        for t in ex:
            if len(out) >= n: break
            if t not in out: out.append(t)
        if len(out) >= n: return out
    pool = list(TT.get(theme, [])) + (GENERIC if len(GENERIC) > 200 else GENERIC + GENERIC)
    _bad = ('通知', '既読', 'メッセージ', 'ペンライト')
    pool += [z for z in gen_vocab.titles(theme, r, 24) if era >= 3 or not any(k in z for k in _bad)]
    pool = [z for z in pool if eraword.ok(z, year)]
    par = [t for t, e in PARODY if era >= e]
    tries = 0
    while len(out) < n and tries < 400:
        tries += 1
        x = r.random()
        if x < 0.02 and par and extra is None: t = r.choice(par)  # 実在アーティスト(extraあり)には他人のもじり曲を混ぜない
        elif x < 0.9: t = r.choice(pool)
        else: t = r.choice(GENERIC)
        if t not in avoid and t not in out: out.append(t)
    return out

def _dur(r):
    return "%d:%02d" % (r.choice([2, 3, 3, 3, 4, 4, 5]), r.randint(0, 59))

def tracklist(h, style, era, theme, prev_titles, extra=None):
    """h: 作品dict(title, kind, ...)。返り値: [{n,t,d,tag}]"""
    r = random.Random(_seed(h['title'], h['year'], "trk"))
    yy = h.get('year')
    kind = h['kind']; title = h['title']; tr = []
    avoid = set(prev_titles) | {title}
    def add(t, tag="", d=None): tr.append({"t": t, "d": d or _dur(r), "g": tag})
    if kind in ("シングル", "配信限定シングル"):
        add(title, "表題曲")
        if kind == "配信限定シングル":
            if r.random() < 0.5: add(title, "Instrumental")
        else:
            for t in _titles(r, theme, era, 2 if r.random() < 0.5 else 1, avoid, extra, yy): add(t, "c/w" if era <= 2 else "")
            if r.random() < 0.55: add(title, "Instrumental")
    elif kind == "EP":
        n = r.randint(4, 6); ts = _titles(r, theme, era, n - 1, avoid, extra, yy)
        lead = r.randrange(0, 2); order = ts[:]
        order.insert(lead, title)
        for i, t in enumerate(order): add(t, "表題曲" if t == title else "")
        if r.random() < 0.3: tr[-1]["g"] = "ボーナストラック"
    else:  # アルバム
        n = r.randint(9, 13); ts = _titles(r, theme, era, n, avoid, extra, yy)
        gag = r.random()
        r.random(); main = title  # 表題曲は必ずアルバム名と同じ曲(歌詞もアルバム名で作られるため)
        if era <= 2 and r.random() < 0.5: add("Intro", "SE", "0:%02d" % r.randint(20, 59))
        order = ts[:n - 2]
        pos = r.randrange(1, max(2, len(order)))
        order.insert(pos, main)
        for t in order: add(t, "表題曲" if t == main else "")
        if prev_titles and r.random() < 0.4: add(r.choice(prev_titles), "再録")
        if r.random() < 0.35: tr.insert(len(tr) // 2, {"t": "Interlude", "d": "1:%02d" % r.randint(0, 40), "g": ""})
        if r.random() < 0.18: tr[r.randrange(1, len(tr))]["d"] = "%d:%02d" % (r.randint(9, 17), r.randint(0, 59)); 
        if r.random() < 0.25: add("無題", "隠しトラック", "%d:%02d" % (r.randint(10, 12), r.randint(0, 59)))
        elif r.random() < 0.3: add(r.choice(eraword.filt([t for t in (extra or GENERIC) if t not in avoid] or GENERIC, h.get('year'))), "初回限定盤のみ")
        if style in ("rap",) and r.random() < 0.5 and len(tr) > 3: tr[2]["t"] += " feat. " + r.choice(["KAGE", "N.O.W.", "SHIN", "ミナト", "ゲスト"])
    for i, t in enumerate(tr): t["n"] = i + 1
    return tr

# ---- メンバー ----
FAM = ["佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "山本", "中村", "小林", "加藤", "吉田", "山田", "松本", "井上", "木村", "林", "清水", "山口", "阿部", "池田", "橋本", "石川", "前田", "藤田", "岡田", "後藤", "長谷川", "村上", "近藤", "石井"]
GIV_M = ["タクヤ", "ケンジ", "ユウスケ", "ヒロシ", "ショウタ", "リョウ", "ダイスケ", "マサト", "カズキ", "シュン", "ジュン", "テツ", "コウタ", "マコト", "アキラ", "レン", "トモヤ", "イサム", "ヨシオ", "ハジメ", "ユウジ", "ケイスケ", "タイチ", "ナオキ"]
GIV_F = ["アヤ", "ミキ", "サトミ", "ユイ", "ハルカ", "ユキ", "ミホ", "サキ", "カオル", "ミサキ", "アヤカ", "ナナ", "ミドリ", "リナ", "チサト", "エミ", "マイ", "ノゾミ", "ユカ", "ナオ", "ミナミ", "ヒトミ", "レイコ", "マユ"]
GIV = ["タクヤ", "ケンジ", "ユウスケ", "ヒロシ", "ショウタ", "リョウ", "ダイスケ", "マサト", "カズキ", "ナオ", "アヤ", "ミキ", "サトミ", "ユイ", "ハルカ", "シュン", "ジュン", "テツ", "コウタ", "ユキ", "マコト", "アキラ", "レン", "ミホ", "サキ", "トモヤ", "イサム", "ヨシオ", "カオル", "ハジメ"]
NICK = ["ぐっさん", "リーダー", "センセイ", "ポチ", "おやっさん", "てっちゃん", "K", "しょーた", "ボス", "ちびっこ", "マスター", "ハカセ", "サブ", "ミッキー"]
TRAIT = ["遅刻魔", "機材オタク", "最年少", "酒が強い", "曲の八割を書く", "なぜか車を持っている", "MCが長い", "バイトを三つ掛け持ち", "ライブ前に必ず腹を壊す", "地元の先輩", "楽屋でずっと寝ている", "物販の天才", "元・別バンドのリーダー", "譜面が読めない", "笑い声がでかい", "禁酒中(三日目)"]
ROLES = {"band": ["Vo", "Gt", "Ba", "Dr"], "inst": ["Gt", "Gt", "Ba", "Dr"], "duo": ["Vo/Gt", "Key/Cho"]}
TEAM = {"solo": ["サポートギター", "マネージャー", "録音担当"], "rap": ["DJ", "トラックメイカー", "マネージャー"], "beat": ["ミックス担当", "ジャケット担当"],
        "dj": ["VJ", "マネージャー"], "ai_pure": ["運営", "プロンプト担当"], "ai_collab": ["AI運用担当", "マネージャー"]}

def people(seed, style, n=None):
    r = random.Random(_seed(seed, style, "mem"))
    roles = ROLES.get(style) or TEAM.get(style, [])
    out = []; used = set()
    for i, role in enumerate(roles):
        while True:
            g = "m" if r.random() < 0.55 else "f"
            nm = r.choice(FAM) + " " + r.choice(GIV_M if g == "m" else GIV_F)
            if nm not in used: used.add(nm); break
        out.append({"g": g, "n": nm, "r": role, "k": r.choice(NICK) if r.random() < 0.35 else "", "t": r.choice(TRAIT) if r.random() < 0.7 else "", **bio.member_extra(seed, role, i)})
    return out

def newcomer(seed, role, taken):
    r = random.Random(_seed(seed, role, "new", len(taken)))
    g = "m" if r.random() < 0.5 else "f"
    while True:
        nm = r.choice(FAM) + " " + r.choice(GIV_M if g == "m" else GIV_F)
        if nm not in taken: break
    return {"g": g, "n": nm, "r": role, "k": "", "t": r.choice(TRAIT), **bio.member_extra(seed, role, len(taken) + 50)}
