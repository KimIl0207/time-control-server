import os
import json
from datetime import datetime
import requests

if os.name == 'nt':
    APP_DIR = os.path.join(os.getenv('APPDATA'), 'ComputerUsageController')
else:
    APP_DIR = os.path.expanduser('~/.ComputerUsageController')

os.makedirs(APP_DIR, exist_ok=True)

SETTINGS_FILE = os.path.join(APP_DIR, 'settings.json')
SAVE_FILE = os.path.join(APP_DIR, 'usage_data.json')
STATUS_FILE = os.path.join(APP_DIR, 'usage_status.json')
SERVER_URL = 'https://time-control-server-a4qg.onrender.com/'

def get_settings_from_server():
    try:
        response = requests.get(f"{SERVER_URL}/settings")
        if response.status_code == 200:
            return response.json()
        else:
            print("⚠️ 서버에서 설정 불러오기 실패, 상태코드:", response.status_code)
    except Exception as e:
        print("❌ 서버 연결 오류:", e)
    return None

def update_settings_on_server(new_settings: dict):
    try:
        response = requests.post(
            f"{SERVER_URL}/settings",
            json=new_settings
        )
        if response.status_code == 200:
            print("✅ 서버 설정 업데이트 성공:", response.json())
        else:
            print("⚠️ 설정 업데이트 실패:", response.status_code)
    except Exception as e:
        print("❌ 서버 요청 오류:", e)

def update_usage_on_server(seconds):
    try:
        requests.post(f"{SERVER_URL}/usage", json={"used": seconds})
    except:
        pass

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        default_settings = {
            "daily_limit": 3600,
            "master_mode": False
        }
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(default_settings, f, indent=2)
        return default_settings
    else:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

def load_usage():
    if not os.path.exists(SAVE_FILE):
        return {}
    with open(SAVE_FILE, 'r') as f:
        content = f.read().strip()
        if not content:
            return {}
        return json.loads(content)

def save_usage(data):
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f)

def get_today():
    return datetime.now().strftime('%Y-%m-%d')
