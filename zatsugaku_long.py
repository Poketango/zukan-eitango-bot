# ずんだもんと冥鳴ひまりの「ポケモン雑学」週末まとめ（横動画 1920x1080・毎週日曜）
#   ・台本は scripts/long/NNNN.json（裏どりした雑学を人が書く／Claude が毎週書き足す）
#       NNNN は 2026-11-15 からの週番号。台本が無い週は、ネタ帳から自動で作る
#   ・画像は assets/img/ に置く（art_25.png＝公式イラスト、rb_＝赤緑、gold_＝金銀、frlg_＝ファイアレッドのドット絵）
#   ・台本の各せりふに "img": ["art:25|説明", ...] を付けると、その画像を出す（次に指定があるまで出し続ける）
import os, re, sys, json, random, datetime, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import post as P
import zatsugaku as Z

W, H, FPS, SR = 1920, 1080, 24, P.SR
F, FONT_B, FONT_K = P.F, P.FONT_B, P.FONT_K
CHAR = Z.CHAR
HERE = Z.HERE
START = datetime.date(2026, 11, 15)    # 最初の日曜
N_TOPICS = 6
PIXEL_KINDS = ("rb", "gold", "frlg")


def say_fix(s):
    """読み上げで記号やアルファベットが飛ばないようにする"""
    s = s.replace("「！」", "びっくりマーク").replace("「？」", "はてなマーク")
    s = re.sub(r"『([^』]*)』", r"\1", s)
    return s


def bg():
    im = Image.new("RGB", (W, H), (250, 247, 240)); d = ImageDraw.Draw(im)
    for y in range(0, H, 56):
        for x in range(0 if (y // 56) % 2 else 28, W, 56): d.ellipse([x, y, x + 7, y + 7], fill=(236, 230, 218))
    return im


BG = bg()
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


def panel(im, refs, t):
    """画面中央の白いボードに画像を並べる（説明付き）"""
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = 400, 130, W - 400, 735
    d.rounded_rectangle([x0, y0, x1, y1], 36, fill=(255, 255, 255), outline=(230, 222, 240), width=8)
    if refs == ["unown"]:
        keys = [f"frlg:201-{c}" for c in "abcdefghijklmnopqrstuvwxyz"] + ["frlg:201-exclamation", "frlg:201-question"]
        cols, rows = 7, 4
        cw, ch = (x1 - x0 - 60) / cols, (y1 - y0 - 50) / rows
        for i, k in enumerate(keys):
            s = load_img(k)
            if s is None: continue
            s = fit(s, cw - 14, ch - 14, True)
            cx = x0 + 30 + cw * (i % cols) + cw / 2; cy = y0 + 25 + ch * (i // cols) + ch / 2
            cy += np.sin(t * 3 + i) * 4
            im.paste(s, (int(cx - s.width / 2), int(cy - s.height / 2)), s)
        return
    n = len(refs); gap = 30
    cw = (x1 - x0 - 60 - gap * (n - 1)) / n
    for i, r in enumerate(refs):
        ref, _, cap = r.partition("|")
        s = load_img(ref)
        if s is None: continue
        pix = ref.split(":")[0] in PIXEL_KINDS
        ih = (y1 - y0 - 60) - (60 if cap else 0)
        s = fit(s, cw, ih, pix)
        z = 1 + 0.02 * np.sin(t * 2 + i)
        if not pix and z != 1: s = s.resize((int(s.width * z), int(s.height * z)), Image.LANCZOS)
        cx = x0 + 30 + (cw + gap) * i + cw / 2; cy = y0 + 30 + ih / 2
        im.paste(s, (int(cx - s.width / 2), int(cy - s.height / 2)), s)
        if cap:
            d.rounded_rectangle([cx - cw / 2 + 10, y1 - 78, cx + cw / 2 - 10, y1 - 22], 24, fill=(124, 78, 178))
            d.text((cx, y1 - 50), cap, font=F(FONT_K, 34), fill=(255, 255, 255), anchor="mm")


def header(d, sub):
    d.rectangle([0, 0, W, 96], fill=(124, 78, 178)); d.rectangle([0, 96, W, 106], fill=(96, 176, 56))
    d.text((40, 48), "ずんだもんと冥鳴ひまりの ポケモン雑学", font=F(FONT_K, 44), fill=(255, 255, 255), anchor="lm")
    if sub: d.text((W - 40, 48), sub, font=F(FONT_K, 42), fill=(255, 236, 120), anchor="rm")


def frame(sub, refs, who, text, t, big_title=None):
    im = BG.copy(); d = ImageDraw.Draw(im)
    header(d, sub)
    if refs: panel(im, refs, t)
    elif big_title:
        d.text((W // 2, 330), big_title[0], font=F(FONT_K, 90), fill=(40, 34, 50), anchor="mm")
        d.text((W // 2, 480), big_title[1], font=F(FONT_K, 140), fill=(124, 78, 178), anchor="mm", stroke_width=10, stroke_fill=(255, 255, 255))
    for c in ([("h" if who == "z" else "z")] + [who]):
        act = c == who
        name = "zundamon" if c == "z" else ("himari" if act else "himari_jito")
        img = tachie(name, 820 if act else 780, not act)
        bob = int(abs(np.sin(t * 8)) * 12) if act else 0
        x = -40 if c == "z" else W - img.width + 40
        im.paste(img, (x, H - img.height + 60 - bob), img)
    d = ImageDraw.Draw(im)
    c = CHAR[who]
    for size in (52, 46, 40):                       # 長いせりふは文字を小さくして、全部表示する
        f = F(FONT_K, size); lines = P.jwrap(d, text, f, 1180)
        if len(lines) <= 3: break
    lh = int(size * 1.35)
    h = 56 + lh * len(lines); top = H - 30 - h
    d.rounded_rectangle([340, top, W - 340, top + h], 30, fill=(255, 255, 255), outline=c["col"], width=9)
    d.rounded_rectangle([370, top - 28, 370 + 40 + 40 * len(c["name"]), top + 24], 24, fill=c["col"])
    d.text((390, top - 2), c["name"], font=F(FONT_B, 36), fill=(255, 255, 255), anchor="lm")
    for i, ln in enumerate(lines): d.text((W // 2, top + 28 + lh // 2 + lh * i), ln, font=f, fill=(40, 34, 50), anchor="mm")
    return im


def card(no, label, ref):
    im = Image.new("RGB", (W, H), (124, 78, 178)); d = ImageDraw.Draw(im)
    d.polygon([(0, 0), (W * 0.55, 0), (W * 0.45, H), (0, H)], fill=(96, 176, 56))
    s = load_img(ref) if ref else None
    if s is not None:
        s = fit(s, 520, 520, ref.split(":")[0] in PIXEL_KINDS)
        sh = s.split()[3].filter(ImageFilter.GaussianBlur(10))
        shadow = Image.new("RGBA", s.size, (0, 0, 0, 0)); shadow.putalpha(sh.point(lambda v: int(v * 0.35)))
        im.paste(shadow, (W // 2 - s.width // 2 + 10, 470 - s.height // 2 + 12), shadow)
        im.paste(s, (W // 2 - s.width // 2, 470 - s.height // 2), s)
    d.text((W // 2, 120), f"その{no}", font=F(FONT_K, 110), fill=(255, 236, 120), anchor="mm", stroke_width=12, stroke_fill=(40, 30, 60))
    d.text((W // 2, 900), label, font=F(FONT_K, 96), fill=(255, 255, 255), anchor="mm", stroke_width=12, stroke_fill=(40, 30, 60))
    return im


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
    segs, voices = [], []
    state = dict(t=0.0, voiced=False)

    def add_line(sub, refs, ln, big_title=None):
        c = CHAR[ln["w"]]
        say = say_fix(ln.get("say") or P.voice_text(say_fix(ln["t"])) or ln["t"])
        v = P.tts(say, c["sp"], c["speed"])
        if v is not None: state["voiced"] = True
        dur = (len(v) / SR + 0.35) if v is not None else max(1.8, len(say) * 0.17 + 0.35)
        segs.append((lambda t, sub=sub, refs=refs, ln=ln: frame(sub, refs, ln["w"], ln["t"], t, big_title), dur))
        voices.append((state["t"] + 0.1, v)); state["t"] += dur

    chapters = [(0.0, "オープニング")]
    bt = ("ポケモンの", "意外な裏話")
    for ln in sc["opening"]: add_line(None, ln.get("img"), ln, bt)
    for no, tp in enumerate(sc["topics"], 1):
        chapters.append((state["t"], f"その{no} {tp['label']}"))
        first_img = next((r.split("|")[0] for ln in tp["lines"] for r in ln.get("img", []) if r != "unown"), None)
        im = card(no, tp["label"], first_img)
        segs.append((lambda t, im=im: im, 2.0)); state["t"] += 2.0
        refs = None
        for ln in tp["lines"]:
            refs = ln.get("img", refs)
            add_line(f"その{no}　{tp['jn']}", refs, ln)
    chapters.append((state["t"], "エンディング"))
    for ln in sc["ending"]: add_line(None, ln.get("img"), ln, bt)
    total = sum(round(dd * FPS) / FPS for _, dd in segs)
    parts = []
    for k, (fn, dur) in enumerate(segs):
        nfr = max(1, int(round(dur * FPS))); step = 3
        for i in range(0, nfr, step): fn(i / FPS).save(f"_w/s{k}_{i // step:04d}.jpg", quality=90)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS / step), "-i", f"_w/s{k}_%04d.jpg", "-t", f"{nfr / FPS:.3f}",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-r", str(FPS), f"_w/s{k}.mp4"], check=True)
        for i in range(0, nfr, step): os.remove(f"_w/s{k}_{i // step:04d}.jpg")
        parts.append(f"_w/s{k}.mp4")
    open("_wlist.txt", "w").write("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "_wlist.txt", "-c", "copy", "_wv.mp4"], check=True)
    mix = Z.bgm(total) * 0.6
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


def thumb(sc):
    th = Image.new("RGB", (W, H), (124, 78, 178)); d = ImageDraw.Draw(th)
    d.polygon([(0, 0), (W * 0.55, 0), (W * 0.45, H), (0, H)], fill=(96, 176, 56))
    tb = sc.get("thumb") or {}
    refs = tb.get("imgs") or [next((r.split("|")[0] for ln in tp["lines"] for r in ln.get("img", []) if r != "unown"), None) for tp in sc["topics"][:3]]
    refs = [r for r in refs if r][:3]
    for i, r in enumerate(refs):
        s = load_img(r)
        if s is None: continue
        s = fit(s, 420, 420, r.split(":")[0] in PIXEL_KINDS)
        cx = W // 2 + (i - (len(refs) - 1) / 2) * 400
        th.paste(s, (int(cx - s.width / 2), 560 - s.height // 2), s)
    d.text((W // 2, 170), tb.get("text1", "ポケモンの意外な裏話"), font=F(FONT_K, 130), fill=(255, 255, 255), anchor="mm", stroke_width=14, stroke_fill=(40, 30, 60))
    d.text((W // 2, 920), tb.get("text2", f"{len(sc['topics'])}選"), font=F(FONT_K, 150), fill=(255, 236, 120), anchor="mm", stroke_width=16, stroke_fill=(40, 30, 60))
    z = tachie("zundamon", 700, False); h = tachie("himari", 680, False)
    th.paste(z, (-60, H - z.height + 90), z); th.paste(h, (W - h.width + 60, H - h.height + 90), h)
    return th


def meta(sc, voiced, chapters):
    names = "・".join(tp["jn"] for tp in sc["topics"])
    lines = ["ずんだもんと冥鳴ひまりが、ポケモンの意外な雑学をくわしく紹介します。", "今回のポケモン：" + names, ""]
    lines += [f"{int(t // 60)}:{int(t % 60):02d} {name}" for t, name in chapters]
    srcs = "\n".join(f"・{tp['jn']}　" + "／".join(s for s in tp.get("sources", []) if s) for tp in sc["topics"])
    credit = ("\n\n音声 VOICEVOX:ずんだもん、VOICEVOX:冥鳴ひまり" if voiced else "") + \
        "\n立ち絵 東北ずん子・ずんだもんプロジェクト、冥鳴ひまり公式（イラスト Sameta様）"
    desc = "\n".join(lines) + f"\n\n英語版のポケモン図鑑と日本語訳 → {P.SITE}/\n\n参考にした資料\n{srcs}{credit}\n\n" \
        "※ファンが運営する非公式のチャンネルです。\n#ポケモン #ポケモン雑学 #ずんだもん #冥鳴ひまり"
    return sc["title"][:100], desc[:4900]


if __name__ == "__main__":
    d = dict(names=P.get_json("pokemon_names_jp.json"), stats=P.get_json("pokedex_stats.json"),
             origins=P.get_json("name_origins.json"), back=P.get_json("backstories.json"))
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(hours=9)
    week = int(os.environ["WEEK"]) if os.environ.get("WEEK") else max(0, (now.date() - START).days // 7)
    sc = script_for(week, d)
    voiced, total, chapters = build(sc, "zatsugaku_long.mp4")
    title, desc = meta(sc, voiced, chapters); print(title); print(desc); print("長さ", round(total), "秒")
    if os.environ.get("DRY_RUN") == "1": sys.exit()
    os.environ["THUMB"] = "thumb_long.jpg"
    Z.upload(title, desc, "zatsugaku_long.mp4")
