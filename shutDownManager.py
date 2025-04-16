import time
import json
from datetime import datetime
from settingManager import get_settings_from_server, load_usage, save_usage, get_today, update_usage_on_server, update_settings_on_server
import tkinter as tk
import traceback
import os
from screeninfo import get_monitors

APP_DIR = os.path.join(os.getenv('APPDATA'), 'ComputerUsageController')
os.makedirs(APP_DIR, exist_ok=True)

STATUS_FILE = os.path.join(APP_DIR, 'usage_status.json')
LOG_FILE = os.path.join(APP_DIR, 'fatal.log')

def show_block_screen():
    windows = []

    def try_unlock(entry, label, roots):
        if entry.get() == "697442":
            update_settings_on_server({"master_mode": True})
            for win in roots:
                win.destroy()
        else:
            label.config(text="❌ 비밀번호가 틀렸습니다.")

    def poll_server_and_check_unlock():
        while True:
            settings = get_settings_from_server()
            if settings and settings.get("master_mode", False):
                for win in windows:
                    try:
                        win.destroy()
                    except:
                        pass
                break
            time.sleep(2)

    for monitor in get_monitors():
        win = tk.Tk() if not windows else tk.Toplevel()
        win.title("시간 초과")
        win.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
        win.attributes("-topmost", True)
        win.overrideredirect(True)
        win.configure(bg="black")
        win.bind("<Escape>", lambda e: "break")
        win.protocol("WM_DELETE_WINDOW", lambda: None)

        label = tk.Label(win, text="사용 시간이 초과되었습니다.\n지금은 컴퓨터를 사용할 수 없습니다.",
                         fg="white", bg="black", font=("맑은 고딕", 24), justify="center")
        label.pack(pady=20)

        pw_entry = tk.Entry(win, show="*", font=("맑은 고딕", 16), justify="center")
        pw_entry.pack(ipadx=10, ipady=5)
        pw_entry.focus()

        unlock_btn = tk.Button(win, text="🔓 잠금 해제", font=("맑은 고딕", 14),
                               command=lambda e=pw_entry, l=None, r=windows: try_unlock(e, l or error_label, r))
        unlock_btn.pack(pady=10)

        error_label = tk.Label(win, text="", fg="red", bg="black", font=("맑은 고딕", 11))
        error_label.pack()

        windows.append(win)

    # 🔄 원격 해제 감시 스레드 시작
    import threading
    threading.Thread(target=poll_server_and_check_unlock, daemon=True).start()

    windows[0].mainloop()

def shutdown():
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as log:
            log.write("[!] 사용 시간 초과 — 화면 잠금 실행됨\n")
    except:
        pass
    show_block_screen()

# 설정
initial_settings = get_settings_from_server() or {}
USAGE_LIMIT = initial_settings.get("daily_limit", 3600)
MASTER_MODE = initial_settings.get("master_mode", False)

usage_data = load_usage()
today = get_today()
start_time = time.time()
last_save_time = time.time()
loop_start_time = time.time()
last_settings_fetch = time.time()
SETTINGS_REFRESH_INTERVAL = 10

try:
    while True:
        current_time = time.time()

        if current_time - last_settings_fetch >= SETTINGS_REFRESH_INTERVAL:
            new_settings = get_settings_from_server()
            if new_settings:
                USAGE_LIMIT = new_settings.get("daily_limit", USAGE_LIMIT)
                MASTER_MODE = new_settings.get("master_mode", MASTER_MODE)
            last_settings_fetch = current_time

        loop_elapsed = current_time - loop_start_time
        loop_start_time = current_time

        if not MASTER_MODE:
            usage_data[today] = usage_data.get(today, 0) + loop_elapsed

            if usage_data[today] >= USAGE_LIMIT and not MASTER_MODE:
                save_usage(usage_data)
                status = {
                    "limit": USAGE_LIMIT,
                    "used": usage_data[today],
                    "remaining": 0,
                    "percent": 100,
                    "master_mode": MASTER_MODE,
                    "updated_at": datetime.now().strftime("%H:%M:%S")
                }
                with open(STATUS_FILE, "w", encoding="utf-8") as f:
                    json.dump(status, f, indent=2)
                shutdown()
                break

        if current_time - last_save_time >= 1:
            status = {
                "limit": USAGE_LIMIT,
                "used": usage_data.get(today, 0),
                "remaining": max(0, USAGE_LIMIT - usage_data.get(today, 0)),
                "percent": min(100, round((usage_data.get(today, 0) / USAGE_LIMIT) * 100, 1)),
                "master_mode": MASTER_MODE,
                "updated_at": datetime.now().strftime("%H:%M:%S")
            }
            with open(STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump(status, f, indent=2)
            save_usage(usage_data)
            update_usage_on_server(usage_data.get(today, 0))
            last_save_time = current_time

        time.sleep(1)

except KeyboardInterrupt:
    pass
except Exception as e:
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(traceback.format_exc())

finally:
    end_time = time.time()
    if not MASTER_MODE:
        usage_data[today] += end_time - start_time
    save_usage(usage_data)
