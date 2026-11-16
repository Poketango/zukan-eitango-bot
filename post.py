# ポケモン英語図鑑 YouTubeショート自動投稿（GitHub Actions で1日3回実行）
# 2026-11-13 てこ入れ版
#   ・2026-11-14 型を7つに増やした（新しい5つは formats.py）。投稿ごとに順番に回す
#   ・もとの2つのエンタメ型
#       英語名シルエットクイズ「この英語名、だーれだ？」（ナレーション：VOICEVOX ずんだもん）
#       英語版の図鑑が怖すぎる（ホラー演出・ナレーション：VOICEVOX 冥鳴ひまり）
#   ・VOICEVOX エンジン（Actions の docker で起動）が無いときは、ナレーションなしで作る
import os, sys, json, random, re, datetime, subprocess, io, math, wave, struct
import urllib.request, urllib.parse
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

SITE = "https://poketango.com"
START = datetime.date(2026, 11, 14)
SLOTS_PER_DAY = 3                              # 1日の投稿回数（workflow の cron と合わせる）
FONT_B = os.environ.get("FONT_B", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
FONT_K = os.environ.get("FONT_K", "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc")
FONT_M = os.environ.get("FONT_M", "/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc")   # 怖い回の明朝体
VW, VH, FPS, SR = 1080, 1920, 24, 44100
LOCAL = os.environ.get("LOCAL_DATA")
VV = os.environ.get("VOICEVOX_URL", "http://127.0.0.1:50021")
ZUNDA, METAN = 3, 2                            # VOICEVOX 話者ID（ずんだもん ノーマル／四国めたん ノーマル）。冥鳴ひまりは四国めたんに替えた（2026-11-15 指示書）
HIMARI = METAN                                 # 古い名前で呼んでいる所のため
SPEED = 1.3                                    # 指示書：話す速さは1.3倍くらい
HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "fonts")
F_DELA = os.path.join(FD, "DelaGothicOne-Regular.ttf")      # 型ごとに書体を変えて単調にしない（指示書：フォントを多様に）
F_ROUND = os.path.join(FD, "MPLUSRounded1c-Black.ttf")
F_ROCK = os.path.join(FD, "RocknRollOne-Regular.ttf")
F_MOCHI = os.path.join(FD, "MochiyPopOne-Regular.ttf")
try: KANA = json.load(open(os.path.join(HERE, "en_kana.json"), encoding="utf-8"))   # 英語名の発音（カタカナ）。1〜649番
except Exception: KANA = {}


def kana(key):
    """英語名の発音のカタカナ。無ければ空"""
    return KANA.get(key, "")


def same_as_jp(key, jn):
    """英語名の発音が日本語名とほぼ同じ（ピカチュウなど）なら True。指示書：そういうポケモンの英語名は紹介しない"""
    norm = lambda s: re.sub(r"[ー・\s]", "", s or "").replace("ヴ", "ブ")
    return bool(kana(key)) and norm(kana(key)) == norm(jn)

SCARY = ["haunter", "cubone", "drifloon", "victreebel", "banette", "golbat", "yamask", "phantump", "froslass", "dusknoir",
         "mimikyu", "spiritomb", "marowak", "duskull", "gourgeist", "lampent", "mandibuzz", "cursola", "bramblin", "misdreavus",
         "drifblim", "dhelmise", "sableye", "litwick", "chandelure", "shuppet", "gengar", "jellicent", "trevenant", "polteageist"]


_FONTS = {}


def F(p, s):
    k = (p, s)
    if k not in _FONTS: _FONTS[k] = _F(p, s)      # 同じフォントを何度も読み込まない
    return _FONTS[k]


def _F(p, s):
    # 太いフォントが無い環境では、ある太さで代用する
    for cand in (p, p.replace("Black", "Bold"), FONT_B):
        if os.path.exists(cand): return ImageFont.truetype(cand, s, index=0)
    return ImageFont.load_default()


def get_json(name):
    if LOCAL: return json.load(open(os.path.join(LOCAL, name), encoding="utf-8"))
    with urllib.request.urlopen(f"{SITE}/{name}") as r: return json.loads(r.read().decode("utf-8"))


_HD, _JS = {}, {}


def get_json_cached(name):
    if name not in _JS: _JS[name] = get_json(name)
    return _JS[name]



def sprite(key):
    """ポケモンの絵。2026-11-16 てこ入れ：本番では小さいドット絵ではなく大きな公式イラストを使う（取れなければドット絵）"""
    if not LOCAL and os.environ.get("HD_ART", "1") == "1":
        if key not in _HD:
            _HD[key] = None
            try:
                pid = int(get_json_cached("pokedex_stats.json")[key]["id"])
                with urllib.request.urlopen(f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pid}.png", timeout=20) as r:
                    _HD[key] = Image.open(io.BytesIO(r.read())).convert("RGBA")
            except Exception as e: print("公式イラストなし", key, repr(e)[:80])
        if _HD[key] is not None: return _HD[key].copy()
    try:
        if LOCAL: return Image.open(os.path.join(LOCAL, "pokemon_sprites", key + ".png")).convert("RGBA")
        with urllib.request.urlopen(f"{SITE}/pokemon_sprites/{urllib.parse.quote(key)}.png") as r:
            return Image.open(io.BytesIO(r.read())).convert("RGBA")
    except Exception as e:
        print("sprite error", key, e); return None


def big(sp, size):
    bb = sp.getbbox() or (0, 0, sp.width, sp.height)
    sp = sp.crop(bb); s = size / max(sp.size)
    return sp.resize((max(1, int(sp.width * s)), max(1, int(sp.height * s))), Image.NEAREST if max(sp.size) < 200 else Image.LANCZOS)


def silhouette(sp, color=(30, 30, 40)):
    a = sp.split()[3]; im = Image.new("RGBA", sp.size, color + (0,)); im.putalpha(a); return im


def ename(k):
    special = {"mr. mime": "Mr. Mime", "mr. rime": "Mr. Rime", "mime jr.": "Mime Jr.", "farfetchd": "Farfetch'd", "sirfetchd": "Sirfetch'd",
               "nidoranf": "Nidoran♀", "nidoranm": "Nidoran♂", "ho-oh": "Ho-Oh", "porygon-z": "Porygon-Z", "type-null": "Type: Null"}
    return special.get(k, "-".join(p.capitalize() for p in k.split("-")))


def short_origin(t):
    t = re.sub(r"^英語名「[^」]*」は、", "", t.split("。")[0])
    t = re.sub(r"を組み合わせた名前と考えられている$", "", t)
    return re.sub(r"(と考えられている|とされる|である)$", "", t)


NG_HEAD = "、。，．」』）〕！？ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮー…・"


def _kind(c):
    if "ぁ" <= c <= "ゖ": return "h"
    if c in "、。，．！？」』）…": return "p"
    return "o"


def _phrases(text):
    """文節くらいの単位に分ける。ひらがな（や句読点）の直後に漢字・カタカナ・英字・「（が来る所でだけ区切る。
    英単語と（ ）の中は1つのかたまりにする"""
    out, cur, i = [], "", 0
    while i < len(text):
        c = text[i]
        if c == "（":                                    # （ ）は丸ごと前にくっつける
            j = text.find("）", i); j = len(text) - 1 if j < 0 else j
            cur += text[i:j + 1]; i = j + 1; continue
        # 「吸い取る」「組み合わせる」のような複合動詞は、送りがなの後でも切らない
        compound = (len(cur) >= 2 and cur[-1] in "いきしちにみりびぎ" and _kind(cur[-2]) == "o" and c in "取込出上下合付続返切直始回抜入替立掛")
        if cur and _kind(cur[-1]) in "hp" and _kind(c) == "o" and c not in NG_HEAD and not compound:
            out.append(cur); cur = ""
        cur += c; i += 1
    if cur: out.append(cur)
    return out


def _split_long(d, s, font, maxw):
    """1つの文節が1行に入らないときだけ、字で折る（行頭に句読点や小さい字を置かない）"""
    out = []
    while d.textlength(s, font=font) > maxw:
        k = len(s)
        while k > 1 and d.textlength(s[:k], font=font) > maxw: k -= 1
        while k > 1 and s[k] in NG_HEAD: k -= 1
        while k > 1 and s[k - 1].isascii() and s[k].isascii() and s[k].isalpha(): k -= 1   # 英単語の途中で切らない
        out.append(s[:k]); s = s[k:]
    return out + [s]


def jwrap(d, text, font, maxw):
    """日本語の折り返し（指示書：単語・数字・（ ）の途中や、句読点だけの行・行頭の句読点を作らない）"""
    lines = []
    for para in text.split("\n"):
        cur = ""
        for ph in _phrases(para):
            if d.textlength(cur + ph, font=font) <= maxw: cur += ph; continue
            k = cur.rfind("、")                       # 行の後半に読点があれば、そこで切ってバランスを取る
            if 0 < k < len(cur) - 1 and k >= len(cur) * 0.5 and d.textlength(cur[k + 1:] + ph, font=font) <= maxw:
                lines.append(cur[:k + 1]); cur = cur[k + 1:] + ph; continue
            if cur: lines.append(cur); cur = ""
            parts = _split_long(d, ph, font, maxw)
            lines += parts[:-1]; cur = parts[-1]
        if cur: lines.append(cur)
    return lines


def ewrap(d, text, font, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines


def center(d, y, text, font, fill, stroke=0, sfill=None):
    d.text((VW // 2, y), text, font=font, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=sfill)


# ---------- ナレーション（VOICEVOX） ----------
def tts(text, speaker, speed=1.0, pitch=0.0, intonation=1.0):
    """読み上げ音声を numpy 配列（44.1kHz, -1〜1）で返す。エンジンが無ければ None"""
    try:
        try:
            import yomi; yomi.prepare(VV, text)    # ポケモン名をユーザー辞書に（崩れる名前だけ）
        except Exception:
            pass
        q = urllib.request.urlopen(urllib.request.Request(
            f"{VV}/audio_query?" + urllib.parse.urlencode({"text": text, "speaker": speaker}), method="POST"), timeout=60).read()
        q = json.loads(q)
        q.update(speedScale=speed, pitchScale=pitch, intonationScale=intonation, outputSamplingRate=SR, volumeScale=1.3,
                 prePhonemeLength=0.05, postPhonemeLength=0.15)
        wav = urllib.request.urlopen(urllib.request.Request(f"{VV}/synthesis?speaker={speaker}", data=json.dumps(q).encode(),
                                                            headers={"Content-Type": "application/json"}), timeout=120).read()
        with wave.open(io.BytesIO(wav)) as w:
            a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
            if w.getnchannels() == 2: a = a.reshape(-1, 2).mean(axis=1)
        return a
    except Exception as e:
        print("VOICEVOX なし:", repr(e)[:120]); return None


def voice_text(s):
    """英単語＋（意味）の形は、日本語の意味だけ読む"""
    s = s.replace("「！」", "びっくりマーク").replace("「？」", "はてなマーク")
    s = re.sub(r"[A-Za-z][A-Za-z' .\-]*（([^）]+)）", r"\1", s)
    s = re.sub(r"[A-Za-z][A-Za-z'\-]*", "", s)
    return re.sub(r"\s+", "", s)


# ---------- 出題 ----------
import functools


@functools.lru_cache(maxsize=None)
def origin_fits(s):
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    return any(len(jwrap(d, s, F(F_ROUND, z), 650)) <= 3 for z in range(44, 29, -2))


def pick(n, names, origins, stats, en):
    ids = {k: int(stats[k]["id"]) for k in en if k in stats and k in names}
    if n % 2 == 0:
        pool = [k for k in ids if k in origins and ids[k] <= 493 and ("組み合わせ" in origins[k]["t"] or "もじ" in origins[k]["t"])
                and origins[k]["t"].startswith("英語名") and origin_fits(short_origin(origins[k]["t"]))]   # 由来が画面に収まるものだけ（途中で切らない）
        pool.sort(key=lambda k: ids[k]); random.Random(20261114).shuffle(pool)
        return dict(kind="name", key=pool[(n // 2) % len(pool)])
    pool = [k for k in SCARY if k in ids]
    return dict(kind="scary", key=pool[(n // 2) % len(pool)])


def scary_text(key, en, jp):
    kw = r"dead|death|deceased|die|soul|skull|kidnap|curse|blood|bones|grudge|afterlife|drag|wither|life|lives|victim|prey|melt|dissolve|spirit|ghost|haunt|child"
    strong = r"death|dead|deceased|die|skull|kidnap|wither|victim|bones|melt|dissolve|blood|grudge|afterlife|drag|lives|life-force|soul"
    es = [s for s in re.split(r"(?<=[.!?])\s+", en[key].replace("\n", " ")) if s]
    js = [s for s in re.split(r"(?<=[。！？])", jp.get(key, "")) if s.strip()]
    i = max(range(len(es)), key=lambda j: (3 * len(re.findall(strong, es[j], re.I)) + len(re.findall(kw, es[j], re.I)), -j))
    two = len(es[i]) < 40 and i + 1 < len(es) and len(es[i]) + len(es[i + 1]) < 120
    sent = " ".join(es[i:i + 2]) if two else es[i]
    if len(js) == len(es): ja = "".join(js[i:i + 2]) if two else js[i]
    else: ja = "".join(js)
    return sent, ja


# ---------- 英語名シルエットクイズ ----------
BG1, RED, YEL, DARK, WHITE = (255, 214, 64), (227, 53, 13), (255, 240, 170), (31, 41, 51), (255, 255, 255)


def fit(d, text, path, size, maxw, minsize=40):
    """枠からはみ出さない大きさのフォントを返す（指示書：文字を枠からはみ出させない）"""
    f = F(path, size)
    while size > minsize and d.textlength(text, font=f) > maxw: size -= 4; f = F(path, size)
    return f


def ruby(d, cx, y, key, fill=DARK, size=50, path=None, box=True):
    """英語名の下に発音のカタカナを振る（指示書：英語名とその発音を入れる）"""
    k = kana(key)
    if not k: return
    f = fit(d, k, path or F_ROUND, size, VW - 220)
    w = d.textlength(k, font=f)
    if box: d.rounded_rectangle([cx - w / 2 - 28, y - size * 0.72, cx + w / 2 + 28, y + size * 0.72], int(size * 0.7), fill=WHITE)
    d.text((cx, y), k, font=f, fill=fill, anchor="mm")


def footer_left(d, l1, l2, top=VH - 230, bg=DARK, c1=WHITE, c2=YEL):
    """下の帯。右下はずんだもんが立つので、文字は左に寄せる"""
    d.rectangle([0, top, VW, VH], fill=bg)
    d.text((50, top + 80), l1, font=fit(d, l1, F_ROUND, 46, 700), fill=c1, anchor="lm")
    d.text((50, top + 150), l2, font=fit(d, l2, F_ROUND, 46, 700), fill=c2, anchor="lm")


def name_scene(q, sp, phase, count=None):
    im = Image.new("RGB", (VW, VH), BG1); d = ImageDraw.Draw(im)
    for k in range(14):
        a0 = k * (360 / 14); d.pieslice([-900, -500, VW + 900, VH + 900], a0, a0 + 360 / 28, fill=(255, 200, 40))
    d.rectangle([0, 0, VW, 190], fill=RED); center(d, 95, "英語名クイズ", F(F_DELA, 84), WHITE)
    footer_left(d, "全1000匹の英語名と由来は", "poketango.com")
    E, J = ename(q["key"]), q["jn"]
    center(d, 300, "この英語名、だーれだ？" if phase != "reveal" else "正解は…", F(F_ROUND, 72), DARK)
    center(d, 470, E, fit(d, E, F_DELA, 150, VW - 120, 80), WHITE, stroke=14, sfill=DARK)
    ruby(d, VW // 2, 600, q["key"])
    cx, cy = VW // 2, 1000
    if sp:
        s = big(sp, 560); img = s if phase == "reveal" else silhouette(s)
        d.ellipse([cx - 330, cy - 330, cx + 330, cy + 330], fill=WHITE)
        im.paste(img, (cx - img.width // 2, cy - img.height // 2), img)
    if phase == "q" and count:
        d.ellipse([VW // 2 - 80, 1350, VW // 2 + 80, 1510], fill=RED)
        d.text((VW // 2, 1430), str(count), font=F(F_DELA, 110), fill=WHITE, anchor="mm")
    if phase == "reveal":
        center(d, 1410, J + "！", fit(d, J + "！", F_DELA, 110, VW - 120), RED, stroke=10, sfill=WHITE)
        o = q.get("origin", "")
        if o:
            size = 44                       # 途中で切らずに全部入るまで字を小さくする（3行まで）
            while True:
                f = F(F_ROUND, size); lines = jwrap(d, o, f, 650)
                if len(lines) <= 3 or size <= 30: break
                size -= 2
            lh = int(size * 1.36)
            d.rounded_rectangle([50, 1480, 760, 1480 + lh * len(lines) + 30], 30, fill=WHITE)
            for k, ln in enumerate(lines): d.text((80, 1495 + k * lh + lh // 2), ln, font=f, fill=DARK, anchor="lm")
    return im


def name_video(q, sp):
    """(フレームを返す関数, 秒数) の並びと、ナレーションの配置を返す"""
    k = kana(q["key"])
    v1 = tts(f"この英語名、{k}。だーれだ？" if k else "この英語名のポケモン、だーれだ？", ZUNDA, SPEED)
    vo = voice_text(q.get("origin", ""))
    v2 = tts(f"正解は、{q['jn']}なのだ！" + (f"{vo}、が由来なのだ。" if vo else ""), ZUNDA, SPEED)
    intro = max(1.6, (len(v1) / SR + 0.3) if v1 is not None else 0)
    rev = max(5.0, (len(v2) / SR + 0.7) if v2 is not None else 0)
    imgs = {"i": name_scene(q, sp, "intro"), 3: name_scene(q, sp, "q", 3), 2: name_scene(q, sp, "q", 2), 1: name_scene(q, sp, "q", 1),
            "r": name_scene(q, sp, "reveal")}
    segs = [(lambda t: imgs["i"], intro), (lambda t: imgs[3], 1.0), (lambda t: imgs[2], 1.0), (lambda t: imgs[1], 1.0), (lambda t: imgs["r"], rev)]
    voices = [(0.1, v1, "happy"), (intro + 3.0 + 0.2, v2, "proud")]
    return segs, voices, imgs["i"]


# ---------- 英語版の図鑑が怖すぎる（ホラー演出） ----------
BLOOD, BONE = (190, 10, 20), (232, 226, 214)
rng = np.random.default_rng(7)
GRAIN = [Image.fromarray((rng.integers(0, 255, (VH // 4, VW // 4), dtype=np.uint8))).resize((VW, VH), Image.NEAREST) for _ in range(6)]


def vignette():
    y, x = np.ogrid[:VH, :VW]
    r = np.sqrt(((x - VW / 2) / (VW * 0.62)) ** 2 + ((y - VH * 0.42) / (VH * 0.55)) ** 2)
    a = np.clip((r - 0.45) * 1.6, 0, 1) * 255
    return Image.fromarray(a.astype(np.uint8))


VIG = vignette()


SCARY_WORDS = r"\b(?:death|dead|deceased|die|skull|kidnap|curse|blood|bone|grudge|afterlife|drag|wither|life|soul|victim|prey|melt|dissolv|spirit|ghost|haunt|lick|kill|scream|darkness)"


def horror_sprite(sp):
    s = big(sp, 560)
    rgb = s.convert("RGB"); gray = ImageOps.grayscale(rgb)
    tinted = ImageOps.colorize(gray, black=(10, 0, 0), white=(235, 205, 200)).convert("RGBA")
    tinted.putalpha(s.split()[3])
    return s, tinted


def horror_frame(q, spr, t, total, state):
    """t秒目のフレーム。state: 英文の表示割合など"""
    im = Image.new("RGB", (VW, VH), (6, 3, 5)); d = ImageDraw.Draw(im)
    # 赤い霧
    glow = Image.new("RGB", (VW, VH), (0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse([VW / 2 - 520, 380, VW / 2 + 520, 1300], fill=(70, 0, 8))
    im = Image.blend(im, glow.filter(ImageFilter.GaussianBlur(120)), 0.9); d = ImageDraw.Draw(im)
    # ポケモン：止めて見せる（指示書：画像を揺らしたりゆっくりズームしたりしない）。ときどき本来の色が一瞬だけ見え、最後に一度だけ飛び出す
    if spr:
        s, tinted = spr
        z = 1.0
        if state.get("lunge"): z = 1.9
        w, h = int(tinted.width * z), int(tinted.height * z)
        flick = (int(t * FPS) % 37 == 0)
        src = s if flick else tinted
        img = src.resize((w, h), Image.NEAREST)
        jx = jy = 0
        y0 = 760 if not state.get("lunge") else 900
        shadow = silhouette(img, (120, 0, 10)).filter(ImageFilter.GaussianBlur(28))
        im.paste(shadow, (VW // 2 - w // 2 + jx, y0 - h // 2 + jy + 10), shadow)
        im.paste(img, (VW // 2 - w // 2 + jx, y0 - h // 2 + jy), img)
    # 粒子ノイズ・周辺を暗く・走査線（文字より先にかけて、文字は読みやすく保つ）
    im = Image.composite(Image.new("RGB", (VW, VH), (0, 0, 0)), im, VIG)
    im = Image.blend(im, GRAIN[int(t * FPS) % len(GRAIN)].convert("RGB"), 0.07)
    d = ImageDraw.Draw(im)
    for yy in range(0, VH, 6): d.line([(0, yy), (VW, yy)], fill=(0, 0, 0), width=1)
    d = ImageDraw.Draw(im)
    # 見出し（ときどきグリッチ）
    title = "英語版の図鑑が怖すぎる"
    gx = int(rng.integers(-14, 14)) if int(t * FPS) % 9 == 0 else 0
    tf = F(FONT_M, 80)
    d.text((VW // 2 + gx - 5, 140), title, font=tf, fill=(0, 160, 170), anchor="mm")
    d.text((VW // 2 + gx + 5, 140), title, font=tf, fill=(120, 0, 0), anchor="mm")
    d.text((VW // 2 + gx, 140), title, font=tf, fill=(235, 30, 40), anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))
    d.text((VW // 2, 245), f"{q['jn']}　{ename(q['key'])}", font=F(FONT_M, 54), fill=BONE, anchor="mm")
    if kana(q["key"]) and not same_as_jp(q["key"], q["jn"]):
        d.text((VW // 2, 310), f"英語名の発音 {kana(q['key'])}", font=F(FONT_M, 36), fill=(170, 150, 150), anchor="mm")
    # 英文：タイプライターで1文字ずつ。怖い単語は赤
    n = int(len(q["sent"]) * state.get("en", 0))
    if n:
        f = F(FONT_B, 56); left = n
        en_lines = ewrap(d, q["sent"], f, VW - 110)[:5]; y = 1090
        for ln in en_lines:
            if left <= 0: break
            words = ln.split(" "); full = d.textlength(ln, font=f); x = VW / 2 - full / 2
            for w in words:
                part = w[:max(0, left)]; left -= len(w) + 1
                if part:
                    hot = re.search(SCARY_WORDS, w, re.I)
                    d.text((x, y), part, font=f, fill=(255, 40, 40) if hot else BONE, anchor="lm")
                if len(part) < len(w) or left <= 0:
                    if n < len(q["sent"]): d.text((x + d.textlength(part, font=f), y), "▌", font=f, fill=BONE, anchor="lm")
                    break
                x += d.textlength(w + " ", font=f)
            y += 74
    # 日本語訳：じわっと出る
    a = state.get("ja", 0)
    if a > 0:
        fj = F(FONT_M, 64); lines = jwrap(d, q["ja"], fj, VW - 130)[:4]
        y = 1090 + 74 * len(ewrap(d, q["sent"], F(FONT_B, 56), VW - 110)[:5]) + 50
        col = tuple(int(c * a) for c in (255, 235, 230)); glow = tuple(int(c * a) for c in (170, 0, 0))
        for ln in lines:
            d.text((VW // 2, y), ln, font=fj, fill=col, anchor="mm", stroke_width=6, stroke_fill=glow); y += 88
    # 最後のひとこと
    if state.get("end"):
        d.text((VW // 2, 1500), "…あなたの後ろにも。", font=F(FONT_M, 84), fill=(240, 30, 40), anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
    d.rectangle([0, VH - 170, VW, VH], fill=(10, 0, 0))
    d.text((VW // 2, VH - 120), "英語版の図鑑の和訳は", font=F(FONT_B, 40), fill=(170, 150, 150), anchor="mm")
    d.text((VW // 2, VH - 65), "プロフィールのサイトで", font=F(FONT_B, 40), fill=BLOOD, anchor="mm")
    if state.get("flash"):  # 赤い閃光
        im = Image.blend(im, Image.new("RGB", (VW, VH), (200, 0, 0)), 0.55)
    return im


def scary_video(q, sp):
    spr = horror_sprite(sp) if sp else None
    vja = tts(q["ja"], METAN, 0.95, -0.06, 0.6)
    t_type = min(4.5, 1.2 + len(q["sent"]) / 30)      # 英文のタイプ時間
    t_ja = max(4.5, (len(vja) / SR + 0.8) if vja is not None else 0)
    total = 1.0 + t_type + 1.0 + t_ja + 1.6

    def seg_intro(t):
        st = {"flash": int(t * FPS) in (3, 4, 9)}
        return horror_frame(q, spr, t, total, st)

    def seg_type(t):
        return horror_frame(q, spr, 1.0 + t, total, {"en": min(1, t / (t_type - 0.4))})

    def seg_hold(t):
        return horror_frame(q, spr, 1.0 + t_type + t, total, {"en": 1})

    def seg_ja(t):
        return horror_frame(q, spr, 2.0 + t_type + t, total, {"en": 1, "ja": min(1, t / 0.8)})

    def seg_end(t):
        lunge = t > 0.55
        return horror_frame(q, spr, total - 1.6 + t, total, {"en": 0, "ja": 0, "end": not lunge, "lunge": lunge, "flash": 0.55 < t < 0.75})
    segs = [(seg_intro, 1.0), (seg_type, t_type), (seg_hold, 1.0), (seg_ja, t_ja), (seg_end, 1.6)]
    voices = [(2.0 + t_type + 0.3, vja, None)]
    thumb = horror_frame(q, spr, total * 0.7, total, {"en": 1, "ja": 1})
    return segs, voices, thumb


# ---------- 音 ----------
def bgm(kind, dur, marks):
    n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n, dtype=np.float32)

    def put(t0, sig):
        a = int(t0 * SR); b = min(n, a + len(sig))
        if a < n: out[a:b] += sig[:b - a]

    def tone(freq, length, vol, shape="sq"):
        tt = np.arange(int(length * SR)) / SR; ph = (tt * freq) % 1
        v = np.where(ph < 0.5, 1, -1) if shape == "sq" else np.sin(2 * np.pi * ph)
        env = np.minimum(1, tt * 200) * np.clip(1 - tt / length, 0, 1) ** 0.7
        return (v * env * vol).astype(np.float32)
    if kind == "name":
        # 2026-11-14 BGMと効果音を毎回ちがう自作のものにした（music.py）
        import music
        out += music.bgm(STYLE, dur)[:n]; fx = music.SFX_SETS[STYLE["sfx"]]
        import sfx; put(0.02, sfx.load("impact", SR)[0] * 0.8)   # 冒頭の一発（2026-11-16 の分析）
        for s in range(3): put(marks["count"] + s, fx["tick"]())
        put(marks["reveal"], fx["ding"]())
    else:
        # 低いうなり＋不協和音＋心臓の鼓動＋最後に衝撃音
        r = random.Random(STYLE["seed"]); f0 = r.choice([41.2, 46.2, 49.0, 55.0, 61.7]); bt = r.uniform(0.8, 4.0)
        out += (0.10 * np.sin(2 * np.pi * f0 * t) + 0.06 * np.sin(2 * np.pi * (f0 + bt) * t) + 0.05 * np.sin(2 * np.pi * f0 * 1.5 * t * (1 + 0.002 * np.sin(t)))).astype(np.float32)
        out += (0.025 * np.sin(2 * np.pi * 466 * t + 3 * np.sin(2 * np.pi * 0.3 * t)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.17 * t))).astype(np.float32)
        hb = np.arange(int(0.12 * SR)) / SR
        beat = (np.sin(2 * np.pi * 50 * hb) * np.exp(-hb * 30) * 0.5).astype(np.float32)
        x = 0.5; bpm = 60
        while x < dur - 1.8:
            put(x, beat); put(x + 0.22, beat * 0.7); bpm = min(130, bpm + 4); x += 60 / bpm
        nz = np.arange(int(1.2 * SR)) / SR
        hit = ((np.random.default_rng(1).standard_normal(len(nz)) * 0.5 + np.sin(2 * np.pi * 40 * nz)) * np.exp(-nz * 3) * 0.6).astype(np.float32)
        put(marks["hit"], hit)
        sw = np.arange(int(0.9 * SR)) / SR
        put(0.05, (np.sin(2 * np.pi * (2000 - 1800 * sw) * sw) * np.exp(-sw * 4) * 0.15).astype(np.float32))
    return out


def render(segs, voices, kind, marks, out):
    os.makedirs("_f", exist_ok=True)
    parts = []
    talker = None
    if any(v is not None and f for _, v, f in voices):     # しゃべる立ち絵（ずんだもん）を右下に重ねる
        import chara_overlay
        talker = chara_overlay.Talker()
        for t0, v, f in voices:
            if f: talker.add(t0, v, f)
        T0 = 0.0; wrapped = []
        for fn, dur in segs:
            wrapped.append((lambda t, fn=fn, T0=T0: talker.draw(fn(t), T0 + t), dur)); T0 += round(dur * FPS) / FPS
        segs = wrapped
    for k, (fn, dur) in enumerate(segs):
        nfr = max(1, int(round(dur * FPS)))
        first = fn(0.0); still = all(fn(i / FPS) is first for i in (1, nfr // 2)) if nfr > 2 else True
        if still:
            first.save(f"_f/s{k}.png")
            cmd = ["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS), "-i", f"_f/s{k}.png", "-t", f"{nfr / FPS:.3f}"]
        else:
            for i in range(nfr): fn(i / FPS).save(f"_f/s{k}_{i:04d}.png")
            cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"_f/s{k}_%04d.png"]
        cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-r", str(FPS), f"_f/s{k}.mp4"]
        subprocess.run(cmd, check=True); parts.append(f"_f/s{k}.mp4")
    open("_list.txt", "w").write("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "_list.txt", "-c", "copy", "_v.mp4"], check=True)
    total = sum(round(d * FPS) / FPS for _, d in segs)
    mix = bgm(kind, total, marks)
    for t0, v, _ in voices:
        if v is None: continue
        a = int(t0 * SR); b = min(len(mix), a + len(v))
        mix[a:b] = mix[a:b] * 0.45 + v[:b - a]          # 声の間はBGMを下げる
    mix = np.clip(mix, -1, 1)
    with wave.open("_a.wav", "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 30000).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "_v.mp4", "-i", "_a.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", out], check=True)


def build(q, out):
    sp = sprite(q["key"])
    if q["kind"] == "name":
        segs, voices, thumb = name_video(q, sp)
        intro = segs[0][1]; marks = {"count": intro, "reveal": intro + 3.0}
    else:
        segs, voices, thumb = scary_video(q, sp)
        marks = {"hit": sum(d for _, d in segs) - 1.6 + 0.55}
    render(segs, voices, q["kind"], marks, out)
    thumb.save("thumb.png")
    return any(v is not None for _, v, _ in voices)


def meta(q, voiced):
    page = f"{SITE}/p/{q['key'].replace(' ', '_').replace('.', '')}.html"
    credit = ("\n\nナレーション：VOICEVOX:ずんだもん\n立ち絵：坂本アヒル様" if q["kind"] == "name" else "\n\nナレーション：VOICEVOX:四国めたん") if voiced else ""
    credit += ("\n" if credit else "\n\n") + "効果音：OtoLogic（https://otologic.jp）"   # 冒頭の衝撃音（sfx.py）
    if q["kind"] == "name":
        title = f"この英語名、どのポケモン？「{ename(q['key'])}」【英語名クイズ】 #shorts"
        pron = f"（発音：{kana(q['key'])}）" if kana(q["key"]) else ""
        desc = (f"正解は{q['jn']}！\n{ename(q['key'])}{pron}\n英語名の由来：{q.get('origin', '')}\n\n{q['jn']}の英語版図鑑と日本語訳 → {page}\n"
                f"英語名がダジャレなポケモンまとめ → {SITE}/p/pun.html\n"
                f"📚 ポケモン図鑑で覚える英単語(中1〜大学) → {SITE}/p/words.html\n🖨️ 無料の英単語プリント → {SITE}/p/print.html{credit}\n\n#ポケモン #ポケモン英語 #英語名")
    else:
        title = f"英語版のポケモン図鑑が怖すぎる…【{q['jn']}】 #shorts"
        desc = (f"英語版の図鑑より\n{q['sent']}\n→ {q['ja']}\n\n{q['jn']}の英語版図鑑と日本語訳 → {page}\n"
                f"英語版の図鑑が怖すぎるポケモンまとめ → {SITE}/p/scary.html\n"
                f"📚 ポケモン図鑑で覚える英単語(中1〜大学) → {SITE}/p/words.html{credit}\n\n#ポケモン #ポケモン図鑑 #ホラー")
    return title[:100], desc


def tag_links(text, source="youtube", medium="video", campaign="eitango"):
    """概要欄の poketango.com のリンクに、どこから来たか分かる目印（utm）を付ける。Googleアナリティクスで流入元を見分けるため"""
    q = f"utm_source={source}&utm_medium={medium}&utm_campaign={campaign}"
    return re.sub(r"(https://poketango\.com[^\s?#）)]*)", lambda m: m.group(1) + "?" + q, text)


def post_youtube(title, desc, mp4, campaign="eitango"):
    desc = tag_links(desc, campaign=campaign)
    cid, cs, rt = (re.sub(r"\s", "", os.environ.get(x) or "") for x in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"))
    if not all((cid, cs, rt)): print("YouTube: 鍵が未設定なのでスキップ"); return
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build as gbuild
    from googleapiclient.http import MediaFileUpload
    cred = Credentials(None, refresh_token=rt, token_uri="https://oauth2.googleapis.com/token", client_id=cid, client_secret=cs,
                       scopes=["https://www.googleapis.com/auth/youtube.upload"])
    yt = gbuild("youtube", "v3", credentials=cred)
    body = {"snippet": {"title": title, "description": desc, "categoryId": "20", "defaultLanguage": "ja",
                        "tags": ["ポケモン", "ポケモン英語", "英語名", "ポケモン図鑑", "Pokemon"]},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}}
    r = yt.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(mp4, mimetype="video/mp4")).execute()
    print("YouTube:", r.get("id"), r.get("status", {}).get("privacyStatus"))
    thumb = os.environ.get("THUMB")
    if thumb and os.path.exists(thumb) and r.get("id"):
        try:   # サムネイルの設定は、電話番号で確認済みのチャンネルだけできる。できなければ自動のサムネイルのまま
            yt.thumbnails().set(videoId=r["id"], media_body=MediaFileUpload(thumb)).execute(); print("サムネイルを設定しました")
        except Exception as e:
            print("サムネイルは設定できませんでした:", str(e)[:150])
    return r.get("id")


def slot_now(now):
    # 日本時間 7時台／12時台／19時台 の実行を 0／1／2 番目とみなす
    return 0 if now.hour < 10 else (1 if now.hour < 16 else 2)


# 2026-11-14 型を7つに増やし、投稿ごとに順番に回す（どの型が伸びるかを比べるため）
KINDS = ["name", "plus", "scary", "real3", "speed5", "which", "rank"]
STYLE = None
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shorts_log.jsonl")   # 型の比べ用の記録

if __name__ == "__main__":
    en, jp, names, stats, origins = (get_json(n) for n in ("pokedex_en.json", "pokedex_jp.json", "pokemon_names_jp.json", "pokedex_stats.json", "name_origins.json"))
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(hours=9)
    n = int(os.environ["N"]) if os.environ.get("N") else (now.date() - START).days * SLOTS_PER_DAY + slot_now(now)
    kind = os.environ.get("KIND") or KINDS[n % len(KINDS)]
    # 2026-11-16 てこ入れ：夜19:05の回は、掛け合いの新しい型「英語名の意味」を出す（台本 talk/ が残っているかぎり）
    import talk
    try: done0 = {json.loads(l)["title"] for l in open(LOG, encoding="utf-8") if l.strip()}
    except Exception: done0 = set()
    tpath, TS = talk.next_script(done0)
    if (os.environ.get("KIND") == "talk") or (not os.environ.get("KIND") and slot_now(now) == 2 and TS is not None):
        kind = "talk"
    m = n // len(KINDS)
    import music
    STYLE = music.style(n * 101 + (KINDS.index(kind) if kind in KINDS else 7), "quiz")
    bgm_label = music.label(STYLE) if kind != "scary" else "horror/" + str(STYLE["seed"])
    # 指示書：同じ内容のショートは二度と上げない。これまでに出した題名と同じになる出題は飛ばす
    try: done = {json.loads(l)["title"] for l in open(LOG, encoding="utf-8") if l.strip()}
    except Exception: done = set()
    import formats
    D = dict(en=en, jp=jp, names=names, stats=stats, origins=origins)
    if kind == "talk":
        if TS is None: print("掛け合いの台本が残っていません"); sys.exit(1)
        print("台本:", tpath)
        talk.build(TS, "short.mp4", seed=n)
        title, desc = talk.meta(TS)
        import end_card; end_card.add("short.mp4")
        print(kind, n); print(title); print(desc)
        if os.environ.get("DRY_RUN") == "1": sys.exit()
        vid = post_youtube(title, desc, "short.mp4")
        line = json.dumps({"date": now.strftime("%Y-%m-%d %H:%M"), "n": n, "kind": kind, "id": vid, "title": title, "bgm": music.label(music.style(n, "quiz"))}, ensure_ascii=False) + "\n"
        open("/tmp/new_log_line", "w", encoding="utf-8").write(line)
        sys.exit()
    for skip in range(200):
        mm = m + skip
        if kind in ("name", "scary"):
            q = pick(2 * (mm + 1) + (kind == "scary"), names, origins, stats, en)   # 11-14朝・昼に出した1本目どうしを飛ばす
            q["jn"] = names[q["key"]]
            if q["kind"] == "name": q["origin"] = short_origin(origins[q["key"]]["t"])
            else: q["sent"], q["ja"] = scary_text(q["key"], en, jp)
            title, desc = meta(q, True)
        else:
            q = formats.pick(kind, mm, D); title, desc = formats.meta(kind, q, D)
        if title not in done: break
        print("出したことのある題名なので飛ばす:", title)
    print(json.dumps(q, ensure_ascii=False))
    if kind in ("name", "scary"):
        voiced = build(q, "short.mp4")
        title, desc = meta(q, voiced)
    else:
        formats.make(kind, mm, D, "short.mp4", seed=n * 101 + KINDS.index(kind), q=q)
        bgm_label = music.label(formats.STYLE) if kind != "rank" else "horror/" + str(formats.STYLE["seed"])
        voice = "VOICEVOX:四国めたん" if kind == "rank" else "VOICEVOX:ずんだもん\n立ち絵：坂本アヒル様"
        desc += f"\n\nナレーション：{voice}"
    import end_card; end_card.add("short.mp4")   # 最後にサイトのアドレスとホーム画面（2026-11-16 検索からアドレス表示へ）
    print(kind, n); print(title); print(desc)
    print("BGM:", bgm_label)
    if os.environ.get("DRY_RUN") == "1": sys.exit()
    vid = post_youtube(title, desc, "short.mp4")
    line = json.dumps({"date": now.strftime("%Y-%m-%d %H:%M"), "n": n, "kind": kind, "id": vid, "title": title, "bgm": bgm_label}, ensure_ascii=False) + "\n"
    open("/tmp/new_log_line", "w", encoding="utf-8").write(line)
    with open(LOG, "a", encoding="utf-8") as fp:
        fp.write(json.dumps({"date": now.strftime("%Y-%m-%d %H:%M"), "n": n, "kind": kind, "id": vid, "title": title, "bgm": bgm_label}, ensure_ascii=False) + "\n")
