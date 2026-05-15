import requests
import time
import os
from dotenv import load_dotenv

# ===== TELEGRAM CONFIG =====
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        requests.post(
            url,
            json={
                "chat_id": CHAT_ID,
                "text": message
            },
            timeout=5
        )
    except Exception as e:
        print("Telegram error:", e)


# ===== LOKI CONFIG =====
LOKI_URL = "http://localhost:3100/loki/api/v1/query"

query = {
    "query": '{job=~".+"}',
    "limit": 50,
    "direction": "backward"
}

# tránh gửi trùng log
seen = set()

# từ khóa lỗi
ERROR_KEYWORDS = [
    "error", "warn", "failed", "timeout",
    "exception", "refused", "bad address",
    "no route", "crash", "oom", "killed"
]

def is_error(log: str):
    log_lower = log.lower()
    return any(k in log_lower for k in ERROR_KEYWORDS)


print("🚀 Realtime collector started...")

while True:

    try:
        r = requests.get(LOKI_URL, params=query, timeout=5)
        data = r.json()

        for stream in data.get("data", {}).get("result", []):

            job = stream["stream"].get("job", "unknown")
            pod = stream["stream"].get("pod", "unknown")

            for ts, log in stream["values"]:

                key = f"{ts}:{log}"

                if key in seen:
                    continue

                seen.add(key)

                if is_error(log):

                    msg = f"""🚨 Kubernetes Alert

Job: {job}
Pod: {pod}
Log: {log}
"""

                    print(msg)

                    send_telegram(msg)

        time.sleep(2)

    except Exception as e:
        print("Collector error:", e)
        time.sleep(3)