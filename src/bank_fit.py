# -*- coding: utf-8 -*-
"""namebank.json の寄り道(sd)と出来事(ev)に、活動形態に合わないものの印 ns(出さない st のリスト)を付ける。
画面側は (x.ns || []).includes(m.st) なら出さない。merge_add.py の最後でも呼ぶ。
  python3 bank_fit.py   (namebank.json を読み、ns を付け直して保存)"""
import json, re

P = '/home/claude/namebank.json'
LIVE = r"路上|駅前で(歌|弾|演奏)|弾き語り|ライブハウス|対バン|ステージ|ツアー|楽屋|打ち上げ|リハ|客席|ノルマ|物販|ギャラ|マイクスタンド|ゲストで呼ばれ|出番|機材車|遠征"
RULES = {
    "duo": r"バンド(?!名|仲間)|ドラム|ドラマー|ベーシスト|ベースの|三人|四人|五人|リーダーを決め|メンバー全員",
    "beat": LIVE + r"|歌い|歌って|歌う|歌え|合唱|楽器だけ持って",
    "dj": r"弾き語り|路上|駅前で(歌|弾)|歌い|歌って|歌う|合唱|楽器を|バンド",
    "rap": r"弾き語り|楽器を|ピアノ|合唱団",
    "inst": r"歌い|歌って|歌う|歌え|合唱|歌詞",
    "solo": r"バンド(?!名|仲間)|ドラマー|メンバー|三人|四人|五人",
}
RX = {k: re.compile(v) for k, v in RULES.items()}


def tag(b):
    n = 0
    for key, txt in (("sd", lambda x: x["pr"] + " " + " ".join(o.get("l", "") + " " + o.get("ok", "") + " " + o.get("ng", "") for o in x["o"])), ("ev", lambda x: x["t"])):
        for x in b.get(key, []):
            t = txt(x)
            ns = [st for st, rx in RX.items() if rx.search(t) and not (st == "solo" and x.get("k") == "g")]
            if x.get("k") == "s": ns = [s for s in ns if s != "duo"]
            if ns: x["ns"] = ns; n += 1
            else: x.pop("ns", None)
    tempt(b)
    return n


TEMPT = re.compile(r"よからぬ|悪魔がささや|魔が差|出来心|悪い考え|ずるい考え|邪な考え")


def tempt(b):
    """「よからぬ考えが頭をよぎる」などの問い: 危ない選択肢(gs)が必ず出るよう、選択肢を「善良な一つ+危ない一つ」の2つにする
    (画面側は選択肢が3つ以上のとき gs を間引くため)"""
    k = 0
    for x in b.get("sd", []):
        o = x.get("o") or []
        if not TEMPT.search(x.get("pr", "")) or len(o) < 3: continue
        bad = [y for y in o if y.get("gs")]
        if not bad: continue
        good = [y for y in o if not y.get("gs")]
        x["o"] = [good[0], bad[0]] if good else bad[:2]; k += 1
    return k


if __name__ == "__main__":
    b = json.load(open(P, encoding="utf-8"))
    n = tag(b)
    json.dump(b, open(P, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("ns tagged", n)
