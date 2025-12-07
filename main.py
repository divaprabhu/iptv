import time
import re
import random
import logging
from datetime import datetime

import yt_dlp
from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn

PATTERN = r'[^a-zA-Z0-9]'
HOST = "0.0.0.0"
M3U_PORT = 9000
MEDIA_FOLDER = "/data/media"
M3U_FILE = "playlist.m3u"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()


@app.get("/m3u")
def serve_m3u():
    return FileResponse(path=M3U_FILE, filename=M3U_FILE, media_type="audio/x-mpegurl")


@app.get("/kids")
def serve_kids():
    return FileResponse(path=M3U_FILE, filename=M3U_FILE, media_type="audio/x-mpegurl")


YT_LIST = [
    ("Green Gold Kids", "https://www.youtube.com/@GreenGoldKids/videos", "480"),
    ("Pogo", "https://www.youtube.com/@PogoChannel/videos", "480"),
    ("Sonig Gang", "https://www.youtube.com/@Sonic-Gang/videos", "480"),
    ("Rudra", "https://www.youtube.com/@Rudra-SonicGang/videos", "480"),
    ("Kids Galaxy", "https://www.youtube.com/@KidsGalaxyYT/videos", "480"),
    ("Ninja Hatori", "https://www.youtube.com/@Ninja_Hattori_SonicGang/videos", "480"),
    ("Yo Kids", "https://www.youtube.com/@yokidscartoon-c8h/videos", "480"),
    ("Masha and the Bear", "https://www.youtube.com/@MashaBearEN/videos", "480"),
    ("Hotstar Kids", "https://www.youtube.com/@jio_hotstar_kids/videos", "480"),
    ("Discovery", "https://www.youtube.com/@DiscoveryKidsIN/videos", "480"),
    ("Detective Mehul", "https://www.youtube.com/@MindYourLogic.Riddles/videos", "480"),
]

YT_SHORTS = [
    ("Physics", "https://www.youtube.com/@Theory_of_Physics/shorts", "1080")
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
        "quiet": True,           # don’t spam logs
        "skip_download": True,   # don’t download video
        "extract_flat": True,    # don’t go deep into formats,
        "match_filter": yt_dlp.utils.match_filter_func("duration >= 300"),
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
        "quiet": True,           # don’t spam logs
        "format": f"best[height<={res}]",  # equivalent of -f
        'outtmpl': f"{MEDIA_FOLDER}/{name}.mp4",  # equivalent of -o
        "overwrites": True,      # force overwrite existing files
        "ignoreerrors": True,   # skip unavailable/private/deleted videos
        "match_filter": yt_dlp.utils.match_filter_func("duration >= 300"),
    }
    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        rc = ydl.download(f"https://www.youtube.com/watch?v={video_id}")
        if rc == 0:
            logger.info("===> Completed Download")
        else:
            logger.info("===> Download failed with return code: {rc}")


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
    rem = today.day % 3

    for name, url, res in YT_LIST[rem::3]:
        clean_name = re.sub(PATTERN, '', name)

        logger.info(f"<=== {clean_name} {url}")
        file_path = f"{MEDIA_FOLDER}/{clean_name}.mp4"
        process_youtube_playlist(clean_name, url, res)
        time.sleep(300)

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
