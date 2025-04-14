import subprocess
import time
import psutil
import os
import sys

# 실행할 대상 프로그램 이름
TARGET_EXE = "usageguard.exe"
CHECK_INTERVAL = 5  # 초 단위

# 현재 실행 경로에서 exe를 실행할 수 있도록 절대 경로 계산
def get_exe_path():
    base_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
    return os.path.join(base_dir, TARGET_EXE)

# 해당 프로세스가 실행 중인지 확인
def is_process_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == TARGET_EXE:
            return True
    return False

# 타겟 프로그램 실행
def start_process():
    exe_path = get_exe_path()
    print(f"🔁 {TARGET_EXE} 실행 시도 중: {exe_path}")
    
    if not os.path.exists(exe_path):
        print("❌ usageguard.exe 파일을 찾을 수 없습니다. 실행 중단.")
        return

    try:
        subprocess.Popen(
            [exe_path],
            cwd=os.path.dirname(exe_path),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("✅ 실행 성공")
    except Exception as e:
        print(f"❌ 실행 실패: {e}")

if __name__ == "__main__":
    print("👀 Watchdog 시작됨. 타겟 프로세스 감시 중...")
    while True:
        if not is_process_running():
            print("⚠️ 프로세스 종료 감지! 재실행 중...")
            start_process()
        time.sleep(CHECK_INTERVAL)
