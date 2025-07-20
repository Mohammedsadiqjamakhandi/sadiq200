import requests

# Telegram credentials
TELEGRAM_BOT_TOKEN = '7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0'
TELEGRAM_CHAT_ID = '5795808600'

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("📩 Telegram alert sent.")
        else:
            print("❌ Failed to send Telegram message.")
    except Exception as e:
        print("❌ Error sending Telegram message:", str(e))
