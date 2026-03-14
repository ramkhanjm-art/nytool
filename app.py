from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from gtts import gTTS
import os
import uuid

app = Flask(__name__)
CORS(app)

# បង្កើត Folder សម្រាប់រក្សាទុកសំឡេង
AUDIO_DIR = "static/audio"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# បញ្ជីភាសាទាំង ២១
SUPPORTED_LANGS = {
    'km': 'km', 'en': 'en', 'zh-CN': 'zh-CN', 'ja': 'ja', 
    'ko': 'ko', 'th': 'th', 'vi': 'vi', 'lo': 'lo', 
    'my': 'my', 'tl': 'tl', 'ms': 'ms', 'id': 'id', 
    'bn': 'bn', 'hi': 'hi', 'ar': 'ar', 'pt': 'pt', 
    'fr': 'fr', 'de': 'de', 'es': 'es', 'ru': 'ru', 'it': 'it'
}

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.json
        text = data.get('text', '').strip()
        lang = data.get('lang', 'en')

        if not text:
            return jsonify({"error": "Missing text"}), 400

        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)
        
        # បង្កើតសំឡេងតាមរយៈ gTTS
        tts = gTTS(text=text, lang=SUPPORTED_LANGS.get(lang, 'en'), slow=False)
        tts.save(filepath)
        
        return jsonify({"audioUrl": f"/{filepath}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# បើកឱ្យចូលមើល file ក្នុង static folder
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
