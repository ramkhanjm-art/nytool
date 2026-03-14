import os, uuid, asyncio, edge_tts
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS

app = Flask(__name__, template_folder='.')
CORS(app)

AUDIO_FOLDER = '/tmp/audio'
if not os.path.exists(AUDIO_FOLDER): os.makedirs(AUDIO_FOLDER)

# បញ្ជីសម្លេង ២១ ភាសាពេញលេញ
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
    "bn": {"male": "bn-BD-PradeepNeural", "female": "bn-BD-NabanitaNeural"},
    "hi": {"male": "hi-IN-MadhurNeural", "female": "hi-IN-SwaraNeural"},
    "ar": {"male": "ar-SA-HamedNeural", "female": "ar-SA-ZariyahNeural"},
    "pt": {"male": "pt-PT-DuarteNeural", "female": "pt-PT-RaquelNeural"},
    "fr": {"male": "fr-FR-HenriNeural", "female": "fr-FR-DeniseNeural"},
    "de": {"male": "de-DE-ConradNeural", "female": "de-DE-KatjaNeural"},
    "es": {"male": "es-ES-AlvaroNeural", "female": "es-ES-ElviraNeural"},
    "ru": {"male": "ru-RU-DmitryNeural", "female": "ru-RU-SvetlanaNeural"},
    "it": {"male": "it-IT-DiegoNeural", "female": "it-IT-ElsaNeural"}
}

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/tts', methods=['POST'])
def tts_endpoint():
    try:
        data = request.json
        text, lang, gender = data.get('text', ''), data.get('lang', 'km'), data.get('gender', 'male')
        file_name = f"voice_{uuid.uuid4()}.mp3"
        file_path = os.path.join(AUDIO_FOLDER, file_name)
        voice = VOICE_DATA.get(lang, VOICE_DATA['en']).get(gender)
        async def run(): await edge_tts.Communicate(text, voice).save(file_path)
        asyncio.run(run())
        return jsonify({"audioUrl": f"{request.host_url}download/audio/{file_name}"})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/download/audio/<filename>')
def download_audio(filename): return send_from_directory(AUDIO_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
