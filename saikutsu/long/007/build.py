import json, os
# 第007回 台本（トピーカ市：ピカチュウに名前をゆずった市が、次はGoogleにも名前を差し出した）
# 2026-11-17 プロデューサーの指示で作った回（定期の予約とは別。すぐ公開）
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
POTATO = "wiki:en:Potato^commons:Potato harvest - geograph.org.uk - 248459.jpg"
DIG = "commons:Potato harvest - geograph.org.uk - 248459.jpg^wiki:en:Potato"
REDBLUE = "wiki:en:Pokémon_Red_and_Blue^commons:PokemonRedBlueYellowBack.jpg"
GB = "commons:Game-Boy-FL.jpg^wiki:en:Game_Boy"
SKY = "wiki:en:Parachuting^wiki:en:Skydiving"
FORBES = "commons:Forbesafb-02242002.jpg^wiki:en:Topeka_Regional_Airport"
BEETLE = "commons:Voiture Pikachu avec Peluches.jpg"
GLOGO = "commons:Google logo (2010-2013).svg^wiki:en:Google"
FIBER = "commons:Optical fiber cable-01ASD.jpg^wiki:en:Optical_fiber"
BUNTEN = "commons:Topeka mayor bill bunten.jpg"
DULUTH = "commons:LakeSuperior from Duluth in Winter.jpg^wiki:en:Lake_Superior"
SHARK = "commons:Wonders of Wildlife Museum (shark tank).jpg"
TOPEKALOGO = "web:https://www.google.com/logos/2010/topeka-hp.gif"
SCHMIDT = "wiki:en:Eric_Schmidt"
GFKC = "commons:GoogleFiberKansasCity.JPG^wiki:en:Google_Fiber"
HALFWAY = "commons:Halfway-Oregon.jpg^commons:HalfwayOregonskyline.jpg"
TOPIKA = "row:" + TOPEKA.split("^")[0] + "|トピーカ;art:25|ピカチュウ"
MAYOR18 = "row:commons:Michelle De La Isla.jpg|デ・ラ・イスラ市長;commons:Gage Park Zoo Topeka-KS(2463602266).jpg|ゲージ公園の動物園"
ZOO = "commons:Gage Park Zoo Topeka-KS(2463602266).jpg"
PIKABUI = "wiki:en:Pokémon:_Let's_Go,_Pikachu!_and_Let's_Go,_Eevee!^commons:Nintendo-Pokemon-Lets-Go-Poke-Ball-Plus-Controller.jpg"
JYNX = "art:124"
DIGLETT = "art:50"
PIKA = "art:25"
LUJ = "table:あくまのキッス=相手を眠らせる技;ふぶき=相手を凍らせることもある大技;初代のこおり状態=ほうっておいても治らない"
EVENT = "table:日にち=1998年8月27日（木）;場所=トピーカの昔の空軍基地の飛行場;空から=スカイダイバー10人とぬいぐるみ;ぬいぐるみ=パラシュートつき 約750個"
FIBERT = "table:発表=2010年2月;中身=それまでの約100倍速いネットを引く;引く場所=手をあげた市から選ぶ;応募した市=1100以上"
RACE = "table:トピーカ=市の名前を「Google」に（3月の1か月）;ダルース=市長が真冬の湖に飛び込む;サラソタ=市長がサメの水槽に入る;ダルースの冗談の動画=最初の子どもを「Googleファイバー」と名づける"
PICK = "table:選ばれた街=カンザス州カンザスシティ;発表=2011年3月30日;トピーカから=東へ約100km"
HALFT = "table:新しい名前=Half.com（ハーフ・ドットコム）;期間=2000年の1年間;町がもらったもの=お金（報道で7万5000〜10万ドル）;小学校には=パソコン20台あまり"
ANS = "table:1998年=アメリカで最初のポケモンの会;2010年=Googleのロゴ1日分;2018年=ピカブイの試遊会;お金=もらった記録なし"
NAME = "row:" + KANSA.split("^")[0] + "|カンザ族の言葉>" + TOPEKA.split("^")[0] + "|1855年 町の名前に>art:25|1998年 トピカチュウ"

# ---- コールドオープン ----
S("m", "normal", "ずんだもん。アメリカには、ピカチュウに\n自分の名前を明け渡した市があるの。", TOPEKA, sec="ポケモン雑学採掘所")
S("z", "surprise", "明け渡したのだ？\n市の名前を？", TOPEKA)
S("m", "think", "しかも12年後、こんどは\nGoogleにも名前を差し出したのよ。", GLOGO,
  say="しかもじゅうにねんご、こんどは、グーグルにも名前を差し出したのよ。")
S("z", "shock", "名前が軽すぎるのだ！", GLOGO, big="名前が軽すぎる！", ans=True)
L.append({"type": "op", "w": "m", "t": "ポケモンの深い雑学を掘り出す、\nポケモン雑学採掘所。", "say": "ポケモンの深い雑学を掘り出す、ポケモン雑学採掘所。"})

# ---- 導入 ----
S("z", "happy", "めたん、見るのだ！\n坑道の奥から、お宝を掘り当てたのだ。", POTATO, sec="導入　坑道のジャガイモ", label="掘り当てたお宝")
S("m", "think", "それ、ジャガイモよね。\n誰かのお弁当じゃない？", POTATO, label="ジャガイモ")
S("z", "think", "ディグダの頭かと思って、\n3回くらい叩いちゃったのだ。", DIGLETT, label="ディグダ",
  say="ディグダの頭かと思って、さんかいくらい叩いちゃったのだ。")
S("m", "happy", "ディグダは、もっと\nつるっとしてるわよ。", DIGLETT, label="ディグダ", v="tsun")
S("m", "normal", "それより今日は、1998年の\nアメリカの話をしようと思ってたの。", REDBLUE, label="アメリカ版の赤と青")
S("z", "proud", "1998年なら、ボクのルージュラが\nいちばん強かった時代なのだ。", JYNX, label="ルージュラ", bgm="battle")
S("z", "proud", "あくまのキッスで眠らせて、\nふぶきで凍らせるのだ。", LUJ, label="初代のルージュラの戦い方")
S("m", "normal", "初代のこおりは、ほうっておいても\n治らなかったものね。", LUJ, label="初代のルージュラの戦い方")
S("m", "happy", "いまの対戦では、\nほとんど見かけないけど。", JYNX, label="ルージュラ", v="tsun")
S("z", "sad", "ルージュラの話はいいのだ。\nアメリカの話をするのだ。", JYNX)
S("m", "normal", "ポケモンがアメリカに上陸したとき、\nある市が、名前をピカチュウにゆずったの。", TOPEKA, label="トピーカ市")
S("m", "normal", "市の名前はトピーカ。アメリカのまんなか、\nカンザス州の州都よ。", KSUS, label="カンザス州", ety=["州都（しゅうと）", "州の政治の中心になる市。日本の県庁所在地のようなもの"])
S("z", "think", "トピーカ。\nピカは入ってるのだ。", TOPEKA, label="トピーカ市")
T("本日の採掘", "ピカチュウに名前をゆずった市は、何を手に入れた？")

# ---- 第一層 ----
T("第一層", "トピカチュウの日", "第一層　1998年のトピカチュウ",
  x={"head": "1998年、アメリカのトピーカ市は\n1日だけ名前を\n「トピカチュウ」に変えた",
     "img": [CAPITOL], "bubble": "ダジャレなのだ", "who": "z",
     "post": "1998年8月27日、アメリカのカンザス州トピーカ市は、1日だけ名前を「トピカチュウ」に変えました。アメリカで初めてのポケモンのお披露目会のためです。その日、空からは約750個のピカチュウのぬいぐるみが降りました。どうやって降らせたと思いますか？"})
S("m", "normal", "1998年8月27日。トピーカの市長が、\nこの日だけ市の名前を変えると宣言したの。", CAPITOL, label="トピーカのカンザス州議事堂")
S("m", "normal", "新しい名前は「トピカチュウ」。\nトピーカと、ピカチュウを混ぜたのね。", TOPIKA, big="トピカチュウ",
  ety=["ToPikachu（トピカチュウ）", "Topeka（トピーカ）＋Pikachu（ピカチュウ）"], ans=True)
S("z", "surprise", "ダジャレで、市の名前を\n変えちゃったのだ！？", TOPIKA)
S("m", "normal", "アメリカで赤と青が出たのは、\n1か月後の9月28日。", REDBLUE, label="アメリカ版の赤と青")
S("m", "normal", "その前に、アメリカで初めての\nポケモンのお披露目会が、トピーカで開かれたの。", EVENT, label="トピカチュウの日")
S("m", "think", "カンザス大学の学生新聞は、\nその日のことをこう書いているわ。", FORBES, label="会場になった昔の空軍基地")
S("m", "normal", "「市長が街をポケモンに明け渡すと、\n空からの攻撃が始まった」", FORBES, big="空からの攻撃", label="カンザス大学の学生新聞")
S("z", "shock", "攻撃なのだ！？\nポケモンが攻めてきたのだ？", FORBES)
S("m", "happy", "飛行機から、スカイダイバー10人と\nピカチュウのぬいぐるみが降ってきたの。", SKY, label="スカイダイバー", cap="写真は別の日のスカイダイビング",
  say="飛行機から、スカイダイバーじゅうにんと、ピカチュウのぬいぐるみが降ってきたの。")
S("m", "normal", "ぬいぐるみには小さなパラシュートつき。\n参加した人の記録では、約750個よ。", EVENT, label="トピカチュウの日",
  say="ぬいぐるみには小さなパラシュートつき。参加した人の記録では、やくななひゃくごじゅっこよ。")
S("z", "happy", "ピカチュウの雨なのだ。\n夢みたいなのだ。", PIKA)
S("m", "think", "子どもたちは、落ちてくるぬいぐるみを追いかけて、\n飛行場の原っぱを走り回ったそうよ。", FORBES, label="会場になった昔の空軍基地")
S("m", "think", "でも参加した人の思い出話では、数が足りなくて、\n大人が子どもから取っていたって。", PIKA)
S("z", "proud", "大人げないのだ。ボクなら子どもにゆずるのだ。\nボクは大人だから。", PIKA)
S("m", "normal", "会場には、ポケモンの絵の入った\nフォルクスワーゲンのビートルが10台。", BEETLE, label="ポケモン仕様の黄色いビートル", cap="写真は別の催しの同じ型の車",
  say="会場には、ポケモンの絵の入った、フォルクスワーゲンのビートルがじゅうだい。")
S("m", "normal", "車にはテレビとゲーム機が積んであって、\nこのあと全米の10の都市を回ったの。", BEETLE, label="ポケモン仕様の黄色いビートル", cap="写真は別の催しの同じ型の車",
  say="車にはテレビとゲーム機が積んであって、このあと、全米のじゅうの都市を回ったの。")
S("m", "normal", "子どもたちは、発売前の赤と青を、\n会場で先に遊べたのよ。", GB, label="ゲームボーイ")
S("z", "think", "でも、どうしてトピーカだったのだ？\nもっと大きい街があるのだ。", KSUS, label="カンザス州")
S("m", "normal", "理由のひとつは、アメリカのまんなかにあること。\nもうひとつは、市長が名前を変えてくれたことなの。", KSUS, label="カンザス州")
S("m", "normal", "市長は記者に、こう話しているわ。\n「今日だけよ。市長ができる楽しい仕事のひとつね」", CAPITOL, label="ジョーン・ワグノン市長の言葉")
S("z", "think", "名前を貸すのが、\n楽しい仕事なのだ…？", CAPITOL)
S("z", "happy", "じゃあ、ここも「ピカチュウ採掘所」にすれば、\n空からぬいぐるみが降ってくるのだ。", PIKA)
S("m", "happy", "ここは地下よ。\n降ってくるのは、天井の石だけ。", None, v="tsun")

# ---- 第二層 ----
T("第二層", "トピーカという名前の意味", "第二層　トピーカの名前",
  x={"head": "アメリカの州都トピーカの名前は\n先住民の言葉で\n「イモを掘るのにいい場所」",
     "img": [KANSA], "bubble": "掘る場所なのだ", "who": "z",
     "post": "ピカチュウにちなんで1日だけ「トピカチュウ」になったアメリカのトピーカ市。トピーカは、もともと先住民カンザ族の言葉で「イモを掘るのにいい場所」という意味です。1855年に町の名前に選ばれた理由は何だったと思いますか？"})
S("m", "think", "実はね、ピカが入っていたのは偶然。\nトピーカは、もともと先住民の言葉なの。", KANSA, label="カンザ族の首長")
S("m", "normal", "この土地に昔から住んでいたカンザ族。\nカンザス州の名前も、この人たちから来ているわ。", KANSA, label="1822年に描かれた肖像")
S("z", "think", "それで、トピーカは\nどういう意味なのだ？", KANSA)
S("m", "normal", "イモを掘るのに、いい場所。", DIG, big="イモを掘るのにいい場所",
  ety=["Topeka（トピーカ）", "カンザ族の言葉　イモを掘るのにいい場所"], ans=True)
S("z", "shock", "イモ！？\nボクのジャガイモと同じなのだ！", POTATO, label="坑道で掘ったジャガイモ")
S("m", "happy", "そうね。あなたが坑道でジャガイモを掘ったのも、\nトピーカの名前どおりってこと。", POTATO, label="坑道で掘ったジャガイモ")
S("z", "proud", "じゃあ、この坑道も\nトピーカなのだ。", POTATO)
S("m", "happy", "掘ってたのは、\n金のはずだけどね。", None, v="tsun")
S("m", "normal", "この言葉は1826年の記録では、町のそばを\n流れるカンザス川の名前だったの。", TOPEKA, label="カンザス川とトピーカの町")
S("m", "normal", "1855年、町をつくった人たちが\nそれを町の名前にした。選んだ理由が面白いの。", NAME, label="トピーカという名前の歩み")
S("m", "normal", "「新しくて、先住民の言葉から来ていて、\n響きがいいから」。", TOPEKA2, label="町をつくった人たちの言葉")
S("z", "think", "響きで、\n選んだのだ。", TOPEKA2)
S("m", "think", "響きで選ばれた名前が、140年あとに、\n響きでピカチュウに選ばれたのね。", NAME, label="トピーカという名前の歩み", ans="idea")
S("z", "surprise", "名前の響きに、\n2回選ばれた市なのだ。", NAME)
S("m", "normal", "でもね、トピーカが名前を変えたのは、\nピカチュウのときだけじゃないの。", TOPEKA)

# ---- 第三層 ----
T("第三層", "Google、カンザス州", "第三層　2010年のGoogle市",
  x={"head": "2010年、トピーカ市は\n1か月だけ名前を\n「Google」に変えた",
     "img": [TOPEKALOGO], "bubble": "次はGoogleなのだ", "who": "z",
     "post": "1998年にピカチュウにちなんで「トピカチュウ」になったトピーカ市は、2010年3月、こんどは「Google」を名乗りました。速いネットを引いてもらうためです。翌月、Googleはお返しにロゴを「Topeka」に変えました。最後に選ばれたのはどの街だと思いますか？"})
S("m", "normal", "2010年2月、Googleが、\nある計画を発表したの。", GLOGO,
  say="にせんじゅうねん、にがつ、グーグルが、ある計画を発表したの。")
S("m", "normal", "それまでの100倍くらい速いインターネットを、\n試しに、いくつかの街に引くという計画。", FIBER, label="光ファイバーのケーブル")
S("m", "normal", "どの街に引くかは、手をあげた市から選ぶ。\n応募した市は、全米で1100をこえたの。", FIBERT, label="Googleの計画",
  say="どの街に引くかは、手をあげた市から選ぶ。応募した市は、全米でせんひゃくをこえたの。")
S("z", "think", "1100の中から選ばれるのは、\nたいへんなのだ。", FIBERT, say="せんひゃくの中から選ばれるのは、たいへんなのだ。")
S("m", "think", "そこでトピーカの市長は、3月のあいだ、\n市の名前を「Google」に変えたの。", BUNTEN, label="ビル・バンテン市長",
  say="そこでトピーカの市長は、さんがつのあいだ、市の名前を、グーグルに変えたの。")
S("m", "normal", "名乗った名前は「Google、カンザス州。\n光ファイバーの首都」。", BUNTEN, label="ビル・バンテン市長",
  say="名乗った名前は、グーグル、カンザス州。光ファイバーの首都。")
S("z", "shock", "トピカチュウの次は、\nGoogleなのだ！？", BUNTEN, big="トピカチュウの次はGoogle",
  say="トピカチュウの次は、グーグルなのだ！？", ans=True)
S("z", "happy", "じゃあボクも今日から「Googleもん」なのだ。\nネットが速くなるのだ。", None,
  say="じゃあボクも今日から、グーグルもん、なのだ。ネットが速くなるのだ。")
S("m", "happy", "この坑道、電波が\n1本も入らないわよ。", None, v="tsun", say="この坑道、電波がいっぽんも入らないわよ。")
S("m", "normal", "必死だったのは、トピーカだけじゃないの。\nほかの市長たちも、すごかったのよ。", RACE, label="Googleを呼びたい市の争い")
S("m", "normal", "ミネソタ州ダルースの市長は、真冬のスペリオル湖に、\nTシャツと短パンで飛び込んだの。", DULUTH, label="冬のスペリオル湖（ダルース）",
  ety=["スペリオル湖", "北アメリカの五大湖で、いちばん大きい湖"],
  say="ミネソタ州ダルースの市長は、真冬のスペリオル湖に、ティーシャツと短パンで飛び込んだの。")
S("m", "normal", "湖から上がると、こう叫んだそうよ。\n「ほかの市長たちよ、欲しいなら湖に飛び込め！」", DULUTH, big="湖に飛び込め！", label="ダルース市長の言葉")
S("m", "normal", "フロリダ州サラソタの市長は、それに応えて、\nサメの泳ぐ水槽に入ったの。", SHARK, label="サメの泳ぐ水槽", cap="写真は別の水族館の水槽")
S("z", "shock", "市長が、\n命がけなのだ！", SHARK)
S("m", "think", "ダルースは、冗談の動画で、\nこんなことまで言っていたの。", RACE, label="Googleを呼びたい市の争い")
S("m", "normal", "「最初の男の子は『Googleファイバー』、\n女の子は『Googleットファイバー』と名づける」", RACE, label="ダルースの冗談の動画",
  say="最初の男の子は、グーグルファイバー、女の子は、グーグレットファイバーと名づける。")
S("z", "sad", "Googleもんは、\nもう古いのだ…。", None, v="hero", say="グーグルもんは、もう古いのだ。")
S("m", "normal", "そして2010年4月1日。\nGoogleが、思わぬ返事をしたの。", GLOGO,
  say="そして、にせんじゅうねん、しがつついたち。グーグルが、思わぬ返事をしたの。")
S("m", "normal", "Googleのトップページのロゴが、\nこうなったのよ。", TOPEKALOGO, label="2010年4月1日のロゴ",
  say="グーグルのトップページのロゴが、こうなったのよ。", ans=True)
S("z", "shock", "Googleが、トピーカに\nなったのだ！？", TOPEKALOGO, big="Googleがトピーカに", label="2010年4月1日のロゴ",
  say="グーグルが、トピーカになったのだ！？")
S("m", "normal", "エイプリルフールの冗談よ。\nトピーカがGoogleを名乗ったお返しね。", TOPEKALOGO, label="2010年4月1日のロゴ",
  say="エイプリルフールの冗談よ。トピーカがグーグルを名乗ったお返しね。")
S("z", "happy", "名前の交換なのだ。\n両思いなのだ！", TOPEKALOGO, v="amaama")
S("m", "think", "でも当時の社長のエリック・シュミットさんは、\nその日のブログにこう書いていたの。", SCHMIDT, label="エリック・シュミット")
S("m", "normal", "「この改名は、どの市を選ぶかには\nいっさい関係ありません」", SCHMIDT, label="エリック・シュミットの言葉")
S("z", "think", "…それ、わざわざ\n書く必要あるのだ？", SCHMIDT)
S("m", "normal", "2011年3月、Googleが選んだのは、\nカンザス州のカンザスシティ。", GFKC, label="選ばれたカンザスシティ",
  say="にせんじゅういちねん、さんがつ、グーグルが選んだのは、カンザス州のカンザスシティ。", ans=True)
S("m", "normal", "トピーカから東へ、\n100kmほどの街よ。", PICK, label="Googleが選んだ街", say="トピーカから東へ、ひゃっキロほどの街よ。")
S("z", "sad", "名前を差し出したのに、\nふられたのだ…。", PICK, v="namida")
S("m", "normal", "湖に飛び込んだダルースも、\nサメと泳いだサラソタも、選ばれなかったわ。", DULUTH)

# ---- 第四層 ----
T("第四層", "名前の値段", "第四層　名前を売った町",
  x={"head": "2000年、オレゴン州の町は\nお金とパソコンをもらって\n名前を「Half.com」に変えた",
     "img": [HALFWAY], "bubble": "売れてるのだ", "who": "z",
     "post": "2000年、人口350人ほどのオレゴン州ハーフウェイは、1年だけ名前を「Half.com」に変えました。中古品を売るサイトから、お金と学校のパソコン20台あまりをもらっています。ピカチュウやGoogleに名前を貸したトピーカは、いくらもらったと思いますか？"})
S("m", "think", "名前を変えて、ちゃんと\nお金をもらった町もあるの。", HALFWAY, label="オレゴン州ハーフウェイ")
S("m", "normal", "オレゴン州の、人口350人ほどの町ハーフウェイ。\n名前は「道のりの半分」という意味ね。", HALFWAY, label="オレゴン州ハーフウェイ",
  ety=["Halfway（ハーフウェイ）", "英語　道のりの半分"],
  say="オレゴン州の、人口さんびゃくごじゅうにんほどの町、ハーフウェイ。名前は、道のりの半分という意味ね。")
S("m", "normal", "2000年、中古の本やゲームを売るサイトが、\n町に名前を貸してほしいと頼んだの。", HALFT, label="ハーフ・ドットコムとの約束")
S("m", "normal", "1年だけ、町の名前を「ハーフ・ドットコム」に。\nかわりに、お金と、学校のパソコン20台あまり。", HALFT, label="ハーフ・ドットコムとの約束",
  say="いちねんだけ、町の名前を、ハーフドットコムに。かわりに、お金と、学校のパソコンにじゅうだいあまり。")
S("z", "surprise", "ちゃんと、\n名前が売れてるのだ！", HALFT, ans=True)
S("m", "normal", "トピーカのほうは、名前を貸して\nお金をもらった記録は、見つからなかったの。", ANS, label="トピーカが名前を変えて得たもの")
S("z", "think", "トピーカは、タダで\n名前を貸してたのだ。", ANS)
S("m", "happy", "タダどころか、Googleのときは\nこっちからお願いしてたのよ。", BUNTEN, label="ビル・バンテン市長",
  say="タダどころか、グーグルのときは、こっちからお願いしてたのよ。")
S("z", "sad", "名前を売るのが、\nヘタな市なのだ…。", TOPEKA)

# ---- 最深層 ----
T("最深層", "2度目のトピカチュウ", "最深層　2018年のトピカチュウ",
  x={"head": "トピーカ市は2018年に\nもう一度「トピカチュウ」になった\n1回目から20年後",
     "img": [PIKABUI], "bubble": "また、やったのだ", "who": "z",
     "post": "1998年に1日だけ「トピカチュウ」になったアメリカのトピーカ市は、20年後の2018年10月27日、もう一度トピカチュウを名乗りました。きっかけはスイッチの「ピカブイ」の試遊会。1998年にぬいぐるみを追いかけた子どもたちは、このとき何歳くらいだったと思いますか？"})
S("m", "normal", "そして2018年10月。トピーカの市長が、\n市の議会で、また宣言したの。", MAYOR18, label="2018年のトピーカ")
S("m", "normal", "「10月27日だけ、市の名前を\nトピカチュウにします」", MAYOR18, big="また、トピカチュウ", label="デ・ラ・イスラ市長の宣言")
S("z", "shock", "また、\nやったのだ！？", TOPIKA, ans=True)
S("m", "normal", "スイッチの「ピカブイ」が出る前に、任天堂が\n全米8か所で、試しに遊べる会を開いたの。", PIKABUI, label="ピカブイ（2018年）")
S("m", "normal", "トピーカの会場は、動物園の駐車場。\n20年前と同じ名前で迎えたのね。", ZOO, label="ゲージ公園の動物園", cap="写真は昔の動物園の入口")
S("z", "happy", "ピカブイは、初代の151匹が\n出てくるゲームなのだ。", PIKABUI, label="ピカブイ（2018年）",
  say="ピカブイは、初代の、ひゃくごじゅういっぴきが、出てくるゲームなのだ。")
S("z", "proud", "ボクのルージュラの時代が、\n帰ってきたのだ。", JYNX, label="ルージュラ")
S("m", "happy", "出てはくるわね。\n強いかどうかは、別の話だけど。", JYNX, v="tsun")
S("m", "think", "1998年にぬいぐるみを追いかけた子どもは、\nこのとき30歳くらいね。", PIKA, say="1998年にぬいぐるみを追いかけた子どもは、このとき、さんじゅっさいくらいね。")
S("z", "think", "じゃあ、子どもから取った大人たちは、\nもう、おじいちゃんかもしれないのだ。", PIKA)
S("m", "happy", "孫のぶんのぬいぐるみは、\n取らないであげてほしいわね。", PIKA)

# ---- まとめ ----
S("m", "think", "今日の答え。トピーカが名前を変えて\n手に入れたのは、お金じゃなかったの。", ANS, sec="まとめ", label="トピーカが名前を変えて得たもの")
S("m", "normal", "最初のポケモンの会と、Googleのロゴ1日分。\nそれと、28年たっても語られる名前ね。", ANS, label="トピーカが名前を変えて得たもの",
  say="最初のポケモンの会と、グーグルのロゴ、いちにちぶん。それと、にじゅうはちねんたっても語られる名前ね。")
S("z", "think", "でも、本当の名前は、\nずっと変わってないのだ。", TOPEKA)
S("m", "normal", "そう。どれも市長の宣言だけの、\n1日や1か月だけの名前だったから。", TOPEKA, say="そう。どれも市長の宣言だけの、いちにちや、いっかげつだけの名前だったから。")
S("m", "happy", "ところで、もしいま空から、\nピカチュウのぬいぐるみが降ってきたら？", PIKA)
S("z", "proud", "ここには子どもがいないから、\n全部ボクのなのだ。", PIKA)
S("m", "happy", "大人げないわね。", PIKA, v="tsun")
S("z", "proud", "決めたのだ。このジャガイモの名前は、\n今日から「トピーカ」なのだ。", POTATO, label="坑道で掘ったジャガイモ")
S("m", "happy", "イモを掘る場所の名前を、\nイモにつけてどうするのよ。", POTATO, v="tsun", ans="idea")
S("m", "normal", "あなたの住む街なら、どのポケモンと名前を混ぜる？\nコメントで教えてね。", TOPIKA)

# ---- 英語名 ----
T("おまけ", "今日のポケモンの英語名", "今日のポケモンの英語名")
S("m", "happy", "今日のポケモンの英語名。\n1匹目はルージュラ。", JYNX, label="Jynx（ジンクス）")
S("m", "normal", "ジンクス。英語で、縁起の悪いものや、\nまじないを意味する言葉から来た名前よ。", JYNX, label="Jynx（ジンクス）",
  ety=["Jynx（ジンクス）", "英語　jinx（縁起の悪いもの・まじない）"])
S("z", "sad", "ボクの推しに、\n縁起が悪いはひどいのだ。", JYNX)
S("m", "happy", "2匹目はディグダ。\nディグレット。", DIGLETT, label="Diglett（ディグレット）")
S("m", "normal", "英語の「掘る」ディグに、小さいものを表す\n「レット」をつけた名前よ。", DIGLETT, label="Diglett（ディグレット）",
  ety=["Diglett（ディグレット）", "英語　dig（掘る）＋-let（小さいもの）"])
S("z", "happy", "トピーカにぴったりの\nポケモンなのだ。", DIGLETT)
S("m", "normal", "今日出てきたポケモンの英語名は、\n英単語帳サイト「もんすぺ！」でも調べられるわ。", "site:", label="「もんすぺ！」で検索")
S("m", "happy", "もんすぺ！には、ポケモンの面白い雑学のコラムもあるの。\n動画の続きみたいに読めるわよ。", "site:", label="「もんすぺ！」雑学コラムもあります")
S("z", "happy", "今日の採掘はここまでなのだ。\nチャンネル登録もよろしくなのだ。", "site:", label="「もんすぺ！」で検索")
L.append({"type": "ed"})

script = {
    "no": 7,
    "title": "ピカチュウに名前を明け渡した市。次の相手はGoogleだった。",
    "neta": "アメリカの市が1日だけトピカチュウに改名",
    "thumb": {"layout": "v2", "pre": "ピカチュウの次は", "big": ["グーグルに", "改名"], "hl": 1, "hl_color": "red",
              "back": TOPEKA, "badge": TOPEKALOGO, "chara": ["z", "shock"]},
    "lines": L,
}
here = os.path.dirname(os.path.abspath(__file__))
json.dump(script, open(os.path.join(here, "script.json"), "w"), ensure_ascii=False, indent=1)
n = sum(len(l.get("t", "").replace("\n", "")) for l in L)
print("行数", len(L), "字幕の字数", n)
