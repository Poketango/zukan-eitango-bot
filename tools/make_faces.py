import sys, os
sys.path.insert(0, '/home/claude')
import psdmini as P
from PIL import Image
OUT = '/home/claude/poketango/zukan-eitango-bot/chara'
Z = {  # 表情: (共通の部品, 口を閉じた形, 口を開けた形)
 'normal':  (dict(眉='普通眉', 目='目セット', 目セット=['!黒目', '普通白目'], 黒目='普通目'), 'むふ', 'ほあ'),
 'happy':   (dict(眉='普通眉', 目='にっこり'), 'むふ', 'ほあー'),
 'proud':   (dict(眉='上がり眉', 目='細め目'), 'むふ', 'ほあー'),
 'surprise':(dict(眉='上がり眉', 目='目セット', 目セット=['!黒目', '見開き白目'], 黒目='普通目'), 'お', 'んあー'),
 'sad':     (dict(眉='困り眉1', 目='目セット', 目セット=['!黒目', '普通白目'], 黒目='目逸らし'), 'んー', 'んへー'),
 'shock':   (dict(眉='困り眉2', 目='〇〇', 顔色=['ほっぺ', '青ざめ'], 記号など=['汗1']), '△', 'んあー'),
 'think':   (dict(眉='困り眉1', 目='目セット', 目セット=['!黒目', '普通白目'], 黒目='目逸らし2'), 'ゆ', 'お'),
}
MA = dict(左腕='普通', 右腕='普通')
M = {
 'normal':  (dict(眉='ごきげん', 目='目セット', 目セット=['!黒目', '普通白目'], 黒目='カメラ目線'), 'ほほえみ', 'わあー'),
 'happy':   (dict(眉='ごきげん', 目='目閉じ'), 'ほほえみ', '▽'),
 'proud':   (dict(眉='ややおこ', 目='目セット', 目セット=['!黒目', '普通白目'], 黒目='目そらし'), 'にやり', 'わあー'),
 'surprise':(dict(眉='こまり', 目='目セット', 目セット=['!黒目', '見開き白目'], 黒目='カメラ目線'), 'お', 'わあー'),
 'sad':     (dict(眉='こまり', 目='目セット', 目セット=['!黒目', '普通白目'], 黒目='目そらし'), 'む', 'うえー'),
 'shock':   (dict(眉='こまり', 目='○○', 顔色=['青ざめ'], 記号など=['汗']), '△', 'うえー'),
 'think':   (dict(眉='こまり', 目='見上げ', 左腕='口元に指', 右腕='普通'), 'ゆ', 'む'),
}
def build(psd, table, helmet, prefix, preview_crop, arms=None):
    global ARMS; ARMS = arms or {}
    root, W, H = P.load(psd)
    hel = Image.open(helmet).convert('RGBA')
    tiles = []
    for name, (base, mc, mo) in table.items():
        for mouth, suf in ((mc, ''), (mo, '_open')):
            picks = dict(ARMS); picks.update(base); picks['口'] = mouth
            im = Image.fromarray(P.compose(root, W, H, P.selector(picks)), 'RGBA')
            im.alpha_composite(hel)
            small = im.resize((round(W * 0.65), round(H * 0.65)), Image.LANCZOS)
            small.save(f'{OUT}/{prefix}_{name}{suf}.png', optimize=True)
            if suf == '': tiles.append((name, im.crop(preview_crop).resize((220, 400))))
    return tiles
tz = build('/tmp/zt/ずんだもん立ち絵素材2.3.psd', Z, '/mnt/user-data/uploads/Downloads/helmet_z.png', 'zundamon_h', (240, 60, 840, 1140))
tm = build('/tmp/mt/metan.psd', M, '/mnt/user-data/uploads/Downloads/helmet_m.png', 'metan_h', (240, 20, 840, 1100), MA)
from PIL import ImageDraw, ImageFont
f = ImageFont.truetype('/home/claude/poketango/zukan-eitango-bot/fonts/MPLUSRounded1c-ExtraBold.ttf', 22)
o = Image.new('RGB', (230 * 7, 2 * 430), (70, 60, 50)); d = ImageDraw.Draw(o)
for r, tiles in enumerate((tz, tm)):
    for i, (n, t) in enumerate(tiles):
        o.paste(t, (i * 230, r * 430), t); d.text((i * 230 + 6, r * 430 + 224), n, font=f, fill='white')
o.save('/tmp/faces.jpg')
