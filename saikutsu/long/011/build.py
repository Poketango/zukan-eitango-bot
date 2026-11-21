import json, os
# 第011回 台本（韓国でポケモンGOが遊べたのは、北朝鮮のそばの町だけだった。2016年の束草と、韓国の地図の決まり）
# 2026-11-22 定期作業で作成。ネタ帳「韓国では1つの町でだけ遊べてバスが売り切れ」。
# 裏取り（2つ以上の情報源で照合したものだけを使う）：
#   Korea Times（2016-07-13、07-14）、京郷新聞（07-14、07-17）、WikiTree（07-13）、スポーツ京郷（07-13）、Kotaku（07-14）、
#   Reuters/Fortune（07-13、08-24）、Guardian、AP（07-14）、HuffPost（訂正文つき）、Newspim（07-14）、MT（07-15）、
#   The Fact（07-25）、OSEN（08-04）、Korea JoongAng Daily（08-21）、AP/phys.org・AFP（2016-11-18）、イートゥデイ、政策ブリーフィング（2016-11-18）、
#   VOA・電子新聞・inews24（2017-01-24）、Newspim（2017-01-30）、Newsis・AP・京郷新聞（2026-02-27）、
#   ソウル新聞・京郷新聞英語版（2026-11-13）、空間情報の構築及び管理等に関する法律 第16条（韓国法制研究院の英訳）。
# 1つの出典でしか確かめられなかったこと（バスの増便の数、ホテルの無料宿泊、市の言い換えの宣伝名、OpenStreetMap の表示、
#   束草ブームの終わった時期、2016年の申請の縮尺）は使っていない。束草だけ遊べた理由は Niantic が公式に説明していないので「報じられた」とする。
L = []
def S(w, face, t, img=None, **kw):
    d = {"w": w, "face": face, "t": t}
    if img: d["img"] = img
    d.update(kw); L.append(d)
def T(sub, t, sec=None, **kw):
    L.append({"type": "title", "sub": sub, "t": t, **({"sec": sec} if sec else {}), **kw})

# 画像（コモンズのファイル名は 2026-11-22 に内蔵ブラウザで実在と中身を確かめた）
KMAP = "commons:South Korea adm location map.svg"          # 範囲 北緯33.0〜38.9度、東経124.5〜132.0度
P_SOKCHO = [0.546, 0.117, 0.05]
P_SEOUL = [0.330, 0.226, 0.05]
P_ULLEUNG = [0.849, 0.237, 0.05]
P_GANJ = [0.648, 0.600, 0.05]
P_BUSAN = [0.611, 0.631, 0.05]
GMAP = "commons:Map Sokcho-si.PNG"
SOKCHO = "commons:View of Sokcho 01.jpg"
SOKCHO2 = "commons:Korea-Sokcho from Seoraksan-01.jpg"
BEACH = "commons:Sokcho, Sokcho Beach.jpg"
DAEPO = "commons:Daepo Port, Sokcho 01.jpg"
BUS = "commons:동해상사고속 속초동서울시외 1546호.png"
TERM = "commons:속초고속터미널 외부.png"
DSEOUL = "commons:Eastern Seoul Bus Terminal.jpg"
ABAI = "commons:Abai Village.jpg"
FERRY = "commons:Ferry in Sokcho.jpg"
SEORAK = "commons:Seoraksan National Park panorama 3.jpg"
EXPO = "commons:Korea-Sokcho-Expo Tower-01.jpg"
S1951 = "commons:Socho-Ri Korea from Duck, December 1951.jpg"
RELEASE = "commons:Pokémon Go Release Map.svg"
GOLOGO = "commons:Pokémon GO logo.svg"
PHONE = "commons:App-augmented-reality-game-gps-163042.jpg"
CROWD = "commons:Pokémon GO Fever in Tsuruma Park - 4.jpg"
JPFEVER = "commons:Pokémon GO Fever in Japan (28387760021).jpg"
INGRESS = "commons:Ingress Logo vector.svg"
ARMIS = "commons:Korean War armistice agreement 1953.jpg"
NIGHT = "commons:Korean Peninsula at night from space.jpg"
GMLOGO = "commons:Google Maps Logo 2020.svg"
GHQ = "commons:Googleplex HQ (cropped).jpg"
MOLIT = "commons:Ministry of Land, Infrastructure, and Transport(South Korea).JPG"
SVCAR = "commons:Google Street View car in Bern.jpg"
GANJ = "commons:Ganjeolgot, Ulsan on August 16th, 2018.jpg"
TSUSHIMA = "commons:Busan as seen from Korea Observatory in Tsushima.jpg"
ULLEUNG = "commons:Ulleung island from above.jpg"
UNIOBS = "commons:Goseong Unification Observatory Tower.jpg"
JSA = "commons:Flag of the DPRK at Panmunjom Joint Security Area (13952141430).jpg"
SEOUL = "commons:Seoul Skyline Night 2018.jpg"
PEN = "commons:Korean Peninsula boundaries.png"
TWO = "row:" + DSEOUL + "|東ソウルのバスターミナル>" + TERM + "|束草のバスターミナル"

# ---- コールドオープン ----
S("m", "normal", "2016年の夏、韓国で、ソウルから\nある町へ行くバスの切符が売り切れたの。", BUS,
  sec="ポケモン雑学採掘場", label="ソウルと束草を結ぶバス")
S("z", "surprise", "売り切れ！？\nお祭りでもあったのだ？", BUS, label="ソウルと束草を結ぶバス")
S("m", "think", "みんな、ポケモンGOをしに行ったの。\n韓国で遊べたのは、ほぼその町のあたりだけだったのよ。", KMAP, label="束草（ソクチョ）", mark=P_SOKCHO, ans=True)
S("z", "shock", "国の中で、そこだけ！？\nどうしてそんなことになるのだ？", KMAP, label="束草（ソクチョ）", mark=P_SOKCHO)
L.append({"type": "op", "w": "m", "t": "ポケモンの深い雑学を掘り出す、\nポケモン雑学採掘場。", "say": "ポケモンの深い雑学を掘り出す、ポケモン雑学さいくつじょう。"})

# ---- 導入 ----
S("z", "think", "この坑道の地図、古すぎるのだ。\nさっきから同じ所を回っている気がするのだ。", PEN, sec="導入　地図のない国", label="地図がないと迷う")
S("m", "normal", "地図がないと困るわよね。\nじつは、地図のせいでポケモンGOが遊べなかった国があるの。", PHONE, label="ポケモンGO（2016年〜）")
S("z", "surprise", "ポケモンGOって、\n地図の上を歩いて遊ぶゲームなのだ。", PHONE, label="ポケモンGO（2016年〜）")
S("m", "normal", "そう。スマホの地図の上で、\n本当に歩いた所にポケモンが出るの。", CROWD, label="ポケモンGOに集まる人たち（名古屋）")
S("m", "normal", "だから地図が使えない国では、\nゲームそのものが成り立たないのね。", CROWD, label="ポケモンGOに集まる人たち（名古屋）")
S("z", "think", "地図が使えない国なんて、\nあるのだ？", KMAP, label="韓国")
S("m", "normal", "それが、お隣の韓国なの。今日は、2016年の夏に\n韓国で起きた、ポケモンGOの大移動を掘るわ。", KMAP, label="韓国")
T("本日の採掘", "なぜ韓国では、束草でしか遊べなかった？", font="mincho")

# ---- 第一層 ----
T("第一層", "2016年7月、韓国だけ置いてけぼり", "第一層　配信されない国", font="reggae",
  x={"head": "2016年、ポケモンGOは\n韓国では配信されず\n非公式に数十万人が入れた", "img": [RELEASE], "bubble": "待ちきれないのだ", "who": "z",
     "post": "2016年7月6日、ポケモンGOはアメリカ、オーストラリア、ニュージーランドで始まりました。日本は7月22日。ところが韓国では正式に配信されず、待ちきれない人が非公式な方法で入れたアプリは数十万人分にのぼったと報じられました。でも入れても、地図が出ないので遊べませんでした。"})
S("m", "normal", "ポケモンGOが始まったのは、2016年7月6日。\nアメリカ、オーストラリア、ニュージーランドが最初よ。", RELEASE, label="ポケモンGOが始まった国（赤が最初）")
S("m", "normal", "日本では、2週間あとの7月22日。\n公園や駅前に、人があふれたわね。", JPFEVER, label="2016年夏の日本")
S("m", "normal", "でも韓国では、正式には配信されなかったの。\nアプリのお店にも、並ばなかったのね。", KMAP, label="2016年夏の韓国")
S("z", "sad", "日本のすぐ隣なのに、\nおあずけなのだ…。", KMAP, label="2016年夏の韓国")
S("m", "normal", "待ちきれない人たちは、正式ではない方法で、\nアプリをスマホに入れたの。", PHONE, label="非公式に入れたアプリ")
S("m", "normal", "その数は、数十万人分にのぼったと報じられたわ。\nところが、入れても遊べなかったの。", PHONE, label="非公式に入れたアプリ")
S("z", "think", "アプリが動かないのだ？", PHONE, label="非公式に入れたアプリ")
S("m", "normal", "アプリは動くけれど、韓国の中では、\n地図もポケモンも出てこなかったの。", KMAP, label="韓国では地図が出ない")
S("m", "normal", "ところが7月12日の夜、ネットに、\nある書き込みが広まったの。", KMAP, label="2016年7月12日の夜")
S("m", "normal", "束草では、ポケモンGOが遊べる。\nポケモンがちゃんと出てくる、というのよ。", KMAP, label="束草（ソクチョ）", mark=P_SOKCHO, ans=True)
S("m", "normal", "書き込まれたのは、韓国のゲーム情報サイト、\nインベンの掲示板。次の日には、サイトの記者が束草まで確かめに行ったわ。", KMAP, label="束草（ソクチョ）", mark=P_SOKCHO)
S("m", "normal", "束草のコンビニの店員さんは、\nお客さんは来ないのに、ポケモンだけ来る、と書き込んだそうよ。", SOKCHO, label="束草の町")
S("z", "surprise", "束草？\nどこにある町なのだ？", KMAP, label="束草（ソクチョ）", mark=P_SOKCHO)

# ---- 第二層 ----
T("第二層", "北の端の港町、束草", "第二層　束草へ大移動", font="potta",
  x={"head": "ポケモンGOのために\nソウル発の束草行きの\nバスが売り切れた", "img": [BUS], "bubble": "遠くても行くのだ", "who": "z",
     "post": "2016年7月、韓国でポケモンGOが遊べるのは北東の港町・束草のあたりだけだと分かると、ソウルの東ソウルのバスターミナルから出る束草行きのバスが売り切れました。束草の宿の予約は前の週の5倍ほどに。市は無料Wi-Fiの地図を出し、「半島で唯一のポケモンGOの聖地」と呼びかけました。あなたなら行きますか？"})
S("m", "normal", "束草は、韓国の北東のはし、\n江原道という地方の海沿いにある市よ。", GMAP, label="江原道の束草市", mark=[0.62, 0.28, 0.06])
S("m", "normal", "人口は8万人ほど。雪岳山という、\n韓国でも有名な山の入り口の町なの。", SEORAK, label="雪岳山（ソラクサン）")
S("m", "normal", "北朝鮮との境目にも近くて、国が南北に分かれた\n1945年からしばらくは、北朝鮮の側にあった町なの。", S1951, label="1951年の束草")
S("m", "normal", "戦争中の1951年に韓国軍が取って、\n休戦のあとは韓国の町になったのね。", S1951, label="1951年の束草")
S("m", "normal", "北から逃げてきた人たちが作った、\nアバイ村という集落も残っているわ。", ABAI, label="アバイ村")
S("z", "think", "歴史のある港町なのだ。\nでも、ソウルからは遠そうなのだ。", SOKCHO, label="束草の町")
S("m", "normal", "ソウルから行くには、東へ山を越えて、\n反対側の海まで出ないといけないの。", TWO, label="ソウルから束草へ")
S("m", "normal", "書き込みが広まった翌日の7月13日、\n東ソウルのバスターミナルの束草行きは、全部売り切れ。", DSEOUL, label="東ソウル総合ターミナル", ans=True)
S("m", "normal", "週末のバスも、\n満席になったと報じられたわ。", BUS, label="ソウルと束草を結ぶバス")
S("z", "surprise", "ゲームのために、\n山の向こうまで行くのだ！？", BUS, label="ソウルと束草を結ぶバス")
S("m", "normal", "宿の予約も増えたの。旅行会社のアプリでは、\n束草の予約が前の週の5倍ほどになったわ。", BEACH, label="束草の海水浴場")
S("m", "normal", "束草市も、すぐに動いたの。\n無料Wi-Fiが使える場所の地図を出したのよ。", EXPO, label="束草の夜の町")
S("m", "normal", "そして、「半島で唯一のポケモンGOの聖地」と\n呼びかけたの。", EXPO, label="束草市の呼びかけ", big="半島で唯一の聖地", bf="fude")
S("z", "happy", "町ぐるみで\n乗っかったのだ！", EXPO, label="束草の夜の町")
S("m", "normal", "市長は、市長室でポケモンを捕まえる動画を、\n自分でフェイスブックに載せたの。", SOKCHO, label="束草の町")
S("m", "normal", "思いがけない幸運だ、と話したそうよ。\nスマホの充電ができる場所も、増やすと約束したわ。", SOKCHO, label="束草の町")
S("z", "think", "でも、どうして束草だけ\n遊べたのだ？", KMAP, label="束草（ソクチョ）", mark=P_SOKCHO)

# ---- 第三層 ----
T("第三層", "地図のマス目のすき間", "第三層　なぜ束草だけ？", font="train",
  x={"head": "束草のあたりは\nポケモンGOの区分で\n韓国の外にあったと報じられた", "img": [KMAP], "bubble": "マス目のすき間なのだ", "who": "z",
     "post": "なぜ韓国で束草のあたりだけポケモンGOが遊べたのか。当時の報道では、運営のナイアンティックが世界をマス目の区画に分けていて、束草のあたりが韓国ではなく北朝鮮の区画に入っていたからだと説明されました。運営は理由を公式には説明していません。鬱陵島や、近くの襄陽・高城でも遊べました。"})
S("m", "normal", "ポケモンGOを作ったのは、ナイアンティックという\nアメリカの会社なの。", INGRESS, label="ナイアンティックの前作「イングレス」")
S("m", "normal", "前の作品のイングレスという陣取りゲームの地図や\n場所のデータを、ポケモンGOにも使っていたの。", INGRESS, label="ナイアンティックの前作「イングレス」")
S("m", "normal", "ジムやポケストップの場所も、\nイングレスで登録された場所がもとになっているわ。", CROWD, label="ポケストップに集まる人たち（名古屋）")
S("m", "normal", "そのデータは、世界を\nひし形のマス目のような区画に分けていたの。", PEN, label="朝鮮半島")
S("m", "normal", "ネットには、遊べない所をひし形のマス目で塗った地図が\n出回ったの。束草のあたりは、そのマス目から外れていたのね。", KMAP, label="遊べない区画の外", mark=P_SOKCHO)
S("m", "normal", "当時の報道によれば、束草のあたりは、\n韓国ではなく北朝鮮の区画に入っていたの。", KMAP, label="束草（ソクチョ）", mark=P_SOKCHO, ans=True)
S("z", "shock", "北朝鮮の区画！？\nだから遊べたのだ？", KMAP, label="束草（ソクチョ）", mark=P_SOKCHO)
S("m", "normal", "韓国の区画では遊べないようにしていたから、\nそこから外れた束草では遊べた、というわけね。", KMAP, label="束草（ソクチョ）", mark=P_SOKCHO)
S("z", "think", "国じゅうのブレーカーを落としたのに、\n別の配線の部屋だけ、電気がついていたようなものなのだ。", KMAP, label="束草（ソクチョ）", mark=P_SOKCHO)
S("m", "normal", "そのたとえで、だいたい合っているわ。\n束草は、別の配線の部屋だったのね。", KMAP, label="束草（ソクチョ）", mark=P_SOKCHO)
S("m", "normal", "ただ、グーグルマップが束草を北朝鮮としていた、\nというわけではないの。", GMLOGO, label="グーグルマップ")
S("m", "normal", "最初にそう書いた記事は、のちに、\nゲームの区分の話だったと訂正しているわ。", GMLOGO, label="グーグルマップ")
S("m", "normal", "それに、ナイアンティックは、\n理由を公式には説明していないの。", INGRESS, label="ナイアンティックは説明していない")
S("z", "think", "ほかにも、遊べた所は\nあったのだ？", ULLEUNG, label="鬱陵島（ウルルンド）")
S("m", "normal", "束草の近くの襄陽や高城の一部。\nそれに、日本海に浮かぶ鬱陵島でも遊べたの。", ULLEUNG, label="鬱陵島（ウルルンド）")
S("m", "normal", "高城は、北朝鮮との境目に接する郡。\n北朝鮮の山を見渡せる、統一展望台がある所ね。", UNIOBS, label="高城の統一展望台")
S("z", "think", "北に近い所ばかり\n遊べたのだ。", KMAP, label="北の境目に近い所", mark=[0.53, 0.08, 0.08])
S("m", "normal", "ちなみに、境目の板門店にも、\nジムがあったの。", JSA, label="板門店（共同警備区域）")
S("m", "normal", "南と北の兵士がにらみ合う場所よ。イングレスで\n登録された場所が残っていたけれど、のちに消されたわ。", JSA, label="板門店（共同警備区域）")
S("z", "surprise", "そんな所でジムバトルは、\nさすがにできないのだ。", JSA, label="板門店（共同警備区域）")

# ---- 第四層 ----
T("第四層", "地図を国の外に出せない国", "第四層　地図の法律", font="mincho",
  x={"head": "韓国では、細かい地図を\n国の許可なく\n国外に持ち出せない", "img": [MOLIT], "bubble": "地図が国の秘密なのだ", "who": "z",
     "post": "そもそもなぜ韓国全体でポケモンGOが遊べなかったのか。当時よく挙げられた理由は、韓国の地図の法律でした。細かい地図のデータは、国の許可なく国外に持ち出せません。北朝鮮と休戦中で、軍の施設の場所が知られるおそれがあるからです。グーグルは2016年に持ち出しを申し込み、その年の11月に断られました。"})
S("z", "think", "そもそも、韓国のほかの所は、\nどうして遊べなかったのだ？", SEOUL, label="ソウル")
S("m", "normal", "当時よく挙げられた理由は、\n韓国の地図の法律なの。", MOLIT, label="韓国の国土交通部")
S("m", "normal", "韓国の法律では、国が作った細かい地図のデータを、\n許可なく国の外へ持ち出してはいけないの。", MOLIT, label="韓国の国土交通部")
S("m", "normal", "空間情報の構築及び管理等に関する法律、\nその第16条の決まりよ。", MOLIT, label="空間情報の法律 第16条", say="空間情報の構築および管理とうに関する法律、その第16条の決まりよ。")
S("z", "think", "地図を外に出すと、\nなにが困るのだ？", NIGHT, label="夜の朝鮮半島（宇宙から）")
S("m", "normal", "朝鮮戦争は、1953年に休戦しただけで、\n今も正式には終わっていないの。", ARMIS, label="休戦協定の調印（1953年）")
S("m", "normal", "細かい地図が外に出ると、軍の基地などの場所を、\n北朝鮮に知られるおそれがある、という考えなのね。", NIGHT, label="夜の朝鮮半島（宇宙から）")
S("m", "normal", "グーグルのサーバーは国の外にあるから、\n韓国の細かい地図は、グーグルマップに入れられないの。", GHQ, label="グーグルの本社（アメリカ）")
S("m", "normal", "だから韓国のグーグルマップでは、\n電車やバスの案内はできても、車や歩きの道案内ができないの。", GMLOGO, label="韓国のグーグルマップ")
S("z", "surprise", "道案内のできない\nグーグルマップなのだ！？", GMLOGO, label="韓国のグーグルマップ")
S("m", "normal", "グーグルは2016年6月、地図のデータを\n持ち出させてほしいと、韓国の国に申し込んだの。", GHQ, label="グーグルの申し込み（2016年6月）")
S("m", "normal", "国は、衛星写真の軍の施設をぼかすなら、\nという条件を出したけれど、グーグルは受け入れなかったの。", SVCAR, label="グーグルの地図づくりの車")
S("m", "normal", "判断したのは、国土交通部を中心に、国防部や\n国の情報機関まで入った、8つの役所の集まりよ。", MOLIT, label="8つの役所で判断")
S("z", "think", "地図1枚に、\n軍や情報機関まで出てくるのだ。", MOLIT, label="8つの役所で判断")
S("m", "normal", "そして2016年11月18日、国は、\n申し込みを断ったわ。", MOLIT, label="2016年11月18日 却下", big="持ち出し却下", bf="mincho", ans=True)
S("m", "normal", "ちなみに2023年には、アップルの地図の\n持ち出しの申し込みも、断られているわ。", MOLIT, label="2023年 アップルも却下")
S("z", "sad", "ポケモンGOは、\nもっと遠のいたのだ…。", SEOUL, label="ソウル")

# ---- 第五層 ----
T("第五層", "日本の配信で、韓国の岬が遊べた", "第五層　日本につながった岬", font="deco",
  x={"head": "日本でポケモンGOが始まると\n韓国の岬・カンジョルゴッが\n遊べるようになった", "img": [GANJ], "bubble": "日本の区画なのだ", "who": "z",
     "post": "2016年7月22日に日本でポケモンGOが始まると、韓国南東の蔚山にある岬・カンジョルゴッのあたりでも遊べるようになりました。日本の区画に入っていたと報じられています。対馬と同じ区画の釜山も遊べると期待されましたが、遊べたのは岬のまわりだけでした。区画の線1本で、遊べる場所が決まっていたのです。"})
S("m", "normal", "このお話には、日本につながる続きがあるの。\n7月22日、日本でポケモンGOが始まった日よ。", JPFEVER, label="2016年7月22日 日本で配信")
S("m", "normal", "その日から、韓国の南東の、蔚山という町の\nカンジョルゴッという岬でも、遊べるようになったの。", KMAP, label="蔚山のカンジョルゴッ", mark=P_GANJ, ans=True)
S("z", "surprise", "日本で始まったのに、\n韓国の岬が遊べたのだ？", GANJ, label="カンジョルゴッの岬")
S("m", "normal", "釜山のあたりは、日本の対馬と同じ区画だから、\n日本で始まれば遊べる、と期待されていたの。", TSUSHIMA, label="対馬から見た釜山")
S("m", "normal", "対馬から釜山までは、50キロほど。\n晴れた日には、町が見えるほど近いの。", TSUSHIMA, label="対馬から見た釜山",
  kana="ツシマカラ'/プサンマ'デワ、ゴジュッキ'ロホド、ハレタ'/ヒ'ニワ、マチ'ガ/ミエル'ホド/チカイ'ノ")
S("m", "normal", "でも、釜山の町では遊べなかったの。\n遊べたのは、岬のまわりだけだったのよ。", GANJ, label="カンジョルゴッの岬")
S("z", "think", "区画の分け方しだいで、\n遊べる所が変わるのだ。", KMAP, label="釜山と蔚山", mark=P_BUSAN)
S("m", "normal", "それでも、日の出の名所の静かな岬に、\nスマホを持った人たちが押し寄せたのよ。", GANJ, label="カンジョルゴッの岬", big="岬に人が押し寄せた", bf="rampart")
S("z", "happy", "日本の配信日に、\n韓国の岬が日本の仲間入りなのだ。", GANJ, label="カンジョルゴッの岬")

# ---- 最深層 ----
T("最深層", "10年後、グーグルの地図はどうなった", "最深層　10年越しの許可", font="fude",
  x={"head": "韓国の地図の持ち出し\n2026年、グーグルに\n条件つきで許可が出た", "img": [GMLOGO], "bubble": "10年越しなのだ", "who": "z",
     "post": "ポケモンGOは2017年1月24日に韓国で正式に始まり、初日に約291万人が遊びました。いっぽうグーグルの地図の持ち出しは、2016年に断られたあと、2025年に申し込み直し、2026年2月27日に条件つきで認められました。軍の施設をぼかす、緊急時に機能を止められるようにする、などの条件です。"})
S("m", "normal", "ポケモンGOが韓国で正式に始まったのは、\n2017年1月24日。束草さわぎの半年後よ。", RELEASE, label="黄色が韓国（2017年1月24日）", mark=[0.628, 0.215, 0.03])
S("m", "normal", "ナイアンティックは、公開されている\nいろいろな地図のデータを使った、と話したの。", PHONE, label="2017年1月24日 韓国で配信")
S("m", "normal", "遅れたのは地図のせいではなく、\nたくさんの人を受け止める準備のためだった、とも説明したわ。", INGRESS, label="ナイアンティックの説明")
S("z", "think", "地図のせいだと思われていたけれど、\n会社の説明は違ったのだ。", INGRESS, label="ナイアンティックの説明")
S("m", "normal", "始まった日には、韓国で\n約291万人が遊んだと調べられているの。", SEOUL, label="配信の初日に約291万人", big="初日に約291万人", bf="rampart")
S("m", "normal", "そして、グーグルの地図のほう。\n2025年2月、グーグルはもう一度、持ち出しを申し込んだの。", GHQ, label="2025年2月 もう一度申し込み")
S("m", "normal", "国は判断を何度も延ばして、\n2026年2月27日、条件つきで認めたわ。", MOLIT, label="2026年2月27日 条件つきの許可", ans=True)
S("z", "surprise", "最初に断られてから、\n10年近くたっているのだ！", MOLIT, label="2026年2月27日 条件つきの許可")
S("m", "normal", "束草行きのバスが売り切れた夏から数えると、\nもう10年がたったのね。", BUS, label="2016年夏から10年")
S("m", "normal", "条件は、衛星写真やストリートビューで、\n軍の施設をぼかしたり消したりすること。", SVCAR, label="ストリートビューの車")
S("m", "normal", "それに、国の安全にかかわる時には、\n地図の機能を止められるようにすること、などよ。", NIGHT, label="夜の朝鮮半島（宇宙から）")
S("m", "normal", "地図に、韓国の土地の緯度と経度を出さないこと。\nデータは、韓国の会社のサーバーで処理してから出すこと。", GMLOGO, label="許可の条件")
S("z", "surprise", "条件がびっしりなのだ。\n地図って、国にとってそんなに大事なのだ。", GMLOGO, label="許可の条件")
S("m", "normal", "2026年11月13日、国は、グーグルが\n条件を守っていることを確かめたと発表したわ。", MOLIT, label="2026年11月13日の発表")
S("m", "normal", "ただ、韓国のグーグルマップで道案内が始まる日は、\nまだ発表されていないの。", GMLOGO, label="道案内の開始はまだ")

# ---- まとめ ----
S("m", "think", "今日の答え。韓国で束草のあたりだけ遊べたのは、\nゲームの区画で、韓国の外にあったからと報じられたの。", KMAP, sec="まとめ", label="束草（ソクチョ）", mark=P_SOKCHO)
S("m", "normal", "地図を外に出せない国のルールと、\nゲームのマス目のすき間が重なって、町に人が押し寄せたのね。", BUS, label="ソウルと束草を結ぶバス")
S("z", "think", "地図の線1本で、\nバスが売り切れたのだ。", BUS, label="ソウルと束草を結ぶバス")
S("m", "normal", "あなたなら、ポケモンGOのために、\n山の向こうの町まで行く？", DAEPO, label="束草の港")

# ---- 英語名 ----
T("おまけ", "今日のポケモンの英語名", "今日のポケモンの英語名", font="hachi")
S("m", "happy", "今日の英語名は、ポケモンGOで\n最初に選べる3匹から2匹よ。", "row:art:1|フシギダネ;art:4|ヒトカゲ", label="ポケモンGOの最初の相棒", lf="hachi")
S("m", "happy", "まず、フシギダネ。\nバルバソー。", "art:1", label="Bulbasaur（バルバソー）", lf="hachi")
S("m", "normal", "bulbは、球根。saurは、トカゲという意味で、\n恐竜の名前の終わりにつく言葉ね。", "art:1", label="Bulbasaur（バルバソー）", lf="hachi",
  ety=["Bulbasaur（バルバソー）", "英語　bulb（球根）＋ギリシャ語　sauros（トカゲ）"],
  say="バルブは、球根。ソーは、トカゲという意味で、恐竜の名前の終わりにつく言葉ね。")
S("m", "happy", "次は、ヒトカゲ。\nチャーマンダー。", "art:4", label="Charmander（チャーマンダー）", lf="hachi")
S("m", "normal", "charは、焦がすこと。salamanderは、\n火の中にすむと言われたトカゲの名前よ。", "art:4", label="Charmander（チャーマンダー）", lf="hachi",
  ety=["Charmander（チャーマンダー）", "英語　char（焦がす）＋salamander（火トカゲ）"],
  say="チャーは、焦がすこと。サラマンダーは、火の中にすむと言われたトカゲの名前よ。")
S("m", "normal", "今日出てきたポケモンの英語名は、\n英単語帳サイト「もんすぺ！」でも調べられるわ。", "site:", label="「もんすぺ！」で検索")
S("m", "happy", "もんすぺ！には、ポケモンの雑学のコラムもあるの。\n動画の続きみたいに読めるわよ。", "site:", label="「もんすぺ！」雑学コラムもあります")
S("z", "happy", "今日の採掘はここまでなのだ。\nチャンネル登録もよろしくなのだ。", "site:", label="「もんすぺ！」で検索")
L.append({"type": "ed"})

script = {
    "no": 11,
    "title": "韓国でポケモンGOが遊べたのは、北朝鮮の近くの町だった。",
    "neta": "韓国では1つの町でだけ遊べてバスが売り切れ",
    "thumb": {"layout": "v2", "pre": "韓国でここだけ遊べた", "big": ["バスが", "売り切れ"], "hl": 1, "hl_color": "red",
              "fonts": ["mincho", "mincho"], "pre_font": "maru", "pre_size": 62,
              "back": SOKCHO, "photo": BUS, "photo_label": "ソウル発 束草行きのバス", "chara": None},
    "lines": L,
}
here = os.path.dirname(os.path.abspath(__file__))
json.dump(script, open(os.path.join(here, "script.json"), "w"), ensure_ascii=False, indent=1)
n = sum(len(l.get("t", "").replace("\n", "")) for l in L)
print("行数", len(L), "字幕の字数", n)
