# -*- coding: utf-8 -*-
"""namebank.json の後処理(merge_add.py の最後から呼ぶ。単体実行も可)。
1) 実名に近すぎるもじり(ongaku_storyline_gen.PUNS_RAW で差し替えた旧表記)を、生成済みのアーティスト名・出来事文から置き換える
2) 出来事文の先頭に紛れた「a:」などの種別ラベルを外す
3) グループ向け(k='g')の出来事文の「四人で」「残りの三人」などの人数語を、人数によらない言い方にする(デュオ・五人組でも破綻しないように)
"""
import json, re

# 旧もじり -> 新もじり(PUNS_RAW と揃える)
PUN_FIX = {
    "MALICE MIXER": "PALACE MIXER", "yoniger": "yonaki", "OKUMOTO'S": "OKAMOCHI'S", "SILENT HIREN": "SILENT SIRLOIN",
    "UB": "UMA", "MISIO": "MISOA", "the HIATUSU": "the KYUKEI", "ガガガSS": "ガガガSALE", "SoM": "SUMO", "ZORM": "ZORRO",
    "KOHM": "KOOHII", "ZEEBLA": "SHIMAUMA", "DJ KRASH": "DJ KUSSHON", "DJ HASEBU": "DJ HASAMI", "Nujabez": "Nujabeans",
    "hid": "hidari", "BUCK-TOCK": "BUCK-TACO", "SMAT": "SNAP", "GRAY": "GLAZE", "細野晴巨": "細野晴天",
    "坂本龍二": "坂本竜宮", "崎山蒼紙": "崎山蒼白", "BABYMETAR": "BABYMETRO", "ORIGINAL LAVE": "ORIGINAL LAVA",
    # 読みが同じ・実名をまるごと含む名前(names_x の派生で出たもの)
    "小室哲也": "小室鉄道", "細野春臣": "細野春雨", "高橋幸広": "タカハシ幸福", "ゆらゆら帝国": "ゆらゆら王国", "中島みゆみ": "中島みそしる",
    "吉井和哉也": "吉井和菓子", "吉田拓朗": "ヨシダ拓本", "安室奈美江": "安室並木", "宮本浩次元": "宮本次元", "山下達朗": "ヤマシタ達磨",
    "新井由実": "新井油田", "松任屋由実": "松屋の由実", "槇原敬之助": "マキハラ敬老", "浜田省五": "浜田省エネ", "竹内まりあ": "タケウチまりも",
    "the band a part": "the band a parfait", "the band a party": "the band a parfait",
    # 実名をまるごと含む・1字違いのもじり(PUNS_RAW と揃える)
    "Dragon Cash": "Dragoon Cash", "MONGOL900": "MONGOOSE800", "Scha Dara Part": "Scha Dara Pasta",
    "Unlucky Kilimanjaro": "Unlucky Kilimanju", "ONE OK ROCK STEADY": "ONE OK STEADY", "JUMP OF CHICKEN": "JUMP OF CHIKUWA",
    "かぐや姫路": "かぐや彦根", "サディスティック・ミカン・バンド": "サディスティック・ミカン箱", "スチャダラパパ": "スチャダラママ",
    "スピッツァー": "スピリッツァー", "人間座椅子": "人間マッサージ椅子", "四人囃子はやし": "四川囃子はやし", "松任谷由美子": "松任谷由紀子",
    "ザ・スターリング": "ザ・スターアニス", "電気グルーヴィー": "電気グルーミー", "東京事案": "東京自慢", "少女ナイフ": "少女バターナイフ",
    # 2026-11: 元ネタに近すぎる(1字足し・同音・実名をまるごと含む)もじりの見直し(PUNS_RAW と揃える)
    "サザンカオールスターズ": "サザエオールスターズ", "Ms.Children": "Mr.Childish", "スピッツァ": "スプリッツ", "コブクリ": "コンブクロ",
    "ONE OK ROCKET": "ONE NG ROCK", "back numbers": "back lumber", "Mrs. GREEN PINEAPPLE": "Mrs. GREEN PEPPER",
    "サカナアクション": "サカナオークション", "Queen Gnu": "King Gnocchi", "YORUASOBI": "HIRUASOBI", "Official髭女dism": "Official眉毛dism",
    "ASIAN FU-KUNG GENERATION": "ASIAN TAI-CHI GENERATION", "Imperfume": "Parfait", "RADWIMPY": "RADSHRIMPS",
    "ELLEGARDENER": "ELLEGARLIC", "RHYMESTEAR": "RHYMESTEAK", "LUNA SEE": "TUNA SEA", "スキマスイッチョ": "スキマスイーツ",
    "andyamori": "andymochi", "THE ARFEE": "THE ALFALFA", "RIP SLIME": "RIP SLIPPERS", "ORANGE RANGER": "ORANGE RANCH",
    "Aqua Times": "Aqua Tights", "flumpoo": "flumpurin", "[Alexandoros]": "[Alexandria]", "SPYFAIR": "SPICEAIR",
    "WOMAN WITH A MISSION": "MAN WITH A MITTEN", "ゲスの極みおとめ座": "ゲスの極みおじさん", "フジファブリクス": "フジファブリーズ",
    "フジファブリック工場": "フジテキスタイル", "ストレイトナー": "ストロングテナー", "ストレイト・テナー": "ストレイテナガザル", "ストレイテナーズ": "ストレッチテナー",
    "JUDY AND MARRY": "JUDY AND MAYO", "エレファントカシマシマ": "エレファントカシミヤ", "Omoinotaki": "Omoshirotake",
    "Omoinotakeout": "Omoinomatake", "パスピエル": "パスタピエ", "ケツメイジ": "ヘソメイシ", "SHAKKAZOMBIES": "SHAKKAVAMPIRE",
    "BUDDHA BRANDY": "BUDDHA BRUNCH", "Janne Da Ark": "Janne Da Shark", "ゴスペルーズ": "コスプレーズ",
    "MONKEY MAGIC": "MONKEY MAGNET", "amazarashii": "amazakezarashi", "tricote": "tricorn",
    "Every Little Thin": "Every Lettuce Thing", "nano.RIPEN": "nano.RICE", "Suchmoss": "Suchmochi",
    "never young beech": "never young peach", "ずっと真夜中でいいのにね。": "ずっと夜食でいいのに。", "ヨルシカク": "ヨルシャケ",
    "Chilly Beans.": "Chilli Beef.", "Old Age Factory": "Ego Factory", "BANK BAND": "BANK BOND", "あぶらだこ焼き": "あぶらいか焼き",
    "はっぴいえんどう": "はっぴいえんぴつ", "RCサクセスション": "RCサクサクション", "ゴダイコ": "ゴ大根", "悠歌団": "陽歌団", "BOØWAY": "BOØWLING",
    "THE BOOMERANG": "THE BROOM", "有頂天国": "無頂天", "ストリート・スライダー": "ストリート・スライサー", "ヒカシュウ": "ヒヤシチュー", "ボ・ガンボ": "ボ・ガンモ",
    "ジュンスキーウォーカーズ": "ジュンスキーランナーズ", "ASPARAGUSS": "ASPARABACON", "BRADIO": "RADIATOR", "SHISHAMOO": "SHISHAKEBAB",
    "フラワーカンパニーＺ": "フライパンカンパニーズ", "POLYSIXX": "POLYSTICKS", "BEAT CRUSADER": "BEAT CRUSHERS",
    "ザ・ブルーハーツ・ガーデン": "ザ・ブルーベリーハーツ", "BUMP OF CHICKEN NANBAN": "BUMP OF KARAAGE", "ELLE GARDEN": "ELLE GUARDMAN",
    "じゃがたらこ": "じゃがバター", "ラ・ムーン": "ラ・メーン", "ノイバウテン": "ノイバウムクーヘン", "CHANGE and ASKA": "CABBAGE and ASPARA",
    "レミオロメンタイ": "レミオラーメン", "ZIGGY STARDUSTBOX": "ZIGGURAT", "ミツキ屋": "ミツバ屋", "緑黄色社会人": "緑黄色野菜", "星野源泉": "星野温泉",
    "LOVE PSYCHEDELICOLA": "LOVE PSYCHEDELICURRY", "斉藤和義理": "斉藤和牛",
    "ASIAN KUNG-FU DEGENERATION": "ASIAN KUNG-PAO GENERATION", "コブクロス": "コブラクロス", "山下達磨": "ヤマシタ達磨", "竹内まりも": "タケウチまりも",
    "WANIMAL": "WANIKAMA", "the band a part": "the band a parfait", "聖飢魔Ⅲ": "正義魔Ⅲ", "氣志團地": "喜寿團", "ねごとば": "ねぞう",
    "ジャックス・ジャック": "ジャグラーズ", "hide&seek": "hidari", "吉田拓本": "ヨシダ拓本", "大瀧詠二": "オオタキ詠二", "佐野元夏": "サノ元夏", "浜崎あゆむ": "ハマサキあゆむ",
    "槇原敬老": "マキハラ敬老", "高橋幸福": "タカハシ幸福",
}
# 短い・普通の言葉と重なる旧名は、アーティスト名(b['a'])の中で、名前全体(PUN_VARS の前後飾りつき)が一致するときだけ置き換える
PUN_FIX_NAME = {
    "ゆす": "ゆば", "sumiko": "sumire", "capsules": "capsicum", "toes": "toast", "cerori": "cereal", "Templay": "Tempura",
    "アリソ": "アリクイ", "HiGE": "HiZA", "鬚": "髷", "ツイストパン": "ツイスター", "チューリップ畑": "チューリッヒ", "BEGINNER": "BEGONIA",
    "ザ・バースデー": "ザ・アニバーサリー", "ミッシェル": "ミシュラン", "Even": "Ebi", "あいこ": "あいす", "ゆずこしょう": "ゆこう", "ゆずぽん": "ゆめぽん",
    "KOHHI": "KOOHII", "SPEEDY": "SPREAD",
}
_PRE = ["新生", "元祖", "偽", "ミニ", "スーパー", "ゴールデン", "ポケット", "ネオ", "二代目", "夜の", "裏", "全日本"]
_SUF = ["ズ", "の弟", "2号", "・改", "公式", "ガールズ", "feat.豆腐", " II", "(仮)", "ラジオ", "ファクトリー", "クラブ", "の逆襲", "会議", "電気商会", "オールスターズ"]
_NAME_RX = re.compile("^((?:" + "|".join(map(re.escape, _PRE)) + ")?)(" + "|".join(map(re.escape, sorted(PUN_FIX_NAME, key=len, reverse=True))) + ")((?:" + "|".join(map(re.escape, _SUF)) + ")?)$")


def pun_name(s):
    s = pun(s)
    return _NAME_RX.sub(lambda m: m.group(1) + PUN_FIX_NAME[m.group(2)] + m.group(3), s)
_PUN_RX = []
for _o, _n in PUN_FIX.items():
    if re.fullmatch(r"[\x20-\x7e]+", _o):
        _PUN_RX.append((re.compile(r"(?<![A-Za-z])" + re.escape(_o) + r"(?:(?![A-Za-z])|(?=feat\.))"), _n))
    else:
        _PUN_RX.append((re.compile(re.escape(_o)), _n))

_LABEL = re.compile(r"^[a-z]{1,3}:\s*")
_N = "[三四五六3-6３-６]人"
_COUNT = [
    (re.compile(r"(残りの|他の|ほかの)" + _N), r"\1メンバー"),
    (re.compile(_N + "とも"), "全員"),
    (re.compile(_N + "全員"), "全員"),
    (re.compile("[四五六]人分"), "人数分"),
    (re.compile("[四五六]人だけ"), "メンバーだけ"),
    (re.compile(_N + "揃って"), "全員揃って"),
    (re.compile(_N + "で"), "みんなで"),
    (re.compile(_N + "(?=[はがをのにと、])"), "メンバー"),
]


def pun(s):
    for rx, n in _PUN_RX:
        s = rx.sub(n, s)
    return s


def count(s):
    for rx, n in _COUNT:
        s = rx.sub(n, s)
    return s


def _walk(x, f):
    if isinstance(x, str): return f(x)
    if isinstance(x, list): return [_walk(y, f) for y in x]
    if isinstance(x, dict): return {k: _walk(v, f) for k, v in x.items()}
    return x


def sanitize(b):
    b['a'] = _walk(b.get('a', {}), pun_name)
    for e in b.get('ev', []):
        t = _LABEL.sub('', pun(e['t']))
        e['t'] = count(t) if e.get('k') == 'g' else t
    sd = []
    for x in b.get('sd', []):
        x = _walk(x, pun)
        if x.get('k') == 'g':
            x = dict(x, pr=count(x['pr']), o=[{k: (count(v) if isinstance(v, str) else v) for k, v in o.items()} for o in x['o']])
        sd.append(x)
    b['sd'] = sd
    # 4) 実在の有名曲名そのまま(末尾の(…)を外して同じも含む。rosters/realtitles.txt)は、titlefix.json のもじりに差し替え、残りは外す
    try:
        import realtitles as _rt
        b['pt'] = _rt.fix_list(b.get('pt', []), None, 'parody')
        b['t'] = {e: _rt.fix_list(v) for e, v in b.get('t', {}).items()}
        b['tt'] = {th: [[_rt.fix(x[0])] + list(x[1:]) for x in v if not _rt.hit(_rt.fix(x[0]))] for th, v in b.get('tt', {}).items()}
    except Exception as _e:
        print('realtitles skip', _e)
    return b


if __name__ == '__main__':
    p = '/home/claude/namebank.json'
    b = json.load(open(p, encoding='utf-8'))
    s0 = json.dumps(b, ensure_ascii=False)
    sanitize(b)
    s1 = json.dumps(b, ensure_ascii=False)
    print('changed' if s0 != s1 else 'no change')
    json.dump(b, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
