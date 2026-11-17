import json, os
# 第007回 台本（アメリカの州都トピーカが、ピカチュウに降伏した日。アメリカで最初のポケモンの会）
# 2026-11-17 プロデューサーの指示で作った回。1回目の台本は「ポケモンの話になっていない（半分がGoogleと街の改名）」
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
DIGLETT = "art:50"
NEWS = "table:新聞=カンザス大学の学生新聞;日付=1998年8月28日;見出し=任天堂の侵略の標的になったトピーカ"
JP = "table:日本=1996年発売。ゲーム約800万本、カード4億枚以上;アメリカ=赤と青の発売は1998年9月28日。まだ誰も遊んでいない"
EVENT = "table:日にち=1998年8月27日（木）;場所=昔の空軍基地の飛行場;時間=昼11時から2時まで。雨でも決行;入場=無料"
DROP = "table:落ちてきたもの=ピカチュウのぬいぐるみ 約750個;つき方=1個ずつ小さなパラシュート;いっしょに=黄色い服のスカイダイバー 10人ほど"
ANIME = "table:流れたアニメ=日本語のまま。英語版の放送が始まる前;覚えている人の話=カスミとヒトデマンが出る回"
DANCE = "table:名前=Hoke Pokémon（ホーク・ポケモン）;中身=踊り。振り付けの記録は残っていない;そっくりな名前=英語圏の子どもの踊り歌 Hokey Pokey"
MASTER = "table:講習の名前=Meet the Monsters;もらえたもの=マスタートレーナーの名札;穴あけカード=ブースを回るたびに穴を開けてもらう"
GIFT = "table:おみやげ=ポケモン入りのはずむボール;ほかに=赤のソフト、Tシャツなど;ある子は=ボールを割って手を切った"
CARS = "table:車=ピカチュウの絵のフォルクスワーゲン・ビートル;トランク=中にブラウン管のテレビ。赤と青が動いていた;その後=何年も全米のイベントを回った"
WHY = "table:理由1=アメリカのまんなかにある;理由2=市長が1日だけ名前を変えてくれる"
GOOG = "table:2010年3月=トピーカが1か月だけ市の名前を「Google」に;ねらい=Googleの速いネットを引いてもらう;4月1日=Googleのロゴが「Topeka」に;結果=選ばれたのはカンザスシティ"
TRADE = "table:出したもの=テントを回って集めたおまけの山;もらったもの=年下の子のピカチュウのぬいぐるみ;交換した人=カールさんと友だちのアレックスさん;その後=あとで謝った"
MEWT = "table:1999年=モールを回るポケモンのツアー;交換=任天堂の人が通信でミュウを渡した;ミュウのおや=Mario"
INVITE = "table:招待の理由=母がカセットの袋を注文していた;届いたビデオ=サトシのママの実写の寸劇"
HELI = "table:いつ=会の約24時間後;どこ=同じ飛行場。テントから約180メートル;けが=操縦士と整備士の3人が軽いけが"
GRAND = "table:シェインくん=当時3歳。おじいさんと来ていた;落ちてきたピカチュウ=大きい子に取られた;泣いていたら=おじいさんがぬいぐるみを見つけてきた"
MEW = "art:151"
ANS = "table:1998年=アメリカで最初のポケモンの会;2010年=Googleにも名前を差し出す;2018年=20年ぶりに、またトピカチュウ"

# ---- コールドオープン ----
S("m", "normal", "1998年、アメリカの州都がひとつ、\nピカチュウに降伏したの。", CAPITOL, sec="ポケモン雑学採掘所", label="カンザス州の議事堂（トピーカ）", lf="mincho")
S("z", "surprise", "降伏！？\nピカチュウは、何を要求したのだ？", PIKA)
S("m", "normal", "市の名前を1日だけ、\n「トピカチュウ」にすること。", TOPIKA, big="トピカチュウ", bf="potta")
S("z", "think", "要求が、\nかわいすぎるのだ。", TOPIKA)
L.append({"type": "op", "w": "m", "t": "ポケモンの深い雑学を掘り出す、\nポケモン雑学採掘所。", "say": "ポケモンの深い雑学を掘り出す、ポケモン雑学採掘所。"})

# ---- 導入 ----
S("z", "think", "めたん、さっきから\n何を読んでるのだ？", NEWS, sec="導入　任天堂の侵略", label="1998年の学生新聞", lf="mincho")
S("m", "normal", "1998年のアメリカの大学新聞。見出しが\n「任天堂の侵略の標的になったトピーカ」。", NEWS, label="1998年の学生新聞", lf="mincho")
S("z", "surprise", "任天堂が、\nアメリカに攻め込んだのだ？", NEWS)
S("m", "normal", "ポケモンがアメリカに上陸した、\n最初の日の記事よ。", REDBLUE, label="アメリカ版の赤と青")
S("z", "proud", "1998年なら、ボクの時代なのだ。\n初代こそ至高なのだ。", REDBLUE, label="アメリカ版の赤と青")
S("m", "happy", "あなたが知ってるのは、\n日本の初代でしょ。", JP, label="1998年の日本とアメリカ", v="tsun", say="あなたが知ってるのは、にほんの初代でしょ。")
S("z", "think", "…アメリカの初代は、\n知らないのだ。", JP, label="1998年の日本とアメリカ")
S("m", "normal", "日本ではもうゲームが800万本売れてたけど、\nアメリカでは、まだ誰も遊んでいなかったの。", JP, label="1998年の日本とアメリカ",
  say="にほんではもう、ゲームがはっぴゃくまんぼん売れてたけど、アメリカでは、まだ誰も遊んでいなかったの。")
S("m", "normal", "そこに任天堂が、\nどうやって攻め込んだか。", NEWS, label="1998年の学生新聞", lf="mincho")
T("本日の採掘", "アメリカで最初のポケモンの会で、何が起きた？", font="mincho")

# ---- 第一層 ----
T("第一層", "州都、ピカチュウに降伏す", "第一層　州都の降伏", font="fude",
  x={"head": "1998年、アメリカの州都が\nピカチュウに降伏した\n（記事の言葉どおり）",
     "img": [CAPITOL], "bubble": "要求がかわいいのだ", "who": "z",
     "post": "1998年8月27日、アメリカのカンザス州の州都トピーカで、アメリカで初めてのポケモンの会が開かれました。市長は1日だけ市の名前を「トピカチュウ」にすると宣言し、学生新聞は「市長が街をポケモンに明け渡すと、空からの攻撃が始まった」と書きました。何が降ってきたと思いますか？"})
S("m", "normal", "1998年8月27日。カンザス州の州都トピーカで、\nアメリカ初のポケモンの会が開かれたの。", KSUS, label="カンザス州")
S("m", "normal", "市長は、この日だけ\n市の名前をトピカチュウにすると宣言したわ。", TOPIKA)
S("m", "normal", "記者には「今日だけよ。\n市長ができる楽しい仕事のひとつね」って。", CAPITOL, label="ジョーン・ワグノン市長の言葉", lf="mincho")
S("z", "think", "降伏した人の、\n顔じゃないのだ。", CAPITOL, big="降伏した人の顔じゃない", bf="magic")
S("m", "normal", "会場は、昔の空軍基地の飛行場。\n今はトピーカの空港になっているところよ。", EVENT, label="アメリカ初のポケモンの会")
S("m", "think", "新聞は、その日のことをこう書いているの。", FORBES, label="会場になった昔の空軍基地")
S("m", "normal", "「市長が街をポケモンに明け渡すと、\n空からの攻撃が始まった」", FORBES, big="空からの攻撃", bf="mincho", label="カンザス大学の学生新聞", lf="mincho")
S("z", "shock", "容赦ないのだ！\n何が落ちてきたのだ？", FORBES)
S("m", "normal", "ピカチュウのぬいぐるみ、約750個。\nひとつずつ、小さなパラシュートつき。", DROP, label="空から降ってきたもの",
  say="ピカチュウのぬいぐるみ、やくななひゃくごじゅっこ。ひとつずつ、小さなパラシュートつき。")
S("m", "normal", "黄色い服のスカイダイバーも、\n10人ほど飛び降りてきたわ。", SKY, label="スカイダイバー", cap="写真は別の日のスカイダイビング",
  say="黄色い服のスカイダイバーも、じゅうにんほど飛び降りてきたわ。")
S("z", "think", "それは攻撃じゃなくて、\n物資の投下なのだ。", PIKA, big="ただの物資投下", bf="magic")
S("m", "happy", "受け取る側は、\n戦場だったけどね。", PIKA)
S("m", "normal", "参加した人は、大人が子どもを踏みつけて、\nぬいぐるみを全部ひったくっていたって書いてるわ。", PIKA, label="参加した人の思い出")
S("z", "shock", "いちばんポケモンに降伏してるのは、\n大人なのだ。", PIKA, big="大人が降伏", bf="rampart", ans=True)
S("m", "normal", "3歳だったシェインくんも、おじいさんに\n「取っておいで」と言われて走ったけど…", GRAND, label="シェインくんの思い出")
S("m", "normal", "落ちてきたピカチュウは、\n大きい子に取られてしまったの。", GRAND, label="シェインくんの思い出")
S("z", "sad", "かわいそうなのだ…。", GRAND)
S("m", "normal", "泣いていたら、おじいさんが\nどこからかぬいぐるみを見つけてきてくれたそうよ。", PIKA, label="シェインくんの思い出")
S("z", "think", "その日いちばんのトレーナーは、\nおじいさんなのだ。", PIKA)

# ---- 第二層 ----
T("第二層", "マスタートレーナー養成会場", "第二層　会場の中身", font="dot",
  x={"head": "アメリカ初のポケモンの会で\nアニメは日本語のまま流れた\n回はカスミとヒトデマン",
     "img": [STARYU], "bubble": "吹き替えは邪道なのだ", "who": "z",
     "post": "1998年、アメリカで最初のポケモンの会では、英語版の放送が始まる前のアニメが日本語のまま流れました。参加した人が覚えているのは、カスミとヒトデマンが出る回。ほかにも、マスタートレーナーの講習や、トランクでゲームが動く車がありました。"})
S("m", "normal", "会場の中は、\nもっとちぐはぐだったの。", EVENT, label="アメリカ初のポケモンの会")
S("m", "normal", "まずアニメ。英語版の放送が始まる前だったから、\n日本語のまま流れていたそうよ。", ANIME, label="会場で流れたアニメ")
S("z", "proud", "正しいのだ。\n吹き替えは邪道なのだ。", PIKA, big="吹き替えは邪道", bf="magic")
S("m", "happy", "アメリカの子は、\n一言もわからないけどね。", ANIME, v="tsun")
S("m", "normal", "参加した人が覚えているのは、\nカスミとヒトデマンが出る回。", STARYU, label="ヒトデマン")
S("z", "think", "ヒトデマン？ピカチュウの会なのに、\n地味なのだ。", STARYU, label="ヒトデマン")
S("m", "normal", "地味じゃないわよ。進化したスターミーは、\n初代の対戦で最強クラスなんだから。", STARMIE, label="スターミー")
S("z", "proud", "…ヒトデマンは、\n最初から最強なのだ。", STARMIE, label="スターミー")
S("m", "happy", "手のひらを返すのが、\n速すぎるわね。", STARMIE, v="tsun")
S("m", "normal", "それから、踊り。\n名前は「ホーク・ポケモン」。", DANCE, label="会場の踊り", lf="dot")
S("m", "normal", "英語圏の子どもの定番の踊り歌、\n「ホーキー・ポーキー」にそっくりな名前ね。", DANCE, label="会場の踊り",
  ety=["Hokey Pokey（ホーキー・ポーキー）", "手や足を輪の中に入れたり出したりして回る、英語圏の子どもの踊り歌"])
S("z", "think", "どんな踊りだったのだ？", DANCE)
S("m", "normal", "振り付けは、\n記録に残ってないの。", DANCE, label="会場の踊り")
S("z", "happy", "じゃあボクが復元するのだ。右手を入れて、\n右手を出して、10まんボルト！", PIKA, big="10まんボルト！", bf="potta",
  say="じゃあボクが復元するのだ。右手を入れて、右手を出して、じゅうまんボルト！")
S("m", "happy", "それ、自分が\n感電してるじゃない。", PIKA, v="tsun")
S("m", "normal", "「マスタートレーナー」の講習もあったの。\n名札と、穴あけカードがもらえたそうよ。", MASTER, label="マスタートレーナーの講習", lf="dot")
S("z", "think", "ブースを回って、\n穴を開けてもらうだけなのだ？", MASTER, label="マスタートレーナーの講習", lf="dot")
S("m", "happy", "ジムバッジ8つより、\nずっと早いわね。", MASTER, label="マスタートレーナーの講習", lf="dot",
  say="ジムバッジやっつより、ずっと早いわね。")
S("z", "sad", "ボクがセキエイ高原まで\n歩いた日々は、何だったのだ…。", REDBLUE, v="hero")
S("m", "normal", "おみやげは、中に小さなピカチュウが入った、\nはずむボール。", GIFT, label="会場のおみやげ")
S("m", "normal", "中のピカチュウを出そうとして、\nボールを割って手を切った子もいたそうよ。", GIFT, label="会場のおみやげ")
S("z", "sad", "その子の気持ちは、\n痛いほどわかるのだ。", GIFT)
S("m", "normal", "赤のソフトやTシャツも配られたわ。\n大人用の大きなTシャツを、パジャマにした子もいたそうよ。", GIFT, label="会場のおみやげ")
S("z", "happy", "今なら、\nぴったりなのだ。", GIFT)
S("m", "normal", "車も来ていたわ。\nピカチュウの絵のフォルクスワーゲン・ビートル。", BEETLE, label="ポケモン仕様の黄色いビートル", cap="写真は別の催しの同じ型の車")
S("m", "normal", "トランクの中にブラウン管のテレビがあって、\n発売前の赤と青が動いていたの。", CARS, label="ピカチュウの車")
S("z", "happy", "トランクでポケモンができる車、\nほしいのだ。", BEETLE, label="ポケモン仕様の黄色いビートル", cap="写真は別の催しの同じ型の車")
S("m", "normal", "子どもたちは、発売の1か月前に、\nそのトランクで赤と青を遊べたのよ。", CARS, label="ピカチュウの車")
S("z", "think", "1か月早いのは、ずるいのだ。\nアメリカでいちばんの古参なのだ。", REDBLUE, label="アメリカ版の赤と青")

# ---- 第三層 ----
T("第三層", "アメリカ最初のポケモン交換", "第三層　最初の交換", font="maru",
  x={"head": "1998年、アメリカ最初のポケモンの会で\nがらくたの山と\nピカチュウのぬいぐるみが交換された",
     "img": [PIKA], "bubble": "コラッタ10匹なのだ", "who": "z",
     "post": "1998年、アメリカで最初のポケモンの会で、テントを回って集めたおまけの山と、年下の子のピカチュウのぬいぐるみが交換されました。交換した2人は、あとで謝ったそうです。"})
S("m", "normal", "会場では、アメリカで最初の\nポケモン交換もあったの。", TRADE, label="会場での交換")
S("z", "surprise", "通信ケーブルなのだ？\nゲームボーイを持ってきた子がいたのだ？", GB, label="ゲームボーイ")
S("m", "happy", "いいえ、手渡しよ。", TRADE, label="会場での交換")
S("m", "normal", "カールさんと友だちは、テントを回って集めたおまけの山を、\n年下の子のピカチュウのぬいぐるみと交換したの。", TRADE, label="会場での交換")
S("z", "think", "コラッタ10匹で、\nピカチュウをもらうようなものなのだ。", "art:19", label="コラッタ", big="コラッタ10匹", bf="reggae", say="コラッタじゅっぴきで、ピカチュウをもらうようなものなのだ。")
S("m", "normal", "本人たちも気がとがめたみたいで、\nあとで謝ったそうよ。", TRADE, label="会場での交換")
S("z", "proud", "正直者なのだ。ボクは昔、ニックネームを\n「ミュウ」にしたポッポを交換に出したことがあるのだ。", "art:16", label="ポッポ")
S("m", "happy", "最低ね。", "art:16", label="ポッポ", v="tsun")
S("m", "normal", "本物の通信交換の話もあるわ。この会に来ていたアリッサさんは、\n次の年、ショッピングモールを回るポケモンの催しで…", MEWT, label="1999年の夏")
S("m", "normal", "任天堂の人から、\n通信ケーブルでミュウをもらったの。", MEW, label="ミュウ")
S("z", "shock", "本物のミュウ！？\n古参でも、なかなか手に入らなかったのだ。", MEW, label="ミュウ")
S("m", "normal", "しかも、そのミュウの\nおやの名前は「Mario」。", MEW, label="ミュウ", big="おや　Mario", bf="dot", say="しかも、そのミュウの、おやの名前は、マリオ。")
S("z", "surprise", "マリオが捕まえたミュウなのだ！？\n配った人、遊び心がすぎるのだ。", MEW, label="ミュウ")
S("m", "normal", "アリッサさんが、そもそもこの会に\n招待された理由も変わっていてね。", INVITE, label="アリッサさんの招待状")
S("m", "normal", "お母さんが昔、任天堂から\nファミコンのカセットを入れる袋を取り寄せていたの。", INVITE, label="アリッサさんの招待状")
S("m", "normal", "それで、任天堂の名簿に\n名前がのっていたのね。", INVITE, label="アリッサさんの招待状")
S("z", "think", "袋を頼んだだけで、\n歴史の現場に呼ばれたのだ。", INVITE, label="アリッサさんの招待状")
S("m", "normal", "その前には、予告編のビデオも届いていたそうよ。\nサトシのママを女優さんが演じる、実写の寸劇入り。", INVITE, label="アリッサさんの招待状")
S("z", "surprise", "実写のハナコさん！？\nそれは見てみたいのだ。", INVITE, label="アリッサさんの招待状")
S("m", "think", "最後に、ちょっと怖い話。", FORBES, label="会場になった昔の空軍基地")
S("m", "normal", "会の約24時間後、同じ飛行場で\nヘリコプターが墜落しているの。", HELI, label="翌日の飛行場")
S("m", "normal", "テントから180メートルほどの場所。\n乗っていた3人は、軽いけがですんだわ。", HELI, label="翌日の飛行場")
S("z", "shock", "1日ずれていたら、ポケモンの上陸は\nどうなっていたのだ…。", HELI, label="翌日の飛行場")
S("m", "normal", "この話を集めた記事の人も、\n同じことを書いているわ。", HELI, label="翌日の飛行場")

# ---- 第四層 ----
T("第四層", "トピーカという名前", "第四層　トピーカの名前", font="deco",
  x={"head": "アメリカで最初のポケモンの会の街\nトピーカの名前は\n先住民の言葉で「イモを掘るのにいい場所」",
     "img": [KANSA], "bubble": "掘る場所なのだ", "who": "z",
     "post": "1998年、アメリカで最初のポケモンの会が開かれたトピーカ。選ばれた理由は、アメリカのまんなかにあることと、市長が1日だけ名前を変えてくれることでした。トピーカは、先住民カンザ族の言葉で「イモを掘るのにいい場所」という意味です。"})
S("z", "think", "でも、どうしてトピーカだったのだ？\nもっと大きい街があるのだ。", KSUS, label="カンザス州")
S("m", "normal", "新聞によると、理由は2つ。\nアメリカのまんなかにあることと…", WHY, label="トピーカが選ばれた理由")
S("m", "normal", "市長が、1日だけ\n名前を変えてくれること。", WHY, label="トピーカが選ばれた理由")
S("z", "think", "ダジャレに乗ってくれる市長が、\n決め手なのだ。", WHY, label="トピーカが選ばれた理由")
S("m", "normal", "トピーカは、もともと\n先住民カンザ族の言葉なの。", KANSA, label="カンザ族の首長", lf="deco")
S("z", "think", "どういう意味なのだ？", KANSA)
S("m", "normal", "イモを掘るのに、\nいい場所。", DIG, big="イモを掘るのにいい場所", bf="deco",
  ety=["Topeka（トピーカ）", "カンザ族の言葉　イモを掘るのにいい場所"], ans=True)
S("z", "happy", "掘る場所なのだ！\n採掘所の仲間なのだ。", DIG)
S("m", "normal", "1855年に町をつくった人たちは、\n響きがいいからこの名前を選んだそうよ。", TOPEKA2, label="トピーカの町", lf="deco")
S("z", "think", "響きで選んだ名前が、\n響きでピカチュウとくっついたのだ。", TOPIKA)

# ---- 第四層 ----
T("第五層", "降伏ぐせ", "第五層　2度目の降伏", font="reggae",
  x={"head": "ピカチュウに降伏したトピーカ市は\n2010年\nGoogleにも降伏した",
     "img": [TOPEKALOGO], "bubble": "降伏ぐせなのだ", "who": "z",
     "post": "1998年にピカチュウにちなんで「トピカチュウ」になったトピーカ市は、2010年3月、Googleの速いネットを呼ぶために「Google」を名乗りました。4月1日、Googleはお返しにロゴを「Topeka」に変えました。それでも選ばれたのは、となりのカンザスシティでした。"})
S("m", "normal", "でも、トピーカの降伏は\nこれで終わらないの。", TOPEKA)
S("m", "normal", "2010年、Googleが、速いネットを引く街を募集したとき、\nトピーカは1か月だけ市の名前を「Google」に変えたの。", BUNTEN, label="ビル・バンテン市長",
  say="にせんじゅうねん、グーグルが、速いネットを引く街を募集したとき、トピーカは、いっかげつだけ、市の名前を、グーグルに変えたの。")
S("z", "shock", "2度目の、\n降伏なのだ！", BUNTEN, big="2度目の降伏", bf="rampart", ans=True)
S("m", "normal", "するとGoogleは、4月1日に\nロゴを「Topeka」に変えて返したの。", TOPEKALOGO, label="2010年4月1日のロゴ",
  say="するとグーグルは、しがつついたちに、ロゴを、トピーカに変えて返したの。")
S("z", "surprise", "Googleまで、\n降伏したのだ！", TOPEKALOGO, label="2010年4月1日のロゴ", say="グーグルまで、降伏したのだ！")
S("m", "happy", "エイプリルフールの冗談よ。\nしかも選ばれたのは、となりのカンザスシティ。", GOOG, label="2010年のGoogleの件",
  say="エイプリルフールの冗談よ。しかも選ばれたのは、となりのカンザスシティ。")
S("z", "sad", "降伏し損なのだ…。", GOOG, v="namida")

# ---- 最深層 ----
T("最深層", "3度目のトピカチュウ", "最深層　2018年のトピカチュウ", font="rampart",
  x={"head": "トピーカ市は2018年に\nもう一度「トピカチュウ」になった\n1回目から20年後",
     "img": [PIKABUI], "bubble": "また降伏したのだ", "who": "z",
     "post": "1998年に1日だけ「トピカチュウ」になったアメリカのトピーカ市は、20年後の2018年10月27日、もう一度トピカチュウを名乗りました。スイッチの「ピカブイ」の発売前に任天堂が全米8か所で開いた試遊会のひとつでした。"})
S("m", "normal", "そして2018年。スイッチの「ピカブイ」の発売前に、\n任天堂が全米8か所で試遊会を開いたの。", PIKABUI, label="ピカブイ（2018年）",
  say="そして、2018年。スイッチの、ピカブイの発売前に、任天堂が、全米はっかしょで試遊会を開いたの。")
S("m", "normal", "トピーカの市長は、20年ぶりに宣言したわ。\n「10月27日だけ、トピカチュウにします」", MAYOR18, label="2018年のトピーカ")
S("z", "shock", "3度目の、\n降伏なのだ！", MAYOR18, big="3度目の降伏", bf="rampart", ans=True)
S("m", "normal", "1998年にぬいぐるみを追いかけた子どもは、\nこのとき30歳くらい。", PIKA)
S("z", "proud", "ぬいぐるみを取られた子どもが、\n大人になって取り返しに来たのだ。", PIKA)
S("m", "happy", "今度は、子どもを\n踏まないでほしいわね。", PIKA, v="tsun")

# ---- まとめ ----
S("m", "think", "今日の答え。トピーカは、アメリカで最初に\nポケモンに降伏した街。", ANS, sec="まとめ", label="トピーカの降伏の記録", lf="mincho")
S("m", "normal", "イモを掘るのにいい場所は、アメリカで最初に\nポケモンを掘り当てた場所になったの。", DIG, ans="idea")
S("z", "think", "それで20年たっても、\n同じ思い出話を繰り返してるのだ。", ANS, label="トピーカの降伏の記録", lf="mincho")
S("m", "happy", "あなたが初代の話を繰り返すのと、\n同じね。", REDBLUE, v="tsun")
S("z", "happy", "…トピーカとは、\n仲良くなれそうなのだ。", TOPIKA)
S("m", "normal", "あなたの街なら、どのポケモンに降伏する？\nコメントで教えてね。", TOPIKA)

# ---- 英語名 ----
T("おまけ", "今日のポケモンの英語名", "今日のポケモンの英語名", font="hachi")
S("m", "happy", "今日のポケモンの英語名。1匹目は、\n会場にかざりがあったというゼニガメ。", SQUIRTLE, label="Squirtle（スクワートル）", lf="hachi")
S("m", "normal", "スクワートル。「水をぴゅっと出す」スクワートと、\n「カメ」のタートルを合わせた名前よ。", SQUIRTLE, label="Squirtle（スクワートル）", lf="hachi",
  ety=["Squirtle（スクワートル）", "英語　squirt（水をぴゅっと出す）＋turtle（カメ）"])
S("z", "happy", "名前に、\n水鉄砲が入ってるのだ。", SQUIRTLE)
S("m", "happy", "2匹目はディグダ。ディグレット。\n「掘る」ディグに、小さいものを表すレット。", DIGLETT, label="Diglett（ディグレット）", lf="hachi",
  ety=["Diglett（ディグレット）", "英語　dig（掘る）＋-let（小さいもの）"])
S("z", "proud", "トピーカの公式ポケモンに\nするべきなのだ。", DIGLETT)
S("m", "normal", "今日出てきたポケモンの英語名は、\n英単語帳サイト「もんすぺ！」でも調べられるわ。", "site:", label="「もんすぺ！」で検索")
S("m", "happy", "もんすぺ！には、ポケモンの雑学のコラムもあるの。\n動画の続きみたいに読めるわよ。", "site:", label="「もんすぺ！」雑学コラムもあります")
S("z", "happy", "今日の採掘はここまでなのだ。\nチャンネル登録もよろしくなのだ。", "site:", label="「もんすぺ！」で検索")
L.append({"type": "ed"})

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
