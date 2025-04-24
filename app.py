from flask import Flask, render_template, request, jsonify, send_file, after_this_request
import yt_dlp
import os
import uuid
import time
from threading import Timer

app = Flask(__name__)
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def sanitize_filename(filename):
    return filename.replace("..", "").replace("/", "").replace("\\", "")

def download_generic(url, audio_only=False):
    file_id = str(uuid.uuid4())
    video_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.mp4")
    audio_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.mp3")

    ydl_opts = {
        'quiet': True,
        'format': 'mp4',
        'noplaylist': True,
        'outtmpl': video_path,
        'cookies': 'cookies.json',
        'no_check_certificate': True,
        'geo_bypass': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    if audio_only:
        extract_audio(video_path, audio_path)
        check_and_clean_downloads()
        return audio_path

    check_and_clean_downloads()
    return video_path

def extract_audio(video_path, output_path):
    os.system(f'ffmpeg -y -i "{video_path}" -vn -acodec libmp3lame -q:a 2 "{output_path}"')
    os.remove(video_path)

def handle_youtube(url, audio_only=False):
    if audio_only:
        return download_generic(url, audio_only=True)

    file_id = str(uuid.uuid4())
    video_path = os.path.join(DOWNLOAD_DIR, f"{file_id}_video.mp4")
    audio_path = os.path.join(DOWNLOAD_DIR, f"{file_id}_audio.m4a")
    final_output = os.path.join(DOWNLOAD_DIR, f"{file_id}_final.mp4")

    video_opts = {
        'quiet': True,
        'format': 'bestvideo[height<=1080]',
        'outtmpl': video_path,
        'cookies': 'cookies.json',
        'no_check_certificate': True,
        'geo_bypass': True,
    }
    audio_opts = {
        'quiet': True,
        'format': 'bestaudio',
        'outtmpl': audio_path,
        'cookies': 'cookies.json',
        'no_check_certificate': True,
        'geo_bypass': True,
    }

    with yt_dlp.YoutubeDL(video_opts) as ydl:
        ydl.download([url])
    with yt_dlp.YoutubeDL(audio_opts) as ydl:
        ydl.download([url])

    os.system(f'ffmpeg -y -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac "{final_output}"')
    os.remove(video_path)
    os.remove(audio_path)
    check_and_clean_downloads()
    return final_output

def check_and_clean_downloads():
    if len(os.listdir(DOWNLOAD_DIR)) >= 5:
        Timer(5.0, clean_downloads).start()

def clean_downloads():
    for f in os.listdir(DOWNLOAD_DIR):
        file_path = os.path.join(DOWNLOAD_DIR, f)
        if os.path.isfile(file_path):
            os.remove(file_path)

def handle_tiktok(url, audio_only=False):
    return download_generic(url, audio_only)

def handle_instagram(url, audio_only=False):
    return download_generic(url, audio_only)

def handle_facebook(url, audio_only=False):
    return download_generic(url, audio_only)

def handle_twitter(url, audio_only=False):
    return download_generic(url, audio_only)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_direct_url", methods=["POST"])
def get_direct_url():
    data = request.get_json()
    url = data.get("url")
    audio_only = data.get("audio_only", False)

    if not url:
        return jsonify({"error": "لم يتم تقديم الرابط"}), 400

    try:
        if "youtube.com" in url or "youtu.be" in url:
            path = handle_youtube(url, audio_only)
            return jsonify({"url": f"/download_file?path={os.path.basename(path)}&download=1", "type": "download"})
        elif "tiktok.com" in url:
            path = handle_tiktok(url, audio_only)
            return jsonify({"url": f"/download_file?path={os.path.basename(path)}&download=1", "type": "download"})
        elif "instagram.com" in url:
            path = handle_instagram(url, audio_only)
            return jsonify({"url": f"/download_file?path={os.path.basename(path)}&download=1", "type": "download"})
        elif "facebook.com" in url:
            path = handle_facebook(url, audio_only)
            return jsonify({"url": f"/download_file?path={os.path.basename(path)}&download=1", "type": "download"})
        elif "twitter.com" in url or "x.com" in url:
            path = handle_twitter(url, audio_only)
            return jsonify({"url": f"/download_file?path={os.path.basename(path)}&download=1", "type": "download"})
        else:
            return jsonify({"error": "رابط غير مدعوم"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download_file")
def download_file():
    file_name = request.args.get("path")
    safe_name = sanitize_filename(file_name)
    file_path = os.path.join(DOWNLOAD_DIR, safe_name)

    if os.path.exists(file_path):
        @after_this_request
        def remove_file(response):
            try:
                os.remove(file_path)
            except Exception:
                pass
            return response

        as_attachment = request.args.get("download", "1") == "1"
        return send_file(file_path, as_attachment=as_attachment)
    
    return "File not found", 404

@app.route('/googlee746176d37c57674.html')
def google_verify():
    return send_file('googlee746176d37c57674.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

