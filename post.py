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
ZUNDA, HIMARI = 3, 14                          # VOICEVOX 話者ID（ずんだもん ノーマル／冥鳴ひまり）

SCARY = ["haunter", "cubone", "drifloon", "victreebel", "banette", "golbat", "yamask", "phantump", "froslass", "dusknoir",
         "mimikyu", "spiritomb", "marowak", "duskull", "gourgeist", "lampent", "mandibuzz", "cursola", "bramblin", "misdreavus",
         "drifblim", "dhelmise", "sableye", "litwick", "chandelure", "shuppet", "gengar", "jellicent", "trevenant", "polteageist"]


def F(p, s):
    # 太いフォントが無い環境では、ある太さで代用する
    for cand in (p, p.replace("Black", "Bold"), FONT_B):
        if os.path.exists(cand): return ImageFont.truetype(cand, s, index=0)
    return ImageFont.load_default()


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
    return re.sub(r"(と考えられている|とされる|である)$", "", t)


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


# ---------- ナレーション（VOICEVOX） ----------
def tts(text, speaker, speed=1.0, pitch=0.0, intonation=1.0):
    """読み上げ音声を numpy 配列（44.1kHz, -1〜1）で返す。エンジンが無ければ None"""
    try:
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
def pick(n, names, origins, stats, en):
    ids = {k: int(stats[k]["id"]) for k in en if k in stats and k in names}
    if n % 2 == 0:
        pool = [k for k in ids if k in origins and ids[k] <= 493 and ("組み合わせ" in origins[k]["t"] or "もじ" in origins[k]["t"])]
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


def name_scene(q, sp, phase, count=None):
    im = Image.new("RGB", (VW, VH), BG1); d = ImageDraw.Draw(im)
    for k in range(14):
        a0 = k * (360 / 14); d.pieslice([-900, -500, VW + 900, VH + 900], a0, a0 + 360 / 28, fill=(255, 200, 40))
    d.rectangle([0, 0, VW, 190], fill=RED); center(d, 95, "英語名クイズ", F(FONT_K, 84), WHITE)
    d.rectangle([0, VH - 230, VW, VH], fill=DARK)
    center(d, VH - 150, "全1000匹の英語名と由来は", F(FONT_B, 46), WHITE); center(d, VH - 85, "プロフィールのサイトで", F(FONT_B, 46), YEL)
    E, J = ename(q["key"]), q["jn"]
    center(d, 330, "この英語名、だーれだ？" if phase != "reveal" else "正解は…", F(FONT_K, 72), DARK)
    center(d, 520, E, F(FONT_K, 150 if len(E) <= 9 else 118), WHITE, stroke=14, sfill=DARK)
    if sp:
        s = big(sp, 620); img = s if phase == "reveal" else silhouette(s)
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
            f = F(FONT_B, 48); lines = jwrap(d, o, f, VW - 160)[:2]
            d.rounded_rectangle([60, 1520, VW - 60, 1520 + 66 * len(lines) + 30], 30, fill=WHITE)
            for k, ln in enumerate(lines): center(d, 1568 + k * 66, ln, f, DARK)
    return im


def name_video(q, sp):
    """(フレームを返す関数, 秒数) の並びと、ナレーションの配置を返す"""
    v1 = tts("この英語名のポケモン、だーれだ？", ZUNDA, 1.15)
    vo = voice_text(q.get("origin", ""))
    v2 = tts(f"正解は、{q['jn']}なのだ！" + (f"{vo}、が由来なのだ。" if vo else ""), ZUNDA, 1.12)
    intro = max(1.6, (len(v1) / SR + 0.2) if v1 is not None else 0)
    rev = max(5.0, (len(v2) / SR + 0.6) if v2 is not None else 0)
    imgs = {"i": name_scene(q, sp, "intro"), 3: name_scene(q, sp, "q", 3), 2: name_scene(q, sp, "q", 2), 1: name_scene(q, sp, "q", 1),
            "r": name_scene(q, sp, "reveal")}
    segs = [(lambda t: imgs["i"], intro), (lambda t: imgs[3], 1.0), (lambda t: imgs[2], 1.0), (lambda t: imgs[1], 1.0), (lambda t: imgs["r"], rev)]
    voices = [(0.1, v1), (intro + 3.0 + 0.2, v2)]
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
    # ポケモン：ゆっくり近づく＋小刻みに揺れる＋ときどき本来の色が一瞬だけ見える
    if spr:
        s, tinted = spr
        z = 0.85 + 0.35 * min(1, t / total)
        if state.get("lunge"): z = 1.9
        w, h = int(tinted.width * z), int(tinted.height * z)
        flick = (int(t * FPS) % 37 == 0)
        src = s if flick else tinted
        img = src.resize((w, h), Image.NEAREST)
        jx = int(math.sin(t * 23) * 6 + (rng.integers(-10, 10) if int(t * FPS) % 11 == 0 else 0))
        jy = int(math.cos(t * 17) * 4)
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
    vja = tts(q["ja"], HIMARI, 0.82, -0.06, 0.6)
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
    voices = [(2.0 + t_type + 0.3, vja)]
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
    for t0, v in voices:
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
    return any(v is not None for _, v in voices)


def meta(q, voiced):
    page = f"{SITE}/p/{q['key'].replace(' ', '_').replace('.', '')}.html"
    credit = ("\n\nナレーション：VOICEVOX:ずんだもん" if q["kind"] == "name" else "\n\nナレーション：VOICEVOX:冥鳴ひまり") if voiced else ""
    if q["kind"] == "name":
        title = f"この英語名、どのポケモン？「{ename(q['key'])}」【英語名クイズ】 #shorts"
        desc = (f"正解は{q['jn']}！\n英語名の由来：{q.get('origin', '')}\n\n{q['jn']}の英語版図鑑と日本語訳 → {page}\n"
                f"英語名がダジャレなポケモンまとめ → {SITE}/p/pun.html\n"
                f"📚 ポケモン図鑑で覚える英単語(中1〜大学) → {SITE}/p/words.html\n🖨️ 無料の英単語プリント → {SITE}/p/print.html{credit}\n\n#ポケモン #ポケモン英語 #英語名")
    else:
        title = f"英語版のポケモン図鑑が怖すぎる…【{q['jn']}】 #shorts"
        desc = (f"英語版の図鑑より\n{q['sent']}\n→ {q['ja']}\n\n{q['jn']}の英語版図鑑と日本語訳 → {page}\n"
                f"英語版の図鑑が怖すぎるポケモンまとめ → {SITE}/p/scary.html\n"
                f"📚 ポケモン図鑑で覚える英単語(中1〜大学) → {SITE}/p/words.html{credit}\n\n#ポケモン #ポケモン図鑑 #ホラー")
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
    m = n // len(KINDS)
    import music
    STYLE = music.style(n * 101 + KINDS.index(kind), "quiz")
    bgm_label = music.label(STYLE) if kind != "scary" else "horror/" + str(STYLE["seed"])
    if kind in ("name", "scary"):
        q = pick(2 * (m + 1) + (kind == "scary"), names, origins, stats, en)   # 11-14朝・昼に出した1本目どうしを飛ばす
        q["jn"] = names[q["key"]]
        if q["kind"] == "name": q["origin"] = short_origin(origins[q["key"]]["t"])
        else: q["sent"], q["ja"] = scary_text(q["key"], en, jp)
        print(json.dumps(q, ensure_ascii=False))
        voiced = build(q, "short.mp4")
        title, desc = meta(q, voiced)
    else:
        import formats
        D = dict(en=en, jp=jp, names=names, stats=stats, origins=origins)
        q = formats.make(kind, m, D, "short.mp4", seed=n * 101 + KINDS.index(kind))
        bgm_label = music.label(formats.STYLE) if kind != "rank" else "horror/" + str(formats.STYLE["seed"])
        title, desc = formats.meta(kind, q, D)
        voice = "VOICEVOX:冥鳴ひまり" if kind == "rank" else "VOICEVOX:ずんだもん"
        desc += f"\n\nナレーション：{voice}"
    print(kind, n); print(title); print(desc)
    print("BGM:", bgm_label)
    if os.environ.get("DRY_RUN") == "1": sys.exit()
    vid = post_youtube(title, desc, "short.mp4")
    line = json.dumps({"date": now.strftime("%Y-%m-%d %H:%M"), "n": n, "kind": kind, "id": vid, "title": title, "bgm": bgm_label}, ensure_ascii=False) + "\n"
    open("/tmp/new_log_line", "w", encoding="utf-8").write(line)
    with open(LOG, "a", encoding="utf-8") as fp:
        fp.write(json.dumps({"date": now.strftime("%Y-%m-%d %H:%M"), "n": n, "kind": kind, "id": vid, "title": title, "bgm": bgm_label}, ensure_ascii=False) + "\n")
