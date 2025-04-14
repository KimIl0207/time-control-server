import subprocess
import time
import psutil
import os

# 실행할 대상 프로그램 이름
TARGET_EXE = "usageguard.exe"
CHECK_INTERVAL = 5  # 초 단위

# 현재 실행 경로에서 exe를 실행할 수 있도록 절대 경로 계산
def get_exe_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), TARGET_EXE)

# 해당 프로세스가 실행 중인지 확인
def is_process_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == TARGET_EXE:
            return True
    return False

# 타겟 프로그램 실행
def start_process():
    exe_path = get_exe_path()
    print(f"🔁 {TARGET_EXE} 실행 시도 중...")
    subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    print("👀 Watchdog 시작됨. 타겟 프로세스 감시 중...")
    while True:
        if not is_process_running():
            print("⚠️ 프로세스 종료 감지! 재실행 중...")
            start_process()
        time.sleep(CHECK_INTERVAL)
