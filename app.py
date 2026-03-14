import asyncio
import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import edge_tts

app = Flask(__name__)
CORS(app)

AUDIO_DIR = "static/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# បញ្ជីសំឡេងសម្រាប់ភាសាទាំង ២១
VOICES = {
    'km': {'female': 'km-KH-SreymomNeural', 'male': 'km-KH-PisethNeural'},
    'en': {'female': 'en-US-AriaNeural', 'male': 'en-US-GuyNeural'},
    'th': {'female': 'th-TH-PremwadeeNeural', 'male': 'th-TH-NiwatNeural'},
    'zh-CN': {'female': 'zh-CN-XiaoxiaoNeural', 'male': 'zh-CN-YunxiNeural'}
    # ... បន្ថែមភាសាផ្សេងទៀតតាមទម្រង់នេះ ...
}

async def generate_audio(text, lang, gender, path):
    v_info = VOICES.get(lang, VOICES['en'])
    voice = v_info.get(gender, v_info['female'])
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(path)

@app.route('/api/tts', methods=['POST'])
def tts():
    try:
        data = request.json
        text, lang, gender = data.get('text', ''), data.get('lang', 'en'), data.get('gender', 'female')
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_audio(text, lang, gender, filepath))
        loop.close()
        
        return jsonify({"url": f"/static/audio/{filename}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/static/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
