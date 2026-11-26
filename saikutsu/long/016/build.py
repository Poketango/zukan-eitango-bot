import json, os
# 第016回 台本（山火事の5日後、ポケモン社は「次の世界大会はハワイ」と発表した。）
# 2026-11-27 定期作業で作成。ネタ帳「世界大会のハワイ開催発表が山火事と重なった」。
# 裏取り（2つ以上の情報源で照合したものだけを使う）：
#   発表：TechRadar（2023-08-14）、Pokécharms（2023-08-13）、SI.com、電ファミ（2023-08-14）、Dot Esports
#   寄付：Siliconera（2023-08-13）、Nintendo Wire（2023-08-15）、GlobalGiving、ポケモン社の英語の発表（gamespress 2023-08-14）
#   批判の返事：TechRadar（X の返事の引用）、LevelUp（2023-08-15）
#   山火事：wildfire.gov、ABC/AP、Maui Now（2023-08-12、2023-08-22、2024-06-24）、Spectrum News、HTA の資料（2023-09-08）
#   ラハイナ：米国立公園局、ブリタニカ。バニヤンツリー：CBS（2023-09-19）、NBC、Star-Advertiser
#   アローラ：TIME（2016-10-19）、Siliconera（Nintendo UK のインタビュー）
#   過去の大会：ANN（公式プレスリリース 2007）、Honolulu Advertiser（2007-08-12）、Star-Advertiser（2010）、Serebii、Bulbapedia、
#     公式の選手向け資料（2012）、ギネス世界記録（レイ・リッツォの3連覇）
#   2024年大会：公式メディアアラート（2024-04-08）、Civil Beat、Honolulu Star-Advertiser
# 1つの出典でしか確かめられなかったこと（発表映像のピカチュウの服、先住ハワイ人の投稿、賞金の総額、
#   日本の選手の人数、ホノルルとマウイの距離と飛行時間）は使っていない。謝罪や投稿の削除は、どの出典にもなかったので「しなかった」とは言い切らない。
L = []
def S(w, face, t, img=None, **kw):
    d = {"w": w, "face": face, "t": t}
    if img: d["img"] = img
    d.update(kw); L.append(d)
def T(sub, t, sec=None, **kw):
    L.append({"type": "title", "sub": sub, "t": t, **({"sec": sec} if sec else {}), **kw})

# 画像（コモンズのファイル名は 2026-11-27 に内蔵ブラウザで実在と中身を確かめた）
LAH_NIGHT = "commons:Lahaina fire - 8 august.jpg"                    # 2023-08-08、ワイレアから見たラハイナの火
LAH_CG = "commons:2023 Maui fires - Lahaina damage via Coast Guard.jpg"   # 夜の港と燃える町
LAH_CG2 = "commons:2023 Maui fires - Lahaina damage via Coast Guard 2.jpg"  # 焼けたあとの港と灯台
LAH_SF = "commons:Maui community of Lahaina burned by wildfire - 53119882503.jpg"  # 2023-08-15
LAH_TRUCK = "commons:Maui Fire Department truck along the street with the burned community of Lahaina in the background.jpg"
LAH_CAR = "commons:Car burned in Lahaina, Hawaii following wildfire - 53119394866.jpg"
GUARD = "commons:Hawaii Army National Guard fighting Maui wildfires, August 9, 2023.jpg"
SAT = "commons:Maui wildfires 2023.jpg"
FRONT = "commons:Front Street Lahaina at Sunset.jpg"
FRONT2 = "commons:Lahaina Front Street.jpg"
HARBOR = "commons:Lahaina Hawaii 2016 Harbor.jpg"
COURT = "commons:Maui-Lahaina-Courthouse-front.JPG"
BANYAN = "commons:Lahaina Banyan Tree.jpg"
BANYAN2 = "commons:Lahaina Banyan Tree (June 2019).jpg"
HCC = "commons:Hawaii Convention Center.jpg"
HCC_N = "commons:Aerial View of the Hawaii Convention Center at night (iau0919a).jpg"
WAIKIKI = "commons:Waikiki Skyline (7733357776).jpg"
HNL = "commons:Skyline of Honolulu Hawaii.JPG"
WAIKIKI_N = "commons:Waikiki Beach and Diamond Head at night.jpg"
WAIKOLOA = "commons:Hilton Waikoloa Village (53313376225).jpg"
WAIKOLOA2 = "commons:Hilton Waikoloa Village Resort (2008) 05.JPG"
PACIFICO = "commons:Pacifico-Yokohama-01.jpg"
PACIFICO2 = "commons:Pacifico Yokohama 2012.JPG"
WCS14 = "commons:Pokémon World Championships 2014.jpg"
WCS24 = "commons:Line to buy merchandise at Pokemon World Championships (54277323262).jpg"   # 2024-08-17 ホノルル
MAP_MAUI = "commons:Map of Hawaii highlighting Maui.svg^commons:Location map Maui.png"
MAP_OAHU = "commons:Map of Hawaii highlighting Oahu.svg^" + HNL
MAP_BIG = "commons:Map of Hawaii highlighting Hawaii County.svg^" + WAIKOLOA
RELIEF = "commons:Hawaiian Islands Full Relief Template.png"
GREEN = "commons:Josh Green Official Photo 2022 (cropped).jpg"
SM = "wiki:en:Pokémon Sun and Moon"
HGSS = "wiki:en:Pokémon HeartGold and SoulSilver"
TWO = "row:" + MAP_OAHU + "|オアフ島（大会）;" + MAP_MAUI + "|マウイ島（山火事）"

# ---- コールドオープン ----
S("m", "normal", "2023年8月13日、横浜。\nポケモンの世界大会が、最終日を迎えたの。", PACIFICO,
  sec="ポケモン雑学採掘場", label="パシフィコ横浜")
S("m", "normal", "閉会式で、次の年の開催地が発表されたわ。\nハワイの、ホノルルよ。", HNL, label="ホノルル（ハワイ州）")
S("z", "happy", "ハワイなのだ！？\n選手もファンも、大喜びなのだ。", WAIKIKI, label="ホノルルのワイキキ")
S("m", "sad", "ところが、発表の投稿には、\n「今は来ないで」という返事が並んだの。", LAH_SF, label="ラハイナ（2023年8月）",
  big="今は来ないで", bf="mincho", ans=True)
S("z", "shock", "来ないで！？\nハワイで、いったい何があったのだ？", LAH_SF, label="ラハイナ（2023年8月）")
L.append({"type": "op", "w": "m", "t": "ポケモンの深い雑学を掘り出す、\nポケモン雑学採掘場。",
          "say": "ポケモンの深い雑学を掘り出す、ポケモン雑学さいくつじょう。"})

# ---- 導入 ----
S("z", "sad", "今日の坑道は、蒸し暑いのだ。\n南の島の海で、泳ぎたいのだ。", WAIKIKI, sec="導入　南の島の世界大会", label="南の島の海")
S("m", "normal", "南の島といえば、ポケモンの世界大会は、\nハワイで何度も開かれているのよ。", WAIKOLOA2, label="ハワイ島のホテル")
S("z", "surprise", "世界大会がハワイで！？\nうらやましすぎるのだ。", WAIKOLOA, label="ハワイ島のホテル")
S("m", "normal", "そして2023年、4回目のハワイでの開催が\n決まった日に、あの返事が並んだの。", HNL, label="4回目のハワイ開催")
S("z", "think", "めでたい発表なのに、\nなんで来ないでなのだ？", HNL, label="4回目のハワイ開催")
T("本日の採掘", "ハワイでの世界大会は、なぜ「来ないで」と言われた？", font="mincho")

# ---- 第一層 ----
T("第一層", "南の島の世界大会", "第一層　ハワイの世界大会", font="mincho",
  x={"head": "ポケモンの世界大会は\nハワイ島のホテルで\n3回も開かれていた",
     "img": [WAIKOLOA2], "bubble": "3回もなのだ", "who": "z",
     "post": "ポケモンの世界大会は、2007年、2010年、2012年の3回、ハワイ島ワイコロアのホテルで開かれました。2010年のゲーム部門は、ハートゴールド・ソウルシルバーで、伝説のポケモンを2匹まで使えるルールでした。あなたはそのころ、何で遊んでいましたか？"})
S("m", "normal", "ポケモンの世界大会がはじめてハワイに\n来たのは、2007年の8月よ。", WAIKOLOA2, label="2007年の世界大会の会場")
S("m", "normal", "会場は、ハワイ島のワイコロアにある、\n海辺の大きなホテルだったの。", WAIKOLOA, label="ヒルトン・ワイコロア")
S("z", "think", "ハワイ島？\nハワイとは、違う島なのだ？", RELIEF, label="ハワイ州の島々")
S("m", "normal", "ハワイ州には、大きな島がいくつもあるの。\nいちばん大きい島の名前が、ハワイ島よ。", MAP_BIG, label="ハワイ島")
S("m", "normal", "このときは、カードゲームの大会で、\nおよそ30か国の選手が集まったわ。", WCS14, label="世界大会の会場（2014年）")
S("z", "happy", "南の島で世界一を決めるなんて、\nぜいたくな大会なのだ。", WAIKOLOA2, label="2007年の世界大会の会場")
S("z", "think", "カードの大会なのだ。\nゲームの対戦は、なかったのだ？", WCS14, label="世界大会の会場（2014年）")
S("m", "normal", "ゲームの部門の世界大会が始まったのは、\n2009年の、アメリカのサンディエゴからよ。", WCS14, label="ゲームの部門は2009年から")
S("m", "normal", "そして2010年、ゲームの大会も\nいっしょに、ハワイ島へ来たの。", WAIKOLOA2, label="2010年もハワイ島")
S("z", "happy", "2010年なら、ハートゴールドと\nソウルシルバーのころなのだ！", HGSS, label="ハートゴールド・ソウルシルバー",
  kana="ニセンジュ'ウネンナラ、ハアトゴ'オルドト/ソウルシ'ルバアノ/コ'ロナノダ")
S("m", "normal", "その年のルールは、カイオーガや\nグラードンを、2匹まで使えたのよ。", "row:art:382|カイオーガ;art:383|グラードン",
  label="2010年の世界大会のルール")
S("z", "happy", "伝説が2匹並ぶダブルバトル、\nボクも大好きだったのだ。", "row:art:382|カイオーガ;art:383|グラードン",
  label="2010年の世界大会のルール")
S("m", "normal", "このハワイで勝ったのが、アメリカの\nレイ・リッツォさん。10代前半の部門よ。", WAIKOLOA, label="2010年 シニア部門で優勝",
  say="このハワイで勝ったのが、アメリカの、レイ、リッツォさん。じゅうだい前半の部門よ。")
S("m", "normal", "2011年は、いちばん上の年齢の部門で優勝。\n2012年、またハワイ島で優勝したの。", WAIKOLOA2, label="3年続けて世界一", ans=True,
  say="2011年は、いちばんうえの年齢の部門で優勝。2012年、またハワイ島で優勝したの。")
S("m", "normal", "3年続けての世界一は、\nギネス世界記録にもなっているわ。", WAIKOLOA2, label="ギネス世界記録")
S("m", "normal", "2012年の決勝の相手は、ウルフ・グリックさん。\nのちの2016年に、自分も世界一になる選手よ。", WAIKOLOA2, label="2012年の決勝",
  say="2012年の決勝の相手は、ウルフ、グリックさん。のちの2016年に、自分も世界一になる選手よ。")
S("z", "surprise", "ハワイ島で、2回も\n優勝しているのだ。", WAIKOLOA, label="ハワイ島のホテル")
S("z", "think", "でも、なんで世界大会は、\nハワイばかりなのだ？", RELIEF, label="なぜハワイ？")
S("m", "normal", "それが、選んだ理由の公式の説明は、\n見つからなかったの。", RELIEF, label="なぜハワイ？")
S("m", "normal", "ただ、ポケモンにとってハワイが特別な\n場所になったのは、このあとよ。", WAIKIKI, label="ハワイとポケモン")

# ---- 第二層 ----
T("第二層", "アローラの元になった島", "第二層　アローラはハワイ", font="reggae",
  x={"head": "サン・ムーンのアローラは\n最初からずっと\nハワイが元だった",
     "img": ["art:10114"], "bubble": "首が長いのだ", "who": "z",
     "post": "2016年のポケモン サン・ムーンの舞台、アローラ地方。ディレクターの大森滋さんは、元にするのは最初からずっとハワイがいいと思っていた、と話しています。音楽にもハワイの伝統のリズムが使われました。アローラで、いちばん好きなポケモンは？"})
S("m", "normal", "2016年に出た、ポケットモンスター\nサン・ムーン。舞台は、アローラ地方よ。", SM, label="サン・ムーン（2016年）")
S("m", "normal", "ディレクターの大森滋さんは、\nアメリカの雑誌に、こう話しているわ。", SM, label="大森滋さんの言葉",
  say="ディレクターの、おおもりしげるさんは、アメリカの雑誌に、こう話しているわ。")
S("m", "normal", "「地方の元にするのは、最初からずっと、\nハワイがいいと思っていた」", WAIKIKI, label="TIME（2016年10月）", ans=True)
S("z", "surprise", "最初から、\nハワイに決めていたのだ。", WAIKIKI, label="TIME（2016年10月）")
S("m", "normal", "増田順一さんも、音楽に、\nハワイの伝統のリズムを入れたと話しているの。", "row:art:722|モクロー;art:725|ニャビー;art:728|アシマリ",
  label="アローラの最初の3匹")
S("m", "normal", "見なれたポケモンも、アローラでは、\n姿が変わったわね。", "row:art:10100|ライチュウ;art:10103|ロコン;art:10114|ナッシー",
  label="アローラのすがた")
S("z", "surprise", "ナッシーの首が、\nとんでもなく伸びているのだ！", "art:10114", label="アローラのナッシー")
S("m", "normal", "南の島の強い日差しで、首が伸びた。\n図鑑には、そう書かれているわ。", "art:10114", label="アローラのナッシー")
S("m", "normal", "ロコンは、南の島の雪山にすんで、\nこおりタイプになったの。", "art:10103", label="アローラのロコン")
S("z", "surprise", "ハワイに、\n雪山があるのだ？", "art:10103", label="アローラのロコン")
S("m", "normal", "ハワイ島の高い山には、\n冬になると、雪がつもるのよ。", MAP_BIG, label="ハワイ島の高い山")
S("z", "happy", "アローラの元になったハワイで\n世界大会をしたら、盛り上がるのだ。", HNL, label="ホノルル（オアフ島）")
S("m", "normal", "ポケモン社も、きっとそう考えたのね。\n話は、2023年8月の横浜に移るわ。", PACIFICO2, label="パシフィコ横浜")

# ---- 第三層 ----
T("第三層", "横浜の閉会式", "第三層　横浜の閉会式", font="potta",
  x={"head": "ポケモン世界大会の\n「次はハワイ」の発表は\n山火事のお見舞いとセットだった",
     "img": [PACIFICO2], "bubble": "同じ場でなのだ", "who": "z",
     "post": "2023年8月13日、横浜の世界大会の閉会式で、株式会社ポケモンの石原恒和社長が、次の開催地をホノルルと発表しました。同じ場で、ハワイの山火事の被害にあった人たちへのお見舞いも述べています。この発表、あなたはどう感じますか？"})
S("m", "normal", "2023年の世界大会は、8月11日から\n13日まで、パシフィコ横浜で開かれたの。", PACIFICO2, label="パシフィコ横浜")
S("m", "normal", "世界大会が日本で開かれたのは、\nこのときが初めてだったのよ。", PACIFICO2, label="日本で初めての世界大会")
S("z", "happy", "横浜で世界一が決まるなんて、\nボクも見に行きたかったのだ。", PACIFICO2, label="日本で初めての世界大会")
S("z", "think", "世界大会って、\nだれでも出られるのだ？", PACIFICO2, label="パシフィコ横浜")
S("m", "normal", "いいえ。世界の各地の大会で、成績を\n積んだ選手が招かれる大会よ。", WCS14, label="招かれた選手の大会")
S("m", "normal", "そして閉会式の最後には、次の年の\n開催地を発表するのが、毎年の流れなの。", PACIFICO, label="閉会式で次の開催地")
S("m", "normal", "前の年のロンドン大会の閉会式でも、\n横浜での開催が発表されたわ。", "commons:Entrance of the 2022 London Pokémon World Championships - August 2022.jpg",
  label="2022年のロンドン大会")
S("m", "normal", "最終日の閉会式で、社長の石原恒和さんが、\n次の開催地を発表したわ。", PACIFICO, label="閉会式（8月13日）",
  kana="サイシュ'ウビノ/ヘエカイ'シキデ、シャチョオノ'、イシハラ/ツネ'カズサンガ、ツギ'ノ/カイサイ'チオ/ハッピョオシタ'ワ")
S("m", "normal", "次は、ハワイのホノルル。\nアローラの元になった場所だ、と。", HNL, label="次はホノルル", ans=True)
S("z", "happy", "やっぱりハワイなのだ！\n4回目のハワイなのだ。", WAIKIKI, label="4回目のハワイ開催")
S("m", "normal", "ホノルルは、ハワイ島とは別の、\nオアフ島にある州の中心の町よ。", MAP_OAHU, label="オアフ島（ホノルル）")
S("m", "normal", "ただ、石原さんはこのとき、\nもう1つの話もしていたの。", PACIFICO, label="閉会式（8月13日）")
S("m", "sad", "ハワイの山火事で被害にあった人たちに、\n心からのお見舞いを伝えたのよ。", LAH_NIGHT, label="ハワイの山火事")
S("m", "normal", "そして、助けになるために、何ができるか\n考えている、と続けたわ。", LAH_NIGHT, label="ハワイの山火事")
S("z", "shock", "山火事なのだ？\nそんな大変なことが、起きていたのだ？", LAH_NIGHT, label="ハワイの山火事")

# ---- 第四層 ----
T("第四層", "王国の都が燃えた", "第四層　マウイ島の山火事", font="fude",
  x={"head": "ハワイ王国の都だった町ラハイナが\n2023年8月の山火事で焼け\n102人が亡くなった",
     "img": [LAH_CG2], "bubble": "言葉が出ないのだ", "who": "z",
     "post": "2023年8月8日、マウイ島の町ラハイナを山火事がおそい、102人が亡くなりました。アメリカの山火事で、この100年あまりで最悪の被害です。ラハイナは1820年から1845年まで、ハワイ王国の都でした。ポケモンの世界大会の閉会式は、その5日後でした。"})
S("m", "normal", "閉会式の5日前、8月8日のこと。\nハワイのマウイ島で、山火事が起きたの。", MAP_MAUI, label="マウイ島")
S("m", "normal", "火は強い風にあおられて、\n海辺の町、ラハイナに燃え広がったわ。", LAH_NIGHT, label="燃えるラハイナ（8月8日）")
S("m", "normal", "ラハイナは、1820年から1845年まで、\nハワイ王国の都だった町よ。", FRONT, label="火事の前のラハイナ",
  say="ラハイナは、1820年から1845年まで、ハワイ王国のみやこだった町よ。")
S("z", "surprise", "ハワイに、\n王国があったのだ？", FRONT2, label="火事の前のラハイナ")
S("m", "normal", "ええ。今はアメリカの州だけど、\nもとは、王さまが治める国だったの。", COURT, label="ラハイナの古い役所")
S("m", "normal", "1800年代には、クジラをとる船が\nたくさん集まる港町としても、栄えたわ。", HARBOR, label="ラハイナの港（2016年）")
S("z", "think", "歴史のある、\n古い港町だったのだ。", HARBOR, label="ラハイナの港（2016年）", say="歴史のある、古い、みなとまちだったのだ。")
S("m", "normal", "町の広場には、1873年に植えられた、\n大きなバニヤンツリーがあったわ。", BANYAN, label="ラハイナのバニヤンツリー")
S("z", "surprise", "これが1本の木なのだ！？\n森みたいに、広がっているのだ。", BANYAN, label="ラハイナのバニヤンツリー")
S("m", "sad", "火事で、その町の大部分が焼けたの。\n焼けた建物は、2200棟あまり。", LAH_SF, label="焼けたラハイナ", ans=True,
  kana="カ'ジデ、ソノ'/マチ'ノ/ダイブ'ブンガ/ヤケタ'ノ。ヤケタ'/タテ'モノワ、ニセンニヒャクトウア'マリ")
S("m", "sad", "焼けた広さは、およそ8.8平方キロ。\n東京ドームの、およそ190個分よ。", SAT, label="宇宙から見たマウイ島",
  kana="ヤケタ/ヒ'ロサワ、オヨソ/ハ'チテンハチ/ヘエホオキ'ロ。トオキョオド'オムノ、オヨソ/ヒャクキュウジュ'ッコブンヨ")
S("m", "sad", "亡くなった人は、102人。\n2024年の6月に、警察が確かめた数よ。", LAH_CG2, label="102人が亡くなった")
S("m", "sad", "アメリカの山火事で、この100年あまりで、\nいちばん多くの人が亡くなったの。", LAH_TRUCK, label="この100年あまりで最悪")
S("z", "sad", "そんなに多くの人が、\n亡くなってしまったのだ…。", LAH_TRUCK, label="この100年あまりで最悪", v="namida")
S("m", "sad", "閉会式の8月13日は、まだ行方のわからない\n人を、探している最中だったの。", GUARD, label="山火事と戦う州兵（8月9日）")

# ---- 第五層 ----
T("第五層", "来ないで、と、来てほしい", "第五層　来ないで、来てほしい", font="mincho",
  x={"head": "ポケモン世界大会の\nハワイ開催の発表に\n「今は来ないで」の返事",
     "img": [LAH_SF], "bubble": "どっちも本音なのだ", "who": "z",
     "post": "ハワイでの世界大会の発表には、「地元はまだ苦しんでいるから来ないで」という返事が並びました。一方、ハワイ州の知事は8月22日、西マウイ以外は安全だとして、来れば地元の経済を支えることになると呼びかけました。あなたなら、行きますか？"})
S("m", "normal", "山火事の5日後に、ポケモン社は、\n「次はハワイ」と発表したの。", HNL, label="山火事の5日後の発表")
S("m", "normal", "Xの公式の投稿にも、\n開催地の発表が載ったわ。", HNL, label="Xの公式の投稿")
S("z", "think", "ポケモン社は、山火事のことを\n知らなかったのだ？", LAH_SF, label="発表への返事")
S("m", "normal", "知っていたはずよ。閉会式で、\nお見舞いを伝えていたんだもの。", PACIFICO, label="閉会式でお見舞い")
S("m", "normal", "それでも、その発表のすぐ下に、\nこんな返事が並んだの。", LAH_SF, label="発表への返事")
S("m", "sad", "「よりによって、\n最悪の場所だ」", LAH_SF, label="発表への返事")
S("m", "sad", "「地元はまだ苦しんでいるから、\n来ないでほしい」", LAH_CAR, label="発表への返事")
S("m", "sad", "「別の島に変えることを、考えてほしい」", LAH_CAR, label="発表への返事")
S("z", "think", "でも、大会はホノルルなのだ。\nマウイ島とは、別の島なのだ。", TWO, label="オアフ島とマウイ島")
S("m", "normal", "そうね。オアフ島とマウイ島は、\n海をへだてた、別の島よ。", TWO, label="オアフ島とマウイ島")
S("m", "normal", "それでも同じハワイ州で、たくさんの人が\n悲しみの中にいた時期だったの。", LAH_CG2, label="同じハワイ州")
S("m", "normal", "それに、ハワイ州の観光局も、\n8月12日に、こう呼びかけていたわ。", LAH_TRUCK, label="ハワイ州の観光局")
S("m", "normal", "西マウイへの観光の旅は、\n強く控えてほしい、と。", LAH_TRUCK, label="西マウイへの旅は控えて")
S("z", "think", "州も、来ないでって\n言っていたのだ。", LAH_TRUCK, label="西マウイへの旅は控えて")
S("m", "normal", "ところが8月22日、ハワイ州の知事、\nジョシュ・グリーンさんは、こう話したの。", GREEN, label="ジョシュ・グリーン知事")
S("m", "normal", "西マウイのほかは安全。来てくれれば、\n地元の経済を支えることになる、と。", GREEN, label="ジョシュ・グリーン知事", ans=True)
S("z", "surprise", "今度は、\n来てほしいのだ！？", GREEN, label="ジョシュ・グリーン知事")
S("m", "normal", "9月8日には、観光局も、10月8日から\n西マウイの観光を再び開くと発表したわ。", HARBOR, label="10月8日に西マウイを再開")
S("m", "normal", "ただ、焼けたラハイナの町は、\n入れないままだったの。", LAH_CG2, label="ラハイナは閉じたまま")
S("m", "normal", "ハワイには、観光で暮らす人がとても多いの。\n来ないでも、来てほしいも、地元の声なのよ。", WAIKIKI, label="観光の島ハワイ")
S("z", "think", "どっちの気持ちも、\nわかるのだ…。", WAIKIKI, label="観光の島ハワイ")
S("m", "normal", "そしてポケモン社は、発表と同じ\n8月13日に、寄付も発表していたわ。", LAH_CG2, label="発表と同じ日に寄付")
S("m", "normal", "20万ドル、日本円で約2900万円を、\n山火事の被害を助ける基金に寄付したの。", LAH_CG2, label="20万ドルを寄付",
  kana="ニジュウマン'ドル、ニホンエンデ/ヤク/ニセンキュウヒャクマ'ンエンオ、ヤマ'カジノ/ヒガイオ/タスケ'ル/キ'キンニ/キフシタ'ノ")
S("m", "normal", "寄付先は、グローバルギビングという、\n寄付を集めて届けるアメリカの団体の基金よ。", LAH_CG2, label="ハワイの山火事の基金",
  say="寄付先は、グローバル、ギビングという、寄付を集めて届けるアメリカの団体の基金よ。")
S("m", "normal", "社員が寄付したら、会社が同じ額を\n上乗せする仕組みも作ったわ。", GUARD, label="社員の寄付に上乗せ")
S("m", "normal", "担当の副社長、コリン・パーマーさんは、\nこう話しているの。", GUARD, label="ポケモン社の言葉",
  say="担当の副社長、コリン、パーマーさんは、こう話しているの。")
S("m", "normal", "「いちばん大切なのは、子どもと家族、\nそして被害にあった地域を助けること」", LAH_CG2, label="ポケモン社の言葉")
S("z", "think", "すぐに、寄付も\n決めていたのだ。", LAH_CG2, label="ポケモン社の言葉")
S("z", "think", "それなら、発表を少し\n待つこともできたのだ？", HNL, label="発表を待てた？")
S("m", "normal", "どうして予定どおり発表したのか、\nポケモン社の説明は、見つからなかったわ。", HNL, label="発表を待てた？")
S("m", "normal", "発表は取り消されず、大会は、\nそのままホノルルで開かれることになったの。", HNL, label="開催地はそのまま")

# ---- 最深層 ----
T("最深層", "2024年8月、ホノルル", "最深層　2024年のホノルル", font="mincho",
  x={"head": "ハワイの山火事から1年\nホノルルのポケモン世界大会に\n50以上の国と地域から3000人",
     "img": [WCS24], "bubble": "すごい人なのだ", "who": "z",
     "post": "2024年8月16日から18日、ポケモンの世界大会がホノルルのハワイ・コンベンション・センターで開かれ、50を超える国と地域から3000人あまりの選手が集まりました。ハワイでの世界大会は4回目、州都ホノルルでは初めてでした。行ってみたいですか？"})
S("m", "normal", "2024年4月、会場と日付が発表されたわ。\nハワイ・コンベンション・センターよ。", HCC, label="ホノルルの会場",
  say="2024年4月、会場と日付が発表されたわ。ハワイ、コンベンションセンターよ。")
S("m", "normal", "そして8月16日から18日まで、\n世界大会が、ホノルルで開かれたの。", HCC_N, label="2024年8月16〜18日")
S("m", "normal", "選手は、3000人あまり。\n50を超える国と地域から、集まったわ。", WCS24, label="ホノルルの会場（2024年）",
  kana="セ'ンシュワ、サンゼンニンア'マリ。ゴジュウオ/コエル'/クニト'/チ'イキカラ、アツマ'ッタワ")
S("z", "happy", "すごい人なのだ！\nグッズの列が、ずっと続いているのだ。", WCS24, label="グッズの列（2024年8月）")
S("m", "normal", "地元の新聞によると、大会に来た人が使う\nお金は、5700万ドルあまりと見積もられたの。", WAIKIKI_N, label="5700万ドルあまり",
  kana="ジモトノ/シ'ンブンニ/ヨ'ルト、タイカイニ/キ'タ/ヒトガ/ツカウ/オカネワ、ゴセンナナヒャクマンドルアマリト/ミツモラレタ'ノ")
S("m", "normal", "日本円にすると、80億円あまり。\n観光の島には、大きなお金よ。", WAIKIKI_N, label="80億円あまり",
  kana="ニホンエンニ'/スルト'、ハチジュウオクエンア'マリ。カンコオノ'/シマ'ニワ、オ'オキナ/オカネヨ'")
S("z", "think", "それだけのお金が、\nハワイの町に落ちるのだ。", WAIKIKI_N, label="80億円あまり")
S("m", "normal", "知事の、来てくれれば地元を支える、\nという言葉は、こういうことでもあるのね。", GREEN, label="ジョシュ・グリーン知事")
S("m", "normal", "ハワイ島で3回開かれた、ハワイの大会。\n州の中心のホノルルでは、これが初めてよ。", HCC, label="ホノルルでは初めて")
S("m", "normal", "その閉会式では、次の2025年がアナハイム、\n2026年がサンフランシスコと発表されたわ。", HCC_N, label="次の開催地の発表")
S("z", "think", "そのころ、マウイ島の\nラハイナは、どうなっていたのだ？", MAP_MAUI, label="マウイ島")
S("m", "normal", "焼けた町の片付けと、\n立て直しが続いていたわ。", LAH_CG2, label="ラハイナのその後")
S("m", "normal", "そして、あの広場のバニヤンツリー。\n火事のあと、新しい葉を出したの。", BANYAN2, label="火事の前の姿（2019年）", ans=True)
S("m", "normal", "2023年の9月に、州の役所が、\nその新しい葉の映像を公開したわ。", BANYAN2, label="火事の前の姿（2019年）")
S("z", "happy", "あの木は、\nまだ生きていたのだ…！", BANYAN2, label="火事の前の姿（2019年）")
S("m", "normal", "150年、町の広場に立ってきた木よ。\n幹は焼けても、根は生きていたの。", BANYAN, label="150年の木")

# ---- まとめ ----
S("m", "think", "今日の答え。ハワイ開催を発表したのは、\nマウイ島が燃えた、5日後だったから。", LAH_NIGHT, label="山火事の5日後の発表", sec="まとめ")
S("m", "normal", "アローラの元だから選んだ、ハワイ。\nその同じハワイで、町が焼けたばかりだったの。", "art:10114", label="アローラの元のハワイ")
S("z", "think", "来ないでも、来てほしいも、\nどっちも、ハワイの人の本当の声なのだ。", WAIKIKI, label="ハワイの人の声")
S("m", "normal", "あなたなら、発表の時期を、\nずらしたほうがよかったと思う？", HNL, label="あなたならどうする？")
S("z", "happy", "今日の採掘はここまでなのだ。\nチャンネル登録も、よろしくなのだ。", WAIKIKI, label="ホノルル（ハワイ州）")
L.append({"type": "ed"})

script = {
    "no": 16,
    "title": "山火事の5日後、ポケモン社は「次の世界大会はハワイ」と発表した。",
    "neta": "世界大会のハワイ開催発表が山火事と重なった",
    "thumb": {"layout": "v2", "pre": "ポケモン世界大会の発表に", "big": ["今は", "来ないで"], "hl": 1, "hl_color": "red",
              "fonts": ["mincho", "mincho"], "pre_font": "maru", "pre_size": 60,
              "back": LAH_NIGHT, "photo": LAH_SF, "photo_label": "山火事のラハイナ", "chara": None, "big_w": 620,
              "big_size": [170, 230]},
    "lines": L,
}
here = os.path.dirname(os.path.abspath(__file__))
json.dump(script, open(os.path.join(here, "script.json"), "w"), ensure_ascii=False, indent=1)
n = sum(len(l.get("t", "").replace("\n", "")) for l in L)
print("行数", len(L), "字幕の字数", n)
