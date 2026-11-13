# 雑学チャンネル（@poke_zatsugaku）をボットにつなぐ（最初に1回だけ）
#   承認コードを、今のチャンネルと同じアプリの鍵でリフレッシュトークンに交換し、
#   アプリの鍵から作った暗号鍵で暗号化して yt2_token.enc に保存する（鍵そのものはリポジトリに置かない）
import os, sys, json, base64, hashlib, urllib.request, urllib.parse
from cryptography.fernet import Fernet


def fernet():
    sec = "".join((os.environ.get("YT_CLIENT_SECRET") or "").split())
    if not sec: sys.exit("YT_CLIENT_SECRET がありません")
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(("poke-zatsugaku:" + sec).encode()).digest()))


def load_token():
    """zatsugaku.py から呼ぶ。保存済みのリフレッシュトークンを返す（無ければ None）"""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yt2_token.enc")
    if not os.path.exists(p) or not os.environ.get("YT_CLIENT_SECRET"): return None
    try: return fernet().decrypt(open(p, "rb").read()).decode()
    except Exception as e: print("yt2_token.enc を読めませんでした:", type(e).__name__); return None


if __name__ == "__main__":
    code = (os.environ.get("AUTH_CODE") or "").strip()
    code = urllib.parse.unquote(code.split("code=")[-1].split("&")[0])   # アドレス欄ごと貼られても大丈夫にする
    if not code: sys.exit("承認コードが空です")
    body = urllib.parse.urlencode({
        "code": code, "grant_type": "authorization_code",
        "client_id": "".join(os.environ["YT_CLIENT_ID"].split()), "client_secret": "".join(os.environ["YT_CLIENT_SECRET"].split()),
        "redirect_uri": os.environ.get("REDIRECT_URI", "https://poketango.github.io/oauth.html")}).encode()
    try:
        r = json.loads(urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", data=body), timeout=60).read())
    except urllib.error.HTTPError as e:
        sys.exit("交換に失敗しました: " + e.read().decode()[:300])
    rt = r.get("refresh_token")
    if not rt: sys.exit("リフレッシュトークンが返ってきませんでした（もう一度、承認からやり直してください）")
    # どのチャンネルにつながったか確認する
    at = r["access_token"]
    try:
        me = json.loads(urllib.request.urlopen(urllib.request.Request(
            "https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true", headers={"Authorization": "Bearer " + at}), timeout=60).read())
        print("つながったチャンネル:", [i["snippet"]["title"] for i in me.get("items", [])])
    except Exception as e:
        print("チャンネル名の確認はできませんでした:", type(e).__name__)
    open("yt2_token.enc", "wb").write(fernet().encrypt(rt.encode()))
    print("yt2_token.enc に保存しました")
