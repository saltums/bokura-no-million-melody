# -*- coding: utf-8 -*-
CV = [[0, 1], [2, 2], [3, 3], [3], [2, 3]]
YR = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 18]
LB = ["自主レーベル", "メジャー", "メジャー", "メジャー", "インディーズ"]

def A(k, nm, st, y0, ge, vg, th, sa, tx, roles, tr, ev, ex, d, eh, ea, cp, alt, mem):
    return dict(k=k, nm=nm, st=st, y0=y0, ge=ge, vg=vg, th=th, sa=sa, tx=tx, roles=roles, tr=tr,
                par=k, yr=YR, cv=CV, lb=LB, ev=ev, ex=ex, d=d, eh=eh, ea=ea, cp=cp, eras=[0, 1, 2, 3, 4], alt=alt,
                members=[{"n": n, "r": r, "g": g} for n, r, g in mem])

def D(*rows):
    out = []
    for i, (q, a, b, ra, rb) in enumerate(rows):
        out.append((q, a, b, ra, rb, 3 if i == 1 else 2, 0))
    return out

ARCS = [
 A("c03_drn", "DURAN-DON DURAN-DON", "band", 1978, "ニュー・ロマンティック", "m", ["恋のはじまり", "推しとファンへの手紙", "人工物への違和感", "夏と青春"],
  "中部の大きな街の小さなナイトクラブ", "中部の大きな街のナイトクラブで、鍵盤とベースの少年たちが、きらびやかなダンスの音を作り始めたところから始まった",
  ["Vo", "Key", "Ba", "Gt", "Dr"], ["マイクを握って流し目を送る", "鍵盤の前で髪型を整えてから弾き始める", "ベースを低く構えて涼しい顔で立つ", "ギターを抱えて大きく足を開く", "ドラムの前で静かに息を整える"],
  ["ナイトクラブの片隅で、少年たちは機械の音と派手な服に夢中になっていた。", "歌い手が加わって、五人の顔ぶれがそろった。", "映像の中で遊ぶように見せた曲が、海を越えて少女たちの心をつかんだ。", "世界じゅうの客席が、五人の名前を叫んだ。", "五人が別々の活動に散り、やがて顔ぶれが変わる節目が来た。", "長い年月ののち、元の五人が同じ舞台に戻ってきた。"],
  ["リハで、鍵盤の音色をめぐって三十分も議論した。", "撮影の合間に、衣装の色の相談ばかりしていた。", "打ち上げで、誰の髪型が一番決まっていたかで盛り上がった。", "取材で、同じ名字のメンバーの見分け方を聞かれた。", "ツアー先のホテルで、ファンの出待ちが朝まで続いた。", "新曲の題名が、いつも映画の題名のように聞こえた。"],
  D(("ナイトクラブの店主が言った。『派手な服で出るなら、毎週ここで演らせてやる』。どうする?", "衣装も映像も派手にいく", "音だけで勝負する", "撮った映像の中の五人が、海の向こうで評判になった。", "音は守れたが、客席は静かなまま。華やかな入口は遠かった。"),
    ("レコード会社の人が言った。『もっと機械の音で踊らせろ。ギターは引っ込めろ』。どうする?", "踊れる機械の音に寄せる", "生のバンドの音を貫く", "光る音のダンス曲が、国境を越えて鳴った。", "バンドの音は太くなったが、踊る客席は遠かった。"),
    ("映画の主題歌の話が来た。世界中継の大舞台にも呼ばれている。", "どちらも引き受ける", "断って目の前の客席を守る", "中継で高音が少し揺れたが、それも語り草になった。", "ライブハウスの客とは近くなったが、世界の目には映らなかった。"),
    ("ギターとドラムが言った。『もう抜けたい。休ませてくれ』。どうする?", "残った仲間で看板を守る", "この五人じゃないなら幕を引く", "新しい顔ぶれで続けた。何年もあと、元の五人がまた同じ舞台に立った。", "最後の夜、五人は並んで頭を下げ、幕を引いた。再会の景色は、もう生まれなかった。")),
  "映像で遊ぶように見せ、ダンスの光沢で押し、大舞台に挑み、新しい仲間と看板を守った。",
  ["音だけで勝負したが、華やかな入口を逃した。", "バンドの音を貫き、踊る客席が遠かった。", "幕を引き、再会の景色は生まれなかった。"],
  ["映像の遊び", "ダンスの光沢", "世界中継の舞台", "看板を守る"], ["DURAN-DON DURAN-DON", "DURAN-DON DURAN-DON"],
  [("サイモン・ル・ボトル", "Vo", "m"), ("ニック・ロースハム", "Key", "m"), ("ジョン・テイリー", "Ba", "m"), ("アンディ・テイラン", "Gt", "m"), ("ロジャー・テイロー", "Dr", "m")]),

 A("c03_smi", "THE SUMISOS", "band", 1982, "ギター・ポップ", "m", ["孤独と夜", "自己否定と肯定", "日常のぼやき", "失恋"],
  "北の工業都市の下町の古い家", "北の工業都市の古い家の戸口を、ギターを抱えた青年が突然叩き、言葉を書く青年と話し込んだところから始まった",
  ["Vo", "Gt", "Ba", "Dr"], ["両手をだらりと下げてマイクに近づく", "ギターを抱えて軽やかに弦を転がす", "ベースを抱えて淡々と指を動かす", "ドラムの前で静かに頷いている"],
  ["古い家の戸口で、二人は好きな音楽の話を夜通し続けた。", "ベースとドラムが加わって、四人の形が固まった。", "小さな独立系レーベルから出した曲が、若者たちの部屋で何度も回った。", "ギターが鳴り響く一枚が、後の世代の手本になった。", "ギターの青年が去り、四人の形が崩れる節目が来た。", "解散後も、四人の歌は部屋で静かに聴かれ続けた。"],
  ["リハで、ギターのコード進行をめぐって夜まで試行錯誤した。", "録音の合間に、歌い手が花束を振り回して笑いを取った。", "打ち上げで、好きな本の話ばかりが続いた。", "取材で、暗い歌詞なのになぜ曲が明るいのかを聞かれた。", "ツアー先の町で、ファンが花束を投げ込んできた。", "新曲の題名が、いつも皮肉っぽかった。"],
  D(("知らない青年が家の戸口を叩いた。『一緒に曲を作らないか』。どうする?", "家に上げて話し込む", "戸口を閉じる", "夜通し話し込み、明け方には最初の曲の形ができていた。", "戸口を閉じた。その夜も、一人でレコードを聴いて眠った。"),
    ("大手の担当者が言った。『うちに来れば、すぐ全国で売ってやる』。どうする?", "小さな独立系レーベルに残る", "大手に移る", "手作りの盤が、若者たちの部屋で何度も回った。", "大手の広告で名前は広まったが、手作りの熱は薄れた。"),
    ("ギターが明るいフレーズを弾いた。あなたの詞は暗い。『音も暗くするか?』", "暗い詞を明るいギターに乗せる", "音も沈めて合わせる", "暗い言葉と明るい音の落差が、ほかにない味になった。", "曲の色はそろったが、救いの光が見えにくくなった。"),
    ("ギターが言った。『もう抜ける。このバンドでは息ができない』。どうする?", "引き止めず、それぞれの道に進む", "代わりを入れて四人で作り直す", "解散した。別々の道に進んでも、四人の盤は聴かれ続けた。", "新しいギターを入れて作り直したが、最初の呼吸は戻らなかった。")),
  "戸口で話し込み、独立系レーベルで出し、沈んだ言葉をきらめくギターに乗せ、それぞれの道に進んだ。",
  ["戸口を閉じ、歌が生まれる機会を逃した。", "早めに大手へ移り、手作りの熱が薄れた。", "作り直したが、最初の呼吸は戻らなかった。"],
  ["戸口の夜", "小さなレーベル", "暗い言葉と明るい音", "それぞれの道"], ["THE SUMISOS", "THE SUMISOS"],
  [("モリモリッシュ", "Vo", "m"), ("ジョニー・マル", "Gt", "m"), ("アンディ・ルーフトップ", "Ba", "m"), ("マイク・ジョイズ", "Dr", "m")]),

 A("c03_eur", "EURYTHMIX JUICE", "duo", 1980, "シンセ・ポップ", "f", ["自己否定と肯定", "人工物への違和感", "恋のはじまり", "時代風刺"],
  "小さな録音室", "前のバンドが終わったあと、女性歌手と青年が、二人だけで新しい音を探し始めたところから始まった",
  ["Vo/Key", "Gt/Key"], ["短い髪でまっすぐ前を見て歌う", "機械のつまみを回しながら笑う"],
  ["前のバンドの終わりのあと、二人は小さな録音室で次の音を探していた。", "最初の一枚は思うように売れず、二人は壁に突き当たった。", "機械の音で作った一曲が、世界じゅうの客席に広がった。", "二枚目の大成功のあと、映画の音楽も手がけて幅を広げた。", "歩みが少しずつずれ、二人は静かに距離を置いた。", "長い年月ののち、二人は再び同じ舞台に立った。"],
  ["録音中、機械の調子が悪くなって何度もやり直した。", "打ち上げで、前のバンドの思い出話に花が咲いた。", "取材で、二人だけでやる理由を聞かれた。", "リハで、機械のつまみの位置を巡って意見が割れた。", "ツアー先で、歌い手が衣装を替えて客席を驚かせた。", "新曲の題名が、いつも短い問いかけのように聞こえた。"],
  D(("前のバンドが解散した夜、相方が言った。『二人だけで、もう一度やらないか』。", "二人だけで続ける", "仲間を集めてバンドを組み直す", "小さな録音室で、二人だけの音を探し始めた。", "バンドを組み直して賑やかになったが、二人の濃さは薄れた。"),
    ("最初の一枚は売れず、借金で買った機材だけが部屋に残った。どうする?", "機械の音に賭けて作り直す", "生の音のまま続ける", "機械で作った一曲が、世界じゅうの踊り場で鳴った。", "生の音の味は守れたが、世間の目は向かず、借金も残った。"),
    ("映画監督から電話が来た。『次の映画の音楽を、全部任せたい』。", "映画の音楽を引き受ける", "自分たちの歌に専念する", "映画館で流れた曲が、新しい聴き手を連れてきた。", "歌は磨かれたが、広がりは小さかった。"),
    ("ツアー最終日の楽屋で、相方が言った。『しばらく、別々にやらないか』。", "別々の道を許す", "無理にでも二人で続ける", "何年も別々に歩いたあと、再会の舞台で客席が湧いた。", "無理に続けたが、二人の間の空気は重くなった。")),
  "二人だけで続け、機械の音に切り替え、映画の音楽を引き受け、それぞれの道を許して再会した。",
  ["バンドを組み直したが、二人の濃さが薄れた。", "生の音のまま続け、世間の目は向かなかった。", "無理に続けて、二人の間の空気が重くなった。"],
  ["二人だけの音", "機械への切り替え", "映画の音楽", "再会の舞台"], ["EURYTHMIX JUICE", "EURYTHMIX JUICE"],
  [("アニー・レノクス", "Vo/Key", "f"), ("デイヴ・スチュワード", "Gt/Key", "m")]),

 A("c03_psb", "PET BOTTLE BOYS", "duo", 1981, "シンセ・ポップ", "m", ["日常のぼやき", "時代風刺", "孤独と夜", "自己否定と肯定"],
  "ロンドンの大通り沿いのレコード店", "ロンドンの大通り沿いのレコード店で、シンセサイザーの部品を探していた青年と、居合わせた鍵盤の青年が出会ったところから始まった",
  ["Vo", "Key"], ["顔色を変えずに淡々と歌う", "帽子を深くかぶって鍵盤の前に立つ"],
  ["レコード店での立ち話から、二人はダンスの音楽の話に夢中になった。", "小さな録音室で、二人は曲を書いては試し続けた。", "ニューヨークの制作者と録った曲が、クラブで少しずつ評判になった。", "大手と契約して録り直した曲が、国じゅうで一位になった。", "古い歌を自分たちの色で歌い直し、クリスマスの客席を湧かせた。", "何十年たっても、二人は新しい音を出し続けた。"],
  ["録音中、鍵盤の音色を決めるのに半日かかった。", "取材で、笑わない顔の理由を聞かれて困った。", "打ち上げで、映画や舞台の話ばかりが続いた。", "リハで、衣装の帽子の位置を巡って小さな議論になった。", "ツアー先で、舞台装置の凝り方に驚かれた。", "新曲の題名が、いつも皮肉を含んでいた。"],
  D(("レコード店で、シンセの部品を手にした青年が話しかけてきた。『ダンスの曲、作ってる?』", "話し込んで、一緒に曲を書く", "挨拶だけで別れる", "立ち話が、その日のうちに最初のデモ作りになった。", "挨拶だけで別れた。部品の袋を抱えて、一人で帰った。"),
    ("海の向こうの制作者から手紙が来た。『曲を預けてくれれば、クラブで鳴らしてみせる』。", "曲を預ける", "自分たちだけで録り続ける", "海の向こうのクラブで、二人の曲が少しずつ回り始めた。", "自分たちだけで録音を続けた。形は守れたが、広がりに時間がかかった。"),
    ("大手の担当が言った。『契約するなら、あの曲を一から録り直してもらう』。どうする?", "大手と契約して録り直す", "最初の版のまま小さな会社で出す", "録り直した曲が、国じゅうで一位になった。", "最初の版の味は守れたが、広がりは頭打ちになった。"),
    ("会社の人が言った。『冬に、誰もが知る古い歌を出そう』。どうする?", "古い歌を自分たちの色で歌い直す", "自作の曲だけで通す", "歌い直した曲が、冬の客席を湧かせた。", "自作だけで通した。色は守れたが、記憶に残る一曲を逃した。")),
  "音楽の話に踏み込み、制作者に曲を預け、大手と契約して録り直し、古い歌を自分たちの色で歌い直した。",
  ["挨拶だけで別れ、二人の音は生まれなかった。", "自分たちだけで録音を続け、広がりに時間がかかった。", "自作だけで通し、記憶に残る一曲を逃した。"],
  ["立ち話から", "海の向こうの制作者", "録り直しの一位", "歌い直しの冬"], ["PET BOTTLE BOYS", "PET BOTTLE BOYS"],
  [("ニール・テナンツ", "Vo", "m"), ("クリス・ロウズ", "Key", "m")]),

 A("c03_whm", "WASABAM!", "duo", 1981, "ダンス・ポップ", "m", ["夏と青春", "恋のはじまり", "旅立ちと別れの春", "応援歌"],
  "ロンドン近郊の町の学校の教室", "ロンドン近郊の町の学校で出会った二人の少年が、一緒に音を鳴らし始めたところから始まった",
  ["Vo", "Gt"], ["金髪をかき上げてから高らかに歌う", "ギターを抱えて白い歯を見せて笑う"],
  ["学校の教室で、二人は音楽の話ばかりしていた。", "小さなバンドが終わり、二人だけの新しい形が始まった。", "初めてのシングルは小さな反響だったが、二曲目が大きく跳ねた。", "二枚目の一枚が、国じゅうの一位を飾った。", "遠い国まで渡って、誰も行かなかった客席に立った。", "頂点で、二人は大きな競技場で別れを告げた。"],
  ["リハで、ダンスの足並みが揃わず何度も笑った。", "撮影の合間に、衣装の短パンの丈で盛り上がった。", "打ち上げで、昔の学校の思い出話が続いた。", "取材で、二人の役割分担を聞かれた。", "ツアー先で、空港が少女たちで埋まった。", "新曲の題名が、いつも掛け声のようだった。"],
  D(("父親が言った。『音楽なんかやめて、ちゃんと勉強しろ』。相棒はデモテープを持って待っている。", "相棒と本気で曲を出す", "父の言うとおり、思い出に留める", "二人で作ったデモが、小さな会社の耳に届いた。", "テープは引き出しにしまわれ、世に出る機会を逃した。"),
    ("相棒が言った。『次は、しっとりしたバラードを歌ってみないか』。", "バラードに挑む", "明るい曲だけで通す", "切ない一曲が、二人のもう一つの顔になった。", "明るさは守れたが、大人の客席には届かなかった。"),
    ("事務所の人が言った。『誰も行ったことのない遠い国で、公演の話がある』。", "遠い国に渡る", "慣れた国で稼ぎ続ける", "見慣れない客席が、最後には手拍子で応えた。", "足元は固まったが、歴史に残る話題は生まれなかった。"),
    ("絶頂のさなか、相棒が言った。『おまえは一人でやるべきだ。ここで終わろう』。", "頂点で別れ、競技場で幕を引く", "引き止めて二人で続ける", "満員の競技場で、二人は最後の曲を歌い切った。", "引き止めて続けたが、あの輝きを保てなかった。")),
  "遊びを本気にして出し、バラードにも挑み、遠い国に渡り、頂点で競技場の別れを告げた。",
  ["思い出のまま留め、世に出る機会を逃した。", "明るさだけで通し、大人の客席には届かなかった。", "続けたが、あの輝きを保てなかった。"],
  ["本気の遊び", "もう一つの顔", "遠い国の舞台", "頂点の別れ"], ["WASABAM!", "WASABAM!"],
  [("ジョージ・マイクル", "Vo", "m"), ("アンドリュー・リッジレー", "Gt", "m")]),

 A("c03_run", "UDON-D.M.C.", "rap", 1983, "ヒップホップ", "m", ["地元愛", "時代風刺", "ナンセンスと言葉遊び", "自己否定と肯定"],
  "ニューヨークの住宅街の通り", "ニューヨークの住宅街で育った三人が、マイクとターンテーブルで韻を踏み始めたところから始まった",
  ["MC", "MC", "DJ"], ["帽子を深くかぶって力強くマイクを握る", "眼鏡をかけて低い声でリズムを刻む", "ターンテーブルの前で静かに頷く"],
  ["住宅街の通りで、三人は韻を踏んで遊んでいた。", "兄が運営する形で、小さなレーベルから最初の曲を出した。", "ロックのギターを混ぜた曲が、新しい聴き手を呼び込んだ。", "ロックの大御所と一曲を組み直し、客席の垣根を壊した。", "愛用の靴を歌った曲が、大きな契約を呼び込んだ。", "長い歩みの果てに、三人の音は街の誇りとして語られた。"],
  ["リハで、ターンテーブルの針を何度も落としては笑った。", "撮影の合間に、靴ひもの結び方で盛り上がった。", "打ち上げで、地元の店の話ばかりが続いた。", "取材で、帽子を取らない理由を聞かれた。", "ツアー先で、街の子供たちが真似をして踊っていた。", "新曲の題名が、いつも一行で言い切れた。"],
  D(("兄が言った。『大学なんか休んで、俺のレーベルから曲を出せ』。親は卒業を望んでいる。", "兄のレーベルから曲を出す", "大学を優先し、韻は週末だけにする", "最初の曲が、住宅街のラジカセから流れ始めた。", "卒業は近づいたが、マイクを握るのは週末だけになった。"),
    ("レコード会社の人が言った。『ロックのギターを入れれば、もっと売れる』。地元の仲間は眉をひそめた。", "ロックのギターと混ぜる", "ヒップホップだけの音を守る", "混ざった音が、ロック好きの客席まで開いた。", "地元の仲間は喜んだ。音の純度は守れたが、広がりは小さかった。"),
    ("ロックの大御所から連絡が来た。『あの曲を一緒にやり直さないか』。", "大御所と組んで組み直す", "断って単独で出し続ける", "壁を突き破る映像が、テレビで何度も流れた。", "自分たちの色は守れたが、象徴的な瞬間は逃した。"),
    ("靴の会社の人が楽屋に来た。『あの靴の歌に、大金を出したい』。", "靴の会社と契約を結ぶ", "断って歌だけで通す", "靴の歌が、音楽と商売をつなぐ橋になった。", "断って歌だけで通した。歌の純粋さは守れたが、橋は生まれなかった。")),
  "街の普段着で行き、ロックと混ぜ、大御所と曲を組み直し、靴の会社と契約を結んだ。",
  ["派手な衣装で飾り、街の匂いが薄れた。", "音の純度を守り、広がりは小さかった。", "断って歌だけで通し、橋は生まれなかった。"],
  ["街の普段着", "ロックとの混ざり", "大御所との組み直し", "靴との契約"], ["UDON-D.M.C.", "UDON-D.M.C."],
  [("ジョセフ・ラン・シモンス", "MC", "m"), ("ダリル・マクダニエルス", "MC", "m"), ("ジャム・マスター・ジェムストーン", "DJ", "m")]),

 A("c03_pol", "THE POLYBAGS", "band", 1977, "ニューウェーブ", "m", ["社会への怒り", "孤独と夜", "恋のはじまり", "時代風刺"],
  "ロンドンの小さな練習スタジオ", "ロンドンで、ドラマーとベース兼歌い手が、パンクの熱気の中でバンドを始めたところから始まった",
  ["Vo/Ba", "Gt", "Dr"], ["ベースを抱えて高い声で歌う", "ギターを抱えて静かに音色を探す", "ドラムの前で細かく刻みながら笑う"],
  ["練習スタジオで、ドラムとベースの二人が速い曲を試していた。", "経験豊かなギターが加わって、三人の形が固まった。", "最初のシングルは売れなかったが、再び出した曲が少しずつ届いた。", "レゲエやジャズを混ぜた音が、新しい聴き手を呼んだ。", "頂点のところで、三人は活動を休む決断をした。", "長い年月ののち、三人は世界を回る舞台に戻ってきた。"],
  ["リハで、ドラムの手数が多すぎて歌が聞こえなくなった。", "録音の合間に、誰かが新しいリズムを思いついて夢中になった。", "打ち上げで、旅の話ばかりが続いた。", "取材で、三人の仲の良さを何度も聞かれた。", "ツアー先で、地元の楽器屋を回って買い物を楽しんだ。", "新曲の題名が、いつも短くて覚えやすかった。"],
  D(("腕のいいギタリストがスタジオに来て言った。『俺を入れるなら、今のギターとは組めない』。", "最初のギターを外して三人組にする", "最初の顔ぶれで続ける", "三人で鳴らした最初の音で、隙間の多い響きが見つかった。", "最初の顔ぶれで続けた。親しみは守れたが、音の厚みは物足りなかった。"),
    ("最初のシングルは売れなかった。会社の人が言った。『次で駄目なら契約終了だ』。", "同じ曲をもう一度出す", "諦めて次の新曲に賭ける", "再び出した曲が、じわじわとラジオでかかり始めた。", "諦めて次に進んだ。新曲は出せたが、看板の曲を逃した。"),
    ("ドラムが言った。『パンクの速さだけじゃ、すぐ飽きられる』。どうする?", "レゲエやジャズを混ぜる", "速い音のまま通す", "隙間の多いリズムが、誰にも似ない音になった。", "勢いは守れたが、流行の波に埋もれた。"),
    ("世界ツアーの最終日。楽屋では、もう誰も口をきかなかった。", "頂点で活動を休む", "休まず次の盤を作る", "照明が落ちたあと、三人は別々の車で帰った。", "休まず走り続けたが、疲れが音に出た。")),
  "経験豊かなギタリストを迎え、最初の曲をもう一度出し、レゲエやジャズを混ぜ、頂点で休んで後に再会した。",
  ["最初の顔ぶれで続け、音の厚みが物足りなかった。", "諦めて次に進み、看板の曲を逃した。", "休まず走り、疲れが音に出た。"],
  ["三人の形", "もう一度の曲", "混ざった音", "休んでの再会"], ["THE POLYBAGS", "THE POLYBAGS"],
  [("スタング", "Vo/Ba", "m"), ("アンディ・サンマーズ", "Gt", "m"), ("スチュワート・コープランズ", "Dr", "m")]),

 A("c03_cul", "CULTURE CLUB SANDWICH", "band", 1981, "ブルー・アイド・ソウル", "m", ["自己否定と肯定", "恋のはじまり", "失恋", "時代風刺"],
  "ロンドンの古いクラブの楽屋", "ロンドンのクラブの楽屋で、派手な化粧の歌い手と、ベース、ギター、ドラムの三人が集まったところから始まった",
  ["Vo", "Gt/Key", "Ba", "Dr"], ["派手な帽子をかぶって柔らかく歌う", "ギターを抱えて穏やかに弾く", "ベースを抱えて静かに笑う", "ドラムの前で真面目な顔で刻む"],
  ["楽屋で、四人は前のバンド名の失敗を笑い合った。", "最初に断られた大手とは別の会社が、四人に手を差し伸べた。", "一曲が国じゅうで一位になり、四人の名が一気に広まった。", "世界的な賞に選ばれ、歌い手の姿は憧れの的になった。", "歌い手のひとりの仕事が増え、四人の間の空気が変わった。", "長い年月ののち、四人は再び同じ舞台に立った。"],
  ["リハで、歌い手の帽子が舞台装置に引っかかった。", "撮影の合間に、化粧の色で盛り上がった。", "打ち上げで、昔の音楽の話に花が咲いた。", "取材で、歌い手の発言が毎回見出しになった。", "ツアー先で、ファンが同じ格好で待っていた。", "新曲の題名が、いつも切ない色の名前を含んでいた。"],
  D(("前のバンド名で出たライブは、客が三人だった。仲間が言った。『名前も顔ぶれも変えて、出直そう』。", "新しい名前で出直す", "元の名前で粘る", "新しい名前のポスターを、四人で夜通し貼った。", "元の名前で粘った。慣れてはいたが、新鮮さは生まれなかった。"),
    ("大手の担当が言った。『その音じゃ売れない。うちの言うとおりに直せ』。", "音を変えず、別の会社を探す", "言うとおりに直す", "小さな会社が手を挙げ、四人の音がそのまま世に出た。", "合わせた音は無難だったが、個性が薄れた。"),
    ("テレビ局の人が言った。『その化粧と服、もう少し地味にできない?』", "派手な姿を貫く", "地味に整える", "画面に映った姿が、翌日には街で真似されていた。", "落ち着いた姿になったが、目を引く魅力が薄れた。"),
    ("ツアー先のホテルで、歌い手が言った。『ひとりの作品も作ってみたい』。", "ツアーを止めて、それぞれの道を許す", "四人だけで走り続ける", "ツアーは途中で終わった。長い休みのあと、四人はまた同じ舞台に立った。", "四人だけで走り続けたが、すれ違いが重なって離れた。")),
  "新しい名前で出直し、別の会社に行き、派手な外見を貫き、それぞれの道を経てまた集まった。",
  ["元の名前で粘り、新鮮さが生まれなかった。", "合わせた音で、個性が薄れた。", "四人だけで走り、すれ違って離れた。"],
  ["出直しの名前", "別の会社", "派手な外見", "打ち明けた休み"], ["CULTURE CLUB SANDWICH", "CULTURE CLUB SANDWICH"],
  [("ボーイ・ジョーゼット", "Vo", "m"), ("ロイ・ベイエリア", "Gt/Key", "m"), ("マイキー・グレイグ", "Ba", "m"), ("ジョン・モッス", "Dr", "m")]),
]

PT = {
 "c03_drn": ["Hungry Like the Golf", "Girls on Firm", "Rice-O", "The Reflux", "The Mild Boys", "Save a Player", "Is There Something I Should Snow?", "A View to a Kiln", "Ordinary Word", "Come Undue", "Planet Earl", "Motorious", "Union of the Snack", "New Moon on Money", "Careless Memoirs", "My Own Wax", "Hold Back the Rein", "Skin Grade", "Serious Salad", "Reach Up for The Sunrice", "Night Boot", "Lonely in Your Nightcap", "Last Chance on the Stairwell", "Tiger Tigre", "New Region", "Of Crime and Fashion", "Shadows on Your Slide", "Too Much Inflation", "Skin Drivers", "Sound of Blunder", "Burning the Gravy", "Hold Meat", "The Seventh Stranded", "Meet El Residente", "Tel Avid", "Winter Marshes On", "Pop Crash Movie", "Girl Picnic!", "Paper Cods", "Pleasure Off", "Last Night in the Silly", "All You Need Is Cow", "Breath After Bread", "Electric Barbecue", "White Limes", "Watching the Detergents", "Be My Iron", "Sing of the City", "Valentine Stoves", "Late Bark"],
 "c03_smi": ["This Charming Mat", "How Soon Is Snow?", "There Is a Lime That Never Goes Out", "Bigmouse Strikes Again", "Heaven Knows I'm Miserly Now", "Hand in Grove", "What Difference Does It Bake?", "Panic Pantry", "Asparagus", "The Boy with the Horn in His Side", "Shopfitters of the World Unite", "Sheila Take a Bowl", "Girlfriend in a Comma", "Girl Aphid", "The Headmaster Rival", "Heat Is Murder", "Barbarism Begins at Rome", "Cemetry Dates", "Frankly, Mr. Shanty", "I Know It's Oven", "Never Had No Wine Ever", "Some Gulls Are Bigger Than Others", "Vicar in a Tutor", "Rusholme Ruffles", "The Queen Is Dread", "Reel Around the Mountain", "Pretty Girls Make Gravy", "Still Elk", "These Things Take Lime", "Please, Please, Please, Let Me Eat What I Want", "Stop Me If You Think You've Heard This Tune Before", "Death of a Disco Danger", "I Started Something I Couldn't Furnish", "Is It Really So Strong?", "Sweet and Tender Hooligin", "That Joke Isn't Sunny Anymore", "Well I Wander", "Back to the Old Mouse", "The Hand That Rocks the Candle", "Handsome Duvet", "Ouija Bored, Ouija Bored", "Willie, It Was Really Nothing", "You've Got Everyone Now", "Oscillate Mildly", "Paint a Vulgar Picnic", "Honey Changes Everything", "Half a Persian", "A Rush and a Push and the Band Is Ours", "Nowhere Last", "Rubber Wing", "Shakespeare's Mister", "Work Is a Five Letter Word", "I Keep Mime Hidden", "Miserable Pie", "Golden Nights", "Unhappy Bathday", "Last Night I Dreamt That Somebody Moved Me", "Stretch Out and Wail", "The Draize Brain"],
 "c03_eur": ["Sweet Dreams Are Made of Tea", "Here Comes the Pain Again", "There Must Be an Angle Playing with My Heart", "Would I Fly to You?", "Misters Are Doin' It for Themselves", 'Love Is a Manger', "Who's That Curl?", "Missionary Van", "I Shaved the World Today", "I've Got a Wife", 'Corn in My Soup', "Night by Your Side", "Julienne", "Don't Ask Me Who", "Thorn in My Salad", "Better to Have Lost in Glove Than Never to Have Loved at All", 'When Tomorrow Crumbs', "When the Day Goes Brown", "The Miracle of Dove", "Sexcrime (Nineteen Eighty-Pork)", 'Anglerfish', 'Sausage Roll', "Conditioned Sole", "Leaven", "Beautiful Chilli", "Take Me to Your Hearth", "Put the Lame on Me", "Peace Is Just a Bird", "Power to the Meat", "Beethoven (I Love to Listen to Beans)", "Right by Your Sled", "I Need a Pan", 'I Need Ewe', "Wide Eyed Grill", "Rap It Up", "Brand New Bay", "Never Gonna Fry Again", "You Have Placed a Chip in My Heart", "I Could Give You a Miracle", "Satellite of Lava", 'This City Never Sweeps Up', 'The King and Queen of Arkansas', "Caveman Bed", "Cool Blur", "English Simmer", "I Did It Just the Sane", "Rice Girl", "Cone Together", "Hello I Love Yew"],
 "c03_psb": ["Vest End Girls", "It's a Gin", 'Always on My Mime', "What Have I Done to Reserve This?", "Heat", "Go Wet", "Can You Forgive Him?", "Being Snoring", "Left to My Own Devils", "Domino Prancing", "So Lard", "Opportunities Let's Make Lots of Honey", 'Love Combs Quickly', 'Rank', 'Jellyously', "Libration", "Weaving", "Nightlift", "New York City Toy", "You Only Tell Me You Love Me When You're Dunked", "I Don't Know What You Want But I Can't Give It Any Moor", 'Home and Dine', 'Somewhen Else', 'Dinner Winner', "Live Etc.", "Did You See Me Combing?", "Beautiful Pebble", "Building a Mall", "Minimal Mincemeat", 'Dreaming of the Queue Jump', "Chopping", 'Violets', "One More Dance", "Luna Pork", "Suburban Pie", "Love Is a Bourgeois Constrict", "Vocal Fry", "Electrocity", "Flamboyant Fondant", "Hit Musk", "Miracle Whip", "Sad Robot Word", 'Twenty-noodling', "Yesterday, When I Was Bad", "Your Early Staff", "Give Stupidity a Chant", "King's Crass", "Dancing Stair", "A Red Lettuce Day", "Birthday Bow"],
 "c03_whm": ["Wake Me Up Before You Go-Slow", "Careless Whimper", "Fast Christmas", "Kingdumpling", "Everything He Wants", "I'm Your Van", "The Wedge of Heaven", "Cub Tropicana", "Young Gums Go for It!", "Wham Wrap! Enjoy What You Do", "Bad Toys", "A Rat of Sunshine", "Dove Machine", "Nothing Looks the Same in the Night", "Comb On!", "Like a Maybe", 'Heartbeet Soup', "If You Were Hare", "Credit Cord Baby", "Blue Alarmed with Love", "Battlesensations", "Where Did Your Cart Go?", "A Different Coroner", "Wham! Rap '68", "Club Fantastic Megamax", "Growing for It!", "Do It Tight"],
 "c03_run": ["It's Like Cat", "Sucker M.D.'s", "Hard Dimes", "Sock Box", "Jam-Master Jar", "Hollis Crow", "30 Dogs", "Wake Cup", "Jay's Gum", "Rock the Mouse", "Ring of Rock", "You Walk Too Much", "Ham-Master Jammin'", "Roots, Rap, Reggie", "Can You Sock It Like This", "You're Blond", "It's Not Funky", "Darryl and Joey", "Peter Paper", "It's Tickly", "My Adidos", "Talk This Way", "Is It Liver", "Percussion Pan", "Hit It Bun", "Raising Hen", "You Be Chillin'", "Numb Girl", "Sun of Byford", "Proud to Be Back", "Lord of Lyres", "Run's Hose", "Mary, Marry", "They Call Us Ron-D.M.C.", "Beets to the Rhyme", "Radish Station", "Papa Lazy", "Tougher Than Weather", "I'm Not Going In Like That", "How'd Ya Do It Dew", "Kiss Elaine", "Soul to Rock and Bowl", "Bagtime", "Christmas in Hollow", "Cause", "Ghostbutlers", "What's It All Shout", "Laces", "Ooh, Whatcha Gonna Moo", "Down with the Kong", "Can I Get It, Yo-Yo", "Come On Everyday", "Hit 'Em Lard", "To the Baker", "3 in the Bed", "Big Willow", "Three Little Pigeons", "In the Louse", 'Can I Get a Fitness Band', "Get Oven", "Wheat's Next", "Wreck Ship", "For 10 Tears"],
 "c03_pol": ["Foxanne", "Message in a Battle", "Every Breath You Bake", "Every Little Thing She Does Is Music", "Don't Sit So Close to Me", "Talking on the Moon", "Can't Stand Using You", "So Lovely", "Invisible Bun", "Spirits in the Material Word", "Synchronicity III", "Roxanne Risotto", "Ring of Pain", "Wrapped Around Your Ginger", "De Do Do Do, De Di Di Di", "Bring On the Light", "Hungry for Two", "Tea in the Sauna", "Driven to Fears", "Secret Journal", "Burger by Numbers", "Demolition Mat", "Shadows in the Rein", "Man in a Briefcase", "Masoko Tango", "Reggatta de Blank", "Born in the '60s Soup", "Text to You", "Pecans", "Truffle Hits Everyone", "Visions of the Light", "Low Wife", "Canary in a Goldmine", "Rehumanize Yourshelf", "One Word Not Three", "Behind My Camembert", "Contract", "Dankness", "Does Everyone Share", "Ball Out", "Fiends", "Pole in My Life", "How Stupid Mr. Dates", "I Burp for You", "It's Airtight for You", "Lardlord", "Brotherhood of Biscuits", "No Time This Mime", "Nothing Grieving", "O My Cod", "On Any Other Bay", "Someone to Walk To", "Voices Inside My Bed", "Walking in Your Footprints", "Mrs. Gradenko"],
 "c03_cul": ["Drama Chameleon", "Do You Really Want to Hunt Me", "Time Clock of the Cart", "Church of the Poison Mine", "It's a Mirage", "Victims of Pickles", "Kiss Me Blind", "The Wart Song", "Mope Away", "I'll Tumble 5 Ya", "Mistake No. 4", "The Metal Song", "Mister Fan", "White Toy", "I'm Afraid of Bee", "History Boy", "Live Is Love", "Don't Go Down That Sheet", "Dog Thank You Woman", "Gusto Busto", "Black Honey", "Charging Every Day", "That's the Way I'm Only Trying to Hug You", "Stormsleeper", "Man-Snake", "Melting Plot", "Collar by Numbers", "Romance Revised", "Dangerous Pan", "Unfortunate Ring", "Prime Time", "The Dove", "Don't Walk About It", "Mandarin", "Hello Goodbuy", "The Cream", "Take Console", "Love Twin", "Boy Boy I'm the Buoy", "White Boys Can't Control Us", "You Know I'm Not Lazy", "Love Is Gold You Were Never No Good", "Mirror Rap Trap", "Romance Beyond the Almanac", "I Pay", "Work on Me Bobby", "Heaven's Chickens", 'Seasoning', "Too Bat", "Come Lean", "From Luxury to Heartburn", "Everything I Oven", "Love Hearts", "Don't Dry", "After the Glove", "More Than Lively", "The Frying Game"],
}

# 本家の経歴に沿う側(0=A,1=B)
_REAL = {"c03_drn": [0, 0, 0, 0], "c03_smi": [0, 0, 0, 0], "c03_eur": [0, 0, 0, 0], "c03_psb": [0, 0, 0, 0], "c03_whm": [0, 0, 0, 0], "c03_run": [0, 0, 0, 0], "c03_pol": [0, 0, 0, 0], "c03_cul": [0, 0, 0, 0]}
for _a in ARCS:
    if _a["k"] in _REAL: _a["real"] = _REAL[_a["k"]]
