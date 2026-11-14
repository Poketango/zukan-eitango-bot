# 図鑑で英単語クイズ：新しいショート動画の型（2026-11-14 試作）
#   plus   … 英語名の足し算クイズ「bulb＋dinosaur＝？」
#   real3  … 本物の英語名はどれ？（3択・ほかの2つは別のポケモンの英語名）
#   speed5 … 英語名5連発（1問2.5秒・何問わかったかコメントで）
#   which  … この英語版図鑑、どのポケモン？（4択）
#   rank   … 英語版図鑑の怖い一文ランキングTOP3
# 使い方: LOCAL_DATA=<サイトのフォルダ> FORMAT=plus N=0 python formats.py
import os, sys, json, random, re, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import post as P
import music
from post import F, FONT_K, FONT_B, FONT_M, VW, VH, FPS, SR, ZUNDA, HIMARI, tts, big, silhouette, ename, center, jwrap, ewrap

DARK, WHITE = (31, 41, 51), (255, 255, 255)


def jwrap2(d, text, font, maxw):
    lines = jwrap(d, text, font, maxw)
    for k in range(1, len(lines)):
        while lines[k] and lines[k][0] in "。、」』！？）":
            lines[k - 1] += lines[k][0]; lines[k] = lines[k][1:]
    return [l for l in lines if l]


def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3


def pop(x):
    """0→1で少し行きすぎて戻る（ポンと出る）"""
    x = max(0.0, min(1.0, x)); return 1 + 2.2 * (x - 1) ** 3 + 1.2 * (x - 1) ** 2 if x < 1 else 1.0


def dur(v, base):
    return max(base, (len(v) / SR + 0.4) if v is not None else 0)


def grad(c1, c2):
    a = np.linspace(0, 1, VH)[:, None, None]
    arr = (np.array(c1)[None, None, :] * (1 - a) + np.array(c2)[None, None, :] * a).astype(np.uint8)
    return Image.fromarray(np.repeat(arr, VW, axis=1))


def dots(im, color, step=90, r=6, alpha=40):
    o = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    for y in range(0, VH, step):
        for x in range((y // step % 2) * step // 2, VW, step): d.ellipse([x - r, y - r, x + r, y + r], fill=color + (alpha,))
    im.paste(o, (0, 0), o); return im


def paste_c(im, sp, cx, cy, scale=1.0):
    if sp is None: return
    if scale != 1.0: sp = sp.resize((max(1, int(sp.width * scale)), max(1, int(sp.height * scale))), Image.NEAREST)
    im.paste(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2)), sp)


def header(d, text, color, sub=None):
    d.rounded_rectangle([60, 70, VW - 60, 230], 40, fill=color)
    center(d, 150, text, F(FONT_K, 76), WHITE)
    if sub: center(d, 290, sub, F(FONT_K, 56), DARK)


def footer(d, line1="答えと由来は全部サイトに", line2="プロフィールのリンクから"):
    d.rectangle([0, VH - 210, VW, VH], fill=DARK)
    center(d, VH - 140, line1, F(FONT_B, 44), WHITE); center(d, VH - 80, line2, F(FONT_B, 44), (255, 224, 102))


def timer(d, cx, cy, frac, n):
    d.ellipse([cx - 95, cy - 95, cx + 95, cy + 95], fill=WHITE)
    d.pieslice([cx - 85, cy - 85, cx + 85, cy + 85], -90, -90 + 360 * frac, fill=(227, 53, 13))
    d.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], fill=WHITE)
    d.text((cx, cy), str(n), font=F(FONT_K, 90), fill=DARK, anchor="mm")


# ---------- 効果音 ----------
class Mix:
    def __init__(s, total, st=None):
        s.n = int(total * SR) + SR; s.a = np.zeros(s.n, np.float32); s.total = total
        s.st = st or music.style(0); s.fx = music.SFX_SETS[s.st["sfx"]]

    def put(s, t0, sig, vol=1.0):
        a = int(t0 * SR); b = min(s.n, a + len(sig))
        if 0 <= a < s.n: s.a[a:b] += sig[:b - a] * vol

    def music(s, t0=0.0, t1=None, vol=1.0):
        """t0〜t1 にBGMを流す（毎回ちがう自作の曲）"""
        t1 = t1 or s.total; seg = music.bgm(s.st, t1 - t0, vol); s.put(t0, seg[:int((t1 - t0) * SR)])

    def tick(s, t): s.put(t, s.fx["tick"]())
    def ding(s, t): s.put(t, s.fx["ding"]())
    def buzz(s, t): s.put(t, s.fx["buzz"]())
    def pon(s, t): s.put(t, s.fx["pop"]())
    def whoosh(s, t):
        n = np.arange(int(0.35 * SR)) / SR
        s.put(t, (np.random.default_rng(int(t * 100)).standard_normal(len(n)) * np.sin(np.pi * n / 0.35) * 0.08).astype(np.float32))
    def boom(s, t):
        n = np.arange(int(1.0 * SR)) / SR
        s.put(t, ((np.random.default_rng(3).standard_normal(len(n)) * 0.4 + np.sin(2 * np.pi * 45 * n)) * np.exp(-n * 3.5) * 0.55).astype(np.float32))

    def voice(s, t, v):
        if v is None: return
        a = int(t * SR); b = min(s.n, a + len(v)); s.a[a:b] = s.a[a:b] * 0.4 + v[:b - a]


def render(segs, mix, out):
    os.makedirs("_f", exist_ok=True); parts = []
    for k, (fn, d) in enumerate(segs):
        nfr = max(1, int(round(d * FPS)))
        for i in range(nfr): fn(i / FPS).save(f"_f/s{k}_{i:04d}.jpg", quality=92)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"_f/s{k}_%04d.jpg", "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "21", "-pix_fmt", "yuv420p", f"_f/s{k}.mp4"], check=True)
        for f in os.listdir("_f"):
            if f.startswith(f"s{k}_"): os.remove(f"_f/{f}")
        parts.append(f"_f/s{k}.mp4")
    open("_list.txt", "w").write("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "_list.txt", "-c", "copy", "_v.mp4"], check=True)
    a = np.clip(mix.a, -1, 1)
    with wave.open("_a.wav", "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((a * 30000).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "_v.mp4", "-i", "_a.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", out], check=True)


def seq(segs):
    """(関数, 秒) の並びから、各区切りの開始時刻を返す"""
    t = 0; out = []
    for _, d in segs: out.append(t); t += round(d * FPS) / FPS
    return out, t


# =========================================================
# 1. 英語名の足し算クイズ
# =========================================================
PLUS_RE = re.compile(r"^英語名「([^」]+)」は、([A-Za-z\-' ]+)（([^）]+)）と([A-Za-z\-' ]+)（([^）]+)）を組み合わせた")


def plus_pool(D):
    out = []
    for k, o in D["origins"].items():
        m = PLUS_RE.match(o["t"])
        if m and k in D["names"] and int(D["stats"].get(k, {}).get("id", 9999)) <= 493:
            out.append(dict(key=k, en=m.group(1), w1=m.group(2), m1=m.group(3), w2=m.group(4), m2=m.group(5)))
    return out


def plus_frame(q, sp, t, st):
    im = dots(grad((255, 236, 179), (255, 196, 120)), (227, 53, 13)); d = ImageDraw.Draw(im)
    header(d, "英語名の足し算クイズ", (227, 53, 13), "このポケモン、だーれだ？")
    cards = [(q["w1"], q["m1"]), (q["w2"], q["m2"])]
    for i, (w, m) in enumerate(cards):
        x = ease((t - 0.3 - i * 0.45) / 0.4)
        if x <= 0: continue
        y0 = 400 + i * 300; off = int((1 - x) * VW)
        d.rounded_rectangle([90 + off, y0, VW - 90 + off, y0 + 230], 36, fill=WHITE, outline=DARK, width=6)
        fw = F(FONT_K, 104 if len(w) <= 9 else 80)
        d.text((VW // 2 + off, y0 + 95), w, font=fw, fill=DARK, anchor="mm")
        d.text((VW // 2 + off, y0 + 185), m, font=F(FONT_B, 46), fill=(184, 41, 10), anchor="mm")
        if i == 0 and x >= 1:
            d.text((VW // 2, y0 + 265), "＋", font=F(FONT_K, 90), fill=DARK, anchor="mm")
    cy = 1350
    if st.get("count") is not None:
        d.text((VW // 2, 1040), "＝", font=F(FONT_K, 90), fill=DARK, anchor="mm")
    if st.get("count") is not None:
        d.ellipse([VW // 2 - 230, cy - 230, VW // 2 + 230, cy + 230], fill=WHITE)
        if sp: paste_c(im, silhouette(big(sp, 360)), VW // 2, cy)
        timer(d, VW - 170, cy - 170, st["frac"], st["count"])
    if st.get("reveal") is not None:
        s = pop(st["reveal"] / 0.35)
        d.ellipse([VW // 2 - 230, cy - 230, VW // 2 + 230, cy + 230], fill=WHITE)
        if sp: paste_c(im, big(sp, 360), VW // 2, cy, max(0.05, s))
        center(d, 1045, "＝ " + q["en"], F(FONT_K, 96 if len(q["en"]) <= 10 else 80), WHITE, 12, DARK)
        center(d, 1640, q["jn"] + "！", F(FONT_K, 96), (227, 53, 13), 10, WHITE)
    footer(d)
    return im


def plus_video(q, sp):
    v1 = tts(f"{voice_word(q['m1'])}、たす、{voice_word(q['m2'])}。このポケモン、だーれだ？", ZUNDA, 1.15)
    v2 = tts(f"正解は、{q['jn']}なのだ！", ZUNDA, 1.12)
    t_in = dur(v1, 2.4)
    segs = [(lambda t: plus_frame(q, sp, t, {}), t_in)]
    for c in (3, 2, 1): segs.append((lambda t, c=c: plus_frame(q, sp, 9, {"count": c, "frac": (c - t) / 3}), 1.0))
    segs.append((lambda t: plus_frame(q, sp, 9, {"reveal": t}), dur(v2, 3.6)))
    st, total = seq(segs); m = Mix(total, STYLE)
    m.music(0, total)
    m.whoosh(0.3); m.whoosh(0.75)
    for c in range(3): m.tick(st[1 + c])
    m.ding(st[4]); m.voice(0.15, v1); m.voice(st[4] + 0.25, v2)
    return segs, m, plus_frame(q, sp, 9, {"reveal": 1})


def voice_word(m):
    return re.sub(r"[A-Za-z「」]", "", m) or m


# =========================================================
# 2. 本物の英語名はどれ？（3択）
# =========================================================
def real3_pick(D, n):
    ids = {k: int(D["stats"][k]["id"]) for k in D["en"] if k in D["stats"] and k in D["names"]}
    pool = sorted([k for k in ids if ids[k] <= 386], key=lambda k: ids[k])
    random.Random(31).shuffle(pool)
    key = pool[n % len(pool)]; E = ename(key)
    r = random.Random(n)
    near = [k for k in ids if k != key and ids[k] <= 649 and ename(k)[0] == E[0] and abs(len(ename(k)) - len(E)) <= 3]
    if len(near) < 2: near = [k for k in ids if k != key and ids[k] <= 649 and abs(len(ename(k)) - len(E)) <= 2]
    dec = r.sample(near, 2)
    opts = [key] + dec; r.shuffle(opts)
    return dict(key=key, opts=opts)


def real3_frame(q, sp, st, D):
    im = dots(grad((198, 232, 255), (120, 180, 240)), (31, 90, 145)); d = ImageDraw.Draw(im)
    header(d, "本物の英語名はどれ？", (31, 90, 145), f"「{q['jn']}」の英語名は…")
    d.ellipse([VW // 2 - 230, 360, VW // 2 + 230, 820], fill=WHITE)
    if sp: paste_c(im, big(sp, 360), VW // 2, 590)
    rv = st.get("reveal")
    for i, k in enumerate(q["opts"]):
        x = ease((st.get("t", 9) - 0.2 - i * 0.25) / 0.3)
        if x <= 0: continue
        y = 900 + i * 210; off = int((1 - x) * VW)
        ok = k == q["key"]
        fill = WHITE if rv is None else ((214, 245, 214) if ok else (240, 240, 240))
        outl = DARK if rv is None else ((47, 168, 79) if ok else (200, 200, 200))
        d.rounded_rectangle([90 + off, y, VW - 90 + off, y + 170], 40, fill=fill, outline=outl, width=8)
        d.ellipse([120 + off, y + 35, 220 + off, y + 135], fill=(31, 90, 145))
        d.text((170 + off, y + 85), "ABC"[i], font=F(FONT_K, 64), fill=WHITE, anchor="mm")
        E = ename(k); d.text((VW // 2 + 50 + off, y + 85), E, font=F(FONT_K, 86 if len(E) <= 10 else 66),
                            fill=DARK if (rv is None or ok) else (150, 150, 150), anchor="mm")
        if rv is not None:
            if ok: d.text((VW - 150, y + 85), "◎", font=F(FONT_K, 90), fill=(47, 168, 79), anchor="mm")
            else:
                d.text((VW - 150, y + 85), "×", font=F(FONT_K, 90), fill=(227, 53, 13), anchor="mm")
                d.text((VW // 2 + 50, y + 150), f"↑ これは{D['names'][k]}", font=F(FONT_B, 36), fill=(120, 120, 120), anchor="mm")
    if st.get("count"): timer(d, VW - 160, 600, st["frac"], st["count"])
    footer(d, "全ポケモンの英語名は", "プロフィールのサイトで")
    return im


def real3_video(q, sp, D):
    v1 = tts(f"{q['jn']}の、本物の英語名はどれ？", ZUNDA, 1.15)
    v2 = tts(f"正解は、{['エー', 'ビー', 'シー'][q['opts'].index(q['key'])]}なのだ！", ZUNDA, 1.12)
    t_in = dur(v1, 1.8)
    segs = [(lambda t: real3_frame(q, sp, {"t": t}, D), t_in)]
    for c in (3, 2, 1): segs.append((lambda t, c=c: real3_frame(q, sp, {"count": c, "frac": (c - t) / 3}, D), 1.0))
    segs.append((lambda t: real3_frame(q, sp, {"reveal": t}, D), dur(v2, 3.4)))
    st, total = seq(segs); m = Mix(total, STYLE)
    m.music(0, total)
    for i in range(3): m.pon(0.2 + i * 0.25)
    for c in range(3): m.tick(st[1 + c])
    m.ding(st[4]); m.voice(0.1, v1); m.voice(st[4] + 0.25, v2)
    return segs, m, real3_frame(q, sp, {"count": 3, "frac": 1}, D)


# =========================================================
# 3. 英語名5連発
# =========================================================
def speed5_pick(D, n):
    ids = {k: int(D["stats"][k]["id"]) for k in D["en"] if k in D["stats"] and k in D["names"]}
    lv = n % 3   # 0:かんたん(初代) 1:ふつう(2〜3世代) 2:むずかしい(4〜5世代)
    rng = [(1, 151), (152, 386), (387, 649)][lv]
    pool = sorted([k for k in ids if rng[0] <= ids[k] <= rng[1]], key=lambda k: ids[k]); random.Random(55 + lv).shuffle(pool)
    s = (n // 3) * 5
    return dict(keys=[pool[(s + i) % len(pool)] for i in range(5)], level=["かんたん", "ふつう", "むずかしい"][lv])


def speed5_frame(q, sps, st, D):
    im = grad((34, 30, 60), (90, 40, 120)); d = ImageDraw.Draw(im)
    for k in range(18):
        a0 = k * 20; d.pieslice([-900, -300, VW + 900, VH + 1500], a0 + st.get("spin", 0), a0 + 10 + st.get("spin", 0), fill=(60, 50, 100))
    d.rounded_rectangle([60, 70, VW - 60, 230], 40, fill=(255, 203, 5))
    center(d, 150, f"英語名5連発【{q['level']}】", F(FONT_K, 72), DARK)
    i = st.get("i")
    if i is None:
        center(d, 760, "1問2.5秒！", F(FONT_K, 120), WHITE, 10, DARK)
        center(d, 920, "英語名だけで", F(FONT_K, 92), (255, 224, 102))
        center(d, 1040, "ポケモンを当てろ", F(FONT_K, 92), (255, 224, 102))
        center(d, 1240, "何問わかった？", F(FONT_K, 80), WHITE)
        center(d, 1340, "コメントで教えて！", F(FONT_K, 80), WHITE)
        return im
    for j in range(5):
        c = (255, 203, 5) if j < i else ((255, 255, 255) if j == i else (90, 80, 130))
        d.ellipse([VW // 2 - 250 + j * 110, 280, VW // 2 - 190 + j * 110, 340], fill=c)
    k = q["keys"][i]; E = ename(k)
    center(d, 470, f"第{i + 1}問", F(FONT_K, 70), (255, 224, 102))
    s = pop(st.get("t", 1) / 0.25)
    fE = F(FONT_K, int((140 if len(E) <= 9 else 110) * max(0.2, s)))
    center(d, 620, E, fE, WHITE, 12, DARK)
    d.ellipse([VW // 2 - 300, 760, VW // 2 + 300, 1360], fill=WHITE)
    sp = sps[i]
    if st.get("rev"):
        paste_c(im, big(sp, 470), VW // 2, 1060) if sp else None
        center(d, 1500, D["names"][k], F(FONT_K, 110), (255, 203, 5), 10, DARK)
    else:
        if sp: paste_c(im, silhouette(big(sp, 470), (40, 34, 70)), VW // 2, 1060)
        fr = st.get("frac", 1)
        d.rounded_rectangle([140, 1460, VW - 140, 1510], 25, fill=(60, 50, 100))
        d.rounded_rectangle([140, 1460, 140 + int((VW - 280) * fr), 1510], 25, fill=(227, 53, 13) if fr < 0.35 else (255, 203, 5))
    d.rectangle([0, VH - 210, VW, VH], fill=(20, 18, 40))
    center(d, VH - 140, "全ポケモンの英語名と由来は", F(FONT_B, 44), WHITE); center(d, VH - 80, "プロフィールのサイトで", F(FONT_B, 44), (255, 224, 102))
    return im


def speed5_video(q, sps, D):
    v0 = tts("英語名だけで、ポケモンを当てるのだ！", ZUNDA, 1.2)
    segs = [(lambda t: speed5_frame(q, sps, {"spin": t * 20}, D), dur(v0, 2.0))]
    for i in range(5):
        segs.append((lambda t, i=i: speed5_frame(q, sps, {"i": i, "t": t, "frac": 1 - t / 2.5, "spin": t * 20}, D), 2.5))
        segs.append((lambda t, i=i: speed5_frame(q, sps, {"i": i, "rev": 1, "t": 1, "spin": t * 20}, D), 1.1))
    v9 = tts("何問わかった？コメントで教えてほしいのだ！", ZUNDA, 1.15)
    segs.append((lambda t: speed5_frame(q, sps, {"spin": t * 20}, D), dur(v9, 2.2)))
    st, total = seq(segs); m = Mix(total, STYLE)
    m.music(0, total)
    for i in range(5):
        t0 = st[1 + 2 * i]; m.whoosh(t0)
        for s in (1.0, 1.5, 2.0): m.tick(t0 + s)
        m.ding(st[2 + 2 * i])
    m.voice(0.1, v0); m.voice(st[-1] + 0.1, v9)
    return segs, m, speed5_frame(q, sps, {"i": 0, "t": 1, "frac": 0.6}, D)


# =========================================================
# 4. この英語版図鑑、どのポケモン？（4択）
# =========================================================
def which_pick(D, n):
    ids = {k: int(D["stats"][k]["id"]) for k in D["en"] if k in D["stats"] and k in D["names"]}
    r = random.Random(n * 7 + 1)
    pool = sorted([k for k in ids if ids[k] <= 251], key=lambda k: ids[k]); random.Random(77).shuffle(pool)
    for j in range(len(pool)):
        key = pool[(n + j) % len(pool)]
        es = [s for s in re.split(r"(?<=[.!?])\s+", D["en"][key].replace("\n", " ")) if s]
        js = [s for s in re.split(r"(?<=[。！？])", D["jp"].get(key, "")) if s.strip()]
        E = ename(key)
        cand = [i for i, s in enumerate(es) if 40 <= len(s) <= 120]
        if not cand or len(js) != len(es): continue
        i = cand[0]
        sent = re.sub(r"(^|[.!?]\s+)" + re.escape(E), lambda m_: m_.group(1) + "This Pokémon", es[i])
        sent = re.sub(re.escape(E), "this Pokémon", sent, flags=re.I)
        if E.lower() in sent.lower(): continue
        others = r.sample([k for k in pool if k != key], 3)
        opts = [key] + others; r.shuffle(opts)
        return dict(key=key, sent=sent, ja=js[i], opts=opts)


def which_frame(q, sps, st, D):
    im = dots(grad((214, 245, 214), (150, 214, 160)), (30, 120, 70)); d = ImageDraw.Draw(im)
    header(d, "この図鑑、どのポケモン？", (30, 120, 70))
    f = F(FONT_B, 54); lines = ewrap(d, "“" + q["sent"] + "”", f, VW - 200)
    h = 70 * len(lines) + 60
    d.rounded_rectangle([70, 280, VW - 70, 280 + h], 36, fill=WHITE, outline=DARK, width=5)
    for k, ln in enumerate(lines): d.text((110, 320 + k * 70), ln, font=f, fill=DARK)
    y0 = 280 + h + 50
    if st.get("reveal") is not None:
        fj = F(FONT_B, 44); jl = jwrap2(d, q["ja"], fj, VW - 200)[:4]
        d.rounded_rectangle([70, y0 - 20, VW - 70, y0 + 60 * len(jl) + 10], 30, fill=(255, 250, 220))
        for k, ln in enumerate(jl): d.text((110, y0 + k * 60), ln, font=fj, fill=DARK)
        y0 += 60 * len(jl) + 50
    cw, ch = 440, 400
    for i, k in enumerate(q["opts"]):
        x = 90 + (i % 2) * (cw + 20); y = y0 + (i // 2) * (ch + 20)
        ok = k == q["key"]; rv = st.get("reveal") is not None
        fill = WHITE if not rv else ((214, 245, 214) if ok else (225, 225, 225))
        d.rounded_rectangle([x, y, x + cw, y + ch], 36, fill=fill, outline=(47, 168, 79) if rv and ok else DARK, width=10 if rv and ok else 5)
        sp = sps[i]
        if sp:
            s = big(sp, 250)
            if rv and not ok: s = ImageEnhance.Brightness(s).enhance(0.45)
            paste_c(im, s, x + cw // 2, y + 170)
        d.text((x + 40, y + 40), "ABCD"[i], font=F(FONT_K, 54), fill=(30, 120, 70), anchor="mm")
        d.text((x + cw // 2, y + ch - 55), D["names"][k], font=F(FONT_K, 52), fill=DARK, anchor="mm")
    if st.get("count"): timer(d, VW // 2, min(VH - 320, y0 + 2 * ch + 20 + 120), st["frac"], st["count"])
    footer(d, "英語版の図鑑と日本語訳は", "プロフィールのサイトで")
    return im


def which_video(q, sps, D):
    v1 = tts("この英語版の図鑑、どのポケモンのこと？", ZUNDA, 1.15)
    v2 = tts(f"正解は、{D['names'][q['key']]}なのだ！", ZUNDA, 1.12)
    segs = [(lambda t: which_frame(q, sps, {}, D), dur(v1, 2.6))]
    for c in (5, 4, 3, 2, 1): segs.append((lambda t, c=c: which_frame(q, sps, {"count": c, "frac": (c - t) / 5}, D), 1.0))
    segs.append((lambda t: which_frame(q, sps, {"reveal": t}, D), dur(v2, 4.5)))
    st, total = seq(segs); m = Mix(total, STYLE)
    m.music(0, total)
    for c in range(5): m.tick(st[1 + c])
    m.ding(st[6]); m.voice(0.1, v1); m.voice(st[6] + 0.25, v2)
    return segs, m, which_frame(q, sps, {"count": 5, "frac": 1}, D)


# =========================================================
# 5. 英語版図鑑の怖い一文ランキングTOP3
# =========================================================
def rank_pick(D, n):
    pool = [k for k in P.SCARY if k in D["en"] and k in D["names"]]
    s = (n * 3) % len(pool)
    return dict(keys=[pool[(s + i) % len(pool)] for i in range(3)])


def rank_frame(q, sps, st, D, items):
    im = Image.new("RGB", (VW, VH), (12, 10, 14)); d = ImageDraw.Draw(im)
    i = st.get("i")
    tf = F(FONT_M, 76)
    center(d, 150, "英語版の図鑑が怖い", tf, (235, 30, 40), 2, (0, 0, 0))
    center(d, 250, "ランキング TOP3", F(FONT_M, 64), (232, 226, 214))
    if i is None:
        center(d, 900, "3位から発表…", F(FONT_M, 96), (232, 226, 214))
        center(d, 1060, "1位は読まない方がいい", F(FONT_M, 64), (190, 10, 20))
        return im
    rank = 3 - i; k = q["keys"][i]; sent, ja = items[i]
    x = ease(st.get("t", 1) / 0.5)
    center(d, 430, f"第{rank}位", F(FONT_M, int(150 * (0.6 + 0.4 * x))), (190, 10, 20) if rank == 1 else (232, 226, 214), 3, (0, 0, 0))
    sp = sps[i]
    if sp:
        s = big(sp, 440); g = ImageEnhance.Color(s).enhance(0.15); g = ImageEnhance.Brightness(g).enhance(0.7)
        zoom = 1 + 0.06 * st.get("t", 0)
        paste_c(im, g, VW // 2 + int(math.sin(st.get("t", 0) * 30) * 4 * (rank == 1)), 820, zoom)
    center(d, 1090, D["names"][k], F(FONT_M, 64), (232, 226, 214))
    fe = F(FONT_B, 46); el = ewrap(d, sent, fe, VW - 180)[:4]
    for j, ln in enumerate(el): center(d, 1200 + j * 62, ln, fe, (232, 226, 214))
    if st.get("ja"):
        fj = F(FONT_M, 48); jl = jwrap2(d, ja, fj, VW - 180)[:4]
        y = 1220 + 62 * len(el)
        for j, ln in enumerate(jl): center(d, y + j * 66, ln, fj, (235, 60, 60))
    d.rectangle([0, VH - 170, VW, VH], fill=(30, 0, 4))
    center(d, VH - 85, "怖い図鑑のまとめはプロフィールのサイトで", F(FONT_B, 40), (232, 226, 214))
    a = np.array(im).astype(np.float32)
    yy, xx = np.ogrid[:VH, :VW]; r = np.sqrt(((xx - VW / 2) / (VW * 0.7)) ** 2 + ((yy - VH * 0.45) / (VH * 0.6)) ** 2)
    a *= np.clip(1.25 - r, 0.25, 1)[..., None]
    return Image.fromarray(a.astype(np.uint8))


def rank_video(q, sps, D):
    items = [P.scary_text(k, D["en"], D["jp"]) for k in q["keys"]]
    segs = [(lambda t: rank_frame(q, sps, {}, D, items), 1.8)]
    vs = []
    for i in range(3):
        v = tts(items[i][1], HIMARI, 0.85, -0.06, 0.6); vs.append(v)
        segs.append((lambda t, i=i: rank_frame(q, sps, {"i": i, "t": t}, D, items), 2.2))
        segs.append((lambda t, i=i: rank_frame(q, sps, {"i": i, "t": 2.2 + t, "ja": 1}, D, items), dur(v, 3.6)))
    st, total = seq(segs); m = Mix(total, STYLE)
    t = np.arange(m.n) / SR; r = random.Random(STYLE["seed"]); f0 = r.choice([41.2, 46.2, 49.0, 55.0, 61.7]); beat = r.uniform(0.8, 4.0)
    m.a += (0.08 * np.sin(2 * np.pi * f0 * t) + 0.05 * np.sin(2 * np.pi * (f0 + beat) * t) + 0.02 * np.sin(2 * np.pi * f0 * r.choice([5.04, 6.73, 7.12]) * t)
            * (0.5 + 0.5 * np.sin(2 * np.pi * r.uniform(0.1, 0.4) * t))).astype(np.float32)
    for i in range(3):
        m.boom(st[1 + 2 * i]) if i == 2 else m.buzz(st[1 + 2 * i])
        m.voice(st[2 + 2 * i] + 0.2, vs[i])
    return segs, m, rank_frame(q, sps, {"i": 2, "t": 1, "ja": 1}, D, items)


# =========================================================
FORMATS = ["plus", "real3", "speed5", "which", "rank"]
MOOD = {"plus": "quiz", "real3": "quiz", "speed5": "fast", "which": "calm", "rank": "calm"}
STYLE = music.style(0)


def make(fmt, n, D, out="short.mp4", seed=None):
    global STYLE
    STYLE = music.style(seed if seed is not None else n * 101 + FORMATS.index(fmt), MOOD[fmt])
    print("BGM:", music.label(STYLE))
    if fmt == "plus":
        pool = plus_pool(D); random.Random(9).shuffle(pool); q = pool[n % len(pool)]; q["jn"] = D["names"][q["key"]]
        segs, m, th = plus_video(q, P.sprite(q["key"]))
    elif fmt == "real3":
        q = real3_pick(D, n); q["jn"] = D["names"][q["key"]]; segs, m, th = real3_video(q, P.sprite(q["key"]), D)
    elif fmt == "speed5":
        q = speed5_pick(D, n); segs, m, th = speed5_video(q, [P.sprite(k) for k in q["keys"]], D)
    elif fmt == "which":
        q = which_pick(D, n); segs, m, th = which_video(q, [P.sprite(k) for k in q["opts"]], D)
    else:
        q = rank_pick(D, n); segs, m, th = rank_video(q, [P.sprite(k) for k in q["keys"]], D)
    render(segs, m, out); th.save("thumb.png")
    return q


def meta(fmt, q, D):
    S = P.SITE
    if fmt == "plus":
        return (f"{q['w1']}＋{q['w2']}＝？このポケモンだーれだ【英語名の足し算クイズ】 #shorts",
                f"正解は{q['jn']}（{q['en']}）！\n{q['w1']}（{q['m1']}）＋{q['w2']}（{q['m2']}）\n\n{q['jn']}の英語版図鑑 → {S}/p/{q['key']}.html\n英語名がダジャレなポケモン → {S}/p/pun.html\n\n#ポケモン #英語名 #クイズ")
    if fmt == "real3":
        return (f"{q['jn']}の本物の英語名はどれ？【3択クイズ】 #shorts",
                f"正解は{ename(q['key'])}！\nほかの選択肢は " + "、".join(f"{ename(k)}＝{D['names'][k]}" for k in q["opts"] if k != q["key"]) +
                f"\n\n{q['jn']}の英語版図鑑 → {S}/p/{q['key']}.html\n全ポケモンの英語名一覧 → {S}/p/\n\n#ポケモン #英語名 #クイズ")
    if fmt == "speed5":
        return (f"英語名だけでポケモン当てられる？5連発【{q['level']}】 #shorts",
                "出てきたポケモン：" + "、".join(f"{ename(k)}＝{D['names'][k]}" for k in q["keys"]) +
                f"\n何問わかったかコメントで教えてね！\n\n全ポケモンの英語名一覧 → {S}/p/\n\n#ポケモン #英語名 #クイズ")
    if fmt == "which":
        return (f"この英語版図鑑、どのポケモン？【4択】 #shorts",
                f"“{q['sent']}”\n→ {q['ja']}\n正解は{D['names'][q['key']]}！\n\n英語版図鑑と日本語訳 → {S}/p/{q['key']}.html\n図鑑で覚える英単語 → {S}/p/words.html\n\n#ポケモン #ポケモン図鑑 #英語")
    return (f"英語版のポケモン図鑑、怖い一文ランキングTOP3 #shorts",
            "3位〜1位：" + "、".join(D["names"][k] for k in q["keys"]) + f"\n\n英語版の図鑑が怖いポケモンまとめ → {S}/p/scary.html\n\n#ポケモン #ポケモン図鑑 #ホラー")


def load():
    g = P.get_json
    return dict(en=g("pokedex_en.json"), jp=g("pokedex_jp.json"), names=g("pokemon_names_jp.json"), stats=g("pokedex_stats.json"), origins=g("name_origins.json"))


if __name__ == "__main__":
    D = load(); fmt = os.environ.get("FORMAT", "plus"); n = int(os.environ.get("N", "0"))
    q = make(fmt, n, D, os.environ.get("OUT", "short.mp4"))
    t, desc = meta(fmt, q, D); print(t); print(desc)
