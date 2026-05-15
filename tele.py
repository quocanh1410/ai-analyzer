# import requests

# BOT_TOKEN = "8631408938:AAGjG4eMXfbs93kcURoh-3VSIHgLt3AXDf0"
# CHAT_ID = "6615540935"

# url = f"https://api.telegram.org/bot8631408938:AAGjG4eMXfbs93kcURoh-3VSIHgLt3AXDf0/sendMessage"

# r = requests.post(
#     url,
#     json={
#         "chat_id": CHAT_ID,
#         "text": "hello"
#     }
# )

# print(r.status_code)
# print(r.text)


import os
import requests
from dotenv import load_dotenv

# load biến từ file .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

r = requests.post(
    url,
    json={
        "chat_id": CHAT_ID,
        "text": "hello"
    }
)

print(r.status_code)
print(r.text)




