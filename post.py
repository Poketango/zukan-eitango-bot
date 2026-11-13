# ポケモン英語図鑑 YouTubeショート自動投稿（GitHub Actions で毎朝実行）
# 2026-11-13 てこ入れ版：勉強っぽい穴埋めクイズをやめ、2つのエンタメ型を日替わりで出す
#   偶数日：シルエット×英語名クイズ「この英語名、だーれだ？」→ 正解と英語名の由来（ダジャレ）
#   奇数日：英語版の図鑑が怖すぎる → 英文と日本語訳
import os, sys, json, random, re, datetime, subprocess, io, math, wave, struct
import urllib.request, urllib.parse
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SITE = "https://poketango.github.io"
START = datetime.date(2026, 11, 14)          # この日を0日目として日替わりで出題
FONT_B = os.environ.get("FONT_B", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
FONT_K = os.environ.get("FONT_K", "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc")
FONT_R = os.environ.get("FONT_R", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
VW, VH = 1080, 1920
LOCAL = os.environ.get("LOCAL_DATA")

# 英語版の図鑑が怖い・切ないポケモン（実際の英語版図鑑の文を使う）
SCARY = ["haunter", "cubone", "drifloon", "victreebel", "banette", "golbat", "yamask", "phantump", "froslass", "dusknoir",
         "mimikyu", "spiritomb", "marowak", "duskull", "gourgeist", "lampent", "mandibuzz", "cursola", "bramblin", "misdreavus",
         "drifblim", "dhelmise", "sableye", "litwick", "chandelure", "shuppet", "gengar", "jellicent", "trevenant", "polteageist"]


def F(p, s): return ImageFont.truetype(p, s, index=0)


def get_json(name):
    if LOCAL: return json.load(open(os.path.join(LOCAL, name), encoding="utf-8"))
    with urllib.request.urlopen(f"{SITE}/{name}") as r: return json.loads(r.read().decode("utf-8"))


def sprite(key):
    try:
        if LOCAL: return Image.open(os.path.join(LOCAL, "pokemon_sprites", key + ".png")).convert("RGBA")
        with urllib.request.urlopen(f"{SITE}/pokemon_sprites/{urllib.parse.quote(key)}.png") as r:
            return Image.open(io.BytesIO(r.read())).convert("RGBA")
    except Exception as e:
        print("sprite error", key, e); return None


def big(sp, size):
    bb = sp.getbbox() or (0, 0, sp.width, sp.height)
    sp = sp.crop(bb); s = size / max(sp.size)
    return sp.resize((max(1, int(sp.width * s)), max(1, int(sp.height * s))), Image.NEAREST)


def silhouette(sp, color=(30, 30, 40)):
    a = sp.split()[3]; im = Image.new("RGBA", sp.size, color + (0,)); im.putalpha(a); return im


def ename(k):
    special = {"mr. mime": "Mr. Mime", "mr. rime": "Mr. Rime", "mime jr.": "Mime Jr.", "farfetchd": "Farfetch'd", "sirfetchd": "Sirfetch'd",
               "nidoranf": "Nidoran♀", "nidoranm": "Nidoran♂", "ho-oh": "Ho-Oh", "porygon-z": "Porygon-Z", "type-null": "Type: Null"}
    return special.get(k, "-".join(p.capitalize() for p in k.split("-")))


def short_origin(t):
    t = re.sub(r"^英語名「[^」]*」は、", "", t.split("。")[0])
    t = re.sub(r"を組み合わせた名前と考えられている$", "", t)
    t = re.sub(r"(と考えられている|とされる|である)$", "", t)
    return t


def jwrap(d, text, font, maxw):
    lines, cur = [], ""
    for ch in text:
        if d.textlength(cur + ch, font=font) > maxw and cur: lines.append(cur); cur = ch
        else: cur += ch
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


# ---------- 出題を決める ----------
def pick(day, names, origins, stats, en):
    ids = {k: int(stats[k]["id"]) for k in en if k in stats and k in names}
    if day % 2 == 0:
        pool = [k for k in ids if k in origins and ids[k] <= 493 and ("組み合わせ" in origins[k]["t"] or "もじ" in origins[k]["t"])]
        pool.sort(key=lambda k: ids[k]); random.Random(20261114).shuffle(pool)
        key = pool[(day // 2) % len(pool)]
        # 選択肢は使わない（シルエットと英語名だけで当てる）
        return dict(kind="name", key=key)
    pool = [k for k in SCARY if k in ids]
    return dict(kind="scary", key=pool[(day // 2) % len(pool)])


# ---------- シルエット英語名クイズ ----------
BG1, RED, YEL, DARK, WHITE = (255, 214, 64), (227, 53, 13), (255, 240, 170), (31, 41, 51), (255, 255, 255)


def name_base(top="英語名クイズ"):
    im = Image.new("RGB", (VW, VH), BG1); d = ImageDraw.Draw(im)
    for k in range(14):  # 放射状のストライプ
        a0 = k * (360 / 14)
        d.pieslice([-900, -500, VW + 900, VH + 900], a0, a0 + 360 / 28, fill=(255, 200, 40))
    d.rectangle([0, 0, VW, 190], fill=RED); center(d, 95, top, F(FONT_K, 84), WHITE)
    d.rectangle([0, VH - 230, VW, VH], fill=DARK)
    center(d, VH - 150, "全1000匹の英語名と由来は", F(FONT_B, 46), WHITE)
    center(d, VH - 85, "プロフィールのサイトで", F(FONT_B, 46), YEL)
    return im, d


def name_scene(q, sp, phase, count=None):
    im, d = name_base()
    E, J = ename(q["key"]), q["jn"]
    center(d, 330, "この英語名、だーれだ？" if phase != "reveal" else "正解は…", F(FONT_K, 72), DARK)
    fE = F(FONT_K, 150 if len(E) <= 9 else 118)
    center(d, 520, E, fE, WHITE, stroke=14, sfill=DARK)
    if sp:
        s = big(sp, 620)
        img = s if phase == "reveal" else silhouette(s)
        # 白い丸の上にのせる
        cx, cy = VW // 2, 1030
        d.ellipse([cx - 360, cy - 360, cx + 360, cy + 360], fill=WHITE)
        im.paste(img, (cx - img.width // 2, cy - img.height // 2), img)
    if phase == "q" and count:
        d.ellipse([VW // 2 - 90, 1420, VW // 2 + 90, 1600], fill=RED)
        d.text((VW // 2, 1510), str(count), font=F(FONT_K, 120), fill=WHITE, anchor="mm")
    if phase == "reveal":
        center(d, 1440, J + "！", F(FONT_K, 110), RED, stroke=10, sfill=WHITE)
        o = q.get("origin", "")
        if o:
            f = F(FONT_B, 48)
            lines = jwrap(d, o, f, VW - 160)[:2]
            d.rounded_rectangle([60, 1520, VW - 60, 1520 + 66 * len(lines) + 30], 30, fill=WHITE)
            for k, ln in enumerate(lines): center(d, 1568 + k * 66, ln, f, DARK)
    return im


# ---------- 英語版の図鑑が怖い ----------
NIGHT, PURP, PALE = (18, 14, 32), (150, 110, 255), (225, 220, 255)


def scary_base():
    im = Image.new("RGB", (VW, VH), NIGHT); d = ImageDraw.Draw(im)
    for r in range(900, 0, -60):  # 中央のぼんやりした紫の光
        c = int(40 * (1 - r / 900))
        d.ellipse([VW // 2 - r, 900 - r, VW // 2 + r, 900 + r], fill=(18 + c, 14 + c // 2, 32 + c * 2))
    d.rectangle([0, 0, VW, 190], fill=(40, 10, 60)); center(d, 95, "英語版の図鑑が怖すぎる…", F(FONT_K, 76), PALE)
    d.rectangle([0, VH - 230, VW, VH], fill=(40, 10, 60))
    center(d, VH - 150, "英語版の図鑑の和訳は", F(FONT_B, 46), PALE)
    center(d, VH - 85, "プロフィールのサイトで", F(FONT_B, 46), PURP)
    return im, d


def scary_scene(q, sp, phase):
    im, d = scary_base()
    center(d, 300, f"{q['jn']}（{ename(q['key'])}）", F(FONT_K, 72), WHITE)
    if sp:
        s = big(sp, 460); glow = silhouette(s, (150, 110, 255)).filter(ImageFilter.GaussianBlur(18))
        x, y = VW // 2 - s.width // 2, 620 - s.height // 2
        im.paste(glow, (x, y), glow); im.paste(s, (x, y), s)
    f = F(FONT_B, 62); y = 940
    for ln in ewrap(d, q["sent"], f, VW - 120)[:6]:
        center(d, y, ln, f, PALE); y += 82
    if phase == "ja":
        fj = F(FONT_K, 66); y += 30
        lines = jwrap(d, q["ja"], fj, VW - 140)[:5]
        d.rounded_rectangle([40, y - 20, VW - 40, y + 92 * len(lines) + 20], 30, fill=(70, 20, 100))
        for ln in lines: center(d, y + 42, ln, fj, WHITE); y += 92
    return im


def scary_text(key, en, jp):
    """怖さが伝わる1〜2文だけを英語と日本語で取り出す"""
    kw = r"dead|death|deceased|die|soul|skull|kidnap|curse|blood|bones|grudge|afterlife|drag|wither|life|lives|victim|prey|melt|dissolve|spirit|ghost|haunt|child"
    es = [s for s in re.split(r"(?<=[.!?])\s+", en[key].replace("\n", " ")) if s]
    js = [s for s in re.split(r"(?<=[。！？])", jp.get(key, "")) if s.strip()]
    strong = r"death|dead|deceased|die|skull|kidnap|wither|victim|bones|melt|dissolve|blood|grudge|afterlife|drag|lives|life-force|soul"
    def score(s): return 3 * len(re.findall(strong, s, re.I)) + len(re.findall(kw, s, re.I))
    i = max(range(len(es)), key=lambda j: (score(es[j]), -j))
    sent = " ".join(es[i:i + 2]) if len(es[i]) < 70 and i + 1 < len(es) else es[i]
    ja = "".join(js[i:i + 2]) if len(js) == len(es) and len(es[i]) < 70 and i + 1 < len(js) else (js[i] if len(js) == len(es) else "".join(js))
    return sent, ja


# ---------- 音 ----------
def synth(path, kind, dur, sr=44100):
    n = int(dur * sr); buf = [0.0] * n

    def tone(t0, length, freq, vol, shape="sq"):
        a = int(t0 * sr); L = int(length * sr)
        for k in range(L):
            if a + k >= n: break
            ph = (k * freq / sr) % 1.0
            v = (1 if ph < 0.5 else -1) if shape == "sq" else (math.sin(2 * math.pi * ph) if shape == "sin" else 2 * abs(2 * ph - 1) - 1)
            env = min(1, k / 300) * max(0, 1 - k / L) ** 0.7
            buf[a + k] += v * vol * env
    if kind == "name":
        mel = [784, 659, 784, 1047, 988, 784, 659, 587, 659, 784, 880, 784, 659, 523, 587, 659]
        t = 0; k = 0
        while t < dur - 0.5:
            tone(t, 0.18, mel[k % 16], 0.045); t += 0.2; k += 1
        for s in range(3): tone(3.0 + s, 0.15, 1046, 0.2, "sin")
        for s, fr in enumerate([784, 988, 1175, 1568, 2093]): tone(6.0 + s * 0.08, 0.3, fr, 0.15)
    else:
        for s in range(int(dur / 1.6)):
            tone(s * 1.6, 1.5, [110, 104, 98, 92][s % 4], 0.12, "tri"); tone(s * 1.6 + 0.8, 0.6, [440, 415, 392, 370][s % 4], 0.03, "sin")
        tone(5.2, 1.2, 233, 0.12, "sin"); tone(5.2, 1.2, 247, 0.12, "sin")
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, x)) * 30000)) for x in buf))


def render(scenes, kind, out):
    files = []
    for k, (im, dur) in enumerate(scenes):
        im.save(f"_s{k}.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-i", f"_s{k}.png", "-vf", f"format=yuv420p,loop=-1:1,trim=duration={dur}",
                        "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", f"_s{k}.mp4"], check=True)
        files.append(f"_s{k}.mp4")
    open("_list.txt", "w").write("".join(f"file '{f}'\n" for f in files))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "_list.txt", "-c", "copy", "_v.mp4"], check=True)
    synth("_a.wav", kind, sum(d for _, d in scenes))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "_v.mp4", "-i", "_a.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-shortest", out], check=True)


def build(q, out):
    sp = sprite(q["key"])
    if q["kind"] == "name":
        scenes = [(name_scene(q, sp, "intro"), 1.5)] + [(name_scene(q, sp, "q", c), 1.0) for c in (3, 2, 1)] + [(name_scene(q, sp, "reveal"), 5.0)]
    else:
        scenes = [(scary_scene(q, sp, "en"), 4.5), (scary_scene(q, sp, "ja"), 6.5)]
    render(scenes, q["kind"], out)
    sp_ = sp.copy() if sp else None
    thumb = (name_scene(q, sp_, "intro") if q["kind"] == "name" else scary_scene(q, sp_, "ja"))
    thumb.save("thumb.png")


def meta(q):
    page = f"{SITE}/p/{q['key'].replace(' ', '_').replace('.', '')}.html"
    if q["kind"] == "name":
        title = f"この英語名、どのポケモン？「{ename(q['key'])}」【英語名クイズ】 #shorts"
        desc = (f"正解は{q['jn']}！\n英語名の由来：{q.get('origin', '')}\n\n{q['jn']}の英語版図鑑と日本語訳 → {page}\n"
                f"英語名がダジャレなポケモンまとめ → {SITE}/p/pun.html\n\n#ポケモン #ポケモン英語 #英語名")
    else:
        title = f"英語版のポケモン図鑑が怖すぎる…【{q['jn']}】 #shorts"
        desc = (f"英語版の図鑑より\n{q['sent']}\n→ {q['ja']}\n\n{q['jn']}の英語版図鑑と日本語訳 → {page}\n"
                f"英語版の図鑑が怖すぎるポケモンまとめ → {SITE}/p/scary.html\n\n#ポケモン #ポケモン英語 #ポケモン図鑑")
    return title[:100], desc


def post_youtube(title, desc, mp4):
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


if __name__ == "__main__":
    en, jp, names, stats, origins = (get_json(n) for n in ("pokedex_en.json", "pokedex_jp.json", "pokemon_names_jp.json", "pokedex_stats.json", "name_origins.json"))
    today = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(hours=9)
    day = int(os.environ.get("DAY", (today.date() - START).days))
    q = pick(day, names, origins, stats, en)
    q["jn"] = names[q["key"]]
    if q["kind"] == "name": q["origin"] = short_origin(origins[q["key"]]["t"])
    else: q["sent"], q["ja"] = scary_text(q["key"], en, jp)
    print(json.dumps(q, ensure_ascii=False))
    build(q, "short.mp4")
    title, desc = meta(q); print(title); print(desc)
    if os.environ.get("DRY_RUN") == "1": sys.exit()
    post_youtube(title, desc, "short.mp4")
