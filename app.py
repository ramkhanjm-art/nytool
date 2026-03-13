import os
import uuid
import random
import time
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
from gtts import gTTS
import qrcode
from PIL import Image

app = Flask(__name__)
CORS(app)

# កំណត់ Folder សម្រាប់ទុក File បណ្ដោះអាសន្នលើ Render
UPLOAD_FOLDER = '/tmp/uploads'
AUDIO_FOLDER = '/tmp/audio'

for folder in [UPLOAD_FOLDER, AUDIO_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# --- ១. ទំព័រដើម (ដោះស្រាយបញ្ហា Not Found) ---
@app.route('/')
def index():
    # ប្រសិនបើអ្នកមាន index.html ក្នុង folder ជាមួយគ្នា វានឹងអានឯកសារនោះ
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Backend is Running!</h1><p>សូមប្រាកដថាអ្នកបាន Upload index.html ទៅក្នុង GitHub មេ។</p>"

# --- ២. Tool: Text to Speech (TTS) ---
@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.json
        text = data.get('text', '')
        lang = data.get('lang', 'km')
        
        if not text:
            return jsonify({"error": "សូមបញ្ចូលអត្ថបទ"}), 400

        file_name = f"tts_{uuid.uuid4()}.mp3"
        file_path = os.path.join(AUDIO_FOLDER, file_name)
        
        tts = gTTS(text=text, lang=lang)
        tts.save(file_path)
        
        return jsonify({"audioUrl": f"{request.host_url}download/audio/{file_name}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ៣. Tool: QR Code Generator ---
@app.route('/api/qr', methods=['POST'])
def generate_qr():
    try:
        data = request.json
        qr_data = data.get('data', '')
        if not qr_data:
            return jsonify({"error": "No data"}), 400

        file_name = f"qr_{uuid.uuid4()}.png"
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        
        img = qrcode.make(qr_data)
        img.save(file_path)
        
        return jsonify({"qrUrl": f"{request.host_url}download/uploads/{file_name}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ៤. Tool: AI Chat / Math AI (Free Mode) ---
@app.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    query = request.json.get('query', '').lower()
    # នេះជា Logic ឆ្លើយតបសាមញ្ញ (អ្នកអាចភ្ជាប់ API កម្រិតខ្ពស់ពេលក្រោយ)
    responses = [
        "ខ្ញុំអាចជួយអ្នកបាន! តើអ្នកចង់សួរអ្វី?",
        "សំណួរល្អណាស់! ចាំបន្តិចខ្ញុំកំពុងគិត...",
        "បាទ/ចាស! ខ្ញុំយល់ហើយ។"
    ]
    return jsonify({"answer": random.choice(responses)})

# --- ៥. មុខងារសម្រាប់ឱ្យគេទាញយក File (Download) ---
@app.route('/download/audio/<filename>')
def download_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

@app.route('/download/uploads/<filename>')
def download_uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    # កំណត់ Port ឱ្យត្រូវជាមួយ Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
