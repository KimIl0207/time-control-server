# 🖥️ Computer Usage Controller

> 자녀의 컴퓨터 사용시간을 제한하고, 원격으로 제어 가능한 타이머 프로그램

## ✅ 주요 기능

- 하루 사용 시간 제한 및 누적 기록 저장
- 마스터 모드 (무제한 사용) 전환 기능
- 원격 웹 UI (부모님 스마트폰에서 설정 변경 가능)
- 실시간 사용량 확인
- 비밀번호 인증 기능으로 설정 보호
- 강제종료 방지 (watchdog 감시 프로세스 포함)
- 설치형 `.exe` 제공 (자동 시작 포함)

---

## 🚀 설치 방법

### 📦 설치파일 다운로드

**[👉 설치파일 받기 (Setup_ComputerUsage.exe)](https://github.com/KimIl0207/time-control-server/releases/download/v1.1.1/Setup_ComputerUsage.exe)**

1. 위 링크에서 설치파일을 다운로드합니다.
2. 실행하면 자동으로 프로그램이 설치되고 백그라운드에서 작동합니다.
3. PC 재부팅 시에도 자동 시작됩니다.

> 설치 후, 웹 UI에서 `마스터 모드` 또는 `시간 제한 설정`을 변경하세요.

---

## 🌐 웹 제어 패널 접속

아래 주소로 접속하면 스마트폰이나 다른 기기에서 사용시간을 원격 제어할 수 있습니다:

🔗 [https://time-control-server-a4qg.onrender.com](https://time-control-server-a4qg.onrender.com)

---

## 🛠 개발 및 커스터마이징

### 🔧 주요 파일

| 파일 | 설명 |
|------|------|
| `shutDownManager.py` | 시간 제한 감시 기능 (PyInstaller로 `.exe` 빌드됨) |
| `watchdog.py` | 감시자: shutDownManager가 꺼지면 자동 재실행 |
| `settingManager.py` | 서버 설정 통신, 파일 저장 담당 |
| `server.py` | Flask 기반 서버 API |
| `client/` | React 기반 웹 UI |

### 🧱 빌드 도구
- `pyinstaller` (`shutDownManager`, `watchdog` 빌드용)
- `Inno Setup` (`Setup_ComputerUsage.exe` 생성용)

---

## 📄 라이선스

MIT License (자유롭게 사용 및 수정 가능)

---

## 🙋 도움말 / 기여

오류나 개선 제안은 이슈로 남겨주세요!

> Made with ❤️ by KimIl0207
