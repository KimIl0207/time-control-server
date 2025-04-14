import tkinter as tk
import json
import time
from threading import Thread

is_topmost = True

def toggle_topmost():
    global is_topmost
    is_topmost = not is_topmost
    root.attributes("-topmost", is_topmost)
    top_button.config(
        text="항상 위(on)" if is_topmost else "항상 위(off)"
    )

# ✅ 상태 읽기 함수
def read_status():
    try:
        with open("usage_status.json", "r") as f:
            return json.load(f)
    except:
        return {
            "limit": 0,
            "used": 0,
            "remaining": 0,
            "percent": 0,
            "updated_at": "-"
        }

# ✅ 시간 포맷팅 함수
def format_time(seconds):
    return f"{int(seconds // 60)}분 {int(seconds % 60)}초"

# ✅ 상태 업데이트 루프
def update_loop():
    while True:
        status = read_status()
        limit_label.config(text=f"\u23f1 제한 시간: {format_time(status['limit'])}")
        used_label.config(text=f"\u2611 사용 시간: {format_time(status['used'])}")
        remain_label.config(text=f"\u23f0 남은 시간: {format_time(status['remaining'])}")
        percent_label.config(text=f"\ud83d\udcca 사용률: {status['percent']}%")
        updated_label.config(text=f"\u25cb {status.get('updated_at', '-')}")
        master_text = "🔓 마스터 모드: ON" if status.get("master_mode") else "🔒 마스터 모드: OFF"
        master_label.config(text=master_text)
        time.sleep(1)

# ✅ 창 드래그 이동용 핸들러
def start_move(event):
    root.x = event.x
    root.y = event.y

def do_move(event):
    x = event.x_root - root.x
    y = event.y_root - root.y
    root.geometry(f"+{x}+{y}")

# ✅ 커스텀 슬라이더 생성
def create_custom_slider(parent, initial_value, callback):
    canvas = tk.Canvas(parent, width=240, height=30, bg="white", highlightthickness=0)
    canvas.pack(pady=10)

    bar_x1, bar_x2 = 10, 230
    unit = (bar_x2 - bar_x1) / 60  # 40~100 기준

    slider_fill = canvas.create_rectangle(bar_x1, 15, bar_x1 + unit * (initial_value - 40), 20, fill="#4caf50", outline="")
    slider_handle = canvas.create_oval(bar_x1 + unit * (initial_value - 40) - 5, 10, bar_x1 + unit * (initial_value - 40) + 5, 25, fill="gray")

    def update_slider(x):
        x = max(bar_x1, min(bar_x2, x))
        value = round((x - bar_x1) / unit + 40)
        canvas.coords(slider_fill, bar_x1, 15, x, 20)
        canvas.coords(slider_handle, x - 5, 10, x + 5, 25)
        callback(value)

    def drag(event):
        update_slider(event.x)

    canvas.bind("<B1-Motion>", drag)
    canvas.bind("<Button-1>", drag)

    return canvas

# ✅ GUI 생성
root = tk.Tk()
root.title("사용 모니터")
root.overrideredirect(True)
root.attributes("-topmost", True)
root.geometry("300x250+50+50")
root.configure(bg="white")


# ✅ 아이콘 설정 (선택)
try:
    root.iconbitmap("monitor.ico")
except:
    pass

# ✅ 드래그용 상단바
move_bar = tk.Frame(root, height=20, bg="#dddddd", cursor="fleur")
move_bar.pack(fill=tk.X)
move_bar.bind("<Button-1>", start_move)
move_bar.bind("<B1-Motion>", do_move)

# ✅ 상태 라벨
font_set = ("맑은 고딕", 11)
limit_label = tk.Label(root, font=font_set, bg="white")
used_label = tk.Label(root, font=font_set, bg="white")
remain_label = tk.Label(root, font=font_set, bg="white")
percent_label = tk.Label(root, font=font_set, bg="white")
updated_label = tk.Label(root, font=("맑은 고딕", 9), fg="gray", bg="white")
master_label = tk.Label(root, font=("맑은 고딕", 11), bg="white", fg="#0077cc")


limit_label.pack(pady=2)
used_label.pack(pady=2)
remain_label.pack(pady=2)
percent_label.pack(pady=2)
updated_label.pack(pady=5)
master_label.pack(pady=2)

# ✅ 커스텀 슬라이더로 투명도 조절
create_custom_slider(root, initial_value=100, callback=lambda v: root.attributes("-alpha", v / 100))

# ✅ 상태 업데이트 시작
Thread(target=update_loop, daemon=True).start()
root.mainloop()

# 상단 고정 버튼
top_button = tk.Button(
    root, text="항상 위(on)", command=toggle_topmost,
    font=("맑은 고딕", 10)
)
top_button.pack(pady=10)