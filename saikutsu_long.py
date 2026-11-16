# ポケモン雑学採掘所の横動画（1920×1080、@poke_zatsugaku、2026-11-16〜）
#   台本と素材は saikutsu/long/NNN/script.json と同じフォルダの画像。
#   画面：背景は採掘場。左上にチャンネル名、右上に「いま何の話か」の帯、中央に大きな画像、
#         左下にめたん、右下にずんだもん、下の中央に字幕（話者ごとに縁取りの色を変える）。
#   特別な行：{"type":"op"} チャンネルOP、{"type":"title","t":"見出し","sub":"小見出し"} 区切り、{"type":"ed"} 終わりの画面
#   画像の書き方（img）：
#     art:142            ポケモンの公式アートワーク（全国図鑑番号。メガシンカなどは PokeAPI の番号）
#     wiki:en:Title      ウィキペディアの記事の代表画像（ja: も可）
#     commons:File.jpg   ウィキメディア・コモンズのファイル
#     csearch:検索語      コモンズの画像検索の1件目
#     row:A|札;B|札      画像を横に並べる（「>」で区切ると矢印でつなぐ）。A は上の書き方
#     table:左=右;左=右   文字の表（技・持ち物・用語の説明用）
#     tiers:強調する階級  Smogon の階級の階段の図
#     sil:A              A を黒いシルエットにして「？」を重ねる（答えを言う前）
#     ファイル名          台本と同じフォルダの画像
#     「A^B」は A が取れないとき B を使う
#   行のほかの項目：label（画像の上の札）、cap（画像の左下の説明）、mark [x,y,r]（赤い丸。画像の中の割合）、
#     big（画面いっぱいの大きな文字）、sec（右上の帯を変える）、face、say、kana
#   環境変数：NUM（回番号）、MODE=sheet（音声なしで1行1コマの一覧だけ作る）／full（動画を作る）
import os, sys, json, re, io, math, wave, subprocess, urllib.request, urllib.parse
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import post as P
import yomi
import saikutsu_shorts as SS
import zatsugaku_long as ZL

HERE = os.path.dirname(os.path.abspath(__file__))
VW, VH, FPS, SR = 1920, 1080, 24, 44100
FD = os.path.join(HERE, "fonts")
F_HOOK = os.path.join(FD, "DelaGothicOne-Regular.ttf")
F_SUB = os.path.join(FD, "MPLUSRounded1c-Black.ttf")
F_SMALL = os.path.join(FD, "MPLUSRounded1c-ExtraBold.ttf")
F_POP = os.path.join(FD, "RocknRollOne-Regular.ttf")
CH = SS.CH
UA = ZL.UA
CREDITS = {}
font = SS.font
stroked = SS.stroked
BOX = (330, 92, 1590, 830)          # 画像を置く場所（立ち絵と字幕を避ける）


# ---------- 画像 ----------
def _get(url, name):
    os.makedirs(os.path.join(HERE, "_cache"), exist_ok=True)
    fn = os.path.join(HERE, "_cache", re.sub(r"[^A-Za-z0-9._-]", "_", name)[-150:])
    if not os.path.exists(fn):
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r: open(fn, "wb").write(r.read())
    return Image.open(fn).convert("RGBA")


def art(n):
    url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{n}.png"
    im = _get(url, f"art_{n}.png"); bb = im.getbbox()
    return im.crop(bb) if bb else im


def wiki(spec):
    lang, _, title = spec.partition(":")
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(title.replace(" ", "_"), safe="")
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r: js = json.loads(r.read().decode())
    src = (js.get("originalimage") or js.get("thumbnail") or {}).get("source")
    if not src: raise RuntimeError("画像のない記事")
    if src.lower().endswith(".svg") and js.get("thumbnail"): src = js["thumbnail"]["source"]
    w = (js.get("originalimage") or {}).get("width", 0)
    if w > 1920 and "/thumb/" not in src and re.search(r"/wikipedia/(commons|en|ja)/", src):   # 大きすぎる原寸は決まった大きさ（1280px）の縮小版
        m = re.search(r"/wikipedia/([a-z]+)/(.+)$", src); fname = m.group(2).rsplit("/", 1)[-1]
        src = f"https://upload.wikimedia.org/wikipedia/{m.group(1)}/thumb/{m.group(2)}/1280px-{fname}"
    src = re.sub(r"/(\d{3,4})px-", lambda mm: "/1280px-" if int(mm.group(1)) not in (1280, 1920, 3840, 960, 500) else mm.group(0), src)
    CREDITS[spec] = f"{title}（{lang}.wikipedia.org の記事の画像。{src.rsplit('/', 1)[-1].split('?')[0]}）"
    try:
        return _get(src, "wiki_" + lang + "_" + title)
    except Exception:                      # 縮小版が取れなければ、記事が示すままの画像
        alt = (js.get("thumbnail") or js.get("originalimage"))["source"]
        return _get(alt, "wiki2_" + lang + "_" + title)


def csearch(q):
    p = urllib.parse.urlencode(dict(action="query", generator="search", gsrsearch=q + " filetype:bitmap", gsrnamespace=6, gsrlimit=1,
                                    prop="imageinfo", iiprop="url", iiurlwidth=1600, format="json"))
    with urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + p, headers=UA), timeout=30) as r:
        pages = json.loads(r.read().decode())["query"]["pages"]
    pg = next(iter(pages.values())); ii = pg["imageinfo"][0]
    CREDITS["csearch:" + q] = pg["title"] + "（ウィキメディア・コモンズ）"
    return _get(ii.get("thumburl") or ii["url"], "cs_" + q)


def fig_row(spec):
    arrow = ">" in spec
    parts = [p for p in re.split(r"[;>]", spec) if p]
    items = []
    for p in parts:
        ref, _, lab = p.partition("|"); items.append((load(ref), lab))
    n = len(items); H = 640; gap = 110 if arrow else 50
    cw = (1800 - gap * (n - 1)) // n
    W = cw * n + gap * (n - 1)
    im = Image.new("RGBA", (W, H + 90), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, (src, lab) in enumerate(items):
        x0 = i * (cw + gap)
        if src is not None:
            s = min(cw / src.width, (H - 20) / src.height); w, h = int(src.width * s), int(src.height * s)
            pic = src.resize((w, h), Image.LANCZOS); px, py = x0 + (cw - w) // 2, (H - h) // 2
            if pic.getchannel("A").getextrema()[0] == 255:
                d.rectangle([px - 8, py - 8, px + w + 8, py + h + 8], fill=(250, 244, 230, 255))
            im.paste(pic, (px, py), pic)
        if lab:
            f = font(F_SUB, 54)
            while d.textlength(lab, font=f) > cw - 10 and f.size > 28: f = font(F_SUB, f.size - 2)
            stroked(d, (x0 + cw // 2, H + 45), lab, f, (255, 255, 255), 8, (0, 0, 0))
        if arrow and i < n - 1:
            ax = x0 + cw + gap // 2; ay = H // 2
            d.polygon([(ax - 34, ay - 40), (ax + 36, ay), (ax - 34, ay + 40)], fill=(255, 214, 90, 255), outline=(0, 0, 0, 255), width=5)
    return im


def fig_table(spec):
    rows = [r.split("=", 1) for r in spec.split(";")]
    f1, f2 = font(F_SUB, 60), font(F_SMALL, 56)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    w1 = max(tmp.textlength(a, font=f1) for a, b in rows) + 70
    w2 = max(tmp.textlength(b, font=f2) for a, b in rows) + 70
    rh = 104; W, H = int(w1 + w2), rh * len(rows)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, (a, b) in enumerate(rows):
        y = i * rh
        d.rectangle([0, y, w1, y + rh - 6], fill=(40, 70, 130, 245))
        d.rectangle([w1, y, W, y + rh - 6], fill=(250, 246, 236, 245))
        d.text((w1 / 2, y + rh / 2 - 3), a, font=f1, fill=(255, 255, 255), anchor="mm")
        d.text((w1 + 35, y + rh / 2 - 3), b, font=f2, fill=(30, 30, 30), anchor="lm")
    return im


def fig_tiers(hl):
    tiers = [("Ubers", "強すぎて禁止"), ("OU", "よく使われる（約4.5%以上）"), ("UU", "あまり使われない"), ("RU", "めったに使われない")]
    if hl.startswith("upto:"):
        tiers = [t for t in tiers if t[0] in hl[5:].split(",")]; hl = ""
    elif hl != "Ubers":
        tiers = tiers[1:]                 # Ubers はその説明をするまで出さない
    W, rh = 1500, 150; im = Image.new("RGBA", (W, rh * len(tiers) + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, (name, desc) in enumerate(tiers):
        y = i * rh; indent = i * 90
        on = name == hl
        d.rounded_rectangle([indent, y, W - 1, y + rh - 18], 18, fill=(255, 214, 90, 255) if on else (250, 244, 230, 245),
                            outline=(255, 40, 40, 255) if on else (0, 0, 0, 255), width=10 if on else 4)
        d.text((indent + 40, y + (rh - 18) / 2), name, font=font(F_HOOK, 70), fill=(30, 30, 30), anchor="lm")
        d.text((indent + 330, y + (rh - 18) / 2), desc, font=font(F_SUB, 52), fill=(30, 30, 30), anchor="lm")
    return im


def fig_sil(ref):
    src = load(ref)
    if src is None: return None
    a = src.getchannel("A"); im = Image.new("RGBA", src.size, (20, 18, 16, 255)); im.putalpha(a)
    if a.getextrema()[0] == 255:      # 写真は黒くつぶして輪郭をぼかす
        g = src.convert("L").point(lambda v: 255 if v < 140 else 0).filter(ImageFilter.GaussianBlur(3))
        im = Image.new("RGBA", src.size, (40, 36, 30, 255)); ov = Image.new("RGBA", src.size, (10, 8, 6, 255)); im.paste(ov, (0, 0), g)
    d = ImageDraw.Draw(im); s = int(min(im.size) * 0.7)
    stroked(d, (im.width // 2, im.height // 2), "？", font(F_HOOK, s), (255, 214, 90), max(6, s // 18), (0, 0, 0))
    return im


def fig_paper(spec):
    """論文の題名を、論文の1ページ目に見立てて見せる（実物の画面がとれないとき）"""
    journal, title, sub = (spec.split("|") + ["", ""])[:3]
    W, H = 1400, 760; im = Image.new("RGBA", (W, H), (252, 251, 247, 255)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 90], fill=(30, 60, 110, 255)); d.text((40, 45), journal, font=font(F_SMALL, 44), fill=(255, 255, 255), anchor="lm")
    y = 150
    for ln in title.split("/"):
        f = font(F_SUB, 54)
        while d.textlength(ln, font=f) > W - 100: f = font(F_SUB, f.size - 2)
        d.text((50, y), ln, font=f, fill=(20, 20, 20), anchor="lm"); y += f.size + 26
    if sub: d.text((50, y + 30), sub, font=font(F_SMALL, 40), fill=(90, 90, 90), anchor="lm")
    for k in range(6): d.rectangle([50, H - 250 + k * 36, W - 50 - (k % 3) * 120, H - 236 + k * 36], fill=(215, 212, 205, 255))
    return im


_IMG = {}
DIR = None


def load(ref):
    if ref in _IMG: return _IMG[ref]
    im = None
    alts = [ref] if ref.startswith("row:") else ref.split("^")      # 並べる図は、中のそれぞれの画像で予備を選ぶ
    for alt in alts:
        try:
            kind, _, arg = alt.partition(":")
            if kind == "art": im = art(arg)
            elif kind == "wiki": im = wiki(arg)
            elif kind == "commons": im = ZL.commons_img(arg)
            elif kind == "web":                              # web:URL（公式サイトの画像など。2026-11-17）
                im = ZL.web_img(arg)
                if im is not None: CREDITS[alt] = arg.split("?")[0]
            elif kind == "csearch": im = csearch(arg)
            elif kind == "row": im = fig_row(arg)
            elif kind == "table": im = fig_table(arg)
            elif kind == "tiers": im = fig_tiers(arg)
            elif kind == "sil": im = fig_sil(arg)
            elif kind == "paper": im = fig_paper(arg)
            elif kind == "site": im = Image.open(os.path.join(HERE, "assets", "img", "site_home.png")).convert("RGBA")
            else: im = Image.open(os.path.join(DIR, alt)).convert("RGBA")
        except Exception as e:
            print("画像を取れない:", alt, repr(e)[:160]); im = None
        if im is not None: break
    _IMG[ref] = im
    return im


# ---------- 背景・飾り ----------
def background():
    rng = np.random.default_rng(11)
    noise = rng.normal(0, 1, (VH // 8, VW // 8)).astype(np.float32)
    noise = np.array(Image.fromarray(((noise + 3) * 40).clip(0, 255).astype(np.uint8)).resize((VW, VH), Image.BICUBIC).filter(ImageFilter.GaussianBlur(6))) / 255.0
    y = np.linspace(0, 1, VH)[:, None]
    base = np.stack([46 + 30 * noise - 18 * y, 34 + 22 * noise - 14 * y, 26 + 16 * noise - 10 * y], -1)
    xx, yy = np.meshgrid(np.linspace(-1, 1, VW), np.linspace(-1, 1, VH))
    glow = np.exp(-((xx) ** 2 * 1.1 + (yy + 0.2) ** 2 * 1.3) * 1.5)[..., None]
    base = base + glow * np.array([70, 44, 18])
    im = Image.fromarray(base.clip(0, 255).astype(np.uint8), "RGB").convert("RGBA")
    d = ImageDraw.Draw(im)
    for x in (120, VW - 120):              # 坑道の柱
        d.rectangle([x - 26, 0, x + 26, VH], fill=(70, 48, 28, 255)); d.rectangle([x - 26, 0, x - 18, VH], fill=(95, 66, 38, 255))
    d.rectangle([0, 0, VW, 30], fill=(70, 48, 28, 255))
    for x in (380, 960, 1540):             # 吊りランプ
        d.line([x, 30, x, 58], fill=(40, 30, 20, 255), width=4)
        g = Image.new("RGBA", (220, 220), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([60, 60, 160, 160], fill=(255, 200, 90, 120))
        g = g.filter(ImageFilter.GaussianBlur(30)); im.paste(g, (x - 110, -40), g)
        d.ellipse([x - 12, 52, x + 12, 76], fill=(255, 224, 140, 255))
    return im


def header(sec):
    im = Image.new("RGBA", (VW, 90), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([24, 18, 360, 74], 28, fill=(20, 16, 12, 235)); d.text((192, 46), "ポケモン雑学採掘所", font=font(F_SMALL, 32), fill=(255, 214, 90), anchor="mm")
    if sec:
        f = font(F_SMALL, 34); w = d.textlength(sec, font=f) + 60
        d.rectangle([VW - 24 - w, 18, VW - 24, 74], fill=(28, 44, 80, 235)); d.rectangle([VW - 24 - w, 18, VW - 16 - w, 74], fill=(255, 214, 90, 255))
        d.text((VW - 24 - w / 2 + 4, 46), sec, font=f, fill=(255, 255, 255), anchor="mm")
    return im


def place_image(base, src, label=None, cap=None, mark=None, zoom=1.0, alpha=1.0, reserve=0):
    bx0, by0, bx1, by1 = BOX; by1 -= reserve
    top = by0 + (70 if label else 0)
    bw, bh = bx1 - bx0, by1 - top
    s = min(bw / src.width, bh / src.height); s = min(s, 4.0)
    w0, h0 = int(src.width * s), int(src.height * s)
    w, h = int(w0 * zoom), int(h0 * zoom)
    pic = src.resize((w, h), Image.LANCZOS)
    x, y = bx0 + (bw - w) // 2, top + (bh - h) // 2
    photo = src.getchannel("A").getextrema()[0] == 255
    d = ImageDraw.Draw(base)
    if photo:
        sh = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([30, 38, w + 30, h + 38], fill=(0, 0, 0, int(170 * alpha)))
        sh = sh.filter(ImageFilter.GaussianBlur(16)); base.paste(sh, (x - 30, y - 30), sh)
        d.rectangle([x - 10, y - 10, x + w + 10, y + h + 10], fill=(250, 244, 230, int(255 * alpha)))
    if alpha < 1: pic = pic.copy(); pic.putalpha(Image.eval(pic.getchannel("A"), lambda v: int(v * alpha)))
    base.paste(pic, (x, y), pic)
    if mark and alpha >= 1:
        mx, my, mr = mark; cx, cy, r = x + mx * w, y + my * h, mr * max(w, h)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 40, 40), width=12)
    if cap and alpha >= 1:
        f = font(F_SMALL, 34); tw = d.textlength(cap, font=f)
        d.rectangle([x, y + h - 56, x + tw + 36, y + h], fill=(0, 0, 0, 230)); d.text((x + 18, y + h - 28), cap, font=f, fill=(255, 255, 255), anchor="lm")
    if label:
        f = font(F_SUB, 60)
        while d.textlength(label, font=f) > bw - 40 and f.size > 30: f = font(F_SUB, f.size - 2)
        stroked(d, ((bx0 + bx1) // 2, by0 + 36), label, f, (255, 230, 80), 10, (0, 0, 0))


def ety_panel(base, ety):
    """学名の言語と意味のテロップ（画像の下のほうに重ねる）。ety = [名前, 説明] か [[名前, 説明], ...]"""
    rows = ety if isinstance(ety[0], (list, tuple)) else [ety]
    d = ImageDraw.Draw(base); bx0, by0, bx1, by1 = BOX
    fn, fe = font(F_SUB, 44), font(F_SMALL, 36)
    hh = 104 * len(rows); y0 = by1 - hh - 6
    w = max(max(d.textlength(a, font=fn), d.textlength(b, font=fe)) for a, b in rows) + 60
    w = min(w, bx1 - bx0); x0 = (bx0 + bx1 - w) // 2
    d.rounded_rectangle([x0, y0, x0 + w, y0 + hh], 18, fill=(20, 24, 40, 228), outline=(255, 214, 90), width=4)
    for k, (a, b) in enumerate(rows):
        yy = y0 + 104 * k
        d.text((x0 + 30, yy + 32), a, font=fn, fill=(255, 220, 90), anchor="lm")
        d.text((x0 + 30, yy + 76), b, font=fe, fill=(255, 255, 255), anchor="lm")


def subtitle(d, ln):
    c = CH[ln["w"]]; text = ln["t"]
    lines = text.split("\n")
    size = 62; f = font(F_SUB, size); maxw = 1220
    if len(lines) == 1 and d.textlength(text, font=f) > maxw:
        lines = SS.wrap(d, text, f, maxw)
    while size > 40 and max(d.textlength(x, font=f) for x in lines) > maxw: size -= 2; f = font(F_SUB, size)
    lh = f.size + 16; n = len(lines); cy = 960 - (n - 1) * lh / 2 + (12 if n == 1 else 0)
    if n >= 3: cy = 1060 - n * lh + lh / 2
    for j, s_ in enumerate(lines):
        stroked(d, (VW // 2, int(cy + j * lh)), s_, f, (255, 255, 255), 12, c["col"])


# ---------- 動画 ----------
class Long:
    def __init__(self, d):
        global DIR
        DIR = d
        self.d = d; self.s = json.load(open(os.path.join(d, "script.json"), encoding="utf-8"))
        self.L = self.s["lines"]
        self.bg = background()
        sec = ""; last = None
        for ln in self.L:
            if ln.get("sec"): sec = ln["sec"]
            ln["_sec"] = sec
            if ln.get("type"): continue
            if ln.get("img"): last = ln["img"]
            ln["_img"] = last
        for ln in self.L:
            if ln.get("_img"): load(ln["_img"])
        self.static = {}

    def listen_face(self, i, who):
        for j in range(i - 1, -1, -1):
            l2 = self.L[j]
            if l2.get("type"): return "normal"
            if l2["w"] == who:
                f = SS.face_of(l2); return f if f in ("shock", "sad", "think") else "normal"
        return "normal"

    def base(self, i, zoom, alpha):
        ln = self.L[i]
        im = self.bg.copy()
        src = _IMG.get(ln.get("_img"))
        if src is not None:
            ety = ln.get("ety"); nrow = (len(ety) if isinstance(ety[0], (list, tuple)) else 1) if ety else 0
            place_image(im, src, ln.get("label"), ln.get("cap"), ln.get("mark"), zoom, alpha, reserve=104 * nrow + 16 if nrow else 0)
        if ln.get("ety") and alpha >= 1: ety_panel(im, ln["ety"])
        h = header(ln["_sec"]); im.paste(h, (0, 0), h)
        return im

    def frame(self, i, t, dur, talking):
        ln = self.L[i]
        if ln.get("type"): return self.special(ln, t, dur, talking)
        prev = self.L[i - 1] if i > 0 else {}
        same = prev.get("_img") == ln.get("_img") and not prev.get("type")
        alpha = 1.0 if same else SS.ease(t / 0.25)
        im = self.base(i, 1.0, alpha)
        d = ImageDraw.Draw(im)
        for who, left in (("m", True), ("z", False)):
            act = ln["w"] == who
            fc = SS.face_of(ln) if act else self.listen_face(i, who)
            th = SS.tachie(who, act and talking and int(t * 9) % 2 == 0, 420, fc)
            if not act:
                th = th.copy(); px = np.array(th).astype(np.float32); px[..., :3] *= 0.62; th = Image.fromarray(px.astype(np.uint8))
            bob = int(abs(np.sin(t * 7)) * 7) if act else 0
            xx = -30 if left else VW - th.width + 30
            im.paste(th, (xx, VH - th.height + 24 - bob), th)
        if ln.get("big"):
            k = SS.ease(t / 0.18)
            ov = Image.new("RGBA", (VW, VH), (0, 0, 0, int(110 * k))); im.alpha_composite(ov)
            d = ImageDraw.Draw(im)
            f = font(F_HOOK, int(170 * (0.7 + 0.3 * k)))
            while d.textlength(ln["big"], font=f) > VW - 200 and f.size > 60: f = font(F_HOOK, f.size - 6)
            stroked(d, (VW // 2, 440), ln["big"], f, (255, 70, 50) if ln.get("bigcol") == "red" else (255, 230, 80), 16, (0, 0, 0))
        d = ImageDraw.Draw(im)
        subtitle(d, ln)
        return im.convert("RGB")

    def special(self, ln, t, dur, talking):
        im = self.bg.copy(); d = ImageDraw.Draw(im)
        typ = ln["type"]
        if typ == "op":
            ov = Image.new("RGBA", (VW, VH), (0, 0, 0, 150)); im.alpha_composite(ov); d = ImageDraw.Draw(im)
            k = SS.ease(t / 0.5)
            stroked(d, (VW // 2, 300), "ポケモンの「深い雑学」を掘り出す", font(F_SUB, 64), (255, 255, 255), 10, (0, 0, 0))
            f = font(F_HOOK, int(150 * (0.8 + 0.2 * k)))
            stroked(d, (VW // 2, 470), "ポケモン雑学採掘所", f, (255, 214, 90), 18, (0, 0, 0))
            for who, x in (("m", 200), ("z", 1720)):
                th = SS.tachie(who, ln.get("w") == who and talking and int(t * 9) % 2 == 0, 400, "happy")
                im.paste(th, (x - th.width // 2, VH - th.height + 20), th)
            if ln.get("t"): subtitle(ImageDraw.Draw(im), ln)
        elif typ == "title":
            ov = Image.new("RGBA", (VW, VH), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            sh = int(-VW + (VW + 300) * SS.ease(t / 0.35))
            for k in range(-4, 30): od.polygon([(sh + k * 120, 0), (sh + k * 120 + 60, 0), (sh + k * 120 - 300, VH), (sh + k * 120 - 360, VH)], fill=(28, 44, 80, 255))
            im.alpha_composite(ov); d = ImageDraw.Draw(im)
            if t > 0.3:
                d.rectangle([0, 360, VW, 720], fill=(20, 16, 12, 235))
                stroked(d, (VW // 2, 440), ln.get("sub", ""), font(F_SUB, 56), (255, 214, 90), 8, (0, 0, 0))
                f = font(F_HOOK, 110)
                while d.textlength(ln["t"], font=f) > VW - 160: f = font(F_HOOK, f.size - 4)
                stroked(d, (VW // 2, 590), ln["t"], f, (255, 255, 255), 14, (0, 0, 0))
        elif typ == "ed":
            im = Image.new("RGBA", (VW, VH), (243, 236, 220, 255)); d = ImageDraw.Draw(im)
            d.text((VW // 2, 90), "今日の採掘はここまで", font=font(F_HOOK, 70), fill=(60, 40, 20), anchor="mm")
            for x0 in (110, 990):                 # おすすめ動画の枠（YouTube の終了画面の要素を重ねる）
                d.rounded_rectangle([x0, 190, x0 + 820, 190 + 461], 16, fill=(220, 210, 190), outline=(120, 90, 50), width=6)
                d.text((x0 + 410, 190 + 230), "おすすめの動画", font=font(F_SUB, 48), fill=(120, 90, 50), anchor="mm")
            d.ellipse([VW // 2 - 110, 700, VW // 2 + 110, 920], fill=(220, 210, 190), outline=(120, 90, 50), width=6)
            d.text((VW // 2, 810), "登録", font=font(F_SUB, 48), fill=(120, 90, 50), anchor="mm")
            d.rounded_rectangle([110, 730, 760, 900], 20, fill=(255, 255, 255), outline=(30, 30, 30), width=5)
            d.text((435, 790), "英語名も、雑学コラムも", font=font(F_SMALL, 40), fill=(30, 30, 30), anchor="mm")
            d.text((435, 850), "poketango.com", font=font(F_SUB, 52), fill=(214, 64, 140), anchor="mm")
            for who, x in (("m", 1380), ("z", 1680)):
                th = SS.tachie(who, False, 330, "happy"); im.paste(th, (x - th.width // 2, VH - th.height + 10), th)
        return im.convert("RGB")


# VOICEVOX の声色（スタイル）。ID は /speakers で確かめたもの
STYLES = {"m": {"normal": 2, "amaama": 0, "tsun": 6, "sexy": 4, "sasayaki": 36, "hiso": 37},
          "z": {"normal": 3, "amaama": 1, "tsun": 7, "sexy": 5, "sasayaki": 22, "hiso": 38, "hero": 75, "namida": 76}}
AUTO = {"z": {"happy": "amaama"}, "m": {}}   # 悲しみの声（namida）は頻繁だと違和感があるので自動では使わない。ここぞという行だけ "v": "namida"（2026-11-16）


def style_id(ln):
    w = ln.get("w", "m"); v = ln.get("v") or AUTO[w].get(SS.face_of(ln) if not ln.get("type") else "happy", "normal")
    return STYLES[w].get(v, STYLES[w]["normal"])


# 読みとアクセントの直し表。VOICEVOX の読み（AquesTalk 風表記）を OJAD（東京大学のアクセント辞典・スズキクン）で確かめて決めたもの。
# ' がアクセントの下がり目（句の最後に ' があれば平板）、/ は区切りなしの句の境目
KFIX = [
    ("カブ_シキガ'/イシャポ'ケモンニ", "カブ'シキガイシャ/ポケモンニ'"),          # 株式会社ポケモン（途中で切れていた）
    ("センハッピャ_クキュウジュウニ'/トシ'", "セ'ンハッピャク/キュ'ウジュウ/ニ'ネン"),  # 1892年（「とし」と読んでいた）
    ("ニ_クショ_クキョオリュウタルボサウル'スノ", "ニクショクキョオリュウ/タルボサ'ウルスノ"),
    ("ズ'ガイ/ド'ス", "ズガ'イドス"), ("ズ'_ツ/キ'/ポケモンナ'", "ズツキポケモンナ'"),
    ("パキ'/ケファロサウル'_ス", "パキケファロサ'ウル_ス"), ("パキ'/ケファロサウル'ス", "パキケファロサ'ウルス"),
    ("ティ'ラ/ノ'/ナ'/ノダ'", "ティラノナ'/ノダ'"), ("ティ'ラ/ノ'/ホド'", "ティラノホド'"), ("ティ'ラ/ノ'/ヨ'リ", "ティラノヨリ'"),
    ("レ'タエ/ウス'", "レタエ'ウス"), ("アノ'/プ'_ス", "アノプ'_ス"), ("アノ'/プ'ス", "アノプ'ス"),
    ("ペ'イ/ト'イアッテ", "ペイトイアッテ'"), ("ペ'イ/ト'イアガ", "ペイトイアガ'"),
    ("ウィ'ッティン/ト'ンサンノ", "ウィッティントンサンノ'"), ("キョ_ク'/ヒド'ウ/ブ'ツノ", "キョクヒド'オブツノ"),
    ("_シカ'モ/ヒャク'ゴオナ/ノダ'", "_シカ'モ/ユリナ'/ノダ'"), ("ヒャク'ゴオッテ", "ユリッテ'"),       # 百合（「ひゃくごう」と読んでいた）
    ("ショ'_クシュニ/ヒャク'ゴオ", "ショクシュニユリ'"), ("ナマエノ'/ヒャク'ゴオワ", "ナマエノ'/ユリワ'"),
    ("ゾ'ルン/ホオ'/フェ'ンッテ/イ'ウ", "ゾルンホ'オフェンッテ/イウ'"), ("モ'ン/_スペ'", "モンスペ'"),
    ("リリイラガ_クサ'/タ'イプナ", "リ'リイラガ/クサタ'イプナ"), ("リリイラノ'", "リ'リイラノ"), ("リリイラワ'", "リ'リイラワ"), ("リリイラ'", "リ'リイラ"),
    ("ア'アマルド", "アアマ'ルド"),
    # 第004回（2026-11-16）：単語の途中の区切りと「日本」の読み
    ("マチ'テメ/キュ'/ラ'ニ", "マ'チ/テメキュ'ラニ"), ("リザ'アド/ンナ'/ノダ'", "リザ'アドンナ/ノダ'"),
    ("ニッポ'ンダト", "ニホ'ンダト"), ("ニッポ'ンニワ", "ニホ'ンニワ"), ("ニッポ'ンデモ", "ニホ'ンデモ"), ("ニッポ'ンワ", "ニホ'ンワ"),
    ("エ'レ/ブ'ウ", "エレブ'ウ"), ("ダ'イ/イチ'ダン", "ダイイ'チダン"), ("ジュウ'/イチ'マイ", "ジュウイチ'マイ"),
    ("ホ'ロジュウ/ロク'シュルイ", "ホ'ロ/ジュウロ'クシュルイ"), ("ジュウ'/ロク'シュルイ", "ジュウロ'クシュルイ"), ("ジュウ'/_シチ'ニチ", "ジュウ_シチ'ニチ"),
 ("ユレイ'ドル", "ユレ'イドル"), ("ニッポ'ンノ", "ニホ'ンノ"), ("ニッポ'ンデワ", "ニホ'ンデワ"),
    # 第005回（2026-11-17）：年が「にせんじゅう／ろくねん」と割れる、「万件」を「まんげん」と読む、億の割れ
    ("ニセ'ン/ニ'ジュウ/イチ'ネン", "ニセンニジュウイチ'ネン"), ("ニセ'ン/ニ'ジュウ/ヨ'ネン", "ニセンニジュウヨ'ネン"),
    ("ニセ'ン/ニ'ジュウ/ゴ'ネン", "ニセンニジュウゴ'ネン"), ("ニセ'ン/ニ'ジュウ/ロク'ネン", "ニセンニジュウロ'クネン"),
    ("ニセ'ン/ニジュウ'ネン", "ニセンニジュ'ウネン"), ("ニセ'ンジュウ/ロク'ネン", "ニセンジュウロ'クネン"),
    ("ニセ'ンジュウ/ゴ'ネン", "ニセンジュウゴ'ネン"), ("ニセ'ンジュウ/ニ'ネン", "ニセンジュウニ'ネン"),
    ("ニセ'ン/ジュウ'ネン", "ニセンジュ'ウネン"), ("ニセ'ン/サン'ネン", "ニセンサ'ンネン"),
    ("ヤ'_クセン/ゴヒャク'/マン'ゲン", "ヤ'ク/センゴヒャクマ'ンケン"), ("ヤ'_クヒャク/マン'ゲン", "ヤ'ク/ヒャクマ'ンケン"),
    ("ゴヒャク'/マン'ゲン", "ゴヒャクマ'ンケン"), ("ヒャク'/マン'ゲン", "ヒャクマ'ンケン"), ("マン'ゲン", "マ'ンケン"),
    ("ゴセ'ン/オクエン", "ゴセンオ'クエン"), ("サ'ンビャク/オク'マイ", "サンビャクオ'クマイ"),
    ("ジュウ'/クニチズケデ'", "ジュウクニチ'ズケデ"), ("ジュウ'/ロク'ニチ", "ジュウロク'ニチ"),
    ("ナ'イ/アンティ'ック", "ナイアンティ'ック"), ("イン'キュウ/テ'ル", "インキュ'ウテル"), ("ブ'イ/ピ'イ/エ'ス", "ブイピイエ'ス"),
    ("マ'ク/レ'ン/ド'ン", "マクレ'ンドン"), ("ゴセ'ン/マ'ンコ", "ゴセンマ'ンコ"), ("ヒャク'/ゴジュッ'チョオ", "ヒャクゴジュッ'チョオ"),
]


FIXLOG = []


def fixed_kana(ln, speaker):
    """VOICEVOX の読みに直し表を当てる。直すところが無ければ None"""
    import urllib.request, urllib.parse
    if ln.get("kana"): return ln["kana"]
    text = ln.get("say") or ln["t"]
    try:
        yomi.prepare(P.VV, text)                   # ポケモン名をユーザー辞書に（崩れる名前だけ）
        q = json.loads(urllib.request.urlopen(urllib.request.Request(P.VV + "/audio_query?" + urllib.parse.urlencode({"text": text, "speaker": speaker}), method="POST"), timeout=90).read())
    except Exception:
        return None
    k0 = q.get("kana", ""); k = k0
    for a, b in KFIX: k = k.replace(a, b)
    k = yomi.autofix(k, text)                      # 「なのだ」の割れなど、確実に直せる崩れ
    return k if k != k0 else None


def durations(L, voiced_lines):
    segs, voices, t0 = [], [], 0.2
    for i, ln in enumerate(L):
        v = voiced_lines[i]
        if ln.get("type") == "ed": dur, talk = 20.0, 0
        elif ln.get("type") == "title": dur, talk = 2.6, 0
        else:
            talk = (len(v) / SR) if v is not None else max(1.4, len(ln.get("t", "")) * 0.11)
            dur = talk + (0.9 if ln.get("type") == "op" else 0.28)
            if ln.get("big"): dur += 0.4
        segs.append((i, dur, talk)); voices.append((t0 + (0.6 if ln.get("type") == "op" else 0.0), v)); t0 += dur
    return segs, voices, t0


def sheet(L_obj, out):
    """1行1コマの一覧（確認用）"""
    L = L_obj.L; tiles = []
    for i, ln in enumerate(L):
        fr = L_obj.frame(i, 1.0, 2.0, False).resize((480, 270), Image.LANCZOS)
        d = ImageDraw.Draw(fr); d.rectangle([0, 0, 60, 30], fill=(0, 0, 0)); d.text((4, 2), str(i), font=font(F_SMALL, 22), fill=(255, 255, 0))
        tiles.append(fr)
    os.makedirs(out, exist_ok=True)
    per = 20
    for k in range(0, len(tiles), per):
        g = Image.new("RGB", (480 * 4, 270 * 5), (0, 0, 0))
        for j, tl in enumerate(tiles[k:k + per]): g.paste(tl, ((j % 4) * 480, (j // 4) * 270))
        g.save(os.path.join(out, f"sheet_{k // per:02d}.jpg"), quality=82)
    for i in (3, 20, 60):                 # 原寸でも数枚
        if i < len(L): L_obj.frame(i, 1.0, 2.0, False).save(os.path.join(out, f"full_{i:03d}.jpg"), quality=88)


BGM_DIR = os.path.join(HERE, "assets", "bgm")
BGM_ROTATION = ["ichimono", "nichiyou", "manabiya", "taai", "haru"]


def load_mp3(name):
    p = os.path.join(BGM_DIR, name + ".mp3")
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", p, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768


def bgm_tracks(total, sections, bgms, segs):
    """区切りごとに曲を変える。行に "bgm" があればその曲に切り替える。前後は0.8秒でフェード"""
    n = int(total * SR); out = np.zeros(n, dtype=np.float32)
    # 行ごとの開始時刻
    starts, t = [], 0.2
    for (_, dur, _) in segs: starts.append(t); t += round(dur * FPS) / FPS
    cuts = []                                    # (時刻, 曲名 か None＝ローテーション, 指定かどうか)
    for k, st in enumerate(starts):
        if bgms[k]: cuts.append([st, bgms[k], True]); continue
        hit = [p for (x, p) in sections if abs(x - st) < 1e-3]
        if hit: cuts.append([st, "ed" if hit[-1] == "ed" else None, hit[-1] == "ed"])
    cuts.sort(key=lambda c: c[0])
    merged = []
    for c in cuts:                                # 5秒以内に続く切り替えはまとめる（指定の曲を優先し、始まりは前の時刻）
        if merged and c[0] - merged[-1][0] < 5.0:
            if c[2] or not merged[-1][2]: merged[-1] = [merged[-1][0], c[1], c[2]]
            continue
        merged.append(c)
    rot = 0; prev = None; out_cuts = []
    for st, name, ex in merged:                   # ローテーションは直前と同じ曲を選ばない
        if name is None:
            for _ in range(len(BGM_ROTATION)):
                name = BGM_ROTATION[rot % len(BGM_ROTATION)]; rot += 1
                if name != prev: break
        if name == prev: continue                 # 同じ曲ならそのまま流し続ける
        out_cuts.append((st, name)); prev = name
    cuts = out_cuts; cache = {}
    for j, (st, name) in enumerate(cuts):
        en = cuts[j + 1][0] if j + 1 < len(cuts) else total
        if en - st < 0.5: continue
        if name not in cache: cache[name] = load_mp3(name)
        src = cache[name]; a, b = int(st * SR), min(n, int(en * SR)); L_ = b - a
        seg = np.tile(src, L_ // len(src) + 1)[:L_].copy()
        f = min(int(0.8 * SR), L_ // 3)
        seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
        out[a:b] += seg
    return out * 0.22


def thumbnail(d, out_dir):
    """サムネイル（1280×720）。台本の "thumb" に従う：{"pre": 前置き, "big": [大きい2行], "hl": 色を変える行の番号, "main": 主役の画像, "back": 背景の写真, "row": [下に並べる画像]}"""
    import glob
    th = json.load(open(os.path.join(d, "script.json"), encoding="utf-8")).get("thumb")
    if not th: return
    W, H = 1280, 720
    cand = sorted(glob.glob("/usr/share/fonts/**/NotoSerifCJK-Black.ttc", recursive=True) + glob.glob("/usr/share/fonts/**/NotoSerifCJK-Bold.ttc", recursive=True))
    FM = cand[0] if cand else F_HOOK
    im = Image.new("RGBA", (W, H), (18, 14, 12, 255))
    back = load(th["back"]) if th.get("back") else None
    if back is not None:                           # 右側に化石の写真をぼかさずに置き、左へ向けて暗くする
        b = back.convert("RGB"); s = max(W * 0.72 / b.width, H / b.height); b = b.resize((int(b.width * s), int(b.height * s)), Image.LANCZOS)
        x0 = W - b.width; y0 = (H - b.height) // 2; im.paste(b, (x0, y0))
    g = np.zeros((H, W, 4), dtype=np.uint8); xs = np.linspace(0, 1, W)
    a = np.clip(1.05 - xs * 1.25, 0.18, 0.96); g[..., 3] = (a[None, :] * 255).astype(np.uint8); g[..., :3] = (14, 10, 8)
    im.alpha_composite(Image.fromarray(g, "RGBA"))
    main = load(th["main"]) if th.get("main") else None
    ch = th.get("chara")                           # ["z", "shock"]：表情を誇張した立ち絵を右下に大きく置く（2026-11-16）
    if main is not None:
        if ch:                                     # 立ち絵があるときは、文字と立ち絵の間（x 680〜880）に収める
            s = min(200 / main.width, 540 / main.height); m = main.resize((int(main.width * s), int(main.height * s)), Image.LANCZOS)
            mx, my = 680 + (200 - m.width) // 2, 90 + (540 - m.height) // 2
        else:
            s = 470 / max(main.width, main.height); m = main.resize((int(main.width * s), int(main.height * s)), Image.LANCZOS)
            mx, my = W - m.width - 40, 20
        sh = Image.new("RGBA", m.size, (0, 0, 0, 0)); sh.putalpha(m.getchannel("A").point(lambda v: int(v * 0.6))); sh = sh.filter(ImageFilter.GaussianBlur(12))
        im.alpha_composite(sh, (mx + 10, my + 14)); im.alpha_composite(m, (mx, my))
    if ch:
        t_ = SS.tachie(ch[0], False, 500, ch[1] if len(ch) > 1 else "surprise")
        if ch[0] == "m": t_ = t_.transpose(Image.FLIP_LEFT_RIGHT)
        sh = Image.new("RGBA", t_.size, (0, 0, 0, 0)); sh.putalpha(t_.getchannel("A").point(lambda v: int(v * 0.7))); sh = sh.filter(ImageFilter.GaussianBlur(10))
        x_ = W - t_.width - 10; y_ = H - t_.height
        im.alpha_composite(sh, (x_ + 8, y_ + 6)); im.alpha_composite(t_, (x_, y_))
    row = [load(r) for r in ([] if ch else th.get("row", []))]
    row = [r for r in row if r is not None]
    for k, r in enumerate(row):                    # 下に小さく並べる（ほかに出てくるポケモン）
        s = 150 / max(r.width, r.height); rr = r.resize((int(r.width * s), int(r.height * s)), Image.LANCZOS)
        x = W - (len(row) - k) * 165 - 20; y = H - rr.height - 18
        im.alpha_composite(rr, (x, y))
    d_ = ImageDraw.Draw(im)
    fp = ImageFont.truetype(FM, 50); y = 110
    d_.text((60, y), th["pre"], font=fp, fill=(255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0), anchor="lm")
    y += 70
    for k, t in enumerate(th["big"]):
        f = ImageFont.truetype(FM, 150)
        while d_.textlength(t, font=f) > 700: f = ImageFont.truetype(FM, f.size - 6)
        col = (255, 214, 40) if k == th.get("hl", -1) else (255, 255, 255)
        d_.text((66, y + f.size // 2 + 8), t, font=f, fill=(0, 0, 0, 200), anchor="lm")           # 影
        d_.text((58, y + f.size // 2), t, font=f, fill=col, stroke_width=12, stroke_fill=(0, 0, 0), anchor="lm")
        y += f.size + 30
    im.convert("RGB").save(os.path.join(out_dir, "thumbnail.png"))


def accent_dump(L, out_dir):
    """全行の読みとアクセント（VOICEVOX の AquesTalk 風表記）を書き出す。' がアクセントの山、/ と 、が句の区切り"""
    import urllib.request, urllib.parse
    vv = SS.P.VV
    def req(path, data=None):
        h = {"Content-Type": "application/json"} if data else {}
        return urllib.request.urlopen(urllib.request.Request(vv + path, data=data, headers=h, method="POST"), timeout=90).read()
    sp = urllib.request.urlopen(vv + "/speakers", timeout=60).read()
    open(os.path.join(out_dir, "speakers.json"), "wb").write(sp)
    out, todo = [], []
    for i, ln in enumerate(L):
        if ln.get("type") in ("title", "ed") or not ln.get("t"): continue
        text = ln.get("say") or ln["t"]
        yomi.prepare(vv, text)
        q = json.loads(req("/audio_query?" + urllib.parse.urlencode({"text": text, "speaker": 3})))
        k = ln.get("kana") or q.get("kana", "")
        if not ln.get("kana"):
            for a, b in KFIX: k = k.replace(a, b)
            k = yomi.autofix(k, text)
        row = f"{i}\t{ln.get('w')}\t{text.replace(chr(10), '')}\t{k}"
        iss = [] if ln.get("kana") else yomi.issues(vv, text, k)
        if iss:
            row += "\t# 要確認：" + " ／ ".join(iss); todo.append(row)
        out.append(row)
    head = [f"# 要確認 {len(todo)} 行（# 要確認 の付いた行を OJAD で確かめる。台本に kana を書いた行は点検しない）"]
    reg = yomi.registered()
    if reg:
        head.append("# ユーザー辞書に登録した言葉：" + "、".join(f"{s}（{p}・{a}型・{why}）" for s, p, a, why in reg))
    open(os.path.join(out_dir, "accent.txt"), "w", encoding="utf-8").write("\n".join(head + [""] + out))
    open(os.path.join(out_dir, "accent_todo.txt"), "w", encoding="utf-8").write("\n".join(todo))


def build(d, out_dir):
    S = Long(d); L = S.L
    os.makedirs(out_dir, exist_ok=True)
    json.dump(CREDITS, open(os.path.join(out_dir, "credits.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if os.environ.get("MODE", "full") == "sheet":
        sheet(S, out_dir); thumbnail(d, out_dir); return
    thumbnail(d, out_dir)
    if os.environ.get("MODE") == "thumb": return
    if os.environ.get("MODE") == "accent":
        accent_dump(L, out_dir); return
    vs = []
    for ln in L:
        if ln.get("type") in ("title", "ed") or not ln.get("t"): vs.append(None); continue
        k = fixed_kana(ln, style_id(ln))
        if k: FIXLOG.append(f"{len(vs)}\t{k}")
        vs.append(SS.tts(dict(ln, kana=k) if k else ln, style_id(ln)))
    segs, voices, total = durations(L, vs)
    os.makedirs("_l", exist_ok=True); parts = []
    for k, (i, dur, talk) in enumerate(segs):
        nfr = max(1, int(round(dur * FPS))); step = 2
        for j in range(0, nfr, step):
            tt = j / FPS
            S.frame(i, tt, dur, tt < talk).save(f"_l/f_{j // step:04d}.jpg", quality=88)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS / step), "-i", "_l/f_%04d.jpg", "-t", f"{nfr / FPS:.3f}",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-r", str(FPS), f"_l/p{k:04d}.mp4"], check=True)
        for fn in os.listdir("_l"):
            if fn.startswith("f_"): os.remove(os.path.join("_l", fn))
        parts.append(f"p{k:04d}.mp4")
    open("_l/list.txt", "w").write("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "_l/list.txt", "-c", "copy", "_l/v.mp4"], check=True)
    total = sum(round(dur * FPS) / FPS for _, dur, _ in segs)
    # BGM：区切りごとに旋律を変え、終わりの画面は別の曲
    sections, t, pi = [], 0.2, 0
    for (i, dur, _) in segs:
        ln = L[i]
        if ln.get("type") in ("op", "title") or i == 0: sections.append((t, pi)); pi += 1
        if ln.get("type") == "ed": sections.append((t, "ed"))
        t += round(dur * FPS) / FPS
    mix = bgm_tracks(total, sections, [L[i].get("bgm") for (i, _, _) in segs], segs)
    # 効果音は「起きた瞬間」だけ（sfx.py の作法）。章のタイトル=シュッ、大きな一言=ドン、赤丸=ポン、答え（"ans"）=衝撃音かキラーン
    import sfx
    t = 0.2; ev = []; prev_mark = None
    for (i, dur, _) in segs:
        ln = L[i]
        if i == 0: ev.append((t, "impact"))
        if ln.get("type") == "title": ev.append((t, "whoosh"))
        if ln.get("big"): ev.append((t, "boom"))
        if ln.get("mark") and ln.get("mark") != prev_mark: ev.append((t + 0.2, "pop"))
        if ln.get("ans"): ev.append((t, ln["ans"] if ln["ans"] in sfx.KIND else "impact"))
        prev_mark = ln.get("mark")
        t += round(dur * FPS) / FPS
    ev = sfx.thin(ev, total, per30=6, gap=2.0); sfx.add(mix, ev, SR); print("効果音", len(ev), "個")
    for t0, v in voices:
        if v is None: continue
        a = int(t0 * SR); b = min(len(mix), a + len(v)); mix[a:b] = mix[a:b] * 0.4 + v[:b - a]
    mix = np.clip(mix, -1, 1)
    with wave.open("_l/a.wav", "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 30000).astype(np.int16).tobytes())
    mp4 = os.path.join(out_dir, "saikutsu_long.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "_l/v.mp4", "-i", "_l/a.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-shortest", mp4], check=True)
    # 確認用：数秒おきのコマ一覧と、行ごとの開始時刻
    tl, t = [], 0.2
    for (i, dur, _) in segs:
        tl.append({"i": i, "start": round(t, 2), "dur": round(dur, 2), "t": L[i].get("t", L[i].get("type", ""))}); t += round(dur * FPS) / FPS
    json.dump(tl, open(os.path.join(out_dir, "timeline.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(out_dir, "kana_fixed.txt"), "w", encoding="utf-8").write("\n".join(FIXLOG))
    open(os.path.join(out_dir, "yomi_dict.txt"), "w", encoding="utf-8").write("\n".join(f"{s}\t{p}\t{a}\t{why}" for s, p, a, why in yomi.registered()))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vf", "fps=1/6,scale=384:216,tile=5x6", os.path.join(out_dir, "frames_%02d.jpg")], check=True)
    print("長さ", round(total, 1), "秒")


if __name__ == "__main__":
    num = int(os.environ.get("NUM", "3"))
    d = os.path.join(HERE, "saikutsu", "long", f"{num:03d}")
    build(d, os.path.join(HERE, "out"))
