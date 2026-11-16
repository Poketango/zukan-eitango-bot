# 効果音を「起きた瞬間」だけに鳴らすための共通の部品（2026-11-16 同系統ショート300本の分析で決めた作法）
#   ・冒頭の一発目と答え・結末 = impact（低い衝撃音）
#   ・画像や場面の切り替え     = whoosh（シュッ）
#   ・赤い丸や札が出た瞬間     = pop（ポン）
#   ・謎が解けた瞬間           = idea（キラーン）
#   ・画面いっぱいの大きな一言 = boom
#   字幕ごとには鳴らさない。30秒あたり6〜10個までにし、多いときは pop → whoosh の順に間引く
# 素材は OtoLogic（https://otologic.jp, CC BY 4.0）。使った動画の概要欄に「効果音：OtoLogic（https://otologic.jp）」を書く
import os, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SE_DIR = os.path.join(HERE, "assets", "se")
CREDIT = "効果音：OtoLogic（https://otologic.jp）"
# 種類: (ファイル名, 音の山の位置 秒, 音量の倍率, 使う長さ 秒)
KIND = {"impact": ("impact", 0.13, 0.55, 2.0), "whoosh": ("whoosh", 0.19, 0.38, 1.0), "pop": ("pop", 0.0, 0.28, 0.5),
        "idea": ("idea", 0.0, 0.5, 1.4), "boom": ("boom", 0.2, 0.55, 2.4), "hit": ("hit", 0.15, 0.4, 1.2)}
PRIORITY = {"impact": 0, "boom": 0, "idea": 1, "hit": 2, "whoosh": 3, "pop": 4}   # 小さいほど残す
_cache = {}


def load(kind, sr):
    key = (kind, sr)
    if key not in _cache:
        name, peak, gain, dur = KIND[kind]
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", os.path.join(SE_DIR, name + ".mp3"), "-t", str(dur),
                              "-f", "s16le", "-ac", "1", "-ar", str(sr), "-"], capture_output=True, check=True).stdout
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
        f = min(len(x), int(0.25 * sr)); x[-f:] *= np.linspace(1, 0, f)
        _cache[key] = (x * gain, peak)
    return _cache[key]


def thin(events, total, per30=10, gap=1.2):
    """多すぎるときに間引く。近すぎる（gap秒未満）ものは優先度の低い方を落とし、30秒あたり per30 個に収める"""
    ev = sorted(events, key=lambda e: e[0]); keep = []
    for e in ev:
        if keep and e[0] - keep[-1][0] < gap:
            if PRIORITY[e[1]] < PRIORITY[keep[-1][1]]: keep[-1] = e
            continue
        keep.append(e)
    limit = max(4, int(per30 * total / 30))
    while len(keep) > limit:
        worst = max(range(len(keep)), key=lambda k: (PRIORITY[keep[k][1]], -k)); keep.pop(worst)
    return keep


def add(mix, events, sr):
    """events = [(鳴らしたい瞬間 秒, 種類)]。音の山がその瞬間に来るように重ねる"""
    for t, kind in events:
        x, peak = load(kind, sr)
        a = max(0, int((t - peak) * sr)); b = min(len(mix), a + len(x))
        if b > a: mix[a:b] += x[:b - a]
    return mix
