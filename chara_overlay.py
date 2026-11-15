# クイズのショートの右下に、しゃべるずんだもん（坂本アヒル様の立ち絵・表情差分）を小さく置く（2026-11-15）
#   ・話している間だけ口を動かし、せりふごとに表情を変える
#   ・右下の隅（x>790, y>1560）に収める。画面の文字や図はこの範囲を避けて置く
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100
H = 360                       # 立ち絵の高さ（頭から腰まで）
_C = {}


def _img(face, open_):
    k = (face, open_)
    if k not in _C:
        p = os.path.join(HERE, "chara", f"zundamon_h_{face}{'_open' if open_ else ''}.png")
        if not os.path.exists(p): p = os.path.join(HERE, "chara", "zundamon_h" + ("_open" if open_ else "") + ".png")
        im = Image.open(p).convert("RGBA")
        im = im.crop((0, 0, im.width, int(im.height * 0.62)))
        _C[k] = im.resize((round(im.width * H / im.height), H), Image.LANCZOS)
    return _C[k]


class Talker:
    def __init__(self):
        self.talks = []              # (始まり, 終わり, 表情)

    def add(self, t0, v, face="normal"):
        if v is None: return
        self.talks.append((t0, t0 + len(v) / SR, face))

    def draw(self, im, T, W=1080, Hh=1920):
        face, talking = "normal", False
        for t0, t1, f in self.talks:
            if T >= t0 - 0.05: face = f
            if t0 <= T < t1: talking = True
        th = _img(face, talking and int(T * 9) % 2 == 0)
        bob = int(abs(np.sin(T * 7)) * 6) if talking else 0
        im = im.convert("RGB")
        im.paste(th, (W - th.width + 30, Hh - th.height + 24 - bob), th)
        return im
