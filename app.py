import os
import uuid
import yt_dlp

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = "/tmp/mj_downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return jsonify({
        "status": "online",
        "app": "MJ Downloader API"
    })


@app.post("/download")
def download():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "URL is required"}), 400

    filename = str(uuid.uuid4())
    output = os.path.join(DOWNLOAD_DIR, filename + ".%(ext)s")

    options = {
        "outtmpl": output,
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)

        return send_file(
            filepath,
            as_attachment=True,
            download_name=os.path.basename(filepath)
        )

    except Exception as e:
        return jsonify({
            "error": "Download failed",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
