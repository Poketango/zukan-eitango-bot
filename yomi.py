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


PARTICLES = {"ト", "トワ", "トモ", "ノ", "ガ", "ワ", "オ", "モ", "ニ", "デ", "ヘ", "ヤ", "カ", "ッテ", "ノワ", "ニワ", "デワ", "トイウ"}
QUOTE_P = re.compile(r"[」』][とのがはをもにでへやか]")


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
        out = phrases[0]
        for s, p in zip(seps, phrases[1:]): out += s + p
        return out
    except Exception:
        return kana


# ---------- 要確認の洗い出し ----------
NUMW = re.compile(r"^(?:イチ|イッ|ニ|サン|ヨン|ヨ|シ|ゴ|ロク|ロッ|ナナ|シチ|ハチ|ハッ|キュウ|キュ|ク|ジュウ|ジュッ|ヒャク|ビャク|ピャク|セン|ゼン|マン|オク|レイ|ゼロ)+$")
NUMHEAD = re.compile(r"^(?:イチ|イッ|ニ|サン|ヨン|ロク|ロッ|ナナ|ハチ|ハッ|キュウ|ジュウ|ジュッ|ヒャク|セン|マン)")
ONE = re.compile(r"(?<![一-龥々])[国方何](?![一-龥々])")   # 取り違えが実際に起きた字（国＝クニ/コク など）


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
