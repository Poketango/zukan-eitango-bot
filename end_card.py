# ショートの最後に「もんすぺ！で検索」とサイトのホーム画面を見せる締めの場面を付ける（2026-11-15）
#   import end_card; end_card.add("short.mp4")
#   ホーム画面の画像は assets/img/site_home.png（スマホ幅で撮ったもの。サイトの見た目が変わったら撮り直す）
import os, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, SR = 1080, 1920, 24, 44100
DUR = 3.4
HOME = os.path.join(HERE, "assets", "img", "site_home.png")
FB = os.path.join(HERE, "fonts", "DelaGothicOne-Regular.ttf")
FM = os.path.join(HERE, "fonts", "MPLUSRounded1c-ExtraBold.ttf")
LINE = "ポケモンの英語名と図鑑は、もんすぺで検索なのだ！"
# 読みとアクセントを指定（エンジン任せだと「もんすぺ、で」で切れて「のだ」が浮いた）
KANA = "ポケモンノ'/エエゴ'メエト/ズカンワ'、モンスペ'デ/ケンサクナ'ノダ"


def _voice():
    import post, json, io, urllib.request, urllib.parse
    vv = post.VV
    def req(path, data=None):
        h = {"Content-Type": "application/json"} if data else {}
        return urllib.request.urlopen(urllib.request.Request(vv + path, data=data, headers=h, method="POST"), timeout=60).read()
    q = json.loads(req("/audio_query?" + urllib.parse.urlencode({"text": LINE, "speaker": post.ZUNDA})))
    try:
        q["accent_phrases"] = json.loads(req("/accent_phrases?" + urllib.parse.urlencode({"text": KANA, "speaker": post.ZUNDA, "is_kana": "true"})))
    except Exception as ex:
        print("アクセント指定なしで読む:", repr(ex)[:100])
    q.update(speedScale=1.15, outputSamplingRate=SR, volumeScale=1.3, prePhonemeLength=0.05, postPhonemeLength=0.15)
    wav = req(f"/synthesis?speaker={post.ZUNDA}", json.dumps(q).encode())
    with wave.open(io.BytesIO(wav)) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2: a = a.reshape(-1, 2).mean(axis=1)
    return a


def ease(x):
    x = min(1.0, max(0.0, x)); return 1 - (1 - x) ** 3


def _font(p, s): return ImageFont.truetype(p, s)


def _ctext(d, y, text, font, fill, stroke=0, sfill=(0, 0, 0)):
    w = d.textbbox((0, 0), text, font=font, stroke_width=stroke)[2]
    d.text(((W - w) / 2, y), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill)


def _base():
    g = np.linspace(0, 1, H)[:, None]
    top, bot = np.array([28, 22, 52]), np.array([10, 10, 18])
    arr = (top * (1 - g) + bot * g)[:, None, :].repeat(W, axis=1).astype(np.uint8)
    im = Image.fromarray(arr, "RGB")
    glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse([140, 560, 940, 1500], fill=110)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    im = Image.composite(Image.new("RGB", (W, H), (255, 120, 40)), im, glow)
    d = ImageDraw.Draw(im)
    _ctext(d, 120, "ポケモンの英語名と図鑑は", _font(FM, 62), (255, 255, 255))
    f = _font(FB, 124)
    w1 = d.textbbox((0, 0), "もんすぺ！", font=f, stroke_width=9)[2]
    w2 = d.textbbox((0, 0), "で検索", font=_font(FB, 80), stroke_width=7)[2]
    x = (W - w1 - w2 - 10) / 2
    d.text((x, 215), "もんすぺ！", font=f, fill=(255, 205, 0), stroke_width=9, stroke_fill=(20, 20, 20))
    d.text((x + w1 + 10, 258), "で検索", font=_font(FB, 80), fill=(255, 255, 255), stroke_width=7, stroke_fill=(20, 20, 20))
    _ctext(d, 580, "poketango.com", _font(FM, 44), (210, 210, 225))
    return im


def _phone():
    shot = Image.open(HOME).convert("RGB")
    shot = shot.crop((0, 0, shot.width, min(shot.height, 1150)))
    sw = 520; shot = shot.resize((sw, int(shot.height * sw / shot.width)), Image.LANCZOS)
    pw, ph, b = sw + 36, shot.height + 36, 18
    ph_im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    ImageDraw.Draw(ph_im).rounded_rectangle([0, 0, pw - 1, ph - 1], 56, fill=(18, 18, 22, 255), outline=(90, 90, 100, 255), width=4)
    m = Image.new("L", shot.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, shot.width - 1, shot.height - 1], 40, fill=255)
    ph_im.paste(shot, (b, b), m)
    return ph_im


def frames():
    base, phone = _base(), _phone()
    sh = Image.new("RGBA", (phone.width + 80, phone.height + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([40, 50, phone.width + 40, phone.height + 50], 56, fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    fq = _font(FM, 52); word = "もんすぺ"
    for i in range(int(DUR * FPS)):
        t = i / FPS
        im = base.copy(); d = ImageDraw.Draw(im)
        # 検索窓（文字を1字ずつ打つ）
        bx, by, bw, bh = 140, 420, 800, 120
        d.rounded_rectangle([bx, by, bx + bw, by + bh], 60, fill=(255, 255, 255))
        d.ellipse([bx + 44, by + 34, bx + 92, by + 82], outline=(110, 110, 120), width=7)
        d.line([bx + 86, by + 76, bx + 106, by + 96], fill=(110, 110, 120), width=8)
        n = min(len(word), int(max(0, t - 0.15) / 0.16) + (t > 0.15))
        d.text((bx + 130, by + 26), word[:n], font=fq, fill=(30, 30, 30))
        if n < len(word) or int(t * 3) % 2 == 0:
            cx = bx + 132 + (d.textbbox((0, 0), word[:n], font=fq)[2] if n else 0)
            d.rectangle([cx, by + 30, cx + 5, by + 92], fill=(30, 110, 230))
        # ホーム画面のスマホが下から上がってきて、少しずつ寄る
        k = ease((t - 0.35) / 0.55)
        s = 1.0 + 0.04 * ease((t - 0.9) / 2.5)
        ph = phone.resize((int(phone.width * s), int(phone.height * s)), Image.BILINEAR) if s != 1 else phone
        x = (W - ph.width) // 2; y = int(680 + (1 - k) * 1300)
        im.paste(sh.resize((ph.width + 80, ph.height + 80)), (x - 40, y - 40), sh.resize((ph.width + 80, ph.height + 80)))
        im.paste(ph, (x, y), ph)
        yield im


def _chime():
    n = int(DUR * SR); a = np.zeros(n, np.float32)
    for t0, f in ((0.0, 1046.5), (0.12, 1568.0)):
        k = np.arange(int(0.9 * SR)); env = np.exp(-k / SR * 5.0)
        tone = (np.sin(2 * np.pi * f * k / SR) + 0.3 * np.sin(4 * np.pi * f * k / SR)) * env * 0.22
        s = int(t0 * SR); a[s:s + len(tone)] += tone[:n - s]
    return a


def add(mp4, voice=True):
    """mp4 の最後に締めの場面を足して、同じ名前で上書きする。失敗しても元の動画はそのまま残す"""
    try:
        global DUR
        os.makedirs("_end", exist_ok=True)
        v = None
        if voice:
            try: v = _voice()
            except Exception as ex: print("締めの声なし:", repr(ex)[:120])
        # 声が最後まで入るように、締めの場面の長さを声に合わせてのばす（声のあとに0.6秒の余白）
        DUR = max(3.4, 0.25 + (len(v) / SR if v is not None else 0) + 0.6)
        for i, im in enumerate(frames()): im.save(f"_end/{i:04d}.jpg", quality=92)
        a = _chime()
        if v is not None:
            s = int(0.25 * SR); e = min(len(a), s + len(v)); a[s:e] += v[:e - s]
        a = np.clip(a, -1, 1)
        with wave.open("_end/a.wav", "w") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((a * 30000).astype(np.int16).tobytes())
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", "_end/%04d.jpg", "-i", "_end/a.wav",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "_end/end.mp4"], check=True)
        fc = (f"[0:v]scale={W}:{H},fps={FPS},format=yuv420p,setsar=1[v0];[1:v]scale={W}:{H},fps={FPS},format=yuv420p,setsar=1[v1];"
              f"[0:a]aresample={SR},aformat=channel_layouts=stereo[a0];[1:a]aresample={SR},aformat=channel_layouts=stereo[a1];"
              f"[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-i", "_end/end.mp4", "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "_end/out.mp4"], check=True)
        os.replace("_end/out.mp4", mp4)
        print("締めの場面を付けました")
    except Exception as ex:
        print("締めの場面を付けられませんでした:", repr(ex)[:200])


if __name__ == "__main__":
    import sys
    add(sys.argv[1], voice=False)
