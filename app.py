import os, time, uuid, random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from gtts import gTTS
import qrcode

app = Flask(__name__)
CORS(app)

# បង្កើត Folder សម្រាប់ទុក File
UPLOAD_FOLDER = 'static/uploads'
AUDIO_FOLDER = 'static/audio'
for folder in [UPLOAD_FOLDER, AUDIO_FOLDER]:
    if not os.path.exists(folder): os.makedirs(folder)

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get('text', '')
    lang = data.get('lang', 'km')
    file_name = f"tts_{uuid.uuid4()}.mp3"
    path = os.path.join(AUDIO_FOLDER, file_name)
    gTTS(text=text, lang=lang).save(path)
    return jsonify({"audioUrl": f"{request.host_url}{path}"})

@app.route('/api/generate-qr', methods=['POST'])
def generate_qr():
    data = request.json.get('data', '')
    file_name = f"qr_{uuid.uuid4()}.png"
    path = os.path.join(UPLOAD_FOLDER, file_name)
    img = qrcode.make(data)
    img.save(path)
    return jsonify({"qrUrl": f"{request.host_url}{path}"})

@app.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    query = request.json.get('query', '')
    # សម្រាប់ AI ពិត អ្នកអាចតភ្ជាប់ OpenAI នៅទីនេះ
    return jsonify({"answer": f"AI ឆ្លើយតបនឹង: {query}"})

if __name__ == '__main__':
    app.run(debug=True)
