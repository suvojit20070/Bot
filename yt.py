from flask import Flask, request, jsonify, send_from_directory
from yt_dlp import YoutubeDL
import os
import uuid

app = Flask(__name__)

# Change this to your domain
BASE_URL = "https://yourdomain.com"

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

VIDEO_QUALITY = {
    "1": "144",
    "2": "360",
    "3": "720",
    "4": "best"
}

AUDIO_QUALITY = {
    "1": "64",
    "2": "128",
    "3": "192",
    "4": "320"
}


@app.route("/downloads/<path:filename>")
def download_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename)


@app.route("/yt.py")
def yt_download():
    url = request.args.get("url")
    media_type = request.args.get("type", "video").lower()
    quality = request.args.get("quality", "4")

    if not url:
        return jsonify({
            "status": False,
            "message": "url parameter missing"
        }), 400

    uid = str(uuid.uuid4())

    try:

        if media_type == "audio":

            bitrate = AUDIO_QUALITY.get(quality, "320")

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": f"{DOWNLOAD_DIR}/{uid}.%(ext)s",
                "noplaylist": True,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": bitrate
                }]
            }

            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            filename = f"{uid}.mp3"

        else:

            q = VIDEO_QUALITY.get(quality, "best")

            if q == "best":
                fmt = "bestvideo+bestaudio/best"
            else:
                fmt = f"bestvideo[height<={q}]+bestaudio/best"

            ydl_opts = {
                "format": fmt,
                "merge_output_format": "mp4",
                "outtmpl": f"{DOWNLOAD_DIR}/{uid}.%(ext)s",
                "noplaylist": True
            }

            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            filename = None

            for file in os.listdir(DOWNLOAD_DIR):
                if file.startswith(uid):
                    filename = file
                    break

            if not filename:
                raise Exception("Downloaded file not found")

        file_url = f"{BASE_URL}/downloads/{filename}"

        return jsonify({
            "status": True,
            "type": media_type,
            "quality": quality,
            "url": file_url
        })

    except Exception as e:
        return jsonify({
            "status": False,
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)