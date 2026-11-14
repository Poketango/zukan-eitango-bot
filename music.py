# ショート動画のBGMと効果音を、その場で毎回ちがうものに作る（著作権の心配がない自作の音）
#   style(seed) で「曲の作り（テンポ・調・音色・リズム・コード進行）」と「効果音のセット」を選ぶ。
#   seed を投稿ごとに変えるので、同じ曲が続かない。新しい音色やリズムは下の表に足していけば自動で混ざる。
import math, random
import numpy as np

SR = 44100
NOTE = {n: i for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}
SCALES = {"major": [0, 2, 4, 5, 7, 9, 11], "minor": [0, 2, 3, 5, 7, 8, 10], "dorian": [0, 2, 3, 5, 7, 9, 10],
          "mixolydian": [0, 2, 4, 5, 7, 9, 10], "penta": [0, 2, 4, 7, 9], "minpenta": [0, 3, 5, 7, 10], "lydian": [0, 2, 4, 6, 7, 9, 11]}
# コード進行（音階の何番目を根音にするか。0始まり）
PROGS = {"major": [[0, 4, 5, 3], [0, 5, 3, 4], [3, 4, 2, 5], [0, 3, 4, 4], [5, 3, 0, 4]],
         "minor": [[0, 5, 2, 6], [0, 3, 4, 0], [0, 6, 5, 6], [5, 6, 0, 0]],
         "dorian": [[0, 3, 0, 3], [0, 6, 3, 0]], "mixolydian": [[0, 6, 3, 0], [0, 3, 6, 0]],
         "lydian": [[0, 1, 0, 1], [0, 1, 4, 3]]}
LEADS = ["square", "pulse25", "triangle", "pluck", "bell", "saw", "organ", "marimba"]
BASSES = ["triangle", "square", "saw", "sine", "pluck"]
DRUMS = ["four", "rock", "half", "shuffle", "bossa", "breaks", "none"]
MOODS = {  # 型ごとに合う雰囲気
    "quiz": dict(tempo=(118, 152), scales=["major", "mixolydian", "penta", "lydian"]),
    "fast": dict(tempo=(140, 172), scales=["major", "minor", "dorian", "minpenta"]),
    "calm": dict(tempo=(92, 118), scales=["major", "dorian", "lydian", "penta"]),
}


def style(seed, mood="quiz"):
    r = random.Random(seed); M = MOODS[mood]
    sc = r.choice(M["scales"])
    return dict(seed=seed, mood=mood, key=r.choice(list(NOTE)), scale=sc, tempo=r.randint(*M["tempo"]),
                prog=r.choice(PROGS.get(sc, PROGS["major"])), lead=r.choice(LEADS), bass=r.choice(BASSES),
                drums=r.choice(DRUMS[:-1] if mood == "fast" else DRUMS), arp=r.random() < 0.5, swing=r.random() < 0.25,
                sfx=r.choice(list(SFX_SETS)))


def label(st):
    return f"{st['key']}{st['scale']}/{st['tempo']}bpm/{st['lead']}+{st['bass']}/{st['drums']}/{st['sfx']}"


# ---------- 音色 ----------
def osc(kind, f, n, t0=0):
    t = (np.arange(n) + t0) / SR; ph = (t * f) % 1.0
    if kind == "square": return np.where(ph < 0.5, 1.0, -1.0)
    if kind == "pulse25": return np.where(ph < 0.25, 1.0, -1.0)
    if kind == "triangle": return 4 * np.abs(ph - 0.5) - 1
    if kind == "saw":
        w = 2 * ph - 1; k = np.ones(9) / 9; return np.convolve(w, k, mode="same")      # かどを少し丸める
    if kind == "sine": return np.sin(2 * np.pi * ph)
    if kind == "organ": return (np.sin(2 * np.pi * ph) + 0.5 * np.sin(4 * np.pi * ph) + 0.25 * np.sin(6 * np.pi * ph)) / 1.6
    if kind == "bell":
        return np.sin(2 * np.pi * f * t + 3.0 * np.exp(-t * 6) * np.sin(2 * np.pi * f * 3.5 * t))
    if kind == "marimba":
        return np.sin(2 * np.pi * f * t) * np.exp(-t * 9) + 0.3 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 30)
    if kind == "pluck":   # カープラス＝ストロング（はじく弦）
        p = max(2, int(SR / f)); buf = np.random.default_rng(int(f)).uniform(-1, 1, p); out = np.zeros(n)
        for i in range(n):
            out[i] = buf[i % p]; buf[i % p] = 0.497 * (buf[i % p] + buf[(i + 1) % p])
        return out
    return np.sin(2 * np.pi * ph)


_CACHE = {}


def note(kind, f, length, vol):
    n = int(length * SR)
    if kind == "pluck":
        key = (round(f, 2), n)
        if key not in _CACHE: _CACHE[key] = osc(kind, f, n)
        w = _CACHE[key]
    else: w = osc(kind, f, n)
    t = np.arange(n) / SR
    if kind in ("pluck", "bell", "marimba"): env = np.minimum(1, t * 400)
    else: env = np.minimum(1, t * 150) * np.clip(1 - t / length, 0, 1) ** 0.6
    return (w * env * vol).astype(np.float32)


def freq(midi): return 440.0 * 2 ** ((midi - 69) / 12)


# ---------- 打楽器 ----------
def kick(v=0.5):
    t = np.arange(int(0.25 * SR)) / SR
    return (np.sin(2 * np.pi * (50 + 90 * np.exp(-t * 30)) * t) * np.exp(-t * 14) * v).astype(np.float32)


def snare(v=0.25):
    t = np.arange(int(0.18 * SR)) / SR
    return ((np.random.default_rng(5).standard_normal(len(t)) * 0.7 + np.sin(2 * np.pi * 190 * t) * 0.4) * np.exp(-t * 22) * v).astype(np.float32)


def hat(v=0.08, open_=False):
    t = np.arange(int((0.12 if open_ else 0.04) * SR)) / SR
    x = np.random.default_rng(9).standard_normal(len(t)); x = np.diff(np.concatenate([[0], x]))
    return (x * np.exp(-t * (18 if open_ else 80)) * v).astype(np.float32)


def shaker(v=0.05):
    t = np.arange(int(0.07 * SR)) / SR
    return (np.random.default_rng(2).standard_normal(len(t)) * np.sin(np.pi * t / 0.07) * v).astype(np.float32)


PATTERNS = {  # 16分音符16個ぶん：k=キック s=スネア h=ハット o=オープンハット c=シェイカー
    "four": ["k.h.k.hok.h.k.ho", "..s.....s......."],
    "rock": ["k.h.s.h.k.k.s.h.", ""],
    "half": ["k.h.h.h.s.h.h.hk", ""],
    "shuffle": ["k..hs..hk..hs..h", ""],
    "bossa": ["k..k..k.k..k..k.", "c.c.ccc.c.c.ccc."],
    "breaks": ["k.h.s.hkh.k.s.h.", "........c......."],
}


# ---------- 曲 ----------
def bgm(st, total, vol=1.0):
    r = random.Random(st["seed"] * 31 + 7)
    n = int(total * SR) + SR; out = np.zeros(n, np.float32)
    beat = 60 / st["tempo"]; s16 = beat / 4
    root = 60 + NOTE[st["key"]]
    if root > 66: root -= 12
    sc = SCALES[st["scale"]]

    def deg(d, octv=0):
        return root + sc[d % len(sc)] + 12 * (d // len(sc) + octv)

    def put(t0, sig):
        a = int(t0 * SR); b = min(n, a + len(sig))
        if 0 <= a < n: out[a:b] += sig[:b - a]
    bars = int(total / (beat * 4)) + 1
    # メロディの型を2小節ぶん作って、少しずつ変えながらくり返す
    rhythm = [r.choice([1, 1, 2, 2, 3, 4]) for _ in range(16)]
    motif = [r.choice([0, 2, 4, 4, 2, 1, 5, 7]) for _ in range(16)]
    for b in range(bars):
        t_bar = b * beat * 4; chord = st["prog"][b % len(st["prog"])]
        sw = lambda i: (s16 * 0.33 if st["swing"] and i % 2 else 0)
        # ベース
        bp = [0, 8] if st["drums"] in ("half", "bossa") else [0, 4, 8, 12]
        for i in bp: put(t_bar + i * s16 + sw(i), note(st["bass"], freq(deg(chord, -2)), s16 * 3.5, 0.10 * vol))
        # 和音（アルペジオか、ゆったりした和音）
        tones = [deg(chord), deg(chord + 2), deg(chord + 4)]
        if st["arp"]:
            for i in range(0, 16, 2): put(t_bar + i * s16 + sw(i), note("triangle", freq(tones[(i // 2) % 3] + 12), s16 * 1.8, 0.025 * vol))
        else:
            for tn in tones: put(t_bar, note("organ" if st["lead"] != "organ" else "sine", freq(tn), beat * 3.8, 0.018 * vol))
        # メロディ（2小節に1回、少し変える）
        i = 0; k = 0
        while i < 16:
            L = rhythm[k % 16]; dd = motif[k % 16] + chord + (r.choice([0, 0, 1, -1]) if b % 2 else 0)
            if r.random() > 0.15: put(t_bar + i * s16 + sw(i), note(st["lead"], freq(deg(dd, 1)), s16 * L * 0.95, 0.045 * vol))
            i += L; k += 1
        # 打楽器
        if st["drums"] != "none" and b > 0 or (st["drums"] != "none" and r.random() < 0.5):
            p1, p2 = PATTERNS[st["drums"]]
            for i in range(16):
                t = t_bar + i * s16 + sw(i)
                for pat in (p1, p2):
                    c = pat[i] if i < len(pat) else "."
                    if c == "k": put(t, kick(0.35 * vol))
                    elif c == "s": put(t, snare(0.18 * vol))
                    elif c == "h": put(t, hat(0.05 * vol))
                    elif c == "o": put(t, hat(0.05 * vol, True))
                    elif c == "c": put(t, shaker(0.04 * vol))
    # 最後は少しずつ小さく
    f = int(0.6 * SR); e = min(n, int(total * SR)); out[max(0, e - f):e] *= np.linspace(1, 0, min(f, e))
    out[e:] = 0
    return out


# ---------- 効果音のセット ----------
def _tone(f, l, v, kind="sine"): return note(kind, f, l, v)


def _seq(fs, step, l, v, kind):
    out = np.zeros(int((step * len(fs) + l) * SR), np.float32)
    for i, f in enumerate(fs):
        s = _tone(f, l, v, kind); a = int(i * step * SR); out[a:a + len(s)] += s
    return out


SFX_SETS = {
    "chime": dict(tick=lambda: _tone(1046, 0.12, 0.16), ding=lambda: _seq([784, 988, 1175, 1568, 2093], 0.07, 0.3, 0.12, "square"),
                  buzz=lambda: _tone(110, 0.35, 0.14, "square"), pop=lambda: _seq([660, 990], 0.06, 0.12, 0.12, "sine")),
    "coin": dict(tick=lambda: _tone(1568, 0.05, 0.12, "pulse25"), ding=lambda: _seq([988, 1319, 1976], 0.08, 0.35, 0.11, "pulse25"),
                 buzz=lambda: _seq([220, 165], 0.12, 0.2, 0.13, "saw"), pop=lambda: _tone(1319, 0.08, 0.1, "pulse25")),
    "marimba": dict(tick=lambda: _tone(880, 0.25, 0.3, "marimba"), ding=lambda: _seq([523, 659, 784, 1047], 0.09, 0.5, 0.35, "marimba"),
                    buzz=lambda: _seq([196, 185], 0.15, 0.4, 0.35, "marimba"), pop=lambda: _tone(1175, 0.25, 0.3, "marimba")),
    "bell": dict(tick=lambda: _tone(1760, 0.2, 0.12, "bell"), ding=lambda: _seq([1047, 1319, 1568, 2093], 0.1, 0.8, 0.12, "bell"),
                 buzz=lambda: _tone(147, 0.5, 0.15, "organ"), pop=lambda: _tone(2093, 0.3, 0.1, "bell")),
    "fanfare": dict(tick=lambda: _tone(1200, 0.06, 0.12, "triangle"), ding=lambda: _seq([523, 523, 523, 698, 880], 0.1, 0.25, 0.1, "saw"),
                    buzz=lambda: _seq([311, 294, 277, 262], 0.15, 0.25, 0.1, "saw"), pop=lambda: _tone(988, 0.1, 0.1, "triangle")),
    "wood": dict(tick=lambda: _wood(1400), ding=lambda: _seq([784, 1047, 1568], 0.06, 0.6, 0.3, "pluck"),
                 buzz=lambda: _tone(98, 0.3, 0.18, "square"), pop=lambda: _wood(2000)),
}


def _wood(f):
    t = np.arange(int(0.08 * SR)) / SR
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 60) * 0.35).astype(np.float32)
