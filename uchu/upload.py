# 宇宙の衝撃ファイル：uchu-queue ブランチの queue/NNN_*.mp4 と .json をアップロードする
#   json: {"title":..., "description":..., "tags":[...], "publishAt":"2026-11-16T12:05:00+09:00"(任意。無ければすぐ公開)}
import os, sys, json, glob, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import link

Q = sys.argv[1] if len(sys.argv) > 1 else "queue"
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "posted.jsonl")


def yt():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    rt = link.load_token()
    if not rt: sys.exit("まだチャンネルにつながっていません（uchu/token.enc がない）")
    cred = Credentials(None, refresh_token=rt, token_uri="https://oauth2.googleapis.com/token",
                       client_id=link.env("YT_CLIENT_ID"), client_secret=link.env("YT_CLIENT_SECRET"))
    return build("youtube", "v3", credentials=cred)


if __name__ == "__main__":
    from googleapiclient.http import MediaFileUpload
    items = sorted(glob.glob(os.path.join(Q, "*.json")))
    if not items: print("投稿待ちはありません"); sys.exit(0)
    api = yt()
    done = set()
    try: done = {json.loads(l)["file"] for l in open(LOG, encoding="utf-8") if l.strip()}
    except FileNotFoundError: pass
    for j in items:
        base = os.path.basename(j)[:-5]
        mp4 = j[:-5] + ".mp4"
        if base in done: print("投稿済みなので飛ばす:", base); continue
        if not os.path.exists(mp4): print("動画がない:", mp4); continue
        m = json.load(open(j, encoding="utf-8"))
        status = {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        if m.get("publishAt"):
            t = datetime.datetime.fromisoformat(m["publishAt"])
            if t > datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10):
                status = {"privacyStatus": "private", "publishAt": t.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                          "selfDeclaredMadeForKids": False}
        body = {"snippet": {"title": m["title"][:100], "description": m["description"][:4900], "categoryId": "28",
                            "defaultLanguage": "ja", "defaultAudioLanguage": "ja",
                            "tags": m.get("tags") or ["宇宙", "NASA", "科学", "実話", "shorts"]},
                "status": status}
        r = api.videos().insert(part="snippet,status", body=body,
                                media_body=MediaFileUpload(mp4, mimetype="video/mp4", resumable=True, chunksize=8 << 20)).execute()
        print("アップロードしました:", base, r.get("id"), r["status"].get("privacyStatus"), r["status"].get("publishAt"))
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({"file": base, "id": r.get("id"), "title": m["title"], "publishAt": r["status"].get("publishAt"),
                                "at": datetime.datetime.now(datetime.timezone.utc).isoformat()}, ensure_ascii=False) + "\n")
