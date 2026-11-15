# 「宇宙の衝撃ファイル」（@uchu_shogeki_file）をボットにつなぐ（最初に1回だけ）
#   AUTH_CODE が空なら、承認ページのアドレスを auth_url.txt に書く（アーティファクトで受け取る）
#   AUTH_CODE があれば、リフレッシュトークンに交換し、暗号化して uchu/token.enc に保存する
import os, sys, json, base64, hashlib, urllib.request, urllib.parse
from cryptography.fernet import Fernet

HERE = os.path.dirname(os.path.abspath(__file__))
REDIRECT = "https://poketango.github.io/oauth.html"
SCOPE = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube"


def env(k):
    return "".join((os.environ.get(k) or "").split())


def fernet():
    sec = env("YT_CLIENT_SECRET")
    if not sec: sys.exit("YT_CLIENT_SECRET がありません")
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(("uchu-shogeki:" + sec).encode()).digest()))


def load_token():
    p = os.path.join(HERE, "token.enc")
    if not os.path.exists(p): return None
    return fernet().decrypt(open(p, "rb").read()).decode()


if __name__ == "__main__":
    code = (os.environ.get("AUTH_CODE") or "").strip()
    if not code:
        q = urllib.parse.urlencode({"client_id": env("YT_CLIENT_ID"), "redirect_uri": REDIRECT, "response_type": "code",
                                    "scope": SCOPE, "access_type": "offline", "prompt": "consent select_account"})
        open("auth_url.txt", "w").write("https://accounts.google.com/o/oauth2/v2/auth?" + q)
        print("承認ページのアドレスを auth_url.txt に書きました"); sys.exit(0)
    code = urllib.parse.unquote(code.split("code=")[-1].split("&")[0])
    body = urllib.parse.urlencode({"code": code, "grant_type": "authorization_code", "client_id": env("YT_CLIENT_ID"),
                                   "client_secret": env("YT_CLIENT_SECRET"), "redirect_uri": REDIRECT}).encode()
    try:
        r = json.loads(urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", data=body), timeout=60).read())
    except urllib.error.HTTPError as e:
        sys.exit("交換に失敗しました: " + e.read().decode()[:300])
    rt = r.get("refresh_token")
    if not rt: sys.exit("リフレッシュトークンが返ってきませんでした")
    me = json.loads(urllib.request.urlopen(urllib.request.Request(
        "https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true",
        headers={"Authorization": "Bearer " + r["access_token"]}), timeout=60).read())
    titles = [i["snippet"]["title"] for i in me.get("items", [])]
    print("つながったチャンネル:", titles)
    if "宇宙の衝撃ファイル" not in titles: sys.exit("宇宙の衝撃ファイル以外のチャンネルが選ばれました。承認からやり直してください")
    open(os.path.join(HERE, "token.enc"), "wb").write(fernet().encrypt(rt.encode()))
    print("uchu/token.enc に保存しました")
