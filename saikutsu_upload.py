# 採掘所の横動画をアップロードする（ユーザーが確認してから手動で動かす）
#   render-saikutsu-NNN ブランチの動画（分割）とサムネイル、saikutsu/long/NNN/upload.json（title, description, tags, publishAt 任意）を使う
#   記録は posted_saikutsu_long.json。記録済みの回は二度上げない
import os, sys, json, glob, datetime, subprocess
import link_channel

HERE = os.path.dirname(os.path.abspath(__file__))
num = int(os.environ["NUM"]); d = os.path.join(HERE, "saikutsu", "long", f"{num:03d}")
src = sys.argv[1]                      # render ブランチを取り出したフォルダ
LOG = os.path.join(HERE, "posted_saikutsu_long.json")
log = json.load(open(LOG, encoding="utf-8")) if os.path.exists(LOG) else []
if any(x.get("num") == num and x.get("id") for x in log): sys.exit(f"第{num}回は投稿済みです")
m = json.load(open(os.path.join(d, "upload.json"), encoding="utf-8"))
mp4 = "upload.mp4"
subprocess.run("cat " + " ".join(sorted(glob.glob(os.path.join(src, "saikutsu_long.mp4.part-*")))) + f" > {mp4}", shell=True, check=True)
desc = m["description"]
cr = os.path.join(src, "credits.json")
if os.path.exists(cr):                 # 画像の出典を、入るだけ足す
    lines = sorted(set(json.load(open(cr, encoding="utf-8")).values()))
    add = "\n\n画像の出典（ウィキペディア・ウィキメディア・コモンズ ほか）\n"
    for l in lines:
        if len(desc) + len(add) + len(l) + 2 > 4900: add += "ほか"; break
        add += "・" + l + "\n"
    desc += add
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
rt = "".join((os.environ.get("YT2_REFRESH_TOKEN") or "").split()) or link_channel.load_token()
if not rt: sys.exit("採掘所のチャンネルの鍵がありません")
cred = Credentials(None, refresh_token=rt, token_uri="https://oauth2.googleapis.com/token",
                   client_id="".join(os.environ["YT_CLIENT_ID"].split()), client_secret="".join(os.environ["YT_CLIENT_SECRET"].split()))
yt = build("youtube", "v3", credentials=cred)
me = yt.channels().list(part="snippet", mine=True).execute()
print("アップロード先:", [i["snippet"]["title"] for i in me.get("items", [])])
status = {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
if m.get("publishAt"):
    t = datetime.datetime.fromisoformat(m["publishAt"])
    if t > datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10):
        status = {"privacyStatus": "private", "publishAt": t.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "selfDeclaredMadeForKids": False}
body = {"snippet": {"title": m["title"][:100], "description": desc[:4950], "categoryId": "20", "defaultLanguage": "ja", "defaultAudioLanguage": "ja",
                    "tags": m.get("tags", [])}, "status": status}
r = yt.videos().insert(part="snippet,status", body=body,
                       media_body=MediaFileUpload(mp4, mimetype="video/mp4", resumable=True, chunksize=8 << 20)).execute()
vid = r["id"]; print("アップロードしました:", vid, r["status"].get("privacyStatus"), r["status"].get("publishAt"))
th = os.path.join(src, "thumbnail.png")
if os.path.exists(th):
    try: yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(th)).execute(); print("サムネイルを設定しました")
    except Exception as e: print("サムネイルを設定できませんでした:", str(e)[:200])
log.append({"num": num, "title": m["title"], "id": vid, "publishAt": r["status"].get("publishAt"),
            "at": datetime.datetime.now(datetime.timezone.utc).isoformat()})
json.dump(log, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open("video_id.txt", "w").write(vid)
