import json, os
# 第008回 台本（宇宙に67日いたピカチュウ。ESAとポケモンのコラボで、ぬいぐるみが国際宇宙ステーションへ。行きも帰りも無人の補給船だった）
# 2026-11-18 定期作業で作成。ネタ帳「ピカチュウが67日間宇宙にいた」ほか（スペースX・約1040周・宇宙服のピカチュウ・JAXAの新年中継）。
# 裏取り：ESAの発表（2026-09-18）、Space.com、collectSPACE（2026-09-19）、TechEBlog、SoraNews24、カラパイア、NASAブログ（シグナスの捕獲 4/13）、
#   CRS-34（6/17着水）、ESAとCNESのアドノさんの紹介、ポケモンGO公式のお知らせ、AUTOMATON・Serebii（2021年のJAXA中継）。
# 1つの出典でしか確かめられなかったこと（クルー12の無重力の目印の中身、アドノさんの船外活動の記録など）は使っていない。
L = []
def S(w, face, t, img=None, **kw):
    d = {"w": w, "face": face, "t": t}
    if img: d["img"] = img
    d.update(kw); L.append(d)
def T(sub, t, sec=None, **kw):
    L.append({"type": "title", "sub": sub, "t": t, **({"sec": sec} if sec else {}), **kw})

# 画像
ESA_M = "https://media.esa.int/legacy/web/images/esa_multimedia/images/2026/09/"
CUPOLA_P = "web:" + ESA_M + "pikachu_in_the_cupola/27530034-1-eng-GB/400273/image-thumb__400273__fill_hero/Pikachu_in_the_Cupola.37aff486.webp^commons:Cupola ISS open shutters.jpg"
ADENOT_P = "web:" + ESA_M + "sophie_adenot_with_astronaut_pikachu_plush_at_the_european_astronaut_centre/27530081-1-eng-GB/400293/image-thumb__400293__fit_medium/Sophie_Adenot_with_Astronaut_Pikachu_plush_at_the_European_Astronaut_Centre.9611b27b.webp^commons:Official portrait of ESA astronaut Sophie Adenot wearing a spacesuit (jsc2025e073892 alt).jpg"
KEYART = "web:" + ESA_M + "pokemon_x_esa_collaboration_key_art/27530128-1-eng-GB/399685/image-thumb__399685__fit_medium/Pokemon_x_ESA_collaboration_key_art.4c898802.webp^art:25"
GOIMG = "web:https://lh3.googleusercontent.com/7CITEYsKb4CAwdYOln7q7h5K6U1cIVu2cnWRbDZtixs10PkfYfHzPn5Iz9wwbMFE3bosgBEiKnZlEZJZmGiyl-YqYRKHlIL8d7VAzR4DjA=e365-pa-nu-w1920^" + KEYART
ADENOT_EVA = "commons:ESA astronaut Sophie Adenot is tethered to the ISS during a spacewalk (iss075e0085867).jpg^commons:Astronauts Anil Menon and Sophie Adenot on Spacewalk.jpg"
ADENOT = "commons:Official portrait of ESA astronaut Sophie Adenot wearing a spacesuit (jsc2025e073892 alt).jpg^commons:ESA astronaut announcement Class of 2022 (52519418671).jpg"
CREW12 = "commons:NASA’s SpaceX Crew-12 Launch (NHQ202602130014).jpg^commons:NASA’s SpaceX Crew-12 Launch (NHQ20260213 admin 0004).jpg"
CREW12P = "commons:The four crew members representing NASA's SpaceX Crew-12 mission (jsc2026e004679).jpg^" + CREW12
NG24 = "commons:CYGNUS NG-24 Launches from Cape Canaveral Space Force Station (9617831).jpg^commons:CYGNUS NG-24 Launches from Cape Canaveral Space Force Station (9617832).jpg"
CYG_ARM = "commons:The Cygnus XL cargo spacecraft is in the grasp of the Canadarm2 robotic arm (iss074e0378294).jpg^commons:The Cygnus XL cargo craft is pictured in the grips of the Canadarm2 robotic arm (iss073e1196807).jpg"
CYG_BERTH = "commons:Northrop Grumman's Cygnus XL cargo spacecraft berthed to the Unity module (iss074e0609033).jpg^" + CYG_ARM
DRAGON = "commons:A SpaceX Dragon cargo spacecraft departs from the International Space Station (iss074e0723944).jpg^commons:SpaceX CRS-14 Dragon approaches the ISS (1).jpg"
SPLASH = "commons:CRS-4 Dragon ocean landing (16601701050).jpg^commons:CRS-5 Dragon ocean landing (16848173281).jpg"
ISS = "commons:STS-134 International Space Station after undocking.jpg^wiki:en:International_Space_Station"
SUNRISE = "commons:Sunrise from ISS 4.jpg^commons:Sunrise from ISS 5.jpg"
WATER = "commons:ISS-19 Crew members drink water from the Water Recovery System.jpg^commons:ISS Water Recovery System.svg"
MELFI = "commons:ISS-20 Robert Thirsk at the Minus Eighty Degree Laboratory Freezer.jpg"
ROOM = "commons:ISS-50 Crew quarters in the Harmony module.jpg^commons:ISS-27 American crew quarters.jpg"
TREMOR = "commons:Douglas Hurley, Robert Behnken and Tremor.png^commons:First Dinosaur in Space.png"
NOGUCHI = "commons:ISS-64 Michael Hopkins and Soichi Noguchi inside the Kibo lab.jpg^commons:ISS-22 Soichi Noguchi in the Kibo lab.jpg"
EAC = "commons:European Astronaut Centre exterior ESA19297332.jpeg^commons:ESA European Astronaut Centre.jpg"
HAIG = "commons:Claudie Haigneré 2017.jpg^commons:HaignereClaudie.jpg"
ESAHQ = "commons:ESA Headquarters in Paris.jpg"
CITE = "commons:Cité de l'espace Toulouse 1.jpg^commons:Mir replica at Cite de l'Espace 1.jpg"
PIKA = "art:25"
RAYQ = "art:384"
CLEF = "art:35"
ELGY = "art:605"
AR2021 = "row:" + NOGUCHI.split("^")[0] + "|野口聡一さん（きぼう）;art:25|ARのピカチュウ;art:384|ARのレックウザ"
SHIPS = "row:" + NG24.split("^")[0] + "|行き　補給船シグナス>" + CUPOLA_P.split("^")[0] + "|ISSで約2か月>" + SPLASH + "|帰り　補給船ドラゴン"
TIMELINE = SHIPS   # 2026-11-18 自作の表をやめて実物の画像に
ORBIT = SUNRISE   # 2026-11-18 自作の表をやめて実物の画像に
PROFILE = ADENOT   # 2026-11-18 自作の表をやめて実物の画像に
CYGTAB = CYG_ARM   # 2026-11-18 自作の表をやめて実物の画像に
DRATAB = DRAGON   # 2026-11-18 自作の表をやめて実物の画像に
TOUR = CUPOLA_P   # 2026-11-18 自作の表をやめて実物の画像に
ZGI2 = TREMOR   # 2026-11-18 自作の表をやめて実物の画像に
ZGI = TREMOR   # 2026-11-18 自作の表をやめて実物の画像に
EPS = ADENOT_P   # 2026-11-18 自作の表をやめて実物の画像に
COLLAB = KEYART   # 2026-11-18 自作の表をやめて実物の画像に
SPAWN = "row:art:25|ピカチュウ;art:35|ピッピ;art:81|コイル;art:605|リグレー"
ANS = SHIPS   # 2026-11-18 自作の表をやめて実物の画像に

# ---- コールドオープン ----
S("m", "normal", "2026年の春、ピカチュウが67日間、\n宇宙にいたの。", CUPOLA_P, sec="ポケモン雑学採掘場", label="国際宇宙ステーションのピカチュウ")
S("z", "surprise", "宇宙に！？\n宇宙飛行士といっしょになのだ？", CUPOLA_P, label="国際宇宙ステーションのピカチュウ")
S("m", "think", "それがね、行きも帰りも、\n人の乗らない荷物の船だったの。", CUPOLA_P, big="行きも帰りも貨物", bf="rampart")
S("z", "shock", "ピカチュウが、\n荷物あつかいなのだ！？", SHIPS)
L.append({"type": "op", "w": "m", "t": "ポケモンの深い雑学を掘り出す、\nポケモン雑学採掘場。", "say": "ポケモンの深い雑学を掘り出す、ポケモン雑学さいくつじょう。"})

# ---- 導入 ----
S("z", "think", "めたん、さっきから\nスマホで何を見てるのだ？", GOIMG, sec="導入　宇宙服のピカチュウ", label="ポケモンGOのお知らせ")
S("m", "normal", "ポケモンGOのお知らせ。ヨーロッパの博物館で、\n宇宙服のピカチュウが出てくるの。", GOIMG, label="ポケモンGOのお知らせ")
S("z", "happy", "宇宙服のピカチュウ、\nかわいいのだ。", GOIMG, label="ポケモンGOのお知らせ")
S("m", "normal", "ヨーロッパの宇宙機関、ESAとポケモンのコラボなの。\nESAは、ヨーロッパの国々が共同でつくった宇宙の役所ね。", ESAHQ, label="ESAの本部（パリ）",
  say="ヨーロッパの宇宙機関、イーエスエーとポケモンのコラボなの。イーエスエーは、ヨーロッパの国々が共同でつくった宇宙の役所ね。")
S("m", "normal", "このコラボで、ピカチュウのぬいぐるみが\n本当に宇宙へ行っているのよ。", ADENOT_P, label="宇宙へ行ったぬいぐるみ")
S("z", "surprise", "それで、さっきの\n荷物あつかいの話なのだ？", ADENOT_P, label="宇宙へ行ったぬいぐるみ")
S("m", "happy", "そう。その旅の中身を、\n順番に掘っていくわね。", ADENOT_P, label="宇宙へ行ったぬいぐるみ")
T("本日の採掘", "宇宙に67日いたピカチュウは、どうやって行って、どうやって帰ってきた？", font="mincho")

# ---- 第一層 ----
T("第一層", "ピカチュウ、67日の宇宙旅行", "第一層　67日の宇宙旅行", font="rampart",
  x={"head": "ピカチュウのぬいぐるみは\n2026年の春、宇宙に67日いた\n地球を約1040周", "img": [CUPOLA_P], "bubble": "1日に16回も朝なのだ", "who": "z",
     "post": "2026年4月11日から6月17日まで、ピカチュウのぬいぐるみが国際宇宙ステーションにいました。ヨーロッパの宇宙機関ESAとポケモンのコラボです。67日で地球を約1040周。ステーションでは1日に約16回も日の出があります。"})
S("m", "normal", "2026年9月18日、ESAが発表したの。\nピカチュウのぬいぐるみが、宇宙に67日いたって。", CUPOLA_P, label="ESAが公開した写真",
  say="にせんにじゅうろくねん、くがつじゅうはちにち、イーエスエーが発表したの。ピカチュウのぬいぐるみが、宇宙にろくじゅうななにちいたって。", kana="ニセンニジュウロ'クネン、ク'ガツ/ジュウハチ'ニチ、イイエスエ'エガ/ハッピョオ'/_シタ'ノ、_ピカ'チュウノ/ヌイグルミガ'、ウ'チュウニ/ロクジュウナナ'ニチ/イタ'ッテ")
S("m", "normal", "行き先は、国際宇宙ステーション。ISSね。\n地上から約400キロの高さを回っている、実験の基地よ。", ISS, label="国際宇宙ステーション（ISS）",
  say="行き先は、国際宇宙ステーション。アイエスエスね。地上から、やくよんひゃっキロの高さを回っている、実験の基地よ。", kana="イ_キサキワ'、コ_クサイウチュウ_ステ'エション、アイエス'エスネ、チジョオカラ'/ヤク/ヨンヒャ'ッキロノ/タカ'サオ/マワッテ'/イル'、ジッケンノ'/キ'チヨ")
S("m", "normal", "ISSは、約1時間半で地球を1周するの。\nだから67日で、約1040周。", ISS, label="国際宇宙ステーション（ISS）",
  say="アイエスエスは、やくいちじかんはんで地球をいっしゅうするの。だから、ろくじゅうななにちで、やくせんよんじゅっしゅう。", kana="アイエス'エスワ、ヤク/イチジ'カンハンデ/_チキュウオ'/イッシュウ'/スル'ノ、ダ'カラ、ロクジュウナナ'ニチデ、ヤク/センヨンジュ'ッシュウ")
S("m", "normal", "速さは、秒速約7.7キロ。\n東京から大阪まで、1分かからない速さよ。", ISS, label="国際宇宙ステーション（ISS）",
  kana="ハヤ'サワ、ビョオソク/ヤク/ナナテンナナ'キロ、トオキョオカラ'/オオサカマ'デ、イップ'ン/カカラナイ'/ハヤ'サヨ")
S("z", "surprise", "ピカチュウ、\nでんこうせっかより速いのだ。", ISS, label="国際宇宙ステーション（ISS）")
S("m", "normal", "日の出も、1日に約16回あるわ。", ISS, label="国際宇宙ステーション（ISS）",
  say="日の出も、いちにちに、やくじゅうろっかいあるわ。", kana="ヒノデモ'、イチ'ニチニ/ヤク/ジュウロ'ッカイ/ア'ルワ")
S("z", "surprise", "1日に16回も、\n朝が来るのだ…。", ISS, label="国際宇宙ステーション（ISS）", say="いちにちに、じゅうろっかいも、朝が来るのだ…。")
S("m", "normal", "写真も出ているの。ISSの窓、\n「キューポラ」に浮かぶピカチュウ。", CUPOLA_P, label="キューポラのピカチュウ")
S("m", "normal", "キューポラは、地球を見下ろすための\n7枚の窓が集まった部屋よ。", "commons:Cupola ISS open shutters.jpg^" + ISS, label="キューポラ（ISSの窓）")
S("z", "happy", "ピカチュウの後ろが、\nぜんぶ地球なのだ。", CUPOLA_P, label="キューポラのピカチュウ")
S("m", "normal", "このキューポラは、ヨーロッパのESAが用意した部屋で、\n2010年にISSにとりつけられたの。", "commons:Cupola ISS open shutters.jpg^" + ISS, label="キューポラ（ISSの窓）",
  kana="コノ'/キュウポラワ'、ヨオロ'ッパノ/イイエスエ'エガ/ヨオイ'/_シタ/ヘヤ'デ、ニセンジュ'ウネンニ/アイエス'エスニ/トリ_ツケラレ'タノ")
S("z", "think", "ESAとのコラボの写真を、\nESAの窓で撮ったのだ。", CUPOLA_P, label="キューポラのピカチュウ", kana="イイエスエ'エトノ/コ'ラボノ/シャシンオ'、イイエスエ'エノ/マ'ドデ/ト'ッタノダ")
S("m", "think", "ここで、日付をよく見てほしいの。\n宇宙にいたのは4月11日から6月17日。", CUPOLA_P, label="キューポラのピカチュウ", kana="ココデ'、ヒズケオ'/ヨ'ク/ミ'テホシイノ、ウ'チュウニ/イタ'/ノワ'、シ'ガツ/ジュウイチ'ニチカラ、ロ'クガツ/ジュウシチ'ニチ")
S("m", "normal", "でも発表は9月18日。帰ってきてから、\n3か月たってからなのよ。", CUPOLA_P, label="キューポラのピカチュウ", ans=True)
S("z", "surprise", "そのあいだ、\nだれも知らなかったのだ？", CUPOLA_P, label="キューポラのピカチュウ")
S("m", "normal", "8月にコラボだけは発表されていたけど、\nピカチュウの宇宙旅行には触れていなかったの。", KEYART, label="ESAとポケモンのコラボ")
S("m", "normal", "宇宙の記念品を追うアメリカのサイトは、\nこれを「秘密の旅」と書いているわ。", CUPOLA_P, label="キューポラのピカチュウ", big="秘密の旅", bf="mincho")

# ---- 第二層 ----
T("第二層", "いっしょに行った宇宙飛行士", "第二層　アドノさん", font="mincho",
  x={"head": "ピカチュウを宇宙へ連れて行ったのは\nフランスの宇宙飛行士アドノさん\nもとはヘリのテストパイロット", "img": [ADENOT_P], "bubble": "ピカチュウ、先に帰るのだ", "who": "z",
     "post": "宇宙へ行ったピカチュウのぬいぐるみの相棒は、ESAの宇宙飛行士ソフィー・アドノさん。もとはフランス空軍のヘリコプターのテストパイロットで、宇宙に237日いました。ピカチュウは、そのうち67日だけ。ピカチュウとアドノさん、どちらが先に地球に帰ったと思いますか？"})
S("m", "normal", "ピカチュウの相棒は、\nESAの宇宙飛行士、ソフィー・アドノさん。", ADENOT, label="ソフィー・アドノさん", say="ピカチュウの相棒は、イーエスエーの宇宙飛行士、ソフィー・アドノさん。")
S("m", "normal", "フランス空軍で、ヘリコプターの\nテストパイロットをしていた人よ。", PROFILE, label="ソフィー・アドノさん")
S("m", "normal", "2022年に、ESAの宇宙飛行士の募集に応募した\n2万2000人あまりの中から選ばれたの。", PROFILE, label="ソフィー・アドノさん",
  kana="ニセンニジュウニ'ネンニ、イイエスエ'エノ/ウチュウ_ヒコオ'_シノ/ボシュウニ'/オオボ'/_シタ、ニマンニセ'ンニンアマリノ/ナ'カカラ/エラバレ'タノ")
S("z", "shock", "2万人の中から、\nなのだ…。", PROFILE, label="ソフィー・アドノさん", kana="ニマ'ンニンノ/ナ'カカラ、ナノ'ダ")
S("m", "normal", "宇宙へ行ったフランスの女性は、\n1996年のクローディ・エニュレさん以来、2人目。", HAIG, label="クローディ・エニュレさん",
  say="宇宙へ行ったフランスの女性は、せんきゅうひゃくきゅうじゅうろくねんの、クローディ・エニュレさん以来、ふたりめ。", kana="ウ'チュウエ/イッタ'/フランスノ'/ジョセエワ'、センキュウヒャクキュウジュウロ'クネンノ、ク'ロオディ/エニュレ'サン/イ'ライ、_フタリメ'")
S("m", "normal", "出発前には、ドイツの宇宙飛行士センターで、\nこのぬいぐるみと写真を撮っているわ。", ADENOT_P, label="出発前のアドノさん（ドイツ・ケルン）")
S("z", "happy", "宇宙服、\nおそろいなのだ。", ADENOT_P, label="出発前のアドノさん（ドイツ・ケルン）")
S("m", "normal", "アドノさんが宇宙へ出発したのは、\n2月13日。スペースXの宇宙船、クルー12よ。", CREW12, label="クルー12の打ち上げ（2月13日）", kana="ア'ドノサンガ/ウ'チュウエ/シュッパツ'/_シタ'/ノワ'、ニ'ガツ/ジュウサン'ニチ、スペエスエ'ックスノ/ウチュウセン'、クル'ウ/ジュウニ'ヨ")
S("z", "think", "あれ？ピカチュウが宇宙に行ったのは、\n4月11日なのだ。", NG24, label="シグナスの打ち上げ（4月11日）", kana="アレ'？、_ピカ'チュウガ/ウ'チュウニ/イッタ'/ノワ'、シ'ガツ/ジュウイチ'ニチナノダ")
S("m", "happy", "そう。ピカチュウは、\nアドノさんとは別に行ったの。", TIMELINE, label="ピカチュウの行きと帰り")
S("z", "surprise", "いっしょに\n行ってないのだ！？", ADENOT, label="ソフィー・アドノさん")
S("m", "normal", "しかも、アドノさんが地球に帰ってきたのは\n10月8日。宇宙に237日いたの。", ADENOT, label="ソフィー・アドノさん",
  say="しかも、アドノさんが地球に帰ってきたのは、じゅうがつようか。宇宙に、にひゃくさんじゅうななにちいたの。", kana="_シカ'モ、ア'ドノサンガ/_チキュウニ'/カ'エッテ/キ'タ/ノワ'、ジュ'ウガツ/ヨ'オカ、ウ'チュウニ/ニヒャクサンジュウナナ'ニチ/イタ'ノ")
S("m", "normal", "ピカチュウが帰ってきたことが発表されたとき、\nアドノさんはまだ宇宙にいたのよ。", ADENOT_EVA, label="宇宙で船外活動をするアドノさん")
S("z", "think", "ピカチュウ、\n先に帰っちゃったのだ。", SPLASH, label="ドラゴンの着水")

# ---- 第三層 ----
T("第三層", "行きの船、シグナス", "第三層　行きの船", font="dot",
  x={"head": "宇宙へ行ったピカチュウの行きの船は\n人の乗らない補給船シグナス\nロボットアームでつかまえられた", "img": [CYG_ARM], "bubble": "UFOキャッチャーなのだ", "who": "z",
     "post": "ESAとポケモンのコラボで宇宙へ行ったピカチュウのぬいぐるみは、宇宙飛行士の船ではなく、人の乗らない補給船シグナスで運ばれました。シグナスはISSのそばで止まり、ロボットアームでつかまえられます。役目を終えると、ごみを積んで大気圏で燃えつきます。"})
S("m", "normal", "ピカチュウが乗ったのは、\n「シグナス」という補給船。", NG24, label="シグナスの打ち上げ")
S("m", "normal", "人は乗らずに、水や食べ物、実験の道具を\nISSに届ける、宇宙の宅配便よ。", CYGTAB, label="補給船シグナス")
S("z", "think", "宅配便で宇宙に行ったのだ。\nまさに荷物なのだ。", CYGTAB, label="補給船シグナス")
S("m", "normal", "4月11日にアメリカのフロリダから打ち上げて、\n2日後にISSのそばまで来たの。", NG24, label="シグナスの打ち上げ",
  say="しがつじゅういちにちに、アメリカのフロリダから打ち上げて、ふつかごに、アイエスエスのそばまで来たの。", kana="シ'ガツ/ジュウイチ'ニチニ、アメリカノ'/フロリダカラ'/ウチアゲテ'、_フツ'カゴニ、アイエス'エスノ/ソ'バマデ/キ'タノ")
S("m", "normal", "シグナスは自分ではくっつけないの。\nISSのロボットアームが、手でつかまえるのよ。", CYG_ARM, label="ロボットアームがシグナスをつかむ",
  say="シグナスは自分ではくっつけないの。アイエスエスのロボットアームが、手でつかまえるのよ。")
S("z", "surprise", "宇宙で、\nUFOキャッチャーなのだ。", CYG_ARM, label="ロボットアームがシグナスをつかむ")
S("m", "happy", "そうね。アームの長さは約17メートル。\nカナダが作ったから「カナダアーム2」っていうの。", CYG_ARM, label="カナダアーム2",
  say="そうね。アームの長さは、やくじゅうななメートル。カナダが作ったから、カナダアームツーっていうの。", kana="ソオネ'、ア'アムノ/ナガ'サワ、ヤク/ジュウナナメ'エトル、カ'ナダガ/_ツク'ッタカラ、カナダア'アム/ツ'ウッテ/イウ'ノ")
S("m", "normal", "つかまえたシグナスは、\nISSの入り口にとりつけて、荷物をおろすの。", CYG_BERTH, label="ISSにとりつけたシグナス")
S("m", "think", "ただ、シグナスには帰り道がないの。", CYG_BERTH, label="ISSにとりつけたシグナス")
S("m", "normal", "最後は、ISSのごみを積んで離れて、\n大気圏に入って燃えつきるのよ。", CYG_BERTH, label="ISSにとりつけたシグナス", big="燃えつきる船", bf="potta", ans=True)
S("z", "shock", "ピカチュウが乗ったままだったら、\n大変だったのだ！", CYGTAB, label="補給船シグナス")

# ---- 第四層 ----
T("第四層", "宇宙のピカチュウの暮らし", "第四層　ISSの中", font="maru",
  x={"head": "宇宙のピカチュウは\nISSの中を見学した\n水は汗や尿から作られる", "img": [WATER], "bubble": "それは飲みたくないのだ", "who": "z",
     "post": "国際宇宙ステーションに67日いたピカチュウのぬいぐるみは、宇宙飛行士のアドノさんの案内で中を見学しました。水の再生装置では、汗や尿まで水の約98%を飲み水にもどします。マイナス98度まで冷える実験の冷凍庫も見ました。"})
S("m", "normal", "ISSでのピカチュウは、アドノさんに案内されて、\n中を見学した動画も公開されているの。", CUPOLA_P, label="ISSのピカチュウ")
S("m", "normal", "まず、水の再生装置。ISSでは、\n水の約98%を、くり返し使うの。", WATER, label="水の再生装置",
  say="まず、水の再生装置。アイエスエスでは、水のやくきゅうじゅうはちパーセントを、くり返し使うの。", kana="マ'ズ、ミズノ'/サイセエソ'オチ、アイエス'エスデワ、ミズノ'/ヤク/キュウジュウハチパ'アセントオ、クリカエ'シ/ツカウ'ノ")
S("z", "think", "98%も、\nどこから集めてくるのだ？", WATER, label="水の再生装置", say="きゅうじゅうはちパーセントも、どこから集めてくるのだ？", kana="キュウジュウハチパ'アセントモ、ド'コカラ/アツメ'テ/ク'ルノダ？")
S("m", "normal", "空気中の湿気、汗、\nそれに尿もよ。", TOUR, label="ISSの見学コース", ans=True)
S("z", "shock", "尿！？それを、\nまた飲むのだ！？", WATER, label="水の再生装置")
S("m", "normal", "もちろん、機械できれいにしてからね。\nアメリカの飛行士は「きのうのコーヒーが、きょうのコーヒー」と言うそうよ。", WATER, label="水の再生装置")
S("m", "normal", "次は、実験の試料をしまう冷凍庫。\nマイナス98度まで冷やせるの。", MELFI, label="実験の冷凍庫",
  say="次は、実験の試料をしまう冷凍庫。マイナスきゅうじゅうはちどまで冷やせるの。", kana="ツギ'ワ、ジッケンノ'/シ'リョオオ/シマウ'/レエト'オコ、マイナ'ス/キュウジュウハ'チドマデ/ヒヤセ'ルノ")
S("m", "normal", "マイナス98度は、南極で記録された\nいちばん低い気温、マイナス89度より冷たいのよ。", MELFI, label="実験の冷凍庫",
  kana="マイナ'ス/キュウジュウハ'チドワ、ナ'ンキョクデ/キロク/サレ'タ、イチバン'/_ヒク'イ/キ'オン、マイナ'ス/ハチジュウキュ'ウドヨリ/_ツメタ'イノヨ")
S("z", "shock", "南極より寒い冷凍庫が、\n宇宙にあるのだ。", MELFI, label="実験の冷凍庫")
S("m", "normal", "最後は、飛行士ひとりずつの個室。\nアドノさんは「お昼寝かな」って声をかけていたわ。", ROOM, label="飛行士の個室")
S("z", "happy", "ぬいぐるみには、\nぴったりの部屋なのだ。", ROOM, label="飛行士の個室")
S("m", "normal", "動画の最後で、アドノさんはこう言っているの。\n「ピカチュウは、私より先に地球に帰るの」", ADENOT_P, label="アドノさんの言葉", lf="mincho", kana="ドオガノ'/サ'イゴデ、ア'ドノサンワ/コ'オ/イッテ'/イル'ノ、_ピカ'チュウワ、ワタシヨ'リ/サキニ'/_チキュウニ'/カエル'ノ")

# ---- 第五層 ----
T("第五層", "帰りの船、ドラゴン", "第五層　帰りの船", font="reggae",
  x={"head": "宇宙のピカチュウは\n帰りも人の乗らない補給船\n海にパラシュートで着水した", "img": [SPLASH], "bubble": "海に落ちたのだ！？", "who": "z",
     "post": "国際宇宙ステーションに行ったピカチュウのぬいぐるみは、6月17日、スペースXの補給船ドラゴンで地球に帰りました。ドラゴンはパラシュートで海に着水する、荷物を地球に持ち帰れる補給船です。いっしょに行った宇宙飛行士のアドノさんが帰ったのは、その約4か月後でした。"})
S("m", "normal", "帰りに乗ったのは、スペースXの補給船、\nドラゴン。これも人は乗らない荷物用の型よ。", DRAGON, label="補給船ドラゴン", cap="写真は別の便のドラゴン", kana="カエリ'ニ/ノッタ'/ノワ'、スペエスエ'ックスノ/ホキュウ'セン、ド'ラゴン、コレモ'/_ヒトワ'/ノラナイ'/ニモツ'ヨオノ/カタ'ヨ")
S("m", "normal", "ドラゴンは燃えつきないで、\n荷物を積んだまま地球に帰ってこられるの。", DRATAB, label="補給船ドラゴン")
S("m", "normal", "実験の試料みたいに、地上で調べたい物を\n持ち帰るための船なのね。", DRATAB, label="補給船ドラゴン")
S("z", "think", "ピカチュウは、\n実験の試料あつかいなのだ。", DRATAB, label="補給船ドラゴン")
S("m", "normal", "6月17日、ドラゴンはパラシュートを開いて、\nアメリカのカリフォルニアの沖に着水したの。", SPLASH, label="ドラゴンの着水", cap="写真は2014年の前の型のドラゴン",
  say="ろくがつじゅうななにち、ドラゴンはパラシュートを開いて、アメリカのカリフォルニアの沖に着水したの。", kana="ロ'クガツ/ジュウシチ'ニチ、ド'ラゴンワ/パラシュ'ウトオ/ヒラ'イテ、アメリカノ'/カリフォ'ルニアノ/オキニ'/チャ_クスイ'/_シタ'ノ")
S("z", "surprise", "海に落ちて、\n帰ってくるのだ！？", SPLASH, label="ドラゴンの着水", cap="写真は2014年の前の型のドラゴン")
S("m", "happy", "船で拾いに行くのよ。\nピカチュウ、ぬれなくてよかったわね。", SPLASH, label="ドラゴンの着水", cap="写真は2014年の前の型のドラゴン")
S("m", "think", "ここで、もう一度だけ数えてみるわね。", SHIPS)
S("m", "normal", "67日は、打ち上げの日から着水の日まで。\n行きと帰りの船の中の日も入っているの。", SHIPS, label="ピカチュウの行きと帰り",
  say="ろくじゅうななにちは、打ち上げの日から、着水の日まで。行きと帰りの、船の中の日も入っているの。", kana="ロクジュウナナ'ニチワ、ウチアゲ'ノ/ヒ'カラ、チャ_クスイノ'/ヒ'マデ、イ_キト'/カエリ'ノ、フ'ネノ/ナ'カノ/ヒ'モ/ハ'イッテ/イル'ノ")
S("m", "normal", "シグナスがつかまったのは4月13日、ドラゴンが離れたのは6月16日。\nISSの中にいたのは、だいたい2か月ね。", SHIPS, label="ピカチュウの行きと帰り",
  say="シグナスがつかまったのは、しがつじゅうさんにち。ドラゴンが離れたのは、ろくがつじゅうろくにち。アイエスエスの中にいたのは、だいたい、にかげつね。", kana="シ'グナスガ/_ツカマッタ'/ノワ'/シ'ガツ/ジュウサン'ニチ、ド'ラゴンガ/ハナレタ'/ノワ'/ロ'クガツ/ジュウロク'ニチ、アイエス'エスノ/ナ'カニ/イタ'/ノワ'、ダイタイ'/ニカ'ゲツネ")
S("z", "think", "行きも帰りも荷物の船で、\nほんとに宅配便の旅なのだ。", SHIPS, label="ピカチュウの行きと帰り")

# ---- 第六層 ----
T("第六層", "なぜ飛行士といっしょじゃない？", "第六層　無重力の目印", font="potta",
  x={"head": "宇宙船には\nぬいぐるみの「無重力の目印」が乗る\n2020年は恐竜のトレマー", "img": [TREMOR], "bubble": "浮いたら宇宙なのだ", "who": "z",
     "post": "人の乗る宇宙船には、小さなぬいぐるみが「無重力の目印」として乗ることがあります。打ち上げのあとでふわっと浮いたら、無重力に入ったしるし。2020年、スペースXの宇宙船で初めて人を運んだ飛行では、飛行士の息子たちが選んだ恐竜のぬいぐるみでした。"})
S("z", "think", "でも、ぬいぐるみなら、アドノさんが\n手で持っていけばよかったのだ。", CREW12P, label="クルー12の4人")
S("m", "normal", "人の乗る宇宙船にぬいぐるみを持ちこむのは、\nじつは決まった役目があるの。", ZGI, label="恐竜のトレマー（2020年）")
S("m", "normal", "「無重力の目印」。打ち上げのあと、\nぬいぐるみがふわっと浮いたら、無重力に入ったしるし。", CREW12P, label="クルー12の4人", big="無重力の目印", bf="maru")
S("m", "normal", "2020年、スペースXの宇宙船が初めて人を運んだときは、\n恐竜のぬいぐるみ「トレマー」が乗ったの。", TREMOR, label="恐竜のトレマー（2020年）", kana="ニセンニジュ'ウネン、スペエスエ'ックスノ/ウチュウセンガ'/ハジ'メテ/_ヒトオ'/ハコンダ'/ト'キワ、キョオリュウノ'/ヌイグルミ'、ト'レマアガ/ノッタ'ノ")
S("m", "normal", "選んだのは、\n乗っていた2人の飛行士の息子たちよ。", TREMOR, label="恐竜のトレマー（2020年）")
S("z", "happy", "子どもが選んだ恐竜が、\n宇宙の目印なのだ。いい話なのだ。", TREMOR, label="恐竜のトレマー（2020年）")
S("m", "normal", "その前の、人の乗らない試験飛行では地球のぬいぐるみ。\n同じ年の秋には、映画の宇宙人の赤ちゃんのぬいぐるみも乗ったわ。", ZGI2, label="恐竜のトレマー（2020年）")
S("z", "think", "ピカチュウも、\n目印になれそうなのだ。", ZGI2, label="恐竜のトレマー（2020年）")
S("m", "normal", "目印は、飛行士たちといっしょに乗って、\n打ち上げの中継にも映るものなの。", CREW12P, label="クルー12の4人")
S("m", "think", "ピカチュウは、その席ではなく、\nあとから荷物の船で届けられたというわけね。", SHIPS)
S("z", "think", "なるほど。荷物の船なら、\n打ち上げの中継にも映らないのだ。", SHIPS)
S("m", "normal", "そのおかげで、9月の発表まで\nだれにも知られずにすんだのね。", CUPOLA_P, label="キューポラのピカチュウ")

# ---- 最深層 ----
T("最深層", "小さくても大切な役目", "最深層　イプシロン", font="fude",
  x={"head": "宇宙飛行士アドノさんの\nミッションの名前はイプシロン\n数学で「とても小さな量」", "img": [ADENOT], "bubble": "ピカチュウも小さいのだ", "who": "z",
     "post": "ピカチュウのぬいぐるみを宇宙へ連れて行ったESAの宇宙飛行士アドノさんのミッションの名前は「εpsilon（イプシロン）」。数学でとても小さな量を表す文字で、大きな共同作業の中の、小さくても大切な役目という意味がこめられています。"})
S("m", "normal", "アドノさんのミッションには、\n名前がついているの。「イプシロン」。", EPS, label="ピカチュウとアドノさん", lf="mincho")
S("m", "normal", "ギリシャ文字のεのことで、\n数学ではとても小さな量を表す文字よ。", EPS, label="ピカチュウとアドノさん", lf="mincho",
  ety=["εpsilon（イプシロン）", "ギリシャ文字のε　数学では、とても小さな量"], kana="ギリシャ'モジノ/イ'プシロンノ/コト'デ、スウガクデワ'/トテモ'/チ'イサナ/リョ'オオ/アラワ'ス/モ'ジヨ")
S("m", "normal", "大きな共同作業の中の、\n小さくても大切な役目、という意味をこめたそうよ。", EPS, label="ピカチュウとアドノさん", lf="mincho", ans="idea", kana="オ'オキナ/キョオドオサ'ギョオノ/ナ'カノ、チイサ'_クテモ/タイセツナ'/ヤクメ'、トイウ'/イ'ミオ/コメ'タ/ソオヨ'")
S("z", "think", "小さくても大切な役目…。", ADENOT_P, label="アドノさんとピカチュウ")
S("m", "normal", "ピカチュウの役目は、ここから始まるの。\nヨーロッパの宇宙機関と博物館をめぐる展示よ。", COLLAB, label="ESAとポケモンのコラボ")
S("m", "normal", "9月19日のパリの本部から、ローマ、オランダ、\nドイツ、スペイン、イギリスのESAの施設を回ったの。", ESAHQ, label="ESAの本部（パリ）",
  kana="ク'ガツ/ジュウク'ニチノ/パ'リノ/ホンブカラ'、ロ'オマ、オ'ランダ、ド'イツ、スペ'イン、イギリスノ'/イイエスエ'エノ/_シ'セツオ/マワッタ'ノ")
S("m", "normal", "ポケモンGOでも、ヨーロッパの6つの博物館で、\n宇宙飛行士ピカチュウのレイドが2027年4月まで続くの。", GOIMG, label="宇宙飛行士ピカチュウ（ポケモンGO）",
  say="ポケモンGOでも、ヨーロッパのむっつの博物館で、宇宙飛行士ピカチュウのレイドが、にせんにじゅうななねんしがつまで続くの。", kana="ポケモンゴ'オデモ、ヨオロ'ッパノ/ム'ッツノ/ハクブツ'カンデ、ウチュウ_ヒコオ'_シ/ピカ'チュウノ/レ'イドガ、ニセンニジュウナナ'ネン/シ'ガツマデ/ツズク'ノ")
S("m", "normal", "フランスのトゥールーズにある、\n宇宙の博物館もそのひとつよ。", CITE, label="シテ・ド・レスパス（フランス・トゥールーズ）", kana="フランスノ'/トゥウル'ウズニ/ア'ル、ウ'チュウノ/ハクブツ'カンモ/ソノ'/_ヒト'ツヨ")
S("z", "happy", "フランスは、アドノさんの国なのだ。", CITE, label="シテ・ド・レスパス（フランス・トゥールーズ）")
S("m", "normal", "最初の1週間は、ピッピやコイル、\nリグレーのような宇宙っぽいポケモンも出ていたわ。", SPAWN, label="博物館のまわりに出たポケモン")
S("m", "think", "じつはピカチュウ、ISSに出るのは\n2回目なの。", AR2021)
S("m", "normal", "2021年の年越しに、JAXAが「きぼう」から中継をしたとき、\nARのピカチュウが野口聡一さんの横に現れたの。", AR2021, label="2021年の年越しの中継",
  say="にせんにじゅういちねんの年越しに、ジャクサが、きぼうから中継をしたとき、エーアールのピカチュウが、野口聡一さんの横に現れたの。", kana="ニセンニジュウイチ'ネンノ/ト_シコシニ'、ジャ'クサガ/キボオカラ'/チュウケエオ'/_シタ'/ト'キ、エエア'アルノ/_ピカ'チュウガ、ノ'グチ/ソオイチサンノ'/ヨコニ'/アラワレ'タノ")
S("m", "normal", "ISSの外には、\nARのレックウザが飛んでいたわ。", AR2021, label="2021年の年越しの中継")
S("z", "surprise", "レックウザ！\n宇宙の空に住むポケモンなのだ。", RAYQ, label="レックウザ")
S("m", "normal", "このとき、ソード・シールドでは「KIBOのピカチュウ」が\n1月15日まで配られていたの。", AR2021, label="2021年の年越しの中継",
  kana="コノ'/ト'キ、ソ'オド/シ'イルドデワ、キ'ボオノ/_ピカ'チュウガ、イチ'ガツ/ジュウゴ'ニチマデ/クバラレテ'/イタ'ノ")
S("z", "happy", "宇宙の記念のピカチュウが、\nゲームの中にも来ていたのだ。", AR2021, label="2021年の年越しの中継")
S("m", "happy", "でもそのときは、画面の中だけ。\n本物のぬいぐるみが行ったのは、今回が初めてね。", CUPOLA_P, label="キューポラのピカチュウ", ans=True)

# ---- まとめ ----
S("m", "think", "今日の答え。宇宙に67日いたピカチュウは、\n人の乗らない補給船シグナスで行って…", ANS, sec="まとめ", label="ピカチュウの宇宙旅行")
S("m", "normal", "地球に帰れる補給船ドラゴンで、\n宇宙飛行士より4か月早く帰ってきたの。", ANS, label="ピカチュウの宇宙旅行")
S("z", "happy", "荷物あつかいでも、\nキューポラの写真はかっこいいのだ。", CUPOLA_P, label="キューポラのピカチュウ")
S("m", "normal", "あなたなら、どのポケモンのぬいぐるみを\n宇宙に連れて行く？コメントで教えてね。", CUPOLA_P, label="キューポラのピカチュウ")

# ---- 英語名 ----
T("おまけ", "今日のポケモンの英語名", "今日のポケモンの英語名", font="hachi")
S("m", "happy", "今日のポケモンの英語名。1匹目は、\nISSの外を飛んだレックウザ。", RAYQ, label="Rayquaza（レイクウェイザ）", lf="hachi")
S("m", "normal", "英語ではレイクウェイザ。\n日本語のレックウザとは、だいぶ響きが違うわね。", RAYQ, label="Rayquaza（レイクウェイザ）", lf="hachi")
S("m", "happy", "2匹目は、博物館のまわりに出たリグレー。\nエルジエム。", ELGY, label="Elgyem（エルジエム）", lf="hachi")
S("m", "normal", "宇宙人のうわさ話で使う「緑の小人」、英語の頭文字LGMを\nそのまま読んだ名前と言われているわ。", ELGY, label="Elgyem（エルジエム）", lf="hachi",
  ety=["Elgyem（エルジエム）", "英語　LGM（little green men 緑の小人＝宇宙人）を読んだ音"],
  say="宇宙人のうわさ話で使う、みどりのこびと。英語の頭文字、エル・ジー・エムを、そのまま読んだ名前と言われているわ。")
S("m", "happy", "3匹目は、月のポケモンのピッピ。\nクレフェアリー。後ろに「妖精」のフェアリーが入っているの。", CLEF, label="Clefairy（クレフェアリー）", lf="hachi")
S("m", "normal", "今日出てきたポケモンの英語名は、\n英単語帳サイト「もんすぺ！」でも調べられるわ。", "site:", label="「もんすぺ！」で検索")
S("m", "happy", "もんすぺ！には、ポケモンの雑学のコラムもあるの。\n動画の続きみたいに読めるわよ。", "site:", label="「もんすぺ！」雑学コラムもあります")
S("z", "happy", "今日の採掘はここまでなのだ。\nチャンネル登録もよろしくなのだ。", "site:", label="「もんすぺ！」で検索")
L.append({"type": "ed"})

script = {
    "no": 8,
    "title": "宇宙に67日いたピカチュウ、行きも帰りも「貨物」だった。",
    "neta": "ピカチュウが67日間宇宙にいた",
    "thumb": {"layout": "v2", "pre": "宇宙に67日いたピカチュウ", "big": ["行きも帰りも", "貨物"], "hl": 1, "hl_color": "red",
              "fonts": ["mincho", "rampart"], "pre_font": "maru", "pre_size": 62,
              "big_w": [700, 600], "big_size": [150, 330], "big_y": 120, "big_gap": -6,
              "back": ISS, "photo": CUPOLA_P, "photo_label": "宇宙ステーションにて", "chara": None},
    "lines": L,
}
here = os.path.dirname(os.path.abspath(__file__))
json.dump(script, open(os.path.join(here, "script.json"), "w"), ensure_ascii=False, indent=1)
n = sum(len(l.get("t", "").replace("\n", "")) for l in L)
print("行数", len(L), "字幕の字数", n)
