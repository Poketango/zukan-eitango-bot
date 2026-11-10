# 図鑑で英単語クイズ 自動投稿（GitHub Actions で毎朝実行）
import os, sys, json, random, re, datetime, subprocess, io, math, wave, struct
import urllib.request
from PIL import Image, ImageDraw, ImageFont

SITE = "https://pokemon-eitango.netlify.app"
START = datetime.date(2026, 11, 16)          # この日を1日目として順番に出題
FONT_B = os.environ.get("FONT_B", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
FONT_R = os.environ.get("FONT_R", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
RED, DARK, CREAM, YEL, GRN = (214,40,40), (36,36,44), (255,250,240), (255,224,102), (46,160,90)
EXCLUDE = set("""about above after again all although always and any as because before below both but by can can't each either ever every few for from has have had here how if in into is it its it's just least less out many more most much now of on once one only or over since some sometimes such than that the their them then there these they this though through to under until very was we were what when where which while who whom whose why will with without would yet you are be been being said says other others another also even still its itself his her him she he our your may might could should must does did done make makes made like likely there's""".split())

def F(p, s): return ImageFont.truetype(p, s, index=0)
def get_json(name, local_dir=None):
    if local_dir: return json.load(open(os.path.join(local_dir, name), encoding="utf-8"))
    with urllib.request.urlopen(f"{SITE}/{name}") as r: return json.loads(r.read().decode("utf-8"))

def order_keys(en):
    keys = list(en.keys())
    rnd = random.Random(20261116)
    # 出題順：第1・第2世代のポケモンを先に（なじみがあるため）、その後はシャッフル
    return keys  # 呼び出し側で並べ替え

def norm(w): return re.sub(r"[^a-z']", "", w.lower())

def make_quiz(day, en, jp, names, stats):
    ids = {k: int(stats[k]["id"]) for k in en if k in stats}
    first = sorted([k for k in ids if ids[k] <= 251]); rest = sorted([k for k in ids if ids[k] > 251])
    rnd = random.Random(20261116); rnd.shuffle(first); rnd.shuffle(rest)
    order = first + rest
    # 全単語のプール（選択肢用）
    pool = set()
    for t in en.values():
        for w in t.split():
            nw = norm(w)
            if nw.isalpha() and 5 <= len(nw) <= 11 and nw not in EXCLUDE and w[:1].islower(): pool.add(nw)
    pool = sorted(pool)
    n = len(order)
    for tries in range(n):
        key = order[(day + tries) % n]
        text = en[key].replace("\n", " ")
        words = text.split(" ")
        name_n = norm(key)
        cands = [i for i, w in enumerate(words) if norm(w).isalpha() and 5 <= len(norm(w)) <= 11
                 and norm(w) not in EXCLUDE and w[:1].islower() and norm(w) != name_n and "-" not in w]
        if not cands: continue
        r = random.Random(day * 7919 + tries)
        i = max(cands, key=lambda c: (len(norm(words[c])) + r.random() * 3))
        ans = norm(words[i])
        def score(x):  # 似た語尾・似た長さを選ぶ
            return (x[-2:] == ans[-2:]) * 3 + (x[-3:] == ans[-3:]) * 2 - abs(len(x) - len(ans)) * 0.5 + r.random()
        others = sorted([x for x in pool if x != ans and x not in text.lower()], key=score, reverse=True)[:12]
        r.shuffle(others); opts = others[:3] + [ans]; r.shuffle(opts)
        # 文を短くする：答えを含む1文だけ使う
        sents = re.split(r"(?<=[.!?])\s+", text)
        acc = 0; sent = text; si = 0
        for si, s in enumerate(sents):
            if acc <= i < acc + len(s.split(" ")): sent = s; j = i - acc; break
            acc += len(s.split(" "))
        sw = sent.split(" "); trail = re.sub(r"[A-Za-z']", "", sw[j]); sw[j] = "___" + trail
        q = " ".join(sw)
        if len(q) > 150: continue
        jtext = jp.get(key, "")
        jsents = [x for x in re.split(r"(?<=[。！？])", jtext) if x.strip()]
        hint = (jsents[si] if len(jsents) == len(sents) and si < len(jsents) else jtext) if jtext else ""
        if len(hint) > 60: hint = hint[:58] + "…"
        return dict(key=key, name=names.get(key, key), sent=q, full=sent, ans=ans, opts=opts, hint=hint, jp=jtext)
    raise SystemExit("no quiz")

def wrap(d, text, font, maxw, blankw=0):
    out, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if d.textlength(t.replace("___", ""), font=font) + blankw * t.count("___") <= maxw: cur = t
        else: out.append(cur); cur = w
    out.append(cur); return out

def icon():
    try:
        with urllib.request.urlopen(f"{SITE}/favicon.png") as r: return Image.open(io.BytesIO(r.read())).convert("RGBA")
    except Exception: return None

def card(q, path, ic):
    W, H = 1200, 675
    im = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 96], fill=RED)
    d.text((40, 18), "ポケモン英語クイズ", font=F(FONT_B, 46), fill="white")
    f = F(FONT_B, 42); lines = wrap(d, q["sent"], f, W - 80, 150)
    total = 50 + 62 * len(lines) + 56 + 2 * 88 - 18
    y0 = 96 + (H - 62 - 96 - total) // 2
    d.text((40, y0), f"{q['name']}の英語版図鑑より", font=F(FONT_B, 34), fill=RED)
    y = y0 + 56
    for ln in lines:
        x = 40
        parts = ln.split("___")
        for k, p in enumerate(parts):
            d.text((x, y), p, font=f, fill=DARK); x += d.textlength(p, font=f)
            if k < len(parts) - 1:
                d.rounded_rectangle([x + 4, y + 6, x + 146, y + 56], 12, fill=YEL, outline=RED, width=3); x += 154
        y += 62
    d.text((40, y + 8), "ヒント（日本語版）：" + q["hint"][:34] + ("…" if len(q["hint"]) > 34 else ""), font=F(FONT_R, 28), fill=(110, 110, 120))
    oy = y + 60; bw = (W - 120) // 2
    for k, o in enumerate(q["opts"]):
        cx = 40 + (k % 2) * (bw + 40); cy = oy + (k // 2) * 88
        d.rounded_rectangle([cx, cy, cx + bw, cy + 70], 16, fill="white", outline=DARK, width=3)
        d.ellipse([cx + 14, cy + 11, cx + 62, cy + 59], fill=RED); d.text((cx + 38, cy + 35), "ABCD"[k], font=F(FONT_B, 30), fill="white", anchor="mm")
        d.text((cx + 80, cy + 35), o, font=F(FONT_B, 36), fill=DARK, anchor="lm")
    d.rectangle([0, H - 62, W, H], fill=DARK)
    if ic: s = ic.resize((44, 44), Image.NEAREST); im.paste(s, (30, H - 53), s)
    d.text((86, H - 31), "答えはリプで！  図鑑で英単語 → pokemon-eitango.netlify.app", font=F(FONT_R, 26), fill="white", anchor="lm")
    im.save(path)

# ---- 縦動画 ----
VW, VH = 1080, 1920
def vbase(ic):
    im = Image.new("RGB", (VW, VH), CREAM); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, VW, 200], fill=RED); d.text((VW // 2, 100), "ポケモン英語クイズ", font=F(FONT_B, 80), fill="white", anchor="mm")
    d.rectangle([0, VH - 210, VW, VH], fill=DARK)
    if ic: s = ic.resize((90, 90), Image.NEAREST); im.paste(s, (60, VH - 150), s)
    d.text((170, VH - 128), "図鑑で英単語", font=F(FONT_B, 44), fill="white"); d.text((170, VH - 72), "pokemon-eitango.netlify.app", font=F(FONT_R, 36), fill=(220, 220, 220))
    return im, d
def vquestion(q, ic, count=None, reveal=False):
    im, d = vbase(ic)
    d.text((VW // 2, 320), f"{q['name']}の英語版図鑑より", font=F(FONT_B, 56), fill=RED, anchor="mm")
    f = F(FONT_B, 60); tok = q["ans"] if reveal else "______"
    sent = q["sent"].replace("___", tok); lines = wrap(d, sent, f, VW - 140); y = 410
    for ln in lines:
        x = (VW - d.textlength(ln, font=f)) / 2
        if tok in ln:
            a, b = ln.split(tok, 1); d.text((x, y), a, font=f, fill=DARK); x += d.textlength(a, font=f); tw = d.textlength(tok, font=f)
            d.rounded_rectangle([x - 8, y + 8, x + tw + 8, y + 84], 16, fill=(GRN if reveal else YEL))
            d.text((x, y), tok, font=f, fill=("white" if reveal else YEL)); x += tw; d.text((x, y), b, font=f, fill=DARK)
        else: d.text((x, y), ln, font=f, fill=DARK)
        y += 92
    hf = F(FONT_R, 40); hl = []
    cur = ""
    for ch in "ヒント：" + q["hint"]:
        if d.textlength(cur + ch, font=hf) > VW - 160: hl.append(cur); cur = ch
        else: cur += ch
    hl.append(cur)
    for k, ln in enumerate(hl[:3]): d.text((VW // 2, y + 30 + k * 52), ln, font=hf, fill=(110, 110, 120), anchor="mm")
    oy = y + 30 + min(len(hl), 3) * 52 + 40
    for k, o in enumerate(q["opts"]):
        cy = oy + k * 140; ok = reveal and o == q["ans"]
        d.rounded_rectangle([90, cy, VW - 90, cy + 118], 28, fill=(GRN if ok else "white"), outline=(DARK if not reveal or ok else (200, 200, 200)), width=5)
        d.ellipse([120, cy + 17, 204, cy + 101], fill=("white" if ok else RED)); d.text((162, cy + 59), "ABCD"[k], font=F(FONT_B, 50), fill=(GRN if ok else "white"), anchor="mm")
        d.text((240, cy + 59), o, font=F(FONT_B, 60), fill=("white" if ok else DARK), anchor="lm")
    ey = oy + 4 * 140 + 20
    if count is not None:
        d.ellipse([VW // 2 - 80, ey, VW // 2 + 80, ey + 160], fill=RED); d.text((VW // 2, ey + 80), str(count), font=F(FONT_B, 100), fill="white", anchor="mm")
    if reveal: d.text((VW // 2, ey + 60), f"正解は {q['ans']}", font=F(FONT_B, 72), fill=GRN, anchor="mm")
    return im
def vintro(q, ic):
    im, d = vbase(ic)
    d.text((VW // 2, 700), "英語版の", font=F(FONT_B, 90), fill=DARK, anchor="mm")
    d.text((VW // 2, 830), "ポケモン図鑑", font=F(FONT_B, 120), fill=RED, anchor="mm")
    d.text((VW // 2, 960), "読める？", font=F(FONT_B, 90), fill=DARK, anchor="mm")
    d.text((VW // 2, 1160), f"今日は「{q['name']}」", font=F(FONT_B, 64), fill=DARK, anchor="mm")
    d.text((VW // 2, 1260), "5秒で答えてね", font=F(FONT_R, 52), fill=(110, 110, 120), anchor="mm")
    return im
def voutro(ic):
    im, d = vbase(ic)
    d.text((VW // 2, 720), "毎日クイズ出してます", font=F(FONT_B, 76), fill=DARK, anchor="mm")
    d.text((VW // 2, 850), "フォローしてね", font=F(FONT_B, 96), fill=RED, anchor="mm")
    d.rounded_rectangle([110, 1010, VW - 110, 1290], 30, fill="white", outline=RED, width=6)
    d.text((VW // 2, 1090), "図鑑の英文で英単語を覚える", font=F(FONT_B, 52), fill=DARK, anchor="mm")
    d.text((VW // 2, 1180), "無料サイトはプロフから", font=F(FONT_B, 58), fill=RED, anchor="mm")
    return im

def synth_audio(path, dur=13.5, sr=44100):
    n = int(dur * sr); buf = [0.0] * n
    def tone(t0, length, freq, vol, shape="sq"):
        a = int(t0 * sr); L = int(length * sr)
        for k in range(L):
            if a + k >= n: break
            ph = (k * freq / sr) % 1.0
            v = (1 if ph < 0.5 else -1) if shape == "sq" else math.sin(2 * math.pi * ph)
            env = min(1, k / 200) * max(0, 1 - k / L) ** 0.6
            buf[a + k] += v * vol * env
    # 明るいピコピコBGM（Cメジャーの繰り返し）
    mel = [523, 659, 784, 659, 587, 698, 880, 698, 523, 659, 784, 1047, 988, 784, 659, 587]
    bass = [131, 131, 175, 175, 147, 147, 196, 196]
    beat = 0.25; t = 0; k = 0
    while t < dur - 1:
        tone(t, beat * 0.9, mel[k % len(mel)], 0.05); 
        if k % 2 == 0: tone(t, beat * 1.8, bass[(k // 2) % len(bass)], 0.06, "sin")
        t += beat; k += 1
    for s in range(5): tone(2.5 + s, 0.12, 880, 0.18, "sin")            # カウントダウン
    for s, fr in enumerate([784, 988, 1175, 1568]): tone(7.5 + s * 0.09, 0.25, fr, 0.16)  # 正解音
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, x)) * 32000)) for x in buf))

def video(q, ic, out):
    scenes = [(vintro(q, ic), 2.5)] + [(vquestion(q, ic, c), 1.0) for c in (5, 4, 3, 2, 1)] + [(vquestion(q, ic, reveal=True), 3.5), (voutro(ic), 2.5)]
    files = []
    for k, (im, dur) in enumerate(scenes):
        im.save(f"_s{k}.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-i", f"_s{k}.png", "-vf", f"format=yuv420p,loop=-1:1,trim=duration={dur}",
                        "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", f"_s{k}.mp4"], check=True)
        files.append(f"_s{k}.mp4")
    open("_list.txt", "w").write("".join(f"file '{f}'\n" for f in files))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "_list.txt", "-c", "copy", "_v.mp4"], check=True)
    synth_audio("_a.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "_v.mp4", "-i", "_a.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-shortest", out], check=True)

def tweet_text(q, prev):
    t = ""
    if prev: t += f"昨日の答え：{'ABCD'[prev['opts'].index(prev['ans'])]} {prev['ans']}\n\n"
    t += f"【ポケモン英語クイズ】\n{q['name']}の英語版図鑑より👇\n{q['sent']}\n\n"
    t += "\n".join(f"{'ABCD'[k]} {o}" for k, o in enumerate(q["opts"]))
    t += "\n\nリプで答えてね！\n#ポケモン英単語 #英語学習"
    return t

def post_x(text, img):
    import tweepy
    k = [re.sub(r"\s", "", os.environ.get(x) or "") for x in ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET")]
    print("X key lengths:", [len(v) for v in k])
    if not all(k) or min(len(v) for v in k) < 20: print("X: 鍵が未設定なのでスキップ（Xはブラウザの予約投稿で運用）"); return
    auth = tweepy.OAuth1UserHandler(*k); api = tweepy.API(auth)
    m = api.media_upload(img)
    c = tweepy.Client(consumer_key=k[0], consumer_secret=k[1], access_token=k[2], access_token_secret=k[3])
    r = c.create_tweet(text=text, media_ids=[m.media_id]); print("X:", r.data)

def post_youtube(q, mp4):
    cid, cs, rt = (re.sub(r"\s", "", os.environ.get(x) or "") for x in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"))
    print("YT id ends with googleusercontent.com:", cid.endswith(".apps.googleusercontent.com"), "lengths:", len(cid), len(cs), len(rt))
    if not all((cid, cs, rt)): print("YouTube: 鍵が未設定なのでスキップ"); return
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    cred = Credentials(None, refresh_token=rt, token_uri="https://oauth2.googleapis.com/token", client_id=cid, client_secret=cs,
                       scopes=["https://www.googleapis.com/auth/youtube.upload"])
    yt = build("youtube", "v3", credentials=cred)
    body = {"snippet": {"title": f"英語版ポケモン図鑑、読める？【{q['name']}】 #shorts",
                        "description": f"英語版図鑑の一文で英単語クイズ！答えは「{q['ans']}」。\n図鑑で英単語を覚えるサイト → {SITE}\n#英語学習 #ポケモン #英単語",
                        "categoryId": "27", "defaultLanguage": "ja"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}}
    r = yt.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(mp4, mimetype="video/mp4")).execute()
    print("YouTube:", r.get("id"), r.get("status", {}).get("privacyStatus"))

if __name__ == "__main__":
    local = os.environ.get("LOCAL_DATA")
    en, jp, names, stats = (get_json(n, local) for n in ("pokedex_en.json", "pokedex_jp.json", "pokemon_names_jp.json", "pokedex_stats.json"))
    today = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(hours=9)
    day = int(os.environ.get("DAY", (today.date() - START).days))
    q = make_quiz(day, en, jp, names, stats); prev = make_quiz(day - 1, en, jp, names, stats) if day > 0 else None
    print(json.dumps(q, ensure_ascii=False))
    ic = icon() if not local else Image.open(os.path.join(local, "favicon.png")).convert("RGBA") if os.path.exists(os.path.join(local, "favicon.png")) else None
    card(q, "card.png", ic)
    if os.environ.get("NO_VIDEO") != "1": video(q, ic, "short.mp4")
    if os.environ.get("DRY_RUN") == "1": print(tweet_text(q, prev)); sys.exit()
    errs = []
    for fn in (lambda: post_x(tweet_text(q, prev), "card.png"), lambda: post_youtube(q, "short.mp4")):
        try: fn()
        except Exception as e: print("エラー:", repr(e)); errs.append(e)
    if errs: sys.exit(1)
