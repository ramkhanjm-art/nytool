import os
import uuid
import asyncio
import edge_tts
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS

app = Flask(__name__, template_folder='.')
CORS(app)

# បង្កើត Folder សម្រាប់ទុក File សំឡេងបណ្ដោះអាសន្ន
AUDIO_FOLDER = '/tmp/audio'
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

# បញ្ជីសំឡេង Neural AI (បុរសជា Default)
VOICE_DATA = {
    "km": {"male": "km-KH-PisethNeural", "female": "km-KH-SreymomNeural"},
    "en": {"male": "en-US-AndrewNeural", "female": "en-US-AvaNeural"},
    "zh": {"male": "zh-CN-YunxiNeural", "female": "zh-CN-XiaoxiaoNeural"},
    "ja": {"male": "ja-JP-KeitaNeural", "female": "ja-JP-NanamiNeural"},
    "ko": {"male": "ko-KR-InJunNeural", "female": "ko-KR-SunHiNeural"},
    "vi": {"male": "vi-VN-NamMinhNeural", "female": "vi-VN-HoaiMyNeural"},
    "lo": {"male": "lo-LA-ChanthavongNeural", "female": "lo-LA-KeotaNeural"},
    "th": {"male": "th-TH-NiwatNeural", "female": "th-TH-PremwadeeNeural"},
    "my": {"male": "my-MM-ThihaNeural", "female": "my-MM-NilarNeural"},
    "id": {"male": "id-ID-ArdiNeural", "female": "id-ID-GadisNeural"},
    "ms": {"male": "ms-MY-OsmanNeural", "female": "ms-MY-YasminNeural"},
    "tl": {"male": "fil-PH-AngeloNeural", "female": "fil-PH-BlessicaNeural"},
    "hi": {"male": "hi-IN-MadhurNeural", "female": "hi-IN-SwaraNeural"},
    "ar": {"male": "ar-SA-HamedNeural", "female": "ar-SA-ZariyahNeural"},
    "fr": {"male": "fr-FR-HenriNeural", "female": "fr-FR-DeniseNeural"},
    "de": {"male": "de-DE-ConradNeural", "female": "de-DE-KatjaNeural"},
    "ru": {"male": "ru-RU-DmitryNeural", "female": "ru-RU-SvetlanaNeural"}
}

async def generate_voice(text, lang, gender, file_path):
    lang_set = VOICE_DATA.get(lang, VOICE_DATA["en"])
    # យក male បើ frontend មិនបានផ្ញើភេទមក
    selected_voice = lang_set.get(gender, lang_set["male"])
    
    communicate = edge_tts.Communicate(text, selected_voice)
    await communicate.save(file_path)

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except:
        return "Backend is Live! Please update index.html in GitHub."

@app.route('/api/tts', methods=['POST'])
def tts_endpoint():
    try:
        data = request.json
        text = data.get('text', '')
        lang = data.get('lang', 'km')
        gender = data.get('gender', 'male') # កំណត់ male ជា Default

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
