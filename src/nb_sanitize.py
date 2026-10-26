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
    "KOHM": "KOHHI", "ZEEBLA": "SHIMAUMA", "DJ KRASH": "DJ KUSSHON", "DJ HASEBU": "DJ HASAMI", "Nujabez": "Nujabeans",
    "hid": "hide&seek", "BUCK-TOCK": "BUCK-TACO", "SMAT": "SNAP", "GRAY": "GLAZE", "細野晴巨": "細野晴天",
    "坂本龍二": "坂本竜宮", "崎山蒼紙": "崎山蒼白", "BABYMETAR": "BABYMETRO", "ORIGINAL LAVE": "ORIGINAL LAVA",
    # 読みが同じ・実名をまるごと含む名前(names_x の派生で出たもの)
    "小室哲也": "小室鉄道", "細野春臣": "細野春雨", "高橋幸広": "高橋幸福", "ゆらゆら帝国": "ゆらゆら王国", "中島みゆみ": "中島みそしる",
    "吉井和哉也": "吉井和菓子", "吉田拓朗": "吉田拓本", "安室奈美江": "安室並木", "宮本浩次元": "宮本次元", "山下達朗": "山下達磨",
    "新井由実": "新井油田", "松任屋由実": "松屋の由実", "槇原敬之助": "槇原敬老", "浜田省五": "浜田省エネ", "竹内まりあ": "竹内まりも",
    "the band a part": "the band a party",
}
_PUN_RX = []
for _o, _n in PUN_FIX.items():
    if re.fullmatch(r"[\x20-\x7e]+", _o):
        _PUN_RX.append((re.compile(r"(?<![A-Za-z])" + re.escape(_o) + r"(?![A-Za-z])"), _n))
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
    b['a'] = _walk(b.get('a', {}), pun)
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
    return b


if __name__ == '__main__':
    p = '/home/claude/namebank.json'
    b = json.load(open(p, encoding='utf-8'))
    s0 = json.dumps(b, ensure_ascii=False)
    sanitize(b)
    s1 = json.dumps(b, ensure_ascii=False)
    print('changed' if s0 != s1 else 'no change')
    json.dump(b, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
