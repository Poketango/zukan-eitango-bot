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


def load_img(ref):
    """'art:25' などから画像を読む"""
    if ref in _IMG: return _IMG[ref]
    kind, num = ref.split(":")
    p = os.path.join(HERE, "assets", "img", f"{kind}_{num}.png")
    im = None
    if os.path.exists(p):
        im = Image.open(p).convert("RGBA")
        bb = im.getbbox()
        if bb: im = im.crop(bb)
    else:
        print("画像なし:", ref)
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
        z = ease_back(tin / 0.32) * (1 + min(tin, 8) * 0.006)        # ポンと出て、ゆっくりズーム
        s = scaled(s, z, False)
        cx = (x0 + x1) / 2; cy = y0 + 25 + ih / 2
        with_shadow(im, s, (int(cx - s.width / 2), int(cy - s.height / 2)), blur=12, alpha=0.3, off=(8, 10), outline=6)
        if cap: cap_tag(ImageDraw.Draw(im), cx, y1 - 46, x1 - x0 - 80, cap, theme)
        return
    d.rounded_rectangle([x0, y0, x1, y1], 36, fill=(255, 255, 255), outline=theme[0], width=8)
    gap = 30
    cw = (x1 - x0 - 60 - gap * (n - 1)) / n
    for i, (ref, s, cap) in enumerate(items):
        pix = ref.split(":")[0] in PIXEL_KINDS
        ih = (y1 - y0 - 60) - (60 if cap else 0)
        s = fit(s, cw, ih, pix)
        z = ease_back((tin - i * 0.14) / 0.3)                     # 1枚ずつ順番に出る
        if z <= 0.02: continue
        s = scaled(s, z * (1 + 0.015 * np.sin(tin * 2 + i)), pix)
        cx = x0 + 30 + (cw + gap) * i + cw / 2; cy = y0 + 30 + ih / 2
        im.paste(s, (int(cx - s.width / 2), int(cy - s.height / 2)), s)
        if cap and tin > i * 0.14 + 0.15: cap_tag(d, cx, y1 - 50, cw - 20, cap, theme)


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
            while j < len(text) and text[j] in "年月日回キロメートル％%匹人番種倍分秒時間歳円位": j += 1
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
    while lab_f.getlength(label) > W - 160 and lab_f.size > 56: lab_f = FF(FD, lab_f.size - 6)

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
            outlined(lay, (W // 2, 100), label, lab_f.size, (255, 255, 255), inner=(40, 30, 60), outer=theme[0], w1=12, w2=24, font=FD)
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
        if t.startswith(("実は", "ところが", "でもね", "それがね")): inton = 1.1
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
            if ln.get("img"): refs = ln["img"]; tin0 = 0.0
            else: tin0 = None
            add_line(f"その{no}　{tp['jn']}", refs, ln, lines[i + 1] if i + 1 < len(lines) else None, None, theme, tin0)
    chapters.append((state["t"], "エンディング"))
    sections.append((state["t"], 0))
    eds = sc["ending"]
    for i, ln in enumerate(eds):
        add_line(None, ln.get("img"), ln, eds[i + 1] if i + 1 < len(eds) else None, bt, THEMES[0], 0.0 if i == 0 else None)
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
    thumb(sc).save("thumb_long.jpg", quality=92)
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
    voiced, total, chapters = build(sc, "zatsugaku_long.mp4")
    title, desc = meta(sc, voiced, chapters); print(title); print(desc); print("長さ", round(total), "秒")
    if os.environ.get("DRY_RUN") == "1": sys.exit()
    os.environ["THUMB"] = "thumb_long.jpg"
    Z.upload(title, desc, "zatsugaku_long.mp4")
