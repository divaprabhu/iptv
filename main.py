import time
import re
import logging
import sqlite3
from datetime import datetime
from dataclasses import dataclass

import yt_dlp

PATTERN = r'[^a-zA-Z0-9]'
MEDIA_FOLDER = "/data/media/tv"
DEBUG=False

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)

YTDL_OPTIONS = {
    "quiet": False if DEBUG else True,
    "no_warnings": False if DEBUG else True,
    "skip_download": True,   # don’t download video
    "extract_flat": True,    # don’t go deep into formats,
    "extractor_args": {
        "youtube": {
            "player_client": ["mweb", "android", "ios", "tv", "web_embedded"]
        }
    },
}

@dataclass
class IPTVLog:
    name: str = ""
    playlist_url: str = ""
    episode_url: str = ""
    index: str = ""
    status: str = ""
    error: str = ""
    create_date: str = ""
    
YT_LIST = [
    # { "name": "Cartoon Network", "url": "https://www.youtube.com/@cnindia/videos", "index": "1-2",  },
    { "name": "Bajarangi", "url": "https://www.youtube.com/playlist?list=PLUX4fpHUux5UEb5xXQ8cBJxba-s6rvPn3", "index": "1-2", },
    { "name": "Bheem", "url": "https://www.youtube.com/@greengoldtv/videos", "index": "1-2", },
    { "name": "Bhoot Boss", "url": "https://www.youtube.com/@PapoNewChannel/videos", "index": "1-2", },
    # { "name": "Curios George", "url": "https://www.youtube.com/@CuriousGeorge/videos", "index": "1-2", },
    { "name": "Detective Mehul", "url": "https://www.youtube.com/@DetectiveMehul.English/videos", "index": "1-2", },
    { "name": "Jungle Book", "url": "https://www.youtube.com/playlist?list=PL51JScfFH33_cVp25i8NBbqPzkEiQ9mTZ", "index":"-12:-15:-1", },
    # { "name": "Kanha", "url": "https://www.youtube.com/playlist?list=PL2XOPpYaVR49Yox7zeyfLSGAcphS0vkxR", "index": "1-2", },
    # { "name": "Krishna", "url": "https://www.youtube.com/playlist?list=PLdhxSHmOPfNQjNcHaHwOmIYv5z1bUbZJS", "index": "1-2", },
    { "name": "Masha and the Bear", "url": "https://www.youtube.com/@MashaBearEN/videos", "index": "1-2", },
    { "name": "Pinaki", "url": "https://www.youtube.com/@BhootBandhus_SonicGang/videos", "index": "1-2", },
    # { "name": "Titoo", "url": "https://www.youtube.com/playlist?list=PLdhxSHmOPfNSHsuxsnjuL3BOsPGXuMDie", "index": "1-2", },
    # { "name": "Wow", "url": "https://www.youtube.com/@WowKidzOfficialTV/videos", "index": "1-2", },
]


def process_youtube_playlist(iptv: IPTVLog):
    video_id = None
    ytdl_opts = dict(YTDL_OPTIONS)
    ytdl_opts["match_filter"] = yt_dlp.utils.match_filter_func("duration >= 300 & live_status!=is_upcoming")
    ytdl_opts["playlist_items"] = iptv.index

    logger.debug(f"OPTIONS: {ytdl_opts}")

    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        info = ydl.extract_info(iptv.playlist_url, download=False)
        entries = info.get("entries") or []
                
        video_ids = [entry['id'] for entry in entries]
        logger.info(f"Video IDs: {video_ids}")

    if not video_ids:
        logger.info("===> Could not extract video id")
        iptv.status = "ERROR"
        iptv.error = "Could not extract video ids"
        return

    ytdl_opts = dict(YTDL_OPTIONS)
    ytdl_opts["format"] = "best"  # equivalent of -f
    ytdl_opts["outtmpl"] = f"{MEDIA_FOLDER}/{iptv.name}.mp4"  # equivalent of -o
    ytdl_opts["overwrites"] =  True,      # force overwrite existing files
    ytdl_opts["ignoreerrors"] = True,   # skip unavailable/private/deleted videos
    ytdl_opts.pop("skip_download", None)
    
    for video_id in video_ids:
        iptv.episode_url = f"https://www.youtube.com/watch?v={video_id}"
        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            rc = ydl.download(iptv.episode_url)
            if rc == 0:
                logger.info("===> Completed Download")
                iptv.status = "SUCCESS"
                break
            else:
                logger.info(f"===> Download failed with return code: {rc}")
                iptv.status = "ERROR"
                iptv.error += f"\n{video_id}: Download failed with return code: {rc}"

if __name__ == "__main__":
    logger.info("Starting the process\n")

    today = datetime.today().strftime("%Y-%m-%d")
    con = sqlite3.connect("iptv/iptv.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS iptv_log(
       id INTEGER PRIMARY KEY,
       name TEXT NOT NULL,
       playlist_url TEXT NOT NULL,
       episode_url TEXT,
       list_index TEXT,
       status TEXT NOT NULL,
       error TEXT,
       create_date TEXT NOT NULL,
       create_time TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    for show in YT_LIST:
        iptv = IPTVLog()
        try:
            clean_name = re.sub(PATTERN, '', show["name"])
            file_path = f"{MEDIA_FOLDER}/{clean_name}.mp4"
            iptv.name = clean_name
            iptv.playlist_url = show["url"]
            iptv.index = str(show["index"])
            iptv.create_date = today
            iptv.error = ""

            logger.info(f"Name: {iptv.name} Playlist: {iptv.playlist_url} Index: {iptv.index}")
            process_youtube_playlist(iptv)
            time.sleep(10)
        except Exception as e:
            logger.error(f"{iptv.name} {iptv.episode_url} {e}")
            iptv.status = "EXCEPTION"
            iptv.error = f"{e}"
        finally:
            cur.execute(
                "INSERT INTO iptv_log(name, playlist_url, episode_url, list_index, status, error, create_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (iptv.name, iptv.playlist_url, iptv.episode_url, iptv.index, iptv.status, iptv.error if iptv.error else None , iptv.create_date)
            )

    con.commit()
    con.close()
