import time
import re
import logging
import sqlite3
from datetime import datetime
from dataclasses import dataclass

import yt_dlp

PATTERN = r'[^a-zA-Z0-9]'
MEDIA_FOLDER = "/data/media/tv"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class IPTVLog:
    name: str = ""
    playlist_url: str = ""
    episode_url: str = ""
    reverse: str = ""
    status: str = ""
    error: str = ""
    create_date: str = ""
    
YT_LIST = [
    # { "name": "Cartoon Network", "url": "https://www.youtube.com/@cnindia/videos", "reverse": False },
    { "name": "Bajarangi", "url": "https://www.youtube.com/playlist?list=PLUX4fpHUux5UEb5xXQ8cBJxba-s6rvPn3", "reverse": False },
    { "name": "Bheem", "url": "https://www.youtube.com/@greengoldtv/videos", "reverse": False },
    { "name": "Bhoot Boss", "url": "https://www.youtube.com/@PapoNewChannel/videos", "reverse": False },
    # { "name": "Curios George", "url": "https://www.youtube.com/@CuriousGeorge/videos", "reverse": False },
    { "name": "Detective Mehul", "url": "https://www.youtube.com/@DetectiveMehul.English/videos", "reverse": False },
    # { "name": "Jungle Book", "url": "https://www.youtube.com/playlist?list=PLHLxDf0gJGDmhX1Udjkn2fSkWarksUzVe","reverse": False },
    { "name": "Jungle Book", "url": "https://www.youtube.com/playlist?list=PL51JScfFH33_cVp25i8NBbqPzkEiQ9mTZ","reverse": True },
    # { "name": "Kanha", "url": "https://www.youtube.com/playlist?list=PL2XOPpYaVR49Yox7zeyfLSGAcphS0vkxR", "reverse": False },
    # { "name": "Krishna", "url": "https://www.youtube.com/playlist?list=PLdhxSHmOPfNQjNcHaHwOmIYv5z1bUbZJS", "reverse": False },
    { "name": "Masha and the Bear", "url": "https://www.youtube.com/@MashaBearEN/videos", "reverse": False },
    { "name": "Pinaki", "url": "https://www.youtube.com/@BhootBandhus_SonicGang/videos", "reverse": False },
    # { "name": "Titoo", "url": "https://www.youtube.com/playlist?list=PLdhxSHmOPfNSHsuxsnjuL3BOsPGXuMDie", "reverse": False },
    # { "name": "Wow", "url": "https://www.youtube.com/@WowKidzOfficialTV/videos", "reverse": False },
]


def process_youtube_playlist(iptv: IPTVLog):
    video_id = None
    ytdl_opts = {
        "quiet": True,           # don’t spam logs
        "skip_download": True,   # don’t download video
        "extract_flat": True,    # don’t go deep into formats,
        "match_filter": yt_dlp.utils.match_filter_func("duration >= 300 & live_status!=is_upcoming"),
        "playlist_items": "-5:-1" if iptv.reverse else "1:5",
    }
    logger.debug(f"OPTIONS: {ytdl_opts}")
    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        info = ydl.extract_info(iptv.playlist_url, download=False)
    
        video_ids = [entry['id'] for entry in info['entries'] if entry]
        logger.debug(f"Video IDs: {video_ids}")

    if not video_ids:
        logger.info("===> Could not extract video id")
        iptv.status = "ERROR"
        iptv.error = "Could not extract video ids"
        return

    ytdl_opts = {
        "quiet": True,           # don’t spam logs
        "format": f"best",  # equivalent of -f
        'outtmpl': f"{MEDIA_FOLDER}/{iptv.name}.mp4",  # equivalent of -o
        "overwrites": True,      # force overwrite existing files
        "ignoreerrors": True,   # skip unavailable/private/deleted videos
        "match_filter": yt_dlp.utils.match_filter_func("duration >= 300"),
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "ios", "web_embedded", "tv"]
            }
        }
    }
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
       reverse TEXT,
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
            iptv.reverse = str(show["reverse"])
            iptv.create_date = today
            iptv.error = "NO ERROR"

            logger.info(f"Name: {iptv.name} Playlist: {iptv.playlist_url} Reverse: {iptv.reverse}")
            process_youtube_playlist(iptv)
            time.sleep(10)
        except Exception as e:
            logger.error(f"{iptv.name} {iptv.episode_url} {e}")
            iptv.status = "EXCEPTION"
            iptv.error = f"{e}"
        finally:
            stmt = f"""
            INSERT INTO iptv_log VALUES
            ({iptv.name}, {iptv.playlist_url}, {iptv.episode_url}, {iptv.reverse}, {iptv.status}, {iptv.error}, {iptv.create_date})
            """
            logger.debug(stmt)
            cur.execute(stmt)
    con.commit()
    con.close()
