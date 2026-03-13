import os
import uuid
import asyncio
import edge_tts
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS

app = Flask(__name__, template_folder='.')
CORS(app)

AUDIO_FOLDER = '/tmp/audio'
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

# បញ្ជីសំឡេង Neural AI គ្រប់ភាសាដែលអ្នកចង់បាន
VOICE_DATA = {
    "km": {"female": "km-KH-SreymomNeural", "male": "km-KH-PisethNeural"},
    "en": {"female": "en-US-AvaNeural", "male": "en-US-AndrewNeural"},
    "zh": {"female": "zh-CN-XiaoxiaoNeural", "male": "zh-CN-YunxiNeural"},
    "ja": {"female": "ja-JP-NanamiNeural", "male": "ja-JP-KeitaNeural"},
    "ko": {"female": "ko-KR-SunHiNeural", "male": "ko-KR-InJunNeural"},
    "vi": {"female": "vi-VN-HoaiMyNeural", "male": "vi-VN-NamMinhNeural"},
    "lo": {"female": "lo-LA-KeotaNeural", "male": "lo-LA-ChanthavongNeural"},
    "th": {"female": "th-TH-PremwadeeNeural", "male": "th-TH-NiwatNeural"},
    "my": {"female": "my-MM-NilarNeural", "male": "my-MM-ThihaNeural"},
    "id": {"female": "id-ID-GadisNeural", "male": "id-ID-ArdiNeural"},
    "ms": {"female": "ms-MY-YasminNeural", "male": "ms-MY-OsmanNeural"},
    "tl": {"female": "fil-PH-BlessicaNeural", "male": "fil-PH-AngeloNeural"},
    "bn": {"female": "bn-BD-NabanitaNeural", "male": "bn-BD-PradeepNeural"},
    "hi": {"female": "hi-IN-SwaraNeural", "male": "hi-IN-MadhurNeural"},
    "ar": {"female": "ar-SA-ZariyahNeural", "male": "ar-SA-HamedNeural"},
    "fr": {"female": "fr-FR-DeniseNeural", "male": "fr-FR-HenriNeural"},
    "de": {"female": "de-DE-KatjaNeural", "male": "de-DE-ConradNeural"},
    "ru": {"female": "ru-RU-SvetlanaNeural", "male": "ru-RU-DmitryNeural"}
}

async def generate_voice(text, lang, gender, file_path):
    lang_set = VOICE_DATA.get(lang, VOICE_DATA["en"])
    selected_voice = lang_set.get(gender, lang_set["female"])
    communicate = edge_tts.Communicate(text, selected_voice)
    await communicate.save(file_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tts', methods=['POST'])
def tts_endpoint():
    try:
        data = request.json
        text = data.get('text', '')
        lang = data.get('lang', 'km')
        gender = data.get('gender', 'female')

        if not text:
            return jsonify({"error": "No text"}), 400

        file_name = f"voice_{uuid.uuid4()}.mp3"
        file_path = os.path.join(AUDIO_FOLDER, file_name)

        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(generate_voice(text, lang, gender, file_path))
        new_loop.close()

        return jsonify({"audioUrl": f"{request.host_url}download/audio/{file_name}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/audio/<filename>')
def download_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
