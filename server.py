from flask import Flask, request, jsonify, render_template_string, send_from_directory
from settingManager import load_settings, save_settings, load_usage, save_usage
from datetime import datetime
from flask_cors import CORS
import os

build_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "client", "build")
app = Flask(__name__, static_folder=build_dir, static_url_path="/")
CORS(app)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(build_dir, 'static'), filename)

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

@app.route('/usage', methods=['POST'])
def update_usage():
    usage = load_usage()
    today = datetime.now().strftime('%Y-%m-%d')
    data = request.get_json()

    print(f"[📥] 사용 기록 요청 수신: {data}")

    if not isinstance(data, dict):
        return jsonify({"error": "올바르지 않은 형식입니다."}), 400

    if 'used' in data:
        try:
            usage[today] = float(data['used'])
            save_usage(usage)
            print(f"[✅] {today} 사용 기록 저장 완료: {usage[today]}초")
        except Exception as e:
            print(f"[❌] 저장 중 오류 발생: {e}")
            return jsonify({"error": "저장 실패"}), 500
    else:
        print("[⚠️] 'used' 키가 포함되지 않음")

    return jsonify({"message": "✅ 사용 기록이 서버에 저장되었습니다."})

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)