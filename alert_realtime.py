# import requests
# import time
# import os
# from dotenv import load_dotenv

# # ===== TELEGRAM CONFIG =====
# load_dotenv()
# BOT_TOKEN = os.getenv("BOT_TOKEN")
# CHAT_ID = os.getenv("CHAT_ID")

# def send_telegram(message: str):
#     url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

#     try:
#         requests.post(
#             url,
#             json={
#                 "chat_id": CHAT_ID,
#                 "text": message
#             },
#             timeout=5
#         )
#     except Exception as e:
#         print("Telegram error:", e)


# # ===== LOKI CONFIG =====
# LOKI_URL = "http://localhost:3100/loki/api/v1/query"

# query = {
#     "query": '{job=~".+"}',
#     "limit": 50,
#     "direction": "backward"
# }

# # tránh gửi trùng log
# seen = set()

# # từ khóa lỗi
# ERROR_KEYWORDS = [
#     "error", "warn", "failed", "timeout",
#     "exception", "refused", "bad address",
#     "no route", "crash", "oom", "killed"
# ]

# def is_error(log: str):
#     log_lower = log.lower()
#     return any(k in log_lower for k in ERROR_KEYWORDS)


# print("🚀 Realtime collector started...")

# while True:

#     try:
#         r = requests.get(LOKI_URL, params=query, timeout=5)
#         data = r.json()

#         for stream in data.get("data", {}).get("result", []):

#             job = stream["stream"].get("job", "unknown")
#             pod = stream["stream"].get("pod", "unknown")

#             for ts, log in stream["values"]:

#                 key = f"{ts}:{log}"

#                 if key in seen:
#                     continue

#                 seen.add(key)

#                 if is_error(log):

#                     msg = f"""🚨 Kubernetes Alert

# Job: {job}
# Pod: {pod}
# Log: {log}
# """

#                     print(msg)

#                     send_telegram(msg)

#         time.sleep(2)

#     except Exception as e:
#         print("Collector error:", e)
#         time.sleep(3)


import requests
import time
import os
from dotenv import load_dotenv

# ===== CONFIG =====
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LOKI_URL = "http://localhost:3100/loki/api/v1/query"

ERROR_KEYWORDS = [
    "error", "warn", "failed", "timeout",
    "exception", "refused", "bad address",
    "no route", "crash", "oom", "killed"
]

COOLDOWN_SECONDS = 300  # 5 phút, cùng 1 lỗi từ cùng 1 pod sẽ không gửi lại

# ===== TELEGRAM =====
def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(
            url,
            json={"chat_id": CHAT_ID, "text": message},
            timeout=5
        )
    except Exception as e:
        print("Telegram error:", e)

# ===== HELPERS =====
def is_error(log: str) -> bool:
    return any(k in log.lower() for k in ERROR_KEYWORDS)

def get_alert_key(job: str, pod: str, log: str) -> str:
    # Key dựa trên pod + 50 ký tự đầu của log (tránh key quá dài)
    return f"{job}:{pod}:{log[:50]}"

# ===== MAIN LOOP =====
last_ts = str(time.time_ns())
alert_cooldown = {}  # key -> timestamp lần cuối gửi

print("🚀 Realtime collector started...")

while True:
    try:
        query = {
            "query": '{job=~".+", job!~"kube-system.*"}',
            "limit": 50,
            "direction": "forward",
            "start": last_ts
        }

        r = requests.get(LOKI_URL, params=query, timeout=5)
        data = r.json()

        for stream in data.get("data", {}).get("result", []):
            job = stream["stream"].get("job", "unknown")
            pod = stream["stream"].get("pod", "unknown")

            for ts, log in stream["values"]:
                if int(ts) >= int(last_ts):
                    last_ts = str(int(ts) + 1)

                if not is_error(log):
                    continue

                key = get_alert_key(job, pod, log)
                now = time.time()
                last_sent = alert_cooldown.get(key, 0)

                if now - last_sent < COOLDOWN_SECONDS:
                    continue  # Bỏ qua, chưa hết cooldown

                # Gửi alert và cập nhật cooldown
                alert_cooldown[key] = now

                msg = (
                    f"🚨 Kubernetes Alert\n"
                    f"Job: {job}\n"
                    f"Pod: {pod}\n"
                    f"Log: {log}"
                )
                print(msg)
                send_telegram(msg)

        time.sleep(2)

    except Exception as e:
        print("Collector error:", e)
        time.sleep(3)