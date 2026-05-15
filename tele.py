import requests

BOT_TOKEN = "8631408938:AAECCfuK_g0GqOqzKmsjCFHRIWG928vO5XI"
CHAT_ID = "6615540935"

url = f"https://api.telegram.org/bot8631408938:AAECCfuK_g0GqOqzKmsjCFHRIWG928vO5XI/sendMessage"

r = requests.post(
    url,
    json={
        "chat_id": CHAT_ID,
        "text": "hello"
    }
)

print(r.status_code)
print(r.text)
