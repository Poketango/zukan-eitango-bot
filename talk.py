# 図鑑で英単語クイズ：掛け合いの型「英語名の意味、聞いたら二度見する」（2026-11-16 てこ入れ）
#   ・ずんだもんが英語名の意味を自信満々に勘違いし、四国めたんが本当の意味を明かす
#   ・台本は talk/NNNN.json（Claude が由来を裏取りして書く）。若い番号から、まだ出していないものを1本ずつ出す
#   ・見た目：上に2段の見出し（白の前置き＋黄色の極太文字、黒い太縁）、中央に大きな公式イラスト、
#     その下に英語名と「単語→意味」の札、オチの言葉は画面中央に特大で叩きつける、字幕は話者ごとに縁の色を変える
#   ・立ち絵は めたん＝左下、ずんだもん＝右下（坂本アヒル様）。字幕と札は立ち絵より上に置く
# 使い方（試し）: LOCAL_DATA=<サイトのフォルダ> TALK=0000 python talk.py
import os, sys, json, io, glob, math, urllib.request
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import post as P
import music
from post import F, FONT_K, VW, VH, FPS, SR, ZUNDA, METAN, SPEED, tts, ename
from post import F_DELA, F_ROUND, F_ROCK, fit
from formats import Mix, render, seq, ease, pop

HERE = os.path.dirname(os.path.abspath(__file__))
TDIR = os.path.join(HERE, "talk")
WHITE, BLACK, DARK = (255, 255, 255), (0, 0, 0), (31, 41, 51)
YEL, RED = (255, 222, 40), (230, 30, 40)
EDGE = {"z": (40, 140, 40), "m": (200, 50, 120)}           # 字幕の縁の色（ずんだもん＝緑、めたん＝ピンク）
# 動画ごとに背景の色を変える（単調にしない）
THEMES = [((20, 30, 70), (70, 20, 90)), ((10, 60, 70), (20, 30, 60)), ((80, 20, 30), (30, 10, 40)),
          ((20, 50, 30), (10, 30, 50)), ((60, 40, 10), (30, 15, 40)), ((15, 15, 25), (60, 30, 80))]


# ---------- 素材 ----------
_ART, _DATA = {}, {}


def _data(name):
    if name not in _DATA: _DATA[name] = P.get_json(name)
    return _DATA[name]


_GLOW = {}


def glow(cx, cy):
    if (cx, cy) not in _GLOW:
        g = Image.new("RGBA", (VW, VH), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        gd.ellipse([cx - 290, cy - 290, cx + 290, cy + 290], fill=(255, 255, 255, 60))
        _GLOW[(cx, cy)] = g.filter(ImageFilter.GaussianBlur(40))
    return _GLOW[(cx, cy)]


def art(key):
    """大きな公式イラスト。取れなければ手元の art_番号.png、最後はドット絵"""
    if key in _ART: return _ART[key]
    im = None
    try: pid = int(_data("pokedex_stats.json")[key]["id"])
    except Exception: pid = None
    if pid:
        try:
            with urllib.request.urlopen(f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pid}.png", timeout=20) as r:
                im = Image.open(io.BytesIO(r.read())).convert("RGBA")
        except Exception as e:
            print("公式イラストなし", key, repr(e)[:80])
            p = os.path.join(HERE, "assets", "img", f"art_{pid}.png")
            if os.path.exists(p): im = Image.open(p).convert("RGBA")
    if im is None:
        sp = P.sprite(key)
        if sp is not None: im = P.big(sp, 640)
    if im is not None:
        bb = im.getbbox()
        if bb: im = im.crop(bb)
    _ART[key] = im
    return im


def fit_art(im, size):
    s = size / max(im.size)
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)


_CH = {}


def chara(who, face, open_):
    name = "zundamon" if who == "z" else "metan"
    k = (name, face, open_)
    if k not in _CH:
        p = os.path.join(HERE, "chara", f"{name}_h_{face}{'_open' if open_ else ''}.png")
        if not os.path.exists(p): p = os.path.join(HERE, "chara", f"{name}_h{'_open' if open_ else ''}.png")
        im = Image.open(p).convert("RGBA")
        im = im.crop((0, 0, im.width, int(im.height * 0.62)))
        H = 400
        im = im.resize((round(im.width * H / im.height), H), Image.LANCZOS)
        if who == "m": im = im.transpose(Image.FLIP_LEFT_RIGHT)     # 左下から画面の中央を向く
        _CH[k] = im
    return _CH[k]


# ---------- 文字 ----------
def stroke_text(d, xy, s, font, fill, sw, sc, anchor="mm"):
    d.text(xy, s, font=font, fill=fill, stroke_width=sw, stroke_fill=sc, anchor=anchor)


def wrap(d, s, font, maxw):
    """字幕の改行：文節で折る post.jwrap を使い、行の長さがそろう幅まで縮めてバランスを取る"""
    lines = P.jwrap(d, s, font, maxw); n = len(lines); w = maxw
    while n > 1 and w > maxw * 0.5:
        t = P.jwrap(d, s, font, w - 20)
        if len(t) > n: break
        lines = t; w -= 20
    return lines


# ---------- 1コマ ----------
def bg(theme, t):
    c1, c2 = theme
    a = np.linspace(0, 1, VH)[:, None, None]
    arr = (np.array(c1)[None, None, :] * (1 - a) + np.array(c2)[None, None, :] * a)
    im = Image.fromarray(np.repeat(arr, VW, axis=1).astype(np.uint8)).convert("RGBA")
    # ななめのストライプ（ゆっくり流れる）
    o = Image.new("RGBA", (VW, VH), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    off = int(t * 40) % 160
    for x in range(-VH, VW + 160, 160):
        d.polygon([(x + off, 0), (x + off + 60, 0), (x + off + 60 - VH * 0.5, VH), (x + off - VH * 0.5, VH)], fill=(255, 255, 255, 14))
    im.alpha_composite(o)
    return im


def headline(im, d, S, t):
    """上の見出し：小さい前置き（白）＋大きい結論（黄、強調語は赤）。黒い線で囲む"""
    x = ease(t / 0.35)
    if x <= 0: return
    y0 = 60 + int((1 - x) * -260)
    d.rounded_rectangle([40, y0, VW - 40, y0 + 300], 34, fill=(0, 0, 0, 200), outline=BLACK, width=10)
    d.rounded_rectangle([46, y0 + 6, VW - 46, y0 + 294], 30, outline=WHITE, width=4)
    f1 = fit(d, S["head1"], F_DELA, 64, VW - 160)
    stroke_text(d, (VW // 2, y0 + 80), S["head1"], f1, WHITE, 8, BLACK)
    h2, hl = S["head2"], S.get("hl", "")
    f2 = fit(d, h2, F_DELA, 110, VW - 140, 60)
    w = d.textlength(h2, font=f2); x0 = VW / 2 - w / 2; yy = y0 + 205
    i = h2.find(hl) if hl else -1
    segs = [(h2, YEL)] if i < 0 else [(h2[:i], YEL), (hl, RED), (h2[i + len(hl):], YEL)]
    for s, c in segs:
        if not s: continue
        d.text((x0, yy), s, font=f2, fill=c, stroke_width=12, stroke_fill=BLACK, anchor="lm")
        x0 += d.textlength(s, font=f2)


def frame(S, st, t, theme):
    """st: その時点の表示状態（key, en, parts, big, sub, who, t_line）"""
    im = bg(theme, t); d = ImageDraw.Draw(im, "RGBA")
    headline(im, d, S, t)
    # 中央の大きなイラスト（出るときだけポンと拡大。出たあとは動かさない）
    a = art(st["key"])
    tl = t - st["t_key"]
    if a is not None:
        sc = pop(tl / 0.35)
        ai = fit_art(a, int(470 * max(0.05, sc)))
        cx, cy = VW // 2, 625
        im.alpha_composite(glow(cx, cy))
        im.alpha_composite(ai, (cx - ai.width // 2, cy - ai.height // 2))
    # 英語名
    if st.get("en"):
        fe = fit(d, st["en"], F_ROCK, 120, VW - 120, 60)
        stroke_text(d, (VW // 2, 935), st["en"], fe, WHITE, 12, BLACK)
    # 単語→意味の札（横に並べ、収まらなければ縮める）
    parts = st.get("parts") or []
    if parts:
        n = len(parts); gap = 18; cw = (VW - 80 - gap * (n - 1)) // n
        for i, (w_, m_) in enumerate(parts):
            x = ease((t - st["t_parts"] - i * 0.18) / 0.25)
            if x <= 0: continue
            x0 = 40 + i * (cw + gap); y0 = 1010 + int((1 - x) * 60)
            d.rounded_rectangle([x0, y0, x0 + cw, y0 + 170], 26, fill=WHITE, outline=BLACK, width=7)
            fw = fit(d, w_, F_ROCK, 62, cw - 30, 30)
            d.text((x0 + cw / 2, y0 + 52), w_, font=fw, fill=DARK, anchor="mm")
            d.line([x0 + 24, y0 + 94, x0 + cw - 24, y0 + 94], fill=(200, 200, 200), width=3)
            fm = fit(d, m_, F_ROUND, 50, cw - 30, 26)
            d.text((x0 + cw / 2, y0 + 132), m_, font=fm, fill=RED, anchor="mm")
    # 字幕（箱なし、太い縁。話者ごとに縁の色を変える）
    if st.get("sub"):
        fs = F(F_ROUND, 62)
        lines = wrap(d, st["sub"], fs, VW - 110)
        if len(lines) > 3: fs = F(F_ROUND, 52); lines = wrap(d, st["sub"], fs, VW - 90)
        lh = fs.size + 16; y = 1250 + lh / 2
        sp = 1 + 0.08 * (1 - ease((t - st["t_line"]) / 0.15))
        for ln in lines:
            f2 = F(F_ROUND, int(fs.size * sp)) if sp > 1.001 else fs
            stroke_text(d, (VW // 2, y), ln, f2, WHITE, 12, EDGE[st["who"]])
            y += lh
    # 立ち絵（話している方は口が動き、少し上下する）
    for who, xL in (("m", -40), ("z", None)):
        face = st["faces"][who]; talking = st["talking"] == who
        c = chara(who, face, talking and int(t * 9) % 2 == 0)
        bob = int(abs(math.sin(t * 7)) * 8) if talking else 0
        x = xL if xL is not None else VW - c.width + 40
        if not talking: c = c.copy(); c.putalpha(c.split()[3].point(lambda v: int(v * 0.85)))
        im.alpha_composite(c, (x, VH - c.height + 30 - bob))
    # オチの言葉を画面中央に特大で叩きつける
    if st.get("big") is not None:
        tb = t - st["t_big"]
        if 0 <= tb < 1.3:
            o = Image.new("RGBA", (VW, VH), (0, 0, 0, int(140 * min(1, tb / 0.1))))
            im.alpha_composite(o); d = ImageDraw.Draw(im, "RGBA")
            s = st["big"]; z = 1.6 - 0.6 * ease(tb / 0.18)
            fb = fit(d, s, F_DELA, int(230 * z), int((VW - 60) * z), 60)
            stroke_text(d, (VW // 2, 760), s, fb, RED if not s.isascii() else YEL, 20, WHITE)
    return im.convert("RGB")


# ---------- 1本 ----------
def build(S, out="short.mp4", seed=0):
    theme = THEMES[seed % len(THEMES)]
    st0 = music.style(seed, "quiz")
    voices = []
    for L in S["lines"]:
        voices.append(tts(L["v"], ZUNDA if L["s"] == "z" else METAN, SPEED))
    # 各せりふの長さ（音声＋少しの間。音声が無いときは文字数から見積もる）
    durs = []
    for L, v in zip(S["lines"], voices):
        base = len(v) / SR + 0.25 if v is not None else max(1.6, len(L["t"]) * 0.11)
        if L.get("big"): base = max(base, 1.4)
        durs.append(base)
    t0 = 0.5                                   # 見出しが入る間
    starts = []; t = t0
    for dd in durs: starts.append(t); t += dd
    total = t + 0.6
    faces = {"z": "normal", "m": "normal"}
    states = []                                # せりふごとの状態
    cur = dict(key=S["key"], t_key=0.0, en=None, parts=None, t_parts=0, big=None, t_big=-9)
    for i, L in enumerate(S["lines"]):
        if L.get("key") and L["key"] != cur["key"]: cur["key"] = L["key"]; cur["t_key"] = starts[i]
        if "en" in L: cur["en"] = L["en"]
        if "parts" in L: cur["parts"] = L["parts"]; cur["t_parts"] = starts[i] + 0.3
        faces = dict(faces); faces[L["s"]] = L.get("face", "normal")
        cur_i = dict(cur, sub=L["t"], who=L["s"], t_line=starts[i], faces=faces,
                     big=L.get("big"), t_big=starts[i] + (len(voices[i]) / SR * 0.55 if voices[i] is not None else 0.6))
        states.append(cur_i)

    def at(T):
        st = dict(states[0]); st.update(sub=None, talking=None, t_line=0)
        for i, s in enumerate(states):
            if T >= starts[i] - 0.05:
                st = dict(s)
                v = voices[i]; vlen = len(v) / SR if v is not None else durs[i] - 0.3
                st["talking"] = s["who"] if T < starts[i] + vlen else None
        if T < starts[0] - 0.05: st["big"] = None
        return st

    segs = [(lambda tt: frame(S, at(tt), tt, theme), total)]
    m = Mix(total, st0)
    m.music(0, total, 0.55)
    m.boom(0.05)                               # 見出しを叩きつける
    for i, s in enumerate(states):
        m.whoosh(starts[i] - 0.1)
        if voices[i] is not None: m.voice(starts[i], voices[i])
        if s.get("big"): m.boom(s["t_big"])
        if S["lines"][i].get("parts"):
            for k in range(len(S["lines"][i]["parts"])): m.pon(s["t_parts"] + k * 0.18)
        if S["lines"][i].get("key"): m.ding(starts[i])
    render(segs, m, out)
    # サムネイル：見出しと大きなイラスト、英語名
    th = frame(S, dict(states[0], sub=None, talking=None, big=None, en=states[0]["en"]), 2.0, theme)
    th.save("thumb.png")


def meta(S):
    k = S["key"]; site = P.SITE
    words = []
    for L in S["lines"]:
        for w, m_ in (L.get("parts") or []): words.append(f"{w}＝{m_}")
    title = f"{S['title']}【英語名の意味】 #shorts"
    desc = (f"{S['title']}。\n" + "\n".join(words) +
            f"\n\n{_data('pokemon_names_jp.json').get(k, '')}の英語版図鑑 → {site}/p/{k}.html\n全ポケモンの英語名と由来 → {site}/p/\n\n"
            "出典：\n" + "\n".join(S.get("src", [])) +
            "\n\nナレーション：VOICEVOX:ずんだもん、VOICEVOX:四国めたん\n立ち絵：坂本アヒル様\n\n#ポケモン #英語名 #英語 #雑学")
    return title, desc


def next_script(done_titles):
    for p in sorted(glob.glob(os.path.join(TDIR, "*.json"))):
        S = json.load(open(p, encoding="utf-8"))
        if meta(S)[0] not in done_titles: return p, S
    return None, None


if __name__ == "__main__":
    S = json.load(open(os.path.join(TDIR, os.environ.get("TALK", "0000") + ".json"), encoding="utf-8"))
    build(S, os.environ.get("OUT", "short.mp4"), int(os.environ.get("SEED", "0")))
    print(*meta(S), sep="\n")
