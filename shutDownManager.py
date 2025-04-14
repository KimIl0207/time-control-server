import time
import os
import json
from datetime import datetime
from settingManager import get_settings_from_server, load_usage, save_usage, get_today, update_usage_on_server
import tkinter as tk

def show_block_screen():
    root = tk.Tk()
    root.title("시간 초과")
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.configure(bg="black")

    # ESC, Alt+F4 방지
    root.bind("<Escape>", lambda e: "break")
    root.protocol("WM_DELETE_WINDOW", lambda: None)

    def try_unlock():
        if pw_entry.get() == "697442":  # ✅ 여기에 원하는 비밀번호 설정
            from settingManager import update_settings_on_server
            update_settings_on_server({"master_mode": True})
            
            root.destroy()
        else:
            error_label.config(text="❌ 비밀번호가 틀렸습니다.")

    label = tk.Label(
        root,
        text="⛔ 사용 시간이 초과되었습니다.\n지금은 컴퓨터를 사용할 수 없습니다.",
        fg="white",
        bg="black",
        font=("맑은 고딕", 24),
        justify="center"
    )
    label.pack(pady=20)

    pw_entry = tk.Entry(root, show="*", font=("맑은 고딕", 16), justify="center")
    pw_entry.pack(ipadx=10, ipady=5)
    pw_entry.focus()

    unlock_btn = tk.Button(root, text="🔓 잠금 해제", font=("맑은 고딕", 14), command=try_unlock)
    unlock_btn.pack(pady=10)

    error_label = tk.Label(root, text="", fg="red", bg="black", font=("맑은 고딕", 11))
    error_label.pack()

    root.mainloop()

# ✅ 제한 초과 시 호출 함수 (컴퓨터 종료 대신 화면 잠금)
def shutdown():
    print("⛔ 사용 시간 초과! 화면 잠금 실행 중...")
    show_block_screen()

# ✅ 초기 설정
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
        current_time = time.time()

        # 설정 갱신
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
                "percent": min(100, round((usage_data[today] / USAGE_LIMIT) * 100, 1)),
                "master_mode": MASTER_MODE,
                "updated_at": datetime.now().strftime("%H:%M:%S")
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
                "percent": min(100, round((usage_data[today] / USAGE_LIMIT) * 100, 1)),
                "master_mode": MASTER_MODE,
                "updated_at": datetime.now().strftime("%H:%M:%S")
            }
            with open("usage_status.json", "w") as f:
                json.dump(status, f, indent=2)
            save_usage(usage_data)
            last_save_time = current_time
            update_usage_on_server(usage_data[today])

        time.sleep(1)

except KeyboardInterrupt:
    pass
finally:
    end_time = time.time()
    usage_data[today] = usage_data.get(today, 0) + (end_time - start_time)
    save_usage(usage_data)
