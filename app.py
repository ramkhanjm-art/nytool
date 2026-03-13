import os
import uuid
import asyncio
import edge_tts
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS

app = Flask(__name__, template_folder='.')
CORS(app)

# បង្កើត Folder សម្រាប់ទុក File សំឡេង
AUDIO_FOLDER = '/tmp/audio'
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

# មុខងារបំប្លែងអត្ថបទទៅជាសំឡេងពិរោះ (Async)
async def generate_voice(text, lang, file_path):
    # កំណត់សំឡេងតាមភាសា (Neural Voices)
    voices = {
        "km": "km-KH-SreymomNeural", # ខ្មែរ (ស្រី)
        "en": "en-US-AvaNeural",      # អង់គ្លេស
        "zh": "zh-CN-XiaoxiaoNeural", # ចិន
        "ja": "ja-JP-NanamiNeural",   # ជប៉ុន
        "ko": "ko-KR-SunHiNeural",    # កូរ៉េ
        "th": "th-TH-PremwadeeNeural",# ថៃ
        "vi": "vi-VN-HoaiMyNeural",   # វៀតណាម
        "fr": "fr-FR-DeniseNeural",   # បារាំង
        "ar": "ar-SA-ZariyahNeural"   # អារ៉ាប់
    }
    
    # បើមិនមានក្នុងបញ្ជី ឱ្យប្រើភាសាអង់គ្លេសជា Default
    selected_voice = voices.get(lang, "en-US-AvaNeural")
    
    communicate = edge_tts.Communicate(text, selected_voice)
    await communicate.save(file_path)

# --- ផ្លូវទៅកាន់ទំព័រដើម ---
@app.route('/')
def index():
    try:
        return render_template('index.html')
    except:
        return "Backend is running! Please upload index.html"

# --- API បង្កើតសំឡេង ---
@app.route('/api/tts', methods=['POST'])
def tts_endpoint():
    data = request.json
    text = data.get('text', '')
    lang = data.get('lang', 'km')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    file_name = f"voice_{uuid.uuid4()}.mp3"
    file_path = os.path.join(AUDIO_FOLDER, file_name)

    # ដំណើរការ Async ក្នុង Flask
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(generate_voice(text, lang, file_path))
    loop.close()

    return jsonify({
        "audioUrl": f"{request.host_url}download/audio/{file_name}"
    })

# --- ផ្លូវសម្រាប់ទាញយក File ---
@app.route('/download/audio/<filename>')
def download_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
