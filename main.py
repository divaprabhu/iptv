import time
import re
import os
import random
import sys
import logging

import yt_dlp
from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn

PATTERN = r'[^a-zA-Z0-9]'
HOST = "0.0.0.0"
M3U_PORT = 9000
MEDIA_FOLDER = "/pi"
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
    ("Chhota Bheem", "https://www.youtube.com/playlist?list=PL0rMr_qVm_FI9ELiYrqK7jk9JjTgIdmoA", "480"),
    ("Titoo", "https://www.youtube.com/playlist?list=PLdhxSHmOPfNSHsuxsnjuL3BOsPGXuMDie", "480"),
    ("Little Krishna", "https://www.youtube.com/playlist?list=PLdhxSHmOPfNQjNcHaHwOmIYv5z1bUbZJS", "480"),
    ("Teen Titans", "https://www.youtube.com/playlist?list=PLcrApfnvcfVw8109V5oSIBQXZ9BRUmeCw", "480"),
    ("Shiva", "https://www.youtube.com/playlist?list=PLAepapbv7F5Cim-FG2XDlG65Oj7kRtVdf", "480"),
    ("Rudra", "https://www.youtube.com/playlist?list=PL2iQy8b-6D1Rdcm5ETFpBSqo7K-MXvZ4g", "480"),
    ("Bhoot Boss", "https://www.youtube.com/playlist?list=PLAgLR8cSB8ILSfgMZ3hBOhbX2xFJWo8a_", "480"),
    ("Chikoo", "https://www.youtube.com/playlist?list=PL2XOPpYaVR48o-sRPz3TKhic5FsXaUsdZ", "480"),
    ("Ninja Hatori", "https://www.youtube.com/playlist?list=PL5MT6UuH0i2CLc7zJdOFR-BQQHacRzzZB", "480"),
    ("Kicko", "https://www.youtube.com/playlist?list=PLjVIMJjREH-SmAXZ9WvZmispI9kLXfsAL", "480"),
    ("Mr Bean", "https://www.youtube.com/playlist?list=PLwIV8SNgQyXGhQCAzcP1DmWJ4QbwNmWv3", "480"),
    ("Mr Bean Classic", "https://www.youtube.com/playlist?list=PLC1EDzqtkrh8Pta-kBwb-hrDJKkUTfirz", "480"),
    ("Masha and the Bear", "https://www.youtube.com/playlist?list=PL-yqdhzdKqQRAm93SDGOtPK8KIe2QZQTO", "480"),
    ("Abhimanyu", "https://www.youtube.com/playlist?list=PLAepapbv7F5DBWSxLxUNnMSE3Q7lwKsSW", "480"),
    ("Motu Patlu", "https://www.youtube.com/playlist?list=PLRbgYr_kkJFk0oAYeSLwSkye342dv7Zht", "480"),
    ("Budh Aur Badri", "https://www.youtube.com/playlist?list=PL-4vjtQdv9wMAbt6Q2lmR4V2h4gtg_99X", "480"),
    ("Fukrey Boyzzz", "https://www.youtube.com/playlist?list=PLKRxH8XztcuDemtJvUcFSdHu27uR1zt8l", "480")
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
        video_id = random.choice(video_ids)
        logger.info(f"===> Selected Video ID: {video_id} out of {len(video_ids)} videos")

    if not video_id:
        logger.info(f"===> Could not extract video id")
        return
    

    ytdl_opts = {
        "quiet": True,           # don’t spam logs
        "format": f"best[height<={res}]", # equivalent of -f
        'outtmpl': f"{MEDIA_FOLDER}/{name}.mp4", # equivalent of -o
        "overwrites": True,      # force overwrite existing files
        "ignoreerrors": True,   # skip unavailable/private/deleted videos
        "match_filter": yt_dlp.utils.match_filter_func("duration >= 300"),
    }
    print(f"Options: {ytdl_opts}")
    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        rc = ydl.download(f"https://www.youtube.com/watch?v={video_id}")
        if rc == 0:
            logger.info(f"===> Completed Download")
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
        logger.info(f"===> Could not extract video id")
        return
    

    ytdl_opts = {
        "quiet": True,           # don’t spam logs
        "format": f"best[height<={res}]", # equivalent of -f
        'outtmpl': f"{MEDIA_FOLDER}/{name}.mp4", # equivalent of -o
        "overwrites": True,      # force overwrite existing files
        "ignoreerrors": True,   # skip unavailable/private/deleted videos
    }  
    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        rc = ydl.download(f"https://www.youtube.com/shorts/{video_id}")   
        if rc == 0:
            logger.info(f"===> Completed Download")
        else:
            logger.info(f"===> Download failed with return code: {rc}")   


def process_youtube_channel(name, url):
    video_id = None
    m3u_entry = []

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
            logger.info(f"Either No Info or No Entries")
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
 
    name, url, res = random.choice(YT_LIST)
    clean_name = re.sub(PATTERN, '', name)

    logger.info(f"<=== {clean_name} {url}")
    file_path = f"{MEDIA_FOLDER}/{clean_name}.mp4"
    process_youtube_playlist(clean_name, url, res)
    time.sleep(5)

    # name, url, res = random.choice(YT_SHORTS)
    # clean_name = re.sub(PATTERN, '', name)

    # logger.info(f"<=== {clean_name} {url}")
    # file_path = f"{MEDIA_FOLDER}/{clean_name}.mp4"
    # process_youtube_shorts(clean_name, url, res)
    # time.sleep(5)
    
    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, url in YT_CHANNELS:
            logger.info(f"<=== {name} {url}")
            entries = process_youtube_channel(name, url)
            for line in entries:
                f.write(line)
            logger.info(f"<=== Added m3u8 for {name}")

        logger.info(f"<=== M3U File Created")

    uvicorn.run(app, host=HOST, port=M3U_PORT)
