import os

ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")


def _load_env():
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


def _setup():
    print("=" * 50)
    print("  날씨알림봇 최초 설정")
    print("=" * 50)
    print()
    print("텔레그램 봇 토큰과 채팅방 ID를 입력해 주세요.")
    print("(BotFather에서 발급받은 토큰 / @userinfobot 에서 확인한 ID)")
    print()

    token = input("봇 토큰: ").strip()
    chat_id = input("채팅방 ID: ").strip()

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write(f"TELEGRAM_TOKEN={token}\n")
        f.write(f"CHAT_ID={chat_id}\n")
        f.write(f"CITY=Seoul\n")
        f.write(f"ALERT_HOUR=7\n")
        f.write(f"ALERT_MINUTE=30\n")
        f.write(f"DASHBOARD_PORT=8500\n")

    print()
    print("[완료] 설정이 저장되었습니다! (.env 파일)")
    print()
    os.environ["TELEGRAM_TOKEN"] = token
    os.environ["CHAT_ID"] = chat_id


_load_env()

# .env 없으면 최초 설정 실행
if not os.path.exists(ENV_FILE):
    _setup()
    _load_env()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID        = int(os.environ.get("CHAT_ID", "0"))
CITY           = os.environ.get("CITY", "Seoul")
ALERT_HOUR     = int(os.environ.get("ALERT_HOUR", "7"))
ALERT_MINUTE   = int(os.environ.get("ALERT_MINUTE", "30"))
DASHBOARD_PORT = int(os.environ.get("DASHBOARD_PORT", "8500"))

if not TELEGRAM_TOKEN or CHAT_ID == 0:
    _setup()
    _load_env()
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
    CHAT_ID        = int(os.environ.get("CHAT_ID", "0"))
