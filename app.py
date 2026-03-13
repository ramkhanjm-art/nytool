import os
import uuid
import asyncio
import edge_tts
from flask import Flask, request, jsonify, send_from_directory, render_template

app = Flask(__name__, template_folder='.')
from flask_cors import CORS
CORS(app)

# បង្កើត Folder សម្រាប់ទុក File សំឡេងបណ្តោះអាសន្ន
AUDIO_FOLDER = '/tmp/audio'
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

async def generate_voice(text, lang, file_path):
    # សំឡេងស្រីមុំ (Neural) ពិរោះបំផុតសម្រាប់ខ្មែរ
    voice_map = {
        "km": "km-KH-SreymomNeural",
        "en": "en-US-AvaNeural",
        "th": "th-TH-PremwadeeNeural"
    }
    selected_voice = voice_map.get(lang, "en-US-AvaNeural")
    communicate = edge_tts.Communicate(text, selected_voice)
    await communicate.save(file_path)

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except:
        return "Server is Live! ប៉ុន្តែរកមិនឃើញ index.html ក្នុង GitHub របស់អ្នកទេ។"

@app.route('/api/tts', methods=['POST'])
def tts_endpoint():
    try:
        data = request.json
        text = data.get('text', '')
        lang = data.get('lang', 'km')

        if not text:
            return jsonify({"error": "No text"}), 400

        file_name = f"voice_{uuid.uuid4()}.mp3"
        file_path = os.path.join(AUDIO_FOLDER, file_name)

        # កូដសម្រាប់ដំណើរការ Async ក្នុង Flask
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(generate_voice(text, lang, file_path))
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
