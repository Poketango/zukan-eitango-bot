import json, os
# 第017回 台本（金閣が燃えた夜、鳳凰だけは屋根にいなかった。ポケモンの焼けた塔と、本当に放火された金閣）
# 2026-11-28 定期作業で作成。ネタ帳「焼けた塔のモデルは本当に放火された金閣」「スズの塔のモデルの銀閣には銀が貼られていない」。
# 裏取り（2つ以上の情報源で照合したものだけを使う）：
#   ゲームの文：クリスタルの台詞の書き起こし（mimemo）と、英語版のプログラムの解析（pokecrystal WiseTriosRoom.asm）、Bulbapedia
#   名前の移り変わり：Bulbapedia（Burned Tower、Bell Tower、Talk:Bell Tower）、ニコニコ大百科
#   モデルの説：公式の発表は見つからなかった。Bulbapedia、TheGamer（2021-04-13）、ファンの投稿で説が割れている
#   東寺の五重塔：観光庁の多言語解説文、日本語版ウィキペディア「東寺」
#   金閣：日本語版ウィキペディア「鹿苑寺」「金閣寺放火事件」、英語版「Kinkaku-ji arson」、Japanese Wiki Corpus、
#     京都市「京都市文化財の年表」、文化遺産オンライン（世界遺産の推薦書）
#   銀閣：日本語版ウィキペディア「慈照寺」、観光庁の多言語解説文、The Japan News（読売新聞）
# 1つの出典でしか確かめられなかったこと（鳳凰を下ろした年、今の保管場所、漆の量、「三日三晩燃えた」）は使っていない。
# 放火した僧の名前と、家族のその後には触れない。モデルは「ファンの説」として話し、公式とは言わない。
L = []
def S(w, face, t, img=None, **kw):
    d = {"w": w, "face": face, "t": t}
    if img: d["img"] = img
    d.update(kw); L.append(d)
def T(sub, t, sec=None, **kw):
    L.append({"type": "title", "sub": sub, "t": t, **({"sec": sec} if sec else {}), **kw})

# 画像（コモンズのファイル名は 2026-11-28 に内蔵ブラウザで実在と中身を確かめた。
#   ゲームの画面は Bulbagarden Archives から取り込み、このフォルダに置いた）
KIN = "commons:Kinkaku-ji the Golden Temple in Kyoto overlooking the lake - high rez.JPG"
KIN2 = "commons:Shariden, Kinkaku-ji, Kyoto, East View 20130811 1.jpg"
KIN3 = "commons:Kinkaku-ji in November 2016 -04.jpg"
KIN4 = "commons:Golden Pavilion Kinkaku-ji 2024.jpg"
KIN5 = "commons:Kinkakuji (Golden Pavilion), Kyoto, Japan.jpg"
KIN6 = "commons:Kinkakuji (Golden Pavilion), Kyoto, Japan - 34036736784.jpg"
KIN_SNOW = "commons:雪の金閣寺 Kinkakuji temple in snow (5360758678).jpg"
KIN_SNOW2 = "commons:雪の金閣寺 Kinkakuji temple in snow (5360756490).jpg"
KIN_PHX = "commons:Kinkaku-ji, Ginkaku-ji and Daitoku-ji - KyotoTemples401.jpg"
KIN_OLD = "commons:Kusakabe Kimbei 1337 Kinkakuji.JPG"
BURNED = "commons:Burned Kinkaku.jpg"
FIRE_ART = "commons:Kawabata Ryūshi - Kinkakuji-Temple on Fire.jpg"
YOSHI = "commons:Yoshimitsu Ashikaga.jpg"
YOSHI_UK = "commons:Ashikaga Yoshimitsu Admiring the Golden Pavilion LACMA M.2007.152.67.jpg"
STATUE = "commons:Lost statue of Ashikaga Yoshimitsu at Kinkaku-ji.jpg"
GIN = "commons:Ginkaku-ji after being restored in 2008.jpg"
GIN2 = "commons:Silver Pavilion (31313034916).jpg"
GIN_PHX = "commons:Ginkakuji 2011-04 (5760370533).jpg"
GIN_SAND = "commons:Ginkakuji Kō getsudai.jpg"
GIN_UP = "commons:Sunlight through clouds and view of Ginkaku-ji Temple from above, Kyoto, Japan.jpg"
TOJI = "commons:Five roofs of Toji-ji, Kyoto.jpg"
TOJI2 = "commons:Toji-pagoda-closeupzoom-dec2013-.jpg"
TOJI3 = "commons:Tō-ji reflected in Hyōtan Pond.jpg"
TOJI_N = "commons:Toji Temple light-up (51473618820).jpg"
MISHIMA = "commons:Yukio Mishima, 1955.jpg"
KYOTO = "commons:Kyoto city map.png"
GS = "wiki:en:Pokémon Gold and Silver"
HGSS = "wiki:en:Pokémon HeartGold and SoulSilver"
# ゲームの画面（Bulbagarden Archives）
E_ART = "ecruteak_art.png"        # エンジュシティの絵（HGSS）
E_MAP = "ecruteak_hgss.png"       # エンジュシティの町（HGSS）
E_ANI = "ecruteak_anime.png"      # アニメのエンジュシティ
BR_GS = "brass_gs.png"            # 金銀の焼けた塔の入り口
BR_BG = "brass_bg.png"            # HGSS の焼けた塔の中（戦いの背景）
B1F = "burned_1f.png"             # HGSS の焼けた塔の1階
B1F_GS = "burned_1f_gs.png"       # 金銀の焼けた塔の1階
BB1F = "burned_b1f.png"           # HGSS の焼けた塔の地下
BEASTS = "beasts_hgss.png"        # 地下の3匹（HGSS）
BEASTS_GS = "beasts_gs.png"       # 地下の3匹（金銀）
B_ANI = "burned_anime.png"        # アニメの焼けた塔
BELL = "bell_hgss.png"            # スズの塔（HGSS）
BELL_BG = "bell_bg.png"           # スズの塔の中（戦いの背景）
BELL_TOP = "bell_summit.png"      # スズの塔のてっぺん
HOOH_TOP = "hooh_bell.png"        # スズの塔のてっぺんのホウオウ
THREE = "row:art:243|ライコウ;art:244|エンテイ;art:245|スイクン"
TWO_P = "row:art:250|ホウオウ（金）;art:249|ルギア（銀）"
TWO_T = "row:" + B1F + "|カネの塔（焼けた塔）;" + BELL + "|スズの塔"
TWO_K = "row:" + KIN + "|金閣（鹿苑寺）;" + GIN + "|銀閣（慈照寺）"
PHX2 = "row:" + KIN_PHX + "|金閣の鳳凰;" + GIN_PHX + "|銀閣の鳳凰"

# ---- コールドオープン ----
S("m", "normal", "1950年7月2日の、夜明け前。\n京都で、国宝の金閣が燃えたの。", FIRE_ART,
  sec="ポケモン雑学採掘場", label="川端龍子『金閣炎上』（1950年）")
S("m", "normal", "建物は、ほとんど焼け落ちたわ。\n火をつけたのは、寺の若い僧だった。", BURNED, label="焼けた金閣（1950年）")
S("m", "normal", "でも、屋根のてっぺんにいるはずの鳳凰は、\n焼けなかったの。", KIN_PHX, label="金閣の屋根の鳳凰",
  big="鳳凰は無事", bf="mincho", ans=True)
S("z", "surprise", "鳳凰って、ホウオウなのだ！？\nなんで鳳凰だけ、無事だったのだ？", "art:250", label="ホウオウ")
L.append({"type": "op", "w": "m", "t": "ポケモンの深い雑学を掘り出す、\nポケモン雑学採掘場。",
          "say": "ポケモンの深い雑学を掘り出す、ポケモン雑学さいくつじょう。"})

# ---- 導入 ----
S("z", "happy", "今日の坑道は、紅葉の葉っぱが\n吹きこんで、きれいなのだ。", E_ART, sec="導入　ふたつの塔の町", label="紅葉の町")
S("m", "normal", "紅葉といえば、ジョウト地方の\nエンジュシティを思い出すわね。", E_ART, label="エンジュシティ（HGSS）")
S("z", "happy", "ハートゴールドで、何十時間も\nいた町なのだ。塔が2つあるのだ。", E_MAP, label="エンジュシティ（HGSS）")
S("m", "normal", "その片方は、焼けた塔。\n昔、火事で焼けた塔よ。", B1F, label="焼けた塔")
S("m", "normal", "エンジュは、京都が元になった町だと、\nファンの間では言われているの。", E_ANI, label="アニメのエンジュシティ")
S("m", "normal", "そして京都には、本当に焼けた\n金色の建物があるのよ。", BURNED, label="焼けた金閣（1950年）")
S("z", "think", "焼けた塔の元は、\nその金閣なのだ？", TWO_T, label="エンジュの2つの塔")
S("m", "normal", "今日は、ゲームの塔の言い伝えと、\n本当に燃えた金閣を、並べて掘るわ。", TWO_K, label="ゲームの塔と京都の寺")
T("本日の採掘", "焼けた金閣の鳳凰は、なぜ無事だった？", font="mincho")

# ---- 第一層 ----
T("第一層", "カネの塔とスズの塔", "第一層　エンジュの2つの塔", font="mincho",
  x={"head": "ポケモンの焼けた塔は\n昔は「カネの塔」と\n呼ばれていた",
     "img": [B1F], "bubble": "名前があったのだ", "who": "z",
     "post": "ポケモン金銀のエンジュシティにある焼けた塔。町の人は、昔の名前を「カネの塔」と呼びます。およそ150年前に雷が落ちて焼け、もう1つの塔は「スズの塔」。英語版では、カネを Brass、スズを Tin と訳しました。あなたはどちらの塔が好きですか？"})
S("m", "normal", "ポケモン金銀が出たのは、1999年。\n舞台はジョウト地方よ。", GS, label="ポケモン金・銀（1999年）")
S("m", "normal", "2009年には、作り直した\nハートゴールドとソウルシルバーが出たわ。", HGSS, label="ハートゴールド・ソウルシルバー")
S("m", "normal", "その間の2000年には、\nポケモンクリスタルも出ているわね。", GS, label="ポケモンクリスタル（2000年）")
S("z", "happy", "ボクがやりこんだのは、\nハートゴールドのほうなのだ。", HGSS, label="ハートゴールド・ソウルシルバー")
S("z", "happy", "万歩計のポケウォーカーも、\n毎日持ち歩いていたのだ。", HGSS, label="ハートゴールド・ソウルシルバー")
S("m", "normal", "エンジュシティには、\n大きな塔が2つ建っているの。", E_MAP, label="エンジュシティ（HGSS）")
S("m", "normal", "片方が、焼けた塔。\n中は黒こげで、床に大きな穴があいているわ。", B1F, label="焼けた塔の1階（HGSS）")
S("z", "think", "金銀のころは、\nもっと地味な見た目だったのだ。", B1F_GS, label="焼けた塔の1階（金銀）")
S("m", "normal", "町の僧が、この塔の昔話を\n聞かせてくれるのよ。", BR_BG, label="焼けた塔の中")
S("m", "normal", "「今から、およそ150年前、\n1つの塔に、雷が落ちたそうです」", BR_BG, label="ゲームの中の言葉",
  bf="mincho", ans=True)
S("m", "normal", "焼けた塔は、昔は「カネの塔」と\n呼ばれていたの。", BR_GS, label="カネの塔（金銀）")
S("m", "normal", "もう1つが、「スズの塔」。\n今も焼けずに建っている塔よ。", BELL, label="スズの塔（HGSS）")
S("m", "normal", "僧の話では、カネの塔は\n「ポケモンを起こす塔」と言われていたの。", BR_GS, label="ポケモンを起こす塔")
S("m", "normal", "スズの塔は、\n「ポケモンを休める塔」よ。", BELL, label="ポケモンを休める塔")
S("z", "think", "起こす塔と、休める塔。\n2つで1組の塔なのだ。", TWO_T, label="起こす塔と休める塔")
S("z", "surprise", "カネとスズ。\nどっちも、金属の名前なのだ。", TWO_T, label="カネの塔とスズの塔")
S("m", "normal", "そうね。でも、カネには鐘、\nスズには鈴の意味も重なるのよ。", TWO_T, label="カネ＝金・鐘　スズ＝錫・鈴")
S("z", "think", "鐘と鈴。どっちも、\n鳴らすものでもあるのだ。", BELL_BG, label="スズの塔の中")
S("m", "normal", "英語版では、そこが訳しにくかったの。\nカネはブラス、つまり真ちゅう。", BR_GS, label="英語では Brass Tower",
  say="英語版では、そこが訳しにくかったの。カネはブラス、つまり、しんちゅう。")
S("m", "normal", "スズはティン。金属のスズね。\nでもハートゴールドで、名前が変わったわ。", BELL, label="英語では Tin Tower")
S("m", "normal", "英語版では、ベルタワー。\n鈴のほうの意味に、変えたのよ。", BELL_TOP, label="2009年から Bell Tower", ans=True)
S("z", "surprise", "日本語の名前は、1つで\n2つの意味を持っていたのだ。", TWO_T, label="1つの名前に2つの意味")

# ---- 第二層 ----
T("第二層", "雷と3匹とホウオウ", "第二層　焼けた塔の言い伝え", font="fude",
  x={"head": "焼けた塔で死んだ3匹を\nよみがえらせたのが\nホウオウだった",
     "img": [THREE], "bubble": "伝説の3匹なのだ", "who": "z",
     "post": "ポケモン金銀の言い伝えでは、およそ150年前、カネの塔に雷が落ちて燃え、名もないポケモンが3匹死にました。空から現れたホウオウが3匹をよみがえらせ、ライコウ、エンテイ、スイクンになったといいます。3匹の中で、だれが好きですか？"})
S("m", "normal", "僧の話には、続きがあるの。\nカネの塔が焼けたとき、ポケモンが3匹死んだ。", BB1F, label="焼けた塔の地下（HGSS）")
S("m", "normal", "すると、ホウオウが空から現れて、\n3匹をよみがえらせたそうよ。", "art:250", label="ホウオウ")
S("z", "happy", "それが、ライコウ、エンテイ、\nスイクンなのだ！", THREE, label="よみがえった3匹", ans=True)
S("m", "normal", "雷のライコウ、炎のエンテイ、\n火を消した雨のスイクン、ね。", THREE, label="雷・炎・雨")
S("m", "normal", "塔に落ちた雷、塔を焼いた炎、\n炎を消した雨。それが3匹の元とされているの。", THREE, label="雷・炎・雨から生まれた3匹")
S("z", "happy", "焼けた塔の地下で、3匹が\nいっせいに逃げるのは、名場面なのだ。", BEASTS, label="焼けた塔の地下の3匹（HGSS）")
S("m", "normal", "金銀のころは、こんな画面だったわね。", BEASTS_GS, label="焼けた塔の地下の3匹（金銀）")
S("z", "happy", "クリスタルでは、逃げたスイクンを\nあちこち追いかけたのだ。", "art:245", label="スイクン")
S("m", "normal", "英語版の言い伝えには、銀色の大きなポケモンが\nカネの塔の上で休んでいた、ともあるわ。", "art:249", label="ルギア")
S("z", "think", "ルギアなのだ。\n塔が焼けて、出ていったのだ？", "art:249", label="ルギア")
S("m", "normal", "そう言われているわ。そしてホウオウは、\nスズの塔のてっぺんに来るの。", HOOH_TOP, label="スズの塔のホウオウ（HGSS）")
S("m", "normal", "ホウオウは、アニメでも1997年の\n第1話で、空を飛ぶ姿が描かれているの。", "art:250", label="アニメ第1話のホウオウ")
S("z", "surprise", "金銀が出る前から、\n出ていたのだ！？", "art:250", label="アニメ第1話（1997年）")
S("z", "think", "ホウオウが金、ルギアが銀。\nゲームの名前と、同じなのだ。", TWO_P, label="金のホウオウ・銀のルギア")
S("m", "normal", "ホウオウの名前の元は、\n中国から伝わった、鳳凰という鳥よ。", "art:250", label="ホウオウ＝鳳凰")
S("z", "happy", "ホウオウの専用の技も、\nせいなるほのお、なのだ。", "art:250", label="専用の技「せいなるほのお」")
S("m", "normal", "鳳凰は、よい世の中になると現れる、\nめでたい鳥とされてきたの。", "art:250", label="めでたい鳥、鳳凰")
S("m", "normal", "その鳳凰の像が、京都の金閣と銀閣の\n屋根のてっぺんに、立っているの。", PHX2, label="金閣と銀閣の鳳凰", ans=True)
S("z", "surprise", "金と銀に、\n鳳凰！？", PHX2, label="金閣と銀閣の鳳凰")

# ---- 第三層 ----
T("第三層", "モデルはどこ？", "第三層　ファンの説", font="reggae",
  x={"head": "ポケモンの焼けた塔とスズの塔の\nモデルは公式に\n発表されていない",
     "img": [TWO_K], "bubble": "説が割れているのだ", "who": "z",
     "post": "エンジュシティの2つの塔のモデルは、公式には発表されていません。ファンの間では、金閣と銀閣、そして雷などで4回焼けた東寺の五重塔が挙がります。金銀の伝説の2匹、ホウオウの名前の元の鳳凰は、金閣と銀閣の屋根にいます。あなたはどの説だと思いますか？"})
S("z", "happy", "じゃあ、カネの塔が金閣、\nスズの塔が銀閣で、決まりなのだ。", TWO_K, label="金閣と銀閣")
S("m", "normal", "そう言うファンは多いわ。でも、\n公式に発表された話では、ないの。", TWO_K, label="公式の発表はない")
S("m", "normal", "海外のポケモンの百科事典では、\n逆の組み合わせが書かれているくらいよ。", TWO_K, label="ファンの説は割れている")
S("m", "normal", "そこでは、スズの塔は、\n金閣と、別の寺の塔を混ぜたもの、とされているわ。", TWO_K, label="海外の百科事典の説")
S("z", "think", "逆なのだ？\nファンでも、意見が割れているのだ。", TWO_T, label="ファンの説は割れている")
S("m", "normal", "それに、ゲームの塔は細長い塔よね。\n英語版では、9階建てと言っているの。", BELL, label="スズの塔（HGSS）")
S("m", "normal", "金閣は、3階建て。\n形はだいぶ違うわ。", KIN2, label="金閣（3階建て）")
S("z", "think", "たしかに。金閣は、\n塔って感じじゃないのだ。", KIN2, label="金閣（3階建て）")
S("m", "normal", "そこで名前が挙がるのが、京都の東寺。\n五重塔の高さは、およそ55メートル。", TOJI, label="東寺の五重塔",
  say="そこで名前が挙がるのが、京都の、とうじ。五重塔の高さは、およそ55メートル。")
S("m", "normal", "東寺は、平安京ができてまもなく、\n都の入り口に建てられた寺よ。", TOJI3, label="東寺（教王護国寺）",
  say="とうじは、平安京ができてまもなく、都の入り口に建てられた寺よ。")
S("m", "normal", "木で造られた塔では、\n日本でいちばん高い塔よ。", TOJI3, label="木造の塔で日本一")
S("m", "normal", "そしてこの塔は、雷の火などで、\nこれまで4回も焼けているの。", TOJI2, label="4回焼けた五重塔", ans=True)
S("z", "surprise", "雷で焼けた塔！\nカネの塔と、そっくりなのだ。", TOJI_N, label="東寺の五重塔")
S("m", "normal", "今の塔は、1644年に\n建て直されたものよ。", TOJI, label="1644年に建て直し")
S("m", "normal", "つまり、モデルは1つとは限らないの。\n京都の寺の、いいとこ取りかもしれないわ。", KYOTO, label="京都市")
S("z", "happy", "京都の寺をめぐって、\nゲームの元を探すのも、楽しそうなのだ。", KYOTO, label="京都市")
S("z", "think", "じゃあ、金閣が本当に焼けた話は、\nどうつながるのだ？", BURNED, label="焼けた金閣（1950年）")
S("m", "normal", "それは、金閣と鳳凰の話を\n掘ってみると、見えてくるわ。", KIN_PHX, label="金閣の鳳凰")

# ---- 第四層 ----
T("第四層", "金閣と銀閣", "第四層　金閣と銀閣", font="deco",
  x={"head": "銀閣には\n銀が一度も\n貼られていなかった",
     "img": [GIN], "bubble": "銀閣なのに！？", "who": "z",
     "post": "京都の銀閣（慈照寺の観音殿）には、銀箔が貼られていません。2007年の調べで、建てられたときから銀は貼られていなかったとわかりました。銀閣という呼び名は、江戸時代に広まったものです。ポケモン金銀のスズの塔の元とも言われる建物です。銀閣に行ったことはありますか？"})
S("m", "normal", "金閣の本当の名前は、鹿苑寺の舎利殿。\n寺の建物の1つよ。", KIN, label="鹿苑寺の舎利殿（金閣）",
  say="金閣の本当の名前は、ろくおんじの、しゃりでん。寺の建物の1つよ。")
S("m", "normal", "1397年、室町幕府の将軍だった\n足利義満が、ここに屋敷を造り始めたの。", YOSHI, label="足利義満",
  say="1397年、室町幕府の将軍だった、あしかがよしみつが、ここに屋敷を造り始めたの。")
S("m", "normal", "義満が亡くなったあと、\n屋敷は寺に変わり、鹿苑寺になったわ。", KIN3, label="屋敷が寺になった",
  say="よしみつが亡くなったあと、屋敷は寺に変わり、ろくおんじになったわ。")
S("m", "normal", "金閣は3階建てで、\n階ごとに、建て方が違うの。", KIN2, label="3階建ての舎利殿")
S("m", "normal", "1階は貴族の屋敷、2階は武士の家、\n3階は禅の寺の造りよ。", KIN2, label="1階・2階・3階で違う造り")
S("z", "surprise", "1つの建物に、\n3つの建て方なのだ。", KIN3, label="3つの建て方")
S("z", "think", "金ピカなのは、\n義満の趣味なのだ？", YOSHI_UK, label="金閣を眺める義満（浮世絵）",
  say="きんぴかなのは、よしみつの趣味なのだ？")
S("m", "normal", "金箔を貼ったのは義満よ。でも明治の\n修理の前には、金箔はほとんどはげていたの。", KIN_OLD, label="明治時代の金閣の写真")
S("z", "surprise", "はげていたのだ！？\nじゃあ、ずっと金色じゃなかったのだ。", KIN_OLD, label="明治時代の金閣の写真")
S("m", "normal", "そして、銀閣。こちらは、\n義満の孫の足利義政が建てた、観音殿よ。", GIN, label="慈照寺の観音殿（銀閣）",
  say="そして、ぎんかく。こちらは、よしみつの孫の、あしかがよしまさが建てた、かんのんでんよ。")
S("m", "normal", "金閣から、およそ90年あと。\n1489年に、屋根の骨組みが組まれたわ。", GIN_SAND, label="1489年に棟上げ")
S("z", "happy", "銀閣だから、\n銀がぴかぴかなのだ。", GIN2, label="慈照寺の観音殿（銀閣）")
S("m", "normal", "それが、銀は一度も貼られていないの。\n2007年の調べで、わかったことよ。", GIN, label="銀は貼られていない", ans=True)
S("z", "shock", "銀閣なのに、\n銀がないのだ！？", GIN2, label="銀は貼られていない")
S("m", "normal", "上の階は、黒い漆の塗りだったの。\n銀閣という呼び名は、江戸時代に広まったものよ。", GIN_UP, label="銀閣の呼び名は江戸時代から")
S("m", "normal", "銀閣の庭には、白い砂を\n山の形に盛った、向月台もあるわ。", GIN_SAND, label="銀閣の庭の向月台",
  say="ぎんかくの庭には、白い砂を、山の形に盛った、こうげつだいもあるわ。")
S("z", "think", "銀のかわりに、\n白い砂が光っているみたいなのだ。", GIN_SAND, label="銀閣の庭の向月台")
S("m", "normal", "でも屋根の上には、どちらにも\n鳳凰が立っているの。", PHX2, label="金閣と銀閣の鳳凰")
S("m", "normal", "金閣は金色の鳳凰。\n銀閣は銅の鳳凰で、東を向いているわ。", PHX2, label="金の鳳凰と銅の鳳凰")
S("z", "think", "金と銀の建物に、\nどっちもホウオウがいるのだ。", "art:250", label="ホウオウ")

# ---- 第五層 ----
T("第五層", "1950年7月2日", "第五層　金閣が燃えた日", font="fude",
  x={"head": "1950年に放火された金閣\n屋根の鳳凰だけは\n前に下ろされていて無事だった",
     "img": [BURNED], "bubble": "鳳凰は無事なのだ", "who": "z",
     "post": "1950年7月2日の未明、京都の金閣が寺の若い僧の放火で焼けました。国宝の建物も、中の足利義満の像も焼けましたが、屋根の鳳凰は、火事の前に屋根から下ろされて寺にしまわれていたので、焼けずに残りました。いまは京都市の文化財です。"})
S("m", "normal", "1950年7月2日の夜明け前。\n午前3時7分に、消防の見張り台が火を見つけたわ。", FIRE_ART, label="1950年7月2日",
  say="1950年7月2日の夜明け前。午前3時7分に、消防の見張り台が、火を見つけたわ。")
S("m", "normal", "最初に見せた絵は、日本画家の川端龍子が、\nその年に描いた『金閣炎上』よ。", FIRE_ART, label="川端龍子『金閣炎上』",
  say="最初に見せた絵は、日本画家の、かわばたりゅうしが、その年に描いた、きんかくえんじょう、よ。")
S("m", "normal", "火をつけたのは、この寺で修行していた\n21歳の僧。大学に通う学生でもあったの。", BURNED, label="21歳の見習いの僧")
S("m", "normal", "消防が駆けつけたけれど、\n古い木の建物は、あっという間に燃えたわ。", FIRE_ART, label="燃える金閣")
S("z", "shock", "お寺の人が、\n自分で火をつけたのだ！？", BURNED, label="焼けた金閣（1950年）")
S("m", "sad", "国宝の建物も、中にあった\n足利義満の像も、焼けてしまったわ。", STATUE, label="焼けた足利義満の像",
  say="国宝の建物も、中にあった、あしかがよしみつの像も、焼けてしまったわ。")
S("z", "sad", "550年あまり残っていたものが、\n一晩で、なくなったのだ…。", BURNED, label="焼けた金閣（1950年）", v="namida")
S("z", "think", "どうして、\nそんなことをしたのだ？", BURNED, label="焼けた金閣（1950年）")
S("m", "normal", "僧は、金閣と死ぬつもりだった、と\n話したそうよ。", BURNED, label="本当の理由はわからない")
S("m", "normal", "でも裁判では、自分の動機について、\nはっきりとは答えなかったの。", BURNED, label="本当の理由はわからない")
S("m", "normal", "判決は、懲役7年。\n僧は、出てきた次の年に、病気で亡くなったわ。", BURNED, label="判決は懲役7年")
S("z", "sad", "金閣も僧も、\nどっちも助からなかったのだ。", BURNED, label="焼けた金閣（1950年）")
S("z", "think", "それで、屋根の鳳凰は、\nどうして無事だったのだ？", KIN_PHX, label="金閣の鳳凰")
S("m", "normal", "鳳凰は、火事の前に\n屋根から下ろされていたの。", KIN_PHX, label="火事の前に下ろされていた", ans=True)
S("m", "normal", "古い鳳凰は寺の中にしまわれ、\n屋根には、代わりの鳳凰が付いていたのよ。", KIN_SNOW, label="今の金閣の屋根の鳳凰")
S("z", "surprise", "だから、建物が焼けても、\n本物の鳳凰は残ったのだ！", KIN_PHX, label="焼けなかった鳳凰")
S("m", "normal", "焼け残った鳳凰は、1999年に\n京都市の文化財になっているわ。", KIN_PHX, label="京都市の文化財（1999年）")
S("z", "happy", "炎をくぐり抜けた鳳凰。\nまるで、本物のホウオウなのだ。", "art:250", label="ホウオウ")
S("m", "normal", "ほんとうは、炎の中にいなかったから\n無事だったのだけれどね。", KIN_PHX, label="火事のときは屋根にいなかった")

# ---- 最深層 ----
T("最深層", "よみがえった金閣", "最深層　よみがえった金閣", font="deco",
  x={"head": "放火から5年で\n金閣は建て直された",
     "img": [KIN4], "bubble": "5年でなのだ", "who": "z",
     "post": "1950年に焼けた金閣は、1952年に工事を始め、1955年10月に建て直されました。明治の修理のときの細かい図面が残っていたおかげで、元の姿どおりに造れたといいます。1987年には、ふつうの5倍の厚さの金箔を、およそ20万枚貼り直しました。"})
S("m", "normal", "焼けた金閣は、1952年に工事を始めて、\n1955年の10月に建て直されたの。", KIN4, label="1955年に再建")
S("z", "surprise", "たった5年で、\n元どおりなのだ？", KIN3, label="1955年に再建")
S("m", "normal", "明治の修理のときに、細かい図面を\n作っていたおかげで、元の姿で造れたのよ。", KIN_OLD, label="明治の修理の図面のおかげ")
S("m", "normal", "1987年には、金箔を貼り直したわ。\nふつうの5倍の厚さの金箔を、およそ20万枚。", KIN5, label="5倍の厚さの金箔",
  say="1987年には、金箔を貼り直したわ。ふつうの5倍の厚さの金箔を、およそ20万まい。")
S("m", "normal", "使った金は、およそ20キロよ。", KIN6, label="金はおよそ20キロ")
S("z", "happy", "だから今の金閣は、\nこんなに金ピカなのだ。", KIN_SNOW2, label="今の金閣",
  say="だから今の金閣は、こんなに、きんぴかなのだ。")
S("z", "think", "でも、建物は新しくなったのだ。\n元の金閣は、もう戻らないのだ。", KIN4, label="建て直された金閣")
S("m", "normal", "そうね。だからこそ、火事の前から\n残った鳳凰は、大切にされているのよ。", KIN_PHX, label="火事の前から残る鳳凰")
S("m", "normal", "この放火は、小説にもなったわ。\n三島由紀夫の『金閣寺』。1956年よ。", MISHIMA, label="三島由紀夫（1955年）")
S("m", "normal", "水上勉も、僧の生い立ちを調べて、\n1979年に『金閣炎上』を書いたわ。", KIN_SNOW, label="水上勉『金閣炎上』（1979年）",
  say="みずかみつとむも、僧の生い立ちを調べて、1979年に、きんかくえんじょう、を書いたわ。")
S("z", "think", "絵も小説も、\nみんな同じ火事を描いているのだ。", FIRE_ART, label="川端龍子『金閣炎上』")
S("m", "normal", "1994年には、金閣も銀閣も東寺も、\n世界遺産に選ばれたの。", TWO_K, label="古都京都の文化財（世界遺産）")
S("z", "think", "ゲームの焼けた塔は、\nずっと焼けたままなのだ。", B1F, label="焼けた塔（HGSS）")
S("m", "normal", "ハートゴールドでも、焼けた塔は\n建て直されなかったわね。", BR_BG, label="焼けた塔（HGSS）")
S("m", "normal", "焼けた塔は、焼け跡のまま。\n伝説のポケモンがよみがえった場所としてね。", BB1F, label="焼けた塔の地下（HGSS）")
S("m", "normal", "金閣は、建物は焼けたけれど、\n鳳凰を残して、よみがえったの。", KIN, label="よみがえった金閣")
S("z", "happy", "炎の中からよみがえるのは、\nホウオウの言い伝えと、同じなのだ。", "art:250", label="ホウオウ")

# ---- まとめ ----
S("m", "think", "今日の答え。金閣の鳳凰は、火事の前に\n屋根から下ろされていたから、焼けなかった。", KIN_PHX, label="今日の答え", sec="まとめ")
S("m", "normal", "焼けた塔のモデルが金閣かどうかは、\n公式には、わからないままよ。", TWO_T, label="モデルは公式には不明")
S("z", "think", "でも、エンジュの町を歩くと、\n京都の寺に行きたくなるのだ。", E_ART, label="エンジュシティ")
S("m", "normal", "あなたは、焼けた塔のモデルは、\nどこだと思う？", TWO_K, label="あなたはどの説？")
S("z", "happy", "今日の採掘はここまでなのだ。\nチャンネル登録も、よろしくなのだ。", E_ART, label="エンジュシティ")
L.append({"type": "ed"})

script = {
    "no": 17,
    "title": "【焼けた塔の元ネタ？】金閣が燃えた夜、鳳凰だけは屋根にいなかった。",
    "neta": "焼けた塔のモデルは本当に放火された金閣",
    "thumb": {"layout": "v2", "pre": "焼けた塔の元ネタ？", "big": ["金閣", "放火"], "hl": 1, "hl_color": "red",
              "fonts": ["mincho", "mincho"], "pre_font": "maru", "pre_size": 60,
              "back": FIRE_ART, "photo": BURNED, "photo_label": "1950年の金閣", "chara": None, "big_w": 620,
              "big_size": [200, 200]},
    "lines": L,
}
here = os.path.dirname(os.path.abspath(__file__))
json.dump(script, open(os.path.join(here, "script.json"), "w"), ensure_ascii=False, indent=1)
n = sum(len(l.get("t", "").replace("\n", "")) for l in L)
print("行数", len(L), "字幕の字数", n)
