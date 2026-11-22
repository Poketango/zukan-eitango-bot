import json, os
# 第012回 台本（なぜゴッホ美術館の職員は、ピカチュウのカードで停職になったのか？）
# 2026-11-23 定期作業で作成。ネタ帳「ゴッホ美術館のピカチュウで職員が停職」。
# 裏取り（2つ以上の情報源で照合したものだけを使う）：
#   ポケモン社とゴッホ美術館の共同プレスリリース（2023-09-27、pokemon.gamespress.com）、Smithsonian、Nintendo Life（2023-09-12）、
#   NOS（2023-09-28、2023-10-07、2024-01-24）、DutchNews（2023-09-28、2024-01-24）、Art Newspaper（2024-01-25）、
#   GameSpot・Kotaku（2023-09-29）、GamesRadar・Polygon（2023-09-29、2023-10-13）、NL Times（2023-10-14、2024-01-24）、
#   AFP（Dawn 2023-10-15）、Guardian、PC Gamer、VGC（2024-02-04）、DutchReview（2024-02-05）、Artnet、Euronews、
#   NH Nieuws・AT5（2024-01-24）、Serebii・PokeGuardian（展示の6点）、美術手帖・ファミ通・インサイド（日本語の報道）、
#   ゴッホの手紙（webexhibits.org の英訳。1888-03-18 ベルナール宛て、1888-07-15・1888-09-24 テオ宛て）。
# 1つの出典でしか確かめられなかったこと（出口の外での買い取り値、1日に900ユーロの少年、職員向けの絵の転売、
#   2023年の入館者数、「法的には解雇ではない」という一文、ひまわりの本数の問題、ぬいぐるみの完売時刻）は使っていない。
#   職員の処分の中身は美術館が認めていないので「報じられた」とする。
L = []
def S(w, face, t, img=None, **kw):
    d = {"w": w, "face": face, "t": t}
    if img: d["img"] = img
    d.update(kw); L.append(d)
def T(sub, t, sec=None, **kw):
    L.append({"type": "title", "sub": sub, "t": t, **({"sec": sec} if sec else {}), **kw})

# 画像（コモンズのファイル名は 2026-11-23 に内蔵ブラウザで実在と中身を確かめた）
CARD = "web:https://images.pokemontcg.io/svp/85_hires.png"     # Pikachu with Grey Felt Hat（SV プロモ 085）
FELT = "commons:Zelfportret met grijze vilthoed - s0016V1962 - Van Gogh Museum.jpg^commons:Vincent van Gogh - Self-portrait with grey felt hat - Google Art Project.jpg"
PAIR = "row:" + FELT + "|ゴッホの自画像（1887年）>" + CARD + "|ピカチュウのカード（2023年）"
VGM = "commons:Van Gogh Museum 7206 rt HDR.jpg"
VGM2 = "commons:Van Gogh Museum, Kurokawa wing.jpg"
VGM3 = "commons:Van Gogh Museum Amsterdam.jpg"
OPEN73 = "commons:Bezoekers tijdens de opening, Bestanddeelnr 926-8880.jpg"
JULIANA = "commons:Koningin Juliana wordt rondgeleid door het museum, Bestanddeelnr 926-4520.jpg"
PLUM = "commons:Bloeiende pruimenboomgaard (naar Hiroshige) - s0115V1962 - Van Gogh Museum.jpg"
PLUM_H = "commons:Utagawa Hiroshige Plum Garden at Kameido (Kameido Umeyashiki).jpeg"
PLUM2 = "row:" + PLUM_H + "|広重「亀戸梅屋舗」>" + PLUM + "|ゴッホの模写（1887年）"
RAIN = "commons:Brug in de regen (naar Hiroshige) - s0114V1962 - Van Gogh Museum.jpg"
RAIN_H = "commons:Hiroshige, Sudden shower over Shin-Ōhashi bridge and Atake, 1857.jpg"
RAIN2 = "row:" + RAIN_H + "|広重「大はしあたけの夕立」>" + RAIN + "|ゴッホの模写（1887年）"
EISEN = "commons:Courtisane (naar Eisen) - s0116V1962 - Van Gogh Museum.jpg"
LANGLOIS = "commons:Vincent van Gogh - De brug van Langlois - Google Art Project.jpg"
YELLOW = "commons:Vincent van Gogh - The yellow house ('The street').jpg"
THEO = "commons:Portret van Theo van Gogh - s0157V1962 - Van Gogh Museum.jpg"
TANGUY = "commons:Van Gogh - Portrait of Pere Tanguy 1887-8.JPG"
EAR = "commons:Vincent van Gogh - Self-portrait with bandaged ear (1889, Courtauld Institute).jpg"
SUN = "commons:Zonnebloemen - s0031V1962 - Van Gogh Museum.jpg"
BED = "commons:Vincent van Gogh - De slaapkamer - Google Art Project.jpg"
CROWS = "commons:Korenveld met kraaien - s0149V1962 - Van Gogh Museum.jpg"
STRAW = "commons:Zelfportret met strohoed - s0164V1962 - Van Gogh Museum.jpg"
PAINTER = "commons:Zelfportret als schilder - s0022V1962 - Van Gogh Museum.jpg"
ALMOND = "commons:Amandelbloesem - s0176V1962 - Van Gogh Museum.jpg"
VERMEER = "commons:Johannes Vermeer - Het melkmeisje - Google Art Project.jpg"
EBAY = "commons:EBay logo.svg^commons:EBay former logo.svg"
MPL = "commons:Marktplaats Logo.png"
TCG = "commons:Pokémon Trading Card Game logo.svg"
VEND = "commons:Gare Centrale distributeur cartes pokémon.jpg"
CANAL = "commons:Water reflection of canal houses at blue hour in Damrak Amsterdam the Netherlands.jpg"
POLICE = "commons:Hoofdbureau-van-Politie-Amsterdam.jpg"

# ---- コールドオープン ----
S("m", "normal", "2023年の秋、オランダのゴッホ美術館で、\n職員が少なくとも4人、仕事を外されたの。", VGM,
  sec="ポケモン雑学採掘場", label="ゴッホ美術館（アムステルダム）")
S("z", "surprise", "名画を盗んだのだ？\n大事件なのだ。", VGM, label="ゴッホ美術館（アムステルダム）")
S("m", "think", "絵ではないの。原因は、帽子をかぶった\nピカチュウの、カード1枚よ。", CARD, label="帽子をかぶったピカチュウのカード", ans=True)
S("z", "shock", "ピカチュウのカードで、\n美術館の人が処分されたのだ！？", CARD, label="帽子をかぶったピカチュウのカード")
L.append({"type": "op", "w": "m", "t": "ポケモンの深い雑学を掘り出す、\nポケモン雑学採掘場。", "say": "ポケモンの深い雑学を掘り出す、ポケモン雑学さいくつじょう。"})

# ---- 導入 ----
S("z", "think", "このヘルメット、毎日かぶっていると\n頭が蒸れるのだ。帽子に替えたいのだ。", FELT, sec="導入　帽子のピカチュウ", label="フェルトの帽子")
S("m", "normal", "帽子といえば、ゴッホの帽子を\nかぶったピカチュウがいるのよ。", PAIR, label="自画像とピカチュウ")
S("z", "surprise", "ゴッホって、ひまわりの絵の、\nあの画家なのだ？", SUN, label="ゴッホ「ひまわり」（1889年）")
S("m", "normal", "そう。19世紀のオランダの画家、\nフィンセント・ファン・ゴッホよ。", FELT, label="ゴッホの自画像（1887年）")
S("m", "normal", "この自画像は、灰色のフェルト帽の自画像。\nゴッホがパリにいた1887年の絵ね。", FELT, label="灰色のフェルト帽の自画像")
S("m", "normal", "2023年、この帽子をピカチュウにかぶせた\nカードが、美術館で配られたの。", PAIR, label="自画像とピカチュウ")
S("z", "happy", "かわいいのだ。\nもらったらうれしいのだ。", CARD, label="帽子をかぶったピカチュウのカード")
S("m", "normal", "ところがこのカードのせいで、美術館は\n配るのをやめて、職員まで処分されたの。", VGM2, label="ゴッホ美術館")
T("本日の採掘", "ピカチュウのカードで、美術館に何が起きた？", font="mincho")

# ---- 第一層 ----
T("第一層", "なぜゴッホ美術館に、ポケモンが？", "第一層　ゴッホと日本", font="mincho",
  x={"head": "ゴッホ美術館が\nポケモンと組んだのは\n開館50周年の企画だった", "img": [VGM], "bubble": "50歳なのだ", "who": "z",
     "post": "オランダのゴッホ美術館は、2023年にポケモンと組んで展示をしました。開館は1973年で、50周年の企画です。館長は、ゴッホが日本の浮世絵に深い関心を持っていたこと、そしてポケモンが日本の絵の文化の象徴であることを理由に挙げました。美術館とポケモン、意外な組み合わせだと思いますか？"})
S("m", "normal", "ゴッホ美術館は、オランダの首都、\nアムステルダムにある美術館よ。", CANAL, label="アムステルダム（オランダ）")
S("m", "normal", "ゴッホの絵を世界でいちばん多く持っていて、\n開いたのは1973年なの。", OPEN73, label="1973年の開館の日")
S("m", "normal", "開館の日には、オランダのユリアナ女王が\n館内を見て回ったのよ。", JULIANA, label="1973年 ユリアナ女王")
S("m", "normal", "だから2023年は、ちょうど50周年。\nその記念の企画の1つが、ポケモンだったの。", VGM3, label="開館50周年（2023年）", ans=True)
S("z", "think", "でも、どうしてポケモンなのだ？\n美術館とゲームは、遠い気がするのだ。", VGM3, label="開館50周年（2023年）")
S("m", "normal", "鍵は日本よ。ゴッホは、日本の\n浮世絵が大好きだったの。", EISEN, label="ゴッホが浮世絵を写した「花魁」", say="鍵は、にほんよ。ゴッホは、日本の浮世絵が大好きだったの。")
S("m", "normal", "パリにいたころ、浮世絵を何百枚も\n集めていて、今も美術館が持っているわ。", EISEN, label="ゴッホが浮世絵を写した「花魁」")
S("m", "normal", "歌川広重の梅の木の版画を、\n油絵でそっくり写したりもしたの。", PLUM2, label="広重の版画とゴッホの模写")
S("m", "normal", "見比べると、ゴッホのほうが空の赤が強くて、\n色がずっとあざやかなのよ。", PLUM2, label="広重の版画とゴッホの模写")
S("z", "surprise", "まわりの漢字の飾りまで\nまねしているのだ。", PLUM, label="ゴッホの模写（1887年）", mark=[0.1, 0.5, 0.12])
S("m", "normal", "雨の中の橋の絵も写したわ。\n細い線で雨を描く、広重の描き方ね。", RAIN2, label="広重の版画とゴッホの模写")
S("m", "normal", "パリの画材屋さんの主人を描いた絵では、\n後ろの壁を、浮世絵で埋めつくしたほどよ。", TANGUY, label="タンギー爺さん（1887年）")
S("m", "normal", "南フランスのアルルに移ったときは、\n日本のように美しい土地だと手紙に書いたの。", LANGLOIS, label="アルルの跳ね橋（1888年）")
S("m", "normal", "弟のテオには、自分の仕事はすべて\n日本の美術がもとになっている、とまで書いたわ。", THEO, label="弟のテオ（1887年）", big="すべて日本の美術がもと", bf="mincho")
S("z", "think", "ゴッホといえば、耳を切った\n画家なのだ。帽子の絵も、そのあとなのだ？", EAR, label="耳に包帯をした自画像（1889年）")
S("m", "normal", "ちがうの。耳を傷つけたのは、\n南フランスのアルルにいた1888年の12月。", EAR, label="耳に包帯をした自画像（1889年）")
S("m", "normal", "灰色のフェルト帽の自画像は、その1年ほど前、\nパリで描いたものよ。耳はまだ無事ね。", FELT, label="灰色のフェルト帽の自画像（1887年）")
S("m", "normal", "ちなみに、耳に包帯をした自画像の\n後ろの壁にも、浮世絵がかかっているの。", EAR, label="後ろの壁に浮世絵", mark=[0.78, 0.35, 0.2])
S("m", "normal", "館長は、ポケモンは日本の絵の文化の\n象徴だから、組む意味がある、と話したの。", VGM, label="館長の説明")
S("m", "normal", "目的は、若い世代にゴッホを知ってもらうこと。\nポケモンの宣伝ではない、ともね。", VGM, label="館長の説明")
S("m", "normal", "ポケモン社の担当者も、ポケモンとゴッホの名画は、\n発想のもとが強くつながっている、と話したわ。", "commons:International Pokémon logo.svg", label="ポケモン社の説明")
S("z", "think", "日本の絵を好きになった画家と、\n日本で生まれたポケモン、なのだ。", PAIR, label="自画像とピカチュウ")

# ---- 第二層 ----
T("第二層", "ポケモンになった、6枚の名画", "第二層　6枚の名画", font="reggae",
  x={"head": "ゴッホ美術館に\nポケモン版の名画が\n6枚並んだ", "img": [SUN, "art:192"], "bubble": "キマワリがいるのだ", "who": "z",
     "post": "2023年9月28日から2024年1月7日まで、ゴッホ美術館にポケモン版の名画が6枚並びました。ひまわりにはキマワリ、寝室にはカビゴンとゴンベ、カラスのいる麦畑にはアーマーガア。どれもポケモン社のイラストレーターが描いた新しい絵です。あなたならどの絵をポケモンにしますか？"})
S("m", "normal", "展示は、2023年9月28日から、\n2024年1月7日まで開かれたわ。", VGM2, label="2023年9月28日〜2024年1月7日")
S("m", "normal", "9月12日の予告の動画では、ひまわり畑を、\nピカチュウとイーブイが走っていたの。", "row:art:25|ピカチュウ;art:133|イーブイ", label="2023年9月12日の予告")
S("m", "normal", "最後に、ひまわりの間から\nキマワリが顔を出す、という流れね。", "art:192", label="キマワリ")
S("m", "normal", "ポケモン社のイラストレーターたちが、\nゴッホの名画をもとに、新しく6枚を描いたの。", "row:" + SUN + "|ひまわり;" + BED + "|寝室;" + CROWS + "|カラスのいる麦畑", label="もとになったゴッホの名画（一部）")
S("m", "normal", "まず、ひまわり。花びんのひまわりの中に、\nキマワリがまぎれこんでいるの。", "row:" + SUN + "|ゴッホ「ひまわり」>art:192|キマワリ", label="ひまわり → キマワリ")
S("m", "normal", "ゴッホの寝室の絵では、ベッドに\nカビゴンが寝ころんで、ゴンベもいるわ。", "row:" + BED + "|ゴッホ「寝室」;art:143|カビゴン;art:446|ゴンベ", label="寝室 → カビゴンとゴンベ")
S("z", "happy", "ベッドがつぶれそうなのだ。\nカビゴンは重さ460キロなのだ。", "art:143", label="カビゴン（重さ460kg）")
S("m", "normal", "この寝室は、ゴッホがアルルで借りた\n黄色い家の、2階の部屋なの。", YELLOW, label="アルルの黄色い家", mark=[0.33, 0.45, 0.1])
S("m", "normal", "カラスのいる麦畑には、\nカラスのポケモン、アーマーガア。", "row:" + CROWS + "|カラスのいる麦畑>art:823|アーマーガア", label="カラスのいる麦畑 → アーマーガア")
S("m", "normal", "麦畑の絵は、ゴッホが亡くなった\n1890年の夏に描かれたものよ。", CROWS, label="カラスのいる麦畑（1890年）")
S("m", "normal", "麦わら帽子をかぶった自画像は、\nイーブイになったわ。", "row:" + STRAW + "|麦わら帽子の自画像>art:133|イーブイ", label="麦わら帽子の自画像 → イーブイ")
S("m", "normal", "絵を描いている自画像は、\n絵かきのポケモン、ドーブルね。", "row:" + PAINTER + "|画家としての自画像>art:235|ドーブル", label="画家としての自画像 → ドーブル")
S("m", "normal", "そして6枚目が、灰色のフェルト帽の自画像。\nこれが、ピカチュウになったの。", PAIR, label="灰色のフェルト帽 → ピカチュウ", ans=True)
S("z", "think", "ピカチュウの耳が、\n帽子の横から出ているのだ。", CARD, label="帽子をかぶったピカチュウのカード", mark=[0.3, 0.27, 0.12])
S("m", "normal", "そう。このピカチュウを描いたのは、\nイラストレーターの木村直代さんよ。", CARD, label="絵　木村直代さん", say="そう。このピカチュウを描いたのは、イラストレーターの、きむらなおよさんよ。")

# ---- 第三層 ----
T("第三層", "開幕の日、美術館の売店で", "第三層　開幕の日", font="potta",
  x={"head": "ゴッホ美術館の開幕日\n警備員いわく\n「フェルメール展より混んでいる」", "img": [VGM2], "bubble": "そんなにいたのだ", "who": "z",
     "post": "2023年9月28日、ポケモン展が始まったゴッホ美術館には人が押し寄せ、売店で商品を取り合う動画が広まりました。警備員は、同じ年に近くで開かれた大人気のフェルメール展より混んでいる、と話したと報じられています。美術館は次の日から、商品を1人1点までにしました。"})
S("m", "normal", "このカードは、お店で売られたわけではないの。\n美術館の中で、もらえたのよ。", CARD, label="美術館でもらえたカード")
S("m", "normal", "カードの名前は、灰色のフェルト帽のピカチュウ。\nほかのカードと同じように遊べる、本物よ。", CARD, label="Pikachu with Grey Felt Hat")
S("m", "normal", "ポケモンカードの、特別に配られるプロモカードで、\n番号は085なの。", CARD, label="プロモカード 085", say="ポケモンカードの、特別に配られるプロモカードで、番号は、ゼロ、ハチ、ゴ、なの。")
S("m", "normal", "6歳以上向けの冊子を持って、館内の絵を回って\n課題を解くと、出口で1枚もらえたの。", VGM2, label="館内の課題を解くと1枚")
S("m", "normal", "冊子の名前は、ポケモン・アドベンチャー。\nオランダ語と英語で用意されていたの。", VGM2, label="冊子「ポケモン・アドベンチャー」")
S("m", "normal", "カードは封をしたまま、\n1人に1枚だけ渡されたわ。", CARD, label="出口で1人1枚")
S("m", "normal", "しかも、18歳未満は入館料が無料。\n大人は、入館料を払って入るのね。", VGM2, label="18歳未満は入館無料")
S("z", "happy", "子どもは、ただで\nピカチュウがもらえるのだ。", CARD, label="帽子をかぶったピカチュウのカード")
S("m", "normal", "ほかに、アメリカやイギリスのポケモンセンターの\n通販でも、限定の商品を買うと付いてきたわ。", TCG, label="ポケモンセンターの通販")
S("m", "normal", "そして2023年9月28日、展示が始まった日。\n美術館に、人が押し寄せたの。", VGM, label="2023年9月28日 開幕", big="開幕の日に大混乱", bf="rampart")
S("m", "normal", "売店で、限定の商品を取り合う人たちの\n動画が、ネットに広まったわ。", VGM3, label="売店で商品の取り合い")
S("m", "normal", "警備員は、フェルメール展より\n混んでいる、と話したと報じられたの。", VERMEER, label="フェルメール「牛乳を注ぐ女」")
S("z", "think", "フェルメールって、ゴッホとは\nちがう画家なのだ？", VERMEER, label="フェルメール「牛乳を注ぐ女」")
S("m", "normal", "17世紀のオランダの画家よ。その年の春、\n近くの国立美術館で、大きな展覧会があったの。", VERMEER, label="17世紀のオランダの画家")
S("m", "normal", "チケットが売り切れるほどの人気だった、\nその展覧会よりも混んでいた、ということね。", VERMEER, label="2023年春のフェルメール展")
S("m", "normal", "次の日の9月29日、ポケモン社は\n通販のお客さんに謝ったの。", TCG, label="2023年9月29日 謝罪")
S("m", "normal", "通販の商品は、あまりの人気で\nすべて売り切れました、とね。", TCG, label="通販の商品はすべて売り切れ")
S("m", "normal", "美術館も、売店の商品は\n1人1点までと決めたわ。", VGM2, label="売店の商品は1人1点まで")

# ---- 第四層 ----
T("第四層", "出口で配るカードに、値段がついた", "第四層　転売と配布中止", font="reggae",
  x={"head": "美術館で無料のピカチュウ\nネットでは最高で\n約600ドルに", "img": [CARD], "bubble": "高すぎるのだ", "who": "z",
     "post": "ゴッホ美術館の館内の課題を解くともらえたピカチュウのカードは、ネットで80ユーロを超え、最高で約600ドルの値がつきました。美術館は2023年10月13日を最後に、館内での配布をやめました。理由は、ごく一部の人たちが望ましくない状況を作った、と発表しています。"})
S("m", "normal", "問題は、カードのほうよ。\nすぐにネットで、高い値段がついたの。", EBAY, label="ネットの売り買い")
S("m", "normal", "イギリスのガーディアン紙によれば、\nネットでは80ユーロを超えたわ。", EBAY, label="80ユーロ超（約1万3000円）")
S("m", "normal", "高いものでは、\n約600ドルの値がついた、と報じられたの。", VGM, label="最高で約600ドル", big="最高で約600ドル", bf="rampart", ans=True)
S("z", "shock", "美術館でもらえるカードが、\n600ドルなのだ！？", CARD, label="帽子をかぶったピカチュウのカード")
S("m", "normal", "カードを目当てに美術館に来て、\nもらったカードを売る人たちが現れたの。", MPL, label="オランダの売り買いのサイト")
S("m", "normal", "美術館の出口の外で、もらったばかりの\nカードを買い取ろうとする人もいたわ。", VGM, label="美術館の出口の外")
S("z", "sad", "絵を見に来た子どもが、\nかわいそうなのだ。", CARD, label="帽子をかぶったピカチュウのカード")
S("m", "normal", "10月12日、ポケモン社は、通販でカードの商品を\n30ドル以上買うと付ける、と発表したの。", TCG, label="2023年10月12日 ポケモン社")
S("m", "normal", "そして美術館は、10月13日を最後に、\n館内でカードを配るのをやめたわ。", VGM2, label="2023年10月13日 配布をやめた", big="カードの配布中止", bf="mincho", ans=True)
S("m", "normal", "翌日の発表で、美術館とポケモン社は、\nこう書いたの。", VGM2, label="美術館とポケモン社の発表")
S("m", "normal", "ごく一部の人たちが、\n望ましくない状況を作った。", VGM2, label="美術館とポケモン社の発表", big="望ましくない状況", bf="mincho")
S("m", "normal", "来館者と職員の安全を、\nとても重く受け止めている、とね。", VGM2, label="美術館とポケモン社の発表")
S("m", "normal", "来館者が、安全に楽しく絵を見られるように、\nカードを配るのはやめる、という発表だったわ。", VGM2, label="美術館とポケモン社の発表")
S("z", "think", "これで、さわぎは\nおさまったのだ？", VGM2, label="ゴッホ美術館")
S("m", "normal", "外のさわぎはね。でも、本当の問題は、\n美術館の中にもあったの。", VGM, label="美術館の中で")

# ---- 第五層 ----
T("第五層", "カードの箱は、どこへ消えた", "第五層　職員の処分", font="fude",
  x={"head": "ピカチュウのカードをめぐり\nゴッホ美術館の職員が\n少なくとも4人停職", "img": [CARD], "bubble": "職員までなのだ", "who": "z",
     "post": "2024年1月、オランダの新聞ヘット・パロールが、ゴッホ美術館の職員が少なくとも4人、ピカチュウのカードをめぐって停職になったと報じました。カードがいつ手に入るかを来館者に教えたり、1人はカードを1箱持ち出したりしたと報じられています。美術館は、行動規範に反したと説明しました。"})
S("m", "normal", "2024年1月24日、アムステルダムの新聞、\nヘット・パロールが報じたの。", CANAL, label="2024年1月24日の報道", kana="ニセンニジュウヨ'ネン/イチガツ'/ニジュウヨッカ'、アム_ステ'ルダムノ/シンブン'、ヘットパロ'オルガ/ホオジタ'ノ")
S("m", "normal", "ゴッホ美術館の職員が、少なくとも4人、\nカードをめぐって停職になっていた、と。", VGM, label="職員が少なくとも4人停職", big="職員が停職", bf="mincho", ans=True)
S("z", "surprise", "美術館で働く人たちが、\nいったい何をしたのだ？", VGM, label="職員が少なくとも4人停職")
S("m", "normal", "報道によると、警備員や、荷物の預かり所、\nチケット売り場で働く人たちよ。", VGM2, label="警備員・荷物預かり所・チケット売り場")
S("m", "normal", "カードがいつ手に入るかを、\n来館者に前もって教えていたというの。", CARD, label="カードの情報を教えていた", say="カードがいつ、てにはいるかを、来館者に前もって教えていたというの。")
S("m", "normal", "そして1人は、カードを1箱、\n持ち出していたと報じられたわ。", CARD, label="カードを1箱持ち出した", big="カードを1箱", bf="rampart")
S("z", "shock", "1箱って、1枚どころでは\nないのだ！", CARD, label="カードを1箱持ち出した")
S("m", "normal", "中には、25年も勤めてきた\n職員もいたと伝えられているの。", VGM3, label="勤めて25年の職員も")
S("z", "sad", "ふだんは、来館者を守る\n側の人たちなのだ。", VGM3, label="警備員・荷物預かり所・チケット売り場")
S("m", "normal", "停職は、2023年の12月の半ば。\nこの人たちは、美術館を去ったわ。", VGM3, label="2023年12月 停職")
S("m", "normal", "報道が出たのは、展示が終わった2週間あと。\nそれまで、外には知られていなかったのね。", VGM3, label="2024年1月7日 展示が終わった")
S("m", "normal", "美術館は、決められた手順と\n行動規範に反した、とだけ説明したの。", VGM, label="美術館の説明")
S("m", "normal", "1人1人のことは話さないので、\nくわしいことは言えない、ともね。", VGM, label="美術館の説明")
S("z", "think", "外の転売よりも、中の人の\nほうがショックなのだ。", VGM, label="ゴッホ美術館")

# ---- 最深層 ----
T("最深層", "ゴッホが日本に見ていたもの", "最深層　その後のピカチュウ", font="mincho",
  x={"head": "配布をやめたピカチュウ\n2024年2月から\nオランダのお店でも配られた", "img": [CARD], "bubble": "やっと手に入るのだ", "who": "z",
     "post": "ゴッホ美術館が配布をやめたピカチュウのカードは、2024年2月10日からオランダのおもちゃ屋などで、ポケモンの商品を29.99ユーロより多く買うともらえるようになりました。いっぽうゴッホは、日本の美術を学べば、より陽気で幸せにならずにはいられない、と手紙に書いています。"})
S("m", "normal", "このカードは、そのあと\nどうなったと思う？", CARD, label="帽子をかぶったピカチュウのカード")
S("z", "think", "もう手に入らなくて、\nもっと高くなったのだ？", CARD, label="帽子をかぶったピカチュウのカード")
S("m", "normal", "逆よ。刷り直されたの。2024年2月10日から、\nオランダのおもちゃ屋さんなどでも配られたわ。", TCG, label="2024年2月10日から お店で配布", ans=True)
S("m", "normal", "ポケモンの商品を、29.99ユーロより多く\n買うと、1枚もらえる、という形ね。", TCG, label="29.99ユーロより多く買うと1枚")
S("z", "happy", "それなら、美術館の出口で\n取り合わなくていいのだ。", CARD, label="お店で配布")
S("m", "normal", "最後に、ゴッホの手紙をもう1つ。\n1888年の9月、弟のテオに書いたものよ。", YELLOW, label="アルルの黄色い家（1888年）")
S("m", "normal", "日本の美術を学べば、より陽気で、\n幸せにならずにはいられない。", ALMOND, label="ゴッホ「花咲くアーモンドの枝」", big="陽気で幸せに", bf="mincho", say="日本の美術をまなべば、より陽気で、幸せにならずにはいられない。")
S("m", "normal", "美術館とポケモン社の発表でも、\nこの手紙が引かれていたの。", ALMOND, label="ゴッホ「花咲くアーモンドの枝」")
S("m", "normal", "同じ手紙で、ゴッホは日本の画家のことを\nこう書いているの。", THEO, label="弟のテオへの手紙（1888年9月）")
S("m", "normal", "日本の画家は、たった一本の草の葉を\n研究することに、時間を使う、とね。", PLUM, label="ゴッホの模写（1887年）")
S("z", "think", "草1本を、ずっと\n見つめるのだ。", PLUM, label="ゴッホの模写（1887年）")
S("m", "normal", "小さな生き物を、じっくり観察する。\nなんだか、ポケモンの図鑑みたいよね。", "art:192", label="キマワリ")
S("z", "sad", "陽気で幸せになるはずが、\n取り合いになってしまったのだ。", ALMOND, label="ゴッホ「花咲くアーモンドの枝」")

# ---- まとめ ----
S("m", "think", "今日の答え。美術館で無料で配ったカードに、\nネットで何万円もの値段がついた。", PAIR, sec="まとめ", label="自画像とピカチュウ")
S("m", "normal", "その値段が、外の転売屋だけでなく、\n美術館の中の人まで動かしてしまったのね。", VGM, label="ゴッホ美術館")
S("z", "think", "ピカチュウの帽子1つで、\n美術館がひっくり返ったのだ。", CARD, label="帽子をかぶったピカチュウのカード")
S("m", "normal", "あなたなら、このカードをもらったら、\n売る？　それとも飾る？", CARD, label="帽子をかぶったピカチュウのカード")

# ---- 英語名 ----
T("おまけ", "今日のポケモンの英語名", "今日のポケモンの英語名", font="hachi")
S("m", "happy", "今日の英語名は、ゴッホの絵に\n入ったポケモンから3匹よ。", "row:art:192|キマワリ;art:235|ドーブル;art:823|アーマーガア", label="ゴッホの絵に入ったポケモン", lf="hachi")
S("m", "happy", "まず、キマワリ。\nサンフローラ。", "art:192", label="Sunflora（サンフローラ）", lf="hachi")
S("m", "normal", "sunは、太陽。floraは、ラテン語で\n花や植物を表す言葉よ。", "art:192", label="Sunflora（サンフローラ）", lf="hachi",
  ety=["Sunflora（サンフローラ）", "英語　sun（太陽）＋ラテン語　flora（花・植物）"],
  say="サンは、太陽。フローラは、ラテン語で花や植物を表す言葉よ。")
S("m", "happy", "次は、ドーブル。\nスミアグル。", "art:235", label="Smeargle（スミアグル）", lf="hachi")
S("m", "normal", "smearは、絵の具を塗りつけること。\nそこに、犬のビーグルを合わせた名前ね。", "art:235", label="Smeargle（スミアグル）", lf="hachi",
  ety=["Smeargle（スミアグル）", "英語　smear（塗りつける）＋beagle（犬のビーグル）"],
  say="スミアは、絵の具を塗りつけること。そこに、犬のビーグルを合わせた名前ね。")
S("m", "happy", "最後は、アーマーガア。\nコーヴィナイト。", "art:823", label="Corviknight（コーヴィナイト）", lf="hachi")
S("m", "normal", "corvusは、ラテン語でカラス。\nknightは、よろいを着た騎士のことよ。", "art:823", label="Corviknight（コーヴィナイト）", lf="hachi",
  ety=["Corviknight（コーヴィナイト）", "ラテン語　corvus（カラス）＋英語　knight（騎士）"],
  say="コルヴスは、ラテン語でカラス。ナイトは、よろいを着た騎士のことよ。")
S("m", "normal", "今日出てきたポケモンの英語名は、\n英単語帳サイト「もんすぺ！」でも調べられるわ。", "site:", label="「もんすぺ！」で検索")
S("m", "happy", "もんすぺ！には、ポケモンの雑学のコラムもあるの。\n動画の続きみたいに読めるわよ。", "site:", label="「もんすぺ！」雑学コラムもあります")
S("z", "happy", "今日の採掘はここまでなのだ。\nチャンネル登録もよろしくなのだ。", "site:", label="「もんすぺ！」で検索")
L.append({"type": "ed"})

script = {
    "no": 12,
    "title": "なぜゴッホ美術館の職員は、ピカチュウのカードで停職になったのか？",
    "neta": "ゴッホ美術館のピカチュウで職員が停職",
    "thumb": {"file": "thumbnail.png", "layout": "v2", "pre": "ゴッホ美術館の職員が", "big": ["カードで", "停職"], "hl": 1, "hl_color": "red",
              "fonts": ["mincho", "mincho"], "pre_font": "maru", "pre_size": 62,
              "back": VGM, "photo": CARD, "photo_label": "帽子をかぶったピカチュウ", "chara": None},
    "lines": L,
}
here = os.path.dirname(os.path.abspath(__file__))
json.dump(script, open(os.path.join(here, "script.json"), "w"), ensure_ascii=False, indent=1)
n = sum(len(l.get("t", "").replace("\n", "")) for l in L)
print("行数", len(L), "字幕の字数", n)
