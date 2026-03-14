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

# បញ្ជីសំឡេងប្រុស/ស្រី សម្រាប់ភាសាទាំង ២១
VOICE_DATA = {
    'km': {'female': 'km-KH-SreymomNeural', 'male': 'km-KH-PisethNeural'},
    'en': {'female': 'en-US-AriaNeural', 'male': 'en-US-GuyNeural'},
    'zh-CN': {'female': 'zh-CN-XiaoxiaoNeural', 'male': 'zh-CN-YunxiNeural'},
    'ja': {'female': 'ja-JP-NanamiNeural', 'male': 'ja-JP-KeitaNeural'},
    'ko': {'female': 'ko-KR-SunHiNeural', 'male': 'ko-KR-InGookNeural'},
    'th': {'female': 'th-TH-PremwadeeNeural', 'male': 'th-TH-NiwatNeural'},
    'vi': {'female': 'vi-VN-HoaiMyNeural', 'male': 'vi-VN-NamMinhNeural'},
    'lo': {'female': 'lo-LA-KeolaNeural', 'male': 'lo-LA-ChanthavongNeural'},
    'my': {'female': 'my-MM-MyaNeural', 'male': 'my-MM-ThihaNeural'},
    'tl': {'female': 'fil-PH-BlessicaNeural', 'male': 'fil-PH-AngeloNeural'},
    'ms': {'female': 'ms-MY-YasminNeural', 'male': 'ms-MY-OsmanNeural'},
    'id': {'female': 'id-ID-GisellaNeural', 'male': 'id-ID-ArdiNeural'},
    'bn': {'female': 'bn-BD-NabanitaNeural', 'male': 'bn-BD-PradeepNeural'},
    'hi': {'female': 'hi-IN-SwaraNeural', 'male': 'hi-IN-MadhurNeural'},
    'ar': {'female': 'ar-SA-ZariyahNeural', 'male': 'ar-SA-HamedNeural'},
    'pt': {'female': 'pt-BR-FranciscaNeural', 'male': 'pt-BR-AntonioNeural'},
    'fr': {'female': 'fr-FR-DeniseNeural', 'male': 'fr-FR-HenriNeural'},
    'de': {'female': 'de-DE-KatjaNeural', 'male': 'de-DE-ConradNeural'},
    'es': {'female': 'es-ES-ElviraNeural', 'male': 'es-ES-AlvaroNeural'},
    'ru': {'female': 'ru-RU-SvetlanaNeural', 'male': 'ru-RU-DmitryNeural'},
    'it': {'female': 'it-IT-ElsaNeural', 'male': 'it-IT-DiegoNeural'}
}

async def save_voice(text, lang, gender, filepath):
    lang_info = VOICE_DATA.get(lang, VOICE_DATA['en'])
    voice = lang_info.get(gender, lang_info['female'])
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filepath)

@app.route('/api/tts', methods=['POST'])
def tts_route():
    try:
        data = request.json
        text = data.get('text', '').strip()
        lang = data.get('lang', 'en')
        gender = data.get('gender', 'female')
        
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(save_voice(text, lang, gender, filepath))
        loop.close()
        return jsonify({"audioUrl": f"/static/audio/{filename}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/static/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
