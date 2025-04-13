import time
import os
from settingManager import get_settings_from_server, load_usage, save_usage, get_today
import json

def shutdown():
    print("사용 시간 초과! 시스템을 종료합니다.")
    os.system("shutdown /s /t 1")  # 리눅스는 'shutdown now'

# 설정 및 초기값
# 루프 전에 설정값 한 번만 미리 받아두자
initial_settings = get_settings_from_server()
USAGE_LIMIT = initial_settings.get("daily_limit", 3600)
MASTER_MODE = initial_settings.get("master_mode", False)

usage_data = load_usage()
today = get_today()
start_time = time.time()
last_save_time = time.time()
loop_start_time = time.time()
last_settings_fetch = time.time()

SETTINGS_REFRESH_INTERRAL = 10


used_time = usage_data.get(today, 0)

try:
    while True:
        # 설정 갱신
        current_time = time.time()

        if current_time - last_settings_fetch >= SETTINGS_REFRESH_INTERRAL:
            new_settings = get_settings_from_server()
            if new_settings:
                USAGE_LIMIT = new_settings.get("daily_limit", USAGE_LIMIT)
                MASTER_MODE = new_settings.get("master_mode", MASTER_MODE)
            last_settings_fetch = current_time

        if MASTER_MODE:
            print("🔓 마스터 모드 활성화 — 사용시간 제한 중단됨.")
            time.sleep(1)
            continue

        loop_elapsed = current_time - loop_start_time
        loop_start_time = current_time

        usage_data[today] = usage_data.get(today, 0) + loop_elapsed

        if usage_data[today] >= USAGE_LIMIT:
            status = {
                "limit": USAGE_LIMIT,
                "used": usage_data[today],
                "remaining": max(0, USAGE_LIMIT - usage_data[today]),
                "percent": min(100, round((usage_data[today] / USAGE_LIMIT) * 100, 1))
            }
            with open("usage_status.json", "w") as f:
                json.dump(status, f, indent=2)
            save_usage(usage_data)
            shutdown()
            break

        if current_time - last_save_time >= 1:
            status = {
                "limit": USAGE_LIMIT,
                "used": usage_data[today],
                "remaining": max(0, USAGE_LIMIT - usage_data[today]),
                "percent": min(100, round((usage_data[today] / USAGE_LIMIT) * 100, 1))
            }
            with open("usage_status.json", "w") as f:
                json.dump(status, f, indent=2)
            save_usage(usage_data)
            last_save_time = current_time
            # print(f'{current_time}: 저장')

        time.sleep(1)

except KeyboardInterrupt:
    pass
finally:
    end_time = time.time()
    usage_data[today] = usage_data.get(today, 0) + (end_time - start_time)
    save_usage(usage_data)

