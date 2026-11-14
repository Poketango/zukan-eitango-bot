# ずんだもんと冥鳴ひまりの「ポケモン雑学」まとめ（横動画 1920x1080・毎日 19:35）
#   ・台本は scripts/long/NNNN.json（裏どりした雑学を人が書く／Claude が毎日書き足す）
#       NNNN は 2026-11-13 からの日数（0000＝11-13、0001＝11-14）。台本が無い日は投稿しない（品質を保つため）
#   ・画像は assets/img/ に置く（art_25.png＝公式イラスト、rb_＝赤緑、gold_＝金銀、frlg_＝ファイアレッドのドット絵）
#   ・台本の各せりふに "img": ["art:25|説明", ...] を付けると、その画像を出す（次に指定があるまで出し続ける）
import os, re, sys, json, random, datetime, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import post as P
import zatsugaku as Z

W, H, FPS, SR = 1920, 1080, 24, P.SR
F, FONT_B, FONT_K = P.F, P.FONT_B, P.FONT_K
CHAR = Z.CHAR
HERE = Z.HERE
START = datetime.date(2026, 11, 13)    # 回番号0の日（2026-11-14 から毎日更新）
N_TOPICS = 6
PIXEL_KINDS = ("rb", "gold", "frlg")


def say_fix(s):
    """読み上げで記号やアルファベットが飛ばないようにする"""
    s = s.replace("「！」", "びっくりマーク").replace("「？」", "はてなマーク")
    s = re.sub(r"『([^』]*)』", r"\1", s)
    s = re.sub(r"([0-9０-９一二三四五六七八九十百千]+)文字", r"\1もじ", s)      # 「十文字」を「じゅうもんじ」と読まないように
    return s


# ---------- フォント ----------
FONT_DIR = os.path.join(HERE, "fonts")
FD, FR, FRB, FPOP, FROCK = ("DelaGothicOne-Regular.ttf", "MPLUSRounded1c-ExtraBold.ttf", "MPLUSRounded1c-Black.ttf",
                            "MochiyPopOne-Regular.ttf", "RocknRollOne-Regular.ttf")
_FF = {}


def FF(name, size):
    k = (name, size)
    if k not in _FF:
        try: _FF[k] = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
        except Exception: _FF[k] = F(FONT_K, size)
    return _FF[k]


# 話題ごとに色を変える（ヘッダー、アクセント、強調）
THEMES = [((124, 78, 178), (96, 176, 56), (255, 236, 120)), ((214, 84, 60), (250, 178, 40), (255, 250, 200)),
          ((40, 118, 200), (250, 140, 60), (255, 236, 120)), ((24, 140, 112), (236, 88, 120), (255, 240, 150)),
          ((84, 84, 176), (56, 186, 200), (255, 236, 120)), ((196, 64, 136), (110, 180, 60), (255, 240, 170)),
          ((60, 60, 72), (230, 70, 70), (255, 220, 90))]
RED = (224, 52, 40)


def ease_back(x):
    x = min(max(x, 0.0), 1.0); c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


_BG = {}


def bg(theme=THEMES[0]):
    if theme in _BG: return _BG[theme]
    base = tuple(int(250 * 0.93 + c * 0.07) for c in theme[0])
    dot = tuple(int(b * 0.94) for b in base)
    im = Image.new("RGB", (W, H), base); d = ImageDraw.Draw(im)
    for y in range(0, H, 56):
        for x in range(0 if (y // 56) % 2 else 28, W, 56): d.ellipse([x, y, x + 7, y + 7], fill=dot)
    _BG[theme] = im
    return im


_T, _IMG = {}, {}


def tachie(name, h, dim):
    k = (name, h, dim)
    if k not in _T:
        im = Image.open(os.path.join(HERE, "chara", name + ".png")).convert("RGBA")
        im = im.crop((0, 0, im.width, int(im.height * (0.62 if name == "zundamon" else 0.56))))
        im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
        if dim:
            px = np.array(im).astype(np.float32); px[..., :3] *= 0.62; im = Image.fromarray(px.astype(np.uint8))
        _T[k] = im
    return _T[k]


CREDITS = {}      # ウィキメディア・コモンズの画像の出典（概要欄に書く）
UA = {"User-Agent": "poke-zatsugaku-bot/1.0 (https://poketango.com; YouTube channel video maker)"}


def commons_img(name):
    """ウィキメディア・コモンズの画像を取ってくる（GitHub Actions 上で）。自由なライセンスのものだけ使い、出典を記録する"""
    import urllib.request, urllib.parse, html
    os.makedirs(os.path.join(HERE, "_cache"), exist_ok=True)
    title = "File:" + name.replace("_", " ")
    q = urllib.parse.urlencode(dict(action="query", titles=title, prop="imageinfo", iiprop="url|extmetadata", iiurlwidth=1400, format="json"))
    try:
        with urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + q, headers=UA), timeout=30) as r:
            page = next(iter(json.loads(r.read().decode())["query"]["pages"].values()))
        ii = page["imageinfo"][0]; md = ii.get("extmetadata", {})
        lic = md.get("LicenseShortName", {}).get("value", "")
        if not lic or "fair use" in lic.lower() or "non-free" in lic.lower():
            print("自由なライセンスでないので使わない:", name, lic); return None
        url = ii.get("thumburl") or ii["url"]
        fn = os.path.join(HERE, "_cache", re.sub(r"[^A-Za-z0-9._-]", "_", name))
        if not os.path.exists(fn):
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r: open(fn, "wb").write(r.read())
        artist = re.sub(r"<[^>]+>", "", html.unescape(md.get("Artist", {}).get("value", ""))).strip()
        CREDITS[name] = f"{name}（{artist + '、' if artist else ''}{lic}、ウィキメディア・コモンズ）"
        im = Image.open(fn)
        if im.mode in ("P", "LA", "L"): im = im.convert("RGBA")
        im = im.convert("RGBA")
        if im.getchannel("A").getextrema()[0] == 255:            # 写真は角を丸めて白いふちを付ける
            r = max(8, min(im.size) // 30)
            m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=255)
            im.putalpha(m)
        return im
    except Exception as e:
        print("コモンズの画像を取れない:", name, repr(e)); return None


def word_card(text, sub=""):
    """知らない固有名詞を大きな文字で見せるカード"""
    f = FF(FD, 120)
    while f.getlength(text) > 1000 and f.size > 50: f = FF(FD, f.size - 6)
    w = int(f.getlength(text)) + 140; h = f.size + 120
    im = Image.new("RGBA", (max(w, 500), h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, h - 1], 40, fill=(255, 255, 255), outline=(60, 50, 80), width=8)
    d.text((im.width / 2, h / 2), text, font=f, fill=(40, 34, 50), anchor="mm")
    return im


def color_card(hexcol):
    c = tuple(int(hexcol.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    im = Image.new("RGBA", (420, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 419, 419], 60, fill=c, outline=(60, 50, 80), width=10)
    return im


def flow_card(spec):
    """「光>視細胞>双極細胞>脳」のような流れの図"""
    parts = [x.strip() for x in spec.split(">") if x.strip()]
    f = FF(FPOP, 54)
    boxes = [int(f.getlength(t)) + 80 for t in parts]; gap = 110; h = 170
    W2 = sum(boxes) + gap * (len(parts) - 1) + 20
    im = Image.new("RGBA", (W2, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 10
    cols = [(124, 78, 178), (40, 118, 200), (24, 140, 112), (214, 84, 60), (196, 64, 136), (84, 84, 176)]
    for i, (t, bw) in enumerate(zip(parts, boxes)):
        c = cols[i % len(cols)]
        d.rounded_rectangle([x, 10, x + bw, 10 + h], 36, fill=(255, 255, 255), outline=c, width=10)
        d.text((x + bw / 2, 10 + h / 2), t, font=f, fill=c, anchor="mm")
        if i < len(parts) - 1:
            ax = x + bw + 18; ay = 10 + h / 2
            d.polygon([(ax, ay - 26), (ax + gap - 46, ay - 26), (ax + gap - 46, ay - 48), (ax + gap - 10, ay), (ax + gap - 46, ay + 48), (ax + gap - 46, ay + 26), (ax, ay + 26)], fill=(230, 60, 60))
        x += bw + gap
    return im


# ---------- 自作の図 ----------
INK = (40, 34, 50)
REDC = (230, 30, 30)


def _canvas(w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); return im, ImageDraw.Draw(im)


def fig_eye(mark=True):
    """目の断面図。網膜を太い赤い帯で示し、赤い丸でかこむ"""
    im, d = _canvas(1100, 620)
    cx, cy, R = 560, 320, 250
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(255, 250, 245), outline=(120, 110, 130), width=10)        # 白目（強膜）
    if mark:
        d.arc([cx - R + 10, cy - R + 10, cx + R - 10, cy + R - 10], -75, 75, fill=(235, 70, 90), width=30)           # 網膜（奥の内側の層）
    d.chord([cx - R - 40, cy - 120, cx - R + 70, cy + 120], 90, 270, fill=(200, 230, 255), outline=(90, 140, 200), width=6)   # 角膜
    d.ellipse([cx - R + 40, cy - 95, cx - R + 120, cy + 95], fill=(255, 245, 200), outline=(200, 160, 60), width=6)         # 水晶体
    d.rectangle([cx + R - 10, cy - 30, cx + R + 150, cy + 30], fill=(250, 210, 120), outline=(190, 140, 50), width=5)      # 視神経
    f = FF(FPOP, 40)
    d.text((cx - R - 20, cy - 165), "角膜", font=f, fill=INK, anchor="mm")
    d.text((cx - R + 80, cy + 150), "水晶体", font=f, fill=INK, anchor="mm")
    d.text((cx + R + 150, cy + 80), "視神経", font=f, fill=INK, anchor="mm")
    d.polygon([(60, cy - 20), (170, cy - 20), (170, cy - 44), (230, cy), (170, cy + 44), (170, cy + 20), (60, cy + 20)], fill=(255, 210, 60))
    d.text((100, cy - 70), "光", font=FF(FPOP, 54), fill=(220, 150, 0), anchor="mm")
    if not mark:
        return im
    # 網膜を赤い丸でかこむ
    d.ellipse([cx + R - 190, cy - 270, cx + R + 40, cy + 270], outline=REDC, width=12)
    d.rounded_rectangle([cx + R - 160, 0, cx + R + 140, 70], 24, fill=REDC)
    d.text((cx + R - 10, 35), "ここが網膜", font=FF(FPOP, 44), fill=(255, 255, 255), anchor="mm")
    return im


def fig_retina():
    """網膜の中のつながり。視細胞と双極細胞のつなぎ目にピカチュリン"""
    im, d = _canvas(1200, 560)
    f = FF(FPOP, 40)
    d.polygon([(30, 250), (150, 250), (150, 222), (210, 280), (150, 338), (150, 310), (30, 310)], fill=(255, 210, 60))
    d.text((90, 200), "光", font=FF(FPOP, 54), fill=(220, 150, 0), anchor="mm")
    # 視細胞
    for i, x in enumerate((300, 380, 460)):
        d.rounded_rectangle([x, 150, x + 50, 400], 25, fill=(150, 200, 255), outline=(60, 110, 200), width=5)
    d.text((405, 450), "視細胞", font=f, fill=(60, 110, 200), anchor="mm")
    d.text((405, 495), "光を受けとる", font=FF(FPOP, 30), fill=INK, anchor="mm")
    # 双極細胞
    for x in (700, 800):
        d.ellipse([x, 230, x + 70, 330], fill=(190, 240, 200), outline=(40, 150, 90), width=5)
        d.line([(x, 280), (520, 280)], fill=(40, 150, 90), width=6)
        d.line([(x + 70, 280), (960, 280)], fill=(40, 150, 90), width=6)
    d.text((770, 450), "双極細胞", font=f, fill=(40, 150, 90), anchor="mm")
    d.rounded_rectangle([960, 220, 1170, 340], 30, fill=(255, 235, 240), outline=(200, 80, 120), width=6)
    d.text((1065, 280), "脳へ", font=f, fill=(200, 80, 120), anchor="mm")
    # つなぎ目を赤でかこむ
    d.ellipse([500, 170, 690, 390], outline=REDC, width=12)
    d.rounded_rectangle([370, 20, 830, 110], 26, fill=REDC)
    d.text((600, 65), "つなぎ目にピカチュリン", font=FF(FPOP, 34), fill=(255, 255, 255), anchor="mm")
    return im


def _nice_step(mx):
    raw = mx / 4; p = 10 ** np.floor(np.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * p: return m * p
    return 10 * p


def fig_bars(spec):
    """bars:コスモッグ=0.1,カビゴン=460,unit=kg → 0から始まる目盛りつきの横棒グラフ。max=100 で目盛りの最大をそろえる"""
    items = []; mx = None; unit = ""
    for p in spec.split(","):
        k, _, v = p.partition("=")
        k = k.strip()
        if k == "unit": unit = v.strip(); continue
        try:
            if k == "max": mx = float(v); continue
            items.append((k, float(v)))
        except ValueError: pass
    if not items: return None
    top = mx or max(v for _, v in items) or 1
    step = _nice_step(top); axmax = step * np.ceil(top / step - 1e-9)
    f = FF(FPOP, 42)
    while max(f.getlength(k) for k, _ in items) > 420 and f.size > 24: f = FF(FPOP, f.size - 2)
    lw = int(max(f.getlength(k) for k, _ in items)) + 30
    BW = 620; rowh = 110
    H2 = rowh * len(items) + 110
    im, d = _canvas(lw + BW + 260, H2)
    ft = FF(FPOP, 28)
    # 目盛り（0から始める）
    t = 0.0
    while t <= axmax + 1e-9:
        x = lw + BW * t / axmax
        d.line([(x, 10), (x, H2 - 70)], fill=(200, 200, 210), width=2)
        d.text((x, H2 - 40), f"{t:g}", font=ft, fill=(90, 90, 100), anchor="mm")
        t += step
    if unit: d.text((lw + BW + 50, H2 - 40), f"（{unit}）", font=ft, fill=(90, 90, 100), anchor="lm")
    d.line([(lw, 10), (lw, H2 - 70)], fill=INK, width=5)                       # 0の線
    cols = [(124, 78, 178), (40, 118, 200), (214, 84, 60), (24, 140, 112), (196, 64, 136)]
    for i, (k, v) in enumerate(items):
        y = 20 + i * rowh
        d.text((lw - 20, y + 40), k, font=f, fill=INK, anchor="rm")
        w = BW * v / axmax
        if w >= 2:
            d.rounded_rectangle([lw, y + 8, lw + w, y + 72], min(16, w / 2), fill=cols[i % len(cols)])
        d.text((lw + max(w, 0) + 12, y + 40), f"{v:g}{unit}", font=FF(FD, 44), fill=cols[i % len(cols)], anchor="lm")
    return im


def fig_slots(text):
    """slots:フシギバナ → 1文字ずつ箱に入れて文字数を見せる"""
    chars = list(text); n = len(chars)
    s = 150 if n <= 6 else max(70, int(1100 / n) - 10)
    im, d = _canvas(n * (s + 14) + 20, s + 110)
    f = FF(FD, int(s * 0.62))
    for i, c in enumerate(chars):
        x = 10 + i * (s + 14)
        d.rounded_rectangle([x, 10, x + s, 10 + s], 22, fill=(255, 255, 255), outline=(124, 78, 178), width=8)
        d.text((x + s / 2, 10 + s / 2), c, font=f, fill=INK, anchor="mm")
        d.text((x + s / 2, s + 60), str(i + 1), font=FF(FPOP, 40), fill=REDC, anchor="mm")
    return im


TYPE_COL = {"ノーマル": (168, 167, 122), "ほのお": (238, 129, 48), "みず": (99, 144, 240), "でんき": (247, 208, 44), "くさ": (122, 199, 76),
            "こおり": (150, 217, 214), "かくとう": (194, 46, 40), "どく": (163, 62, 161), "じめん": (226, 191, 101), "ひこう": (169, 143, 243),
            "エスパー": (249, 85, 135), "むし": (166, 185, 26), "いわ": (182, 161, 54), "ゴースト": (115, 87, 151), "ドラゴン": (111, 53, 252),
            "あく": (112, 87, 70), "はがね": (183, 183, 206), "フェアリー": (214, 133, 173)}


def fig_vs(spec):
    """vs:ゴースト>エスパー=×0 → タイプ相性の図"""
    left, _, rest = spec.partition(">"); right, _, res = rest.partition("=")
    im, d = _canvas(1150, 330)
    f = FF(FD, 64)
    for x, t in ((40, left), (720, right)):
        c = TYPE_COL.get(t.strip(), (120, 120, 140))
        d.rounded_rectangle([x, 60, x + 390, 210], 75, fill=c, outline=(255, 255, 255), width=8)
        d.text((x + 195, 135), t.strip(), font=f, fill=(255, 255, 255), anchor="mm", stroke_width=4, stroke_fill=(60, 50, 60))
    d.polygon([(460, 115), (620, 115), (620, 85), (690, 135), (620, 185), (620, 155), (460, 155)], fill=INK)
    if res:
        bad = bool(re.match(r"(×0(?![.．])|0(?![.．])|こうかなし|効果なし)", res.strip()))
        d.rounded_rectangle([380, 225, 770, 320], 30, fill=REDC if bad else ((230, 130, 30) if "いまひとつ" in res else (40, 150, 90)))
        d.text((575, 272), res.strip(), font=FF(FD, 52), fill=(255, 255, 255), anchor="mm")
        if bad:
            d.line([(470, 70), (690, 200)], fill=REDC, width=18); d.line([(470, 200), (690, 70)], fill=REDC, width=18)
    return im


def fig_spell(spec):
    """spell:alligator>Feraligatr → 2つのつづりを並べ、ちがう文字を赤で示す"""
    a, _, b = spec.partition(">")
    im, d = _canvas(1150, 330)
    f = FF(FD, 96)
    import difflib
    sm = difflib.SequenceMatcher(None, a.lower(), b.lower())
    def draw(word, y, other_is_a):
        x = 575 - f.getlength(word) / 2
        keep = set()
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal": keep.update(range(j1, j2) if not other_is_a else range(i1, i2))
        for i, ch in enumerate(word):
            col = INK if i in keep else REDC
            d.text((x, y), ch, font=f, fill=col, anchor="lm"); x += f.getlength(ch)
    draw(a, 90, True); draw(b, 240, False)
    return im


def fig_palette(spec):
    """palette:トキワ=#007B43,ニビ=#727171 → 色見本のチップと名前を並べる"""
    items = []
    for p in spec.split(","):
        k, _, v = p.partition("=")
        if k.strip(): items.append((k.strip(), v.strip()))
    n = len(items); cols = min(n, 5); rows = (n + cols - 1) // cols
    cw, chh = 220, 260
    im, d = _canvas(cols * cw + 20, rows * chh + 20)
    for i, (k, v) in enumerate(items):
        x = 10 + (i % cols) * cw; y = 10 + (i // cols) * chh
        if v == "rainbow":
            chip = rainbow(170)
        else:
            c = tuple(int(v.lstrip("#")[j:j + 2], 16) for j in (0, 2, 4))
            chip = Image.new("RGBA", (170, 170), c + (255,))
        m = Image.new("L", (170, 170), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, 169, 169], 34, fill=255)
        im.paste(chip, (x + 25, y), m)
        d.rounded_rectangle([x + 25, y, x + 195, y + 170], 34, outline=(60, 50, 80), width=6)
        f = FF(FPOP, 40)
        while f.getlength(k) > cw - 10 and f.size > 22: f = FF(FPOP, f.size - 2)
        d.text((x + 110, y + 215), k, font=f, fill=INK, anchor="mm")
    return im


def rainbow(sz):
    """玉虫色・にじ色の見本"""
    a = np.linspace(0, 1, sz)
    hsv = np.stack([np.tile(a[None, :], (sz, 1)) * 255, np.full((sz, sz), 180), np.full((sz, sz), 235)], -1).astype(np.uint8)
    return Image.fromarray(hsv, "HSV").convert("RGBA")


def fig_sign(spec):
    """sign:1行目|2行目 → ゲームの町にある木の看板の絵"""
    lines = [x for x in spec.split("/") if x]
    f = FF(FPOP, 64)
    w = int(max(f.getlength(t) for t in lines)) + 140; h = len(lines) * 90 + 90
    im, d = _canvas(w, h + 200)
    d.rectangle([w / 2 - 22, h - 10, w / 2 + 22, h + 190], fill=(150, 100, 60), outline=(90, 60, 30), width=5)
    d.rounded_rectangle([0, 0, w - 1, h], 26, fill=(214, 168, 108), outline=(110, 72, 36), width=10)
    d.rounded_rectangle([24, 24, w - 25, h - 24], 16, fill=(255, 252, 240), outline=(170, 130, 80), width=4)
    for i, t in enumerate(lines):
        d.text((w / 2, 45 + 45 + i * 90), t, font=f, fill=INK, anchor="mm")
    return im


KANTO = {  # 町の位置（だいたいの配置）と、名前のもとになった色
    "マサラ": ((1.6, 7.6), "#FFFFFF"), "トキワ": ((1.6, 5.0), "#007B43"), "ニビ": ((1.6, 2.0), "#727171"),
    "ハナダ": ((6.2, 1.4), "#2792C3"), "ヤマブキ": ((6.2, 4.2), "#F8B500"), "クチバ": ((6.2, 6.8), "#917347"),
    "シオン": ((9.0, 4.2), "#867BA9"), "タマムシ": ((4.0, 4.2), "rainbow"), "セキチク": ((4.8, 8.8), "#E5ABBE"),
    "グレン": ((1.6, 10.2), "#E83929")}
KANTO_ROADS = [("マサラ", "トキワ"), ("トキワ", "ニビ"), ("ニビ", "ハナダ"), ("ハナダ", "ヤマブキ"), ("ヤマブキ", "クチバ"),
               ("ハナダ", "シオン"), ("シオン", "ヤマブキ"), ("ヤマブキ", "タマムシ"), ("シオン", "クチバ"), ("クチバ", "セキチク"),
               ("タマムシ", "セキチク"), ("セキチク", "グレン"), ("グレン", "マサラ")]


def fig_kanto(spec):
    """kanto:all（全部の町に色）／kanto:トキワ,ニビ（その町だけ色をつけて赤丸）→ カントー地方の町の地図"""
    sel = list(KANTO) if spec.strip() in ("all", "") else [x.strip() for x in spec.split(",")]
    im, d = _canvas(1180, 760)
    d.rounded_rectangle([0, 0, 1179, 759], 40, fill=(214, 236, 250))                      # 海
    d.rounded_rectangle([40, 30, 1060, 590], 60, fill=(200, 232, 170), outline=(150, 190, 120), width=6)   # 陸
    P2 = lambda k: (90 + KANTO[k][0][0] * 100, 60 + KANTO[k][0][1] * 56)
    for a, b in KANTO_ROADS:
        d.line([P2(a), P2(b)], fill=(240, 225, 180), width=18)
    f = FF(FPOP, 36)
    for k, ((_, _), col) in KANTO.items():
        x, y = P2(k); on = k in sel
        r = 46 if on else 26
        if on and col == "rainbow":
            chip = rainbow(r * 2); m = Image.new("L", (r * 2, r * 2), 0); ImageDraw.Draw(m).ellipse([0, 0, r * 2 - 1, r * 2 - 1], fill=255)
            im.paste(chip, (int(x - r), int(y - r)), m)
            d.ellipse([x - r, y - r, x + r, y + r], outline=(60, 50, 80), width=5)
        else:
            c = col if on else "#B8B8C0"
            d.ellipse([x - r, y - r, x + r, y + r], fill=c, outline=(60, 50, 80), width=5)
        if on and len(sel) < len(KANTO):
            d.ellipse([x - r - 16, y - r - 16, x + r + 16, y + r + 16], outline=REDC, width=8)
        d.text((x, y + r + 30), k, font=FF(FPOP, 50) if on else FF(FPOP, 40), fill=INK if on else (110, 110, 120), anchor="mm",
               stroke_width=5, stroke_fill=(255, 255, 255))
    return im


def annotate(im, spec):
    """mark=x,y,w,h（画像に対する0〜1の位置）を赤い丸でかこむ。label=文字 で札を付ける。はみ出さないよう周りに余白を足す"""
    try:
        x, y, w, h = [float(v) for v in spec.get("mark", "").split(",")]
    except ValueError:
        return im
    W0, H0 = im.size
    lw = max(6, int(min(W0, H0) / 45))
    f = FF(FPOP, max(30, int(max(W0, H0) / 12)))
    pad = int(f.size + 50)
    out = Image.new("RGBA", (W0 + pad * 2, H0 + pad * 2), (0, 0, 0, 0)); out.alpha_composite(im, (pad, pad))
    d = ImageDraw.Draw(out)
    ex = 0.04
    box = [pad + (x - ex) * W0, pad + (y - ex) * H0, pad + (x + w + ex) * W0, pad + (y + h + ex) * H0]
    d.ellipse(box, outline=(255, 255, 255), width=lw + 8)
    d.ellipse(box, outline=REDC, width=lw)
    lab = spec.get("label")
    if lab:
        tw = f.getlength(lab) + 40; th = f.size + 20
        tx = min(max(0, (box[0] + box[2]) / 2 - tw / 2), out.width - tw)
        ty = box[1] - th - 6 if box[1] - th - 6 >= 0 else min(out.height - th, box[3] + 6)
        d.rounded_rectangle([tx, ty, tx + tw, ty + th], 16, fill=REDC)
        d.text((tx + tw / 2, ty + th / 2), lab, font=f, fill=(255, 255, 255), anchor="mm")
    return out


def web_img(url):
    """web:URL → ゲームやアニメの画像などをネットから取る（取れなければ None）"""
    import urllib.request
    try:
        fn = os.path.join(HERE, "_cache", "web_" + re.sub(r"[^A-Za-z0-9._-]", "_", url)[-120:])
        os.makedirs(os.path.dirname(fn), exist_ok=True)
        if not os.path.exists(fn):
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r: open(fn, "wb").write(r.read())
        im = Image.open(fn).convert("RGBA")
        if im.width < 500:                                   # 小さいゲーム画面はくっきり拡大
            k = max(1, 900 // im.width); im = im.resize((im.width * k, im.height * k), Image.NEAREST)
        return im
    except Exception as e:
        print("ネットの画像を取れない:", url, repr(e)); return None


def load_img(ref):
    """「A^B」と書くと、Aが取れないときはBを使う"""
    if "^" in ref.split("@")[0]:
        for alt in ref.split("^"):
            im = load_img(alt)
            if im is not None: return im
        return None
    return _load_img(ref)


def _load_img(ref):
    """'art:25' などから画像を読む。commons:ファイル名 / word:言葉 / color:#色 / flow:A>B>C も使える"""
    if ref in _IMG: return _IMG[ref]
    base, _, opt = ref.partition("@")
    spec = dict(o.split("=", 1) for o in opt.split("@") if "=" in o) if opt else {}
    kind, _, num = base.partition(":")
    im = None
    if kind == "fig": im = {"eye": fig_eye, "eye0": lambda: fig_eye(False), "retina": fig_retina}.get(num, lambda: None)()
    elif kind == "bars": im = fig_bars(num)
    elif kind == "slots": im = fig_slots(num)
    elif kind == "vs": im = fig_vs(num)
    elif kind == "spell": im = fig_spell(num)
    elif kind == "palette": im = fig_palette(num)
    elif kind == "sign": im = fig_sign(num)
    elif kind == "kanto": im = fig_kanto(num)
    elif kind == "commons": im = commons_img(num)
    elif kind == "web": im = web_img(num)
    elif kind == "word": im = word_card(num)
    elif kind == "color": im = color_card(num) if num != "rainbow" else rainbow(420)
    elif kind == "flow": im = flow_card(num)
    else:
        p = os.path.join(HERE, "assets", "img", f"{kind}_{num}.png")
        if os.path.exists(p):
            im = Image.open(p).convert("RGBA")
            bb = im.getbbox()
            if bb: im = im.crop(bb)
        else:
            print("画像なし:", ref)
    if im is not None and spec.get("crop"):
        cx_, cy_, cw_, ch_ = [float(v) for v in spec["crop"].split(",")]
        im = im.crop((int(cx_ * im.width), int(cy_ * im.height), int((cx_ + cw_) * im.width), int((cy_ + ch_) * im.height)))
    if im is not None and spec.get("mark"): im = annotate(im, spec)
    _IMG[ref] = im
    return im


def fit(im, w, h, pixel):
    s = min(w / im.width, h / im.height)
    if pixel and s > 1: s = max(1, int(s))           # ドット絵は整数倍でくっきり
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.NEAREST if pixel else Image.LANCZOS)


def scaled(s, z, pix):
    if abs(z - 1) < 0.004: return s
    return s.resize((max(1, int(s.width * z)), max(1, int(s.height * z))), Image.NEAREST if pix else Image.BILINEAR)


_SPOT = {}


def spot_bg(w, h, theme):
    """1枚だけ見せるときの、色つきの集中線ボード"""
    k = (w, h, theme)
    if k not in _SPOT:
        c1 = tuple(int(255 * 0.82 + c * 0.18) for c in theme[0]); c2 = tuple(int(255 * 0.9 + c * 0.1) for c in theme[0])
        b = Image.new("RGB", (w, h), c1); d = ImageDraw.Draw(b)
        cx, cy, R = w / 2, h / 2, w
        for i in range(24):
            a0 = 2 * np.pi * i / 24; a1 = a0 + np.pi / 24
            d.polygon([(cx, cy), (cx + R * np.cos(a0), cy + R * np.sin(a0)), (cx + R * np.cos(a1), cy + R * np.sin(a1))], fill=c2)
        g = Image.new("L", (w, h), 0); ImageDraw.Draw(g).ellipse([cx - 330, cy - 230, cx + 330, cy + 230], fill=255)
        b = Image.composite(Image.new("RGB", (w, h), (255, 255, 250)), b, g.filter(ImageFilter.GaussianBlur(90)))
        m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 36, fill=255)
        out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); out.paste(b, (0, 0), m)
        _SPOT[k] = out
    return _SPOT[k]


def cap_tag(d, cx, y, w, cap, theme):
    f = FF(FPOP, 34)
    while f.getlength(cap) + 60 > w and f.size > 22: f = FF(FPOP, f.size - 2)      # 札からはみ出さないよう文字を小さく
    tw = min(w, f.getlength(cap) + 60)
    d.rounded_rectangle([cx - tw / 2, y - 28, cx + tw / 2, y + 28], 26, fill=theme[0])
    d.text((cx, y), cap, font=f, fill=(255, 255, 255), anchor="mm")


def panel(im, refs, tin, theme):
    """画面中央に画像を出す。1枚なら集中線ボードで大きく、複数なら白いボードに並べる。出るときはポンと弾む"""
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = 400, 128, W - 400, 735
    if refs == ["unown"]:
        d.rounded_rectangle([x0, y0, x1, y1], 36, fill=(255, 255, 255), outline=theme[0], width=8)
        keys = [f"frlg:201-{c}" for c in "abcdefghijklmnopqrstuvwxyz"] + ["frlg:201-exclamation", "frlg:201-question"]
        cols, rows = 7, 4
        cw, ch = (x1 - x0 - 60) / cols, (y1 - y0 - 50) / rows
        for i, k in enumerate(keys):
            s = load_img(k)
            if s is None: continue
            s = fit(s, cw - 14, ch - 14, True)
            z = ease_back((tin - i * 0.03) / 0.25)
            if z <= 0.02: continue
            s = scaled(s, z, True)
            cx = x0 + 30 + cw * (i % cols) + cw / 2; cy = y0 + 25 + ch * (i // cols) + ch / 2 + np.sin(tin * 3 + i) * 4
            im.paste(s, (int(cx - s.width / 2), int(cy - s.height / 2)), s)
        return
    items = []
    for r in refs:
        ref, _, cap = r.partition("|")
        s = load_img(ref)
        if s is not None: items.append((ref, s, cap))
    if not items: return
    n = len(items)
    if n == 1 and items[0][0].split(":")[0] not in PIXEL_KINDS:
        ref, s, cap = items[0]
        im.paste(spot_bg(x1 - x0, y1 - y0, theme), (x0, y0), spot_bg(x1 - x0, y1 - y0, theme))
        ih = (y1 - y0 - 50) - (70 if cap else 0)
        s = fit(s, x1 - x0 - 120, ih, False)
        z = ease_back(tin / 0.32)        # ポンと出たら、あとは動かさない
        s = scaled(s, z, False)
        cx = (x0 + x1) / 2; cy = y0 + 25 + ih / 2
        with_shadow(im, s, (int(cx - s.width / 2), int(cy - s.height / 2)), blur=12, alpha=0.3, off=(8, 10), outline=6)
        if cap: cap_tag(ImageDraw.Draw(im), cx, y1 - 46, x1 - x0 - 80, cap, theme)
        return
    d.rounded_rectangle([x0, y0, x1, y1], 36, fill=(255, 255, 255), outline=theme[0], width=8)
    gap = 30
    # 横に並べるか、縦に積むか。画像が大きく見える方を選ぶ（横長の図は縦に積む）
    AW, AH = x1 - x0 - 60, y1 - y0 - 60
    capw = 60 if any(c for _, _, c in items) else 0
    def row_layout():
        ih = AH - capw; asp = [s.width / s.height for _, s, _ in items]
        tot = sum(asp) * ih + gap * (n - 1)
        k = min(1.0, (AW - gap * (n - 1)) / (sum(asp) * ih)) if tot > AW else 1.0
        hh = ih * k; out = []; x = x0 + 30 + (AW - (sum(asp) * hh + gap * (n - 1))) / 2
        for a in asp:
            w_ = a * hh; out.append((x + w_ / 2, y0 + 30 + ih / 2, w_, hh, y1 - 50, max(w_ + 40, (AW - gap * (n - 1)) / n))); x += w_ + gap
        return out
    def col_layout():
        rh = (AH - gap * (n - 1)) / n; out = []
        for i, (_, s, cap) in enumerate(items):
            top = y0 + 30 + i * (rh + gap)
            if cap:
                out.append((x0 + 30 + (AW - 300) / 2, top + rh / 2, AW - 340, rh, top + rh / 2, 300))
            else:
                out.append((x0 + 30 + AW / 2, top + rh / 2, AW, rh, None, 0))
        return out
    def area(L):
        a = 0
        for (cx, cy, bw, bh, _, _), (_, s, _) in zip(L, items):
            k = min(bw / s.width, bh / s.height); a += min(k * s.width * k * s.height, bw * bh)
        return a
    L = row_layout()
    if 2 <= n <= 3:
        L2 = col_layout()
        if area(L2) > area(L) * 1.15: L = L2
    for i, ((cx, cy, bw, bh, capy, capw_), (ref, s, cap)) in enumerate(zip(L, items)):
        pix = ref.split(":")[0] in PIXEL_KINDS
        s = fit(s, bw, bh, pix)
        z = ease_back((tin - i * 0.14) / 0.3)                     # 1枚ずつ順番に出る
        if z <= 0.02: continue
        s = scaled(s, z, pix)          # 出たあとは動かさない
        im.paste(s, (int(cx - s.width / 2), int(cy - s.height / 2)), s)
        if cap and tin > i * 0.14 + 0.15:
            if capw_ == 300: cap_tag(d, x1 - 30 - 150, capy, 290, cap, theme)
            else:
                cw_ = min(capw_, 2 * min(cx - x0 - 10, x1 - 10 - cx))     # 枠の外へ出さない
                cap_tag(d, cx, capy, cw_, cap, theme)


def header(d, sub, theme):
    d.rectangle([0, 0, W, 96], fill=theme[0]); d.rectangle([0, 96, W, 106], fill=theme[1])
    d.text((40, 48), "ずんだもんと冥鳴ひまりの ポケモン雑学", font=FF(FPOP, 40), fill=(255, 255, 255), anchor="lm")
    if sub: d.text((W - 40, 48), sub, font=FF(FROCK, 40), fill=theme[2], anchor="rm")


# ---------- 字幕の改行 ----------
NG_START = set("、。，．・！？!?」』）)]ーっゃゅょぁぃぅぇぉッャュョァィゥェォ…〜～")
NG_END = set("「『（([")
GOOD_END = set("、。！？!?」』…　")


def cclass(c):
    o = ord(c)
    if c.isascii() and c.isalnum() or "０" <= c <= "９": return "a"
    if 0x30A0 <= o <= 0x30FF: return "k"
    if 0x3040 <= o <= 0x309F: return "h"
    if 0x4E00 <= o <= 0x9FFF or c in "々〆": return "c"
    return "p"


_WRAP = {}


def wrap_jp(text, fname, size, maxw):
    """読みやすい位置で改行する。句読点や助詞のあとで切り、行の長さをそろえ、記号だけの行や行頭の句読点を作らない"""
    k = (text, fname, size, maxw)
    if k in _WRAP: return _WRAP[k]
    f = FF(fname, size); n = len(text)
    pre = [0.0] + [f.getlength(text[:i]) for i in range(1, n + 1)]
    total = pre[n]
    if total <= maxw:
        _WRAP[k] = [text]; return [text]

    def bcost(j):
        a, b = text[j - 1], text[j]
        if b in NG_START or a in NG_END: return None
        if (a in ".．" and b.isdigit()) or (b in ".．%％" and a.isdigit()): return None   # 2.9 や 5% を分けない
        if a in "」』" and cclass(b) == "h": return 30                                # 「まっさら」から を分けない
        if a in "。！？!?」』": return -3
        if a in "、…　": return 0
        ca, cb = cclass(a), cclass(b)
        if cb == "h" and b in "をにがはでともへやのねよかなだ" and ca != "h": return 30    # 行頭に助詞を置かない
        if a in "はがをにでともへやねよか" and cb != "h": return 1
        if ca == cb and ca in "akc": return 30                                        # 単語の途中
        if ca == cb == "h": return 40                                                 # ひらがなの途中（「あとな|のだ」など）
        if text[j:j + 2] in ("さん", "くん", "ちゃん") or b in "用的性製版": return 30
        return 4

    best = None; INF = 1e18
    lmin = int(np.ceil(total / maxw))
    for L in range(lmin, lmin + 2):
        target = total / L
        dp = [[INF] * (L + 1) for _ in range(n + 1)]; bk = [[0] * (L + 1) for _ in range(n + 1)]
        dp[0][0] = 0
        for j in range(1, n + 1):
            bc = 0 if j == n else bcost(j)
            if bc is None: continue
            for l in range(1, L + 1):
                for i in range(j - 1, -1, -1):
                    w = pre[j] - pre[i]
                    if w > maxw: break
                    if dp[i][l - 1] >= INF or j - i < 4: continue
                    c = dp[i][l - 1] + bc + ((w - target) / target) ** 2 * 30
                    if c < dp[j][l]: dp[j][l] = c; bk[j][l] = i
        if dp[n][L] < INF:
            c = dp[n][L] + (L - lmin) * 12
            if best is None or c < best[0]:
                out = []; j = n
                for l in range(L, 0, -1): i = bk[j][l]; out.append(text[i:j]); j = i
                best = (c, [s.strip("　 ") for s in out[::-1]])
    res = best[1] if best else P.jwrap(ImageDraw.Draw(Image.new("L", (1, 1))), text, f, maxw)
    _WRAP[k] = res
    return res


UNIT_RE = re.compile(r"(?:キロメートル|キロ|メートル|センチ|ミリ|トン|グラム|パーセント|か所|カ所|文字|世代|市町村|時間|年代|年|月|日|回|匹|人|番|種類|種|倍|分|秒|歳|円|位|枚|機|本|話|色|kg|km|cm|m|g|t|%|％)")


def colors_for(text, accent):
    """「」『』の中はアクセント色、数字（と単位）は赤"""
    cols = [None] * len(text); depth = 0
    for i, c in enumerate(text):
        if c in "「『": depth += 1
        if depth: cols[i] = accent
        if c in "」』": depth = max(0, depth - 1)
    i = 0
    while i < len(text):
        if text[i].isdigit():
            j = i
            while j < len(text) and (text[j].isdigit() or text[j] in ",.，．万億千百十"): j += 1
            m = UNIT_RE.match(text, j)
            if m: j = m.end()
            for x in range(i, j): cols[x] = RED
            i = j
        else: i += 1
    return cols


def draw_rich(d, lines, full, f, cy0, lh, accent):
    cols = colors_for(full, accent); pos = 0
    for li, ln in enumerate(lines):
        k = full.find(ln, pos); k = pos if k < 0 else k; pos = k + len(ln)
        x = W / 2 - f.getlength(ln) / 2; y = cy0 + lh * li
        run, rc = "", None
        for ci, ch in enumerate(ln):
            c = cols[k + ci] or (40, 34, 50)
            if c != rc and run:
                d.text((x, y), run, font=f, fill=rc, anchor="lm"); x += f.getlength(run); run = ""
            run += ch; rc = c
        if run: d.text((x, y), run, font=f, fill=rc, anchor="lm")


def is_shock(who, text):
    return who == "z" and ("！？" in text or text.startswith(("えっ", "ええっ", "えーっ")))


# ---------- 終わりの画面（YouTube の終了画面で、動画2本とチャンネル登録のボタンを重ねる場所） ----------
END_DUR = 20.0
END_BOX_L = (130, 300, 770, 660)     # 左の動画枠（16:9）
END_BOX_R = (1150, 300, 1790, 660)   # 右の動画枠
END_SUB = (960, 470, 120)            # チャンネル登録の丸（中心x, 中心y, 半径）


def end_card(t):
    theme = THEMES[0]
    im = bg(theme).copy().convert("RGBA"); d = ImageDraw.Draw(im)
    header(d, None, theme)
    z = max(0.05, ease_back(t / 0.4))
    lay = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
    outlined(lay, (W // 2, 100), "最後まで見てくれてありがとう！", 84, (40, 34, 50), inner=(255, 255, 255), outer=theme[0], w1=10, w2=20, font=FD)
    lay = scaled(lay, z, False); im.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(195 - lay.height / 2)))
    f = FF(FPOP, 40)
    for (x0, y0, x1, y1), cap in ((END_BOX_L, "前回の動画"), (END_BOX_R, "おすすめの動画")):
        d.rounded_rectangle([x0 - 10, y0 - 10, x1 + 10, y1 + 10], 26, fill=(255, 255, 255), outline=theme[0], width=8)
        d.rounded_rectangle([x0, y0, x1, y1], 18, fill=(236, 232, 244))
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        d.polygon([(cx - 40, cy - 50), (cx - 40, cy + 50), (cx + 52, cy)], fill=(200, 192, 216))
        d.rounded_rectangle([cx - 150, y1 + 26, cx + 150, y1 + 86], 30, fill=theme[0])
        d.text((cx, y1 + 56), cap, font=f, fill=(255, 255, 255), anchor="mm")
    sx, sy, r = END_SUB
    d.ellipse([sx - r - 12, sy - r - 12, sx + r + 12, sy + r + 12], fill=(255, 255, 255), outline=(230, 40, 40), width=10)
    d.rounded_rectangle([sx - 150, sy + r + 30, sx + 150, sy + r + 90], 30, fill=(230, 40, 40))
    d.text((sx, sy + r + 60), "チャンネル登録", font=f, fill=(255, 255, 255), anchor="mm")
    for name, x in (("zundamon", 470), ("himari", 1450)):
        img = tachie(name, 360, False)
        bob = int(abs(np.sin(t * 3 + (0 if name == "zundamon" else 1.5))) * 10)
        im.paste(img, (int(x - img.width / 2), H - img.height + 40 - bob), img)
    return im.convert("RGB")


def frame(sub, refs, who, text, t, big_title=None, theme=THEMES[0], tin=9.0, big=None):
    im = bg(theme).copy().convert("RGBA"); d = ImageDraw.Draw(im)
    header(d, sub, theme)
    if refs: panel(im, refs, tin, theme)
    elif big_title:
        z = max(0.05, ease_back(tin / 0.4))
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        outlined(lay, (W // 2, 330), big_title[0], 96, (40, 34, 50), inner=(255, 255, 255), outer=theme[0], w1=10, w2=20, font=FD)
        outlined(lay, (W // 2, 500), big_title[1], 150, theme[2], inner=(40, 30, 60), outer=(255, 255, 255), w1=14, w2=30, font=FD)
        if z < 0.999:
            lay = lay.resize((int(W * z), int(H * z)), Image.BILINEAR); im.alpha_composite(lay, (int((W - lay.width) / 2), int((H - lay.height) / 2 - 80 * (1 - z))))
        else: im.alpha_composite(lay)
    if big:                                    # 大きなテロップ
        z = ease_back(t / 0.3)
        if z > 0.02:
            f = FF(FD, 84)
            while f.getlength(big) > W - 900 and f.size > 50: f = FF(FD, f.size - 6)
            lay = Image.new("RGBA", (int(f.getlength(big)) + 120, 170), (0, 0, 0, 0))
            outlined(lay, (lay.width // 2, 85), big, f.size, (255, 255, 255), inner=theme[0], outer=(255, 255, 255), w1=10, w2=22, font=FD)
            lay = scaled(lay, z, False)
            im.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(190 - lay.height / 2)))
    shock = is_shock(who, text)
    for c in ([("h" if who == "z" else "z")] + [who]):
        act = c == who
        name = "zundamon" if c == "z" else ("himari" if act else "himari_jito")
        img = tachie(name, 820 if act else 780, not act)
        bob = int(abs(np.sin(t * 8)) * 12) if act else 0
        if act and shock and t < 0.35: bob = int(60 * np.sin(t / 0.35 * np.pi))     # びっくりして跳ねる
        x = -40 if c == "z" else W - img.width + 40
        im.paste(img, (x, H - img.height + 60 - bob), img)
    d = ImageDraw.Draw(im)
    if shock and t < 1.6:                     # 頭の上に「！？」
        z = ease_back(t / 0.25)
        lay = Image.new("RGBA", (260, 200), (0, 0, 0, 0))
        outlined(lay, (130, 100), "！？", 120, RED, inner=(255, 255, 255), outer=(40, 30, 60), w1=8, w2=16, font=FD)
        lay = scaled(lay, z, False); im.alpha_composite(lay, (int(250 - lay.width / 2), int(330 - lay.height / 2)))
    c = CHAR[who]
    for size in (54, 48, 42):                       # 長いせりふは文字を小さくして、全部表示する
        f = FF(FR, size); lines = wrap_jp(text, FR, size, 1150)
        if len(lines) <= 3: break
    lh = int(size * 1.42)
    h = 50 + lh * len(lines); top = H - 30 - h
    slide = int((1 - ease_out(t / 0.15)) * 24)
    top += slide
    d.rounded_rectangle([340, top, W - 340, top + h], 30, fill=(255, 255, 255), outline=c["col"], width=9)
    tag = FF(FPOP, 34)
    d.rounded_rectangle([370, top - 30, 370 + 50 + tag.getlength(c["name"]), top + 24], 24, fill=c["col"])
    d.text((395, top - 3), c["name"], font=tag, fill=(255, 255, 255), anchor="lm")
    draw_rich(d, lines, text, f, top + 25 + lh / 2, lh, c["col"] if who == "h" else (40, 140, 30))
    im = im.convert("RGB")
    if shock and t < 0.4:                     # 画面がゆれる
        a = 14 * (1 - t / 0.4); dx, dy = int(a * np.sin(t * 90)), int(a * np.cos(t * 70))
        im = ImageChops_offset(im, dx, dy)
    return im


def ImageChops_offset(im, dx, dy):
    from PIL import ImageChops
    return ImageChops.offset(im, dx, dy)


# ---------- アイキャッチ ----------
def eyecatch(no, label, ref, theme, dur):
    s0 = load_img(ref) if ref else None
    pix = bool(ref) and ref.split(":")[0] in PIXEL_KINDS
    if s0 is not None: s0 = fit(s0, 500, 500, pix)
    zface = face("zundamon", 420)
    lab_f = FF(FD, 92)
    while lab_f.getlength(label) > W - 640 and lab_f.size > 48: lab_f = FF(FD, lab_f.size - 4)   # 右下のずんだもんと重ならない幅

    def fn(t):
        im = Image.new("RGBA", (W, H), theme[0]); d = ImageDraw.Draw(im)
        # 斜めの帯が流れこむ
        p = ease_out(t / 0.35); q = ease_out((t - (dur - 0.35)) / 0.35)
        off = -W * (1 - p) + W * 1.3 * q
        for k, (col, wdt) in enumerate([(theme[1], 520), (theme[2], 90), ((255, 255, 255), 30)]):
            x = off + 250 + k * 520
            d.polygon([(x, 0), (x + wdt, 0), (x + wdt - 300, H), (x - 300, H)], fill=col)
        for i in range(0, W + H, 90):                                   # うすい斜線
            d.line([(i - H + (t * 120) % 90, H), (i + (t * 120) % 90, 0)], fill=tuple(min(255, c + 18) for c in theme[0]), width=6)
        if s0 is not None:
            z = ease_back((t - 0.25) / 0.4)
            if z > 0.02:
                s = scaled(s0, z, pix); y = 450 + int(10 * np.sin(t * 4))
                with_shadow(im, s, (int(W / 2 - s.width / 2), int(y - s.height / 2)), blur=14, alpha=0.4, outline=8)
        z = ease_back((t - 0.1) / 0.35) if t < dur - 0.3 else 1
        if z > 0.02:
            lay = Image.new("RGBA", (700, 220), (0, 0, 0, 0))
            outlined(lay, (350, 110), f"その{no}", 128, theme[2], inner=(40, 30, 60), outer=(255, 255, 255), w1=12, w2=26, font=FD)
            lay = scaled(lay, 0.6 + 0.4 * z if z < 1 else z, False)
            im.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(130 - lay.height / 2)))
        a = ease_out((t - 0.5) / 0.3)
        if a > 0:
            lay = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
            outlined(lay, ((W - 380) // 2, 100), label, lab_f.size, (255, 255, 255), inner=(40, 30, 60), outer=theme[0], w1=12, w2=24, font=FD)
            im.alpha_composite(lay, (int(-60 * (1 - a)), 820))
        fx = int(W - 330 + 360 * (1 - ease_back((t - 0.6) / 0.4)))       # ずんだもんがのぞきこむ
        im.alpha_composite(zface, (fx, H - zface.height + 40))
        return im.convert("RGB")
    return fn


# ---------- 効果音・BGM ----------
def se(kind):
    sr = SR
    if kind == "pop":
        tt = np.arange(int(0.09 * sr)) / sr; f = 700 + 900 * tt / 0.09
        return (np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt * 40) * 0.22).astype(np.float32)
    if kind == "whoosh":
        n = int(0.45 * sr); rng = np.random.default_rng(1); x = rng.standard_normal(n).astype(np.float32)
        k = 60; x = np.convolve(x, np.ones(k) / k, mode="same"); env = np.sin(np.linspace(0, np.pi, n)) ** 2
        return (x * env * 0.9).astype(np.float32)
    if kind == "jan":
        tt = np.arange(int(0.7 * sr)) / sr; s = sum(np.sin(2 * np.pi * f * tt) for f in (523, 659, 784, 1047))
        return (s * np.exp(-tt * 5) * 0.07).astype(np.float32)
    if kind == "don":
        tt = np.arange(int(0.3 * sr)) / sr; f = 140 * np.exp(-tt * 8) + 50
        return (np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt * 10) * 0.45).astype(np.float32)
    return np.zeros(1, np.float32)


PATTERNS = [([523, 659, 784, 659, 587, 698, 880, 698], 0.30), ([392, 494, 587, 494, 440, 523, 659, 523], 0.26),
            ([659, 784, 988, 784, 698, 880, 1047, 880], 0.34), ([440, 523, 659, 784, 698, 587, 523, 494], 0.24),
            ([587, 740, 880, 740, 659, 784, 988, 784], 0.28), ([523, 587, 659, 784, 880, 784, 659, 587], 0.32)]


def bgm_sections(total, sections):
    """話題ごとに旋律とテンポを変えたBGM（同じ曲がずっと続かないように）"""
    n = int(total * SR); out = np.zeros(n, dtype=np.float32)
    bounds = [s for s, _ in sections] + [total]
    for si, (start, pi) in enumerate(sections):
        notes, step = PATTERNS[pi % len(PATTERNS)]; end = bounds[si + 1]; x = start; k = 0
        while x < end - 0.2:
            tt = np.arange(int(min(0.28, step) * SR)) / SR
            s = np.sin(2 * np.pi * notes[k % len(notes)] * tt) * np.exp(-tt * 9) * 0.05
            if k % 4 == 0:                                                  # 低音
                s = s + np.sin(2 * np.pi * notes[0] / 4 * tt) * np.exp(-tt * 6) * 0.05
            a = int(x * SR); b = min(n, a + len(s)); out[a:b] += s[:b - a].astype(np.float32); x += step; k += 1
    return out


# ---------- テンポ ----------
def pacing(ln, nxt):
    """せりふの速さと、次のせりふまでの間を変える"""
    t = ln.get("say") or ln["t"]; who = ln["w"]
    speed, inton, gap = 1.0, 1.0, 0.32
    if who == "z":
        if "！" in t or "？" in t: speed, inton = 1.06, 1.25
        if len(t) <= 18: gap = 0.16
    else:
        if len(t) >= 50: gap = 0.42
        pass                                     # ひまりは抑揚を一定にして、落ち着いた声にそろえる
    if nxt is not None and nxt["w"] == who: gap = max(gap, 0.25)
    if t.endswith(("？", "?")): gap = min(gap, 0.22)
    return speed, inton, gap


# ---------- 台本 ----------

def script_for(week, d):
    p = os.path.join(HERE, "scripts", "long", f"{week:04d}.json")
    if os.path.exists(p):
        print("台本:", p)
        return json.load(open(p, encoding="utf-8"))
    print("台本が無いので、ネタ帳から自動で作る")
    rnd = random.Random(20261114)
    back = sorted(k for k in d["back"] if k in d["names"]); rnd.shuffle(back); back = back[::-1]
    topics = []
    for i in range(N_TOPICS):
        k = back[(week * N_TOPICS + i) % len(back)]
        random.seed(week * 100 + i)
        q = Z.topic_backstory(k, d)
        lines = [{"w": l[0], "t": l[1], **({"say": l[2]} if len(l) > 2 else {})} for l in q["lines"][:-3]]
        lines[0]["img"] = [f"art:{int(d['stats'][k]['id'])}"]
        topics.append(dict(key=k, jn=d["names"][k], label=f"{d['names'][k]}の裏話", lines=lines, sources=[q.get("src", "")]))
    return dict(title=f"【ポケモン雑学】知ってた？ポケモンの意外な裏話{N_TOPICS}選【ずんだもん・冥鳴ひまり】",
                opening=[{"w": "z", "t": f"今日は、ポケモンの意外な裏話を{N_TOPICS}つ紹介するのだ！"},
                         {"w": "h", "t": "開発の人たちしか知らないような話もあるよ。最後まで見ていってね。"}],
                topics=topics,
                ending=[{"w": "h", "t": "今日の裏話はここまで。英語版の図鑑と和訳は、概要欄のサイトで読めるよ。"},
                        {"w": "z", "t": "チャンネル登録もよろしくなのだ！　またね！"}])


def build(sc, out):
    os.makedirs("_w", exist_ok=True)
    segs, voices, sfx, sections = [], [], [], [(0.0, 0)]
    state = dict(t=0.0, voiced=False)

    def add_line(sub, refs, ln, nxt, big_title=None, theme=THEMES[0], tin0=None):
        c = CHAR[ln["w"]]
        say = say_fix(ln.get("say") or P.voice_text(say_fix(ln["t"])) or ln["t"])
        sp, inton, gap = pacing(ln, nxt)
        v = P.tts(say, c["sp"], c["speed"] * sp, 0.0, inton)
        if v is not None: state["voiced"] = True
        dur = (len(v) / SR + gap) if v is not None else max(1.6, len(say) * 0.16 + gap)
        base = state["tin"] if tin0 is None else tin0
        segs.append((lambda t, sub=sub, refs=refs, ln=ln, base=base: frame(sub, refs, ln["w"], ln["t"], t, big_title, theme, base + t, ln.get("big")), dur, 2))
        if ln.get("img"): sfx.append((state["t"], "pop"))
        if ln.get("big"): sfx.append((state["t"], "jan"))
        if is_shock(ln["w"], ln["t"]): sfx.append((state["t"], "don"))
        voices.append((state["t"] + 0.08, v)); state["t"] += dur; state["tin"] = base + dur

    chapters = [(0.0, "オープニング")]
    bt = ("ポケモンの", "意外な裏話")
    state["tin"] = 0.0
    sfx.append((0.0, "jan"))
    ops = sc["opening"]
    for i, ln in enumerate(ops):
        add_line(None, ln.get("img"), ln, ops[i + 1] if i + 1 < len(ops) else None, bt, THEMES[0], 0.0 if ln.get("img") else None)
    for no, tp in enumerate(sc["topics"], 1):
        theme = THEMES[no % len(THEMES)]
        chapters.append((state["t"], f"その{no} {tp['label']}"))
        sections.append((state["t"], no))
        first_img = next((r.split("|")[0] for ln in tp["lines"] for r in ln.get("img", []) if r != "unown"), None)
        ed = 2.6
        segs.append((eyecatch(no, tp["label"], first_img, theme, ed), ed, 1))
        sfx.append((state["t"], "whoosh")); sfx.append((state["t"] + 0.3, "jan"))
        state["t"] += ed
        refs = None; lines = tp["lines"]
        for i, ln in enumerate(lines):
            same = bool(ln.get("img")) and refs is not None and [r.split("|")[0] for r in ln["img"]] == [r.split("|")[0] for r in refs]
            if ln.get("img") and not same: refs = ln["img"]; tin0 = 0.0
            else:
                if same: refs = ln["img"]           # 同じ画像なら出し直さず、札だけ変える
                tin0 = None
            ln2 = {k: v for k, v in ln.items() if not (same and k == "img")}
            add_line(f"その{no}　{tp['jn']}", refs, ln2, lines[i + 1] if i + 1 < len(lines) else None, None, theme, tin0)
    chapters.append((state["t"], "エンディング"))
    sections.append((state["t"], 0))
    eds = sc["ending"]
    for i, ln in enumerate(eds):
        add_line(None, ln.get("img"), ln, eds[i + 1] if i + 1 < len(eds) else None, bt, THEMES[0], 0.0 if i == 0 else None)
    segs.append((end_card, END_DUR, 2)); sfx.append((state["t"], "jan")); state["t"] += END_DUR      # 終わりの画面
    total = sum(round(dd * FPS) / FPS for _, dd, _ in segs)
    parts = []
    for k, (fn, dur, step) in enumerate(segs):
        nfr = max(1, int(round(dur * FPS)))
        for i in range(0, nfr, step): fn(i / FPS).save(f"_w/s{k}_{i // step:04d}.jpg", quality=90)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS / step), "-i", f"_w/s{k}_%04d.jpg", "-t", f"{nfr / FPS:.3f}",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-r", str(FPS), f"_w/s{k}.mp4"], check=True)
        for i in range(0, nfr, step): os.remove(f"_w/s{k}_{i // step:04d}.jpg")
        parts.append(f"_w/s{k}.mp4")
    open("_wlist.txt", "w").write("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "_wlist.txt", "-c", "copy", "_wv.mp4"], check=True)
    mix = bgm_sections(total, sections) * 0.6
    for t0, kind in sfx:
        s = se(kind); a = int(t0 * SR); b = min(len(mix), a + len(s))
        if b > a: mix[a:b] += s[:b - a]
    for t0, v in voices:
        if v is None: continue
        a = int(t0 * SR); b = min(len(mix), a + len(v)); mix[a:b] = mix[a:b] * 0.5 + v[:b - a]
    mix = np.clip(mix, -1, 1)
    with wave.open("_wa.wav", "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 30000).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "_wv.mp4", "-i", "_wa.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", out], check=True)
    thumb(sc).save(out[:-4] + "_サムネイル.jpg", quality=92)
    return state["voiced"], total, chapters


def outlined(base, xy, text, size, fill, anchor="mm", inner=(20, 14, 30), outer=(255, 255, 255), w1=14, w2=30, grad=None, font=None):
    """太い二重縁取りの文字（外側が白、内側が黒）。grad=(上の色, 下の色) でグラデーション"""
    f = FF(font, size) if font else F(FONT_K, size)
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text(xy, text, font=f, fill=outer, anchor=anchor, stroke_width=w2, stroke_fill=outer)
    d.text(xy, text, font=f, fill=inner, anchor=anchor, stroke_width=w1, stroke_fill=inner)
    sh = lay.split()[3].filter(ImageFilter.GaussianBlur(10))
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0)); shadow.putalpha(sh.point(lambda v: int(v * 0.5)))
    base.alpha_composite(shadow, (8, 10)); base.alpha_composite(lay)
    m = Image.new("L", base.size, 0); ImageDraw.Draw(m).text(xy, text, font=f, fill=255, anchor=anchor)
    if grad:
        bb = m.getbbox() or (0, 0, 1, 1)
        g = Image.new("RGBA", base.size, grad[0] + (255,)); gd = ImageDraw.Draw(g)
        for y in range(bb[1], bb[3] + 1):
            r = (y - bb[1]) / max(1, bb[3] - bb[1])
            gd.line([(0, y), (base.width, y)], fill=tuple(int(grad[0][i] * (1 - r) + grad[1][i] * r) for i in range(3)) + (255,))
        base.paste(g, (0, 0), m)
    else:
        base.paste(Image.new("RGBA", base.size, fill + (255,)), (0, 0), m)


def burst(size, c1, c2, n=28, center=None):
    """集中線（放射状の背景）"""
    w, h = size; cx, cy = center or (w / 2, h / 2)
    im = Image.new("RGB", size, c1); d = ImageDraw.Draw(im)
    R = (w + h) * 1.2
    for i in range(n):
        a0 = 2 * np.pi * i / n; a1 = a0 + np.pi / n
        d.polygon([(cx, cy), (cx + R * np.cos(a0), cy + R * np.sin(a0)), (cx + R * np.cos(a1), cy + R * np.sin(a1))], fill=c2)
    glow = Image.new("L", size, 0); ImageDraw.Draw(glow).ellipse([cx - 520, cy - 420, cx + 520, cy + 420], fill=255)
    im = Image.composite(Image.new("RGB", size, (255, 252, 220)), im, glow.filter(ImageFilter.GaussianBlur(160)))
    vig = Image.new("L", size, 0); ImageDraw.Draw(vig).rectangle([0, 0, w, h], fill=0)
    y, x = np.ogrid[:h, :w]
    r = np.sqrt(((x - w / 2) / (w * 0.7)) ** 2 + ((y - h / 2) / (h * 0.75)) ** 2)
    a = (np.clip(r - 0.55, 0, 1) * 300).clip(0, 140).astype(np.uint8)
    return Image.composite(Image.new("RGB", size, (60, 10, 0)), im, Image.fromarray(a))


def face(name, h, ratio=None):
    """立ち絵の上半身を大きく切り出し、下のほうはなめらかに消す"""
    im = Image.open(os.path.join(HERE, "chara", name + ".png")).convert("RGBA")
    r = ratio or (0.48 if name == "zundamon" else 0.42)
    im = im.crop((0, 0, im.width, int(im.height * r)))
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    a = np.array(im.split()[3]).astype(np.float32)
    fade = np.clip((h - np.arange(h)) / (h * 0.22), 0, 1)[:, None]
    im.putalpha(Image.fromarray((a * fade).astype(np.uint8)))
    return im


def with_shadow(base, img, pos, blur=14, alpha=0.45, off=(10, 14), outline=None):
    a = img.split()[3]
    if outline:
        o = a.filter(ImageFilter.MaxFilter(outline * 2 + 1))
        ol = Image.new("RGBA", img.size, (255, 255, 255, 0)); ol.putalpha(o)
        base.alpha_composite(ol, pos)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha)))
    base.alpha_composite(sh, (pos[0] + off[0], pos[1] + off[1])); base.alpha_composite(img, pos)


def thumb(sc):
    """よく見る解説動画のサムネイルの型：集中線＋主役の大きな画像＋太い二重縁取りの大文字＋キャラの顔とふきだし
    台本の thumb: top（上の文字）, main（下の特大文字）, hero（主役の画像）, sub（比べる画像）, sub_label, bubble（ふきだし）, badge"""
    tb = sc.get("thumb") or {}
    top = tb.get("top") or tb.get("text1") or "ポケモンの"
    main = tb.get("main") or tb.get("text2") or "意外な裏話"
    hero = tb.get("hero") or (tb.get("imgs") or [None])[0]
    sub = tb.get("sub")
    bubble = tb.get("bubble") or "知らなかったのだ！"
    badge = tb.get("badge") or f"ポケモン雑学 {len(sc['topics'])}選"
    th = burst((W, H), (92, 40, 160), (124, 70, 200), n=32, center=(W * 0.47, H * 0.50)).convert("RGBA")
    d = ImageDraw.Draw(th)
    # 主役の画像（大きく、太い白フチ）
    if hero:
        s = load_img(hero)
        if s is not None:
            s = fit(s, 640, 600, hero.split(":")[0] in PIXEL_KINDS)
            with_shadow(th, s, (int(W * 0.47 - s.width / 2), int(H * 0.53 - s.height / 2)), outline=14, alpha=0.6)
    # 比べる画像（赤丸で囲んで矢印）
    if sub:
        s = load_img(sub)
        if s is not None:
            s = fit(s, 270, 270, sub.split(":")[0] in PIXEL_KINDS)
            cx, cy, r = 250, 540, 180
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255), outline=(230, 20, 30), width=18)
            th.alpha_composite(s, (cx - s.width // 2, cy - s.height // 2))
            ax = cx + r + 10
            d.polygon([(ax, cy - 34), (ax + 90, cy - 34), (ax + 90, cy - 85), (ax + 190, cy), (ax + 90, cy + 85), (ax + 90, cy + 34), (ax, cy + 34)],
                      fill=(230, 20, 30), outline=(255, 255, 255), width=8)
            tag = tb.get("sub_label", "初期")
            d.rounded_rectangle([cx - 100, cy - r - 46, cx + 100, cy - r + 30], 20, fill=(230, 20, 30), outline=(255, 255, 255), width=6)
            d.text((cx, cy - r - 8), tag, font=F(FONT_K, 48), fill=(255, 255, 255), anchor="mm")
    # ずんだもん（右側）とふきだし
    z = face("zundamon", 640)
    zx, zy = W - z.width + 10, H - z.height - 60
    with_shadow(th, z, (zx, zy), outline=0, alpha=0.5)
    bx, by = W - 300, 150
    d.rounded_rectangle([bx - 270, by - 66, bx + 270, by + 66], 60, fill=(255, 255, 255), outline=(20, 14, 30), width=8)
    d.polygon([(bx - 20, by + 58), (bx + 40, by + 150), (bx + 60, by + 58)], fill=(255, 255, 255), outline=(20, 14, 30))
    d.rectangle([bx - 16, by + 52, bx + 56, by + 64], fill=(255, 255, 255))
    bs = 56
    while F(FONT_K, bs).getlength(bubble) > 500: bs -= 4
    d.text((bx, by), bubble, font=F(FONT_K, bs), fill=(20, 14, 30), anchor="mm")
    # 左上のバッジ
    d.polygon([(0, 0), (600, 0), (540, 116), (0, 116)], fill=(230, 20, 30))
    d.text((40, 58), badge, font=F(FONT_K, 64), fill=(255, 255, 255), anchor="lm")
    # 大きな文字（上に小さめ、下に特大）。右下は再生時間が重なるので空ける
    ts = 112
    while F(FONT_K, ts).getlength(top) > W * 0.52 and ts > 70: ts -= 6
    outlined(th, (W * 0.36, 210), top, ts, (255, 255, 255), inner=(20, 14, 30), outer=(230, 20, 30), w1=12, w2=26)
    size = 210
    while F(FONT_K, size).getlength(main) > W * 0.74 and size > 120: size -= 10
    outlined(th, (W * 0.39, 930), main, size, (255, 240, 0), grad=((255, 250, 130), (255, 130, 0)), w1=18, w2=36)
    return th.convert("RGB").resize((1280, 720), Image.LANCZOS)


def meta(sc, voiced, chapters):
    names = "・".join(tp["jn"] for tp in sc["topics"])
    lines = ["ずんだもんと冥鳴ひまりが、ポケモンの意外な雑学をくわしく紹介します。", "今回のポケモン：" + names, ""]
    lines += [f"{int(t // 60)}:{int(t % 60):02d} {name}" for t, name in chapters]
    srcs = "\n".join(f"・{tp['jn']}　" + "／".join(s for s in tp.get("sources", []) if s) for tp in sc["topics"])
    credit = ("\n\n音声 VOICEVOX:ずんだもん、VOICEVOX:冥鳴ひまり" if voiced else "") + \
        ("\n画像の出典\n" + "\n".join("・" + c for c in CREDITS.values()) if CREDITS else "") + \
        "\n立ち絵 東北ずん子・ずんだもんプロジェクト、冥鳴ひまり公式（イラスト Sameta様）"
    desc = "\n".join(lines) + f"\n\n英語版のポケモン図鑑と日本語訳 → {P.SITE}/\nポケモン図鑑で覚える英単語 → {P.SITE}/p/words.html\n無料の英単語プリント → {P.SITE}/p/print.html\n\n参考にした資料\n{srcs}{credit}\n\n" \
        "※ファンが運営する非公式のチャンネルです。\n#ポケモン #ポケモン雑学 #ずんだもん #冥鳴ひまり"
    return sc["title"][:100], desc[:4900]


if __name__ == "__main__":
    d = dict(names=P.get_json("pokemon_names_jp.json"), stats=P.get_json("pokedex_stats.json"),
             origins=P.get_json("name_origins.json"), back=P.get_json("backstories.json"))
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(hours=9)
    week = int(os.environ["WEEK"]) if os.environ.get("WEEK") else max(0, (now.date() - START).days)
    if not os.path.exists(os.path.join(HERE, "scripts", "long", f"{week:04d}.json")) and os.environ.get("ALLOW_AUTO") != "1":
        print(f"回番号 {week} の台本がまだ無いので、今日は投稿しません"); sys.exit()
    sc = script_for(week, d)
    day = START + datetime.timedelta(days=week)
    base = f"ポケモン雑学_{day.isoformat()}_第{week:03d}回"          # 毎日作るので、日付と回番号で見分けられる名前にする
    mp4, jpg = f"out/{base}.mp4", f"out/{base}_サムネイル.jpg"
    os.makedirs("out", exist_ok=True)
    if os.environ.get("GITHUB_ENV"):
        open(os.environ["GITHUB_ENV"], "a").write(f"OUT_NAME={base}\n")
    voiced, total, chapters = build(sc, mp4)
    title, desc = meta(sc, voiced, chapters); print(title); print(desc); print("長さ", round(total), "秒")
    if os.environ.get("DRY_RUN") == "1": sys.exit()
    os.environ["THUMB"] = jpg
    Z.upload(title, desc, mp4)
