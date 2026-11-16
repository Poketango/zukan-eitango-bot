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


# ---------- 採掘所の形式（2026-11-16〜）----------
# 横動画の台本 saikutsu/long/NNN/script.json の区切りの行（type: title）に "x" があれば、層ごとに1枚つくる。
#   "x": {"head": 言い切りの一文, "img": [画像の書き方（saikutsu_long.py と同じ）], "bubble": ひとこと, "who": "z" か "m", "post": Xの本文}
#   使い方: python x_cards.py s004 [出力フォルダ]  → sNNN_k.png（k は層の番号）と sNNN_posts.json
LAYER_NO = {"第一層": 1, "第二層": 2, "第三層": 3, "第四層": 4, "第五層": 5, "第六層": 6}


def saikutsu_card(x, sub, title, num):
    import saikutsu_shorts as SS
    import saikutsu_long as SL
    im = SS.background().crop((0, 285, CW, 285 + CH)).convert("RGBA")
    ov = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.rectangle([0, 0, CW, CH], fill=(0, 0, 0, 70)); im.alpha_composite(ov)
    d = ImageDraw.Draw(im)
    # 左上：チャンネル名と層の札
    d.rounded_rectangle([30, 26, 470, 96], 14, fill=(20, 16, 12, 230), outline=(255, 214, 90), width=4)
    d.text((250, 61), "ポケモン雑学採掘所", font=SS.font(SS.F_SUB, 40), fill=(255, 214, 90), anchor="mm")
    lw = d.textlength(sub, font=SS.font(SS.F_HOOK, 44)) + 60
    d.rounded_rectangle([490, 26, 490 + lw, 96], 14, fill=(200, 40, 40, 240))
    d.text((490 + lw / 2, 61), sub, font=SS.font(SS.F_HOOK, 44), fill=(255, 255, 255), anchor="mm")
    d.text((CW - 34, 61), f"第{num}回", font=SS.font(SS.F_SMALL, 34), fill=(230, 220, 200), anchor="rm")
    # 見出し（極太、白に黒の太い縁）
    size = 84
    if "\n" in x["head"]:                       # 改行の位置を台本で決めたとき（単語の途中で切らないため）
        lines = x["head"].split("\n")
        while size > 44 and max(d.textlength(t, font=SS.font(SS.F_HOOK, size)) for t in lines) > CW - 100: size -= 2
    else:
        while size >= 54:
            lines = L.wrap_jp(x["head"], SS.F_HOOK, size, CW - 120)
            if len(lines) <= 3: break
            size -= 4
    y = 130
    for ln in lines:
        SS.stroked(d, (CW // 2, y + size // 2), ln, SS.font(SS.F_HOOK, size), (255, 255, 255), max(8, size // 7), (0, 0, 0))
        y += int(size * 1.3)
    # 中央：話の実物の画像
    top, bottom = y + 24, CH - 330
    refs = x.get("img") or []
    pics = []
    for r in refs:
        ref, _, cap = r.partition("|") if not r.startswith(("row:", "table:")) else (r, "", "")
        a = SL.load(ref)
        if a is not None: pics.append((a, cap))
    if pics:
        n = len(pics); gw = (CW - 100 - 30 * (n - 1)) // n; gh = bottom - top
        for i, (a, cap) in enumerate(pics):
            s_ = min(gw / a.width, (gh - (60 if cap else 0)) / a.height, 3.0)
            a2 = a.resize((max(1, int(a.width * s_)), max(1, int(a.height * s_))), Image.LANCZOS)
            x0 = 50 + i * (gw + 30) + (gw - a2.width) // 2; y0 = top + (gh - (60 if cap else 0) - a2.height) // 2
            if a.getchannel("A").getextrema()[0] == 255:      # 写真は白い縁
                d.rectangle([x0 - 8, y0 - 8, x0 + a2.width + 8, y0 + a2.height + 8], fill=(250, 244, 230))
            im.alpha_composite(a2, (x0, y0))
            if cap:
                f = SS.font(SS.F_SUB, 40); tw = d.textlength(cap, font=f) + 40; cx = 50 + i * (gw + 30) + gw // 2
                d.rounded_rectangle([cx - tw / 2, bottom - 58, cx + tw / 2, bottom - 4], 20, fill=(200, 40, 40))
                d.text((cx, bottom - 31), cap, font=f, fill=(255, 255, 255), anchor="mm")
    # 下の隅：ヘルメット姿の立ち絵と一言
    who = x.get("who", "z"); face = x.get("face", "surprise" if who == "z" else "think")
    t_ = SS.tachie(who, False, 320, face)
    if who == "z": tx = CW - t_.width - 10
    else: tx = 10
    im.alpha_composite(t_, (tx, CH - t_.height))
    bub = x.get("bubble", "")
    if bub:
        f = SS.font(SS.F_SUB, 50)
        while d.textlength(bub, font=f) > 560: f = SS.font(SS.F_SUB, f.size - 4)
        bx0, bx1 = (50, CW - t_.width - 50) if who == "z" else (t_.width + 40, CW - 50)
        by0, by1 = CH - 250, CH - 120
        d.rounded_rectangle([bx0, by0, bx1, by1], 44, fill=(255, 255, 255), outline=(20, 14, 12), width=6)
        col = SS.CH[who]["col"]
        d.text(((bx0 + bx1) // 2, (by0 + by1) // 2), bub, font=f, fill=col, anchor="mm")
    d.text((50 if who == "z" else CW - 50, CH - 50), "YouTube「ポケモン雑学採掘所」", font=SS.font(SS.F_SMALL, 30),
           fill=(230, 220, 200), anchor="lm" if who == "z" else "rm")
    return im.convert("RGB")


def main_saikutsu(num, out):
    import saikutsu_long as SL
    d = os.path.join(L.HERE, "saikutsu", "long", f"{num:03d}")
    SL.DIR = d
    sc = json.load(open(os.path.join(d, "script.json"), encoding="utf-8"))
    os.makedirs(out, exist_ok=True)
    posts = []
    for ln in sc["lines"]:
        x = ln.get("x")
        if ln.get("type") != "title" or not x: continue
        sub = ln.get("sub", ""); k = LAYER_NO.get(sub, len(posts) + 1)
        fn = f"s{num:03d}_{k}.png"
        saikutsu_card(x, sub, ln["t"], num).save(os.path.join(out, fn), optimize=True)
        posts.append({"file": fn, "label": ln["t"], "head": x["head"], "post": x["post"], "jn": x.get("jn", ""), "layer": sub,
                      "deepest": sub == "最深層"})
    json.dump(posts, open(os.path.join(out, f"s{num:03d}_posts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(posts), "枚 →", out)


if __name__ == "__main__":
    a = sys.argv[1]
    if a.startswith("s"): main_saikutsu(int(a[1:]), sys.argv[2] if len(sys.argv) > 2 else "out/x")
    else: main(a, sys.argv[2] if len(sys.argv) > 2 else "out/x")
