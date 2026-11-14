# X（@zukan_eitango）に投稿する雑学カード画像を作る
#   横動画の台本 scripts/long/NNNN.json の各話題に "x" があれば、1話題につき1枚、縦長（1080x1350）の画像を作る。
#   "x": {"head": "画像の上に大きく出す一文（言い切り）", "img": ["art:25", "bars:..."], "bubble": "ずんだもんのひとこと",
#         "post": "Xの本文（画像と同じ話を、問いかけで締める。リンク・ハッシュタグは入れない）"}
#   使い方: python x_cards.py 0003 [出力フォルダ]   → 出力フォルダ/NNNN_k.png と posts.json（本文の一覧）
import os, sys, json
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zatsugaku_long as L

CW, CH = 1080, 1350


def card(x, label, theme_i=0):
    th = L.THEMES[theme_i % len(L.THEMES)]
    im = L.burst((CW, CH), tuple(int(c * 0.75) for c in th[0]), th[0], n=30, center=(CW / 2, CH * 0.55)).convert("RGBA")
    d = ImageDraw.Draw(im)
    # 左上の帯
    d.polygon([(0, 0), (560, 0), (510, 92), (0, 92)], fill=(230, 20, 30))
    d.text((32, 46), "ポケモン雑学", font=L.F(L.FONT_K, 54), fill=(255, 255, 255), anchor="lm")
    d.text((CW - 30, 46), label, font=L.FF(L.FR, 34), fill=(255, 255, 255), anchor="rm")
    # 見出し（言い切りの一文）
    lines, size = None, 84
    while size >= 56:
        lines = L.wrap_jp(x["head"], L.FD, size, CW - 110)
        if len(lines) <= 3: break
        size -= 6
    y = 150
    for ln in lines:
        L.outlined(im, (CW // 2, y + size // 2), ln, size, (255, 255, 255), w1=10, w2=22, font=L.FD)
        y += int(size * 1.28)
    # 画像の枠
    top = y + 30; bottom = CH - 250
    d.rounded_rectangle([50, top, CW - 50, bottom], 40, fill=(255, 255, 255), outline=(20, 14, 30), width=8)
    refs = x.get("img") or []
    ims = [L.load_img(r.split("|")[0]) for r in refs]
    caps = [r.split("|")[1] if "|" in r else "" for r in refs]
    pairs = [(a, c, r) for a, c, r in zip(ims, caps, refs) if a is not None]
    if pairs:
        n = len(pairs); gw = (CW - 160) // n; gh = bottom - top - 60 - (60 if any(c for _, c, _ in pairs) else 0)
        for i, (a, c, r) in enumerate(pairs):
            a = L.fit(a, gw - 20, gh, r.split(":")[0] in L.PIXEL_KINDS)
            cx = 80 + gw * i + gw // 2
            im.alpha_composite(a, (int(cx - a.width / 2), int(top + 30 + (gh - a.height) / 2)))
            if c:
                f = L.F(L.FONT_K, 40)
                tw = f.getlength(c) + 40
                d.rounded_rectangle([cx - tw / 2, bottom - 80, cx + tw / 2, bottom - 26], 22, fill=(230, 20, 30))
                d.text((cx, bottom - 53), c, font=f, fill=(255, 255, 255), anchor="mm")
    # 下：ずんだもんとふきだし
    z = L.face("zundamon", 300)
    im.alpha_composite(z, (20, CH - z.height))
    bub = x.get("bubble") or "知らなかったのだ！"
    bs = 52
    while L.F(L.FONT_K, bs).getlength(bub) > 560: bs -= 4
    bx0, by0, bx1, by1 = 330, CH - 200, CW - 50, CH - 70
    d.rounded_rectangle([bx0, by0, bx1, by1], 50, fill=(255, 255, 255), outline=(20, 14, 30), width=7)
    d.polygon([(bx0 + 4, by0 + 50), (bx0 - 50, by0 + 90), (bx0 + 4, by0 + 90)], fill=(255, 255, 255), outline=(20, 14, 30))
    d.rectangle([bx0 - 2, by0 + 52, bx0 + 8, by0 + 88], fill=(255, 255, 255))
    d.text(((bx0 + bx1) // 2, (by0 + by1) // 2), bub, font=L.F(L.FONT_K, bs), fill=(20, 14, 30), anchor="mm")
    d.text((CW - 40, CH - 28), "YouTube「ずんだもんと冥鳴ひまりのポケモン雑学」", font=L.FF(L.FR, 26), fill=(255, 255, 255), anchor="rm")
    return im.convert("RGB")


def main(num, out):
    sc = json.load(open(os.path.join(L.HERE, "scripts", "long", f"{num}.json"), encoding="utf-8"))
    os.makedirs(out, exist_ok=True)
    posts = []
    for k, tp in enumerate(sc["topics"], 1):
        x = tp.get("x")
        if not x: continue
        fn = f"{num}_{k}.png"
        card(x, tp["label"], k).save(os.path.join(out, fn), optimize=True)
        posts.append({"file": fn, "label": tp["label"], "post": x["post"], "jn": tp["jn"]})
    json.dump(posts, open(os.path.join(out, f"{num}_posts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(posts), "枚 →", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "out/x")
