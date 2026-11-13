# ずんだもんと冥鳴ひまりの「ポケモン雑学」ショート（別チャンネル用・GitHub Actions で1日2回）
#   ・ネタはサイトのデータから作る：開発の裏話（backstories）、英語名の由来（name_origins）、種族値の珍記録（pokedex_stats）
#   ・ずんだもん（聞き役）と冥鳴ひまり（解説役）の掛け合いを VOICEVOX で読み上げる
#   ・アップロード先は YT2_* の鍵のチャンネル（未設定なら動画を作るだけ）
import os, re, sys, json, random, datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import post as P

SITE = P.SITE
START = datetime.date(2026, 11, 14)
SLOTS = 2
ZUNDA, HIMARI = P.ZUNDA, P.HIMARI
VW, VH, FPS, SR = P.VW, P.VH, P.FPS, P.SR
F, FONT_B, FONT_K = P.F, P.FONT_B, P.FONT_K

CHAR = {
    "z": dict(name="ずんだもん", sp=ZUNDA, col=(96, 176, 56), soft=(226, 245, 214), speed=1.12),
    "h": dict(name="冥鳴ひまり", sp=HIMARI, col=(124, 78, 178), soft=(236, 226, 248), speed=1.05),
}
STAT_JA = {"hp": "HP", "attack": "こうげき", "defense": "ぼうぎょ", "special-attack": "とくこう", "special-defense": "とくぼう", "speed": "すばやさ"}


# ---------- ネタ作り ----------
def split_ja(t, n=44):
    """長い説明を、字幕1枚（3行まで）に収まる長さに分ける。読点、なければ助詞のあとで区切る"""
    out = []
    for s in re.split(r"(?<=[。！？])", t):
        s = s.strip()
        if not s: continue
        while len(s) > n:
            k = s.rfind("、", 0, n)
            if k < 12:
                k = max(s.rfind(ch, 12, n) for ch in "はがをにでともへ")
            k = k + 1 if k >= 12 else n
            out.append(s[:k]); s = s[k:]
        if s: out.append(s)
    return out


def talk(s):
    """図鑑の書き言葉（〜である・〜している）を、ひまりの話し言葉にする"""
    rules = [(r"のだ。$", "んだって。"), (r"だという。$", "なんだって。"), (r"という。$", "んだって。"), (r"である。$", "なんだって。"), (r"だ。$", "なんだって。"), (r"(もの|こと|ため)。$", r"\1なんだって。"),
             (r"([るたい])。$", r"\1んだって。")]
    for a, b in rules:
        t = re.sub(a, b, s)
        if t != s: return t
    return s


def topic_backstory(key, d):
    t = d["back"][key]["t"]
    jn = d["names"][key]
    lines = [("z", f"{jn}のひみつを教えてほしいのだ！"), ("h", f"いいよ。{jn}には、こんな裏話があるの。")]
    lines += [("h", talk(s)) for s in split_ja(t)]
    lines += [("z", random.choice(["えっ、そうだったのだ！？", "知らなかったのだ…！", "それはびっくりなのだ！", "ちょっと見る目が変わったのだ。"]))]
    lines += [("h", f"ちなみに英語の名前は、{P.ename(key)}。", "ちなみに英語の名前は、画面に出ている、この名前。"), ("z", "英語版の図鑑も読んでみたいのだ！"),
              ("h", "英語版の図鑑と和訳は、プロフィールのサイトで読めるよ。")]
    return dict(kind="backstory", key=key, title=f"{jn}の意外な裏話【ポケモン雑学】", lines=lines, src=d["back"][key].get("src", ""))


def topic_origin(key, d):
    jn, E = d["names"][key], P.ename(key)
    o = P.short_origin(d["origins"][key]["t"])
    lines = [("z", f"{jn}って、英語だと何て名前なのだ？"), ("h", f"{E}っていうの。", "画面に出ている、この名前なの。"),
             ("z", "どういう意味なのだ？"), ("h", f"{P.voice_text(o)}、から来ていると考えられているよ。" if P.voice_text(o) else f"由来は、{o}。"),
             ("z", random.choice(["なるほど、ぴったりなのだ！", "英語名もよくできてるのだ！", "名前に特徴が詰まってるのだ。"])),
             ("h", "ほかのポケモンの英語名の由来も、プロフィールのサイトにまとめてあるよ。")]
    return dict(kind="origin", key=key, title=f"{jn}の英語名「{E}」の意味、知ってる？【ポケモン雑学】", lines=lines, origin=o,
                src=d["origins"][key].get("src", ""))


def stat_facts(d):
    """種族値の珍記録（全1025匹中で何番目か）"""
    st = d["stats"]; keys = [k for k in st if k in d["names"]]
    facts = []
    for s in STAT_JA:
        order = sorted(keys, key=lambda k: -st[k][s])
        for r, k in enumerate(order[:5], 1): facts.append((k, s, "high", r, st[k][s]))
        low = sorted(keys, key=lambda k: st[k][s])
        for r, k in enumerate(low[:3], 1): facts.append((k, s, "low", r, st[k][s]))
    return facts


def topic_stat(fact, d):
    k, s, hl, r, v = fact
    jn, sj = d["names"][k], STAT_JA[s]
    n = len(d["stats"])
    rank = f"{n}匹の中で{'いちばん' if r == 1 else str(r) + '番目に'}{'高い' if hl == 'high' else '低い'}"
    lines = [("z", f"{jn}の{sj}って、どれくらいなのだ？"), ("h", f"{sj}は{v}。"), ("h", f"実はこれ、全ポケモン{rank}の。"),
             ("z", random.choice(["そんなにすごかったのだ！？", "意外すぎるのだ！", "もっと大事にするのだ…！"])),
             ("h", f"英語の名前は{P.ename(k)}。英語版の図鑑も、プロフィールのサイトで読めるよ。", "英語版の図鑑も、プロフィールのサイトで読めるよ。")]
    title = f"{jn}の{sj}、全ポケモンで{'1位' if r == 1 else str(r) + '位'}{'' if hl == 'high' else '（低い方から）'}【ポケモン雑学】"
    return dict(kind="stat", key=k, title=title, lines=lines, stat=(sj, v, rank))


def pick(n, d):
    rnd = random.Random(20261114)
    back = sorted(k for k in d["back"] if k in d["names"]); rnd.shuffle(back)
    orig = sorted(k for k in d["origins"] if k in d["names"] and int(d["stats"].get(k, {"id": "9999"})["id"]) <= 721
                  and ("組み合わせ" in d["origins"][k]["t"] or "もじ" in d["origins"][k]["t"])); rnd.shuffle(orig)
    facts = stat_facts(d); rnd.shuffle(facts)
    random.seed(n)
    kind = ["backstory", "origin", "backstory", "stat"][n % 4]
    if kind == "backstory": return topic_backstory(back[(n // 2) % len(back)], d)
    if kind == "origin": return topic_origin(orig[(n // 4) % len(orig)], d)
    return topic_stat(facts[(n // 4) % len(facts)], d)


# ---------- 画面 ----------
def bg():
    im = Image.new("RGB", (VW, VH), (250, 247, 240)); d = ImageDraw.Draw(im)
    for y in range(0, VH, 60):
        for x in range(0 if (y // 60) % 2 else 30, VW, 60): d.ellipse([x, y, x + 8, y + 8], fill=(236, 230, 218))
    return im


BG = None


HERE = os.path.dirname(os.path.abspath(__file__))
_TACHIE = {}


def tachie(name, h):
    """立ち絵の上半身（頭から腰まで）を高さ h にして返す"""
    k = (name, h)
    if k not in _TACHIE:
        im = Image.open(os.path.join(HERE, "chara", name + ".png")).convert("RGBA")
        im = im.crop((0, 0, im.width, int(im.height * (0.56 if name == "zundamon" else 0.5))))
        im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
        dim = im.copy(); px = np.array(dim).astype(np.float32); px[..., :3] *= 0.62; dim = Image.fromarray(px.astype(np.uint8))
        _TACHIE[k] = (im, dim)
    return _TACHIE[k]


def put_tachie(im, who, active, t):
    """話している方は明るく、少し大きく弾む。聞いている方は少し暗く"""
    name = "zundamon" if who == "z" else ("himari" if active else "himari_jito")
    h = 800 if active else 760
    img, dim = tachie(name, h)
    src = img if active else dim
    bob = int(abs(np.sin(t * 8)) * 14) if active else 0
    x = -40 if who == "z" else VW - src.width + 60
    y = VH - 170 - h + 120 - bob
    im.paste(src, (x, y), src)


def char_badge(d, cx, cy, c, active, t):
    """キャラの名札（絵は使わず、色と名前で表す）。話している方は少し大きく、上下に弾む"""
    bob = int(abs(np.sin(t * 9)) * 10) if active else 0
    r = 92 if active else 76
    col = c["col"] if active else tuple(int(v * 0.55 + 255 * 0.45) for v in c["col"])
    d.ellipse([cx - r, cy - r - bob, cx + r, cy + r - bob], fill=col, outline=(255, 255, 255), width=8)
    d.text((cx, cy - bob), c["name"][0], font=F(FONT_K, 96 if active else 78), fill=(255, 255, 255), anchor="mm")
    d.text((cx, cy + r + 34 - bob), c["name"], font=F(FONT_B, 38), fill=col, anchor="mm")


def frame(q, sp, who, text, t, info=None):
    global BG
    if BG is None: BG = bg()
    im = BG.copy(); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, VW, 200], fill=(124, 78, 178)); d.rectangle([0, 200, VW, 214], fill=(96, 176, 56))
    d.text((VW // 2, 70), "ずんだもんと冥鳴ひまりの", font=F(FONT_B, 44), fill=(255, 255, 255), anchor="mm")
    d.text((VW // 2, 140), "ポケモン雑学", font=F(FONT_K, 76), fill=(255, 236, 120), anchor="mm")
    jn = q["jn"]
    d.text((VW // 2, 300), jn, font=F(FONT_K, 96), fill=(40, 34, 50), anchor="mm", stroke_width=8, stroke_fill=(255, 255, 255))
    d.text((VW // 2, 390), P.ename(q["key"]), font=F(FONT_B, 54), fill=(124, 78, 178), anchor="mm")
    if sp:
        s = P.big(sp, 470); cx, cy = VW // 2, 720
        z = 1 + 0.03 * np.sin(t * 2.2)
        s2 = s.resize((int(s.width * z), int(s.height * z)), Image.NEAREST)
        d.ellipse([cx - 290, cy - 290, cx + 290, cy + 290], fill=(255, 255, 255), outline=(230, 222, 240), width=10)
        im.paste(s2, (cx - s2.width // 2, cy - s2.height // 2), s2)
    if info:
        d.rounded_rectangle([140, 1030, VW - 140, 1110], 40, fill=(255, 236, 120))
        d.text((VW // 2, 1070), info, font=F(FONT_K, 46), fill=(60, 40, 0), anchor="mm")
    # 聞いている方を先に、話している方を手前に描く
    other = "h" if who == "z" else "z"
    put_tachie(im, other, False, t); put_tachie(im, who, True, t)
    d = ImageDraw.Draw(im)
    # 字幕
    c = CHAR[who]; f = F(FONT_K, 60)
    lines = P.jwrap(d, text, f, VW - 150)[:3]
    h = 70 + 82 * len(lines); top = VH - 150 - h
    d.rounded_rectangle([40, top, VW - 40, top + h], 34, fill=(255, 255, 255), outline=c["col"], width=10)
    d.rounded_rectangle([70, top - 30, 70 + 40 + 44 * len(c["name"]), top + 26], 26, fill=c["col"])
    d.text((90, top - 2), c["name"], font=F(FONT_B, 40), fill=(255, 255, 255), anchor="lm")
    for i, ln in enumerate(lines):
        d.text((VW // 2, top + 70 + 82 * i), ln, font=f, fill=(40, 34, 50), anchor="mm")
    d.rectangle([0, VH - 120, VW, VH], fill=(124, 78, 178))
    d.text((VW // 2, VH - 60), "英語版の図鑑と和訳は プロフィールのサイトで", font=F(FONT_B, 40), fill=(255, 255, 255), anchor="mm")
    return im


def info_for(q, i):
    if q["kind"] == "stat" and i >= 1: return f"{q['stat'][0]} {q['stat'][1]}"
    if q["kind"] == "origin" and i >= 1: return P.ename(q["key"])
    return None


def bgm(dur):
    n = int(dur * SR); out = np.zeros(n, dtype=np.float32)
    # ゆったりした木琴風の伴奏
    notes = [523, 659, 784, 659, 587, 698, 880, 698, 523, 659, 784, 1047, 988, 784, 659, 587]
    step = 0.3; k = 0; x = 0.0
    while x < dur - 0.2:
        tt = np.arange(int(0.28 * SR)) / SR
        s = (np.sin(2 * np.pi * notes[k % 16] * tt) * np.exp(-tt * 9) * 0.05).astype(np.float32)
        a = int(x * SR); b = min(n, a + len(s)); out[a:b] += s[:b - a]; x += step; k += 1
    return out


def build(q, out):
    sp = P.sprite(q["key"])
    segs, voices, t0 = [], [], 0.25
    voiced = False
    for i, line in enumerate(q["lines"]):
        who, text = line[0], line[1]
        say = line[2] if len(line) > 2 else P.voice_text(text) or text
        c = CHAR[who]
        v = P.tts(say, c["sp"], c["speed"])
        if v is not None: voiced = True
        dur = (len(v) / SR + 0.3) if v is not None else max(1.6, len(text) * 0.14)
        info = info_for(q, i)
        segs.append((lambda t, who=who, text=text, info=info: frame(q, sp, who, text, t, info), dur))
        voices.append((t0, v)); t0 += dur
    # 最初のコマを長めに見せる余白
    segs[0] = (segs[0][0], segs[0][1] + 0.25)
    total = sum(round(d * FPS) / FPS for _, d in segs)
    render_with(segs, voices, total, out)
    frame(q, sp, "h", q["lines"][1][1], 0.0, info_for(q, 1)).save("thumb.png")
    return voiced


def render_with(segs, voices, total, out):
    import subprocess, wave
    os.makedirs("_z", exist_ok=True); parts = []
    for k, (fn, dur) in enumerate(segs):
        nfr = max(1, int(round(dur * FPS)))
        # 動きは小さいので 1秒あたり8コマで作って、24fpsに引き延ばす
        step = 3
        for i in range(0, nfr, step): fn(i / FPS).save(f"_z/s{k}_{i // step:04d}.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS / step), "-i", f"_z/s{k}_%04d.png", "-t", f"{nfr / FPS:.3f}",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-r", str(FPS), f"_z/s{k}.mp4"], check=True)
        parts.append(f"_z/s{k}.mp4")
    open("_zlist.txt", "w").write("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "_zlist.txt", "-c", "copy", "_zv.mp4"], check=True)
    mix = bgm(total)
    for t0, v in voices:
        if v is None: continue
        a = int(t0 * SR); b = min(len(mix), a + len(v)); mix[a:b] = mix[a:b] * 0.5 + v[:b - a]
    mix = np.clip(mix, -1, 1)
    with wave.open("_za.wav", "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 30000).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "_zv.mp4", "-i", "_za.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", out], check=True)


def meta(q, voiced):
    page = f"{SITE}/p/{q['key'].replace(' ', '_').replace('.', '')}.html"
    body = "\n".join(f"{CHAR[l[0]]['name']}「{l[1]}」" for l in q["lines"])
    credit = ("\n\n音声：VOICEVOX:ずんだもん、VOICEVOX:冥鳴ひまり" if voiced else "") + \
        "\n立ち絵：東北ずん子・ずんだもんプロジェクト（ずんだもん）、冥鳴ひまり公式（冥鳴ひまり／イラスト Sameta様）"
    src = f"\n参考：{q['src']}" if q.get("src") else ""
    desc = (f"{body}\n\n{q['jn']}の英語版図鑑と日本語訳 → {page}\nポケモン図鑑で英単語 → {SITE}/{src}{credit}\n\n"
            "#ポケモン #ポケモン雑学 #ずんだもん #冥鳴ひまり #shorts")
    return (q["title"] + " #shorts")[:100], desc


def upload(title, desc, mp4):
    env = {k: os.environ.get(k.replace("YT_", "YT2_")) for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN")}
    if not all(env.values()): print("雑学チャンネル: 鍵（YT2_*）が未設定なのでアップロードはしない"); return
    os.environ.update({k: v for k, v in env.items()})
    P.post_youtube(title, desc, mp4)


if __name__ == "__main__":
    d = dict(names=P.get_json("pokemon_names_jp.json"), stats=P.get_json("pokedex_stats.json"),
             origins=P.get_json("name_origins.json"), back=P.get_json("backstories.json"))
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(hours=9)
    n = int(os.environ["N"]) if os.environ.get("N") else (now.date() - START).days * SLOTS + (0 if now.hour < 14 else 1)
    q = pick(n, d); q["jn"] = d["names"][q["key"]]
    print(json.dumps(q, ensure_ascii=False))
    voiced = build(q, "zatsugaku.mp4")
    title, desc = meta(q, voiced); print(title); print(desc)
    if os.environ.get("DRY_RUN") == "1": sys.exit()
    upload(title, desc, "zatsugaku.mp4")
