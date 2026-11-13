# 投稿済みの週末まとめ動画に、台本のサムネイルを付け直す（手動で実行）
import os, sys, json, re
import zatsugaku_long as L
import link_channel

vid, week = os.environ["VIDEO_ID"].strip(), int(os.environ["WEEK"])
sc = json.load(open(os.path.join(L.HERE, "scripts", "long", f"{week:04d}.json"), encoding="utf-8"))
L.thumb(sc).save("thumb_long.jpg", quality=92)
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
cred = Credentials(None, refresh_token=link_channel.load_token(), token_uri="https://oauth2.googleapis.com/token",
                   client_id="".join(os.environ["YT_CLIENT_ID"].split()), client_secret="".join(os.environ["YT_CLIENT_SECRET"].split()))
yt = build("youtube", "v3", credentials=cred)
yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload("thumb_long.jpg")).execute()
print("サムネイルを設定しました:", vid)
