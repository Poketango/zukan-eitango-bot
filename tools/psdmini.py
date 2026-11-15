# 最小限のPSD読み込み（8bit RGB、生データ／RLE）。レイヤーの木構造と画像を取り出す
import struct
import numpy as np


class Layer:
    def __init__(self):
        self.name = ""; self.top = self.left = self.bottom = self.right = 0
        self.channels = []; self.opacity = 255; self.visible = True; self.blend = b"norm"
        self.divider = 0; self.children = []; self.parent = None; self.img = None; self.clip = 0

    @property
    def path(self):
        p, n = [], self
        while n is not None and n.name != "<root>":
            p.append(n.name); n = n.parent
        return "/".join(reversed(p))


def _rle_rows(buf, pos, rows, width):
    counts = struct.unpack(">" + "H" * rows, buf[pos:pos + 2 * rows]); pos += 2 * rows
    out = np.zeros((rows, width), np.uint8)
    for r, c in enumerate(counts):
        data = buf[pos:pos + c]; pos += c
        row = bytearray(); i = 0
        while i < len(data) and len(row) < width:
            n = data[i]; i += 1
            if n < 128:
                row += data[i:i + n + 1]; i += n + 1
            elif n > 128:
                row += bytes([data[i]]) * (257 - n); i += 1
        out[r, :min(width, len(row))] = np.frombuffer(bytes(row[:width]), np.uint8)
    return out, pos


def load(path):
    b = open(path, "rb").read()
    assert b[:4] == b"8BPS"
    ch, H, W, depth, mode = struct.unpack(">HIIHH", b[12:26])
    assert depth == 8, depth
    pos = 26
    n = struct.unpack(">I", b[pos:pos + 4])[0]; pos += 4 + n          # color mode
    n = struct.unpack(">I", b[pos:pos + 4])[0]; pos += 4 + n          # image resources
    lm_len = struct.unpack(">I", b[pos:pos + 4])[0]; pos += 4
    li_len = struct.unpack(">I", b[pos:pos + 4])[0]; pos += 4
    count = struct.unpack(">h", b[pos:pos + 2])[0]; pos += 2
    count = abs(count)
    layers = []
    for _ in range(count):
        L = Layer()
        L.top, L.left, L.bottom, L.right = struct.unpack(">iiii", b[pos:pos + 16]); pos += 16
        nc = struct.unpack(">H", b[pos:pos + 2])[0]; pos += 2
        for _ in range(nc):
            cid, clen = struct.unpack(">hI", b[pos:pos + 6]); pos += 6; L.channels.append((cid, clen))
        pos += 4; L.blend = b[pos:pos + 4]; pos += 4
        L.opacity, L.clip, flags = b[pos], b[pos + 1], b[pos + 2]; pos += 4
        L.visible = not (flags & 2)
        extra = struct.unpack(">I", b[pos:pos + 4])[0]; pos += 4; end = pos + extra
        m = struct.unpack(">I", b[pos:pos + 4])[0]; pos += 4 + m        # mask
        m = struct.unpack(">I", b[pos:pos + 4])[0]; pos += 4 + m        # blending ranges
        nl = b[pos]; L.name = b[pos + 1:pos + 1 + nl].decode("cp932", "replace"); pos += ((1 + nl + 3) // 4) * 4
        while pos < end:
            sig, key, ln = b[pos:pos + 4], b[pos + 4:pos + 8], struct.unpack(">I", b[pos + 8:pos + 12])[0]; pos += 12
            data = b[pos:pos + ln]; pos += ln + (ln % 2 if sig == b"8B64" else 0)
            if key == b"luni":
                k = struct.unpack(">I", data[:4])[0]; L.name = data[4:4 + 2 * k].decode("utf-16-be")
            elif key in (b"lsct", b"lsdk"):
                L.divider = struct.unpack(">I", data[:4])[0]
        pos = end
        layers.append(L)
    for L in layers:
        h, w = L.bottom - L.top, L.right - L.left
        chans = {}
        for cid, clen in L.channels:
            comp = struct.unpack(">H", b[pos:pos + 2])[0]; p2 = pos + 2
            if cid == -2 or h <= 0 or w <= 0:
                pos += clen; continue
            if comp == 0:
                arr = np.frombuffer(b[p2:p2 + h * w], np.uint8).reshape(h, w)
            elif comp == 1:
                arr, _ = _rle_rows(b, p2, h, w)
            else:
                raise ValueError("圧縮形式 %d" % comp)
            chans[cid] = arr; pos += clen
        if h > 0 and w > 0 and 0 in chans:
            a = chans.get(-1, np.full((h, w), 255, np.uint8))
            L.img = np.dstack([chans[0], chans.get(1, chans[0]), chans.get(2, chans[0]), a])
    # 木構造（下から順に並んでいる。区切り=3 が開始、1/2 がフォルダ本体）
    root = Layer(); root.name = "<root>"; stack = [root]
    for L in layers:
        if L.divider == 3:
            stack.append(Layer())  # 仮のフォルダ（中身を集める）
            continue
        if L.divider in (1, 2):
            tmp = stack.pop(); L.children = tmp.children
            for c in L.children: c.parent = L
        L.parent = stack[-1]; stack[-1].children.append(L)
    return root, W, H


def walk(node, depth=0):
    for c in reversed(node.children):            # 上のレイヤーから
        yield c, depth
        if c.children: yield from walk(c, depth + 1)


def compose(root, W, H, choose):
    """choose(layer) -> True/False/None（None はPSDの表示状態に従う）。下から順に重ねる"""
    canvas = np.zeros((H, W, 4), np.float32)

    def blend(dst, L, alpha_mul=1.0):
        if L.img is None: return
        t, l = L.top, L.left; h, w = L.img.shape[:2]
        y0, x0, y1, x1 = max(0, t), max(0, l), min(H, t + h), min(W, l + w)
        if y0 >= y1 or x0 >= x1: return
        src = L.img[y0 - t:y1 - t, x0 - l:x1 - l].astype(np.float32) / 255
        a = src[..., 3:4] * (L.opacity / 255) * alpha_mul
        d = dst[y0:y1, x0:x1]
        rgb = src[..., :3]
        if L.blend == b"mul ": rgb = rgb * np.where(d[..., 3:4] > 0, d[..., :3], 1)
        outa = a + d[..., 3:4] * (1 - a)
        d[..., :3] = np.where(outa > 0, (rgb * a + d[..., :3] * d[..., 3:4] * (1 - a)) / np.maximum(outa, 1e-6), 0)
        d[..., 3:4] = outa

    def vis(L):
        c = choose(L)
        return L.visible if c is None else c

    def render(node, dst):
        base_alpha = None
        for L in node.children:          # 下から
            if not vis(L): continue
            if L.children:
                sub = np.zeros_like(dst); render(L, sub)
                tmp = Layer(); tmp.img = (sub * 255).astype(np.uint8); tmp.opacity = L.opacity; tmp.blend = b"norm"
                blend(dst, tmp); continue
            if L.clip and base_alpha is not None:
                before = dst.copy(); blend(dst, L)
                # クリッピング：下のレイヤーの形の中だけ
                m = base_alpha
                dst[:] = before * (1 - m) + dst * m
            else:
                blend(dst, L)
                if L.img is not None:
                    base_alpha = np.zeros((H, W, 1), np.float32)
                    t, l = L.top, L.left; h, w = L.img.shape[:2]
                    y0, x0, y1, x1 = max(0, t), max(0, l), min(H, t + h), min(W, l + w)
                    base_alpha[y0:y1, x0:x1, 0] = L.img[y0 - t:y1 - t, x0 - l:x1 - l, 3] / 255
    render(root, canvas)
    return (canvas * 255).clip(0, 255).astype(np.uint8)


def selector(picks):
    """picks: {'フォルダ名': '選ぶ子の名前'}。'!' で始まるフォルダは1つだけ表示（PSDToolの決まり）"""
    def choose(L):
        par = L.parent
        if par is not None and par.name.lstrip("!*") in picks:
            want = picks[par.name.lstrip("!*")]
            names = want if isinstance(want, (list, tuple)) else [want]
            return L.name.lstrip("*") in names
        if L.name.lstrip("!*") in picks and picks[L.name.lstrip("!*")] is False: return False
        return None
    return choose
