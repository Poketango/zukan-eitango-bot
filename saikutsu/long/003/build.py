import json, os, sys
# 第003回 台本（化石博物館と、プテラの名をもらった翼竜）
L = []
def S(w, face, t, img=None, **kw):
    d = {"w": w, "face": face, "t": t}
    if img: d["img"] = img
    d.update(kw); L.append(d)
def T(sub, t, sec=None):
    L.append({"type": "title", "sub": sub, "t": t, **({"sec": sec} if sec else {})})

PTERA = "art:142"
# コールドオープン
S("z", "happy", "ねえめたん！\nプテラの名前をもらった\n本物の翼竜がいるって知ってたのだ？", PTERA, sec="ポケモン雑学採掘所")
S("m", "think", "知ってる。その翼竜、いまじゃ\n「世界で最初に見つかった翼竜の、\n子どもだった」って言われてるけどね。", "sil:wiki:en:Aerodactylus^sil:wiki:en:Pterodactylus")
S("z", "shock", "えっ。", big="えっ。")
L.append({"type": "op", "w": "m", "t": "ポケモンの深い雑学を掘り出す、\nポケモン雑学採掘所。", "say": "ポケモンの深い雑学を掘り出す、ポケモン雑学採掘所。"})

# 導入
S("m", "normal", "今日もほこりっぽいわね。\nあ、この岩、渦巻きの模様が入ってる。", "wiki:en:Ammonoidea", sec="導入　昔のプテラ")
S("z", "proud", "化石なのだ！\n化石といえばプテラなのだ。", PTERA)
S("z", "proud", "ダイヤモンド・パールのころ、プテラは\nきあいのタスキを持って先発に出てたのだ。", "dp_lead.png",
  cap="ダイヤモンド・パールの通信対戦（海外版・2008年）", bgm="battle")
S("z", "proud", "ちょうはつとステルスロックで、\n相手の作戦をつぶしまくっていたのだ。", "dp_rockslide.png",
  ety=["第4世代の先発プテラの型", "きあいのタスキ　ちょうはつ／ステルスロック／ストーンエッジ／じしん"])
S("m", "think", "ステルスロックは、交代で出てきた相手に\n毎回ダメージを与える岩をまく技ね。",
  "table:ステルスロック=交代で出てきた相手に毎回ダメージ;ちょうはつ=相手に補助技を使わせない;きあいのタスキ=満タンから一撃では倒れない", label="技と持ち物")
S("m", "think", "でもそれ、もう20年近く前の話でしょ。", "dp_lead.png", cap="ダイヤモンド・パールの通信対戦（海外版・2008年）")
S("m", "normal", "ブラック・ホワイトで、対戦の前に\nお互いの6匹を見せ合うルールが入ったの。", "wiki:en:Pokémon_Black_and_White")
S("m", "normal", "それから、先発の読み合いで得をする役は\n価値が下がったのよ。", "wiki:en:Pokémon_Black_and_White")
S("m", "normal", "英語圏の対戦コミュニティ、Smogonの格付けでも、\nプテラはOUからRUまで落ちたわ。",
  "tiers:upto:OU,UU,RU", say="英語圏の対戦コミュニティ、スモーゴンの格付けでも、プテラはオーユーからアールユーまで落ちたわ。")
S("z", "think", "OUとかRUって、何の階級なのだ？", "tiers:upto:OU,UU,RU", say="オーユーとかアールユーって、何の階級なのだ？")
S("m", "normal", "使われている割合で分けた階級よ。\nOUはオーバーユーズド、よく使われるポケモン。", "tiers:OU",
  say="使われている割合で分けた階級よ。オーユーはオーバーユーズド、よく使われるポケモン。")
S("m", "normal", "組まれたチームのうち、だいたい4.5パーセント以上に\n入っているポケモンがOUになるの。", "tiers:OU",
  say="組まれたチームのうち、だいたい4.5パーセント以上に入っているポケモンがオーユーになるの。")
S("m", "happy", "22チームに1チームくらいね。", "tiers:OU")
S("m", "normal", "OUから外れたポケモンだけでUUの対戦をして、\nそこでまた使われている割合を数えるの。", "tiers:UU",
  say="オーユーから外れたポケモンだけでユーユーの対戦をして、そこでまた使われている割合を数えるの。")
S("m", "normal", "UUはアンダーユーズド、RUはレアリーユーズド。\nつまり、めったに使われないって意味。", "tiers:RU",
  say="ユーユーはアンダーユーズド、アールユーはレアリーユーズド。つまり、めったに使われないって意味。")
S("m", "normal", "階級は、何か月かごとの使われ方で\n入れかわるの。", "tiers:RU")
S("m", "normal", "いちばん上には、強すぎてOUで禁止された\n伝説のポケモンなどを集めたUbersもあるわ。", "tiers:Ubers",
  say="いちばん上には、強すぎてオーユーで禁止された伝説のポケモンなどを集めたウーバーズもあるわ。")
S("z", "shock", "プテラが、めったに使われない側に…", "tiers:RU", big="めったに使われない側")
S("z", "sad", "見せ合いさえなければ、\n今でもプテラは最強だったのだ…", PTERA, label="あの頃は…")
S("m", "happy", "はいはい。今日はその化石の話。\nポケモンの化石と本物の化石を並べた展示があるの。",
  "csearch:Pokémon Fossil Museum^wiki:en:Pokémon_Fossil_Museum^wiki:en:National_Museum_of_Nature_and_Science", v="tsun", bgm="oyaoya")
S("m", "happy", "そこから、化石ポケモンのモデルになった古生物を、\nまとめて掘っていくわよ。", "row:art:408|ズガイドス;art:697|ガチゴラス;art:347|アノプス;art:345|リリーラ;art:142|プテラ")
S("z", "think", "古生物？　恐竜じゃないのだ？", "row:art:408|ズガイドス;art:697|ガチゴラス;art:347|アノプス;art:345|リリーラ;art:142|プテラ")
S("m", "normal", "恐竜もいるけど、海の生き物や翼竜もいるの。\nだから、大昔の生き物をまとめて古生物って呼ぶのよ。", "row:art:408|恐竜;art:697|恐竜;art:347|海の生き物;art:345|海の生き物;art:142|翼竜")
T("本日の採掘", "化石ポケモンのモデル、一挙解説")

# 第一層
T("第一層", "ポケモン化石博物館", sec="第一層　ポケモン化石博物館")
S("m", "normal", "ポケモン化石博物館。\n2021年に、北海道の三笠市立博物館から始まったの。",
  "wiki:ja:三笠市立博物館^wiki:en:Mikasa_City_Museum", say="ポケモン化石博物館。2021年に、北海道の、みかさしりつはくぶつかんから始まったの。")
S("m", "normal", "日本の15か所を回って、2026年の5月からは\nアメリカのシカゴにあるフィールド自然史博物館でやってる。",
  "csearch:Pokémon Fossil Museum^wiki:en:Field_Museum_of_Natural_History", cap="フィールド自然史博物館（シカゴ）",
  say="日本の15か所を回って、にせんにじゅうろくねんの5月からは、アメリカのシカゴにあるフィールド自然史博物館でやってる。")
S("z", "normal", "ポケモンの会社が考えた企画なのだ？", "csearch:Pokémon Fossil Museum^wiki:en:Field_Museum_of_Natural_History")
S("m", "normal", "ちがうの。言い出したのは、三笠市立博物館の\n学芸員だった相場大佑さん。",
  "wiki:ja:三笠市立博物館^wiki:en:Mikasa_City_Museum", say="ちがうの。言い出したのは、みかさしりつはくぶつかんの、がくげいいんだった、あいばだいすけさん。")
S("m", "normal", "学芸員は、博物館で資料を研究して\n展示を作る専門家ね。", "wiki:en:Ammonoidea", say="がくげいいんは、博物館で資料を研究して展示を作る専門家ね。", cap="三笠市立博物館はアンモナイトの展示数が日本一")
S("m", "happy", "子どものころ、ポケモンに似た生き物を\n図鑑で探していたのが、科学者になった原点。", "row:art:140|カブト;wiki:en:Horseshoe_crab|カブトガニ")
S("m", "happy", "それで、自分で株式会社ポケモンに\n企画を持ち込んだんだって。", "row:art:140|カブト;wiki:en:Horseshoe_crab|カブトガニ", say="それで、自分でかぶしきがいしゃポケモンに、企画を持ち込んだんだって。")
S("z", "happy", "熱いのだ。")
S("m", "normal", "東京会場の真ん中には、実物大のガチゴラスの\n骨格模型が立っていたの。", "art:697", label="ガチゴラス")
S("m", "normal", "その奥には、本物の肉食恐竜タルボサウルスの骨格。\nモンゴルで見つかった、ティラノサウルスの仲間よ。",
  "row:art:697|ガチゴラス;wiki:en:Tarbosaurus|タルボサウルス", ety=["Tarbosaurus（タルボサウルス）", "ギリシャ語　tarbos（恐れ）＋ sauros（トカゲ）"])
S("m", "think", "でも私がいちばん面白いと思ったのは、展示の解説。\nポケモンの「しんか」と本物の「進化」は別物だって。", "table:しんか=？;進化=？", label="同じ言葉なのに？")
S("z", "think", "同じ言葉なのに？", "table:しんか=？;進化=？", label="同じ言葉なのに？")
S("m", "normal", "カブトがカブトプスになるのは、\n1匹の体が変わることでしょ。", "row:art:140|カブト>art:141|カブトプス", label="ポケモンのしんか　1匹の体が変わる")
S("m", "normal", "本物の進化は、たくさんの生き物が\n何世代もかけて変わっていくこと。",
  "row:wiki:en:Eusthenopteron|魚>wiki:en:Tiktaalik|ティクターリク>wiki:en:Acanthostega|アカントステガ", label="本物の進化　何世代もかけて変わる")
S("m", "normal", "魚の仲間から両生類が生まれて、\n陸に上がったみたいにね。",
  "row:wiki:en:Eusthenopteron|魚>wiki:en:Tiktaalik|ティクターリク>wiki:en:Acanthostega|アカントステガ", label="本物の進化　何世代もかけて変わる")
S("m", "happy", "だからポケモンの「しんか」は、\n現実でいえば「成長」に近いんだって。", "row:art:140|カブト>art:141|カブトプス", label="しんか ≒ 成長")
S("z", "surprise", "たしかに、カブトが子どもを産んで、\n何世代もたってカブトプスになるわけじゃないのだ。", "row:art:140|カブト>art:141|カブトプス", label="しんか ≒ 成長")
S("m", "normal", "そう。で、ここからが本題。\n化石って、死んだ瞬間の姿しか残らないでしょ。", "wiki:en:Fossil")
S("m", "normal", "だから子どもの化石と大人の化石が、\n別々の場所で見つかると…", "wiki:en:Fossil")
S("m", "think", "同じ生き物なのに、\nちがう種類だと思われちゃうことがあるの。", "wiki:en:Fossil", big="同じ生き物に2つの名前")
S("z", "think", "ポケモンでいえば、カブトとカブトプスを…", "row:art:140|カブト;art:141|カブトプス")
S("z", "think", "しんかでつながらない、\n無関係のポケモンだと思うようなものなのだ。", "row:art:140|カブト;art:141|カブトプス")
S("z", "think", "…あれ、でもポケモン図鑑では\n番号がちがうのだ。", "row:art:140|No.140;art:141|No.141")
S("m", "happy", "そこがポケモンと現実のちがうところね。\n現実の生き物で、同じ種類の子どもと大人に…", "row:art:140|No.140;art:141|No.141")
S("m", "normal", "ちがう名前を付けたら、\nそれは「間違い」なのよ。", "row:art:140|No.140;art:141|No.141")

# 第二層 ズガイドス
T("第二層", "ズガイドスのモデルの恐竜", sec="第二層　ズガイドスのモデル")
S("m", "normal", "たとえばズガイドス。モデルは、頭のてっぺんの骨が\nドームみたいに分厚い恐竜、パキケファロサウルス。",
  "row:art:408|ズガイドス;wiki:en:Pachycephalosaurus|パキケファロサウルス",
  ety=["Pachycephalosaurus（パキケファロサウルス）", "ギリシャ語　pachys（厚い）＋ kephalē（頭）＋ sauros（トカゲ）"])
S("z", "normal", "ずつきポケモンなのだ。", "art:408", label="ずつきポケモン　ズガイドス")
S("m", "normal", "同じ時代の同じ地域からは、頭が平らでトゲトゲの\nドラコレックスも見つかってたの。", "csearch:Dracorex hogwartsia Childrens Museum Indianapolis^csearch:Dracorex holotype skull^wiki:en:Dracorex", label="ドラコレックス",
  ety=["Dracorex（ドラコレックス）", "ラテン語　draco（竜）＋ rex（王）"])
S("m", "normal", "頭の後ろに長いトゲがある\nスティギモロクもね。", "wiki:en:Stygimoloch", label="スティギモロク",
  ety=["Stygimoloch（スティギモロク）", "ギリシャ神話の冥界の川ステュクス ＋ 古代の神の名モロク"])
S("m", "normal", "どちらも、パキケファロサウルスとはちがう種類の恐竜として、\nそれぞれ名前が付いてたの。",
  "row:csearch:Dracorex hogwartsia Childrens Museum Indianapolis^csearch:Dracorex holotype skull|ドラコレックス;wiki:en:Stygimoloch|スティギモロク;wiki:en:Pachycephalosaurus|パキケファロサウルス", label="3つのちがう種類として名前が付いた")
S("m", "happy", "ドラコレックスの正式な名前は、\nドラコレックス・ホグワーツィア。", "csearch:Dracorex hogwartsia Childrens Museum Indianapolis^csearch:Dracorex holotype skull^wiki:en:Dracorex", label="Dracorex hogwartsia")
S("m", "happy", "ハリー・ポッターに出てくる魔法学校、\nホグワーツから取った名前よ。", "csearch:Dracorex hogwartsia Childrens Museum Indianapolis^csearch:Dracorex holotype skull^wiki:en:Dracorex", label="Dracorex hogwartsia",
  ety=[["Dracorex（ドラコレックス）", "ラテン語　draco（竜）＋ rex（王）"], ["hogwartsia（ホグワーツィア）", "魔法学校「ホグワーツ」から"]])
S("z", "happy", "かっこいい名前なのだ。", "csearch:Dracorex hogwartsia Childrens Museum Indianapolis^csearch:Dracorex holotype skull^wiki:en:Dracorex", label="Dracorex hogwartsia")
S("m", "think", "ところが2009年、ホーナーさんとグッドウィンさんという研究者が\n「この3つは同じ恐竜の成長段階だ」と発表したの。",
  "row:csearch:Dracorex hogwartsia Childrens Museum Indianapolis^csearch:Dracorex holotype skull|ドラコレックス;wiki:en:Stygimoloch|スティギモロク;wiki:en:Pachycephalosaurus|パキケファロサウルス", label="3つとも同じ恐竜？")
S("m", "normal", "ドラコレックスとスティギモロクは、\n子どもの頭の骨しか見つかってなくて…",
  "row:csearch:Dracorex hogwartsia Childrens Museum Indianapolis^csearch:Dracorex holotype skull|子どもだけ;wiki:en:Stygimoloch|子どもだけ;wiki:en:Pachycephalosaurus|大人だけ")
S("m", "normal", "パキケファロサウルスは、\n大人しか見つかってなかった。",
  "row:csearch:Dracorex hogwartsia Childrens Museum Indianapolis^csearch:Dracorex holotype skull|子どもだけ;wiki:en:Stygimoloch|子どもだけ;wiki:en:Pachycephalosaurus|大人だけ")
S("z", "surprise", "子どもだけの種類と、大人だけの種類…\nたしかに怪しいのだ。",
  "row:csearch:Dracorex hogwartsia Childrens Museum Indianapolis^csearch:Dracorex holotype skull|子どもだけ;wiki:en:Stygimoloch|子どもだけ;wiki:en:Pachycephalosaurus|大人だけ")
S("m", "normal", "若いうちは頭が平らで、後ろに大きなトゲがある。\n大人になるにつれてトゲが縮んで丸くなり…",
  "commons:Pachycephalosaurus_ontogeny_skulls_-_Museum_of_the_Rockies_-_2013-07-08.jpg", label="成長の順に並べた頭の骨", cap="ロッキー博物館（アメリカ）の展示")
S("m", "happy", "ドームが盛り上がっていく。\nそう考えると、3つがきれいに1列に並ぶの。",
  "commons:Pachycephalosaurus_ontogeny_skulls_-_Museum_of_the_Rockies_-_2013-07-08.jpg", label="成長の順に並べた頭の骨", cap="ロッキー博物館（アメリカ）の展示")
S("z", "proud", "まさにズガイドスから\nラムパルドへのしんかなのだ。", "row:art:408|ズガイドス>art:409|ラムパルド")
S("m", "normal", "2016年には、赤ちゃんの頭の骨にも、\n3つと同じ場所にこぶが並んでることが報告された。", "wiki:en:Pachycephalosaurus")
S("m", "think", "ただ、スティギモロクだけは見つかる地層が少し新しいから、\nパキケファロサウルスの子どもではない、", "wiki:en:Hell_Creek_Formation", cap="ヘルクリーク層（アメリカ）")
S("m", "think", "独立した種類だって考える研究者もいて、\n完全には決着してないの。", "wiki:en:Stygimoloch", label="スティギモロク")
S("z", "think", "化石の世界でも、\nしんかの途中かどうかで揉めてるのだ。", "row:art:408|ズガイドス>art:409|ラムパルド")

# 第三層 ガチゴラス
T("第三層", "ガチゴラスのモデルの恐竜", sec="第三層　ガチゴラスのモデル")
S("m", "normal", "じゃあ逆の話。ガチゴラスのモデルは、\nティラノサウルス。", "row:art:697|ガチゴラス;wiki:en:Sue_(dinosaur)|ティラノサウルス「スー」",
  ety=["Tyrannosaurus（ティラノサウルス）", "ギリシャ語　tyrannos（暴君）＋ sauros（トカゲ）"])
S("m", "normal", "そのティラノサウルスに、ナノティラヌスっていう\n小さめの仲間が本当にいたのかどうか、大論争があったの。", "wiki:en:Nanotyrannus", label="ナノティラヌス")
S("z", "think", "ナノ…小さいティラノなのだ？", "wiki:en:Nanotyrannus", label="ナノティラヌス",
  ety=["Nanotyrannus（ナノティラヌス）", "ギリシャ語　nanos（小人）＋ tyrannos（暴君）"])
S("m", "normal", "1940年代に見つかった頭の骨が始まりで、\n体が細くて、足が長い。", "wiki:en:Nanotyrannus", label="ナノティラヌス")
S("m", "normal", "長いあいだ、多くの研究者が\n「これはティラノサウルスの10代の子どもだ」って考えてた。",
  "row:wiki:en:Nanotyrannus|子ども？>wiki:en:Sue_(dinosaur)|ティラノサウルス", label="ティラノの子ども？")
S("m", "normal", "チゴラスが、ガチゴラスになる前の\n姿みたいにね。", "row:art:696|チゴラス>art:697|ガチゴラス")
S("z", "surprise", "違ったのだ？", "row:wiki:en:Nanotyrannus|子ども？>wiki:en:Sue_(dinosaur)|ティラノサウルス", label="ティラノの子ども？")
S("m", "normal", "去年の10月、世界でいちばん有名な科学雑誌の1つ、\nネイチャーに論文が出たの。",
  "paper:Nature（2025年10月30日）|Nanotyrannus and Tyrannosaurus/coexisted at the close of the Cretaceous|ナノティラヌスとティラノサウルスは白亜紀の終わりに共存していた")
S("m", "normal", "決め手は「決闘する恐竜」って呼ばれる化石。\nアメリカのモンタナ州で見つかったものよ。", "wiki:en:Dueling_Dinosaurs^csearch:Dueling Dinosaurs fossil", cap="決闘する恐竜")
S("m", "normal", "トリケラトプスと一緒に埋まっていた、\n肉食恐竜の全身の骨格なの。", "wiki:en:Dueling_Dinosaurs^csearch:Dueling Dinosaurs fossil", cap="決闘する恐竜")
S("m", "normal", "骨には、木の年輪みたいな成長の線が残ってて…",
  "row:wiki:en:Dendrochronology|木の年輪;csearch:bone histology growth lines|骨の成長線の例")
S("m", "happy", "それを数えると、死んだときは約20歳。\nもう成長が止まった大人だった。",
  "row:wiki:en:Dendrochronology|木の年輪;csearch:bone histology growth lines|骨の成長線の例", say="それを数えると、死んだときは、やく、にじゅっさい。もう成長が止まった大人だった。")
S("z", "think", "大人なのに小さかった…ってことは。", "wiki:en:Nanotyrannus", label="ナノティラヌス")
S("m", "normal", "ティラノの子どもじゃなくて、大人になってもティラノほど大きくならない、\nナノティラヌスという種類の恐竜だったの。", "wiki:en:Nanotyrannus", label="ナノティラヌス　大人でこの大きさ", big="子どもではなかった", bigcol="red")
S("m", "normal", "手はティラノよりずっと長くて、\n上腕と前腕を合わせたのと同じくらいあったの。",
  "row:wiki:en:Sue_(dinosaur)|ティラノサウルス;wiki:en:Nanotyrannus|ナノティラヌス", say="手はティラノよりずっと長くて、じょうわんと、ぜんわんを合わせたのと同じくらいあったの。")
S("m", "happy", "論文を書いた研究者は「これがティラノの子どもなら、\n背骨のある動物の成長の決まりを全部破ることになる」とまで言ってる。",
  "paper:Nature（2025年10月30日）|Nanotyrannus and Tyrannosaurus/coexisted at the close of the Cretaceous|ナノティラヌスとティラノサウルスは白亜紀の終わりに共存していた")
S("m", "normal", "さらに、ほかにもティラノの子どもとされてた骨格を調べ直して、\nナノティラヌスの2つ目の種類にしたの。", "wiki:en:Nanotyrannus")
S("m", "normal", "名前はナノティラヌス・レタエウス。\nギリシャ神話に出てくる忘れの川、レーテーから。", "wiki:en:Lethe", label="Nanotyrannus lethaeus",
  ety=["lethaeus（レタエウス）", "ギリシャ神話の忘却の川レーテーから"])
S("m", "happy", "何十年も忘れられてた種類、\nって意味なの。", "wiki:en:Lethe", label="Nanotyrannus lethaeus")
S("z", "surprise", "チゴラスだと思ってたら、しんかしない、\n大人でもその大きさのポケモンだったのだ。", "row:art:696|チゴラス>sil:art:697|しんかしない")
S("m", "happy", "うまいこと言うじゃない。ただ、2つ目の種類のほうは、\nまだ納得していない研究者もいるみたい。", "wiki:en:Nanotyrannus")
S("z", "normal", "子どもを大人と思ったり、\n大人を子どもと思ったり、忙しいのだ。", "row:csearch:Dracorex hogwartsia Childrens Museum Indianapolis^csearch:Dracorex holotype skull|子どもを別の種類に;wiki:en:Nanotyrannus|大人を子どもに")

# 第四層 アノプス
T("第四層", "アノプスのモデルの生き物", sec="第四層　アノプスのモデル")
S("m", "happy", "次はアノプス。\n進化するとアーマルドになるポケモンね。", "row:art:347|アノプス>art:348|アーマルド")
S("z", "normal", "アーマルドって、対戦ではあんまり見ないのだ。", "art:348", label="アーマルド")
S("m", "happy", "そこがいいのよ。アーマルドは、\n「こうそくスピン」で場を片づける役ができるの。", "art:348", label="アーマルド　こうそくスピン", v="amaama")
S("m", "normal", "こうそくスピンは、さっきのステルスロックみたいに\n相手がまいた岩を取り除く技。", "art:348", label="こうそくスピン　→　ステルスロックを片づける")
S("z", "think", "プテラがまいた岩を、アーマルドが片づける…\nめたんは、マイナーなポケモンの通な戦い方が好きなのだ。", "row:art:142|ステルスロックをまく;art:348|片づける")
S("m", "normal", "そういうこと。で、アノプスとアーマルドのモデルはアノマロカリス。\n5億年くらい前、カンブリア紀の海にいた生き物よ。", "row:art:347|アノプス;wiki:en:Anomalocaris|アノマロカリス", bgm="manabiya")
S("m", "normal", "この仲間は、成長どころか、体の部品がバラバラに見つかって、\nそれぞれちがう生き物の化石だと思われてたの。", "wiki:en:Anomalocaris", label="アノマロカリス")
S("z", "think", "部品？", "wiki:en:Anomalocaris", label="アノマロカリス")
S("m", "normal", "まず1892年、前についてるトゲトゲの腕が、\nエビの胴体だと思われた。",
  "row:csearch:Anomalocaris canadensis frontal appendage|前の腕の化石;wiki:en:Shrimp|エビ", say="まず、せんはっぴゃくきゅうじゅうに年、前についてるトゲトゲの腕が、エビの胴体だと思われた。")
S("m", "happy", "アノマロカリスって名前は、\n「奇妙なエビ」って意味なの。", "csearch:Anomalocaris canadensis frontal appendage", label="アノマロカリス＝奇妙なエビ",
  ety=["Anomalocaris（アノマロカリス）", "ギリシャ語　anomalos（奇妙な）＋ karis（エビ）"])
S("m", "normal", "次に、丸い口がクラゲだと思われて、\nペイトイアって名前が付いた。", "row:wiki:en:Peytoia|口の化石;wiki:en:Jellyfish|クラゲ",
  ety=["Peytoia（ペイトイア）", "カナダの地名ペイトー（山岳ガイドのビル・ペイトーにちなむ湖と山）から"])
S("m", "normal", "胴体はナマコだと思われて、ラガニア。", "row:csearch:Laggania cambria|胴体の化石;wiki:en:Sea_cucumber|ナマコ",
  ety=["Laggania（ラガニア）", "カナダの鉄道の駅名ラガン（今のレイク・ルイーズ）から"])
S("m", "think", "しかもラガニアは、あとで調べたら\n口と海綿が重なった化石だった。", "wiki:en:Sponge", label="海綿", say="しかもラガニアは、あとで調べたら、口と、かいめんが重なった化石だった。")
S("m", "normal", "海綿は、海の底にくっついて暮らす、\nスポンジみたいな動物ね。", "wiki:en:Sponge", label="海綿", say="かいめんは、海の底にくっついて暮らす、スポンジみたいな動物ね。")
S("z", "shock", "1匹の生き物が、\nエビとクラゲとナマコに分かれてたのだ！？",
  "row:wiki:en:Shrimp|エビ;wiki:en:Jellyfish|クラゲ;wiki:en:Sea_cucumber|ナマコ", big="エビとクラゲとナマコ")
S("m", "normal", "そう。1970年代の終わりから80年代にかけて、\nブリッグスさんやウィッティントンさんの研究で…", "wiki:en:Anomalocaris")
S("m", "happy", "腕と口がつながったままの化石が見つかって、\nやっと1匹の大きな生き物だってわかったの。", "wiki:en:Anomalocaris", label="ぜんぶ1匹の部品だった")
S("z", "think", "ポケモンでいえば、アノプスの腕と口と胴体が、\n別々のカセキから復元されたようなものなのだ。", "art:347", label="ツメのカセキ　→　アノプス")
S("m", "happy", "ちなみに、学名は先に付いた名前が優先される決まり。\nだから、クラゲと間違えられたペイトイアが…", "wiki:en:Peytoia", label="ペイトイア")
S("m", "happy", "その生き物の正式な名前として、\n今も使われてるの。", "wiki:en:Peytoia", label="ペイトイア")
S("z", "sad", "クラゲ扱いの名前が勝ったのだ…", "wiki:en:Jellyfish")

# 第五層 リリーラ
T("第五層", "リリーラのモデルの生き物", sec="第五層　リリーラのモデル")
S("m", "happy", "次はリリーラ。\n進化するとユレイドルになるわ。", "row:art:345|リリーラ>art:346|ユレイドル")
S("z", "normal", "ユレイドルも、対戦ではあんまり見ないのだ。", "art:346", label="ユレイドル")
S("m", "happy", "そこがいいの。とくせいの「よびみず」で、\nみずタイプの技を引き寄せて、効かなくできる。", "art:346", label="とくせい　よびみず", v="amaama")
S("m", "normal", "「じこさいせい」で体力を戻しながら、\nステルスロックもまける、守りの役ね。", "art:346", label="じこさいせい・ステルスロック")
S("z", "think", "めたん、ほんとに渋い戦い方が好きなのだ。", "art:346", label="ユレイドル")
S("z", "normal", "リリーラは、いわとくさタイプの、\n花みたいなポケモンなのだ。", "art:345", label="いわ・くさタイプ")
S("m", "normal", "分類はウミユリポケモン。\nでもモデルのウミユリは、植物じゃなくて動物なの。", "row:art:345|リリーラ;wiki:en:Crinoid|ウミユリ",
  ety=["Crinoidea（ウミユリのなかま）", "ギリシャ語　krinon（ユリ）＋ eidos（形）"])
S("m", "normal", "ウニやヒトデと同じ、\n棘皮動物の仲間。", "row:wiki:en:Crinoid|ウミユリ;wiki:en:Sea_urchin|ウニ;wiki:en:Starfish|ヒトデ", label="棘皮動物の仲間",
  say="ウニやヒトデと同じ、きょくひどうぶつの仲間。")
S("z", "shock", "花なのに動物なのだ！？", "wiki:en:Crinoid", big="花なのに動物")
S("m", "normal", "花びらに見えるのは腕で、\n流れてくるプランクトンを捕まえて食べるの。", "wiki:en:Crinoid", label="花びらに見えるのは腕")
S("m", "normal", "しかも子どものころは海を泳いでいて、\n大人になると岩にくっついて暮らす。", "wiki:en:Crinoid")
S("z", "think", "花びらが腕…触手みたいなのだ。", "art:345", label="リリーラ")
S("m", "happy", "まさにそれ。リリーラの中国語の名前は「触手百合」。\n日本語で読むと、しょくしゅゆり。", "art:345", big="触手百合",
  say="まさにそれ。リリーラの中国語の名前は、チューショウ・バイホー。日本語で読むと、しょくしゅゆり。")
S("z", "surprise", "し、触手…\nしかも百合なのだ。", "art:345", label="触手百合", bgm="gudaguda")
S("m", "think", "百合って、日本では女の子どうしの恋愛を\n表す言葉でもあるのよね。", "art:345", label="触手 ＋ 百合")
S("z", "happy", "触手に百合…\nインターネットが大喜びしそうな組み合わせなのだ。", "art:345", label="健全なポケモンです")
S("m", "normal", "変な想像しないの。\n名前の百合は、ただの花のユリよ。", "art:345", label="健全なポケモンです", v="tsun")
S("m", "normal", "ポケモンシールドの図鑑にも、\n花びらのような触手で獲物をからめとるって書いてある。", "art:345", label="ポケモンシールドの図鑑より")
S("m", "happy", "本物のウミユリの体のつくりにも合ってるし、\nいちばん正直な名前なのよ。", "wiki:en:Crinoid")
S("z", "normal", "…正直すぎるのも考えものなのだ。", "art:345", label="触手百合", v="hero")
S("m", "normal", "大昔の海にはウミユリが群れになって生えていて、\n岩がほとんどウミユリの化石でできた石灰岩もあるくらい。", "wiki:en:Crinoidal_limestone^csearch:crinoidal limestone", bgm="taai")
S("m", "normal", "今は主に深い海で生き残ってて、\n「生きた化石」って呼ばれてるの。", "wiki:en:Crinoid")
S("z", "think", "泳ぐ子どもと、くっついて動かない大人。\n化石だけ見たら、子どもと大人がちがう生き物だと思われそうなのだ。", "wiki:en:Crinoid")
S("m", "happy", "でしょ。リリーラがくさタイプなのは見た目からだろうけど、\n中身は立派な動物なのよ。", "art:345", label="中身は動物")

# 最深層 プテラ
T("最深層", "プテラの名前をもらった翼竜", sec="最深層　プテラの名前をもらった翼竜")
S("z", "normal", "…でも、プテラの話がまだなのだ。\n最初のやつ。", "sil:wiki:en:Aerodactylus^sil:wiki:en:Pterodactylus", bgm="kamikakushi")
S("m", "normal", "そうだった。2014年、ドイツのゾルンホーフェンっていう場所の石灰岩から出た\n小さな翼竜の化石に、新しい名前が付いたの。", "wiki:en:Solnhofen_Limestone", cap="ゾルンホーフェンの石灰岩（ドイツ）")
S("m", "happy", "「アエロダクティルス」。", "wiki:en:Aerodactylus", label="Aerodactylus（アエロダクティルス）",
  ety=["Aerodactylus（アエロダクティルス）", "ギリシャ語　aēr（空気）＋ daktylos（指）"])
S("z", "surprise", "プテラの英語名、\nエアロダクティルにそっくりなのだ！", "row:art:142|Aerodactyl;wiki:en:Aerodactylus|Aerodactylus", say="プテラの英語名、エアロダクティルにそっくりなのだ！")
S("m", "normal", "そっくりどころか、論文にはっきり\n「ポケモンのエアロダクティルにちなむ」って書いてあるの。",
  "paper:PLOS ONE（2014年）|名前の由来：Aero（空気）＋ dactylus（指）。/任天堂のポケモン Aerodactyl から取った。|論文の「名前の由来」の部分（日本語訳）")
S("z", "happy", "プテラが本物の科学に名前を残したのだ！\nやっぱりプテラは最強なのだ！", PTERA, big="やっぱり最強")
S("m", "think", "…問題はここから。その論文の題名、\n日本語にすると…",
  "paper:PLOS ONE（2014年）|Pterodactylus scolopaciceps … :/The Problem of Cryptic Pterosaur Taxa/in Early Ontogeny|論文の題名", v="hiso")
S("m", "think", "「成長の初めのころの翼竜に、\n見分けにくい種類がまぎれている問題」。",
  "paper:PLOS ONE（2014年）|Pterodactylus scolopaciceps … :/The Problem of Cryptic Pterosaur Taxa/in Early Ontogeny|成長の初めのころの翼竜に、見分けにくい種類がまぎれている問題")
S("z", "surprise", "今日の話そのままなのだ。", "wiki:en:Aerodactylus")
S("m", "normal", "アエロダクティルスとされた化石は6つ。\n全部、子どもなの。", "wiki:en:Aerodactylus", label="6つとも子ども")
S("z", "sad", "…いやな予感がするのだ。", "wiki:en:Aerodactylus", v="hero")
S("m", "normal", "2018年に、ベネットさんという研究者が\n「プテロダクティルスとほとんど区別がつかない」と反論して…", "row:wiki:en:Aerodactylus|アエロダクティルス;wiki:en:Pterodactylus|プテロダクティルス")
S("m", "normal", "2024年には、スマイスさんとアンウィンさんが、アエロダクティルスは\n「プテロダクティルス・アンティクウスの子ども」だと結論づけたの。",
  "row:wiki:en:Aerodactylus|子ども>wiki:en:Pterodactylus|大人", label="アエロダクティルス ＝ プテロダクティルスの子ども",
  ety=["antiquus（アンティクウス）", "ラテン語で「古い」"])
S("m", "normal", "プテロダクティルスは、約250年前に同じドイツで見つかった、\n世界で最初に見つかった翼竜よ。", "wiki:en:Pterodactylus", label="世界で最初に見つかった翼竜",
  ety=["Pterodactylus（プテロダクティルス）", "ギリシャ語　pteron（翼）＋ daktylos（指）"])
S("z", "shock", "プテラの名前の翼竜が…\nしんか前だったのだ…", "row:wiki:en:Aerodactylus|しんか前>wiki:en:Pterodactylus|しんか後", big="しんか前", say="プテラの名前の翼竜が…しんかまえだったのだ…")
S("m", "normal", "ちなみに、あの石灰岩から子どもの翼竜ばかり見つかる理由も、\n去年の研究でわかってきたの。", "wiki:en:Solnhofen_Limestone")
S("m", "normal", "生まれたばかりの翼竜の化石に、\n腕の骨が折れたあとがあって…", "csearch:Pterodactylus juvenile^wiki:en:Pterodactylus")
S("m", "normal", "嵐に巻き込まれて落ち、\nすぐ泥に埋まったらしいの。", "wiki:en:Storm")
S("m", "normal", "大人は嵐に強いから、\nあまり化石に残らなかった。", "wiki:en:Pterodactylus")
S("z", "think", "子どもの化石ばっかり見つかるから、大人と比べられなくて、\n子どもを新しい種類だと勘違いしやすいのだ。", "wiki:en:Solnhofen_Limestone")
S("m", "normal", "そういうこと。研究者は、何十年もかけて化石を見比べて、\nどれが子どもでどれが大人かを確かめてるの。", "wiki:en:Fossil")
S("z", "proud", "…つまり、プテラの翼竜はまだしんか前。\nこれからもっと強くなるってことなのだ。", PTERA, say="…つまり、プテラの翼竜はまだしんかまえ。これからもっと強くなるってことなのだ。")
S("m", "happy", "プテラはもうメガシンカしてるけどね。", "art:10042", label="メガプテラ", bgm="ichimono")
S("z", "proud", "メガプテラの話は、また今度なのだ！", "art:10042", label="メガプテラ")

# 英語名
T("おまけ", "今日のポケモンの英語名", sec="今日のポケモンの英語名")
S("m", "happy", "今日のポケモンの英語名。\n1匹目はプテラ。", PTERA, label="Aerodactyl（エアロダクティル）")
S("m", "normal", "エアロダクティル。", PTERA, label="Aerodactyl（エアロダクティル）")
S("m", "normal", "ギリシャ語の「空気」と「指」。翼竜の翼は、\nうんと長くのびた薬指で張られていたの。", "wiki:en:Pterosaur", label="翼は長い薬指で張られる")
S("m", "happy", "2匹目はアノプス。アノリス。", "art:347", label="Anorith（アノリス）")
S("m", "normal", "頭の「アノ」は、\nモデルのアノマロカリスから。", "art:347", label="Anorith（アノリス）")
S("m", "happy", "3匹目はリリーラ。リリープ。", "art:345", label="Lileep（リリープ）")
S("m", "normal", "ユリを表す英語のリリーが入ってるの。\n中身は動物だけどね。", "art:345", label="Lileep（リリープ）")
S("m", "normal", "今日出てきたポケモンの英語名は、\n英単語帳サイト「もんすぺ！」でも調べられるわ。", "site:", label="「もんすぺ！」で検索")
S("m", "happy", "もんすぺ！には、ポケモンの面白い雑学のコラムもあるの。\n動画の続きみたいに読めるわよ。", "site:", label="「もんすぺ！」雑学コラムもあります")
S("z", "happy", "今日の採掘はここまでなのだ。\nチャンネル登録もよろしくなのだ。", "site:", label="「もんすぺ！」で検索")
L.append({"type": "ed"})

sc = {"no": 3, "title": "化石ポケモンのモデルになった古生物、一挙解説！　プテラの名前をもらった翼竜も", "lines": L,
      "thumb": {"pre": "化石ポケモンの元ネタ", "big": ["古生物を", "一挙解説！"], "hl": 1, "main": "art:142",
                "back": "wiki:en:Pterodactylus", "row": ["art:408", "art:697", "art:347", "art:345"]}}
d = sys.argv[1]
os.makedirs(d, exist_ok=True)
json.dump(sc, open(os.path.join(d, "script.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(L), "行", sum(len(x.get("t", "")) for x in L), "字")
