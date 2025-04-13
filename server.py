from flask import Flask, request, jsonify, render_template_string, send_from_directory
from settingManager import load_settings, save_settings, load_usage
from datetime import datetime
from flask_cors import CORS
import os

build_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "client", "build")
app = Flask(__name__, static_folder=build_dir, static_url_path="/")
CORS(app)
@app.route('/')
def server_react():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/status', methods=['GET'])
def get_status():
    usage = load_usage()
    settings = load_settings()

    today = datetime.now().strftime('%Y-%m-%d')
    used = usage.get(today, 0)
    limit = settings.get('daily_limit', 3600)

    return jsonify({
        "used": used,
        "limit": limit,
        "remaining": max(limit - used, 0),
        "percent": round(min((used / limit) * 100, 100), 1),
        "master_mode": settings.get("master_mode", False)
    })

@app.route('/usage', methods=['GET'])
def get_usage():
    usage = load_usage()
    return jsonify(usage)

@app.route('/settings', methods=['GET'])
def get_settings():
    settings = load_settings()
    return jsonify(settings)

@app.route('/settings', methods=['POST'])
def update_settings():
    data = request.json
    settings = load_settings()

    if 'daily_limit' in data:
        settings['daily_limit'] = int(data['daily_limit'])

    if 'master_mode' in data:
        settings['master_mode'] = bool(data['master_mode'])

    save_settings(settings)
    return jsonify({"message": "설정이 업데이트되었습니다.", "settings": settings})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)