import requests

TELEGRAM_TOKEN = "7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0"
CHAT_ID = "5795808600"
message = "✅ TEST ALERT from your strategy bot!"

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": message}
r = requests.post(url, data=payload)
print(r.text)
