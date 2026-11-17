import json, os
# 第007回 台本（アメリカの州都トピーカが、ピカチュウに降伏した日。アメリカで最初のポケモンの会）
# 2026-11-17 プロデューサーの指示で作った回。2回目の書き直し：ずんだもんはルビサファ〜BW世代（初代や対戦の話に無理につなげない）。ボケを足さず、事実への素直な反応にとどめる（滑らないことを優先）。
# 2026-11-18 3回目の直し：自作の表をやめて実物の写真に。赤緑と赤青の話を足す。人物や物の説明不足を直す。チャンネル名を「採掘場」に。
# 1回目の書き直しの前：1回目の台本は「ポケモンの話になっていない（半分がGoogleと街の改名）」
# 「型をなぞった前振りと回収」「ずんだもんが驚くだけ」で没。ポケモンの会の中身を主役に書き直した。
L = []
def S(w, face, t, img=None, **kw):
    d = {"w": w, "face": face, "t": t}
    if img: d["img"] = img
    d.update(kw); L.append(d)
def T(sub, t, sec=None, **kw):
    L.append({"type": "title", "sub": sub, "t": t, **({"sec": sec} if sec else {}), **kw})

# 画像
TOPEKA = "commons:Topeka skyline and Kansas River.jpg^wiki:en:Topeka,_Kansas"
TOPEKA2 = "commons:Topeka, Kansas.JPG^" + TOPEKA
CAPITOL = "commons:Kansas State Capitol.jpg^wiki:en:Kansas_State_Capitol"
KSUS = "commons:Kansas in United States.svg^wiki:en:Kansas"
KANSA = "commons:Charles Bird King - Monchousia (White Plume), Kansa - Google Art Project.jpg^commons:Monchousia (White Plume) (7844233464) (2).jpg"
DIG = "commons:Potato harvest - geograph.org.uk - 248459.jpg^wiki:en:Potato"
REDBLUE = "wiki:en:Pokémon_Red_and_Blue^commons:PokemonRedBlueYellowBack.jpg"
GB = "commons:Game-Boy-FL.jpg^wiki:en:Game_Boy"
SKY = "wiki:en:Parachuting^wiki:en:Skydiving"
FORBES = "commons:Forbesafb-02242002.jpg^wiki:en:Topeka_Regional_Airport"
BEETLE = "commons:Voiture Pikachu avec Peluches.jpg"
GLOGO = "commons:Google logo (2010-2013).svg^wiki:en:Google"
BUNTEN = "commons:Topeka mayor bill bunten.jpg"
TOPEKALOGO = "web:https://www.google.com/logos/2010/topeka-hp.gif"
GFKC = "commons:GoogleFiberKansasCity.JPG^wiki:en:Google_Fiber"
TOPIKA = "row:" + TOPEKA.split("^")[0] + "|トピーカ;art:25|ピカチュウ"
MAYOR18 = "row:commons:Michelle De La Isla.jpg|デ・ラ・イスラ市長;commons:Gage Park Zoo Topeka-KS(2463602266).jpg|ゲージ公園の動物園"
PIKABUI = "wiki:en:Pokémon:_Let's_Go,_Pikachu!_and_Let's_Go,_Eevee!^commons:Nintendo-Pokemon-Lets-Go-Poke-Ball-Plus-Controller.jpg"
PIKA = "art:25"
STARYU = "art:120"
STARMIE = "art:121"
SQUIRTLE = "art:7"
DIGLETT = "art:50^wiki:en:Diglett"
# 実物の写真（2026-11-18 ユーザーの指示で、自作の表をやめて全部実物の画像にした）
def J(name):   # The Johto Times「Topikachu: When Pokémon came to America」（2023年）の写真
    return ("web:https://substackcdn.com/image/fetch/w_1456,c_limit,f_jpg,q_auto:good/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F" + name
            + "^web:https://substack-post-media.s3.amazonaws.com/public/images/" + name)
KANSAN = "web:https://digital.lib.ku.edu/islandora/object/ku-udk%3A48032/datastream/JPG/download"   # 学生新聞の1面
RUN = J("fe28c6fb-99bd-42dd-829c-a23399c73228_650x382.jpeg")      # ぬいぐるみに走る子どもたち
SCHED = J("c28549e3-bfb7-4406-b46e-beeb0953c420_1280x960.jpeg")   # その日の予定表
FRAMED = J("092730c8-79fb-48cf-b13b-7e8f5ef21fce_960x1280.jpeg")  # シェインさんの額に入れたTシャツ
PLUSH = J("d1a7d927-e216-461f-b563-6279235628db_480x640.jpeg")    # パラシュートつきのピカチュウ
LANYARD = J("4c2a61fa-332d-4cfe-a8df-84d4a3acaa0e_820x1094.jpeg") # マスタートレーナー見習いの名札
VHS = J("a9d9f8ba-6935-4c8d-8e44-61bc5146d531_1280x960.jpeg")     # 届いたビデオ
BUGS = J("d9249a71-5d6c-42cb-b847-ea81eb83393f_1725x1140.jpeg")   # 10台のピカチュウのビートル
SKYD = J("4a8f7390-3c97-4aa2-be13-10e572bea9bb_1807x1202.jpeg")   # スカイダイバー
BALLS = J("5788eade-8a11-48fe-ad50-156f2e0f38c4_1128x845.jpeg")   # はずむボール
TRUNK = J("d2a4969d-7c48-4a0c-a453-b47cea11098c_1781x1167.jpeg") + "^" + J("a7a62dc6-f960-4f51-ad45-59f41ea10b22_1024x768.jpeg")  # トランクのテレビ
LETTER = J("1de267a6-3ccf-4415-afc5-2c42e610a68b_1076x1320.jpeg") # 招待状
SQUIRTD = J("fc6c73cb-6e00-4327-86cb-dcfc379b34ff_1797x1166.jpeg")# ゼニガメのかざり
# 日米の箱絵（Bulbagarden Archives より。描画のサーバーから取れないので、この回のフォルダに置いた）
RED_JP = "red_jp.jpg"
GREEN_JP = "green_jp.jpg"
BLUE_JP = "blue_jp.jpg"
RED_EN = "red_en.jpg"
BLUE_EN = "blue_en.jpg"
RG_JP = "row:" + RED_JP.split("^")[0] + "|日本の赤（1996年2月）;" + GREEN_JP.split("^")[0] + "|日本の緑（1996年2月）"
RB_EN = "row:" + RED_EN.split("^")[0] + "|アメリカの赤（1998年9月）;" + BLUE_EN.split("^")[0] + "|アメリカの青（1998年9月）"
MEW = "art:151"

# ---- コールドオープン ----
S("m", "normal", "1998年、アメリカの州都がひとつ、\nピカチュウに降伏したの。", CAPITOL, sec="ポケモン雑学採掘場", label="カンザス州の議事堂（トピーカ）", lf="mincho")
S("z", "surprise", "降伏？\nピカチュウに、なのだ？", PIKA)
S("m", "normal", "市の名前を1日だけ、\n「トピカチュウ」に変えたのよ。", TOPIKA, big="トピカチュウ", bf="potta")
S("z", "think", "それを降伏と呼ぶのは、\nだいぶ大げさなのだ。", TOPIKA)
S("m", "happy", "当時の新聞が、\nそう書いたの。", KANSAN, label="カンザス大学の学生新聞（1998年8月28日）", lf="mincho")
L.append({"type": "op", "w": "m", "t": "ポケモンの深い雑学を掘り出す、\nポケモン雑学採掘場。", "say": "ポケモンの深い雑学を掘り出す、ポケモン雑学さいくつじょう。"})

# ---- 導入 ----
S("z", "think", "めたん、さっきから\n何を読んでるのだ？", KANSAN, sec="導入　任天堂の侵略", label="カンザス大学の学生新聞（1998年8月28日）", lf="mincho")
S("m", "normal", "1998年の、カンザス大学の学生新聞。見出しは\n「任天堂の侵略の標的になったトピーカ」。", KANSAN, label="見出し「Topeka target of Nintendo Invasion」", lf="mincho")
S("z", "surprise", "さっきの降伏の話は、\nこれなのだ？", KANSAN, label="カンザス大学の学生新聞（1998年8月28日）", lf="mincho")
S("m", "normal", "そう。アメリカで初めての、ポケモンの会の記事よ。\nゲームの発売の1か月前に開かれたの。", KANSAN, label="カンザス大学の学生新聞（1998年8月28日）", lf="mincho")
S("m", "normal", "アメリカで発売されたのは「赤」と「青」。\n日本で最初に出たのは「赤」と「緑」だったわね。", RG_JP)
S("z", "think", "緑は、\nどこに行ったのだ？", RB_EN)
S("m", "normal", "日本では赤と緑のあとに、コロコロコミックの通信販売で\n「青」が出たの。絵やせりふを新しくした版よ。", BLUE_JP, label="日本の青（1996年10月）")
S("m", "normal", "アメリカ版は、この日本の「青」のプログラムと絵を\n土台にして作られたの。", BLUE_JP, label="日本の青（1996年10月）")
S("m", "normal", "出てくるポケモンの分け方だけは「赤」と「緑」のものを使って、", RB_EN)
S("m", "normal", "名前を「赤」と「青」にしたのね。", RB_EN)
S("z", "surprise", "じゃあ、アメリカの「赤」は、\n日本の「赤」とも違うのだ？", RB_EN)
S("m", "normal", "そう。見た目は、\n日本の「青」に近いの。", BLUE_JP, label="日本の青（1996年10月）")
S("m", "normal", "しかも、日本語を英語に差し替えるだけではすまなくて、\nプログラムを一から作り直したそうよ。", RB_EN)
S("m", "normal", "それで、日本で赤と緑が出てから\n2年半も遅れたの。", RB_EN)
S("z", "think", "緑は、海外では\n一度も出てないのだ？", GREEN_JP, label="日本の緑（1996年2月）")
S("m", "normal", "出てないわ。2016年に3DSで配信されたときも、\n緑は日本だけだったの。", GREEN_JP, label="日本の緑（1996年2月）")
S("m", "normal", "そのアメリカで、ゲームが出る前に、\n任天堂が何をしたか。", KANSAN, label="カンザス大学の学生新聞（1998年8月28日）", lf="mincho")
T("本日の採掘", "アメリカで最初のポケモンの会で、何が起きた？", font="mincho")

# ---- 第一層 ----
T("第一層", "州都、ピカチュウに降伏す", "第一層　州都の降伏", font="fude",
  x={"head": "1998年、アメリカの州都が\nピカチュウに降伏した\n（記事の言葉どおり）",
     "img": [CAPITOL], "bubble": "市長、ノリノリなのだ", "who": "z",
     "post": "1998年8月27日、アメリカのカンザス州の州都トピーカで、アメリカで初めてのポケモンの会が開かれました。市長は1日だけ市の名前を「トピカチュウ」にすると宣言し、学生新聞は「市長が街をポケモンに明け渡すと、空からの攻撃が始まった」と書きました。何が降ってきたと思いますか？"})
S("m", "normal", "1998年8月27日。カンザス州の州都トピーカで、\nアメリカで初めてのポケモンの会が開かれたの。", KSUS, label="カンザス州")
S("m", "normal", "市長は、この日だけ\n市の名前をトピカチュウにすると宣言したわ。", TOPIKA)
S("m", "normal", "記者には「今日だけよ。\n市長ができる楽しい仕事のひとつね」って。", CAPITOL, label="ジョーン・ワグノン市長の言葉", lf="mincho")
S("z", "happy", "市長、\nノリノリなのだ。", CAPITOL, label="ジョーン・ワグノン市長の言葉", lf="mincho")
S("m", "normal", "会場は、昔の空軍基地の飛行場。\n広い原っぱに、ゲームやグッズのテントが並んだの。", FORBES, label="会場になった昔の空軍基地（今のトピーカの空港）")
S("m", "think", "学生新聞は、\nその日のことをこう書いているわ。", KANSAN, label="カンザス大学の学生新聞（1998年8月28日）", lf="mincho")
S("m", "normal", "「市長が街をポケモンに明け渡すと、\n空からの攻撃が始まった」", KANSAN, big="空からの攻撃", bf="mincho", label="カンザス大学の学生新聞", lf="mincho")
S("z", "shock", "攻撃！？\n何が落ちてきたのだ？", FORBES, label="会場になった昔の空軍基地（今のトピーカの空港）")
S("m", "normal", "ピカチュウのぬいぐるみ、約750個。\nひとつずつ、小さなパラシュートがついていたの。", PLUSH, label="このとき落ちてきたピカチュウ",
  say="ピカチュウのぬいぐるみ、やくななひゃくごじゅっこ。ひとつずつ、小さなパラシュートがついていたの。")
S("m", "normal", "黄色い服を着たスカイダイバーも、\n10人ほど降りてきたわ。", SKYD, label="この日のスカイダイバー",
  say="黄色い服を着たスカイダイバーも、じゅうにんほど降りてきたわ。")
S("z", "happy", "ピカチュウが750匹、空から降ってきたのだ…。\nそれは見てみたかったのだ。", PLUSH, label="このとき落ちてきたピカチュウ",
  say="ピカチュウがななひゃくごじゅっぴき、空から降ってきたのだ…。それは見てみたかったのだ。")
S("m", "normal", "この日のことは、2023年に、海外のポケモンの記事\n「ジョウト・タイムズ」がまとめているの。", RUN, label="ぬいぐるみに走る子どもたち（The Johto Times より）")
S("m", "normal", "当時会場にいた人たちに、\nそれぞれの思い出を聞いているのよ。", RUN, label="ぬいぐるみに走る子どもたち（The Johto Times より）")
S("m", "normal", "それによると、落ちてきたぬいぐるみに\n子どもたちがいっせいに走ったそうよ。", RUN, label="ぬいぐるみに走る子どもたち（The Johto Times より）")
S("m", "normal", "子どもが取るためのものだったのに、大人も入ってきて、\n子どもを踏みつけてひったくっていたって。", RUN, label="ぬいぐるみに走る子どもたち（The Johto Times より）")
S("z", "shock", "大人が、\nなのだ！？", RUN, big="大人が奪い合い", bf="rampart")
S("m", "normal", "当時3歳だったシェインさんも、おじいさんに\n「取っておいで」と言われて、丘を駆け下りたの。", RUN, label="ぬいぐるみに走る子どもたち（The Johto Times より）")
S("m", "normal", "1個がゆっくり腕の中に落ちてきたけど、\n大きな子に取られてしまったそうよ。", PLUSH, label="このとき落ちてきたピカチュウ")
S("m", "normal", "泣いていたら、おじいさんが\nぬいぐるみを持ってきてくれたんですって。", PLUSH, label="このとき落ちてきたピカチュウ")
S("z", "think", "おじいさん、\nどこで見つけてきたのだ…。", PLUSH, label="このとき落ちてきたピカチュウ")
S("m", "happy", "それは、\n書いてないわ。", PLUSH, label="このとき落ちてきたピカチュウ")
S("m", "normal", "シェインさんは大人になってから、\nこの日に配られたTシャツを探したの。", FRAMED, label="シェインさんが探し出したこの日のTシャツ")
S("m", "normal", "おじいさんがよく着ていたもので、\nネットで呼びかけて見つけたそうよ。", FRAMED, label="シェインさんが探し出したこの日のTシャツ")
S("z", "think", "…いい話なのだ。", FRAMED, label="シェインさんが探し出したこの日のTシャツ")

# ---- 第二層 ----
T("第二層", "マスタートレーナー養成会場", "第二層　会場の中身", font="dot",
  x={"head": "アメリカ初のポケモンの会で\nアニメは日本語のまま流れた\n回はカスミとヒトデマン",
     "img": [STARYU], "bubble": "アメリカの子はわからないのだ", "who": "z",
     "post": "1998年、アメリカで最初のポケモンの会では、英語版の放送が始まる前のアニメが日本語のまま流れました。参加した人が覚えているのは、カスミとヒトデマンが出る回。ほかにも、マスタートレーナー見習いの名札がもらえる講習や、トランクでゲームが動く車がありました。"})
S("m", "normal", "会場では、この予定表の\n出し物が順番に行われたの。", SCHED, label="この日の予定表")
S("m", "normal", "そのひとつが、アニメの上映。英語版の放送が始まる前で、\n参加した人の話では、日本語のまま流れたそうよ。", SCHED, label="この日の予定表")
S("z", "surprise", "アメリカの子は、何を言ってるか\nわからないのだ。", SCHED, label="この日の予定表")
S("m", "normal", "覚えているのは、カスミと\nヒトデマンが出てくる回だって。", STARYU, label="ヒトデマン")
S("m", "normal", "子ども向けの踊りの時間もあったわ。\n予定表での名前は「ホーク・ポケモン」。", SCHED, label="この日の予定表")
S("m", "normal", "英語圏の子どもが輪になって踊る「ホーキー・ポーキー」に\nそっくりな名前ね。ポケモンの踊りを教わる時間だったそうよ。", SCHED, label="この日の予定表",
  ety=["Hokey Pokey（ホーキー・ポーキー）", "手や足を輪の中に入れたり出したりして回る、英語圏の子どもの踊り歌"])
S("m", "normal", "「モンスターに会おう」という講習もあって、\n出た人には、この名札が配られたの。", LANYARD, label="名札「マスタートレーナー見習い」")
S("m", "normal", "書いてあるのは「マスタートレーナー見習い」。\nもらったアリッサさんは、今も持っているんですって。", LANYARD, label="名札「マスタートレーナー見習い」")
S("z", "surprise", "25年も、\n取ってあるのだ。", LANYARD, label="名札「マスタートレーナー見習い」", say="にじゅうごねんも、取ってあるのだ。")
S("m", "normal", "グッズもたくさん配られたわ。これは、\n中にポケモンの人形が入った、はずむボール。", BALLS, label="会場で配られたはずむボール")
S("m", "normal", "当時6、7歳だったエミリオさんは、\n中のピカチュウを出したくて…", BALLS, label="会場で配られたはずむボール",
  say="当時、ろく、ななさいだったエミリオさんは、中のピカチュウを出したくて…")
S("m", "normal", "家でドライバーを使って、\nボールを割ったの。", BALLS, label="会場で配られたはずむボール")
S("m", "normal", "手を切って、\n病院に行ったそうよ。", BALLS, label="会場で配られたはずむボール")
S("z", "shock", "そこまでして、\n出したかったのだ…。", BALLS, label="会場で配られたはずむボール")
S("m", "normal", "会場の裏には、ピカチュウを描いた\nフォルクスワーゲン・ビートルが10台並んでいたわ。", BUGS, label="10台のピカチュウのビートル")
S("m", "normal", "当時のビートルは出たばかりの新型で、今のテスラくらい\n話題の車だったと、参加した人は話しているわ。", BUGS, label="10台のピカチュウのビートル")
S("m", "normal", "トランクの中にはブラウン管のテレビがあって、\n発売前の赤と青が動いていたの。", TRUNK, label="トランクのテレビ")
S("z", "surprise", "車のトランクで、\nゲームが動いてたのだ？", TRUNK, label="トランクのテレビ")
S("m", "normal", "そう。子どもたちは発売の1か月前に、\nそこで赤と青を遊べたのよ。", TRUNK, label="トランクのテレビ")
S("z", "think", "アメリカで最初に赤と青を遊んだのは、\n車のトランクの前の子たちなのだ。", RB_EN)

# ---- 第三層 ----
T("第三層", "アメリカ最初のポケモン交換", "第三層　最初の交換", font="maru",
  x={"head": "1998年、アメリカ最初のポケモンの会で\n配られたグッズの山と\nピカチュウのぬいぐるみが交換された",
     "img": [PIKA], "bubble": "それは損してないのだ？", "who": "z",
     "post": "1998年、アメリカで最初のポケモンの会で、テントを回って集めたグッズ（はずむボール、カード、小さな人形）の山と、年下の子のピカチュウのぬいぐるみが交換されました。交換した人は、あとで謝ったそうです。"})
S("m", "normal", "会場では、ポケモンの交換もあったの。", BALLS, label="会場で配られたはずむボール")
S("z", "surprise", "通信ケーブルなのだ？", GB, label="ゲームボーイ")
S("m", "happy", "いいえ、手渡しよ。", PLUSH, label="このとき落ちてきたピカチュウ")
S("m", "normal", "参加したカールさんは、友だちとテントを回って、\nただで配られていたグッズを集めていたの。", BALLS, label="会場で配られたはずむボール")
S("m", "normal", "はずむボールに、カードに、小さな人形。それを全部まとめて、", PLUSH, label="このとき落ちてきたピカチュウ")
S("m", "normal", "年下の子のピカチュウのぬいぐるみと交換してもらったの。", PLUSH, label="このとき落ちてきたピカチュウ")
S("z", "think", "…それ、年下の子は\n損してないのだ？", PLUSH, label="このとき落ちてきたピカチュウ")
S("m", "normal", "本人もそう思ったみたいで、\nあとでその子に謝ったそうよ。", PLUSH, label="このとき落ちてきたピカチュウ")
S("m", "normal", "通信ケーブルの交換の話もあるわ。\n名札のアリッサさんは、次の1999年…", LANYARD, label="名札「マスタートレーナー見習い」")
S("m", "normal", "任天堂がショッピングモールを回って開いた\nポケモンの催しに出かけたの。", LANYARD, label="名札「マスタートレーナー見習い」")
S("m", "normal", "そこで任天堂の人と通信して、\nミュウを1匹もらったの。", MEW, label="ミュウ")
S("z", "surprise", "ミュウ！\n配信でしかもらえないポケモンなのだ。", MEW, label="ミュウ")
S("m", "normal", "しかも、そのミュウの\nおやの名前は「Mario」。", MEW, label="ミュウ", big="おや　Mario", bf="dot", say="しかも、そのミュウの、おやの名前は、マリオ。")
S("z", "shock", "おやが、\nマリオなのだ！？", MEW, label="ミュウ")
S("m", "normal", "アリッサさんが、そもそもこの会に\n招待された理由も変わっていてね。", LETTER, label="アリッサさんに届いた招待状")
S("m", "normal", "お母さんが昔、アメリカのファミコンのカセットを入れる袋を、", LETTER, label="アリッサさんに届いた招待状")
S("m", "normal", "任天堂から直接取り寄せていたの。", LETTER, label="アリッサさんに届いた招待状")
S("m", "normal", "そのとき任天堂に名前と住所が残って、\n招待状が届いたんだろうって…", LETTER, label="アリッサさんに届いた招待状")
S("m", "normal", "アリッサさんは話しているわ。", LETTER, label="アリッサさんに届いた招待状")
S("z", "surprise", "袋を注文しただけで、\n招待されたのだ。", LETTER, label="アリッサさんに届いた招待状")
S("m", "normal", "会の前には、任天堂から\nビデオも届いていたそうよ。", VHS, label="アリッサさんに届いたビデオ")
S("m", "normal", "中には、サトシのママを本物の女優さんが演じる、\n実写の寸劇が入っていたの。", VHS, label="アリッサさんに届いたビデオ")
S("z", "think", "実写のサトシのママ、\n気になるのだ。", VHS, label="アリッサさんに届いたビデオ")
S("m", "think", "最後に、ちょっと怖い話。会の約24時間後、\n同じ飛行場にヘリコプターが墜落しているの。", FORBES, label="会場になった昔の空軍基地（今のトピーカの空港）")
S("m", "normal", "テントが立っていた場所から、180メートルほど。\n乗っていた操縦士と整備士の3人は、軽いけがですんだわ。", FORBES, label="会場になった昔の空軍基地（今のトピーカの空港）")
S("z", "shock", "1日ずれていたら、\n大変だったのだ…。", FORBES, label="会場になった昔の空軍基地（今のトピーカの空港）")

# ---- 第四層 ----
T("第四層", "トピーカという名前", "第四層　トピーカの名前", font="deco",
  x={"head": "アメリカで最初のポケモンの会の街\nトピーカの名前は\n先住民の言葉で「イモを掘るのにいい場所」",
     "img": [KANSA], "bubble": "ポケモンと関係ないのだ", "who": "z",
     "post": "1998年、アメリカで最初のポケモンの会が開かれたトピーカ。選ばれた理由は、アメリカのまんなかにあることと、市長が1日だけ名前を変えてくれることでした。トピーカは、先住民カンザ族の言葉で「イモを掘るのにいい場所」という意味です。"})
S("z", "think", "でも、どうしてトピーカだったのだ？\nもっと大きい街があるのだ。", KSUS, label="カンザス州")
S("m", "normal", "学生新聞によると、理由は2つ。\nアメリカのまんなかにあることと…", KSUS, label="カンザス州")
S("m", "normal", "市長が、1日だけ\n名前を変えてくれること。", TOPIKA)
S("z", "think", "トピーカとピカチュウ、\nたしかに似てるのだ。", TOPIKA)
S("m", "normal", "トピーカは、もともと、この土地に住んでいた\n先住民、カンザ族の言葉なの。", KANSA, label="カンザ族の首長", lf="deco")
S("z", "think", "どういう意味なのだ？", KANSA, label="カンザ族の首長", lf="deco")
S("m", "normal", "イモを掘るのに、\nいい場所。", DIG, big="イモを掘るのにいい場所", bf="deco",
  ety=["Topeka（トピーカ）", "カンザ族の言葉　イモを掘るのにいい場所"])
S("z", "surprise", "ポケモンと、\n何も関係ないのだ。", DIG)
S("m", "normal", "1855年に町をつくった人たちが、\n響きがいいからこの名前を選んだそうよ。", TOPEKA2, label="トピーカの町", lf="deco")
S("m", "normal", "響きで選ばれた名前が、140年あとに、\n響きでピカチュウとくっついたのね。", TOPIKA,
  say="響きで選ばれた名前が、ひゃくよんじゅうねんあとに、響きでピカチュウとくっついたのね。")

# ---- 第五層 ----
T("第五層", "2度目の改名", "第五層　2度目の改名", font="reggae",
  x={"head": "トピカチュウになったトピーカ市は\n2010年\n「Google」にもなった",
     "img": [TOPEKALOGO], "bubble": "選ばれなかったのだ", "who": "z",
     "post": "1998年にピカチュウにちなんで「トピカチュウ」になったトピーカ市は、2010年3月、Googleの速いネットを呼ぶために「Google」を名乗りました。4月1日、Googleはお返しにロゴを「Topeka」に変えました。それでも選ばれたのは、となりのカンザスシティでした。"})
S("m", "normal", "トピーカが名前を変えたのは、\nこれだけじゃないの。", TOPEKA)
S("m", "normal", "2010年、Googleが、とても速い\nインターネットの回線を…", GFKC, label="Googleの回線の宣伝（カンザスシティ）",
  say="にせんじゅうねん、グーグルが、とても速いインターネットの回線を…")
S("m", "normal", "試しに引く街を、\n全米から募集したの。", GFKC, label="Googleの回線の宣伝（カンザスシティ）")
S("m", "normal", "トピーカは選ばれたくて、3月の1か月だけ、\n市の名前を「Google」に変えたのよ。", BUNTEN, label="当時のビル・バンテン市長",
  say="トピーカは選ばれたくて、さんがつの、いっかげつだけ、市の名前を、グーグルに変えたのよ。")
S("z", "surprise", "今度は、\nポケモンじゃないのだ。", BUNTEN, label="当時のビル・バンテン市長")
S("m", "normal", "するとGoogleは、4月1日のエイプリルフールに、\n自分のロゴを「Topeka」に変えて応えたの。", TOPEKALOGO, label="2010年4月1日のGoogleのロゴ",
  say="するとグーグルは、しがつついたちのエイプリルフールに、自分のロゴを、トピーカに変えて応えたの。")
S("m", "normal", "でも、回線が引かれたのは、\nとなりのカンザスシティだったわ。", GFKC, label="Googleの回線の宣伝（カンザスシティ）")
S("z", "sad", "名前まで変えたのに、\n選ばれなかったのだ…。", GFKC, label="Googleの回線の宣伝（カンザスシティ）")

# ---- 最深層 ----
T("最深層", "3度目のトピカチュウ", "最深層　2018年のトピカチュウ", font="rampart",
  x={"head": "トピーカ市は2018年に\nもう一度「トピカチュウ」になった\n1回目から20年後",
     "img": [PIKABUI], "bubble": "またトピカチュウなのだ", "who": "z",
     "post": "1998年に1日だけ「トピカチュウ」になったアメリカのトピーカ市は、20年後の2018年10月27日、もう一度トピカチュウを名乗りました。スイッチの「ピカブイ」の発売前に任天堂が全米8か所で開いた試遊会のひとつでした。"})
S("m", "normal", "そして2018年。スイッチの「ピカブイ」が出る前に、\n任天堂は全米8か所で、発売前に遊べる会を開いたの。", PIKABUI, label="ピカブイ（2018年）",
  say="そして、2018年。スイッチの、ピカブイが出る前に、任天堂は、全米はっかしょで、発売前に遊べる会を開いたの。")
S("m", "normal", "トピーカもそのひとつ。当時の市長は、\n会の日の10月27日だけ…", MAYOR18, label="2018年のトピーカ")
S("m", "normal", "市の名前をトピカチュウにすると宣言したわ。", MAYOR18, label="2018年のトピーカ")
S("z", "surprise", "また、\nトピカチュウなのだ！", MAYOR18, label="2018年のトピーカ", big="3度目のトピカチュウ", bf="rampart")
S("m", "normal", "1998年にぬいぐるみを追いかけた子どもたちは、\nこのとき30歳くらい。", RUN, label="1998年、ぬいぐるみに走る子どもたち")
S("z", "think", "今度は自分の子どもを連れて、\n来た人もいたかもしれないのだ。", RUN, label="1998年、ぬいぐるみに走る子どもたち")

# ---- まとめ ----
S("m", "think", "今日の答え。アメリカで最初のポケモンの会は、\nゲームが出る1か月前のトピーカで開かれたの。", KANSAN, sec="まとめ", label="カンザス大学の学生新聞（1998年8月28日）", lf="mincho")
S("m", "normal", "空からピカチュウが降って、車のトランクでは、\n発売前の赤と青が動いていた。", TRUNK, label="トランクのテレビ")
S("z", "think", "トピーカ、\n一度行ってみたいのだ。", TOPEKA2, label="トピーカの町", lf="deco")
S("m", "normal", "あなたの街の名前にポケモンを入れるなら、\nどうなる？コメントで教えてね。", TOPIKA)

# ---- 英語名 ----
T("おまけ", "今日のポケモンの英語名", "今日のポケモンの英語名", font="hachi")
S("m", "happy", "今日のポケモンの英語名。1匹目は、\n会場に大きなかざりがあったゼニガメ。", SQUIRTD, label="会場のゼニガメのかざり", lf="hachi")
S("m", "normal", "スクワートル。「水をぴゅっと出す」スクワートと、\n「カメ」のタートルを合わせた名前よ。", SQUIRTLE, label="Squirtle（スクワートル）", lf="hachi",
  ety=["Squirtle（スクワートル）", "英語　squirt（水をぴゅっと出す）＋turtle（カメ）"])
S("m", "happy", "2匹目はディグダ。ディグレット。\n「掘る」ディグに、小さいものを表すレット。", DIGLETT, label="Diglett（ディグレット）", lf="hachi",
  ety=["Diglett（ディグレット）", "英語　dig（掘る）＋-let（小さいもの）"])
S("m", "normal", "今日出てきたポケモンの英語名は、\n英単語帳サイト「もんすぺ！」でも調べられるわ。", "site:", label="「もんすぺ！」で検索")
S("m", "happy", "もんすぺ！には、ポケモンの雑学のコラムもあるの。\n動画の続きみたいに読めるわよ。", "site:", label="「もんすぺ！」雑学コラムもあります")
S("z", "happy", "今日の採掘はここまでなのだ。\nチャンネル登録もよろしくなのだ。", "site:", label="「もんすぺ！」で検索")
L.append({"type": "ed"})

# 「日本」は読み上げが「ニッポン」になるので、say を「にほん」にする（「日本語」はそのまま）
import re as _re
for _l in L:
    _src = _l.get("say") or _l.get("t", "").replace("\n", "")
    if _re.search(r"日本(?!語)", _src) and _l.get("type") not in ("title", "ed"):
        _l["say"] = _re.sub(r"日本(?!語)", "にほん", _src)

script = {
    "no": 7,
    "title": "アメリカの州都が、ピカチュウに降伏した日。",
    "neta": "アメリカの市が1日だけトピカチュウに改名",
    "thumb": {"layout": "v2", "pre": "1998年、アメリカの州都が", "big": ["ピカチュウに", "降伏"], "hl": 1, "hl_color": "red",
              "fonts": ["potta", "mincho"], "pre_font": "maru", "pre_size": 66,
              "big_w": [1180, 820], "big_size": [230, 400], "big_y": 110, "big_gap": -10,
              "back": CAPITOL, "badge": "art:25", "chara": ["z", "shock"]},
    "lines": L,
}
here = os.path.dirname(os.path.abspath(__file__))
json.dump(script, open(os.path.join(here, "script.json"), "w"), ensure_ascii=False, indent=1)
n = sum(len(l.get("t", "").replace("\n", "")) for l in L)
print("行数", len(L), "字幕の字数", n)
