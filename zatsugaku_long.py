# ずんだもんと冥鳴ひまりの「ポケモン雑学」週末まとめ（横動画 1920x1080・週1回）
#   ・開発の裏話を6つ、掛け合いで紹介する数分の動画
#   ・ショートと同じネタ帳（backstories）を、ショートとは逆の順番で使う
import os, re, sys, json, random, datetime, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import post as P
import zatsugaku as Z

W, H, FPS, SR = 1920, 1080, 24, P.SR
F, FONT_B, FONT_K = P.F, P.FONT_B, P.FONT_K
CHAR = Z.CHAR
START = datetime.date(2026, 11, 15)    # 最初の日曜
N_TOPICS = 6


def bg():
    im = Image.new("RGB", (W, H), (250, 247, 240)); d = ImageDraw.Draw(im)
    for y in range(0, H, 56):
        for x in range(0 if (y // 56) % 2 else 28, W, 56): d.ellipse([x, y, x + 7, y + 7], fill=(236, 230, 218))
    return im


BG = bg()
_T = {}


def tachie(name, h, dim):
    k = (name, h, dim)
    if k not in _T:
        im = Image.open(os.path.join(Z.HERE, "chara", name + ".png")).convert("RGBA")
        im = im.crop((0, 0, im.width, int(im.height * (0.62 if name == "zundamon" else 0.56))))
        im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
        if dim:
            px = np.array(im).astype(np.float32); px[..., :3] *= 0.62; im = Image.fromarray(px.astype(np.uint8))
        _T[k] = im
    return _T[k]


def header(d, sub):
    d.rectangle([0, 0, W, 96], fill=(124, 78, 178)); d.rectangle([0, 96, W, 106], fill=(96, 176, 56))
    d.text((40, 48), "ずんだもんと冥鳴ひまりの ポケモン雑学", font=F(FONT_K, 46), fill=(255, 255, 255), anchor="lm")
    if sub: d.text((W - 40, 48), sub, font=F(FONT_K, 44), fill=(255, 236, 120), anchor="rm")


def frame(item, who, text, t):
    """item: 話題（None ならオープニング・エンディング）"""
    im = BG.copy(); d = ImageDraw.Draw(im)
    header(d, item and f"その{item['no']}　{item['jn']}")
    if item and item.get("sp"):
        s = P.big(item["sp"], 430); cx, cy = W // 2, 430
        z = 1 + 0.03 * np.sin(t * 2.2)
        s2 = s.resize((int(s.width * z), int(s.height * z)), Image.NEAREST)
        d.ellipse([cx - 290, cy - 290, cx + 290, cy + 290], fill=(255, 255, 255), outline=(230, 222, 240), width=10)
        im.paste(s2, (cx - s2.width // 2, cy - s2.height // 2), s2)
        d.text((cx - 330, 190), item["jn"], font=F(FONT_K, 64), fill=(40, 34, 50), anchor="rm", stroke_width=6, stroke_fill=(255, 255, 255))
        d.text((cx - 330, 260), P.ename(item["key"]), font=F(FONT_B, 42), fill=(124, 78, 178), anchor="rm")
    elif not item:
        d.text((W // 2, 330), "ポケモンの", font=F(FONT_K, 90), fill=(40, 34, 50), anchor="mm")
        d.text((W // 2, 470), "意外な裏話", font=F(FONT_K, 150), fill=(124, 78, 178), anchor="mm", stroke_width=10, stroke_fill=(255, 255, 255))
    # 立ち絵（話している方を手前・明るく・弾ませる）
    for c in ([("h" if who == "z" else "z")] + [who]):
        act = c == who
        name = "zundamon" if c == "z" else ("himari" if act else "himari_jito")
        img = tachie(name, 820 if act else 780, not act)
        bob = int(abs(np.sin(t * 8)) * 12) if act else 0
        x = -10 if c == "z" else W - img.width + 10
        im.paste(img, (x, H - img.height + 60 - bob), img)
    d = ImageDraw.Draw(im)
    # 字幕
    c = CHAR[who]; f = F(FONT_K, 54)
    lines = P.jwrap(d, text, f, 1180)[:2]
    h = 60 + 74 * len(lines); top = H - 40 - h
    d.rounded_rectangle([340, top, W - 340, top + h], 30, fill=(255, 255, 255), outline=c["col"], width=9)
    d.rounded_rectangle([370, top - 28, 370 + 40 + 40 * len(c["name"]), top + 24], 24, fill=c["col"])
    d.text((390, top - 2), c["name"], font=F(FONT_B, 36), fill=(255, 255, 255), anchor="lm")
    for i, ln in enumerate(lines): d.text((W // 2, top + 62 + 74 * i), ln, font=f, fill=(40, 34, 50), anchor="mm")
    return im


def card(no, jn):
    """話題の切り替え画面"""
    im = Image.new("RGB", (W, H), (124, 78, 178)); d = ImageDraw.Draw(im)
    d.polygon([(0, 0), (W * 0.55, 0), (W * 0.45, H), (0, H)], fill=(96, 176, 56))
    d.text((W // 2, H // 2 - 80), f"その{no}", font=F(FONT_K, 120), fill=(255, 236, 120), anchor="mm", stroke_width=12, stroke_fill=(40, 30, 60))
    d.text((W // 2, H // 2 + 90), jn, font=F(FONT_K, 110), fill=(255, 255, 255), anchor="mm", stroke_width=12, stroke_fill=(40, 30, 60))
    return im


def make_items(week, d):
    rnd = random.Random(20261114)
    back = sorted(k for k in d["back"] if k in d["names"]); rnd.shuffle(back)
    back = back[::-1]                                  # ショートとは逆の順で使う
    keys = [back[(week * N_TOPICS + i) % len(back)] for i in range(N_TOPICS)]
    items = []
    for i, k in enumerate(keys, 1):
        random.seed(week * 100 + i)
        q = Z.topic_backstory(k, d)
        lines = q["lines"][:-3]                        # 各話題ごとのサイト案内は省く（最後にまとめて言う）
        lines[0] = ("z", random.choice([f"次は{d['names'][k]}なのだ！", f"{d['names'][k]}の話を聞きたいのだ！", f"{d['names'][k]}にも何かあるのだ？"]))
        if i == 1: lines[0] = ("z", f"まずは{d['names'][k]}なのだ！")
        items.append(dict(no=i, key=k, jn=d["names"][k], lines=lines, src=q.get("src", "")))
    return items


def build(items, out):
    os.makedirs("_w", exist_ok=True)
    segs, voices, t0 = [], [], 0.0

    def add_line(item, who, text, say=None):
        nonlocal t0
        c = CHAR[who]
        v = P.tts(say or P.voice_text(text) or text, c["sp"], c["speed"])
        dur = (len(v) / SR + 0.35) if v is not None else max(1.8, len(text) * 0.14)
        segs.append((lambda t, item=item, who=who, text=text: frame(item, who, text, t), dur))
        voices.append((t0 + 0.1, v)); t0 += dur
        return v is not None

    voiced = False
    voiced |= add_line(None, "z", f"今日は、ポケモンの意外な裏話を{len(items)}つ紹介するのだ！")
    voiced |= add_line(None, "h", "開発の人たちしか知らないような話もあるよ。最後まで見ていってね。")
    chapters = [(0.0, "オープニング")]
    for it in items:
        chapters.append((t0, f"その{it['no']} {it['jn']}"))
        it["sp"] = P.sprite(it["key"])
        im = card(it["no"], it["jn"])
        segs.append((lambda t, im=im: im, 1.6)); t0 += 1.6
        for line in it["lines"]:
            voiced |= add_line(it, line[0], line[1], line[2] if len(line) > 2 else None)
    chapters.append((t0, "エンディング"))
    voiced |= add_line(None, "h", "今日の裏話はここまで。英語版の図鑑と和訳は、概要欄のサイトで読めるよ。")
    voiced |= add_line(None, "z", "チャンネル登録もよろしくなのだ！またね！")
    total = sum(round(d * FPS) / FPS for _, d in segs)
    # 映像（動きは小さいので 1秒8コマで作って 24fps に引き延ばす）
    parts = []
    for k, (fn, dur) in enumerate(segs):
        nfr = max(1, int(round(dur * FPS))); step = 3
        for i in range(0, nfr, step): fn(i / FPS).save(f"_w/s{k}_{i // step:04d}.jpg", quality=92)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS / step), "-i", f"_w/s{k}_%04d.jpg", "-t", f"{nfr / FPS:.3f}",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-r", str(FPS), f"_w/s{k}.mp4"], check=True)
        parts.append(f"_w/s{k}.mp4")
    open("_wlist.txt", "w").write("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "_wlist.txt", "-c", "copy", "_wv.mp4"], check=True)
    mix = Z.bgm(total) * 0.7
    for t, v in voices:
        if v is None: continue
        a = int(t * SR); b = min(len(mix), a + len(v)); mix[a:b] = mix[a:b] * 0.5 + v[:b - a]
    mix = np.clip(mix, -1, 1)
    with wave.open("_wa.wav", "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 30000).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "_wv.mp4", "-i", "_wa.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", out], check=True)
    # サムネイル
    th = card("", "")
    d = ImageDraw.Draw(th)
    th = Image.new("RGB", (W, H), (124, 78, 178)); d = ImageDraw.Draw(th)
    d.polygon([(0, 0), (W * 0.55, 0), (W * 0.45, H), (0, H)], fill=(96, 176, 56))
    for i, it in enumerate(items[:3]):
        if it.get("sp"):
            s = P.big(it["sp"], 300); th.paste(s, (560 + i * 300 - s.width // 2 + 120, 560 - s.height // 2), s)
    d.text((W // 2, 180), "ポケモンの意外な裏話", font=F(FONT_K, 130), fill=(255, 255, 255), anchor="mm", stroke_width=14, stroke_fill=(40, 30, 60))
    d.text((W // 2, 900), f"{len(items)}選", font=F(FONT_K, 170), fill=(255, 236, 120), anchor="mm", stroke_width=16, stroke_fill=(40, 30, 60))
    z = tachie("zundamon", 700, False); h = tachie("himari", 680, False)
    th.paste(z, (-40, H - z.height + 80), z); th.paste(h, (W - h.width + 40, H - h.height + 80), h)
    th.save("thumb_long.jpg", quality=92)
    return voiced, total, chapters


def meta(items, week, voiced, total, chapters):
    names = "・".join(it["jn"] for it in items)
    title = f"【ポケモン雑学】知ってた？ポケモンの意外な裏話{len(items)}選 #{week + 1}【ずんだもん・冥鳴ひまり】"
    # チャプター
    lines = ["今回のポケモン：" + names, ""]
    lines += [f"{int(t // 60)}:{int(t % 60):02d} {name}" for t, name in chapters]
    desc = "\n".join(lines)
    srcs = "\n".join(f"・{it['jn']} {it['src']}" for it in items if it.get("src"))
    credit = ("\n\n音声 VOICEVOX:ずんだもん、VOICEVOX:冥鳴ひまり" if voiced else "") + \
        "\n立ち絵 東北ずん子・ずんだもんプロジェクト、冥鳴ひまり公式（イラスト Sameta様）"
    desc += f"\n\n英語版のポケモン図鑑と日本語訳 → {P.SITE}/\n\n参考\n{srcs}{credit}\n\n#ポケモン #ポケモン雑学 #ずんだもん #冥鳴ひまり"
    return title[:100], desc


if __name__ == "__main__":
    d = dict(names=P.get_json("pokemon_names_jp.json"), stats=P.get_json("pokedex_stats.json"),
             origins=P.get_json("name_origins.json"), back=P.get_json("backstories.json"))
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(hours=9)
    week = int(os.environ["WEEK"]) if os.environ.get("WEEK") else max(0, (now.date() - START).days // 7)
    items = make_items(week, d)
    print(json.dumps([(it["jn"], len(it["lines"])) for it in items], ensure_ascii=False))
    voiced, total, chapters = build(items, "zatsugaku_long.mp4")
    title, desc = meta(items, week, voiced, total, chapters); print(title); print(desc); print("長さ", round(total), "秒")
    if os.environ.get("DRY_RUN") == "1": sys.exit()
    Z.upload(title, desc, "zatsugaku_long.mp4")
