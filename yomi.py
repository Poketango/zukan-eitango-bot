# 読みとアクセントの自動点検・自動修正（2026-11-16）
#   VOICEVOX は文を単語に分け、辞書と規則（匂坂規則）でアクセント句と核を決める。規則の正答率は約 87.5% で、
#   特に「辞書にない固有名詞」「数字」「語尾（なのだ）」で崩れる。ここではそれを次の 3 つで減らす。
#   1. prepare(vv, text)  … 台本の行に出てくるポケモン名をエンジンに読ませ、句が割れたり読みが違ったりする名前だけを
#                           ユーザー辞書に登録する（外来語の規則で核を決める）。tools/yomi/words.json の言葉は毎回登録する。
#   2. autofix(kana)      … エンジンの読み（AquesTalk 風表記）のうち、確実に直せる崩れを直す（「ズ'ンダモンナ/ノダ'」→ 1 句）。
#   3. issues(text, kana) … 人が確かめるべき行を見つける（数字、1 拍だけの句、漢字 1 字の語、辞書にないカタカナ語の割れ）。
#   どれも失敗しても読み上げを止めない（例外は握りつぶして元の読みのまま進む）。
import os, re, json, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(HERE, "tools", "yomi")

try:
    NAMES = set(json.load(open(os.path.join(DIR, "pokemon_names.json"), encoding="utf-8")))
except Exception:
    NAMES = set()
try:
    WORDS = json.load(open(os.path.join(DIR, "words.json"), encoding="utf-8")).get("words", [])
except Exception:
    WORDS = []
MANUAL = {w["surface"] for w in WORDS}

SMALL = set("ャュョァィゥェォヮ")
SPECIAL = set("ンッー")
VOWEL = {}
for row, v in (("アカサタナハマヤラワガザダバパァャヮ", "ア"), ("イキシチニヒミリギジヂビピィ", "イ"),
               ("ウクスツヌフムユルグズヅブプゥュヴ", "ウ"), ("エケセテネヘメレゲゼデベペェ", "エ"),
               ("オコソトノホモヨロヲゴゾドボポォョ", "オ")):
    for c in row: VOWEL[c] = v


def moras(s):
    """カタカナを拍に分ける（小さい ャ などは前の拍にくっつける）"""
    out = []
    for c in s:
        if c in SMALL and out: out[-1] += c
        else: out.append(c)
    return out


def rule_accent(pron):
    """外来語の規則：後ろから 3 拍目で下がる。そこが ン・ッ・ー なら 1 拍前にずらす。2 拍以下は頭高"""
    m = moras(pron); n = len(m)
    if n <= 2: return 1
    k = n - 2
    while k > 1 and m[k - 1][0] in SPECIAL: k -= 1
    return k


def plain(s):
    """読みを比べやすい形にする（記号を消し、ー・オウ・エイを長音の母音にそろえる）"""
    s = re.sub(r"[' _/、？]", "", s)
    out = []
    for c in s:
        if c == "ー" and out: c = VOWEL.get(out[-1][-1], "ー")
        out.append(c)
    s = "".join(out)
    s = re.sub(r"(?<=[オコソトノホモヨロゴゾドボポョォ])ウ", "オ", s)
    s = re.sub(r"(?<=[エケセテネヘメレゲゼデベペェ])イ", "エ", s)
    return s


def clean(text):
    """エンジンに渡す前の下ごしらえ（2026-11-20）。カタカナの間の「・」は無音の間になって「ポ'ケット、モ'ンスタア」と割れるので消す
    （「ポケットモンスター」なら 1 句で読まれる）。並べる言葉は台本で「、」を使う"""
    text = re.sub(r"(?<=[ァ-ヴー])・(?=[ァ-ヴー])", "", text)
    # 2026-11-20 短い語句の「」を外す。「」は読点と同じ 0.3〜0.4 秒の間になり、「ポケモンGOを、有害な熱狂、と」のように
    # 途中で息継ぎしたような読みになる（実践者の指摘：一拍置く必要がなければ消す）。長いせりふの引用は人も間を置くので残す
    return re.sub(r"[「『]([^「」『』、。？！]{1,12})[」』]", r"\1", text)


# ---------- 間（ポーズ）の長さ（2026-11-20） ----------
#   エンジンは読点・句点・「」のたびに 0.27〜0.41 秒の間を入れる（1.3 倍速でも 0.21〜0.32 秒）。
#   実践者（note「VOICEVOXで自然な音声を作るために気をつけていること」）は読点の間を 0.10〜0.15 秒に縮めている。
#   読点は短く、文の切れ目（。！？）は少し長く残して、息継ぎと文の区切りを聞き分けられるようにする。
PAUSE_COMMA = 0.13          # 秒（再生したときの長さ）
PAUSE_SENT = 0.30
_PUNC = r"[、。，．,！？!?…‥「」『』（）()\s]+"


def set_pauses(q, text, speed):
    """audio_query の間を、原文の記号の種類に合わせた長さにする。記号と間の数が合わなければ一律に縮める"""
    try:
        pm = [p for p in q.get("accent_phrases", []) if p.get("pause_mora")]
        body = re.sub(_PUNC + "$", "", re.sub("^" + _PUNC, "", text.strip()))
        groups = re.findall(_PUNC, body)
        if pm and len(groups) == len(pm):
            for p, g in zip(pm, groups):
                sec = PAUSE_SENT if re.search(r"[。．！？!?…‥]", g) else PAUSE_COMMA
                p["pause_mora"]["vowel_length"] = sec * speed
            return "matched"
        q["pauseLengthScale"] = 0.5
        return "scaled"
    except Exception:
        return "error"


# ---------- エンジンとのやりとり ----------
def _req(vv, path, data=None, method="POST"):
    h = {"Content-Type": "application/json"} if data else {}
    return urllib.request.urlopen(urllib.request.Request(vv + path, data=data, headers=h, method=method), timeout=60).read()


def kana_of(vv, text, speaker=3):
    q = json.loads(_req(vv, "/audio_query?" + urllib.parse.urlencode({"text": text, "speaker": speaker})))
    return q.get("kana", "")


def _add(vv, surface, pron, accent):
    _req(vv, "/user_dict_word?" + urllib.parse.urlencode({
        "surface": surface, "pronunciation": pron, "accent_type": accent, "word_type": "PROPER_NOUN", "priority": 8}))


_STATE = {"vv": None, "checked": set(), "registered": [], "kata": {}}


def _init(vv):
    if _STATE["vv"] == vv: return
    _STATE.update(vv=vv, checked=set(), registered=[], kata={})
    for w in WORDS:
        try:
            _add(vv, w["surface"], w["pron"], w["accent"]); _STATE["registered"].append((w["surface"], w["pron"], w["accent"], "words.json"))
        except Exception as e:
            print("辞書登録に失敗:", w["surface"], repr(e)[:80])


def names_in(text):
    """行に出てくるポケモン名（カタカナのかたまりが名前そのもの、またはメガ＋名前のとき）"""
    found = []
    for run in re.findall(r"[ァ-ヴー]+", text):
        for cand in (run, run[2:] if run.startswith("メガ") else None):
            if cand and cand in NAMES and cand not in found: found.append(cand)
    return found


def prepare(vv, text):
    """行に出てくるポケモン名を点検し、崩れる名前だけを辞書に登録する。登録した名前のリストを返す"""
    new = []
    try:
        _init(vv)
        for name in names_in(text):
            if name in _STATE["checked"] or name in MANUAL: continue
            _STATE["checked"].add(name)
            k = kana_of(vv, name)
            split = bool(re.search(r"[/、]", k))
            wrong = plain(k) != plain(name)
            if split or wrong:
                acc = rule_accent(name)
                _add(vv, name, name, acc)
                _STATE["registered"].append((name, name, acc, f"自動（エンジンの読み {k}）"))
                new.append(name)
    except Exception as e:
        print("辞書の準備を飛ばした:", repr(e)[:120])
    return new


def registered():
    return list(_STATE["registered"])


# ---------- 自動修正 ----------
TAILS = {"ノダ", "ナノダ", "ノダヨ", "ノダネ", "ナノダヨ", "ナノダネ"}


def _core(p):
    return re.sub(r"['_？]", "", p)


def _merge(a, b):
    """アクセント句 a と、語尾だけの句 b をつなぐ。a に下がり目があればそれを残し、平板なら「の」で下げる"""
    q = "？" if b.endswith("？") else ""
    b = b.rstrip("？")
    bp = b.replace("'", "")
    if "'" in a and not a.endswith("'"):
        return a + bp + q
    ap = a.rstrip("'")
    i = bp.find("ノ")
    return ap + (bp[:i + 1] + "'" + bp[i + 1:] if i >= 0 else bp + "'") + q


# ---------- 句のつなぎすぎ・切りすぎ（2026-11-20） ----------
#   エンジンは「違って/いた」「説明/して/いる」「売る/のを」のように、補助動詞・する・形式名詞の「の」を独立した句にしがち。
#   句が増えるたびに声が低→高と上がり直すので、1 文の中で何度も跳ねるロボットっぽい抑揚になる（第008・009回の 212 行で 123 か所）。
#   東京方言では「て」「てる」は前の語と一つの単位として続き、終助詞の「の」「のだ」は前に関係なく低くつく（郡 2019）。
#   つなぎ方：前の句に下がり目があればそれだけを残し（読んでいるのだ → ヨ'ンデイルノダ）、
#             前が平板なら後ろの句の下がり目をそのまま使う（説明しているわ → セツメエシテイル'ワ、批判したの → ヒハンシタ'ノ）。
AUX_TE = re.compile(r"^(?:イ(?:ル|タ|テ|ナ|マ)|シマ|チャ|オ(?:ク|イ|キ)|ミ(?:ル|タ|テ|ヨ)|ク(?:ル|レ)|キ(?:タ|テ|マ)|コ(?:ナ|イ)|アル|アッ)")
AUX_SURU = re.compile(r"^(?:シ(?:タ|テ|ナ|ヨ|マス|マシ|マセ)|ス(?:ル|レ)|サ(?:レ|セ))")
NO_TAIL = re.compile(r"^(?:ノ|ン)(?:ワ|オ|ガ|モ|ニ|デ|カ|ダ|デス|ヨ|ネ)?(?:ネ|ヨ|カ|ロ)?$")
PART_END = set("ガワニトモヤカノネヨ")
O_ROW = set("オコソトノホモヨロゴゾドボポョォ")
E_ROW = set("エケセテネヘメレゲゼデベペェ")


def _ends_with_particle(c):
    """句の終わりが助詞か。を・へ はエンジンの読みでは オ・エ になるので、長音（ハッピョオ、セツメエ）と区別する"""
    if not c: return False
    if c[-1] in PART_END: return True
    if c[-1] == "オ": return len(c) < 2 or c[-2] not in O_ROW or c.endswith("オオ")
    if c[-1] == "エ": return len(c) < 2 or c[-2] not in E_ROW
    if c.endswith(("マデ", "ノデ", "ニデ", "カラ", "ヨリ")): return True
    return False


def _te_form(c):
    """て形か（テで終わる、または ン・イ のあとのデで終わる。「まで」「ので」は除く）"""
    if c.endswith(("マデ", "ノデ", "ナデ")): return False
    return c.endswith("テ") or bool(re.search(r"[ンイ]デ$", c))
VERB_END = set("ウクスツヌフムユルグズヅブプタダイ")


def _flat(p):
    """句が平板（下がり目が句末）か"""
    return p.rstrip("？").endswith("'")


def _join(a, b):
    """a の後ろに b をつないだ 1 句を返す"""
    q = "？" if b.endswith("？") else ""
    b = b.rstrip("？")
    if _flat(a):
        return a.rstrip("？").rstrip("'") + b + q
    return a + b.replace("'", "") + q


def _glue_aux(phrases, seps):
    i = 1
    while i < len(phrases):
        a, b = phrases[i - 1], phrases[i]
        ca, cb = _core(a), _core(b)
        ok = False
        if seps[i - 1] == "/" and not a.endswith("？") and ca:
            if _te_form(ca) and AUX_TE.match(cb) and len(moras(cb)) <= 6:
                ok = True                                   # 〜て いる／しまう／くる／みる／おく
            elif AUX_SURU.match(cb) and not _ends_with_particle(ca) and len(moras(ca)) >= 2:
                ok = True                                   # 名詞＋する（判断した、説明して）
            elif NO_TAIL.match(cb) and ca[-1] in VERB_END:
                ok = True                                   # 動詞・形容詞＋の（売るのを、なるのは）
        if ok:
            phrases[i - 1] = _join(a, b)
            del phrases[i]; del seps[i - 1]
        else:
            i += 1


NUM_ONLY = re.compile(r"^(?:イチ|イッ|ニ|サン|ヨン|ヨ|ゴ|ロク|ロッ|ナナ|ハチ|ハッ|キュウ|キュ|ジュウ|ジュッ|ヒャク|ビャク|ピャク|セン|ゼン|マン|オク)+$")
def _shift_special(p):
    """下がり目が ン・ッ・ー や長音のウに乗ったら 1 拍前へ（キュウ'ネン → キュ'ウネン、ニセン'イチ → ニセ'ンイチ）"""
    k = p.find("'")
    if k <= 1 or k == len(p.rstrip("？")) - 1: return p
    prev = p[:k].replace("_", "")
    if prev.endswith(("ン", "ッ", "ー")) or re.search(r"[ュョ]ウ$", prev):
        return p[:k - 1] + "'" + p[k - 1] + p[k + 1:]
    return p


YEAR_HEAD = re.compile(r"^(_?セ_?ン(?:キュウ|ハッ|ナナ|ロッ|ゴ|ヨン|サン|ニ)?(?:ヒャ_?ク|ビャ_?ク|ピャ_?ク))(?=.*ネン)")


def _glue_numbers(phrases, seps):
    """「ニセ'ン/イチ'ネンノ」→「ニセンイチ'ネンノ」。下がり目は最後の句のものを残す。
    1000 年代の年号（センキュウヒャク…）は人も「千九百／九十九年」と区切るので、百のあとで句を分ける"""
    i = 1
    while i < len(phrases):
        a, b = phrases[i - 1], phrases[i]
        ca, cb = _core(a), _core(b)
        if seps[i - 1] == "/" and ca in ("シ", "シチ", "ク") and cb.startswith("ガツ"):
            phrases[i - 1] = a + b.replace("'", "")                        # 四月 シ'ガツ、七月 シチ'ガツ、九月 ク'ガツ
            del phrases[i]; del seps[i - 1]; continue
        if seps[i - 1] == "/" and (NUM_ONLY.match(ca) or NUM_ONLY.match(ca[2:] if ca.startswith("ダイ") else "") or ca == "ダイ") and NUMHEAD.match(cb):
            c = (a.replace("'", "") + b) if "'" in b else (a + b)          # 後ろに下がり目がなければ前のを残す
            m = YEAR_HEAD.match(c)
            if m and "'" in c[len(m.group(1)):]:
                head = m.group(1)
                phrases[i - 1] = head.replace("セン", "セ'ン", 1).replace("_セン", "_セ'ン", 1)
                phrases[i] = _shift_special(c[len(head):])
                i += 1
            else:
                phrases[i - 1] = _shift_special(c)
                del phrases[i]; del seps[i - 1]
        else:
            i += 1


PARTICLES = {"ト", "トワ", "トモ", "ノ", "ガ", "ワ", "オ", "モ", "ニ", "デ", "ヘ", "ヤ", "カ", "ッテ", "ノワ", "ニワ", "デワ", "トイウ", "ネ", "ヨ", "ヨネ", "ダ", "デス"}
QUOTE_P = re.compile(r"[」』][とのがはをもにでへやかねよだ]|、(?:と|って|の)(?![ぁ-ん]{0,1}[、。])")   # 2026-11-20 「〜ある、と書かれた」の「と」も


def autofix(kana, text=None):
    """確実に直せる崩れだけを直した読みを返す（直すところが無ければ元のまま）。
    text を渡すと、「」の直後の助詞が間を置いた 1 句に浮いているのを前の句につなぐ"""
    try:
        parts = re.split(r"([/、])", kana)
        phrases, seps = parts[0::2], parts[1::2]
        n = len(QUOTE_P.findall(text or ""))
        i = 1
        while i < len(phrases) and n > 0:
            if seps[i - 1] == "、" and _core(phrases[i]) in PARTICLES and not phrases[i - 1].endswith("？"):
                a, b = phrases[i - 1], phrases[i].replace("'", "")
                phrases[i - 1] = (a.rstrip("'") + b + "'") if a.endswith("'") else (a + b if "'" in a else a + b)
                del phrases[i]; del seps[i - 1]; n -= 1
            else:
                i += 1
        i = 1
        while i < len(phrases):
            if seps[i - 1] == "/" and _core(phrases[i]) in TAILS and not phrases[i - 1].endswith("？"):
                phrases[i - 1] = _merge(phrases[i - 1], phrases[i])
                del phrases[i]; del seps[i - 1]
            else:
                i += 1
        _glue_aux(phrases, seps)                   # 2026-11-20 補助動詞・する・形式名詞の「の」を前の句につなぐ
        _glue_numbers(phrases, seps)               # 2026-11-20 数字の割れを一続きにする
        out = phrases[0]
        for s, p in zip(seps, phrases[1:]): out += s + p
        return out
    except Exception:
        return kana


# ---------- 要確認の洗い出し ----------
NUMW = re.compile(r"^(?:イチ|イッ|ニ|サン|ヨン|ヨ|シ|ゴ|ロク|ロッ|ナナ|シチ|ハチ|ハッ|キュウ|キュ|ク|ジュウ|ジュッ|ヒャク|ビャク|ピャク|セン|ゼン|マン|オク|レイ|ゼロ)+$")
NUMHEAD = re.compile(r"^(?:イチ|イッ|ニ|サン|ヨン|ヨ(?=ネン|ジ|ニン|エン)|ゴ|ロク|ロッ|ナナ|シチ|ハチ|ハッ|キュウ|キュ|ク(?=ニチ|ガツ|ジ)|ジュウ|ジュッ|ヒャク|ビャク|ピャク|セン|ゼン|マン)")
ONE = re.compile(r"(?<![一-龥々])[国方何種位](?![一-龥々])")   # 取り違えが実際に起きた字（国＝クニ/コク、種＝タネ/シュ、位＝クライ/イ など）
_HN = r"(?:いち|さん|よん|ろく|なな|しち|はち|きゅう|じゅう|じゅっ|にひゃく|ごひゃく|ひゃく|びゃく|ぴゃく|にせん|ごせん|せん|ぜん|にまん|ごまん|まん)"
HIRA_NUM = re.compile(_HN + r"(?:" + _HN + r"|がつ|にち|ねん|しゅう|ごう)")


def issues(vv, text, kana):
    """人が確かめるべき点を短い言葉で返す（空なら問題なし）"""
    out = []
    parts = re.split(r"([/、])", kana)
    phrases = [p for p in parts[0::2] if p]
    for a, sep, b in zip(parts[0::2], parts[1::2], parts[2::2]):
        if sep == "/" and NUMW.match(_core(a)) and NUMHEAD.match(_core(b)):
            out.append(f"数字が句に割れている {a}/{b}：一続きに読むなら say にひらがなか kana で指定"); break
    frag = [p for p in phrases if len(moras(_core(p))) <= 1]
    if frag:
        out.append("1拍だけの句 " + " ".join(frag) + "：単語の途中で切れていないか")
    if HIRA_NUM.search(text):
        out.append("ひらがなの数字 " + HIRA_NUM.search(text).group(0) + "：エンジンが区切りを見失って読みが壊れる（じゅうがつようか→ジュウガ/ツヨウカ）。算用数字で書く")
    one = sorted(set(ONE.findall(text)))
    if one:
        out.append("漢字1字の語 " + "".join(one) + "：音読み・訓読みの取り違えがないか")
    for run in re.findall(r"[ァ-ヴー]{3,}", text):
        if run in NAMES or run in MANUAL or (run.startswith("メガ") and run[2:] in NAMES): continue
        if vv is None: continue
        try:
            if run not in _STATE["kata"]: _STATE["kata"][run] = kana_of(vv, run)
            k = _STATE["kata"][run]
            if re.search(r"[/、]", k):
                out.append(f"辞書にないカタカナ語 {run} が {k} に割れる：words.json に足すか確かめる")
        except Exception:
            pass
    return out
