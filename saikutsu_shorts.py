# ポケモン雑学採掘所のショート（@poke_zatsugaku、2026-11-15〜）
#   ・台本と素材は shorts/NNNN/script.json と同じフォルダの画像。Claudeが深く調べた話だけを並べる（自動でネタを作らない）
#   ・めたん（解説）とずんだもん（聞き役）。画面の上に見出し、中央に大きな画像、下に字幕、両下の隅に小さな立ち絵
#   ・最後に end_card でサイトのアドレスとホーム画面
#   ・投稿済みは posted_saikutsu.json に残し、まだ出していない一番若い番号を出す。台本が尽きたら何もしない
import os, sys, json, glob, wave, subprocess, datetime, io, urllib.request, urllib.parse
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import post as P
import yomi

HERE = os.path.dirname(os.path.abspath(__file__))
VW, VH, FPS, SR = 1080, 1920, 24, 44100
FD = os.path.join(HERE, "fonts")
F_HOOK = os.path.join(FD, "DelaGothicOne-Regular.ttf")
F_SUB = os.path.join(FD, "MPLUSRounded1c-Black.ttf")
F_SMALL = os.path.join(FD, "MPLUSRounded1c-ExtraBold.ttf")
METAN, ZUNDA = 2, 3                                  # VOICEVOX 話者ID（四国めたん ノーマル／ずんだもん ノーマル）
SPEED = 1.3                                          # 指示書：話す速さは1.3倍くらい
CH = {"m": dict(name="めたん", sp=METAN, col=(214, 64, 140), img="metan_h"),
      "z": dict(name="ずんだもん", sp=ZUNDA, col=(70, 150, 40), img="zundamon_h")}
HIST = os.path.join(HERE, "posted_saikutsu.json")
_FC = {}


def font(p, s):
    k = (p, s)
    if k not in _FC: _FC[k] = ImageFont.truetype(p, s)
    return _FC[k]


def ease(x):
    x = min(1.0, max(0.0, x)); return 1 - (1 - x) ** 3


# ---------- 読み上げ ----------
def tts(line, speaker):
    """kana（AquesTalk風の読みとアクセント）があればそれで読む。エンジンが無ければ None"""
    vv = P.VV
    def req(path, data=None):
        h = {"Content-Type": "application/json"} if data else {}
        return urllib.request.urlopen(urllib.request.Request(vv + path, data=data, headers=h, method="POST"), timeout=90).read()
    text = line.get("say") or line["t"]
    try:
        yomi.prepare(vv, text)                     # ポケモン名をユーザー辞書に（崩れる名前だけ）
        q = json.loads(req("/audio_query?" + urllib.parse.urlencode({"text": text, "speaker": speaker})))
        kana = line.get("kana")
        if not kana:
            k2 = yomi.autofix(q.get("kana", ""), text)    # 「なのだ」の割れなど、確実に直せる崩れを直す
            if k2 != q.get("kana", ""): kana = k2
            for s in yomi.issues(vv, text, k2): print("【読みの要確認】", text.replace("\n", ""), "|", k2, "|", s)
        if kana:
            q["accent_phrases"] = json.loads(req("/accent_phrases?" + urllib.parse.urlencode({"text": kana, "speaker": speaker, "is_kana": "true"})))
        q.update(speedScale=SPEED, outputSamplingRate=SR, volumeScale=1.25, prePhonemeLength=0.05, postPhonemeLength=0.12)
        wav = req(f"/synthesis?speaker={speaker}", json.dumps(q).encode())
        with wave.open(io.BytesIO(wav)) as w:
            a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
            if w.getnchannels() == 2: a = a.reshape(-1, 2).mean(axis=1)
        return a
    except Exception as e:
        print("VOICEVOX なし:", repr(e)[:120]); return None


# ---------- 素材 ----------
_TACH = {}


FACES = ("normal", "happy", "proud", "surprise", "sad", "shock", "think")


def face_of(ln):
    """台本の face があればそれ。なければせりふの終わり方から選ぶ"""
    if ln.get("face") in FACES: return ln["face"]
    t = ln["t"].replace("\n", "")
    if "！？" in t or "!?" in t: return "surprise"
    if t.endswith("……") or t.endswith("……。"): return "sad"
    if ln["w"] == "z" and t.endswith("？"): return "think"
    if ln["w"] == "z" and t.endswith("！"): return "proud"
    return "normal"


def tachie(who, open_, h, face="normal"):
    k = (who, open_, h, face)
    if k not in _TACH:
        name = CH[who]["img"] + "_" + face + ("_open" if open_ else "")
        path = os.path.join(HERE, "chara", name + ".png")
        if not os.path.exists(path):      # 表情の絵がなければ前の1枚絵
            path = os.path.join(HERE, "chara", CH[who]["img"] + ("_open" if open_ else "") + ".png")
        im = Image.open(path).convert("RGBA")
        im = im.crop((0, 0, im.width, int(im.height * 0.62)))         # 頭から腰まで
        im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
        if who == "m": im = im.transpose(Image.FLIP_LEFT_RIGHT)      # めたんは左の隅から右を向く
        _TACH[k] = im
    return _TACH[k]


def load_img(d, spec):
    """spec: ファイル名、sp:英語名（スプライト1体）、sp2:a,b／sp3:a,b,c（並べる）"""
    if spec.startswith("sp"):
        keys = spec.split(":", 1)[1].split(",")
        sps = [P.sprite(k) for k in keys]
        n = len(sps); size = 620 if n == 1 else (440 if n == 2 else 330)
        im = Image.new("RGBA", (size * n + 40 * (n - 1), size), (0, 0, 0, 0))
        for i, s in enumerate(sps):
            if s is None: continue
            b = P.big(s, size); im.paste(b, (i * (size + 40) + (size - b.width) // 2, (size - b.height) // 2), b)
        return im, True
    im = Image.open(os.path.join(d, spec))
    return im.convert("RGBA"), False


def background():
    # 坑道の岩肌：暗い茶色に、ぼんやりした明かり
    rng = np.random.default_rng(7)
    noise = rng.normal(0, 1, (VH // 8, VW // 8)).astype(np.float32)
    noise = np.array(Image.fromarray(((noise + 3) * 40).clip(0, 255).astype(np.uint8)).resize((VW, VH), Image.BICUBIC).filter(ImageFilter.GaussianBlur(6))) / 255.0
    y = np.linspace(0, 1, VH)[:, None]
    base = np.stack([46 + 30 * noise - 18 * y, 34 + 22 * noise - 14 * y, 26 + 16 * noise - 10 * y], -1)
    xx, yy = np.meshgrid(np.linspace(-1, 1, VW), np.linspace(-1, 1, VH))
    glow = np.exp(-((xx) ** 2 * 1.4 + (yy + 0.15) ** 2 * 1.1) * 1.6)[..., None]
    base = base + glow * np.array([70, 44, 18])
    return Image.fromarray(base.clip(0, 255).astype(np.uint8), "RGB")


def stroked(d, xy, text, f, fill, sw, sfill, anchor="mm"):
    d.text(xy, text, font=f, fill=fill, stroke_width=sw, stroke_fill=sfill, anchor=anchor)


def wrap(d, text, f, maxw):
    """読点・句点のところで区切って詰める。区切りの間が長すぎるときだけ字で折る。
    行頭に句読点や小さい字を置かない。台本に「\n」があればそこで必ず改行"""
    NG = "、。」』）！？ぁぃぅぇぉっゃゅょァィゥェォッャュョー…"
    out = []
    for para in text.split("\n"):
        chunks, cur = [], ""
        for ch in para:
            cur += ch
            if ch in "、。！？": chunks.append(cur); cur = ""
        if cur: chunks.append(cur)
        line = ""
        for c in chunks:
            if d.textlength(line + c, font=f) <= maxw: line += c; continue
            if line: out.append(line); line = ""
            while d.textlength(c, font=f) > maxw:          # 区切りの間が1行より長い
                k = len(c)
                while k > 1 and d.textlength(c[:k], font=f) > maxw: k -= 1
                while k > 1 and c[k] in NG: k -= 1
                out.append(c[:k]); c = c[k:]
            line = c
        if line: out.append(line)
    return out


# ---------- 1コマ ----------
class Short:
    def __init__(self, d):
        self.d = d; self.s = json.load(open(os.path.join(d, "script.json"), encoding="utf-8"))
        self.bg = background(); self.imgs = {}
        for ln in self.s["lines"]:
            if ln["img"] not in self.imgs: self.imgs[ln["img"]] = load_img(d, ln["img"])
        self.head = self._head()

    def _head(self):
        im = Image.new("RGBA", (VW, 430), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([40, 34, 400, 92], 29, fill=(20, 16, 12, 230))
        d.text((220, 63), "ポケモン雑学採掘所", font=font(F_SMALL, 34), fill=(255, 214, 90), anchor="mm")
        pre, l1, l2 = self.s["hook"]; hl = self.s.get("hl", "")
        stroked(d, (VW // 2, 150), pre, font(F_SMALL, 52), (255, 214, 90), 8, (0, 0, 0))
        for i, (txt, y) in enumerate(((l1, 250), (l2, 360))):
            f = font(F_HOOK, 96)
            while d.textlength(txt, font=f) > VW - 90: f = font(F_HOOK, f.size - 4)
            col = (255, 70, 50) if hl and hl in txt and i == 1 else (255, 255, 255)
            stroked(d, (VW // 2, y), txt, f, col, 11, (0, 0, 0))
        return im

    def listen_face(self, i, who):
        """聞いている方は、自分が直前に言ったときの顔を少し引きずる（驚き・ショックだけ）"""
        for j in range(i - 1, -1, -1):
            if self.s["lines"][j]["w"] == who:
                f = face_of(self.s["lines"][j]); return f if f in ("shock", "sad") else "normal"
        return "normal"

    def frame(self, i, t, dur, talking):
        ln = self.s["lines"][i]
        im = self.bg.copy()
        # 画像（ゆっくり寄る）
        src, is_sp = self.imgs[ln["img"]]
        box = (60, 440, VW - 60, 1120); bw, bh = box[2] - box[0], box[3] - box[1]
        same = i > 0 and self.s["lines"][i - 1]["img"] == ln["img"]
        k0 = 0 if not same else 1
        z = 1.0 + 0.05 * (t / max(dur, 0.1)) if not is_sp else 1.0 + 0.02 * np.sin(t * 2)
        s = min(bw / src.width, bh / src.height) * (1 if not is_sp else 1)
        w, h = int(src.width * s * z), int(src.height * s * z)
        pic = src.resize((w, h), Image.LANCZOS if not is_sp else Image.NEAREST)
        x, y = box[0] + (bw - w) // 2, box[1] + (bh - h) // 2
        a = 1.0 if same else ease(t / 0.25)
        if not is_sp:
            sh = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([20, 26, w + 20, h + 26], fill=(0, 0, 0, 160))
            sh = sh.filter(ImageFilter.GaussianBlur(14)); im.paste(sh, (x - 20, y - 20), sh)
            fr = Image.new("RGBA", (w + 16, h + 16), (250, 244, 230, 255)); im.paste(fr, (x - 8, y - 8), fr)
        if a < 1: pic = pic.copy(); pic.putalpha(Image.eval(pic.split()[3], lambda v: int(v * a)))
        im.paste(pic, (x, y), pic)
        d = ImageDraw.Draw(im)
        if ln.get("mark"):
            mx, my, mr = ln["mark"]; cx, cy, r = x + mx * w, y + my * h, mr * max(w, h)
            for k in range(3): d.ellipse([cx - r - k, cy - r - k, cx + r + k, cy + r + k], outline=(255, 40, 40), width=9)
        if ln.get("cap"):
            f = font(F_SMALL, 38); tw = d.textlength(ln["cap"], font=f)
            d.rounded_rectangle([x, y + h - 62, x + tw + 40, y + h], 0, fill=(0, 0, 0, 255))
            d.text((x + 20, y + h - 31), ln["cap"], font=f, fill=(255, 255, 255), anchor="lm")
        if ln.get("label"):
            f = font(F_SUB, 64)
            while d.textlength(ln["label"], font=f) > VW - 160: f = font(F_SUB, f.size - 4)
            stroked(d, (VW // 2, box[1] + 60), ln["label"], f, (255, 230, 80), 10, (0, 0, 0))
        im.paste(self.head, (0, 0), self.head)
        # 立ち絵（話している方は口を動かし、明るく）
        for who, left in (("m", True), ("z", False)):
            act = ln["w"] == who
            fc = face_of(ln) if act else ("normal" if i == 0 else self.listen_face(i, who))
            th = tachie(who, act and talking and int(t * 9) % 2 == 0, 470, fc)
            if not act:
                th = th.copy(); px = np.array(th).astype(np.float32); px[..., :3] *= 0.6; th = Image.fromarray(px.astype(np.uint8))
            bob = int(abs(np.sin(t * 7)) * 8) if act else 0
            xx = -40 if left else VW - th.width + 40
            im.paste(th, (xx, VH - th.height + 30 - bob), th)
        # 字幕（箱なし、太い縁取り、話者の色）
        c = CH[ln["w"]]; lines = ln["t"].split("\n"); size = 70
        f = font(F_SUB, size)
        while size > 46 and max(d.textlength(x, font=f) for x in lines) > VW - 100: size -= 2; f = font(F_SUB, size)
        lh = f.size + 18; top = 1235
        for j, s_ in enumerate(lines):
            stroked(d, (VW // 2, top + j * lh), s_, f, (255, 255, 255), 12, c["col"])
        return im.convert("RGB")


def build(d, out):
    S = Short(d); s = S.s
    segs, voices, t0 = [], [], 0.2
    voiced = False
    for i, ln in enumerate(s["lines"]):
        v = tts(ln, CH[ln["w"]]["sp"])
        if v is not None: voiced = True
        talk = (len(v) / SR) if v is not None else max(1.4, len(ln["t"]) * 0.11)
        dur = talk + 0.22
        segs.append((i, dur, talk)); voices.append((t0, v)); t0 += dur
    segs[0] = (segs[0][0], segs[0][1] + 0.2, segs[0][2])
    os.makedirs("_s", exist_ok=True)
    parts = []
    for k, (i, dur, talk) in enumerate(segs):
        nfr = max(1, int(round(dur * FPS))); step = 2
        for j in range(0, nfr, step):
            tt = j / FPS
            S.frame(i, tt, dur, tt < talk).save(f"_s/f{k}_{j // step:04d}.jpg", quality=90)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS / step), "-i", f"_s/f{k}_%04d.jpg", "-t", f"{nfr / FPS:.3f}",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-r", str(FPS), f"_s/p{k}.mp4"], check=True)
        parts.append(f"_s/p{k}.mp4")
    open("_s/list.txt", "w").write("".join(f"file '{os.path.basename(p)}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "_s/list.txt", "-c", "copy", "_s/v.mp4"], check=True)
    total = sum(round(dur * FPS) / FPS for _, dur, _ in segs)
    import music
    st = music.style(int(s["no"]) * 131 + 7, "calm")
    mix = music.bgm(st, total, 0.5).astype(np.float32)[: int(total * SR)]
    if len(mix) < int(total * SR): mix = np.pad(mix, (0, int(total * SR) - len(mix)))
    for t0, v in voices:
        if v is None: continue
        a = int(t0 * SR); b = min(len(mix), a + len(v)); mix[a:b] = mix[a:b] * 0.35 + v[:b - a]
    # 効果音は「起きた瞬間」だけ（sfx.py の作法）。冒頭=衝撃音、画像が替わる=シュッ、赤丸=ポン、答え（"ans"）=衝撃音かキラーン
    import sfx
    L_ = s["lines"]; starts = [t for t, _ in voices]; ev = [(starts[0], "impact")]
    for k in range(1, len(L_)):
        if L_[k]["img"] != L_[k - 1]["img"]: ev.append((starts[k] - 0.05, "whoosh"))
        if L_[k].get("mark") and L_[k].get("mark") != L_[k - 1].get("mark"): ev.append((starts[k] + 0.2, "pop"))
    for k, ln in enumerate(L_):
        if ln.get("ans"): ev.append((starts[k], ln["ans"] if ln["ans"] in sfx.KIND else "impact"))
    first_cut = next((starts[k] for k in range(1, len(L_)) if L_[k]["img"] != L_[k - 1]["img"]), None)
    if first_cut is not None and first_cut < 3.0: print(f"注意: 最初の画像の切り替えが {first_cut:.1f} 秒。最初の3秒は1枚の絵にする（2行目も同じ img にする）")
    if not any(ln.get("ans") for ln in L_): print('注意: 答えの行に "ans": true が無いので、答えの効果音が鳴らない')
    ev = sfx.thin(ev, total); sfx.add(mix, ev, SR); print("効果音", len(ev), "個", [(round(t, 1), k) for t, k in ev])
    mix = np.clip(mix, -1, 1)
    with wave.open("_s/a.wav", "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 30000).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "_s/v.mp4", "-i", "_s/a.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", out], check=True)
    import end_card
    end_card.add(out)
    # 音の大きさをそろえる（長い動画と同じ基準）
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", out, "-c:v", "copy", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "_s/norm.mp4"], check=True)
    os.replace("_s/norm.mp4", out)
    S.frame(1, 1.0, 2.0, False).save("thumb.png")
    return voiced


def meta(s):
    site = P.SITE
    pages = "\n".join(f"{ja}（{en}）の英語版図鑑 → {site}/p/{slug}.html" for slug, ja, en in s["pokemon"])
    desc = (f"{s['lead']}\n\n"
            f"▼この話の記事（出典つき）\n{s['article']}\n"
            + (f"▼くわしくは本編で\nhttps://youtu.be/{s['video']}\n" if s.get("video") else "")
            + f"\n{pages}\n\nポケモンの英語名と図鑑は「もんすぺ！」→ {site}\n\n"
            "音声：VOICEVOX:四国めたん、VOICEVOX:ずんだもん\n立ち絵：坂本アヒル様\n効果音：OtoLogic（https://otologic.jp）\n"
            "※ファンが運営する非公式のチャンネルです。株式会社ポケモン、任天堂、クリーチャーズ、ゲームフリークとは関係ありません。\n\n"
            "#ポケモン #ポケモン雑学 #ポケモン雑学採掘所 #shorts")
    return (s["title"] + " #shorts")[:100], desc


def load_hist():
    try: return json.load(open(HIST, encoding="utf-8"))
    except Exception: return []


if __name__ == "__main__":
    hist = load_hist(); done = {h["no"] for h in hist}
    dirs = sorted(glob.glob(os.path.join(HERE, "shorts", "[0-9][0-9][0-9][0-9]")))
    want = os.environ.get("NO")
    if want: dirs = [x for x in dirs if int(os.path.basename(x)) == int(want)]
    else: dirs = [x for x in dirs if int(os.path.basename(x)) not in done]
    if not dirs: print("出していない台本がありません。shorts/ に台本を足してください"); sys.exit()
    d = dirs[0]
    voiced = build(d, "saikutsu.mp4")
    s = json.load(open(os.path.join(d, "script.json"), encoding="utf-8"))
    title, desc = meta(s); print(title); print(desc)
    if os.environ.get("DRY_RUN") == "1": sys.exit()
    import zatsugaku as Z
    vid = Z.upload(title, desc, "saikutsu.mp4")
    if vid:
        now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
        hist.append({"no": s["no"], "video": vid, "title": s["title"], "date": now.strftime("%Y-%m-%d %H:%M")})
        json.dump(hist, open(HIST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
