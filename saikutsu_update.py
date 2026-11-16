# 投稿済み（予約中も含む）の採掘所の横動画の、タイトル・概要欄・サムネイルを直す（2026-11-17）
#   saikutsu/long/NNN/update.json を push すると動く。{"title": 新しいタイトル（任意）, "description": 新しい概要欄（任意）, "thumb": true（台本の thumb からサムネを作り直して設定）}
#   動画IDは posted_saikutsu_long.json の記録から取る。公開予約の時刻と公開設定は変えない
import os, json, datetime
import saikutsu_long as SL
import link_channel

HERE = os.path.dirname(os.path.abspath(__file__))
num = int(os.environ["NUM"]); d = os.path.join(HERE, "saikutsu", "long", f"{num:03d}")
u = json.load(open(os.path.join(d, "update.json"), encoding="utf-8"))
LOG = os.path.join(HERE, "posted_saikutsu_long.json")
log = json.load(open(LOG, encoding="utf-8"))
rec = [x for x in log if x.get("num") == num and x.get("id")][-1]
vid = rec["id"]
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
rt = "".join((os.environ.get("YT2_REFRESH_TOKEN") or "").split()) or link_channel.load_token()
cred = Credentials(None, refresh_token=rt, token_uri="https://oauth2.googleapis.com/token",
                   client_id="".join(os.environ["YT_CLIENT_ID"].split()), client_secret="".join(os.environ["YT_CLIENT_SECRET"].split()))
yt = build("youtube", "v3", credentials=cred)
if u.get("title") or u.get("description"):
    v = yt.videos().list(part="snippet", id=vid).execute()["items"][0]
    sn = v["snippet"]
    body = {"id": vid, "snippet": {"title": (u.get("title") or sn["title"])[:100], "description": u.get("description") or sn.get("description", ""),
                                   "categoryId": sn.get("categoryId", "20"), "tags": sn.get("tags", []),
                                   "defaultLanguage": sn.get("defaultLanguage", "ja"), "defaultAudioLanguage": sn.get("defaultAudioLanguage", "ja")}}
    yt.videos().update(part="snippet", body=body).execute()
    print("タイトルを直しました:", vid, body["snippet"]["title"])
    if u.get("title"):
        rec["title"] = u["title"]; rec["retitled_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        json.dump(log, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
if u.get("thumb"):
    SL.DIR = d
    os.makedirs("out", exist_ok=True)
    SL.thumbnail(d, "out")
    yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(os.path.join("out", "thumbnail.png"))).execute()
    print("サムネイルを設定しました:", vid)
