import json, os
# 第005回 台本（ポケモンGOのARスキャンと、GPSが使えない戦場の位置推定）
L = []
def S(w, face, t, img=None, **kw):
    d = {"w": w, "face": face, "t": t}
    if img: d["img"] = img
    d.update(kw); L.append(d)
def T(sub, t, sec=None, **kw):
    L.append({"type": "title", "sub": sub, "t": t, **({"sec": sec} if sec else {}), **kw})

# 画像
GO = "wiki:en:Pokémon_Go"
CROWD = "commons:Pokémon Go players gathering at Mr.Mime spawn point in Pokémon GO PARK (Yokohama, 2017).jpg^" + GO
PHONE = "commons:App-augmented-reality-game-gps-163042.jpg^" + GO
POWERUP = "web:https://lh3.googleusercontent.com/iNoZjYGtiEOV3VVL2ogYNT5oGf23URF8H9EVERRIa1JvdesE8N3SOvOOlSnL8k-K63oxnZafZ-dTDLfNLZkmmPNLKlh2HwLGNOztlt2kOuJHCFQ=s0-e365^" + GO
GYM3 = "row:art:134|シャワーズ;art:149|カイリュー;art:143|カビゴン"
PENTA = "commons:Aerial view of the Pentagon, Arlington, VA (38285035892).jpg^wiki:en:The_Pentagon"
MEMO = "table:日付=2016年7月19日付のメモ;対象=政府が支給したスマホ;理由1=位置情報で施設の中の配置がわかる;理由2=職員の情報がスパイの勧誘に使われうる"
KREMLIN = "wiki:en:Moscow_Kremlin"
NIKI = "wiki:en:Nikolai_Nikiforov^" + KREMLIN
RUSSIA = "commons:Russian Federation (orthographic projection).svg^" + KREMLIN
HANKE = "wiki:en:John_Hanke"
GEARTH = "wiki:en:Google_Earth"
IQT = "paper:In-Q-Tel の発表（2003年6月25日）|In-Q-Tel、Keyhole に戦略的投資/NIMA、イラクの戦争の支援にこの技術を使う|In-Q-Tel＝CIAが作ったベンチャー投資の組織"
IRAQ = "wiki:en:Iraq_War"
NGA = "wiki:en:National_Geospatial-Intelligence_Agency"
FLOW1 = "row:wiki:en:Google_Earth|キーホール>wiki:en:Google|Google（2004年）>wiki:en:Ingress_(video_game)|Niantic Labs（2010年）"
INGRESS = "wiki:en:Ingress_(video_game)"
PORTAL = "table:ポータルの候補=約1500万件の申請;承認されたもの=約500万件;ポケモンGOでは=ポケストップとジムのもとに"
GPS = "wiki:en:Global_Positioning_System"
LGM1 = "web:https://lh3.googleusercontent.com/utNBW57Lr4TvRs98JCP8kOU3hEoKNYZUXoaV_0V6MVixUW7-NHgKSfO1RnLznOxBJPevbO16kJnJXaZRbrCVsiY3eaHHlDOFwshdxdrUqYk2wvs=e365-pa-nu-w1360-rw^wiki:en:Photogrammetry"
VPS = "web:https://lh3.googleusercontent.com/06jKW5x3FnIu1iepBOwkORzFMzOk_XQ2ceo7Qnp2hWZgf_m90tDAwR8ZXWvuD_6rGCyyRUqG3kLqqd6H5PuoaFC3C7brCDK2WjwvObCsKm8Bww=e365-pa-nu-w1360-rw^wiki:en:Augmented_reality"
LGMTAB = "table:スキャンされた場所=約1000万か所;新しいスキャン=週に約100万件;1件のスキャン=数百枚の画像"
SALE = "row:wiki:en:Scopely|Scopely（ゲーム）;wiki:en:Niantic_Spatial|Niantic Spatial（地図とAI）"
SPLIT = "table:Scopely に移ったもの=ポケモンGO、ピクミン ブルームなど;Niantic Spatial に残ったもの=スキャンのデータと位置のAI"
FPV = "commons:UA military FPV drones 01.jpg^wiki:en:First-person_view_(radio_control)"
FPV2 = "commons:UA FPV strike drones 02.jpg^wiki:en:First-person_view_(radio_control)"
UKR = "commons:Ukraine (orthographic projection).svg^wiki:en:Ukraine"
JAM = "commons:Anklav portable jammer GPS GLONASS.jpg^wiki:en:Electronic_warfare"
HIT = "table:妨害がないとき=ほぼ狙いどおり;妨害されると=命中は30〜50%に;新人の操縦士だと=約10%"
JDAM = "table:GPSが使えるとき=誤差 約5m;GPSが使えないとき=誤差 約30m"
VANTOR = "web:https://lh3.googleusercontent.com/FtKVMwYyYZHg7OccXshrzfaAWQy9qoSJfapLgWrBMI2hDr2ZmrxkOgIrS4d1yUUcypBby20saCkqdV_pLmhjAqgAwiWS9I_HBXyPXI-oUd2hyg=e365-pa-nu-w1440-rw^wiki:en:Satellite_imagery"
SAT = "web:https://lh3.googleusercontent.com/B0u3jFoqHCW6PFSbr--c-cdOp-Jk3Iy0fsMeCFzeRk4JSvkOI1utGWhNii1rOYyGhIl_qvCsSe8PtljbDhBjqc9d4hj7lMg0woAmAWyMOuC_Ig=e365-pa-nu-w1440-rw^wiki:en:Satellite_imagery"
COCO = "web:https://lh3.googleusercontent.com/3AQNV7_z0MLdgKxSSIhy7jcg2NMcgwmacOe-BaAe7LjawyLI5UqnZVUsjno7gfcp_TqpshV5kqyxqyPhZwks7P--nPgvSrdQx3YRzWbEtbv-aA=e365-pa-nu-w1440-rw^wiki:en:Delivery_robot"
SGP = "web:https://lh3.googleusercontent.com/DAgRKdu4vREs9B0tvwUneiOWYiqKp0B4ALiVyM2XwWR-16aXgSXxh-vKN0RdRmvalS8XpnvC_148YrA4doR2zw3fOLPCGkaLxThk_whwiq2T2Q=e365-pa-nu-w1440-rw^wiki:en:Singapore"
MCC = "wiki:en:Brian_McClendon"
QUOTE300 = "paper:Niantic の発表（2025年3月12日）|300億枚を超える、位置つきの画像の/データベースの上にモデルを作っている|Niantic Spatial（ナイアンティック・スペーシャル）の説明"
NETS = "table:学習させたAI=場所ごとに5000万個以上;中の数値（パラメータ）=合わせて150兆以上;もとにしたもの=プレイヤーのスキャン"
PANEL = "web:https://lh3.googleusercontent.com/Lcu3oU_lRgC4f2JNjfoxSW3jbPhU6xLtUo3kAgYB8MvynyK4iNo_D2CDFwes3vPPHm5mKYH3yLjAskT9dqJNtKPr75FPTVqdvW0E8UU57SZu=e365-pa-nu-w1360-rw^" + VANTOR
AIRGROUND = "row:web:https://lh3.googleusercontent.com/B0u3jFoqHCW6PFSbr--c-cdOp-Jk3Iy0fsMeCFzeRk4JSvkOI1utGWhNii1rOYyGhIl_qvCsSe8PtljbDhBjqc9d4hj7lMg0woAmAWyMOuC_Ig=e365-pa-nu-w1440-rw|空から（Vantor）>" + "web:https://lh3.googleusercontent.com/06jKW5x3FnIu1iepBOwkORzFMzOk_XQ2ceo7Qnp2hWZgf_m90tDAwR8ZXWvuD_6rGCyyRUqG3kLqqd6H5PuoaFC3C7brCDK2WjwvObCsKm8Bww=e365-pa-nu-w1360-rw|地上から（Niantic Spatial）"
NL = "commons:EU-Netherlands.svg^wiki:en:Netherlands"
TROUW = "wiki:en:Trouw"
ANS = "table:Niantic Spatial=スキャンは初期のAIの学習に使った;Niantic Spatial=ゲームのデータを直接渡す契約ではない;Vantor=ポケモンGOのデータは使っていない"
ARMY = "web:https://lh3.googleusercontent.com/ckIUNeXIi6GeWUouvPhiJ2SuxF7us_3ab1QZ_JllTGt9YoyFYev3m_-5d3vBPwyfpTO5zp-MpYx_Smh9Flka38IsD9pnGg4B_XeichPa3jKrrg4=e365-pa-nu-w1440-rw^" + NGA
CIRCLE = "row:wiki:en:Iraq_War|2003年 NIMAが使う>wiki:en:Pokémon_Go|2016年 ポケモンGO>web:https://lh3.googleusercontent.com/B0u3jFoqHCW6PFSbr--c-cdOp-Jk3Iy0fsMeCFzeRk4JSvkOI1utGWhNii1rOYyGhIl_qvCsSe8PtljbDhBjqc9d4hj7lMg0woAmAWyMOuC_Ig=e365-pa-nu-w1440-rw|2025年 Vantorと提携"

# コールドオープン（めたんが投げかけ、ずんだもんが驚く）
S("m", "normal", "ずんだもん。ポケストップの周りを\nぐるっと歩いて撮る、スキャンってやったことある？", POWERUP, sec="ポケモン雑学採掘所")
S("z", "proud", "ポケストップのパワーアップのために、\n何十回もやったのだ。", POWERUP)
S("m", "think", "その景色で育ったAIが、いま、\nGPSが使えない戦場の話に出てくるの。", FPV2)
S("z", "shock", "えっ。", FPV2, big="えっ。", ans=True)
L.append({"type": "op", "w": "m", "t": "ポケモンの深い雑学を掘り出す、\nポケモン雑学採掘所。", "say": "ポケモンの深い雑学を掘り出す、ポケモン雑学採掘所。"})

# 導入
S("m", "normal", "坑道の奥は電波が届かないわね。\nスマホの地図の青い点が、ぜんぜん動かない。", PHONE, sec="導入　坑道のGPS")
S("z", "proud", "GPSが届かないところでは、\nポケモンGOもできないのだ。", GPS, label="GPSの衛星")
S("z", "proud", "2016年のころは、ジムをシャワーズと\nカイリューとカビゴンで固めてたのだ。", GYM3, label="2016年のジムの常連", bgm="battle")
S("z", "proud", "ボクのシャワーズは、\nいまでも最強の門番なのだ。", "art:134", label="シャワーズ")
S("m", "happy", "いまのジムで、シャワーズを\nあまり見かけないけどね。", "art:134", v="tsun")
S("m", "happy", "わたしは対人戦のGOバトルリーグで、\n使う人の少ないポケモンで勝つほうが好き。", GO)
S("m", "think", "それより、さっきの続き。プレイヤーが\nスキャンした景色は、どこへ行ったのか。", POWERUP)
S("z", "surprise", "ボクたちが撮った景色の、\n行き先の話なのだ？", POWERUP)
S("m", "normal", "その話をするには、\n2016年の夏までさかのぼる必要があるの。", CROWD)
T("本日の採掘", "スキャンした景色は、どこへ行った？")

# 第一層 ペンタゴン
T("第一層", "2016年、ペンタゴンのポケモンGO", "第一層　2016年のペンタゴン",
  x={"head": "2016年、アメリカの国防総省は\n支給したスマホで\nポケモンGOを使わせなかった", "img": [PENTA], "bubble": "国防総省がなのだ？", "who": "z",
     "post": "2016年7月、アメリカの国防総省は、職員に配ったスマホでポケモンGOを使わないよう注意するメモを出しました。理由は位置情報とスパイ対策。でも、自分のスマホで遊ぶのは止めませんでした。どこまでなら安全だと思いますか？"})
S("m", "normal", "ポケモンGOが出たのは2016年7月。\n世界中で、人が公園や駅前に集まったわね。", CROWD, label="2017年 横浜のイベント")
S("m", "normal", "同じころ、アメリカの国防総省、ペンタゴンでも、\n職員がポケモンGOで遊ぶことが心配されたの。", PENTA, label="ペンタゴン（アメリカ国防総省）")
S("z", "surprise", "国防総省の中でポケモンを\n探してたのだ？", PENTA)
S("m", "normal", "そこで2016年7月19日付で、\n職員に注意のメモが出されたの。", MEMO, label="国防総省のメモ（報道による）")
S("m", "normal", "政府が支給したスマホでは、\nポケモンGOを使わないように、という内容よ。", MEMO, label="国防総省のメモ（報道による）")
S("m", "think", "理由は2つ。位置の記録から、\n施設の中のどこに何があるかわかってしまう。", MEMO)
S("m", "think", "もう1つは、職員の情報が、\nスパイの勧誘に使われるかもしれないこと。", MEMO)
S("z", "think", "じゃあ、ペンタゴンでは\nポケモンGOは全面禁止なのだ。", PENTA)
S("m", "normal", "それが違うの。広報の人は、\n自分のスマホで遊ぶのは止めていない、と話してる。", PENTA)
S("m", "normal", "敷地の中にあったジムは、\nゲームから消されたと報じられたわ。", PENTA)
S("m", "normal", "同じ7月、ロシアでは通信大臣の\nニキフォロフ氏が、こう話したの。", NIKI, label="ニコライ・ニキフォロフ通信大臣（当時）")
S("m", "think", "「このアプリは、ある情報機関の手を借りて\n作られたのではないかと疑っている」", NIKI, label="ニキフォロフ氏の発言（2016年7月）")
S("z", "think", "スパイの道具って言われたのだ…。\nさすがに考えすぎなのだ。", RUSSIA)
S("m", "normal", "証拠のない疑いだったわ。でもね、ポケモンGOを作った\n会社の生い立ちには、たしかに情報機関との縁があるの。", HANKE)

# 第二層 生い立ち
T("第二層", "ナイアンティックの生い立ち", "第二層　Googleアースの前身",
  x={"head": "ポケモンGOの会社の創業者が\n昔率いた地図ソフトの会社に、\nCIAの投資組織が出資していた", "img": [HANKE, IRAQ], "bubble": "CIAなのだ！？", "who": "z",
     "post": "ポケモンGOを作ったナイアンティックの創業者は、Googleアースのもとになった地図ソフトの会社の社長でした。その会社には2003年、CIAが作った投資組織が出資しています。この地図ソフト、最初はどこで役に立ったと思いますか？"})
S("m", "normal", "ポケモンGOを作ったナイアンティックの創業者は、\nジョン・ハンケさん。", HANKE, label="ジョン・ハンケさん")
S("m", "normal", "ハンケさんは昔、キーホールという会社で\n社長をしていたの。", HANKE)
S("m", "normal", "キーホールが作ったのは、地球を空から\n眺めるように見られる3Dの地図ソフトよ。", GEARTH, label="のちのGoogleアース")
S("z", "surprise", "それ、Googleアースみたいなのだ。", GEARTH, say="それ、グーグルアースみたいなのだ。")
S("m", "normal", "そのとおり。キーホールは2004年に\nGoogleに買われて、Googleアースになったの。", FLOW1, label="キーホールからポケモンGOまで", say="そのとおり。キーホールは2004年にグーグルに買われて、グーグルアースになったの。")
S("m", "think", "そのキーホールに、2003年、\nIn-Q-Telという組織が出資していたの。", IQT, label="In-Q-Telの発表（2003年）", say="そのキーホールに、2003年、インキューテルという組織が出資していたの。")
S("m", "normal", "In-Q-Telは、アメリカの中央情報局、CIAが作った\nベンチャー投資の組織よ。", IQT, ety=["In-Q-Tel（インキューテル）", "情報機関のために新しい技術へ投資する、CIAが作った組織"], say="インキューテルは、アメリカの中央情報局、シーアイエーが作ったベンチャー投資の組織よ。")
S("z", "shock", "CIAなのだ！？", IQT, ans=True)
S("m", "normal", "発表文の見出しは、こうよ。「NIMAが、\nイラクの戦争の支援にこの技術を使った」", IQT, say="発表文の見出しは、こうよ。ニーマが、イラクの戦争の支援にこの技術を使った。")
S("m", "normal", "NIMAは、衛星写真や地図を扱う\nアメリカの情報機関。いまのNGAね。", NGA, label="のちの国家地球空間情報局（NGA）", ety=["NIMA（ニーマ）", "国家画像地図局。2003年にNGAに改名"], say="ニーマは、衛星写真や地図を扱うアメリカの情報機関。いまのエヌジーエーね。")
S("m", "normal", "2003年のイラク戦争で、キーホールの地図ソフトが使われたの。\nテレビ局も、イラクの町を上から映すのに使ったわ。", IRAQ, label="2003年 イラク戦争")
S("z", "think", "ゲームの会社の話だと\n思ってたのだ…。", HANKE)
S("m", "normal", "ハンケさんはGoogleに移って、2010年に、\n社内でナイアンティック・ラボを作ったの。", FLOW1, label="キーホールからポケモンGOまで", say="ハンケさんはグーグルに移って、2010年に、社内でナイアンティック・ラボを作ったの。")
S("m", "normal", "キーホールで地図を作っていたブライアン・マクレンドンさんも、\nのちにナイアンティックの技術の責任者になったの。", MCC, label="ブライアン・マクレンドンさん")
S("z", "think", "地図を作っていた人たちが、\nゲームを作ったのだ。", MCC)
S("m", "normal", "最初の大きなゲームが、2012年のイングレス。現実の建物や\n像を「ポータル」という陣地にして取り合うゲームよ。", INGRESS, label="イングレス（2012年）")
S("m", "normal", "ポータルにしたい場所はプレイヤーが申請して、\n約1500万件のうち、約500万件が認められたの。", PORTAL, label="イングレスのポータル")
S("z", "surprise", "それが、ポケストップの\nもとになったのだ？", PORTAL, ans="idea")
S("m", "normal", "そう。ナイアンティックは2015年にGoogleから独立して、\n次の年にポケモンGOを出したの。", GO, say="そう。ナイアンティックは2015年にグーグルから独立して、次の年にポケモンGOを出したの。")

# 第三層 スキャン
T("第三層", "ポケストップを撮らせたわけ", "第三層　ARスキャン",
  x={"head": "ポケストップのスキャンは\n2020年、レベル20以上の\nフィールドリサーチになった", "img": [POWERUP], "bubble": "やったのだ", "who": "z",
     "post": "2020年10月、ポケモンGOに「ARマッピングタスク」が加わりました。ポケストップの周りを歩いて撮ると、その日のフィールドリサーチになります。この撮った景色、何に使われていたと思いますか？"})
S("m", "normal", "そのマクレンドンさんは、スマホの地図の青い点は、\nGPSのずれで50mずれることもよくある、と言ってる。", GPS, label="GPSのずれ", say="そのマクレンドンさんは、スマホの地図の青い点は、ジーピーエスのずれで50メートルずれることもよくある、と言ってる。")
S("z", "proud", "わかるのだ。ポケストップの前にいるのに、\n道路の反対側にいることになるのだ。", PHONE)
S("m", "normal", "そこでナイアンティックが考えたのが、カメラの景色で\n位置を知る方法。VPSと呼んでるわ。", VPS, ety=["VPS（ブイピーエス）", "Visual Positioning System。画像で位置と向きを出す仕組み"])
S("m", "normal", "カメラに映った景色を、前もって作った3Dの地図と\n照らし合わせて、立っている場所と向きを割り出すの。", VPS, label="カメラの景色で位置を知る")
S("z", "think", "でも、3Dの地図は\nだれが作るのだ？", VPS)
S("m", "think", "プレイヤーよ。2020年5月に、\nポケストップを撮る機能が発表されたの。", POWERUP)
S("m", "normal", "2020年10月には、ARマッピングタスクとして、\nレベル20以上のフィールドリサーチになった。", POWERUP, label="ARマッピングタスク（2020年10月）")
S("m", "normal", "ポケストップを中心に、20秒から30秒、\nぐるっと歩いて撮るのがコツと案内されてたわ。", POWERUP)
S("m", "normal", "2021年12月には、パワーアップポケストップ。\n何人かでスキャンすると、ポケストップが強くなるの。", POWERUP, label="パワーアップポケストップ（2021年12月）")
S("z", "proud", "スキャン25回でレベル3なのだ。\nみんなで撮ったのだ。", POWERUP, mark=[0.78, 0.5, 0.16])
S("m", "normal", "顔や車のナンバーは自動でぼかして、\nアカウントとは結びつけない、と説明されてたわ。", POWERUP)
S("m", "normal", "スキャンは、やりたい人だけがやる仕組み。\n歩いて遊ぶだけでは、AIの学習には使われない。", POWERUP, label="ナイアンティックの説明")

# 第四層 300億枚
T("第四層", "300億枚の景色の行き先", "第四層　大規模地理空間モデル",
  x={"head": "ナイアンティックは、\n300億枚を超える景色の画像で\n地図のAIを作っている", "img": [LGM1], "bubble": "300億枚なのだ…", "who": "z",
     "post": "ナイアンティックは2025年、300億枚を超える位置つきの画像で、地図のAIを作っていると書きました。ポケモンGOとほかのアプリのスキャンからです。この画像、ポケモンGOが売られたあとはどちらの会社に残ったと思いますか？"})
S("m", "normal", "2024年11月、ナイアンティックは\n大規模地理空間モデル、という計画を発表したの。", LGM1, ety=["大規模地理空間モデル", "世界中の場所の景色を覚えさせた、地図のためのAI"])
S("m", "normal", "スキャンされた場所は約1000万か所。\n新しいスキャンは、週に約100万件。", LGMTAB, label="2024年11月の発表")
S("m", "normal", "1件のスキャンには、数百枚の画像が入ってる。この数には、\nポケモンGO以外のアプリで撮ったスキャンも入ってるわ。", LGMTAB, label="2024年11月の発表")
S("z", "shock", "週に100万件なのだ！？", LGMTAB)
S("m", "normal", "そのスキャンで、場所ごとに小さなAIを学習させてるの。\nその数は5000万個以上。", NETS, label="2024年11月の発表")
S("m", "normal", "AIの中で調整される数値、パラメータは、\n合わせて150兆を超えるそうよ。", NETS, label="2024年11月の発表")
S("z", "surprise", "150兆…。シャワーズの個体値とは、\nけたが違いすぎるのだ。", "art:134")
S("m", "normal", "そして2025年3月。ナイアンティックは、\nポケモンGOなどのゲームを売ると発表したの。", SALE)
S("m", "normal", "買ったのはScopelyというゲーム会社。\n35億ドル、5000億円あまりよ。", "wiki:en:Scopely", label="Scopely（スコープリー）", say="買ったのは、スコープリーというゲーム会社。35億ドル、5000億円あまりよ。")
S("m", "think", "地図とAIの部門は、ナイアンティック・スペーシャル\nという別の会社になって、残ったの。", SPLIT, label="2025年 ゲームと地図が分かれた")
S("m", "normal", "ゲームを売る発表の文には、こう書いてあるわ。\n「300億枚を超える、位置つきの画像のデータ」", QUOTE300, label="Niantic の発表（2025年3月）", ans=True)
S("z", "think", "ボクたちが撮った景色は、\nゲームじゃないほうの会社に残ったのだ…。", SPLIT)
S("m", "normal", "ポケモンGOでのスキャンは、ゲームが\nScopelyに移るのにあわせて終わったと説明されてるわ。", GO, say="ポケモンGOでのスキャンは、ゲームがスコープリーに移るのにあわせて終わったと説明されてるわ。")
S("m", "normal", "それまでに集まった景色と、それで鍛えたAIが、\nナイアンティック・スペーシャルの土台になったの。", LGM1)

# 第五層 GPS妨害
T("第五層", "GPSが使えない戦場", "第五層　GPSの妨害",
  x={"head": "電波の妨害で、\nウクライナの小型ドローンの\n命中は30〜50%に落ちた", "img": [FPV], "bubble": "GPSが効かないのだ", "who": "m",
     "post": "ウクライナでは電波の妨害で、操縦する小型ドローンの命中が30〜50%に下がったと報じられました。新人の操縦士だと約10%。GPSが使えない場所で位置を知るには、何を使えばいいと思いますか？"})
S("m", "normal", "ここで話は、ウクライナに移るわ。\nロシアとの戦争が続いている、ヨーロッパの東の国よ。", UKR, label="ウクライナ")
S("m", "normal", "戦場では、GPSや無線の電波を\nわざと邪魔する装置が使われているの。", JAM, label="GPSを妨害する装置")
S("m", "think", "2024年の報道では、妨害のせいで、\n操縦する小型ドローンの命中が30〜50%に落ちたって。", HIT, label="ロイター通信（2024年7月）", say="2024年の報道では、妨害のせいで、操縦する小型ドローンの命中が、30から50パーセントに落ちたって。")
S("m", "normal", "新人の操縦士だと、10%くらいまで\n下がるそうよ。", HIT)
S("m", "normal", "GPSで導く爆弾も、ふだんの誤差は約5m。\nGPSが使えないと、約30mまで広がるといわれてる。", JDAM, label="イギリスの研究所 RUSI（2023年）", say="ジーピーエスで導く爆弾も、ふだんの誤差は約5メートル。ジーピーエスが使えないと、約30メートルまで広がるといわれてる。")
S("z", "think", "坑道の中のボクのスマホと\n同じなのだ。", PHONE)
S("m", "think", "そう。だから各国の軍は、GPSに頼らずに、\nカメラに映る景色で位置を知る技術をほしがってる。", FPV2)
S("z", "shock", "それって、さっきの\nVPSのことなのだ！？", VPS, ans=True)

# 最深層 Vantor
T("最深層", "国防の会社との提携", "最深層　Vantorとの提携",
  x={"head": "ポケモンGOのスキャンで\nAIを育てた会社が、国防の\n衛星の会社と提携した", "img": [VANTOR], "bubble": "つながったのだ", "who": "z",
     "post": "2025年12月、ナイアンティック・スペーシャルは、アメリカの国防や情報機関に衛星画像を売る会社Vantorと、GPSが使えない場所での位置推定で提携しました。この会社、ポケモンGOのデータを使っていると思いますか？"})
S("m", "normal", "2025年12月16日。ナイアンティック・スペーシャルは、\nVantorという会社との提携を発表したの。", VANTOR, label="提携の発表（2025年12月）", say="2025年12月16日。ナイアンティック・スペーシャルは、ヴァンターという会社との提携を発表したの。")
S("m", "normal", "Vantorは、地球を撮る衛星を持っていて、\nアメリカの国防や情報機関に画像を売る会社よ。", SAT, label="Vantorが運用する撮影衛星", say="ヴァンターは、地球を撮る衛星を持っていて、アメリカの国防や情報機関に画像を売る会社よ。")
S("m", "normal", "提携の中身は、GPSが妨害されたときでも、\n空のドローンと地上の人が同じ位置を共有すること。", AIRGROUND, label="空と地上で同じ位置を共有")
S("m", "normal", "空からの位置はVantorの衛星画像で、地上からの位置は\nナイアンティック・スペーシャルのVPSで割り出すの。", AIRGROUND, label="空と地上で同じ位置を共有", say="空からの位置はヴァンターの衛星画像で、地上からの位置はナイアンティック・スペーシャルのブイピーエスで割り出すの。")
S("z", "shock", "ボクのスキャンが、\nドローンを飛ばしてるのだ！？", FPV2, v="namida")
S("m", "think", "そこは落ち着いて。2026年6月、\nオランダの新聞がこの話を記事にしたの。", NL, label="オランダ")
S("m", "normal", "新聞の名前はトラウ。ポケモンGOのスキャンが、\n国防の技術の開発に役立ったと報じたの。", TROUW, label="オランダの新聞トラウ")
S("m", "normal", "それをきっかけに、イギリスやアメリカの\nメディアにも広まったわ。", TROUW)
S("m", "think", "両方の会社の答えは、こうよ。", ANS, label="会社の説明")
S("m", "normal", "ナイアンティック・スペーシャルは、\nスキャンを初期のAIの学習に使ったことは認めた。", ANS)
S("m", "normal", "でも、AIは学習の結果で、スキャンの写しではない。\nゲームのデータを渡す契約でもない、と。", ANS)
S("m", "normal", "Vantorは、ポケモンGOのデータは使っていないし、\n持ってもいない、と答えたわ。", ANS, say="ヴァンターは、ポケモンGOのデータは使っていないし、持ってもいない、と答えたわ。")
S("z", "think", "じゃあ、ボクのスキャンで\nドローンが飛んでるわけじゃないのだ？", FPV2)
S("m", "normal", "実際に戦場で使われた証拠は、\n公開されてる情報にはないの。", FPV2, big="証拠はない")
S("m", "think", "ただ、2026年6月、ナイアンティック・スペーシャルのVPSは、\nアメリカ陸軍の研究所が導入を検討できる技術の一覧に載ったわ。", ARMY, label="Niantic Spatialの発表（2026年6月）")
S("m", "normal", "ただ、使い道は軍事だけじゃないわ。\n2026年3月には、配達ロボットの会社と提携したの。", COCO, label="配達ロボットの会社 Coco Robotics と提携")
S("m", "normal", "ビルの谷間でGPSが乱れても、\nロボットが自分の位置をつかめるようにするためよ。", COCO)
S("m", "normal", "9月には、シンガポールの地図の役所と、\n国全体のVPSの地図を作れるか確かめ始めたわ。", SGP, label="シンガポール土地庁との覚え書き（2026年9月）")
S("z", "think", "ロボットにも、ドローンにも、\n同じ地図のAIが使われるのだ。", SGP)
S("m", "normal", "Vantorの衛星画像を買っている先には、\nあのNIMAが名前を変えたNGAも入ってるの。", NGA, say="ヴァンターの衛星画像を買っている先には、あのニーマが名前を変えた、エヌジーエーも入ってるの。")
S("z", "surprise", "2003年にキーホールの地図を\n使った役所なのだ！", CIRCLE, label="2003年から2025年まで", ans="idea")
S("m", "normal", "地図ソフトから始まった道が、ゲームを通って、\nまた同じ役所の近くに戻ってきたのね。", CIRCLE, label="2003年から2025年まで")

# まとめ
S("m", "think", "ポケストップを撮ったのは、ポケモンが物かげに\n隠れるような、ゲームの演出のためだった。", POWERUP, sec="まとめ")
S("m", "normal", "でも、その景色で育ったAIは、いま、\nGPSの届かない場所の位置を探す技術になってる。", VANTOR)
S("z", "proud", "…ボクのシャワーズのジムも、\nどこかで地図になってるかもしれないのだ。", "art:134")
S("m", "happy", "シャワーズは、ジムより\n地図の中のほうが長生きしそうね。", "art:134", v="tsun")

# 英語名
T("おまけ", "今日のポケモンの英語名", "今日のポケモンの英語名")
S("m", "happy", "今日のポケモンの英語名。\n1匹目はシャワーズ。", "art:134", label="Vaporeon（ヴェイポリオン）")
S("m", "normal", "ヴェイポリオン。湯気や水蒸気の\n「ヴェイパー」から来てるといわれてるの。", "art:134", label="Vaporeon（ヴェイポリオン）")
S("m", "happy", "2匹目はカイリュー。\nドラゴナイト。", "art:149", label="Dragonite（ドラゴナイト）")
S("m", "normal", "ドラゴンと、騎士の「ナイト」を\n合わせた名前だといわれてるの。", "art:149", label="Dragonite（ドラゴナイト）")
S("m", "happy", "3匹目はカビゴン。\nスノーラックス。", "art:143", label="Snorlax（スノーラックス）")
S("m", "normal", "いびきの「スノア」と、くつろぐの\n「リラックス」を合わせた名前よ。", "art:143", label="Snorlax（スノーラックス）")
S("m", "normal", "今日出てきたポケモンの英語名は、\n英単語帳サイト「もんすぺ！」でも調べられるわ。", "site:", label="「もんすぺ！」で検索")
S("m", "happy", "もんすぺ！には、ポケモンの面白い雑学のコラムもあるの。\n動画の続きみたいに読めるわよ。", "site:", label="「もんすぺ！」雑学コラムもあります")
S("z", "happy", "今日の採掘はここまでなのだ。\nチャンネル登録もよろしくなのだ。", "site:", label="「もんすぺ！」で検索")
L.append({"type": "ed"})

thumb = {"layout": "v2", "pre": "ポケモンGOのスキャンで育ったAIが", "big": ["米軍へ", "売り込み"], "hl": 0, "hl_color": "red",
         "back": PENTA, "badge": GO, "chara": ["z", "shock"]}
out = {"no": 5, "title": "ポケモンGOのスキャンで育ったAIが、米軍に売り込まれている。",
       "neta": "プレイヤーの撮った300億枚の画像がAIに使われた",
       "neta_also": ["アメリカ国防総省が敷地内のポケモンGOを制限", "ロシアの大臣がポケモンGOはスパイの道具かもと疑った"],
       "lines": L, "thumb": thumb}
here = os.path.dirname(os.path.abspath(__file__))
json.dump(out, open(os.path.join(here, "script.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
n = sum(len(l.get("t", "").replace("\n", "")) for l in L)
print(len(L), "行", n, "字")
