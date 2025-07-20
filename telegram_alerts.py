import requests

BOT_TOKEN = "7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0"
CHAT_ID = "5795808600"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("📬 Telegram message sent successfully!")
        else:
            print(f"⚠️ Telegram error: {response.text}")
    except Exception as e:
        print("⚠️ Telegram send failed:", e)
