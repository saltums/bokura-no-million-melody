#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ストーリーライン(音楽版・仮) ジェネレーター

  python3 ongaku_storyline_gen.py --count 100000 --out out     # 構造が全部異なる物語を10万本書き出す
  python3 ongaku_storyline_gen.py --show 12345                  # IDを指定して1本を読む(同じIDは必ず同じ物語)

仕組み: 活動形態 x 性格 x 時代 x 系統 から出発し、リリースごとに
  「歌詞テーマ + 性格との相性 + 時代の流行 + 宣伝力 + 勢い + 運」で結果が決まる。
リリースの合間に「分かれ道(選択)」と「予期せぬ転機」が挟まり、最後に結末が決まる。
選択はプレイヤーが選ぶ想定。ここでは性格の傾向で重みづけして自動で選ばせ、選ばなかった選択肢も記録する。
"""
import argparse, csv, gzip, json, os, random, collections
import gen_vocab


def clamp(x, a, b):
    return max(a, min(b, x))


# ------------------------------------------------------------------ 時代
ERAS = {
    -1: dict(name="70年代(フォーク・ニューロックの黎明期)", short="70年代", year=1974),
    0: dict(name="80年代(パンク・ニューウェーブ・バンドブーム)", short="80年代", year=1983),
    1: dict(name="CD全盛期(90年代)", short="CD全盛期", year=1996),
    2: dict(name="ネット黎明期(00年代)", short="ネット黎明期", year=2004),
    3: dict(name="動画投稿・SNS時代(10年代)", short="SNS時代", year=2013),
    4: dict(name="配信・ショート動画時代(20年代前半)", short="配信時代", year=2021),
    5: dict(name="AI楽曲があふれる時代(近未来)", short="AI楽曲時代", year=2031),
}
ERA_W = {-1: 1.5, 0: 2, 1: 2, 2: 2, 3: 3, 4: 3, 5: 2}

TIERS = ["不発", "通好みの評価", "小ヒット", "ヒット", "大ヒット", "社会現象"]
TH = [0.6, 1.5, 2.4, 3.4, 4.8]
FAME_D = [-1, 2, 5, 10, 18, 28]
FANS_D = [1, 8, 6, 4, 2, 1]
MOM_D = [-0.6, 0.2, 0.6, 1.0, 1.4, 1.8]

# ------------------------------------------------------------------ 活動形態
STYLES = {
    "solo": dict(name="シンガーソングライター", w=16, live=True, ai=False, eras=[-1, 0, 1, 2, 3, 4, 5],
                 genres=["フォーク弾き語り", "ポップス", "シティポップ", "R&B", "オルタナ", "歌謡曲風ポップ", "ニューミュージック", "フォークロック"]),
    "band": dict(name="バンド", w=22, live=True, ai=False, eras=[-1, 0, 1, 2, 3, 4, 5],
                 genres=["轟音ロック", "パンクロック", "ギターロック", "ポップロック", "ハードコア", "ポストロック", "オルタナ", "フォークロック", "ニューウェーブ", "ジャパメタ", "アングラ前衛ロック", "ハードコアパンク", "ロカビリー", "ブルースロック", "歌謡ロック"]),
    "rap": dict(name="ラッパー", w=12, live=True, ai=False, eras=[0, 1, 2, 3, 4, 5],
                genres=["地元系ヒップホップ", "トラップ", "ポエトリーラップ", "ポップラップ"]),
    "beat": dict(name="トラックメイカー", w=12, live=False, ai=False, eras=[0, 1, 2, 3, 4, 5],
                 genres=["エレクトロポップ", "チップチューン", "ハイパーポップ", "アンビエント", "ダンスロック"]),
    "dj": dict(name="DJ・ダンスミュージック", w=6, live=True, ai=False, eras=[0, 1, 2, 3, 4, 5],
               genres=["ハウス", "テクノ", "ドラムンベース", "トランス"]),
    "inst": dict(name="インストバンド", w=6, live=True, ai=False, eras=[1, 2, 3, 4, 5],
                 genres=["ポストロック", "マスロック", "インストロック", "ジャズ・フュージョン"]),
    "duo": dict(name="2人組ユニット", w=8, live=True, ai=False, eras=[-1, 0, 1, 2, 3, 4, 5],
                genres=["ポップス", "エレクトロポップ", "フォークポップ", "シティポップ", "フォークデュオ", "ニューミュージック"]),
    "ai_pure": dict(name="AIミュージシャン(完全生成)", w=22, live=False, ai=True, eras=[4, 5],
                    genres=["AIポップス", "AIロック", "AIエレクトロ", "AIジャズ風"]),
    "ai_collab": dict(name="人間+AIの共作ミュージシャン", w=22, live=False, ai=True, eras=[4, 5],
                      genres=["AIポップス", "AIロック", "AIエレクトロ", "AIジャズ風"]),
}
GROUP = {"band", "duo", "inst"}


def style_name(c):
    s = c['style']
    if s == "beat":
        return "ボカロP・トラックメイカー" if c['era'] >= 3 else "宅録トラックメイカー"
    return STYLES[s]['name']


GENRE_VIBE = {"フォーク弾き語り": -1, "ポップス": 2, "シティポップ": 1, "R&B": 0, "オルタナ": -1, "歌謡曲風ポップ": 1,
              "轟音ロック": -1, "パンクロック": 1, "ギターロック": 0, "ポップロック": 2, "ハードコア": -2, "ポストロック": -1,
              "地元系ヒップホップ": 0, "トラップ": -1, "ポエトリーラップ": -2, "ポップラップ": 2,
              "エレクトロポップ": 1, "チップチューン": 2, "ハイパーポップ": 1, "アンビエント": -2, "ダンスロック": 1,
              "ハウス": 1, "テクノ": -1, "ドラムンベース": 0, "トランス": 1,
              "インストロック": 0, "ジャズ・フュージョン": 1, "轟音シューゲイズ": -2, "マスロック": 0, "スロウコア": -2, "フォークポップ": 1,
              "AIポップス": 2, "AIロック": 0, "AIエレクトロ": 0, "AIジャズ風": -1}

PERS = [
    dict(n="明るい", vibe=2, soc=2, perf=0, amb=1, stab=1),
    dict(n="暗い", vibe=-2, soc=-1, perf=2, amb=0, stab=-1),
    dict(n="普通", vibe=0, soc=0, perf=0, amb=0, stab=0),
    dict(n="頑固", vibe=-1, soc=-1, perf=2, amb=1, stab=1),
    dict(n="気分屋", vibe=0, soc=1, perf=-1, amb=0, stab=-2),
    dict(n="人たらし", vibe=2, soc=3, perf=-1, amb=1, stab=0),
    dict(n="怠け者", vibe=0, soc=0, perf=-1, amb=-2, stab=1),
    dict(n="野心家", vibe=1, soc=1, perf=1, amb=3, stab=0),
    dict(n="繊細", vibe=-2, soc=-1, perf=1, amb=-1, stab=-2),
    dict(n="天然", vibe=1, soc=1, perf=-2, amb=0, stab=0),
]

GENRE_VIBE.update({"ニューミュージック": 1, "フォークロック": 0, "ニューウェーブ": 0, "ジャパメタ": 0, "アングラ前衛ロック": -2, "ハードコアパンク": -2,
                   "ロカビリー": 2, "ブルースロック": -1, "歌謡ロック": 1, "フォークデュオ": 0})
GMIN = {"フォーク弾き語り": -1, "ポップス": -1, "シティポップ": 0, "R&B": 0, "オルタナ": 1, "歌謡曲風ポップ": -1, "ニューミュージック": -1, "フォークロック": -1,
        "轟音ロック": 0, "パンクロック": 0, "ギターロック": 0, "ポップロック": -1, "ハードコア": 0, "ポストロック": 1, "ニューウェーブ": 0, "ジャパメタ": 0,
        "アングラ前衛ロック": -1, "ハードコアパンク": 0, "ロカビリー": 0, "ブルースロック": -1, "歌謡ロック": -1, "フォークデュオ": -1, "フォークポップ": -1,
        "地元系ヒップホップ": 1, "トラップ": 5, "ポエトリーラップ": 0, "ポップラップ": 1, "エレクトロポップ": 0, "チップチューン": 1, "ハイパーポップ": 5,
        "アンビエント": 0, "ダンスロック": 1, "ハウス": 1, "テクノ": 0, "ドラムンベース": 1, "トランス": 1, "インストロック": 1, "ジャズ・フュージョン": 1, "轟音シューゲイズ": 1, "マスロック": 2, "スロウコア": 1}
_tr = random.Random(20261017)
TREND = {}
for _g in GENRE_VIBE:
    for _e in ERAS:
        TREND[(_g, _e)] = 0 if _g.startswith("AI") else _tr.choice([-1, 0, 0, 1])

# ------------------------------------------------------------------ 歌詞テーマ(歌詞そのものではなく、何を歌った曲かの要約)
TIME = ["午前三時", "日曜の夜", "終電", "夏の終わり", "雨上がり", "明け方", "月曜", "放課後", "真夜中", "春先", "十二月", "帰り道"]
PLACE = ["バス停", "踊り場", "屋上", "国道", "改札", "河川敷", "商店街", "踏切", "自販機", "コインランドリー", "港", "駐車場", "団地", "海沿い"]
THING = ["コンパス", "街灯", "ノイズ", "傘", "電波", "蛍光灯", "ポケット", "地図", "記憶", "歯車", "毛布", "ラジオ", "首輪", "合鍵", "影"]
EMO = ["さよなら", "ごめんね", "ありがとう", "まだ", "きっと", "ひとり", "ぜんぶ", "たぶん", "もう一度", "いつか"]
KATA = ["ノイズ", "ネオン", "ループ", "シグナル", "ブルー", "スロウ", "ダイブ", "リフレイン", "ハイライト", "フェード", "アウトロ", "ミッドナイト"]
AIW = ["予測変換", "平均値", "最適解", "学習済み", "ノイズ除去"]

THEMES = [
    dict(n="失恋", v=-1, pre=["{time}の{place}で、連絡できない相手を思い出す歌", "返しそびれた{thing}を前に、別れを少しずつ受け入れていく歌"],
         hit=["失恋した人が夜中にひとりで聴く曲として広まった", "カラオケの失恋ソングの定番になった", "別れた直後の人が歌詞をSNSに引用する流れができた"],
         flop=["感情の説明が多く、聴き手が入り込む余白がなかった"]),
    dict(n="応援歌", v=2, pre=["{time}の{place}で、うまくいかない誰かの背中を押す歌", "{thing}を握りしめて、もう一度走り出す歌"],
         hit=["運動会や部活の応援曲として使われるようになった", "就活や受験の時期に励ましの曲として口コミが広がった"],
         flop=["励ましが一方的で、押しつけがましく聞こえた"]),
    dict(n="上京と故郷", v=-1, pre=["{place}を後にして、{time}の電車で街を出る歌", "故郷に置いてきた{thing}を思い出す歌"],
         hit=["春に上京する人の間で定番になった", "地方出身者が帰省の電車で聴く曲になった"],
         flop=["地方の風景が個人的すぎて共感を呼ばなかった"]),
    dict(n="家族への感謝", v=1, pre=["実家の{thing}と、言えなかった「ありがとう」の歌", "{time}の台所の音を思い出す歌"],
         hit=["結婚式や卒業式で流される曲になった", "親に贈る曲としてSNSで紹介が相次いだ"],
         flop=["個人的すぎて、他人の家族の話に聞こえた"]),
    dict(n="社会への怒り", v=-1, pre=["{place}で見た理不尽を、そのまま言葉にした歌", "{thing}のように使い捨てられる人たちの歌"],
         hit=["同じ不満を抱えた人たちの代弁として支持された", "デモや集会の場で歌われ、議論を呼んだ"],
         flop=["主張が強すぎ、曲として聴かれる前に身構えられた"]),
    dict(n="日常のぼやき", v=0, pre=["{time}の{place}で、ただ疲れたとつぶやくだけの歌", "{thing}を探して一日が終わる歌"],
         hit=["『わかる』という共感がSNSで連鎖した", "給料日前の歌として季節の風物詩になった"],
         flop=["身近すぎて、特別な曲に聞こえなかった"]),
    dict(n="夏と青春", v=2, pre=["{place}で過ごした、二度と来ない夏の歌", "{thing}を貸したまま終わった夏の歌"],
         hit=["夏フェスと学校行事の定番曲になった", "毎年夏に再生数が跳ね上がる曲になった"],
         flop=["懐かしさだけで、新しい視点がなかった"]),
    dict(n="孤独と夜", v=-2, pre=["{time}の{place}で、誰とも話さずに過ごす歌", "眠れない夜に{thing}だけが動いている歌"],
         hit=["眠れない夜の曲として静かに広まった", "深夜ラジオのリクエスト常連になった"],
         flop=["暗さが勝ち、聴き続けるのが重く感じられた"]),
    dict(n="喪失と再生", v=-2, pre=["{thing}を失くしたあとの{time}を描く歌", "{place}で立ち止まり、それでも歩き出す歌"],
         hit=["大切な人を亡くした人たちの間で、心の支えとして語られた", "追悼の場で流れたことをきっかけに広まった"],
         flop=["重いテーマを扱いきれず、説教くさく聞こえた"]),
    dict(n="自己否定と肯定", v=0, pre=["{thing}のように役に立たない自分を、少しだけ許す歌", "{time}に自分を責めてしまう人の歌"],
         hit=["自分を責めがちな人たちの合言葉のように歌詞が引用された"],
         flop=["自己憐憫に聞こえてしまった"]),
    dict(n="地元愛", v=1, pre=["{place}と{thing}しかない町を、それでも好きだと歌う歌"],
         hit=["地元の祭りやスポーツ観戦で歌われる曲になった"],
         flop=["固有名詞が多く、地元以外には伝わらなかった"]),
    dict(n="恋のはじまり", v=2, pre=["{place}で目が合っただけで、世界が変わる歌", "{time}にメッセージを打っては消す歌"],
         hit=["告白の前に聴く曲として若い世代に定着した", "恋愛ドラマの定番の挿入曲として使われた"],
         flop=["甘さが先に立ち、すぐ消費された"]),
    dict(n="時代風刺", v=0, pre=["{thing}に振り回される時代を、笑いにして歌う歌"],
         hit=["時事ネタとして話題になり、ニュース番組で取り上げられた"],
         flop=["時事ネタが古くなり、すぐ忘れられた"]),
    dict(n="ナンセンスと言葉遊び", v=1, pre=["{thing}と{place}が意味もなく会話する歌", "言葉の響きだけで進んでいく歌"],
         hit=["意味不明さが癖になり、真似動画が量産された", "子どもが歌い出し、親世代にまで広まった"],
         flop=["遊びが空回りし、ただの悪ふざけに聞こえた"]),
    dict(n="人工物への違和感", v=-1, pre=["完璧すぎる音と言葉に、少し寒気を覚える歌", "{thing}にまで『最適化』が届いた世界の歌"],
         hit=["AI時代を歌った曲として論考の題材になった"],
         flop=["時事に寄りかかりすぎた"], era_min=4),
    dict(n="推しとファンへの手紙", v=1, era_min=3, pre=["画面越しに届かない人へ、{thing}を添えて書いた歌"],
         hit=["ファンの間で定番の合唱曲になった"],
         flop=["内輪向けすぎ、外には届かなかった"]),
    dict(n="お金と仕事", v=-1, pre=["{time}の{place}で、給料明細を見つめる歌", "辞めたいと言えないまま{thing}を握る歌"],
         hit=["仕事に疲れた会社員の愛唱歌になった", "月曜の朝に聴く曲としてSNSで話題になった"],
         flop=["愚痴の域を出なかった"]),
    dict(n="旅立ちと別れの春", v=1, pre=["{place}で最後に撮った写真の歌", "{thing}を置いて、それぞれの道へ進む歌"],
         hit=["卒業シーズンのたびに再生される定番になった"],
         flop=["季節外れの発売で聴かれなかった"]),
]
THEME_TREND = {}
for _t in THEMES:
    for _e in ERAS:
        THEME_TREND[(_t['n'], _e)] = _tr.choice([-1, 0, 0, 1])


def mk_title(r, ai=False):
    pats = [
        lambda: f"{r.choice(TIME)}の{r.choice(PLACE)}",
        lambda: f"{r.choice(THING)}のままで",
        lambda: f"{r.choice(EMO)}の手前",
        lambda: f"{r.choice(KATA)}と{r.choice(THING)}",
        lambda: f"{r.choice(PLACE)}で会おう",
        lambda: f"{r.choice(THING)}を投げる",
        lambda: f"{r.choice(KATA)}・{r.choice(KATA)}",
        lambda: f"{r.choice(EMO)}、{r.choice(TIME)}",
        lambda: f"{r.choice(THING)}を失くした{r.choice(TIME)}",
    ]
    if ai and r.random() < 0.4:
        return r.choice([lambda: f"{r.choice(AIW)}の{r.choice(EMO)}", lambda: f"{r.choice(AIW)}{r.choice(THING)}"])()
    return r.choice(pats)()


ADJ2 = ["不確かな", "最後の", "三日目の", "優しい", "無数の", "夜更かしの", "ぼやけた", "さえない", "ふやけた", "ちぎれた", "薄情な", "ぐるぐるの", "ひとりきりの", "とろけた", "春の", "冬の", "憂鬱な", "月曜の", "ぼんやりした", "うしろ向きの", "透明な", "ぬるい", "八月の", "深夜の", "錆びた", "眠れない", "遠回りの", "小さな", "無口な", "湿った", "半透明の", "逆さまの", "日曜日の", "迷子の", "乾いた", "青い",
        "低温の", "午前三時の", "臆病な", "裸足の", "退屈な", "古い", "眠そうな", "孤独な", "片道の", "夕暮れの", "真夏の", "甘い", "苦い", "不機嫌な", "余白の", "平熱の",
        "使い捨ての", "曇りの", "四畳半の", "未来の", "壊れた", "銀色の", "朝焼けの", "無料の"]
NOUN2 = ["郵便受け", "ガードレール", "公衆電話", "ひまわり", "ミルクティー", "写真館", "月曜日", "飛行機雲", "鉄塔", "夕立", "文房具", "裏通り", "時刻表", "ビニール傘", "駅前", "古本屋", "雨雲", "回覧板", "非常階段", "冷蔵庫", "電話線", "観覧車", "消防署", "改札", "炭酸", "信号", "犬", "傘", "電波塔", "コインランドリー", "工場", "夜行バス", "蛍光灯", "回転寿司", "非常口", "自動販売機", "踏切", "路線図",
         "乾電池", "洗濯機", "水族館", "図書館", "灯台", "屋上", "踊り場", "公園", "歩道橋", "缶コーヒー", "扇風機", "ストーブ", "目覚まし", "定期券", "絆創膏", "画鋲", "ビー玉",
         "ラムネ", "カセット", "傘立て", "防波堤", "商店街", "銭湯", "団地", "タクシー", "海岸線", "天気予報", "マフラー", "ブランコ", "プラネタリウム", "交番", "駐輪場"]
EADJ = ["LUKEWARM", "MIDNIGHT", "RUSTY", "SILENT", "BROKEN", "PAPER", "GLASS", "CHEAP", "LAZY", "VELVET", "HOLLOW", "TINY", "NEON", "SLOW", "FADED", "WILD"]
ENOUN = ["SIGNALS", "ELEVATORS", "ANIMALS", "COMMUTERS", "RADIOS", "DOGS", "TRAINS", "BALLOONS", "GHOSTS", "MACHINES", "STATIONS", "BICYCLES", "LETTERS", "ORCHESTRA", "WEATHER", "SUBMARINES"]
NUMW = ["午前四時", "三分間", "第三象限", "百円ライター", "七番線", "十五夜", "二軍", "零時", "九月", "第二回", "五反田", "四十九日"]
VERBP = ["笑う", "泣いてる", "走る", "眠る", "燃える", "溶ける", "止まらない", "帰らない", "待っている", "崩れる"]
GIV2 = ["ミナト", "レイ", "ハル", "ソラ", "ユウ", "ナギ", "カエデ", "リク", "ミオ", "アカリ", "サクヤ", "トワ", "ヒカル", "ノゾミ", "シオン", "アオイ", "ツバサ", "イブキ", "ココロ", "ヨウ", "セナ", "ルカ", "リョウ", "ハヤト", "ノア", "ミズキ", "カナタ", "ヒナタ", "シュン", "アサヒ"]
SUR2 = ["佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "山本", "中村", "小林", "加藤", "吉田", "山田", "松本", "井上", "木村", "清水", "斉藤", "森", "藤原", "西村"]
ROMA = ["mina", "haru", "sora", "yuu", "nagi", "kaede", "riku", "mio", "akari", "toa", "hikaru", "nozomi", "shion", "aoi", "rui", "kou", "tsubasa", "ibuki"]


EADJ2 = ["COLD", "SOFT", "PALE", "BITTER", "SWEET", "ELECTRIC", "SUNDAY", "TINY", "WILD", "BLUE", "PLASTIC", "SECOND-HAND", "UNDERGROUND", "LATE", "EARLY", "HIDDEN", "SLEEPY", "CRAZY", "GENTLE", "LONELY"]
ENOUN2 = ["Pencil", "Elevator", "Harbor", "Lantern", "Compass", "Bakery", "Airport", "Satellite", "Postcard", "Envelope", "Marmalade", "Thunder", "Parade", "Lighthouse", "Carousel", "Telescope", "Typewriter", "Orchard", "Platform", "Umbrella",
          "Pillow", "Kettle", "Mirror", "Window", "Garage", "Festival", "Daydream", "Rainfall", "Cassette", "Echo", "Paper", "Velvet", "Marble", "Tunnel", "Ladder", "Voyage", "Picnic", "Sparrow", "Biscuit", "Cinema", "Balcony", "Subway", "Moonlight", "Matchbox"]
COLJ = ["赤い", "青い", "白い", "黒い", "緑の", "金色の", "銀色の", "灰色の", "桃色の", "紫の", "茶色い", "透き通った"]
PLJ = ["高円寺", "下北沢", "新宿", "渋谷", "中野", "吉祥寺", "梅田", "心斎橋", "栄", "博多", "札幌", "仙台", "三宮", "横浜", "江ノ島", "阿佐ヶ谷", "西荻", "北千住", "三軒茶屋", "荻窪"]


def mk_artist(r, style, ai_mode):
    rap = ["KAGE", "DOGMA", "ZERO番地", "TAKUMI", "B-LINE", "RYO-Z", "砂利", "SHIN", "BLOCK", "商店街MC", "N.O.W.", "KOZO", "DOBU", "RAIJIN", "NORIKA", "銀座ボーイ", "A-KIRA", "SEVEN-O", "MC豆腐", "裏通りMC",
           "TETSU-9", "ガレージ田中", "JIN-X", "IKKI", "路地裏TOKYO", "Q-ZONE", "KENTO-B", "夜明けMC", "ZAN", "平成ボーイ"]
    beat = ["mizutama", "nocturne_k", "ぬるま湯P", "lowbit", "aoi_loop", "kurage", "夜更かしP", "sleepwave", "mono_tone", "hanabi_p", "paper_moon", "zzz-tape", "cassette_dog", "烏龍P", "midori", "sunday_loop",
            "ghost_note", "ふとんP", "tsukimi", "dawn_fm", "コタツP", "static_cat", "okapi", "nami_beat", "n0ise_girl"]
    dj = ["DJ NAGI", "DJ 6AM", "midnight_dj", "DJ ひとやすみ", "K-SYNC", "DJ KOMA", "DJ ROKU", "終電DJ", "DJ TOFU", "DJ UMEBOSHI", "NIGHT BUS", "DJ 朝霧", "DJ ZERO-ONE", "BPM田中", "DJ SOUBA", "DJ KAIWAI"]
    duo = ["ふたりのノイズ", "ハニートースト", "ミルクと地図", "月と砂", "午後のふたり", "ぬるい二人", "ソーダとガム", "二人羽織", "Pocket Radio", "ペンギンと郵便", "砂糖と塩", "豆腐と傘", "夜ふかしクラブ",
           "ふたごの信号", "Cherry & Mint", "雨のち曇り", "ミルクティー革命", "あんことバター", "Tape & Glue", "ハンドクリーム"]
    ai_open = ["VIRA", "NOA-7", "ミラ", "ELYSIA", "SYNTH-子", "AOI.exe", "ルミナ", "Echo-9", "KOKORO-0", "NEO-ALICE", "ユリアOS", "Lyra_v2", "MIKU-β", "SORA.ai", "ヒビキ.model", "ZERO-ONE"]
    ai_hide = ["水瀬ユキ", "KAEDE", "ひなた", "luna_ao", "SORA", "天野ミコト", "Rin", "mio_", "桜庭アヤ", "nanase", "ユズハ", "HARU", "夏川ノノ", "雨宮ミナ", "kanata", "ソラネ"]
    if style == "solo":
        x = r.random()
        if x < 0.1: return r.choice(GIV2)
        if x < 0.5: return r.choice(SUR2) + r.choice(GIV2)
        if x < 0.65: return r.choice(GIV2) + "・" + r.choice(SUR2)
        if x < 0.8: return r.choice(GIV2) + r.choice(["と", "の"]) + r.choice(NOUN2)
        return r.choice(ROMA) + r.choice(["", "_", ".", "0", "7", "x"]) + r.choice(["", "k", "n", "s", "ko", "ya", "ta"]) + r.choice(["", "", "99", "_"])
    if style in ("band", "inst"):
        x = r.random()
        if x < 0.14: return r.choice(ADJ2) + r.choice(NOUN2)
        if x < 0.20: return r.choice(NOUN2) + "ズ"
        if x < 0.27: return r.choice(NOUN2) + "と" + r.choice(NOUN2)
        if x < 0.34: return "THE " + r.choice(EADJ + EADJ2) + " " + r.choice(ENOUN + ENOUN2)
        if x < 0.40: return (r.choice(EADJ + EADJ2) + " " + r.choice(ENOUN + ENOUN2)).lower()
        if x < 0.45: return r.choice(NUMW) + r.choice(["の", "", "の"]) + r.choice(NOUN2)
        if x < 0.50: return r.choice(NOUN2) + "が" + r.choice(VERBP)
        if x < 0.55: return r.choice(GIV2) + "と" + r.choice(NOUN2) + "たち"
        if x < 0.60: return r.choice(COLJ) + r.choice(NOUN2)
        if x < 0.65: return r.choice(PLJ) + r.choice(["の", ""]) + r.choice(NOUN2)
        if x < 0.70: return r.choice(GIV2) + " & The " + r.choice(ENOUN + ENOUN2)
        if x < 0.75: return r.choice(ENOUN2) + " " + r.choice(ENOUN2)
        if x < 0.79: return r.choice(NOUN2) + " " + r.choice(["CLUB", "BAND", "ORCHESTRA", "SYSTEM", "UNION", "PROJECT", "SOCIETY", "RADIO"])
        if x < 0.83: return r.choice(NOUN2) + r.choice(["は", "も"]) + r.choice(["まだ眠っている", "どこにもない", "終わらない", "雨に濡れた", "ぬるい", "遠い", "ちょっと怖い"])
        if x < 0.87: return r.choice(ROMA).capitalize() + " " + r.choice(ENOUN2).title()
        if x < 0.91: return r.choice(["午後", "深夜", "早朝", "放課後", "日曜"]) + r.choice(["の", ""]) + r.choice(["ひみつ基地", "音楽室", "天文台", "ボート", "ラジオ体操", "売店", "文化祭", "交換日記"])
        if x < 0.95: return r.choice(ENOUN2).upper() + r.choice(["", "-", "_"]) + r.choice(["X", "9", "ZERO", "ONE", "MK2", "B"])
        return r.choice(KATA) + r.choice(KATA)
    if style == "rap":
        x = r.random()
        if x < 0.3: return r.choice(rap)
        if x < 0.6: return r.choice(ROMA).upper() + r.choice(["-Z", "-X", "K", " ZERO", "MC", "-B", " THE RAPPER", "-9"])
        if x < 0.8: return r.choice(SUR2) + r.choice(["MC", "ラボ", " from " + r.choice(NOUN2), "兄弟"])
        return r.choice(NOUN2) + r.choice(["MC", "ボーイ", "LAB", "GANG", "組"])
    if style == "beat":
        x = r.random()
        if x < 0.25: return r.choice(beat)
        if x < 0.6: return r.choice(ROMA) + r.choice(["_p", "_beat", "_loop", "_wave", "P", ".fm", "_lofi", "_tape"])
        return r.choice(EADJ).lower() + "_" + r.choice(ENOUN).lower()[:-1]
    if style == "dj":
        x = r.random()
        if x < 0.25: return r.choice(dj)
        if x < 0.6: return "DJ " + r.choice(ROMA).upper()
        if x < 0.85: return "DJ " + r.choice(NOUN2)
        return r.choice(NOUN2) + "DJ"
    if style == "duo":
        x = r.random()
        if x < 0.25: return r.choice(duo)
        if x < 0.7: return r.choice(NOUN2) + r.choice(["と", "&", "×", "とその"]) + r.choice(NOUN2)
        return r.choice(EADJ).title() + " & " + r.choice(ENOUN).title()[:-1]
    if ai_mode == "公表":
        x = r.random()
        if x < 0.25: return r.choice(ai_open)
        if x < 0.55: return r.choice(ROMA).upper() + "-" + str(r.randint(1, 99))
        if x < 0.8: return r.choice(GIV2) + r.choice([".exe", ".ai", ".model", "OS", "-β", "_v" + str(r.randint(2, 9))])
        return "NEO-" + r.choice(ROMA).upper() + r.choice(["", "", "-0"])
    x = r.random()
    if x < 0.25: return r.choice(ai_hide)
    if x < 0.65: return r.choice(SUR2) + r.choice(GIV2)
    if x < 0.85: return r.choice(GIV2) + r.choice(["", "", "", "_", "."]) + r.choice(["", "ん", "ちゃん", "ネ"])
    return r.choice(ROMA) + r.choice(["_", "", "."]) + r.choice(["", "k", "o", "ne"])


# もじり名(架空のバンド名。実在のバンドを洒落で連想させる名前だけで、曲や歌詞は一切使わない)
# (もじり名, 元ネタ, 対象形態, 登場しうる最も早い時代)  形態: b=バンド i=インスト d=ユニット r=ラッパー e=トラックメイカー j=DJ s=ソロ
CM = {"b": "band", "i": "inst", "d": "duo", "r": "rap", "e": "beat", "j": "dj", "s": "solo"}
PUNS_RAW = [
    ("JUMP OF CHICKEN", "BUMP OF CHICKEN", "b", 1), ("BUMP OF KITCHEN", "BUMP OF CHICKEN", "b", 1),
    ("ノーザンオールスターズ", "サザンオールスターズ", "b", -1), ("サザンカオールスターズ", "サザンオールスターズ", "b", -1),
    ("Ms.Children", "Mr.Children", "b", 1), ("Mr.Chilled", "Mr.Children", "b", 1),
    ("スピッツァ", "スピッツ", "b", 0), ("ぐるり", "くるり", "bi", 1), ("ゆす", "ゆず", "d", 1),
    ("コブクリ", "コブクロ", "d", 2), ("ONE OK ROCKET", "ONE OK ROCK", "b", 2),
    ("back numbers", "back number", "b", 3), ("Mrs. GREEN PINEAPPLE", "Mrs. GREEN APPLE", "b", 3),
    ("SEKAI NO HAJIMARI", "SEKAI NO OWARI", "bd", 3), ("サカナアクション", "サカナクション", "bej", 3),
    ("Queen Gnu", "King Gnu", "b", 3), ("YORUASOBI", "YOASOBI", "de", 4),
    ("Official髭女dism", "Official髭男dism", "b", 3), ("ASIAN FU-KUNG GENERATION", "ASIAN KUNG-FU GENERATION", "b", 2),
    ("11-FEET", "10-FEET", "b", 1), ("凛として晴れ", "凛として時雨", "bi", 2),
    ("Imperfume", "Perfume", "dej", 2), ("RADWIMPY", "RADWIMPS", "b", 2),
    ("ELLEGARDENER", "ELLEGARDEN", "b", 1), ("L'Arc~en~Sel", "L'Arc~en~Ciel", "b", 0),
    ("サンマスター", "サンボマスター", "b", 2), ("Sleepy Nuts", "Creepy Nuts", "dr", 3),
    ("RHYMESTEAR", "RHYMESTER", "r", 1), ("THE BLUE HEATERS", "THE BLUE HEARTS", "b", 0),
    ("GRAY", "GLAY", "b", 1), ("LUNA SEE", "LUNA SEA", "b", 1), ("DREAM COME TRUCK", "DREAMS COME TRUE", "db", 1),
    ("スキマスイッチョ", "スキマスイッチ", "d", 2), ("andyamori", "andymori", "b", 2),
    ("C'z", "B'z", "bd", 1), ("Y JAPAN", "X JAPAN", "b", 0), ("THE ARFEE", "THE ALFEE", "b", -1),
    ("東京事案", "東京事変", "b", 2), ("RIP SLIME", "RIP SLYME", "r", 1), ("ORANGE RANGER", "ORANGE RANGE", "b", 2),
    ("Aqua Times", "Aqua Timez", "b", 2), ("flumpoo", "flumpool", "b", 2), ("UVERwood", "UVERworld", "b", 2),
    ("BLUE UNCOUNT", "BLUE ENCOUNT", "b", 3), ("[Alexandoros]", "[Alexandros]", "b", 3), ("SPYFAIR", "SPYAIR", "b", 3),
    ("WOMAN WITH A MISSION", "MAN WITH A MISSION", "b", 3), ("05 Limited Sazabys", "04 Limited Sazabys", "b", 3),
    ("indigo la Bed", "indigo la End", "b", 3), ("ゲスの極みお嬢", "ゲスの極み乙女", "b", 3),
    ("クリープバイブ", "クリープハイプ", "b", 3), ("フジファブリクス", "フジファブリック", "b", 2),
    ("ストレイトナー", "ストレイテナー", "b", 2), ("the pillowcases", "the pillows", "b", 0),
    ("銀杏GIRLZ", "銀杏BOYZ", "b", 2), ("毛皮のマリーナ", "毛皮のマリーズ", "b", 3),
    ("神聖かまって欲しいちゃん", "神聖かまってちゃん", "be", 3), ("syrup17g", "syrup16g", "b", 2),
    ("8mm Parabellum Bullet", "9mm Parabellum Bullet", "b", 2), ("JUDY AND MARRY", "JUDY AND MARY", "b", 0),
    ("THE YELLOW DONKEY", "THE YELLOW MONKEY", "b", 0), ("THE MAD CAPSULE SUPERMARKETS", "THE MAD CAPSULE MARKETS", "b", 1),
    ("ウルフルネス", "ウルフルズ", "b", 0), ("エレファントカシマシマ", "エレファントカシマシ", "b", 0),
    ("ユニゴーン", "ユニコーン", "b", 0), ("スーパーカブ", "スーパーカー", "b", 1), ("ナンバープレート", "ナンバーガール", "b", 1),
    ("ZAZEN GIRLS", "ZAZEN BOYS", "bi", 2), ("UNISON SQUARE PARK", "UNISON SQUARE GARDEN", "b", 3),
    ("THE ORAL CHOCOLATES", "THE ORAL CIGARETTES", "b", 3), ("SUPER WEAVER", "SUPER BEAVER", "b", 3),
    ("WANIMAL", "WANIMA", "b", 3), ("KANA-BOOM", "KANA-BOON", "b", 3), ("ヤバイ靴下屋さん", "ヤバイTシャツ屋さん", "b", 3),
    ("赤黄色社会", "緑黄色社会", "b", 3), ("Saucy Cat", "Saucy Dog", "b", 3), ("ペンネえんぴつ", "マカロニえんぴつ", "b", 3),
    ("go!go!chocolates", "go!go!vanillas", "b", 3), ("Novelbrite", "Novelbright", "b", 4), ("sumiko", "sumika", "b", 3),
    ("Omoinotaki", "Omoinotake", "b", 3), ("打首獄門同窓会", "打首獄門同好会", "b", 3), ("パスピエル", "パスピエ", "b", 3),
    ("the cellphones", "the telephones", "be", 2), ("Basket Ball Bear", "Base Ball Bear", "b", 2),
    ("Dragon Cash", "Dragon Ash", "br", 1), ("Hi-SUBSTANDARD", "Hi-STANDARD", "b", 1), ("BRAHMIN", "BRAHMAN", "b", 1),
    ("MONGOL900", "MONGOL800", "b", 2), ("ケツメイジ", "ケツメイシ", "rd", 2), ("シルバーボンバー", "ゴールデンボンバー", "bd", 3),
    ("電気グルメ", "電気グルーヴ", "dej", 0), ("ブルー・マジック・オーケストラ", "イエロー・マジック・オーケストラ", "eb", -1),
    ("capsules", "capsule", "de", 2), ("KICK THE TRASH CAN CREW", "KICK THE CAN CREW", "r", 1), ("m-fly", "m-flo", "dre", 2),
    ("BAD SHOP", "BAD HOP", "r", 4), ("SHAKKAZOMBIES", "SHAKKAZOMBIE", "r", 1), ("Scha Dara Part", "Scha Dara Parr", "r", 0),
    ("BUDDHA BRANDY", "BUDDHA BRAND", "r", 1), ("餓鬼ジャーキー", "餓鬼レンジャー", "r", 1),
    ("BUCK-TIC TAC", "BUCK-TICK", "b", 0), ("the Gazebo", "the GazettE", "b", 2), ("Janne Da Ark", "Janne Da Arc", "b", 1),
    ("TUBA", "TUBE", "b", 1), ("ゴスペルーズ", "ゴスペラーズ", "b", 1), ("Kiroru", "Kiroro", "d", 1),
    ("いきものがおり", "いきものがかり", "b", 2), ("MONKEY MAGIC", "MONKEY MAJIK", "b", 2), ("湘南の追い風", "湘南乃風", "br", 2),
    ("大阪スカパラダイスオーケストラ", "東京スカパラダイスオーケストラ", "b", 1), ("Glim Spunky", "Glim Spanky", "d", 3),
    ("SCAMDAL", "SCANDAL", "b", 3), ("amazarashii", "amazarashi", "b", 3), ("the band a part", "the band apart", "b", 2),
    ("ポルノグラフィック", "ポルノグラフィティ", "db", 1), ("ハンバーグ ハンバーグ", "ハンバート ハンバート", "d", 2),
    ("MOMO", "MONO", "i", 1), ("toes", "toe", "bi", 2), ("envi", "envy", "bi", 1), ("LIGHT", "LITE", "i", 3),
    ("Mouse on the Keyboard", "Mouse on the Keys", "i", 3), ("tricote", "tricot", "bi", 3), ("downey", "downy", "i", 1),
    ("Doris", "Boris", "i", 1), ("Acid Mothers Shrine", "Acid Mothers Temple", "i", 1),
    ("Every Little Thin", "Every Little Thing", "d", 1), ("glove", "globe", "de", 1), ("TRP", "TRF", "ed", 1),
    ("危険地帯", "安全地帯", "b", 0), ("TN NETWORK", "TM NETWORK", "eb", 0), ("the brilliant blue", "the brilliant green", "b", 1),
    ("WANTS", "WANDS", "b", 1), ("Hunch Back", "Hump Back", "b", 3), ("Hawaiian7", "Hawaiian6", "b", 2),
    ("nano.RIPEN", "nano.RIPE", "d", 3), ("Awesome Country Club", "Awesome City Club", "b", 3), ("Suchmoss", "Suchmos", "b", 3),
    ("never old beach", "never young beach", "b", 3), ("Yogee Old Waves", "Yogee New Waves", "b", 3), ("cerori", "cero", "b", 3),
    ("Templay", "Tempalay", "b", 3), ("ネクラトーキー", "ネクライトーキー", "b", 3), ("ずっと真昼でいいのに。", "ずっと真夜中でいいのに。", "be", 3),
    ("ヒルシカ", "ヨルシカ", "d", 3), ("FIVE OLD NEW", "FIVE NEW OLD", "b", 4), ("Chilly Beans.", "Chilli Beans.", "b", 4),
    ("SEVEN LOUNGE", "SIX LOUNGE", "b", 3), ("Old Age Factory", "Age Factory", "b", 3), ("Ivy to Honest Game", "Ivy to Fraudulent Game", "b", 3),
    ("Dos Monkeys", "Dos Monos", "r", 3), ("tofubeets", "tofubeats", "ej", 3), ("TeddyLoad", "TeddyLoid", "ej", 3),
    ("Fantastic Plastic Bag", "Fantastic Plastic Machine", "ej", 1), ("Pizzicato Six", "Pizzicato Five", "ed", 0),
    ("GRAPEWINE", "GRAPEVINE", "b", 1), ("BANK BAND", "Bank Band", "b", 2),
    # ---- 70年代・80年代(アングラ、フォーク、ニューミュージック、パンク、バンドブーム)
    ("頭脳探偵", "頭脳警察", "b", -1), ("あぶらだし", "あぶらだこ", "bi", 0), ("あぶらだこ焼き", "あぶらだこ", "bi", 0),
    ("はっぴいえんどう", "はっぴいえんど", "b", -1), ("内道", "外道", "b", -1), ("村七分", "村八分", "b", -1),
    ("RCサクセスション", "RCサクセション", "b", -1), ("キャロット", "キャロル", "b", -1),
    ("サディスティック・ミカン・バンド", "サディスティック・ミカ・バンド", "b", -1), ("五人囃子", "四人囃子", "bi", -1),
    ("ゴダイコ", "ゴダイゴ", "b", -1), ("アップタウン・ブギウギ・バンド", "ダウンタウン・ブギウギ・バンド", "b", -1),
    ("ERB", "ARB", "b", -1), ("かぐや王子", "かぐや姫", "d", -1), ("オンコース", "オフコース", "d", -1),
    ("ふきのこ", "ふきのとう", "d", -1), ("ムーンハウス", "サンハウス", "b", -1), ("悠歌団", "憂歌団", "b", -1),
    ("ヒヤシンス", "チューリップ", "b", -1), ("アリソ", "アリス", "d", -1),
    ("ガスメーター", "ガスタンク", "b", 0), ("ザ・スターリング", "ザ・スターリン", "b", 0), ("ラフィンヌードル", "ラフィンノーズ", "b", 0),
    ("BOØWAY", "BOØWY", "b", 0), ("リベッカ", "レベッカ", "b", 0), ("プリンス・プリンセス", "プリンセス・プリンセス", "b", 0),
    ("麦麦CLUB", "米米CLUB", "b", 0), ("THE BOOMERANG", "THE BOOM", "b", 0), ("ZAGGY", "ZIGGY", "b", 0),
    ("HOUND CAT", "HOUND DOG", "b", 0), ("爆風ダンプ", "爆風スランプ", "b", 0), ("筋肉少年帯", "筋肉少女帯", "b", 0),
    ("有頂点", "有頂天", "b", 0), ("ストリート・スライダー", "ストリート・スライダーズ", "b", 0), ("THE ODDS", "THE MODS", "b", 0),
    ("孫ばんど", "子供ばんど", "b", -1), ("ヒカシュウ", "ヒカシュー", "be", 0), ("Q-MODEL", "P-MODEL", "be", 0),
    ("ビニールス", "プラスチックス", "be", 0), ("ボ・ガンボ", "ボ・ガンボス", "b", 0), ("非常口", "非常階段", "bi", 0),
    ("ボーダムス", "ボアダムス", "bi", 0), ("少女ナイフ", "少年ナイフ", "b", 0), ("ジュンスキーウォーカーズ", "JUN SKY WALKER(S)", "b", 0),
    ("ゆらゆら共和国", "ゆらゆら帝国", "b", 1), ("THE HIGH-HOWS", "THE HIGH-LOWS", "b", 1), ("ザ・ネアンデルタールズ", "ザ・クロマニヨンズ", "b", 2),
    ("ASPARAGUSS", "ASPARAGUS", "b", 1), ("Your Little Lover", "My Little Lover", "d", 1), ("Do As Finity", "Do As Infinity", "b", 1),
    ("DEER", "DEEN", "b", 1), ("BRADIO", "RADIO", "b", 3), ("ハルカムカイ", "ハルカミライ", "b", 3), ("ハンバーガーズ", "ハンブレッダーズ", "b", 3),
    ("SHISHAMA", "SHISHAMO", "b", 3), ("フレデリカ", "フレデリック", "b", 3), ("キュウソネコカブリ", "キュウソネコカミ", "b", 3),
    # ---- 2000年代〜10年代のロキノン系・下北沢系・関西オルタナ系
    ("ハヌマーム", "ハヌマーン", "b", 2), ("ハヌマーニャ", "ハヌマーン", "b", 2), ("9otto", "8otto", "b", 2), ("ART-COLLEGE", "ART-SCHOOL", "b", 2),
    ("Going Over Ground", "Going Under Ground", "b", 2), ("ゴゴゴSP", "ガガガSP", "b", 2), ("モーモーリリギャバン", "モーモールルギャバン", "b", 3),
    ("グッドイブニングアメリカ", "グッドモーニングアメリカ", "b", 3), ("HE'S", "SHE'S", "b", 3), ("Unlucky Kilimanjaro", "Lucky Kilimanjaro", "be", 3),
    ("cinema crew", "cinema staff", "b", 3), ("LAMP IN TERRACE", "LAMP IN TERREN", "b", 3), ("Dizzy Moonfist", "Dizzy Sunfist", "b", 3),
    ("フタリエ", "ヒトリエ", "b", 3), ("Non Stop Turtle", "Non Stop Rabbit", "b", 3), ("My Hair is Good", "My Hair is Bad", "b", 3),
    ("フラワーカンパニーＺ", "フラワーカンパニーズ", "b", 1), ("GOING UNSTEADY", "GOING STEADY", "b", 1), ("POLYSIXX", "POLYSICS", "be", 2),
    ("BEAT CRUSADER", "BEAT CRUSADERS", "b", 2), ("FOUND IN TIME", "LOST IN TIME", "b", 2), ("ベースウルフ", "ギターウルフ", "b", 1),
    ("ミッシェル・ドン・エレファント", "ミッシェル・ガン・エレファント", "b", 1), ("THEE MICHELLE GUN ELEPHONE", "THEE MICHELLE GUN ELEPHANT", "b", 1),
    ("Blankey Jet Town", "Blankey Jet City", "b", 1), ("bloodthirsty bakers", "bloodthirsty butchers", "b", 1), ("western youth", "eastern youth", "b", 1),
    ("昼の本気ダンス", "夜の本気ダンス", "b", 3), ("ナードマグロ", "ナードマグネット", "b", 3),
    ("ストレイト・テナー", "ストレイテナー", "b", 2), ("HiGE", "髭(HiGE)", "b", 2), ("鬚", "髭(HiGE)", "b", 2),
]
PUNS_RAW += [
    # 同じ元ネタの別バリエーション(有名どころは複数)
    ("ASIAN KUNG-FU DEGENERATION", "ASIAN KUNG-FU GENERATION", "b", 2), ("ASIAN KOMBU-FOOD GENERATION", "ASIAN KUNG-FU GENERATION", "b", 2), ("アジアの昆布ジェネレーション", "ASIAN KUNG-FU GENERATION", "b", 2),
    ("ナンバーボーイ", "ナンバーガール", "b", 1), ("ナンバープレートガール", "ナンバーガール", "b", 1), ("ナンバーガーリー", "ナンバーガール", "b", 1), ("ナンバーガラ", "ナンバーガール", "bi", 1),
    ("くるみ", "くるり", "b", 1), ("スピッツァー", "スピッツ", "b", 0), ("サカナモーション", "サカナクション", "bej", 3), ("ゲスの極みおとめ座", "ゲスの極み乙女", "b", 3),
    ("ミッシェル・ガム・エレファント", "ミッシェル・ガン・エレファント", "b", 1), ("ブランケット・ジェット・シティ", "Blankey Jet City", "b", 1), ("ハヌマーケット", "ハヌマーン", "b", 3),
    ("あぶらだし", "あぶらだこ", "bi", 0), ("脳みそ警察", "頭脳警察", "b", -1), ("ELLE GARDEN", "ELLEGARDEN", "b", 1), ("BUMP OF CHICKEN NANBAN", "BUMP OF CHICKEN", "b", 1),
    ("ミスチルド", "Mr.Children", "b", 1), ("サザンクロス・オールスターズ", "サザンオールスターズ", "b", -1), ("ザ・ブルーハーツ・ガーデン", "THE BLUE HEARTS", "b", 0),
    # 70年代
    ("ザ・チーターズ", "ザ・タイガース", "b", -1), ("ザ・スパゲッティーズ", "ザ・スパイダース", "b", -1), ("ザ・テンプラーズ", "ザ・テンプターズ", "b", -1), ("ブルー・ココアーズ", "ブルー・コメッツ", "b", -1),
    ("ゴールデン・カップめん", "ゴールデン・カップス", "b", -1), ("フラワー・ガーデニング・バンド", "フラワー・トラヴェリン・バンド", "bi", -1), ("ジャッキーズ", "ジャックス", "b", -1),
    ("はちみつぱん", "はちみつぱい", "b", -1), ("ソルト・ベイブ", "シュガー・ベイブ", "b", -1), ("薄紫", "紫", "b", -1), ("ツイストパン", "ツイスト", "b", -1), ("貝バンド", "甲斐バンド", "b", -1),
    ("海老隊", "海援隊", "b", -1), ("チューリップ畑", "チューリップ", "b", -1), ("四人囃子はやし", "四人囃子", "bi", -1),
    # 80年代
    ("ザ・ブースターズ", "ザ・ルースターズ", "b", 0), ("RED WORRIERS", "RED WARRIORS", "b", 0), ("ウィザード", "ウィラード", "b", 0), ("じゃがたらこ", "じゃがたら", "b", 0),
    ("チェックメイツ", "チェッカーズ", "b", 0), ("BARBEQUE BOYS", "BARBEE BOYS", "b", 0), ("ラ・ムーン", "ラ・ムー", "d", 0), ("聖飢魔Ⅲ", "聖飢魔Ⅱ", "b", 0),
    ("EARTHSHAVER", "EARTHSHAKER", "b", 0), ("LOUDNICE", "LOUDNESS", "b", 0), ("SHOW-YOU", "SHOW-YA", "b", 0), ("たまご", "たま", "bd", 0), ("たまねぎ", "たま", "bd", 0),
    ("サンライダーズ", "ムーンライダーズ", "b", 0), ("人間座椅子", "人間椅子", "b", 0), ("人間座布団", "人間椅子", "b", 0), ("ノイバウテン", "アインシュテュルツェンデ・ノイバウテン", "bi", 0),
    ("ザ・スターリン", "ザ・スターリン", "b", 0) if False else ("ザ・スターチン", "ザ・スターリン", "b", 0),
    # 90年代
    ("CHANGE and ASKA", "CHAGE and ASKA", "d", 1), ("白夢", "黒夢", "b", 1), ("SOFA", "SOPHIA", "b", 1), ("MALICE MIXER", "MALICE MIZER", "b", 1), ("DIR EN GREEN", "DIR EN GREY", "b", 1),
    ("T-BONE", "T-BOLAN", "b", 1), ("176R", "175R", "b", 2), ("レミオロメンタイ", "レミオロメン", "b", 2), ("チャットモンチッチ", "チャットモンチー", "b", 2), ("チャットモンブラン", "チャットモンチー", "b", 2),
    ("ACIDWOMAN", "ACIDMAN", "b", 2), ("BEGINNER", "BEGIN", "b", 1), ("かりゆし59", "かりゆし58", "b", 2), ("SOUL'd IN", "SOUL'd OUT", "r", 1), ("somebodyknows+", "nobodyknows+", "r", 2),
    ("ZIGGY STARDUSTBOX", "ZIGGY", "b", 0), ("ザ・バースデー", "The Birthday", "b", 2), ("The Deathday", "The Birthday", "b", 2), ("ミッシェル", "ミッシェル・ガン・エレファント", "b", 1),
    # 00〜10年代
    ("dustbin", "dustbox", "b", 2), ("Fear, and Loathing in Nagoya", "Fear, and Loathing in Las Vegas", "b", 3), ("hotrain", "coldrain", "b", 3), ("Crosswalk", "Crossfaith", "b", 3),
    ("KEYBOARD TALK", "KEYTALK", "b", 3), ("コーラガール", "サイダーガール", "b", 3), ("サイダー男子", "サイダーガール", "b", 3), ("WiSH", "BiSH", "bd", 3), ("yoniger", "yonige", "d", 3),
    ("ドミノ", "ドミコ", "d", 3), ("OKUMOTO'S", "OKAMOTO'S", "b", 3), ("SILENT HIREN", "SILENT SIREN", "b", 3), ("ミツキ屋", "ミツキ", "s", 3), ("ONE OK ROCK STEADY", "ONE OK ROCK", "b", 2),
    ("ストレイテナーズ", "ストレイテナー", "b", 2), ("エレファントカシマシマ", "エレファントカシマシ", "b", 0), ("フジファブリック工場", "フジファブリック", "b", 2), ("毛皮のマリーゴールド", "毛皮のマリーズ", "b", 2),
    ("ずっと真夜中でいいのにね。", "ずっと真夜中でいいのに。", "bd", 4), ("ヨルシカク", "ヨルシカ", "d", 4), ("緑黄色社会人", "緑黄色社会", "b", 4), ("Omoinotake", "Omoinotake", "b", 4) if False else ("Omoinotakeout", "Omoinotake", "b", 4),
    ("Saucy Cat", "Saucy Dog", "b", 3), ("SHISHAMO", "SHISHAMO", "b", 3) if False else ("SHISHAMOO", "SHISHAMO", "b", 3), ("Hump Front", "Hump Back", "b", 3), ("Tempalay", "Tempalay", "b", 3) if False else ("Tempalaugh", "Tempalay", "b", 3),
    ("cero", "cero", "b", 3) if False else ("zero", "cero", "b", 3), ("never young beech", "never young beach", "b", 3), ("Suchmoss", "Suchmos", "b", 3), ("Yogee New Waves", "Yogee New Waves", "b", 3) if False else ("Yoga New Waves", "Yogee New Waves", "b", 3),
    # ソロ(軽い言葉遊びのみ)
    ("米津玄米", "米津玄師", "s", 3), ("あいにゃん", "あいみょん", "s", 3), ("藤井台風", "藤井風", "s", 4), ("星野源泉", "星野源", "s", 2), ("宇多田ヒカゲ", "宇多田ヒカル", "s", 1),
    ("椎名梨", "椎名林檎", "s", 1), ("Vaundo", "Vaundy", "s", 4), ("Adio", "Ado", "s", 4), ("Even", "Eve", "s", 3), ("あいこ", "aiko", "s", 1),
]
PUNS_RAW += [
    ("フリッパーズ・ギョーザ", "フリッパーズ・ギター", "d", 1), ("ORIGINAL LAVE", "ORIGINAL LOVE", "b", 1), ("中村一二三", "中村一義", "s", 1), ("LOVE PSYCHEDELICOLA", "LOVE PSYCHEDELICO", "d", 2),
    ("Cacao", "Cocco", "s", 1), ("UB", "UA", "s", 1), ("barb", "bird", "s", 2), ("MISIO", "MISIA", "s", 1), ("JIJI", "JUJU", "s", 2), ("SEKAI NO HAJIMARI", "SEKAI NO OWARI", "b", 3),
    ("たけのこ帝国", "きのこ帝国", "b", 3), ("Queen Gnu", "King Gnu", "b", 4), ("銀杏GIRLZ", "銀杏BOYZ", "b", 2), ("スガシカバ", "スガシカオ", "s", 1), ("奥田民族", "奥田民生", "s", 1),
    ("斉藤和義理", "斉藤和義", "s", 1), ("山下達磨", "山下達郎", "s", 0), ("竹内まりも", "竹内まりや", "s", 0), ("松任谷由美子", "松任谷由実", "s", -1), ("中島みそき", "中島みゆき", "s", -1),
    ("井上陽炎", "井上陽水", "s", -1), ("かぐや姫路", "かぐや姫", "d", -1), ("ゆずこしょう", "ゆず", "d", 2), ("ゆずぽん", "ゆず", "d", 2), ("コブクロス", "コブクロ", "d", 2), ("ABC48", "AKB48", "d", 2),
    ("イブニング娘。", "モーニング娘。", "d", 1), ("きゃりーぱむぱむ", "きゃりーぱみゅぱみゅ", "s", 3), ("BABYMETAR", "BABYMETAL", "d", 3), ("the HIATUSU", "the HIATUS", "b", 3),
    ("NICO Touches the Wallet", "NICO Touches the Walls", "b", 3), ("superhell", "supercell", "e", 3), ("DECO*28", "DECO*27", "e", 3), ("ヒャダイナモ", "ヒャダイン", "e", 3), ("RISE", "RIZE", "b", 2),
    ("氣志團地", "氣志團", "b", 2), ("ガガガSS", "ガガガSP", "b", 2), ("ミニマムザホルモン", "マキシマム ザ ホルモン", "b", 2), ("Ken Yokohama", "Ken Yokoyama", "s", 2), ("SoM", "SiM", "b", 3),
    ("ねごとば", "ねごと", "b", 3), ("ハルカトミユカ", "ハルカトミユキ", "d", 3), ("People In The Boss", "People In The Box", "b", 3), ("カネコアヤメ", "カネコアヤノ", "s", 4),
    ("崎山蒼紙", "崎山蒼志", "s", 4), ("Awish", "Awich", "r", 4), ("ZORM", "ZORN", "r", 4), ("KOHM", "KOHH", "r", 3), ("般若湯", "般若", "r", 2), ("ZEEBLA", "ZEEBRA", "r", 1), ("DJ KRASH", "DJ KRUSH", "j", 1),
    ("DJ HASEBU", "DJ HASEBE", "j", 2), ("Nujabez", "Nujabes", "e", 2), ("Cornelia", "Cornelius", "e", 1), ("電気グループ", "電気グルーヴ", "ed", 1), ("細野晴巨", "細野晴臣", "s", -1),
    ("坂本龍二", "坂本龍一", "s", 0), ("TUBA", "TUBE", "b", 0), ("GRAY", "GLAY", "b", 1), ("PENICILLUM", "PENICILLIN", "b", 1), ("hid", "hide", "s", 1), ("BUCK-TOCK", "BUCK-TICK", "b", 0),
    ("TRICERABOPS", "TRICERATOPS", "b", 1), ("Hysteric Green", "Hysteric Blue", "b", 1), ("SPEEDY", "SPEED", "d", 1), ("DA PUNK", "DA PUMP", "d", 1), ("SMAT", "SMAP", "d", 1), ("嵐山", "嵐", "d", 2),
    ("ブルー・レディー", "ピンク・レディー", "d", -1), ("キャンディーボーイズ", "キャンディーズ", "d", -1), ("チャンネルズ", "シャネルズ", "b", 0), ("クリスタルクイーン", "クリスタルキング", "b", 0),
    ("THE GOOD-NIGHT", "THE GOOD-BYE", "b", 0), ("危険地帯", "安全地帯", "b", 0), ("麦麦CLUB", "米米CLUB", "b", 0), ("有頂天国", "有頂天", "b", 0), ("ラフィンスマイル", "ラフィン・ノーズ", "b", 0),
    ("The 51 Kaitenz", "The 50 Kaitenz", "b", 2), ("ZARU", "ZARD", "bs", 1), ("SEKAI NO OWARI", "SEKAI NO OWARI", "b", 3) if False else ("世界の終わり、午後三時", "SEKAI NO OWARI", "b", 3),
    ("猫のヤマハ", "ヤマハ", "b", 0) if False else ("ジャックス・ジャック", "ジャックス", "b", -1),
]
PUNS = [(a, b, {CM[x] for x in cs}, e) for a, b, cs, e in PUNS_RAW]
_PRE = ["新生", "元祖", "偽", "ミニ", "スーパー", "ゴールデン", "ポケット", "ネオ", "二代目", "夜の", "裏", "全日本"]
_SUF = ["ズ", "の弟", "2号", "・改", "公式", "ガールズ", "feat.豆腐", " II", "(仮)", "ラジオ", "ファクトリー", "クラブ", "の逆襲", "会議", "電気商会", "オールスターズ"]
_vr = random.Random(777)
PUN_VARS = []
for _a, _b, _cs, _e in PUNS_RAW:
    _seen = set()
    for _i in range(9):
        _x = _vr.random()
        _v = (_vr.choice(_PRE) + _a) if _x < 0.35 else (_a + _vr.choice(_SUF)) if _x < 0.8 else (_vr.choice(_PRE) + _a + _vr.choice(_SUF))
        if _v not in _seen and _v != _a:
            _seen.add(_v); PUN_VARS.append((_v, _b, {CM[k] for k in _cs}, _e))


# ------------------------------------------------------------------ 理由文
REASONS = {
    ('fit', 1): ["{artist}の{pn}性格と{genre}の空気が重なり、聴き手に『嘘のない曲』として届いた", "{genre}に{pn}性格がにじみ出て、曲に説得力があった"],
    ('fit', -1): ["{genre}という路線が{pn}性格の本人の持ち味と噛み合わず、どこか借り物に聞こえた", "{pn}性格に{genre}は少し背伸びで、伝えたいことが曲に乗りきらなかった"],
    ('lyric', 1): ["歌詞の題材『{theme}』が{era}の聴き手の実感とちょうど重なった", "『{theme}』という題材が{pn}性格の本人の言葉で語られ、聴き手に深く刺さった"],
    ('lyric', -1): ["歌詞の題材『{theme}』が{era}の関心とずれていた", "『{theme}』を{pn}性格の本人が歌うことに、聴き手が違和感を覚えた"],
    ('trend', 1): ["{era}で{genre}への注目が高まっていた時期と重なった", "{era}の空気に{genre}の音がちょうどはまった"],
    ('trend', -1): ["{era}では{genre}はすでに流行の外にあり、手に取る人が少なかった", "{era}の聴かれ方と{genre}の音作りが合っていなかった"],
    ('promo_major', 1): ["レーベルの宣伝網が効き、{artist}の名前が一気に届いた", "大きな宣伝費がつき、目立つ場所で曲が流れ続けた"],
    ('promo_indie', 1): ["小さいながらもレーベルの口コミ網が機能した"],
    ('promo_ama', -1): ["宣伝の手段がなく、存在を知ってもらう前に埋もれた", "自分たちで告知するしかなく、届く範囲が狭かった", "口コミが起きる前に、次の話題に押し流された"],
    ('promo_indie', -1): ["流通が小さく、聴きたい人の目に触れる場所に並ばなかった"],
    ('promo_self', -1): ["独立後の宣伝基盤が整っておらず、新作が知られないまま終わった"],
    ('momentum', 1): ["前作の勢いが残っていて、新作を待っていた人が多かった"],
    ('momentum', -1): ["前作の不発で露出が減り、新作の存在自体が知られなかった", "前作が話題にならなかったせいで、新作も目立つ場所に置いてもらえなかった", "前作の不発の印象が残り、新作を試してみる人が少なかった"],
    ('craft', 1): ["細部まで作り込んだ音が評価された", "音の完成度の高さが口コミで広がった"],
    ('craft', -1): ["詰めが甘く、荒削りなまま世に出てしまった", "こだわりすぎて制作が遅れ、旬を逃した"],
    ('sns', 1): ["SNSでの人柄が受け、曲より先に本人のファンが増えた", "口コミが広がり、曲の入口が増えた"],
    ('sns', -1): ["人前に出るのが苦手で、露出が増えなかった", "SNS運用が続かず、話題が続かなかった"],
    ('fans', 1): ["固定ファンが初動を支えた"],
    ('boost', 1): ["直前の露出(出演・タイアップ)の効果が残っていた"],
    ('reach', 1): ["海外での評価が国内にも逆輸入された"],
    ('luck_old', 1): ["有線放送で偶然かかり続け、問い合わせが相次いだ", "深夜のラジオで偶然かかり、翌日リクエストが殺到した"],
    ('luck_net', 1): ["個人サイトの推薦リンクから人が流れ込んだ", "音楽好きのブログで取り上げられた"],
    ('luck_sns', 1): ["有名人が偶然SNSで紹介した", "ライブの一部が切り取られて拡散した", "ダンス動画のBGMに偶然使われた"],
    ('luck', -1): ["リリース日が話題作と重なり、埋もれた", "公開直後に大きなニュースが流れ、話題がかき消された", "直前の機材トラブルでライブが中止になり、告知の機会を逃した"],
    ('ai_new', 1): ["AI音楽がまだ物珍しく、話題性だけでも聴かれた"],
    ('ai_human', 1): ["AI楽曲があふれる中、人間の手触りが逆に新鮮に聞こえた"],
    ('ai', -1): ["似た雰囲気のAI楽曲が大量に出回り、区別されずに埋もれた"],
}
GENERIC = {1: ["目立った要因はないが、タイミングが合った"], -1: ["目立った要因はなく、タイミングが合わなかった"]}


VIRAL = ["深夜のラジオや口コミで曲が広まり、", "個人サイトやブログでの紹介をきっかけに、", "動画の拡散をきっかけに、"]


def fm(c):
    return dict(T="「%s」" % c['last']['title'] if c.get('last') else "", artist=c['artist'], pn=c['P']['n'] + ('' if c['P']['n'] in ('明るい', '暗い') else ('の' if c['P']['n'] == '普通' else 'な')), sns=('SNS' if c['era'] >= 3 else '雑誌やラジオ'), tv=('テレビやネット番組' if c['era'] >= 3 else 'テレビやラジオ番組'), viral=VIRAL[0 if c['era'] <= 1 else (1 if c['era'] == 2 else 2)],
                genre=c['genre'], era=ERAS[c['era']]['short'], theme=c.get('theme', ''), pun=c.get('pun_src') or '')


def pick_theme(c):
    r = c['r']; P = c['P']
    ok = [t for t in THEMES if t.get('era_min', -1) <= c['era']]
    ws = [0.4 + max(0, 2 - abs(P['vibe'] - t['v'])) * 0.6 for t in ok]
    return r.choices(ok, ws)[0]


KINDS = ["シングル", "アルバム", "EP", "配信限定シングル"]
KIND_W = {-1: [4, 3, 0.2, 0], 0: [4, 3, 0.5, 0], 1: [4, 3, 1, 0], 2: [3, 3, 2, 1], 3: [2, 3, 2, 2], 4: [1.5, 3, 2, 3], 5: [1.5, 3, 2, 3.5]}
ORD = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th"]


def fx(c, fame=0, fans=0, mom=0, boost=0, status=None):
    st = c['st']
    st['fame'] = clamp(st['fame'] + fame, 0, 100)
    st['fans'] = clamp(st['fans'] + fans, 0, 100)
    st['mom'] = clamp(st['mom'] + mom, -1.5, 1.5)
    st['boost'] = clamp(st['boost'] + boost, 0, 2)
    st['peak'] = max(st['peak'], st['fame'])
    if status:
        st['status'] = status


def do_release(c):
    r = c['r']; st = c['st']; P = c['P']; era = c['era']; S = STYLES[c['style']]
    i = len(c['hist'])
    if i > 0:
        c['year'] += r.randint(1, 2)
    kind = r.choice(["シングル", "EP", "シングル"]) if i == 0 else r.choices(KINDS, KIND_W[era])[0]
    c['cnt'][kind] = c['cnt'].get(kind, 0) + 1
    ordn = ORD[min(c['cnt'][kind] - 1, 6)]
    title = mk_title(r, S['ai'])
    theme = pick_theme(c)
    c['theme'] = theme['n']
    pres = [x for x in theme['pre'] if era >= 3 or not any(k in x for k in ('メッセージ', '画面越し'))] or theme['pre']
    premise = r.choice(pres).format(time=r.choice(TIME), place=r.choice(PLACE), thing=r.choice(THING))
    status = st['status']
    f = {}
    f['fit'] = 0.4 * (2 - abs(P['vibe'] - GENRE_VIBE[c['genre']]))
    f['lyric'] = 0.3 * (2 - abs(P['vibe'] - theme['v'])) - 0.2 + 0.6 * THEME_TREND[(theme['n'], era)]
    f['trend'] = 0.8 * TREND[(c['genre'], era)]
    pk = {"メジャー": ('promo_major', 0.8), "インディーズ": ('promo_indie', -0.2), "アマチュア": ('promo_ama', -0.8), "自主(再出発)": ('promo_self', -0.5)}[status]
    f[pk[0]] = pk[1]
    f['momentum'] = st['mom']
    f['craft'] = 0.25 * P['perf'] + r.gauss(0, 0.35) + (0.2 if c.get('ai_use') == 'assist' else 0)
    snsw = {-1: 0.0, 0: 0.0, 1: 0.0, 2: 0.2, 3: 0.6, 4: 0.8, 5: 0.7}[era]
    f['sns'] = snsw * 0.35 * P['soc']
    f['fans'] = st['fans'] * 0.01
    f['boost'] = st['boost']
    if 'abroad_ok' in st['tags']:
        f['reach'] = 0.5
    ln = r.gauss(0, 1.1)
    lk = 'luck_old' if era <= 1 else ('luck_net' if era == 2 else 'luck_sns')
    f[lk if ln > 0 else 'luck'] = ln
    if S['ai']:
        f['ai_new' if era == 4 else 'ai'] = 0.5 if era == 4 else -0.9
    elif era == 5:
        f['ai_human'] = 0.4 + (0.3 if 'human_pledge' in st['tags'] else 0)
    total = sum(f.values()) + 0.2
    tier = sum(1 for t in TH if total >= t)
    items = sorted(f.items(), key=lambda kv: kv[1])
    if tier >= 2:
        cand = [k for k, v in reversed(items) if v > 0.15]
        sign = 1
    elif tier == 1:
        cand = [k for k, v in reversed(items) if v > 0.1 and k in ('fit', 'craft', 'fans', 'lyric', 'sns')]
        sign = 1
    else:
        cand = [k for k, v in items if v < -0.15]
        sign = -1
    cand = [k for k in cand if (k if not k.startswith('luck') else 'luck', sign) in REASONS or (k, sign) in REASONS]
    if cand:
        key = cand[0] if (len(cand) == 1 or r.random() < 0.7) else cand[1]
        rk = (key, sign)
        if rk not in REASONS:
            rk = ('luck', sign) if key.startswith('luck') else None
        reason = r.choice(REASONS[rk]).format(**fm(dict(c, last=None))) if rk else r.choice(GENERIC[sign])
        if r.random() < 0.4: reason = reason.rstrip('。') + '。' + gen_vocab.reason(r, sign > 0, c['era'])
    else:
        key = 'none'
        reason = r.choice(GENERIC[sign])
    # ヒットの形・外した形(歌詞に絡む)
    if tier >= 2:
        forms = [x for x in theme['hit'] if (era >= 3 or not any(k in x for k in ('SNS', '動画', '再生数'))) and (era >= 0 or 'カラオケ' not in x) and (era >= 1 or 'フェス' not in x)] or ["ラジオと口コミで少しずつ広まった"]
        form = r.choice(forms)
        if S['ai'] and tier >= 3 and r.random() < 0.3:
            form += "。AIが書いたとは思えない一行が切り取られて話題になった"
    elif tier == 0 and r.random() < 0.45:
        form = r.choice(theme['flop'])
    elif tier == 1:
        form = "一部の聴き手の間でだけ深く刺さり、口コミで静かに広まった"
    else:
        form = None
    if S['ai'] and tier <= 1 and r.random() < 0.35:
        form = "歌詞が無難で、誰の曲でもあり得るように聞こえた"
    scale = 1.2 if kind == "アルバム" else (0.8 if kind == "EP" else 1.0)
    fd = FAME_D[tier] * (scale if FAME_D[tier] > 0 else 1)
    fx(c, fame=fd, fans=FANS_D[tier], mom=0)
    st['mom'] = clamp(0.5 * st['mom'] + MOM_D[tier], -1.5, 1.5)
    st['boost'] *= 0.6
    rec = dict(kind=kind, ord=ordn, title=title, year=c['year'], tier=tier, theme=theme['n'], premise=premise,
               reason=reason, rkey=key, form=form, label=status)
    c['hist'].append(rec)
    c['last'] = rec
    return rec


# ------------------------------------------------------------------ 転機(予期せぬ出来事)
EVENTS = []


def ev(id, w, cond):
    def deco(fn):
        EVENTS.append((id, w, cond, fn))
        return fn
    return deco


def T(c): return "「%s」" % c['last']['title']
def lt(c): return c['last']['tier']
def tags(c): return c['st']['tags']
def live(c): return STYLES[c['style']]['live']
def isai(c): return STYLES[c['style']]['ai']


@ev("drama_theme", 3, lambda c: lt(c) >= 2 and c['st']['fame'] >= 15 and 'tieup' not in tags(c))
def _(c):
    tags(c).add('tieup'); fx(c, fame=12, mom=0.8)
    return c['r'].choice(["ドラマの主題歌に抜擢。脚本家が学生時代から%sを聴いていた、という縁だった。" % T(c),
                          "ドラマの主題歌に抜擢。プロデューサーが通勤中に%sを聴いて、その場で決めたという。" % T(c)])


@ev("cm_song", 2, lambda c: lt(c) >= 3 and 'cm' not in tags(c))
def _(c):
    tags(c).add('cm'); fx(c, fame=8, mom=0.4)
    return "飲料CMに%sが起用された。制作会社が、%sの空気が商品の世界観に合うと判断したため。" % (T(c), c['genre'])


@ev("viral_old", 1.5, lambda c: c['era'] >= 3 and any(h['tier'] == 0 and h is not c['last'] and not h.get('revived') for h in c['hist']))
def _(c):
    old = [h for h in c['hist'] if h['tier'] == 0 and h is not c['last'] and not h.get('revived')]
    h = c['r'].choice(old); h['revived'] = True; h['tier'] = min(5, h['tier'] + 2)
    fx(c, fame=10, mom=0.6)
    return "数年前に不発だった「%s」が、ダンス動画のBGMとして突然広まる。ある配信者が曲の一部を気に入って使い続けたのがきっかけで、この曲は『のちに再評価された』作品になった。" % h['title']


@ev("overseas_buzz", 2, lambda c: c['era'] >= 3 and lt(c) >= 1 and 'overseas_buzz' not in tags(c))
def _(c):
    tags(c).add('overseas_buzz'); fx(c, fame=8, mom=0.4)
    return "海外のリスナーが動画サイトで%sを見つけ、コメント欄が外国語で埋まる。有志が付けた字幕がきっかけだった。" % T(c)


@ev("viral_clip", 2, lambda c: c['era'] >= 3 and live(c) and lt(c) >= 1)
def _(c):
    fx(c, fame=6, mom=0.3)
    return "ライブの切り抜き映像が拡散。曲より先に、客席でたまたま映った観客の反応が話題になり、そこから曲に流れた人が多かった。"


@ev("taiban", 3, lambda c: live(c) and c['st']['status'] in ("アマチュア", "インディーズ") and lt(c) >= 1 and 'taiban' not in tags(c))
def _(c):
    tags(c).add('taiban'); fx(c, fame=6, fans=6, mom=0.4)
    return "格上のバンドとの対バンが決まる。先方のメンバーが%sを個人的に気に入って、指名してくれた。" % T(c)


@ev("fes_sub", 2, lambda c: c['era'] >= 1 and live(c) and lt(c) >= 2 and 'fes_sub' not in tags(c))
def _(c):
    tags(c).add('fes_sub'); fx(c, fame=10, fans=4, mom=0.6)
    return "夏フェスで出演者の急な欠場が出て、代役として出演。短い持ち時間で観客を掴み、一気に名前が知られた。"


@ev("local_hero", 2, lambda c: lt(c) == 2 and c['st']['status'] != "メジャー" and 'local_hero' not in tags(c))
def _(c):
    tags(c).add('local_hero'); fx(c, fame=4, fans=8)
    return "地元のプロスポーツチームの応援歌に%sが採用され、地元でだけ絶大な知名度を得る。" % T(c)


@ev("provide_song", 2, lambda c: lt(c) >= 1 and 'songwriter' not in tags(c) and 'provide_done' not in tags(c))
def _(c):
    tags(c).add('songwriter'); fx(c, fame=6, mom=0.2)
    return "他のアーティストへ楽曲を提供。提供先が売れて、本人名義よりそちらの曲の方が有名になった。"


@ev("become_producer", 3, lambda c: 'songwriter' in tags(c) and len(c['hist']) >= 4 and c['st']['fame'] < 60)
def _(c):
    c['st']['stop'] = 'producer'
    return "提供の依頼が増え、自分で歌うより裏方の方が向いていると気づく。プロデューサー・作曲家に専念することにした。"


@ev("manga_turn", 0.15, lambda c: len(c['hist']) >= 3 and c['style'] != 'ai_pure' and c['seed'] % 5 == 0)
def _(c):
    c['st']['stop'] = 'illustrator'
    return "歌詞カードに添えていた絵が評判になり、他のバンドのジャケットやグッズの依頼が増える。気づけば本業はイラストレーター(のちに漫画家)になっていた。"


@ev("actor_turn", 1, lambda c: not isai(c) and c['st']['fame'] >= 40 and 'actor' not in tags(c))
def _(c):
    tags(c).add('actor'); fx(c, fame=8)
    return "MVでの演技が評判になり、映画監督から出演を依頼される。音楽を続けつつ、俳優としての仕事も増えた。"


@ev("politics", 1, lambda c: not isai(c) and (c['style'] == 'rap' or 'local_hero' in tags(c)) and len(c['hist']) >= 3 and 'politics' not in tags(c))
def _(c):
    tags(c).add('politics')
    if c['r'].random() < 0.5 + c['st']['fans'] * 0.004:
        c['st']['stop'] = 'politician'
        return "地元の商店街の応援歌を作った縁で、商店街の人たちに『出てみないか』と推され、市議会議員選挙に出馬。当選し、音楽は議員の合間の活動になった。"
    fx(c, fame=-3, mom=-0.3)
    return "商店街の人たちに推されて市議会議員選挙に出馬したが、わずかな票差で落選。その経験を曲にして音楽に戻った。"


@ev("radio_dj", 2, lambda c: c['style'] != 'ai_pure' and c['P']['soc'] >= 2 and lt(c) >= 1 and 'radio' not in tags(c))
def _(c):
    tags(c).add('radio'); fx(c, fame=10, mom=0.4)
    return "トークの面白さが先に評判になり、ラジオのパーソナリティに起用される。番組が人気になり、曲が『ラジオの人の曲』として聴かれるようになった。"


@ev("teacher", 2, lambda c: not isai(c) and c['st']['status'] != "メジャー" and c['st']['fame'] < 30 and len(c['hist']) >= 4 and 'daywork' not in tags(c))
def _(c):
    tags(c).add('daywork'); fx(c, fame=3, fans=5)
    return "生活のため音楽教室の講師を始める。教え子の発表会で自作曲が演奏され、それを聴いた親たちの口コミで少しずつ広まった。"


@ev("burnout", 2, lambda c: c['style'] != 'ai_pure' and lt(c) >= 3 and c['P']['stab'] <= 0 and 'hiatus' not in tags(c))
def _(c):
    tags(c).add('hiatus'); fx(c, mom=-1.0)
    return "忙しさに追われて心身が限界に。活動休止を発表した。"


@ev("hiatus_comeback", 8, lambda c: 'hiatus' in tags(c))
def _(c):
    tags(c).discard('hiatus'); fx(c, mom=0.9, fans=4)
    return "休止中に昔の曲が見直されており、復帰の発表が想像以上に歓迎された。"


@ev("scandal_post", 2, lambda c: c['st']['fame'] >= 15 and c['era'] >= 3 and lt(c) >= 2 and 'scandal' not in tags(c))
def _(c):
    tags(c).add('scandal'); fx(c, fame=-8, mom=-1.0)
    return "ヒットで注目が集まった結果、数年前のSNS投稿が掘り起こされて炎上。"


@ev("apology_song", 8, lambda c: 'scandal' in tags(c) and 'scandal_resolved' not in tags(c))
def _(c):
    tags(c).add('scandal_resolved')
    if (c['P']['vibe'] >= 1 or c['style'] == 'rap') and c['r'].random() < 0.7:
        fx(c, fame=10, mom=0.8)
        return "炎上を題材にした自虐的な曲を発表。笑いに変える力が評価され、持ち直した。"
    fx(c, fame=-6, fans=-8, mom=-0.5)
    return "謝罪文が火に油を注ぎ、活動を縮小せざるを得なくなった。"


@ev("member_leaves", 3, lambda c: c['style'] in GROUP and 'member_left' not in tags(c) and len(c['hist']) >= 2)
def _(c):
    tags(c).add('member_left'); fx(c, mom=-0.8)
    why = c['r'].choice(["就職して時間が合わなくなった", "結婚を機に地元へ戻ることになった", "音楽性をめぐって方向が合わなくなった", "家業を継ぐことになった", "体調を崩して長期療養が必要になった"])
    return "メンバーが脱退。理由は、%sため。" % why


@ev("replacement_spark", 6, lambda c: 'member_left' in tags(c) and 'replaced' not in tags(c) and 'crisis_done' in tags(c))
def _(c):
    tags(c).add('replaced')
    if c['r'].random() < 0.6:
        fx(c, mom=0.8, fans=3)
        return "新しく入ったメンバーが予想外にハマり、音がむしろ新鮮になった。"
    fx(c, mom=-0.3)
    return "新メンバーとの呼吸がなかなか合わず、ライブの完成度が安定しなかった。"


@ev("vocal_solo", 2, lambda c: c['style'] == 'band' and lt(c) >= 2 and 'solo_friction' not in tags(c))
def _(c):
    tags(c).add('solo_friction'); fx(c, fame=3, mom=-0.4)
    return "ボーカルが個人名義でソロ曲を出すと、そちらが先に伸びた。バンド内に気まずい空気が流れる。"


@ev("breakup", 3, lambda c: c['style'] in GROUP and ('member_left' in tags(c) or 'solo_friction' in tags(c)) and len(c['hist']) >= 4)
def _(c):
    c['st']['stop'] = 'broke_up'
    why = c['r'].choice(["音楽性の違いが埋まらず", "メンバー間の溝が深まり", "ライブの度に消耗し", "それぞれの人生の選択が分かれ"])
    return "%s、解散を発表した。" % why


@ev("diss", 2, lambda c: c['style'] == 'rap' and c['st']['fame'] >= 8 and 'diss' not in tags(c))
def _(c):
    tags(c).add('diss'); fx(c, fame=10, mom=0.4)
    if c['r'].random() < 0.4:
        tags(c).add('scandal')
    return "同業のラッパーとのディス合戦に発展。罵り合いが話題を呼び、双方の再生数が跳ね上がった。"


@ev("feat_hit", 2, lambda c: c['style'] in ("rap", "solo", "beat") and lt(c) >= 1 and 'feat' not in tags(c))
def _(c):
    tags(c).add('feat'); fx(c, fame=10, fans=2)
    return "人気歌手の曲に客演で参加。客演曲の方が本人名義より売れ、本人はやや複雑な気持ちになった。"


@ev("utaite", 2, lambda c: c['style'] == 'beat' and c['era'] >= 3 and lt(c) >= 1 and 'utaite' not in tags(c))
def _(c):
    tags(c).add('utaite'); fx(c, fame=8)
    return "歌い手が曲をカバーすると、カバーの方が大きく伸びた。元の曲の作者としての名前も、そこから知られていく。"


@ev("name_confusion", 4, lambda c: c.get('pun') and lt(c) <= 1 and 'name_conf' not in tags(c))
def _(c):
    tags(c).add('name_conf'); fx(c, mom=-0.4)
    return ("名前が「%s」に似すぎていて、検索すると本家ばかり出てくる。新作の存在がほとんど知られなかった。" if c['era'] >= 3 else "名前が「%s」に似すぎていて、レコード店でも雑誌でも本家と間違えられ、新作の存在がほとんど知られなかった。") % c['pun_src']


@ev("pun_viral", 3, lambda c: c.get('pun') and lt(c) >= 1 and 'pun_viral' not in tags(c))
def _(c):
    tags(c).add('pun_viral'); fx(c, fame=6, fans=4, mom=0.4)
    return "本家「%s」のファンが『名前がそっくりなバンドがいる』と面白がって話題にした。最初は名前だけが話題だったが、曲を聴いた人が残った。" % c['pun_src']


@ev("label_scout", 9, lambda c: c['st']['status'] == "アマチュア" and lt(c) >= 2 and 'first_label_done' not in tags(c))
def _(c):
    tags(c).add('first_label_done'); fx(c, fame=4, mom=0.4, status="インディーズ")
    return "%sの反応を聞きつけたレーベルから声がかかり、インディーズレーベルと契約した。" % T(c)


@ev("major_scout", 9, lambda c: c['st']['status'] == "インディーズ" and lt(c) >= 4 and 'major_debut_done' not in tags(c))
def _(c):
    tags(c).add('major_debut_done'); fx(c, fame=8, mom=0.6, status="メジャー")
    return "%sの大ヒットを受けて、大手レーベルがメジャー契約を持ちかけた。条件を飲み、メジャーへ移籍した。" % T(c)


@ev("remix_hit", 2, lambda c: c['style'] == 'dj' and 'remix' not in tags(c))
def _(c):
    tags(c).add('remix'); fx(c, fame=10)
    return "リミックスを手がけた曲が、原曲よりヒットした。"


@ev("ai_exposed", 5, lambda c: c.get('ai_mode') in ("隠す", "一部だけ隠す") and c['st']['fame'] >= 18 and 'ai_exposed' not in tags(c))
def _(c):
    tags(c).add('ai_exposed'); r = c['r']
    how = r.choice(["声の癖を聴き分けたリスナーが生成音声との類似を指摘し、有志の検証で裏づけられた", "制作に使われたツールのメタデータから、生成AIの痕跡が見つかった", "運営の元関係者の証言が出て、制作の実態が明るみに出た"])
    p = 0.2 + (0.2 if c['era'] == 5 else 0) + c['st']['fans'] * 0.004
    if r.random() < p:
        fx(c, fame=-2, fans=6, mom=0.2); tags(c).add('ai_tolerated')
        return "%s。運営が経緯を正直に説明すると、『曲が良ければAIでもいい』と受け止める声が思いのほか多く、むしろ応援が増えた。" % how
    fx(c, fame=-22, fans=-20, mom=-1.2); tags(c).add('ai_scandal')
    return "%s。『人間が作った曲だと思って聴いていた』という反発が広がり、配信サービスでの扱いも下がった。" % how


@ev("ai_confess", 5, lambda c: c.get('ai_mode') == "途中で告白" and 'ai_confessed' not in tags(c) and lt(c) >= 1 and len(c['hist']) >= 2)
def _(c):
    tags(c).add('ai_confessed'); r = c['r']; c['ai_mode'] = "公表"
    p = 0.4 + (0.2 if c['era'] == 5 else 0) + c['st']['fans'] * 0.003
    if r.random() < p:
        fx(c, fame=6, fans=8, mom=0.6)
        return "運営が自ら『制作の大半は生成AIだった』と告白。最初から嘘をつかなかったわけではないが、自分から明かした姿勢が評価され、話題が広がった。"
    fx(c, fame=-12, fans=-12, mom=-0.8)
    return "運営が自ら『制作の大半は生成AIだった』と告白。『だまされた』と受け取る人が多く、ファンの離脱が続いた。"


@ev("ai_use_exposed", 5, lambda c: c.get('ai_use') == 'secret' and c['st']['fame'] >= 25 and 'ai_exposed' not in tags(c))
def _(c):
    tags(c).add('ai_exposed'); r = c['r']
    if r.random() < 0.25 + (0.15 if c['era'] == 5 else 0):
        fx(c, fame=-3, fans=3, mom=0.0)
        return "共有した制作データから生成AIの痕跡が見つかる。本人が『補助として使っていた』と正直に説明し、使い方の議論に発展したものの、大きな反発にはならなかった。"
    fx(c, fame=-20, fans=-18, mom=-1.0); tags(c).add('ai_scandal')
    return "共有した制作データから生成AIの痕跡が見つかる。『手作りだと思って聴いていた』という声が広がり、信頼を失った。"


@ev("ai_copy_claim", 3, lambda c: isai(c) and lt(c) >= 2 and 'ai_copy' not in tags(c))
def _(c):
    tags(c).add('ai_copy'); fx(c, fame=-6, mom=-0.8)
    return "既存の曲に似たフレーズがあると指摘され、一部の配信が停止。学習元に近い旋律が出ていたことが原因だった。"


@ev("ai_policy", 3, lambda c: isai(c) and c['era'] >= 4 and 'ai_policy' not in tags(c))
def _(c):
    tags(c).add('ai_policy'); fx(c, fame=-3, mom=-0.5)
    return "配信サービスの規約変更で、AI生成曲の収益化が条件付きになった。"


@ev("ai_fan_mv", 3, lambda c: isai(c) and lt(c) >= 1 and 'ai_fanmv' not in tags(c))
def _(c):
    tags(c).add('ai_fanmv'); fx(c, fame=6, fans=8)
    return "ファンが歌詞をもとに作ったMVが、本体より伸びた。"


@ev("human_vs_ai_stage", 4, lambda c: not isai(c) and c['era'] == 5 and lt(c) <= 1 and 'human_stage' not in tags(c))
def _(c):
    tags(c).add('human_stage'); fx(c, fans=8, mom=0.5)
    return "AI楽曲があふれる中、ライブハウスに足を運ぶ人が増え、人間の演奏が見直された。"


@ev("day_job", 2, lambda c: not isai(c) and c['st']['status'] == "アマチュア" and 'daywork' not in tags(c) and len(c['hist']) >= 2)
def _(c):
    tags(c).add('daywork'); fx(c, mom=-0.3)
    return "仕事が忙しくなり、活動の頻度が落ちた。それでも曲は作り続けている。"


@ev("label_collapse", 2, lambda c: c['st']['status'] == "インディーズ")
def _(c):
    fx(c, mom=-0.6, status="自主(再出発)")
    return "所属レーベルの代表が資金繰りに行き詰まり、レーベルが活動を停止。原盤の扱いが宙に浮き、しばらく新作が出せなかった。"


@ev("major_drop", 3, lambda c: c['st']['status'] == "メジャー" and lt(c) <= 1 and len(c['hist']) >= 3)
def _(c):
    fx(c, fame=-5, mom=-0.6, status="自主(再出発)")
    return "売上が契約の想定に届かず、契約が更新されなかった。再びインディーズ(自主)として出発する。"


# ------------------------------------------------------------------ 分かれ道(選択)
DECS = []
BIGW = dict(major_debut=6, go_overseas=5, festival=7, career_turn=1.5, label_conflict=5, tv_appear=3, tieup=3, collab_offer=3, tour=3, voice_license=4, ai_policy_review=5, ai_use=2.5, sell_masters=4, stance=4, face_reveal=3, ai_stage=4, merch=0.4, cover_song=0.4, release_strategy=0.5, sns_policy=0.5, style_change=0.8, member_crisis=4, first_label=3, move_city=2, quit_job=2)


def dec(id, cond, prompt, opts, w=None):
    w = w if w is not None else BIGW.get(id, 1.0)
    DECS.append(dict(id=id, cond=cond, prompt=prompt, opts=opts, w=w))


def O(lab, w, p, win, lose, wf=None, lf=None, wtag=None, ltag=None, stop=None, lstop=None, mode=None, cond=None):
    return dict(lab=lab, w=w, p=p, win=win, lose=lose, wf=wf or {}, lf=lf or {}, wtag=wtag, ltag=ltag, stop=stop, lstop=lstop, mode=mode, cond=cond or (lambda c: True))


def Pw(f):
    return lambda c: f(c['P'])


def Pp(f):
    return lambda c: f(c)


def done(c, id): return (id + '_done') in c['st']['tags']


dec("major_debut", lambda c: c['st']['status'] == "インディーズ" and lt(c) >= 3 and not done(c, "major_debut"),
    "{T}のヒットを受けて、大手レーベルから『メジャーデビューしないか』と声がかかった。",
    [O("メジャーデビューする", Pw(lambda P: 1 + 0.5 * P['amb']), Pp(lambda c: 0.55 - 0.08 * c['P']['perf'] + 0.05 * c['P']['soc']),
       "大きな宣伝費がつき、作風を保ったまま全国に届いた。ヒットが加速した。", "売れ線に寄せる要求が重なり、作風が迷走した。『魂が抜けた』と古参のファンが離れた。",
       dict(fame=12, mom=0.8, status="メジャー"), dict(fame=-4, fans=-12, mom=-0.8, status="メジャー")),
     O("インディーズに残る", Pw(lambda P: 1 + 0.5 * P['perf']), lambda c: 0.7,
       "自由な制作を守り、ファンとの距離が近いまま息長く活動できた。", "宣伝力の差が出て、ヒットの勢いを広げきれなかった。",
       dict(fans=8), dict(mom=-0.4)),
     O("別の独立系レーベルへ移り、条件を交渉する", lambda c: 1.0, lambda c: 0.5,
       "原盤権を自分で持ったまま流通の手厚いレーベルと組め、いいとこ取りができた。", "交渉が長引き、新作の発売が半年以上遅れた。",
       dict(fame=5, fans=4, mom=0.4), dict(mom=-0.6))])

dec("first_label", lambda c: c['st']['status'] == "アマチュア" and lt(c) >= 1 and not done(c, "first_label"),
    "{T}が少しずつ聴かれ、レーベルや事務所から声がかかり始めた。",
    [O("インディーレーベルと契約する", Pw(lambda P: 1 + 0.3 * P['amb']), lambda c: 0.6,
       "流通と宣伝の手伝いが付き、活動の幅が広がった。", "契約内容が不利で、収益がほとんど手元に残らなかった。",
       dict(fame=4, mom=0.4, status="インディーズ"), dict(fame=1, mom=-0.2, status="インディーズ")),
     O("自主制作・自主流通を続ける", Pw(lambda P: 1 + 0.4 * P['perf'] - 0.2 * P['soc']), lambda c: 0.55,
       "自分たちのペースで作れ、手売りのファンが固い基盤になった。", "宣伝まで手が回らず、新作が知られないまま終わった。",
       dict(fans=8), dict(mom=-0.4)),
     O("マネージャーを付けて事務所に所属する", Pw(lambda P: 0.8 + 0.3 * P['amb'] + 0.2 * P['soc']), lambda c: 0.5,
       "仕事の窓口ができ、ライブや取材の依頼が整理された。", "方針をめぐって事務所と衝突し、半年で契約を解除した。",
       dict(fame=5, mom=0.5, status="インディーズ"), dict(fame=-1, fans=-3))])

dec("go_overseas", lambda c: lt(c) >= 2 and not done(c, "go_overseas"),
    "{T}が海外のリスナーにも届き、現地のプロモーターやレーベルから招待が来た。",
    [O("拠点を海外に移して本格的に挑戦する", Pw(lambda P: 0.5 + 0.5 * P['amb']), Pp(lambda c: 0.35 + 0.05 * (c['era'] >= 3) + 0.04 * c['P']['soc']),
       "現地のライブを重ねるうち、言葉の壁を越えて音が評価された。", "言葉と文化の壁に阻まれ、貯金が尽きて帰国した。",
       dict(fame=12, fans=6, mom=0.8), dict(fame=-10, fans=-6, mom=-1.0), wtag='abroad_ok', ltag='abroad_fail', cond=lambda c: c['style'] != 'ai_pure'),
     O("海外ツアーだけ行って、拠点は国内に残す", lambda c: 1.0, lambda c: 0.6,
       "短期のツアーで現地に熱心なファンができ、国内の評価も上がった。", "赤字のツアーになり、スタッフとの関係が悪くなった。",
       dict(fame=6, fans=6, mom=0.4), dict(fame=-2, mom=-0.5), cond=lambda c: c['style'] != 'ai_pure'),
     O("国内に集中して断る", Pw(lambda P: 0.9 + 0.3 * P['perf'] - 0.2 * P['amb']), lambda c: 0.7,
       "国内の活動に集中でき、じわじわと基盤が固まった。", "あとで『あの時行っておけば』と悔やむ流れになった。",
       dict(fans=5, mom=0.2), dict(mom=-0.2)),
     O("配信とSNSで海外に届け続ける(移動しない)", lambda c: 1.0, lambda c: 0.5,
       "移動せず、現地語の字幕とコメント返しで根強いファンを作れた。", "反応は薄く、言語の壁が最後まで残った。",
       dict(fame=5, fans=6, mom=0.4), dict(mom=-0.2), cond=lambda c: c['era'] >= 3)])

dec("move_city", lambda c: c['style'] != 'ai_pure' and c['st']['status'] in ("アマチュア", "インディーズ") and lt(c) >= 1 and not done(c, "move_city") and 'local_hero' not in tags(c),
    "{T}をきっかけに、都会のライブハウスから『こっちで演らないか』と誘われた。",
    [O("上京する", Pw(lambda P: 0.8 + 0.4 * P['amb']), lambda c: 0.5,
       "人とライブが増え、あっという間に交友が広がった。", "家賃と生活費に追われ、曲を作る時間を失った。",
       dict(fame=6, fans=4, mom=0.5), dict(fame=-3, mom=-0.6)),
     O("地元に残り、通いで活動する", Pw(lambda P: 0.9 + 0.2 * P['stab']), lambda c: 0.6,
       "地元の応援を受けながら無理なく続けられ、固定ファンが増えた。", "移動で体力を使い、活動の頻度が落ちた。",
       dict(fans=8, mom=0.2), dict(mom=-0.4)),
     O("オンラインで活動して地元から出ない", lambda c: 1.0, lambda c: 0.5,
       "距離に関係なくファンが集まり、地元を拠点にしたまま活動が広がった。", "ライブの機会が少なく、熱量が伝わりきらなかった。",
       dict(fame=3, fans=6, mom=0.3), dict(mom=-0.3), cond=lambda c: c['era'] >= 3)])

dec("quit_job", lambda c: c['style'] != 'ai_pure' and c['st']['status'] in ("アマチュア", "インディーズ") and len(c['hist']) >= 3 and lt(c) >= 1 and not done(c, "quit_job"),
    "活動が忙しくなり、仕事との両立が限界に近づいてきた。",
    [O("仕事を辞めて音楽に専念する", Pw(lambda P: 0.5 + 0.5 * P['amb'] - 0.2 * P['stab']), lambda c: 0.45,
       "時間を全部曲に注ぎ、作品の質も量も一気に上がった。", "収入が途絶え、焦りから納得のいかない曲を出してしまった。",
       dict(fame=5, mom=0.6), dict(fame=-2, mom=-0.8)),
     O("兼業で続ける", Pw(lambda P: 1 + 0.3 * P['stab'] - 0.3 * P['amb']), lambda c: 0.65,
       "生活が安定し、無理のない活動で長く続けられた。", "疲れが溜まって制作ペースが落ちた。",
       dict(fans=5, mom=0.2), dict(mom=-0.4), wtag='daywork', ltag='daywork'),
     O("活動を縮小して仕事を優先する", Pw(lambda P: 0.5 - 0.3 * P['amb']), lambda c: 0.8,
       "趣味に戻したことで、逆に曲が自由になった。", "新作のペースが落ち、ファンが少しずつ離れていった。",
       dict(fans=2), dict(fans=-6, mom=-0.5), wtag='daywork', ltag='daywork')])


def _style_prompt(c):
    if lt(c) >= 3:
        return "ヒットの後、『次も同じ路線で』と求められているが、自分は少し飽きている。"
    return "反応が伸び悩み、このまま{genre}の路線を続けるか迷っている。"


dec("style_change", lambda c: len(c['hist']) >= 3 and not done(c, "style_change"), _style_prompt,
    [O("売れ線に寄せて路線を調整する", Pw(lambda P: 0.8 + 0.3 * P['amb'] - 0.3 * P['perf']), lambda c: 0.5,
       "聴きやすさが増し、新しい層に届いた。", "芯がぼやけ、どちらの層にも刺さらなかった。",
       dict(fame=8, mom=0.7), dict(fame=-3, fans=-8, mom=-0.7)),
     O("今の路線を貫く", Pw(lambda P: 0.8 + 0.4 * P['perf']), lambda c: 0.5,
       "ぶれない姿勢が評価され、熱心なファンが増えた。", "時代の聴かれ方とずれて、伸び悩みが続いた。",
       dict(fans=8, mom=0.3), dict(mom=-0.4)),
     O("まったく違う系統に挑戦する", Pw(lambda P: 0.5 - 0.2 * P['stab'] + 0.2 * P['amb']), lambda c: 0.4,
       "意外な組み合わせが新鮮に受け止められた。", "『これじゃない』という声が多かった。",
       dict(fame=8, fans=2, mom=0.8), dict(fame=-4, fans=-6, mom=-0.8), mode='genre_change')])

dec("tv_appear", lambda c: lt(c) >= 2 and c['style'] != 'ai_pure' and not done(c, "tv_appear"),
    "{T}の反応を受けて、{tv}への出演依頼が来た。",
    [O("出演する", Pw(lambda P: 1 + 0.3 * P['soc']), Pp(lambda c: 0.55 + 0.05 * c['P']['soc']),
       "短い出番でも一気に名前が知られた。", "緊張で空回りし、編集された姿が不本意に切り取られて広まった。",
       dict(fame=10, mom=0.6, boost=0.6), dict(fame=2, fans=-4, mom=-0.5)),
     O("『ライブで見てほしい』と断る", Pw(lambda P: 0.5 + 0.5 * P['perf']), lambda c: 0.6,
       "出し惜しみが神秘性になり、ライブの動員が伸びた。", "断ったことが話題にならず、機会だけ失った。",
       dict(fans=8, mom=0.2), dict(mom=-0.4)),
     O("密着ドキュメントを受ける", lambda c: 0.7, lambda c: 0.5,
       "苦労の裏側が共感を呼び、曲まで届いた。", "素の姿が不器用に映り、イメージが固定された。",
       dict(fame=8, fans=4, mom=0.5), dict(fame=1, fans=-2))])

dec("tieup", lambda c: lt(c) >= 2 and not done(c, "tieup") and 'tieup' not in tags(c),
    "大手企業から、新商品のCMに{T}を使いたいという話が来た。ただし歌詞の一部を指定される。",
    [O("条件を飲んで受ける", Pw(lambda P: 0.6 + 0.4 * P['amb']), lambda c: 0.55,
       "お茶の間で流れ続け、曲の名前が一気に浸透した。", "指定された歌詞に違和感が出て、ファンから『売った』と言われた。",
       dict(fame=12, mom=0.7, boost=0.5), dict(fame=4, fans=-10, mom=-0.4)),
     O("断る", Pw(lambda P: 0.6 + 0.5 * P['perf']), lambda c: 0.65,
       "断ったという話が逆に信頼を生んだ。", "代わりに他の曲が起用され、自分は機会を逃した。",
       dict(fans=6), dict(mom=-0.5)),
     O("歌詞を自分で書き直す条件で交渉する", lambda c: 0.7, lambda c: 0.45,
       "交渉が通り、自分の言葉のままCMに流れた。", "交渉が決裂して話が流れ、気まずさだけ残った。",
       dict(fame=10, fans=3, mom=0.7, boost=0.4), dict(mom=-0.3))])

dec("collab_offer", lambda c: lt(c) >= 2 and not done(c, "collab_offer"),
    "人気アーティストから、共作曲のオファーが来た。",
    [O("受ける", Pw(lambda P: 0.7 + 0.3 * P['soc']), lambda c: 0.55,
       "相手のファンが流れ込み、一気に知名度が上がった。", "相手の色に飲まれ、自分の個性が薄まったと言われた。",
       dict(fame=10, fans=3, mom=0.6), dict(fame=2, fans=-6, mom=-0.3)),
     O("対等な共作に持ち込む", Pw(lambda P: 0.4 + 0.5 * P['amb'] + 0.3 * P['perf']), lambda c: 0.4,
       "互いの色が混ざり合い、どちらの名義でも新しい代表曲になった。", "意見が割れて、曲は未完成のまま公開されなかった。",
       dict(fame=12, fans=6, mom=0.9), dict(mom=-0.5)),
     O("断って自分の作品に集中する", Pw(lambda P: 0.6 + 0.4 * P['perf']), lambda c: 0.7,
       "自分の作品に集中でき、アルバムの完成度が上がった。", "あとで相手が大ヒットし、断った話が語り草になった。",
       dict(fans=5, mom=0.2), dict(mom=-0.4))])

dec("sell_masters", lambda c: c['era'] >= 4 and c['st']['fame'] >= 35 and not done(c, "sell_masters"),
    "投資会社から、これまでの楽曲の原盤権を高額で買い取りたいという打診があった。",
    [O("売却して資金を得る", Pw(lambda P: 0.6 + 0.3 * P['amb']), lambda c: 0.6,
       "まとまった資金で自分のスタジオを作り、制作に専念できた。", "のちに自分の曲が広告に使い回され、複雑な気持ちになった。",
       dict(fame=2, mom=0.3), dict(fans=-5)),
     O("持ち続ける", Pw(lambda P: 0.7 + 0.3 * P['perf']), lambda c: 0.65,
       "毎年の使用料が安定した収入になった。", "収入が不安定で、苦しい時期が続いた。",
       dict(fans=3), dict(mom=-0.4)),
     O("一部だけ売る", lambda c: 0.7, lambda c: 0.6,
       "資金と権利の両方を確保でき、バランスの良い判断だったと評された。", "どの曲を売るかで揉め、後味が悪かった。",
       dict(fame=1, fans=2, mom=0.2), dict(mom=-0.3))])

dec("crowdfund", lambda c: c['era'] >= 3 and c['st']['status'] in ("アマチュア", "インディーズ") and lt(c) >= 1 and not done(c, "crowdfund"),
    "次のアルバムを作る資金が足りない。",
    [O("クラウドファンディングを始める", Pw(lambda P: 0.8 + 0.3 * P['soc']), Pp(lambda c: 0.5 + 0.004 * c['st']['fans']),
       "目標額の数倍が集まり、ファンとの絆が固まった。", "目標に届かず、返金対応に追われた。",
       dict(fame=4, fans=10, mom=0.5), dict(fans=-4, mom=-0.6)),
     O("自己資金と借金で作る", Pw(lambda P: 0.6 + 0.3 * P['perf']), lambda c: 0.45,
       "納得のいくまで作り込んだ作品が評価された。", "借金が残り、次の制作に響いた。",
       dict(fame=4, mom=0.5), dict(mom=-0.8)),
     O("規模を縮めて宅録で作る", lambda c: 0.7, lambda c: 0.6,
       "荒削りな音が逆に生々しいと評判になった。", "音質の弱さが目立ち、聴き流された。",
       dict(fans=4, mom=0.3), dict(mom=-0.3))])

dec("release_strategy", lambda c: c['era'] >= 2 and lt(c) <= 1 and not done(c, "release_strategy"),
    "新作が思うように聴かれていない。届け方を変えたい。",
    [O("無料でばらまく", lambda c: 0.8, lambda c: 0.5,
       "口コミが広がって、ライブの動員が増えた。", "無料のイメージが付き、収益が伸びなくなった。",
       dict(fame=5, fans=6, mom=0.5), dict(fans=2, mom=-0.4)),
     O("配信は有料のままライブで勝負する", Pw(lambda P: 0.7 + 0.3 * P['perf']), lambda c: 0.5,
       "ライブで聴いた人が音源を買う流れができた。", "音源が届かず、ライブも埋まらなかった。",
       dict(fans=8, mom=0.3), dict(mom=-0.4)),
     O("USBやカセットなど特別な形の限定盤を作る", lambda c: 0.7, lambda c: 0.45,
       "手に取れる形が収集欲を刺激し、限定盤が完売した。", "在庫を抱えて赤字になった。",
       dict(fame=2, fans=8, mom=0.4), dict(mom=-0.5))])

dec("tour", lambda c: live(c) and lt(c) >= 2 and not done(c, "tour"),
    "ヒットを受けて、全国ツアーをやらないかという話が出た。",
    [O("全国ツアーに出る(赤字覚悟)", Pw(lambda P: 0.7 + 0.4 * P['amb']), lambda c: 0.5,
       "各地で観客を掴み、ライブの評価が定着した。", "会場が埋まらず赤字が膨らみ、関係が悪化した。",
       dict(fame=8, fans=10, mom=0.7), dict(fame=-2, fans=2, mom=-0.8)),
     O("本数を絞って質を重視する", Pw(lambda P: 0.8 + 0.3 * P['perf']), lambda c: 0.6,
       "濃いライブが評判を呼び、チケットが取れないと噂になった。", "絞りすぎて、勢いに乗れなかった。",
       dict(fame=4, fans=8, mom=0.4), dict(mom=-0.3)),
     O("配信ライブを中心にする", lambda c: 1.0, lambda c: 0.5,
       "全国から視聴者が集まり、移動なしで収益になった。", "画面越しでは熱が伝わらず、反応が薄かった。",
       dict(fame=3, fans=5, mom=0.3), dict(mom=-0.3), cond=lambda c: c['era'] >= 3)])

dec("member_crisis", lambda c: c['style'] in GROUP and 'member_left' in tags(c) and not done(c, "member_crisis"),
    "メンバーの脱退を受けて、これからの形を決める必要がある。",
    [O("新メンバーを探して続ける", lambda c: 1.0, lambda c: 0.5,
       "新しい音が加わり、むしろ音楽性が広がった。", "音が合わず、ライブの完成度が落ちた。",
       dict(mom=0.6, fans=2), dict(fans=-6, mom=-0.6), wtag='replaced'),
     O("少人数で形を変えて続ける", lambda c: 0.8, lambda c: 0.5,
       "削ぎ落とした音が新しい個性になった。", "音の厚みが減り、物足りなさが指摘された。",
       dict(fame=3, fans=3, mom=0.5), dict(mom=-0.5), wtag='replaced'),
     O("活動休止にして様子を見る", lambda c: 0.5, lambda c: 0.5,
       "休止中に昔の曲が見直され、復帰の機運が高まった。", "休止が長引き、そのまま自然消滅になった。",
       dict(fans=4, mom=0.2), dict(fans=-6), wtag='hiatus', lstop='broke_up'),
     O("解散する", Pw(lambda P: 0.4 - 0.2 * P['stab']), None,
       "区切りをつけ、それぞれの道へ進んだ。その潔さがのちに語られることになる。", "",
       dict(fans=2), {}, stop='broke_up')])

dec("label_conflict", lambda c: c['st']['status'] == "メジャー" and len(c['hist']) >= 3 and not done(c, "label_conflict"),
    "レーベルが、次作は売れ線の路線でと要求してきた。自分たちのやりたい音楽とは違う。",
    [O("従う", Pw(lambda P: 0.7 + 0.2 * P['amb'] - 0.3 * P['perf']), lambda c: 0.5,
       "売れ線に寄せた新作がヒットし、結果として方向性が広がった。", "ヒットしたが自分の曲に聞こえず、虚しさが残った。",
       dict(fame=10, mom=0.7), dict(fame=4, fans=-10, mom=-0.3)),
     O("反発して独立する", Pw(lambda P: 0.5 + 0.4 * P['perf']), lambda c: 0.4,
       "独立後の自由な作品が熱狂的に迎えられた。", "宣伝の後ろ盾を失い、一気に露出が減った。",
       dict(fans=12, fame=2, mom=0.5, status="自主(再出発)"), dict(fame=-10, mom=-1.0, status="自主(再出発)")),
     O("契約解除を交渉して円満に移籍する", lambda c: 0.7, lambda c: 0.5,
       "円満に移れ、新しい環境で作風を取り戻せた。", "交渉が長引き、新作が出せない期間が続いた。",
       dict(fame=3, fans=4, mom=0.5, status="インディーズ"), dict(mom=-0.6, status="インディーズ"))])

dec("ai_use", lambda c: not isai(c) and c['era'] >= 4 and not done(c, "ai_use"),
    "制作に生成AIを使えば、作業が大幅に早くなる。ただ、周囲の目も気になる。",
    [O("補助として堂々と使い、使い方を公表する", Pw(lambda P: 0.8 + 0.2 * P['soc']), lambda c: 0.55,
       "使い方を正直に説明したことが評価され、『誠実』と受け止められた。", "『人間の作品じゃない』と一部のファンが離れた。",
       dict(fame=4, mom=0.4), dict(fans=-8), mode='ai_assist'),
     O("全面的に頼って作る(公表はしない)", Pw(lambda P: 0.4 + 0.2 * P['amb'] - 0.3 * P['perf']), lambda c: 0.6,
       "制作速度が上がり、リリースの間隔が短くなって露出が増えた。", "曲の個性が薄まり、どれも似た曲に聞こえると言われた。",
       dict(fame=5, mom=0.6), dict(fans=-4, mom=-0.4), mode='ai_secret'),
     O("使わないと宣言する(人間の手作り)", Pw(lambda P: 0.7 + 0.4 * P['perf']), lambda c: 0.6,
       "『人間の手触り』が価値になり、固定ファンが強く支持した。", "制作が遅れ、勢いを逃した。",
       dict(fans=10, mom=0.3), dict(mom=-0.4), wtag='human_pledge', ltag='human_pledge')])

dec("ai_policy_review", lambda c: isai(c) and c.get('ai_mode') in ("隠す", "一部だけ隠す", "途中で告白") and c['st']['fame'] >= 15 and not done(c, "ai_policy_review"),
    "ファンや記者から『本当に誰が作っているのか』と聞かれ始めた。",
    [O("生成AIで作っていると公表する", lambda c: 0.8 + 0.2 * (c['era'] == 5), Pp(lambda c: 0.5 + 0.1 * (c['era'] == 5)),
       "隠さない姿勢が受け入れられ、AIならではの試みとして注目された。", "『裏切られた』と去るファンが出たが、残った層は固かった。",
       dict(fame=4, fans=4, mom=0.4), dict(fame=-6, fans=-10, mom=-0.5), mode='ai_disclose'),
     O("隠し続ける", lambda c: 0.8, lambda c: 0.6,
       "謎めいた存在として話題を保てた。", "疑惑が深まり、掲示板で検証が始まった。",
       dict(fame=6, mom=0.5), dict(fame=-2, mom=-0.3)),
     O("人間の「顔役」を立てて見せ方を変える", lambda c: 0.7, lambda c: 0.45,
       "顔役の人柄が受け、ライブやインタビューで人気が出た。", "顔役が独自に動き出し、運営と揉めて契約が切れた。",
       dict(fame=8, fans=6, mom=0.7), dict(fame=-8, fans=-6, mom=-0.8))])

dec("voice_license", lambda c: c['era'] == 5 and c['st']['fame'] >= 30 and not isai(c) and not done(c, "voice_license"),
    "企業から、あなたの声をAI音声モデルとして学習・ライセンスさせてほしいという打診が来た。",
    [O("許可して収益を得る", Pw(lambda P: 0.6 + 0.3 * P['amb']), lambda c: 0.55,
       "ライセンス料が安定収入になり、ゲームや広告で声が使われて知名度が広がった。", "自分の声で作られた曲が出回り、『どれが本物か分からない』と混乱が起きた。",
       dict(fame=6, mom=0.4), dict(fame=-4, fans=-8, mom=-0.4)),
     O("拒否する", Pw(lambda P: 0.7 + 0.3 * P['perf']), lambda c: 0.6,
       "『声は自分のもの』という姿勢が支持された。", "似た声のAI楽曲が出回り、止める手段がなかった。",
       dict(fans=8), dict(fame=-2, mom=-0.4)),
     O("条件付きで許可する", lambda c: 0.6, lambda c: 0.5,
       "用途と期間を限った契約が、新しい標準的な形として紹介された。", "契約の抜け穴を突かれ、想定外の使われ方をされた。",
       dict(fame=3, fans=3, mom=0.3), dict(fans=-5, mom=-0.3))])

dec("stance", lambda c: c['last']['theme'] in ("社会への怒り", "時代風刺") and c['st']['fame'] >= 12 and not done(c, "stance"),
    "曲が社会的な論争の的になり、立場を問われ始めた。",
    [O("はっきり立場を表明する", Pw(lambda P: 0.5 + 0.3 * P['perf'] + 0.2 * P['amb']), lambda c: 0.45,
       "賛同する人たちが強く支持し、熱量の高いファンが増えた。", "賛否が割れて炎上し、仕事が減った。",
       dict(fame=6, fans=12, mom=0.5), dict(fame=-8, fans=-8, mom=-0.8), ltag='scandal'),
     O("解釈は聴き手に任せて黙る", Pw(lambda P: 0.7 + 0.2 * P['stab']), lambda c: 0.65,
       "解釈の余地が広がり、幅広い層に聴かれた。", "『逃げた』と批判され、熱が冷めた。",
       dict(fame=4, fans=3, mom=0.3), dict(fans=-4, mom=-0.3))])

dec("face_reveal", lambda c: c['style'] in ("beat", "dj") and c['era'] >= 3 and lt(c) >= 2 and not done(c, "face_reveal"),
    "顔も素性も出さずに活動してきたが、メディアが顔出しを求めている。",
    [O("顔を出す", Pw(lambda P: 0.7 + 0.3 * P['soc']), lambda c: 0.55,
       "素顔の魅力で新しいファンがつき、ライブの動員が伸びた。", "『イメージと違う』と言われ、一部のファンが離れた。",
       dict(fame=8, fans=4, mom=0.6), dict(fame=2, fans=-8, mom=-0.3)),
     O("覆面を続ける", Pw(lambda P: 0.7 - 0.2 * P['soc']), lambda c: 0.6,
       "謎めいたイメージが保たれ、作品だけが話題になった。", "取材や出演を断り続け、露出が伸びなかった。",
       dict(fans=6, mom=0.3), dict(mom=-0.4)),
     O("顔の代わりにアバターを出す", lambda c: 0.5 + 0.5 * (c['era'] >= 4), lambda c: 0.55,
       "アバターが愛され、グッズや配信でも人気が出た。", "アバターの作り込みに時間を取られ、制作が遅れた。",
       dict(fame=6, fans=6, mom=0.5), dict(mom=-0.4))])

dec("sns_policy", lambda c: c['era'] >= 3 and len(c['hist']) >= 2 and lt(c) <= 2 and not done(c, "sns_policy"),
    "SNSの運用方針を決めたい。",
    [O("毎日投稿して近況や制作過程を見せる", Pw(lambda P: 0.6 + 0.4 * P['soc']), Pp(lambda c: 0.55 + 0.04 * c['P']['soc']),
       "制作過程を見せたことでファンが増え、新作の初動が良くなった。", "投稿に追われて制作が止まり、発言が誤解されて炎上した。",
       dict(fame=4, fans=10, mom=0.5), dict(fame=-4, fans=-2, mom=-0.6)),
     O("作品の告知だけにする", Pw(lambda P: 0.7 + 0.2 * P['perf']), lambda c: 0.55,
       "作品が主役になり、静かに信頼されるアカウントになった。", "存在感が薄く、新作が見つけてもらえなかった。",
       dict(fans=5, mom=0.2), dict(mom=-0.4)),
     O("匿名のまま作品だけ出す", Pw(lambda P: 0.5 - 0.3 * P['soc']), lambda c: 0.5,
       "謎の作者として語られ、考察が盛り上がった。", "誰が作っているのか分からず、応援しにくいと言われた。",
       dict(fame=3, fans=5, mom=0.4), dict(mom=-0.4))])

dec("producer_offer", lambda c: lt(c) >= 2 and not done(c, "producer_offer"),
    "有名プロデューサーが『アレンジを手伝いたい』と連絡してきた。",
    [O("任せて新しい音に挑戦する", Pw(lambda P: 0.7 + 0.3 * P['amb'] - 0.2 * P['perf']), lambda c: 0.55,
       "洗練された音になり、これまで届かなかった層に届いた。", "プロデューサーの色が強すぎ、自分の作品に聞こえなかった。",
       dict(fame=10, mom=0.7), dict(fame=2, fans=-8, mom=-0.3)),
     O("自分でセルフプロデュースを貫く", Pw(lambda P: 0.7 + 0.4 * P['perf']), lambda c: 0.55,
       "作品の一貫性が評価され、作家としての評価が固まった。", "音が内向きになりすぎ、新しい聴き手が増えなかった。",
       dict(fans=8, mom=0.3), dict(mom=-0.4)),
     O("部分的に共同作業にする", lambda c: 0.8, lambda c: 0.5,
       "互いの得意分野がうまく混ざり、評判の良い一枚になった。", "役割分担があいまいになり、制作が長引いた。",
       dict(fame=6, fans=4, mom=0.6), dict(mom=-0.5))])

dec("provide_song", lambda c: lt(c) >= 1 and 'songwriter' not in tags(c) and not done(c, "provide_song") and 'provide_done' not in tags(c),
    "他のアーティストから、楽曲提供の依頼が来た。",
    [O("提供に力を入れ、裏方の仕事を増やす", Pw(lambda P: 0.5 + 0.2 * P['stab'] - 0.2 * P['amb']), lambda c: 0.55,
       "提供曲がヒットして安定した収入になった。", "自分の名義の曲が後回しになり、勢いが落ちた。",
       dict(fame=4, mom=0.3), dict(mom=-0.5), wtag='songwriter', ltag='songwriter'),
     O("自分名義の活動を優先して断る", Pw(lambda P: 0.8 + 0.2 * P['perf']), lambda c: 0.6,
       "自分の作品に集中でき、作風が研ぎ澄まされた。", "断った相手が後に大物になり、関係を築き損ねたと言われた。",
       dict(fans=5, mom=0.3), dict(mom=-0.3)),
     O("提供はするが匿名にする", lambda c: 0.5, lambda c: 0.5,
       "曲だけが広まり、あとから『あの曲の作者』として発見された。", "誰にも知られないまま、収入だけが残った。",
       dict(fame=4, fans=3, mom=0.3), dict(mom=-0.1), wtag='songwriter', ltag='songwriter')])

dec("retire", lambda c: c['st']['fame'] < 12 and len(c['hist']) >= 5 and not done(c, "retire"),
    "反応が薄いまま年月が経ち、続ける意味を考え始めた。",
    [O("続ける", Pw(lambda P: 0.9 + 0.2 * P['stab']), lambda c: 0.5,
       "続けたことで、ある日突然、{viral}聴かれ始めた。", "変わらない状況のまま、年だけが過ぎた。",
       dict(fame=8, fans=6, mom=0.6), dict(mom=-0.3)),
     O("音楽教室の講師など、形を変えて関わる", lambda c: 0.8, lambda c: 0.65,
       "生徒や教え子が小さな輪を作り、音楽が生活の一部になった。", "忙しさで自分の曲を作れなくなった。",
       dict(fans=5), dict(mom=-0.5), wtag='daywork', ltag='daywork'),
     O("音楽をやめる", Pw(lambda P: 0.3 - 0.2 * P['amb']), None,
       "区切りをつけて別の仕事に移り、音楽は聴く側に戻った。", "", {}, {}, stop='quit')])

dec("festival_slot", lambda c: c['era'] >= 1 and live(c) and lt(c) >= 1 and c['st']['status'] in ("アマチュア", "インディーズ") and not done(c, "festival_slot"),
    "大きなフェスの小さなステージから出演オファーが来た。持ち時間は短い。",
    [O("出演する", Pw(lambda P: 0.9 + 0.2 * P['amb']), lambda c: 0.5,
       "短い持ち時間でも観客を掴み、名前が知られた。", "音響トラブルで本来の力が出せなかった。",
       dict(fame=8, fans=5, mom=0.6), dict(fame=-1, mom=-0.4)),
     O("自主企画のイベントを打つ", Pw(lambda P: 0.7 + 0.3 * P['soc']), lambda c: 0.5,
       "同じ空気を持った仲間が集まり、自分たちの場所ができた。", "集客が伸びず、会場代が赤字になった。",
       dict(fans=8, mom=0.4), dict(mom=-0.5)),
     O("辞退して制作に集中する", Pw(lambda P: 0.6 + 0.3 * P['perf']), lambda c: 0.6,
       "制作に集中できて、次の作品の完成度が上がった。", "辞退した話が広まり、次の機会が来にくくなった。",
       dict(fans=2, mom=0.3), dict(mom=-0.3))])

dec("cover_song", lambda c: lt(c) <= 2 and not done(c, "cover_song"),
    "有名曲のカバーをやれば注目されるが、自分の曲の印象が薄まる心配もある。",
    [O("カバーを出す", Pw(lambda P: 0.7 + 0.2 * P['soc']), lambda c: 0.55,
       "カバーが入り口になり、原曲を知らない層が自作曲を聴き始めた。", "カバーの方ばかり聴かれ、自作曲が埋もれた。",
       dict(fame=5, fans=4, mom=0.5), dict(fame=1, fans=-2, mom=-0.2)),
     O("オリジナル一本で行く", Pw(lambda P: 0.7 + 0.4 * P['perf']), lambda c: 0.5,
       "自作曲だけで評価を築き、作家としての信頼が固まった。", "入口が少なく、新しい聴き手に届かなかった。",
       dict(fans=6, mom=0.3), dict(mom=-0.4))])

dec("merch", lambda c: len(c['hist']) >= 2 and not done(c, "merch"),
    "物販で収益の柱を作れないかと考えている。",
    [O("グッズを積極的に作る", Pw(lambda P: 0.7 + 0.3 * P['soc']), lambda c: 0.5,
       "ライブ会場でグッズが売れ、活動の資金になった。", "在庫が余り、置き場に困った。",
       dict(fans=5, mom=0.3), dict(mom=-0.4)),
     O("手作りのミニコミ誌を付けた限定セットにする", lambda c: 0.6, lambda c: 0.5,
       "手作り感が受け、限定セットが即完売した。", "作る手間に追われ、制作時間が削られた。",
       dict(fame=2, fans=8, mom=0.4), dict(mom=-0.4), cond=lambda c: c['era'] <= 1),
     O("手描きのZINEを付けた限定セットにする", lambda c: 0.6, lambda c: 0.5,
       "手作り感が受け、限定セットが即完売した。", "作る手間に追われ、制作時間が削られた。",
       dict(fame=2, fans=8, mom=0.4), dict(mom=-0.4), cond=lambda c: c['era'] >= 2),
     O("音源のみで勝負する", Pw(lambda P: 0.6 + 0.3 * P['perf']), lambda c: 0.55,
       "音だけで勝負する姿勢が評価され、作品の質が上がった。", "収益の柱がなく、生活が苦しくなった。",
       dict(fans=3, mom=0.2), dict(mom=-0.4))])

dec("ai_stage", lambda c: c['style'] == 'ai_collab' and c['st']['fame'] >= 10 and not done(c, "ai_stage"),
    "ライブでの表現方法を決める必要がある。",
    [O("人間のボーカルを加えてライブ活動を始める", lambda c: 1.0, lambda c: 0.55,
       "『音だけでなく、人がいる』ことが評価され、動員が伸びた。", "AIの音と人の声がうまく噛み合わず、違和感が残った。",
       dict(fame=6, fans=8, mom=0.6), dict(mom=-0.3)),
     O("AI音声だけで配信ライブを行う", lambda c: 0.8, lambda c: 0.5,
       "完全に作り込まれた世界観が受け、配信の視聴者が増えた。", "生の熱がなく、一度見たら満足されてしまった。",
       dict(fame=5, fans=4, mom=0.4), dict(mom=-0.3)),
     O("ホログラムやアバター演出で見せる", lambda c: 0.7, lambda c: 0.5,
       "視覚演出が話題になり、ライブが新しい体験として語られた。", "演出費が膨らみ、赤字になった。",
       dict(fame=8, fans=6, mom=0.6), dict(fame=-1, mom=-0.5))])


dec("pun_name", lambda c: c.get('pun') and len(c['hist']) >= 2 and not done(c, "pun_name"),
    "名前が知られてきたところで、本家「{pun}」の事務所から『名前が紛らわしい』と連絡が来た。",
    [O("名前を変えて出直す", Pw(lambda P: 0.7 + 0.2 * P['stab']), lambda c: 0.5,
       "改名そのものを話題にした再出発が好評で、むしろ記憶に残った。", "改名で積み上げた知名度が途切れ、ファンが散った。",
       dict(fame=2, fans=2, mom=0.3), dict(fans=-8, mom=-0.6), mode='rename'),
     O("貫いて、弁護士に相談する", Pw(lambda P: 0.5 + 0.4 * P['perf']), lambda c: 0.4,
       "『パロディの範囲』と整理され、そのまま活動できた。名前ごと語り草になった。", "揉めた経緯が嫌われ、流通が一時止まった。",
       dict(fame=4, fans=6, mom=0.4), dict(fame=-6, fans=-6, mom=-0.8)),
     O("本家にあいさつに行き、公認のネタにする", Pw(lambda P: 0.4 + 0.4 * P['soc']), lambda c: 0.35,
       "本家のメンバーが{sns}で触れてくれ、公認のように広まった。", "返事はなく、気まずい空気だけが残った。",
       dict(fame=8, fans=6, mom=0.6), dict(mom=-0.3))])


dec("festival", lambda c: c['style'] != 'ai_pure' and live(c) and c['era'] >= 1 and lt(c) >= 2 and c["st"]["fame"] >= 5 and not done(c, "festival"),
    "{T}の評判を聞いた野外フェスの主催者から、出演のオファーが届いた。",
    [O("昼の小さなステージに出る", Pw(lambda P: 0.9 + 0.3 * P['perf']), lambda c: 0.7,
       "目当てでない客まで足を止め、物販に長い列ができた。翌週から問い合わせが増えた。", "音響トラブルと裏の大物の被りで、客席はまばらだった。それでも一人ずつ手を振ってくれた。",
       dict(fame=6, fans=8, mom=0.5), dict(fans=2, mom=-0.2), wtag='fes_ok'),
     O("メインステージの枠を狙って交渉する", Pw(lambda P: 0.5 + 0.5 * P['amb']), Pp(lambda c: 0.3 + 0.1 * (c['st']['fame'] >= 40) + 0.1 * (lt(c) >= 4)),
       "夕暮れのメインステージに立ち、地平線まで続く客席が合唱になった。映像が何度も拡散された。", "枠は取れず、条件で揉めて出演そのものが流れた。主催者との関係もぎくしゃくした。",
       dict(fame=14, fans=10, mom=1.0), dict(fame=-3, mom=-0.5), wtag='fes_main'),
     O("出演を断り、自分たちの企画イベントを開く", Pw(lambda P: 0.7 + 0.3 * P['stab']), lambda c: 0.55,
       "仲間のバンドを集めた小さな野外イベントが毎年の名物になった。", "集客が読めず赤字。仲間に頭を下げる夏になった。",
       dict(fans=10, mom=0.3), dict(fame=-1, mom=-0.4), wtag='fes_own')])

dec("career_turn", lambda c: c['style'] != 'ai_pure' and len(c['hist']) >= 4 and lt(c) <= 1 and c['st']['fame'] < 35 and not done(c, "career_turn"),
    "新作が続けて伸びず、周りから『そろそろ音楽以外の道も』という話が出てきた。ちょうど、声をかけてくれる人もいる。",
    [O("ライブハウスの店長になる", Pw(lambda P: 0.8 + 0.4 * P['soc'] + 0.2 * P['stab']), lambda c: 0.8,
       "世話になっていた箱から『店長をやらないか』と誘われた。ブッキングを組み、新人バンドの音を毎晩聴く日々が始まった。", "話はあったが、箱が閉まることになり流れた。",
       dict(fans=3), dict(mom=-0.4), stop='venue'),
     O("レコーディングスタジオの裏方に入る", Pw(lambda P: 0.7 + 0.3 * P['perf']), lambda c: 0.75,
       "スタジオに就職し、エンジニア見習いからやり直した。他人の曲の音を整える仕事が、思いのほか性に合った。", "見習いの給料では暮らせず、数か月で辞めた。",
       dict(fans=2), dict(mom=-0.3), stop='studio'),
     O("音楽教室を開く", Pw(lambda P: 0.6 + 0.3 * P['stab'] - 0.2 * P['amb']), lambda c: 0.7,
       "小さな教室に、子どもから年配の生徒まで通い始めた。発表会で生徒が自分の曲を弾いてくれた。", "生徒が集まらず、半年で教室を畳んだ。",
       dict(fans=3), dict(mom=-0.3), stop='teacher'),
     O("それでも音楽を続ける", Pw(lambda P: 0.9 + 0.5 * P['amb']), lambda c: 0.6,
       "迷いを曲にしたら、これまでになく率直な一曲になった。", "迷いが抜けず、しばらく筆が止まった。",
       dict(fans=2, mom=0.3), dict(mom=-0.4))])


class NeedChoice(Exception):
    pass


def resolve(c, d):
    r = c['r']; st = c['st']
    opts = [o for o in d['opts'] if o['cond'](c)]
    ws = [max(0.05, o['w'](c)) for o in opts]
    idx = r.choices(range(len(opts)), ws)[0]
    sc = c.get('script')
    if sc is not None:
        if c['spos'] < len(sc):
            idx = sc[c['spos']]
            c['spos'] += 1
        else:
            p0 = d['prompt'](c) if callable(d['prompt']) else d['prompt']
            raise NeedChoice(p0.format(**fm(c)), [x['lab'] for x in opts])
    o = opts[idx]
    ok = True if o['p'] is None else (r.random() < clamp(o['p'](c), 0.05, 0.95))
    prompt = d['prompt'](c) if callable(d['prompt']) else d['prompt']
    F = fm(c)
    extra = ""
    if ok:
        text = o['win'].format(**F); fxv = o['wf']; tg = o['wtag']; stp = o['stop']
    else:
        text = o['lose'].format(**F); fxv = o['lf']; tg = o['ltag']; stp = o['lstop']
    if fxv:
        fx(c, **fxv)
    if tg:
        st['tags'].add(tg)
    if stp:
        st['stop'] = stp
    if o['stop'] and ok:
        st['stop'] = o['stop']
    st['tags'].add(d['id'] + '_done')
    m = o['mode']
    if m == 'genre_change':
        others = [g for g in STYLES[c['style']]['genres'] if g != c['genre']]
        if others and ok:
            c['genre'] = r.choice(others)
            extra = "以後の系統は%sに。" % c['genre']
    elif m == 'rename':
        c['artist'] = mk_artist(r, c['style'], None); c['pun'] = None; c['renamed'] = True
        extra = "新しい名前は「%s」。" % c['artist']
    elif m == 'ai_assist':
        c['ai_use'] = 'assist'
    elif m == 'ai_secret':
        c['ai_use'] = 'secret'
    elif m == 'ai_disclose':
        c['ai_mode'] = "公表"
    return dict(id=d['id'], prompt=prompt.format(**F), labels=[x['lab'] for x in opts], chosen=idx, ok=ok, text=text + extra)


# ------------------------------------------------------------------ 結末
def ending(c):
    st = c['st']; t = st['tags']; fame = st['fame']; peak = st['peak']; fans = st['fans']
    stop = st.get('stop'); era = c['era']
    if stop == 'venue':
        return c['r'].choice(["ライブハウスの店長として夜な夜な出演者を迎える。ごくたまに、昔の対バン相手が客として来て、カウンターで笑い合う",
                              "ライブハウスの店長になった。自分のステージには立たないが、ここから出ていくバンドの背中を、毎晩袖から見ている",
                              "小さな箱の店長として、地元の音楽を支える。フロアの隅にはときどき、昔の自分のバンドのステッカーが貼ってある"])
    if stop == 'studio':
        return "スタジオのエンジニアとして、数えきれない曲の音を整えた。クレジットの端に小さく名前がある。それが一番の誇りになった"
    if stop == 'teacher':
        return "音楽教室の先生になった。生徒の発表会で、自作曲をそっと弾いてみせる日がある"
    if stop == 'producer':
        return "裏方に回り、作曲家・プロデューサーとして成功した。自分の名前より、書いた曲の方が知られている"
    if stop == 'illustrator':
        return "音楽は趣味に戻り、イラストレーター・漫画家として活躍した"
    if stop == 'politician':
        return "市議会議員として地元に尽くす。選挙のたびに、自作曲が街宣車から流れる"
    if stop == 'quit':
        return "区切りをつけて音楽をやめ、別の仕事で暮らす。曲は今も一部の人の再生リストに残っている"
    if stop == 'broke_up':
        if fans >= 25 or peak >= 40:
            return "解散後に再評価され、伝説のバンドとして語り継がれる"
        return "解散後はそれぞれの道へ。音源は一部の人の間で語られるのみ"
    if 'fes_main' in t and fame >= 40:
        return "フェスのメインステージに毎年のように呼ばれる存在になった。夏の夕暮れの合唱は、毎年少しずつ大きくなる"
    if 'fes_own' in t and fame < 40:
        return "毎年夏に自分たちの野外イベントを開く。出演者も客も、年々顔ぶれが増えていく"
    if 'fes_ok' in t and fame < 30 and fans >= 20:
        return "フェスの昼の小ステージの常連になった。『あの時間に出ている人』として、毎年足を止める客がいる"
    if 'ai_scandal' in t:
        return "AIであることを隠していた件が悪名として語られ、曲より経緯の方が有名になった"
    if isai(c):
        if c.get('ai_mode') in ("隠す", "一部だけ隠す") and fame >= 40:
            return "最後まで正体を隠し通した。ただし、いつ暴かれるかは誰にも分からない"
        if 'ai_tolerated' in t and fame >= 20:
            return "正体が明かされた後も支持を保ち、AIミュージシャンの一例として語られる"
        if fame >= 50:
            return "AIミュージシャンとして定着。ライブ配信とグッズが定番の収益源になった"
        if fame >= 20:
            return "AIブームの一角として一定の支持を保つ"
        return "AIブームの一過性の存在として、静かに更新が止まった"
    if peak >= 90 and any(h['tier'] == 5 for h in c['hist']):
        return "社会現象となり、時代を代表する曲として残った"
    if 'abroad_ok' in t and fame >= 45:
        return "海外を拠点に活動する日本人として知られ、日本では逆輸入的に評価される"
    if fame >= 60:
        return "国民的ミュージシャンとして長く愛される"
    if 'radio' in t and fame >= 35:
        return "ラジオパーソナリティとしての方が有名になった。曲は『ラジオの人の曲』として愛されている"
    if 'actor' in t and fame >= 40:
        return "俳優としても知られる存在になった。音楽は変わらず続けている"
    if fame >= 40:
        return "息の長いベテランになった。新作を出すたびに、一定の人が待っている"
    if 'local_hero' in t:
        return "地元の名物ミュージシャンとして愛される"
    if 'abroad_fail' in t and fame < 25:
        return "海外挑戦に敗れて帰国。それでも、その経験を曲にして地道に続けている"
    if fans >= 55:
        return "カルト的人気で、小さな箱を満員にし続ける"
    if era == 5 and fans >= 30:
        return "AI楽曲があふれる時代に『人間の音』として再発見された"
    if 'songwriter' in t:
        return "提供曲が売れ続け、名前を知らない人が曲だけ知っている"
    if 'daywork' in t and fame < 25:
        return "仕事の合間に曲を作る。音楽は趣味に戻したが、辞めはしなかった"
    if fame < 8:
        return "誰にも知られないまま、それでも曲を作り続けている"
    return "少数の熱心なファンに支えられて続けている"


# ------------------------------------------------------------------ 生成
START = {
    ("アマチュア", -1): "ライブ喫茶や学園祭で演奏しながら活動を始めた",
    ("アマチュア", 0): "ライブハウスの対バンに出ながら、カセットのデモを手売りして活動を始めた",
    ("インディーズ", -1): "小さな自主制作盤を出して活動を始めた",
    ("インディーズ", 0): "自主レーベルから自主制作盤を出して活動を始めた",
    ("アマチュア", 1): "ライブハウスでデモテープを手売りしながら活動を始めた",
    ("アマチュア", 2): "自作のホームページで音源を公開しながら活動を始めた",
    ("アマチュア", 3): "動画サイトに曲を投稿しながら活動を始めた",
    ("アマチュア", 4): "ショート動画と配信アプリを中心に活動を始めた",
    ("アマチュア", 5): "SNSに自作曲を投稿しながら活動を始めた",
    ("インディーズ", 1): "インディーズレーベルから少部数のCDを出して活動を始めた",
    ("インディーズ", 2): "インディーズレーベルと契約して活動を始めた",
    ("インディーズ", 3): "小さなインディーレーベルと契約し、配信と流通盤で活動を始めた",
    ("インディーズ", 4): "自主レーベルを立ち上げ、配信中心で活動を始めた",
    ("インディーズ", 5): "小規模レーベルから配信で活動を始めた",
}
AI_START = {
    "公表": "運営が生成AIで曲を作り、『AIのアーティスト』と最初から明かして活動を始めた",
    "隠す": "運営が生成AIで曲を作ったが、AIとは明かさず人間のアーティストとして売り出した",
    "途中で告白": "運営が生成AIで曲を作り、最初は伏せつつ、機を見て明かす予定で活動を始めた",
    "一部だけ隠す": "人間が詞とメロディの一部を作り、残りを生成AIで補う。AIの関与は一部だけ明かして活動を始めた",
}


def generate(seed, script=None, maxdec=None):
    r = random.Random(seed)
    era = r.choices(list(ERAS), [ERA_W[e] for e in ERAS])[0]
    P = r.choice(PERS)
    keys = [k for k, s in STYLES.items() if era in s['eras']]
    # 最初の選択: グループか、ソロか → そのあと形態を選ぶ
    tops = {"グループ": [k for k in keys if k in GROUP], "ソロ": [k for k in keys if k not in GROUP]}
    topw = [max(0.2, 0.9 + 0.3 * P['soc']), max(0.2, 1.1 - 0.1 * P['soc'] + 0.1 * P['perf'])]
    top = r.choices(["グループ", "ソロ"], topw)[0]
    subs = tops[top]
    style = r.choices(subs, [STYLES[k]['w'] for k in subs])[0]
    S = STYLES[style]
    start_choice = dict(top=top, other="ソロ" if top == "グループ" else "グループ",
                        subs=[(k, STYLES[k]['name']) for k in subs], chosen=style)
    ai_mode = None
    if S['ai']:
        ai_mode = r.choice(["公表", "公表", "隠す", "隠す", "途中で告白"] if style == "ai_pure" else ["公表", "公表", "一部だけ隠す", "隠す"])
    genre = r.choice([g for g in S['genres'] if GMIN.get(g, -1) <= era])
    start = "アマチュア" if r.random() < 0.6 else "インディーズ"
    c = dict(r=r, seed=seed, era=era, style=style, ai_mode=ai_mode, P=P, genre=genre, start=start, start_choice=start_choice,
             artist=mk_artist(r, style, ai_mode), year=ERAS[era]['year'] + r.randint(0, 2), hist=[], cnt={},
             st=dict(fame=0, fans=5, mom=0.0, boost=0.0, peak=0, status=start, tags=set(), stop=None),
             log=[], decs=[], evs=[], last=None, ai_use=None, pun=None, pun_src=None, renamed=False, script=script, spos=0, pending=None)
    if not S['ai'] and r.random() < 0.4:
        pl = [p for p in (PUN_VARS if r.random() < 0.45 else PUNS) if style in p[2] and p[3] <= era]
        if pl:
            p = r.choice(pl)
            c['artist'] = p[0]; c['pun'] = p[0]; c['pun_src'] = p[1]
    c['artist0'] = c['artist']
    n = r.randint(5, 9)
    for _ in range(n):
        rec = do_release(c)
        c['log'].append(('release', rec))
        st = c['st']
        st['fame'] = max(0, st['fame'] - 2)
        # ヒットしたのに無所属のままは不自然なので、声がかかる
        if st['status'] == "アマチュア" and rec['tier'] >= 3 and 'first_label_done' not in st['tags'] and r.random() < 0.85:
            st['tags'].add('first_label_done'); fx(c, fame=4, mom=0.4, status="インディーズ")
            t0 = "%sの反応を聞きつけたレーベルから声がかかり、インディーズレーベルと契約した。" % T(c)
            c['evs'].append(("label_scout", t0)); c['log'].append(('ev', "label_scout", t0))
        elif st['status'] == "インディーズ" and rec['tier'] >= 4 and 'major_debut_done' not in st['tags'] and r.random() < 0.6:
            st['tags'].add('major_debut_done'); fx(c, fame=8, mom=0.6, status="メジャー")
            t0 = "%sの大ヒットを受けて、大手レーベルがメジャー契約を持ちかけた。条件を飲み、メジャーへ移籍した。" % T(c)
            c['evs'].append(("major_scout", t0)); c['log'].append(('ev', "major_scout", t0))
        # 分かれ道
        elig = [d for d in DECS if d['cond'](c)]
        pd = 0.7 if len(c['decs']) < 2 else 0.4
        if elig and r.random() < pd and (maxdec is None or len(c['decs']) < maxdec):
            d = r.choices(elig, [x['w'] for x in elig])[0]
            try:
                res = resolve(c, d)
            except NeedChoice as e:
                c['pending'] = dict(prompt=e.args[0], labels=e.args[1])
                return c
            c['decs'].append(res); c['log'].append(('dec', res))
            if st.get('stop'):
                break
        # 転機
        eel = [(i, w, fn) for i, w, cond, fn in EVENTS if cond(c)]
        pe = 0.6 if rec['tier'] >= 2 else 0.45
        if eel and r.random() < pe:
            i, w, fn = r.choices(eel, [x[1] for x in eel])[0]
            text = fn(c)
            c['evs'].append((i, text)); c['log'].append(('ev', i, text))
            if st.get('stop'):
                break
    c['ending'] = ending(c)
    return c


def sig(c):
    return (c['style'], c['ai_mode'], c['era'], c['start'], c['P']['n'], c['genre'], c['pun_src'], c['renamed'],
            tuple((h['tier'], h['rkey'], h['theme']) for h in c['hist']),
            tuple((d['id'], d['chosen'], d['ok']) for d in c['decs']),
            tuple(i for i, _ in c['evs']), c['ending'])


def story_text(c):
    S = STYLES[c['style']]
    L = []
    mode = ("(%s)" % c['ai_mode']) if c['ai_mode'] else ""
    nm = c['artist']
    if c['pun_src'] and not c['renamed']:
        nm += "(「%s」のもじり)" % c['pun_src']
    elif c['renamed']:
        nm += "(旧名「%s」=「%s」のもじり)" % (c['artist0'], c['pun_src'])
    L.append("【ID %d】%s / %s%s" % (c['seed'], nm, style_name(c), mode))
    L.append("性格:%s / 系統:%s / 時代:%s / 開始:%s" % (c['P']['n'], c['genre'] if not any(d['id'] == 'style_change' for d in c['decs']) else '(途中で変化あり)', ERAS[c['era']]['name'], c['start']))
    st0 = AI_START[c['ai_mode']] if c['ai_mode'] else START[(c['start'], c['era'])]
    sc = c['start_choice']
    L.append("⚖ 最初の選択: グループで活動するか、ソロで活動するか")
    L.append("   A. グループ%s  B. ソロ%s" % ("  ←選択" if sc['top'] == "グループ" else "", "  ←選択" if sc['top'] == "ソロ" else ""))
    labs = []
    for k, nm in sc['subs']:
        labs.append("%s%s" % (style_name(dict(style=k, era=c['era'])), "  ←選択" if k == sc['chosen'] else ""))
    L.append("   %sなら: %s" % (sc['top'], " / ".join(labs)))
    L.append("出発点: %s。" % st0)
    L.append("")
    for item in c['log']:
        if item[0] == 'release':
            h = item[1]
            L.append("■ %d年 %s%s「%s」(%s)→ %s%s" % (h['year'], h['ord'], h['kind'], h['title'], h['label'], TIERS[h['tier']], "(のちに再評価)" if h.get('revived') else ""))
            L.append("   歌詞: %s(テーマ:%s)" % (h['premise'], h['theme']))
            L.append("   理由: %s。" % h['reason'])
            if h['form']:
                L.append("   ヒットの形: %s。" % h['form'] if h['tier'] >= 1 and h['form'][:3] != '歌詞が' and h['tier'] >= 2 else "   ひとこと: %s。" % h['form'])
        elif item[0] == 'dec':
            d = item[1]
            L.append("⚖ 分かれ道: %s" % d['prompt'])
            for k, lab in enumerate(d['labels']):
                L.append("   %s. %s%s" % ("ABCD"[k], lab, "  ←選択" if k == d['chosen'] else ""))
            L.append("   → %s(%s)" % (d['text'], "うまくいった" if d['ok'] else "裏目に出た"))
        else:
            L.append("◆ 転機: %s" % item[2])
    L.append("")
    L.append("結末: %s。" % c['ending'])
    return "\n".join(L)


def summary_row(c):
    best = max(c['hist'], key=lambda h: h['tier'])
    hits = sum(1 for h in c['hist'] if h['tier'] >= 2)
    decs = "; ".join("%s→%s(%s)" % (d['id'], d['labels'][d['chosen']], "成功" if d['ok'] else "失敗") for d in c['decs'])
    evs = "; ".join(i for i, _ in c['evs'])
    one = "%s(%s・%s)。%s、%s作で最高『%s』(%s)。結末: %s" % (c['artist'], style_name(c), c['P']['n'], ERAS[c['era']]['short'], len(c['hist']), TIERS[best['tier']], best['theme'], c['ending'])
    return [c['seed'], c['artist'], c['pun_src'] or "", c['start_choice']['top'], style_name(c), c['ai_mode'] or "", ERAS[c['era']]['name'], c['start'], c['P']['n'], c['genre'],
            len(c['hist']), hits, TIERS[best['tier']], best['theme'], decs, evs, c['ending'], one]


COLS = ["ID", "アーティスト", "もじり元", "グループ/ソロ", "活動形態", "AI区分", "時代", "開始状態", "性格", "系統", "リリース数", "小ヒット以上の数", "最高評価", "最高作のテーマ", "選択", "転機", "結末", "一行要約"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=0)
    ap.add_argument("--out", default="out")
    ap.add_argument("--show", type=int, default=None)
    a = ap.parse_args()
    if a.show is not None:
        print(story_text(generate(a.show)))
        return
    os.makedirs(a.out, exist_ok=True)
    seen = set(); stories = []
    seed = 0
    while len(seen) < a.count:
        c = generate(seed)
        s = sig(c)
        if s not in seen:
            seen.add(s); stories.append(c)
        seed += 1
    with open(os.path.join(a.out, "storylines_music_summary.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(COLS)
        for c in stories:
            w.writerow(summary_row(c))
    with gzip.open(os.path.join(a.out, "storylines_music_full.jsonl.gz"), "wt", encoding="utf-8") as f:
        for c in stories:
            f.write(json.dumps(dict(id=c['seed'], text=story_text(c)), ensure_ascii=False) + "\n")
    # 統計
    tiers = collections.Counter(); ends = collections.Counter(); sty = collections.Counter(); decs = collections.Counter()
    evs = collections.Counter(); aiera = collections.Counter(); chosen = collections.Counter(); okc = collections.Counter()
    for c in stories:
        sty[(style_name(c), c['ai_mode'])] += 1
        ends[c['ending'].split("。")[0][:18]] += 1
        for h in c['hist']:
            tiers[TIERS[h['tier']]] += 1
        for d in c['decs']:
            decs[d['id']] += 1; chosen[(d['id'], d['labels'][d['chosen']])] += 1; okc[d['ok']] += 1
        for i, _ in c['evs']:
            evs[i] += 1
        if STYLES[c['style']]['ai']:
            aiera[c['era']] += 1
    tot = sum(tiers.values())
    print("stories", len(stories), "last seed", seed)
    print("tier dist", {k: round(v / tot * 100, 1) for k, v in tiers.items()})
    print("styles", dict(sty))
    print("AI eras", dict(aiera))
    print("decisions", len(decs), dict(decs))
    print("dec ok", dict(okc))
    print("events", len(evs), dict(evs))
    print("endings", len(ends))
    for k, v in ends.most_common():
        print("  ", v, k)
    print("avg releases", sum(len(c['hist']) for c in stories) / len(stories))
    print("avg decs", sum(len(c['decs']) for c in stories) / len(stories), "avg evs", sum(len(c['evs']) for c in stories) / len(stories))


if __name__ == "__main__":
    main()
