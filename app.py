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

VOICE_DATA = {
    "km": {"male": "km-KH-PisethNeural", "female": "km-KH-SreymomNeural"},
    "en": {"male": "en-US-AndrewNeural", "female": "en-US-AvaNeural"},
    "zh": {"male": "zh-CN-YunxiNeural", "female": "zh-CN-XiaoxiaoNeural"},
    "ja": {"male": "ja-JP-KeitaNeural", "female": "ja-JP-NanamiNeural"},
    "ko": {"male": "ko-KR-InJunNeural", "female": "ko-KR-SunHiNeural"},
    "th": {"male": "th-TH-NiwatNeural", "female": "th-TH-PremwadeeNeural"},
    "vi": {"male": "vi-VN-NamMinhNeural", "female": "vi-VN-HoaiMyNeural"},
    "lo": {"male": "lo-LA-ChanthavongNeural", "female": "lo-LA-KeotaNeural"},
    "my": {"male": "my-MM-ThihaNeural", "female": "my-MM-NilarNeural"},
    "tl": {"male": "fil-PH-AngeloNeural", "female": "fil-PH-BlessicaNeural"},
    "ms": {"male": "ms-MY-OsmanNeural", "female": "ms-MY-YasminNeural"},
    "id": {"male": "id-ID-ArdiNeural", "female": "id-ID-GadisNeural"},
    "fr": {"male": "fr-FR-HenriNeural", "female": "fr-FR-DeniseNeural"},
    "ru": {"male": "ru-RU-DmitryNeural", "female": "ru-RU-SvetlanaNeural"},
    "ar": {"male": "ar-SA-HamedNeural", "female": "ar-SA-ZariyahNeural"},
    "bn": {"male": "bn-BD-PradeepNeural", "female": "bn-BD-NabanitaNeural"},
    "pt": {"male": "pt-PT-DuarteNeural", "female": "pt-PT-RaquelNeural"},
    "hi": {"male": "hi-IN-MadhurNeural", "female": "hi-IN-SwaraNeural"},
    "es": {"male": "es-ES-AlvaroNeural", "female": "es-ES-ElviraNeural"},
    "de": {"male": "de-DE-ConradNeural", "female": "de-DE-KatjaNeural"},
    "br": {"male": "ms-MY-OsmanNeural", "female": "ms-MY-YasminNeural"} # Brunei uses Malay
}

async def generate_voice(text, lang, gender, file_path):
    lang_set = VOICE_DATA.get(lang, VOICE_DATA["en"])
    selected_voice = lang_set.get(gender, lang_set["male"])
    communicate = edge_tts.Communicate(text, selected_voice)
    await communicate.save(file_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tts', methods=['POST'])
def tts_endpoint():
    try:
        data = request.json
        text, lang, gender = data.get('text', ''), data.get('lang', 'km'), data.get('gender', 'male')
        if not text: return jsonify({"error": "No text"}), 400
        file_name = f"voice_{uuid.uuid4()}.mp3"
        file_path = os.path.join(AUDIO_FOLDER, file_name)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_voice(text, lang, gender, file_path))
        loop.close()
        
        return jsonify({"audioUrl": f"{request.host_url}download/audio/{file_name}"})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/download/audio/<filename>')
def download_audio(filename):
    # as_attachment=True ជួយឱ្យ Browser ដឹងថាត្រូវដោនឡូត មិនមែនគ្រាន់តែបើកស្ដាប់
    return send_from_directory(AUDIO_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
