import subprocess
import time
import re
import os
import yt_dlp
import datetime

from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn

PATTERN = r'[^a-zA-Z0-9]'
HOST = "0.0.0.0"
BASE_PORT = 9001
MEDIA_FOLDER = "/pi"
M3U_FILE = "playlist.m3u"
CURRENT_DATE=datetime.datetime.now()

app = FastAPI()
@app.get("/m3u")
def serve_m3u():
    return FileResponse(path=M3U_FILE, filename=M3U_FILE, media_type="audio/x-mpegurl")


YT_LIST = [
    ("Mr Bean", "https://www.youtube.com/playlist?list=PLwIV8SNgQyXGhQCAzcP1DmWJ4QbwNmWv3", "480"),
    ("Mr Bean Classic", "https://www.youtube.com/playlist?list=PLC1EDzqtkrh8Pta-kBwb-hrDJKkUTfirz", "480"),
    ("Masha and the Bear", "https://www.youtube.com/playlist?list=PLtMvg0F941zev_gT8jgSE6XQnHPZZ_q39", "480"),
    ("Little Singham", "https://www.youtube.com/playlist?list=PLdhxSHmOPfNSSDIe5dp3v204zqhUJp-b2", "480"),
    ("Chhota Bheem", "https://www.youtube.com/playlist?list=PLdhxSHmOPfNTgFEWOlBzE3rwLYnpPqFvH", "480"),
    ("Titoo", "https://www.youtube.com/playlist?list=PLdhxSHmOPfNSHsuxsnjuL3BOsPGXuMDie", "480"),
    ("Little Krishna", "https://www.youtube.com/playlist?list=PLdhxSHmOPfNQjNcHaHwOmIYv5z1bUbZJS", "480"),
    ("Teen Titans", "https://www.youtube.com/playlist?list=PLcrApfnvcfVw8109V5oSIBQXZ9BRUmeCw", "480"),
    ("Shiva", "https://www.youtube.com/playlist?list=PL2XOPpYaVR4-o4gPiJB5Cplj0Zga10uW6", "480"),
    ("Rudra", "https://www.youtube.com/playlist?list=PL2XOPpYaVR4-KGjiEYPDP_NRE5HfgEATR", "480"),
    ("Bhoot Boss", "https://www.youtube.com/playlist?list=PLAgLR8cSB8IIufPnNIbmrlGPcJubV08nZ", "480")
]

YT_CHANNELS = [
    ("BBC Earth", "https://www.youtube.com/@BBCEarthScience/live", "360"),
    ("Science Channel", "https://www.youtube.com/@sciencechannel/live", "360"),
    ("National Geographic", "https://www.youtube.com/@NatGeo/live", "360"),
    ("DD Bharati", "https://www.youtube.com/@ddbharati/live", "360"),
    ("DD News", "https://www.youtube.com/@DDnews/live", "360"),
    ("NDTV 24x7", "https://www.youtube.com/@NDTV/live", "360"),
    ("Firstpost", "https://www.youtube.com/@Firstpost/live", "360"),
    ("Zee News", "https://www.youtube.com/@ZeeNews/live", "360"),
    ("Aaj Tak", "https://www.youtube.com/@aajtak/live", "360"),
    ("CNBC TV18", "https://www.youtube.com/@CNBC-TV18/live", "360"),
    ("DD India", "https://www.youtube.com/@DDIndia/live", "360"),
    ("Bloomberg", "https://www.youtube.com/bloombergpodcasts/live", "360"),
    ("WION", "https://www.youtube.com/@WION/live", "360"),
    ("TV9 Kannada", "https://www.youtube.com/@tv9kannada/live", "360"),
    ("News18 Kannada", "https://www.youtube.com/@News18Kannada/live", "360"),
]


def get_youtube_playlist_url(name, url, res):
    if current_date.weekday() != 6:  # weekday() returns 6 for Sunday
        print("Today is Sunday!")
        return
        
    command = f"""yt-dlp --flat-playlist --get-id "{url}" | shuf -n 1 | xargs -I {{}} yt-dlp -f "best[height<=480][vcodec*=avc1]" "https://www.youtube.com/watch?v={{}}" -o {MEDIA_FOLDER}/{name}.mp4"""

    print(f"Playlist Command: {command}")
    result = subprocess.run(
        command,
        shell=True,  # The key change
        capture_output=True,
        text=True
    )
    print("Return code:", result.returncode)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

def get_youtube_channel_url(name, url, res, port):
    command = [
        "yt-dlp",
        "-g",
        url
    ]
    print(f"Channel Command: {' '.join(command)}")
    result = subprocess.run(
        command,
        capture_output=True,  # capture stdout and stderr
        text=True             # decode bytes to string
    )
    print(f"URL: {result.stdout}")

    start_streamlink_processes(result.stdout, port, res)

    mu3_entry = [
        f'#EXTINF:-1 tvg-id="{name}" group-title="Live Streams",{name}\n',
        f"http://{HOST}:{port}/stream\n"
    ]
    return mu3_entry

def start_streamlink_processes(url, port, res):
    print(f"Starting Streamlink process for {name} on port {port}...")
    command = [
        "streamlink",
        "--hls-segment-stream-data",
        f"--stream-sorting-excludes", f">{res}p",
        "--stream-sorting-excludes", "vp9",
        "--player-external-http",
        f"--player-external-http-port={port}",
        url.strip(),
        f"best"
    ]
    
    print(f"Streamlink Command: {' '.join(command)}")
    proc = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    print("Starting the process")
    for name, url, res in YT_LIST:
        clean_name = re.sub(PATTERN, '', name)

        print(f"===> {clean_name} {url}")
        file_path = f"{MEDIA_FOLDER}/{clean_name}.mp4"
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"{file_path} deleted")
        else:
            print(f"{file_path} does not exist")

        get_youtube_playlist_url(clean_name, url, res)
        time.sleep(30)


    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        port = BASE_PORT
        for name, url, res in YT_CHANNELS:
            entries = get_youtube_channel_url(name, url, res, port)
            port += 1

            print(f"M3U Entry: {entries}")
            for line in entries:
                f.write(line)
        print(f"M3U File Created")

    uvicorn.run(app, host="0.0.0.0", port=9000)


