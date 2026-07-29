import time
import re
import random
import logging
from datetime import datetime

import yt_dlp


PATTERN = r'[^a-zA-Z0-9]'
HOST = "0.0.0.0"
M3U_PORT = 9000
MEDIA_FOLDER = "/data/media"
M3U_FILE = "playlist.m3u"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


RES="720"
YT_LIST = [
    #("Bheem", "https://www.youtube.com/playlist?list=PLdhxSHmOPfNTgFEWOlBzE3rwLYnpPqFvH"),
    # ("Cartoon Network", "https://www.youtube.com/@cnindia/videos"),
    ("Curios George", "https://www.youtube.com/@CuriousGeorge/videos"),
    ("Detective Mehul", "https://www.youtube.com/@DetectiveMehul.English/videos"),
    # ("Discovery", "https://www.youtube.com/@DiscoveryKidsIN/videos"),
    # ("Disney", "https://www.youtube.com/@disneyindia/videos"),
    ("Krishna", "https://www.youtube.com/playlist?list=PLdhxSHmOPfNQjNcHaHwOmIYv5z1bUbZJS"),
    # ("Masha and the Bear", "https://www.youtube.com/@MashaBearEN/videos"),
    ("Pinaki", "https://www.youtube.com/@BhootBandhus_SonicGang/videos"),
    #("Singham", "https://www.youtube.com/playlist?list=PLdhxSHmOPfNRIWPEkdB9ovz2Lnjhd_Z51"),
    ("Sonic", "https://www.youtube.com/@Sonic-Gang/videos"),
    # ("Sony", "https://www.youtube.com/@SonyYAY/videos"),
    # ("Titoo", "https://www.youtube.com/playlist?list=PLdhxSHmOPfNSHsuxsnjuL3BOsPGXuMDie"),
    # ("Wow", "https://www.youtube.com/@WowKidzOfficialTV/videos"),
]

YT_SHORTS = [
    ("Physics", "https://www.youtube.com/@Theory_of_Physics/shorts")
]

YT_CHANNELS = [
    ("DD Bharati", "https://www.youtube.com/@ddbharati/live"),
    ("DD News", "https://www.youtube.com/@DDnews/live"),
    ("NDTV 24x7", "https://www.youtube.com/@NDTV/live"),
    ("Zee News", "https://www.youtube.com/watch?v=WquRAK-XoV4"),
    ("Aaj Tak", "https://www.youtube.com/watch?v=Nq2wYlWFucg"),
    ("India Today", "https://www.youtube.com/watch?v=sYZtOFzM78M"),
    ("CNBC TV18", "https://www.youtube.com/watch?v=P857H4ej-MQ"),
    ("CNBC Awaaz", "https://www.youtube.com/watch?v=dnQ1M21Z5Tw"),
    ("Zee Business", "https://www.youtube.com/zeebusiness/live"),
    ("DD India", "https://www.youtube.com/@DDIndia/live"),
    ("WION", "https://www.youtube.com/watch?v=JnttcoZFFI8"),
    ("TV9 Kannada", "https://www.youtube.com/watch?v=jdJoOhqCipA"),
    ("News18 Kannada", "https://www.youtube.com/watch?v=st7fBmW20MU"),
]


def process_youtube_playlist(name, url, res):
    video_id = None
    ytdl_opts = {
        "quiet": False,           # don’t spam logs
        "skip_download": True,   # don’t download video
        "extract_flat": True,    # don’t go deep into formats,
        "match_filter": yt_dlp.utils.match_filter_func("duration >= 300 & live_status!=is_upcoming"),
        "playlist_items": "1-5",
    }
    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        video_ids = [entry['id'] for entry in info['entries'] if entry]
        video_id = video_ids[0]
        logger.info(f"===> Selected Video ID: {video_id} out of {len(video_ids)} videos")

    if not video_id:
        logger.info("===> Could not extract video id")
        return

    ytdl_opts = {
        "quiet": False,           # don’t spam logs
        "format": f"best",  # equivalent of -f
        'outtmpl': f"{MEDIA_FOLDER}/{name}.mp4",  # equivalent of -o
        "overwrites": True,      # force overwrite existing files
        "ignoreerrors": True,   # skip unavailable/private/deleted videos
        "match_filter": yt_dlp.utils.match_filter_func("duration >= 300"),
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "ios", "web_embedded"]
            }
        }
    }
    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        rc = ydl.download(f"https://www.youtube.com/watch?v={video_id}")
        if rc == 0:
            logger.info("===> Completed Download")
        else:
            logger.info(f"===> Download failed with return code: {rc}")


def process_youtube_shorts(name, url, res):
    video_id = None
    ytdl_opts = {
        "quiet": True,           # don’t spam logs
        "skip_download": True,   # don’t download video
        "extract_flat": True,    # don’t go deep into formats,
    }
    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        video_ids = [entry['id'] for entry in info['entries'] if entry]
        video_id = random.choice(video_ids)
        logger.info(f"===> Selected Video ID: {video_id} out of {len(video_ids)} videos")

    if not video_id:
        logger.info("===> Could not extract video id")
        return

    ytdl_opts = {
        "quiet": True,           # don’t spam logs
        "format": f"best[height<={res}]",  # equivalent of -f
        'outtmpl': f"{MEDIA_FOLDER}/{name}.mp4",  # equivalent of -o
        "overwrites": True,      # force overwrite existing files
        "ignoreerrors": True,   # skip unavailable/private/deleted videos
    }
    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        rc = ydl.download(f"https://www.youtube.com/shorts/{video_id}")
        if rc == 0:
            logger.info("===> Completed Download")
        else:
            logger.info(f"===> Download failed with return code: {rc}")


def process_youtube_channel(name, url):
    video_id = None

    ytdl_opts = {
        "quiet": True,           # don’t spam logs
        "skip_download": True,   # don’t download video
        "extract_flat": True,    # don’t go deep into formats
        "ignoreerrors": True,    # skip unavailable/private/deleted videos
    }
    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'id' in info:
            video_id = info['id']
        else:
            logger.info("Either No Info or No Entries")
            return []

        logger.info(f"Latest Video ID: {video_id} selected for the channel")
        mu3_entry = [
            f'#EXTINF:-1 tvg-id="{name}" group-title="Live Streams",{name}\n',
            f"plugin://plugin.video.youtube/play/?video_id={video_id}\n"
        ]
        logger.info(f"===> M3U Entry: {mu3_entry}")
        return mu3_entry


if __name__ == "__main__":
    logger.info("Starting the process\n")

    today = datetime.today()

    for name, url in YT_LIST:
    # for i in range(len(YT_LIST):
        try:
            # name, url = random.choice(YT_LIST)
            clean_name = re.sub(PATTERN, '', name)
            logger.info(f"<=== {clean_name} {url}")
            file_path = f"{MEDIA_FOLDER}/{clean_name}.mp4"
            process_youtube_playlist(clean_name, url, RES)
            time.sleep(10)
        except Exception as e:
            logger.error(f"{clean_name} {url} {e}")
            continue


    # name, url, res = random.choice(YT_SHORTS)
    # clean_name = re.sub(PATTERN, '', name)

    # logger.info(f"<=== {clean_name} {url}")
    # file_path = f"{MEDIA_FOLDER}/{clean_name}.mp4"
    # process_youtube_shorts(clean_name, url, res)
    # time.sleep(5)

    # with open(M3U_FILE, "w", encoding="utf-8") as f:
    #     f.write("#EXTM3U\n")
    #     for name, url in YT_CHANNELS:
    #         logger.info(f"<=== {name} {url}")
    #         entries = process_youtube_channel(name, url)
    #         for line in entries:
    #             f.write(line)
    #             logger.info(f"<=== Added m3u8 for {name}")

    #     logger.info("<=== M3U File Created")

    # uvicorn.run(app, host=HOST, port=M3U_PORT)
