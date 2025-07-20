import requests

# ✅ Replace with your actual values
TELEGRAM_BOT_TOKEN = "7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0"
TELEGRAM_CHAT_ID = "5795808600"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload)
        print("📨 Telegram status:", response.status_code, response.text)
    except Exception as e:
        print("❌ Telegram Error:", e)

# 🚨 Only send this one safe message
send_telegram("✅ This is a safe test from your bot.")
