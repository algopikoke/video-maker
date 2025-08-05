from flask import Flask, request
from PIL import Image
import pytesseract
import subprocess
import requests
import uuid
import os

app = Flask(name)

BOT_TOKEN = 'ISI_TOKEN_BOT_KAMU'
CHAT_ID = 'ISI_CHAT_ID_KAMU'

@app.route('/generate', methods=['POST'])
def generate_video():
    file = request.files['screenshot']
    video_id = request.form.get('video', '1')
    music_id = request.form.get('music', '1')

    filename = str(uuid.uuid4())
    img_path = f"/tmp/{filename}.jpg"
    file.save(img_path)

    text = pytesseract.image_to_string(Image.open(img_path))
    title, desc, tags = generate_metadata(text)

    video_path = f"assets/videos/bg_{video_id}.mp4"
    music_path = f"assets/music/music_{music_id}.mp3"
    output_path = f"/tmp/{filename}_out.mp4"

    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-i', img_path,
        '-i', music_path,
        '-filter_complex', '[0:v][1:v]overlay=W-w-20:H-h-20',
        '-shortest',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        output_path
    ]
    subprocess.run(cmd)

    with open(output_path, 'rb') as video_file:
        requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendVideo',
            data={'chat_id': CHAT_ID, 'caption': f"*{title}*\\n\\n{desc}\\n\\n{tags}", 'parse_mode': 'Markdown'},
            files={'video': video_file}
        )

    return "Video berhasil dikirim ke Telegram."

def generate_metadata(text):
    lines = text.strip().split('\\n')
    title = lines[0][:80] if lines else "Berita Hari Ini"
    desc = text[:300].strip()
    tags = ' '.join([f"#{w.lower()}" for w in title.split() if len(w) > 3][:5])
    return title, desc, tags

if name == 'main':
    app.run()
