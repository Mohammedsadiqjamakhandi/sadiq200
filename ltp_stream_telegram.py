from smartapi import SmartConnect
import time
import requests

# === CONFIGURATION ===
API_KEY = "your_api_key_here"
USERNAME = "your_client_id"
PASSWORD = "your_password"
TOTP = "your_totp_here"

TELEGRAM_BOT_TOKEN = "7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0"
TELEGRAM_CHAT_ID = "5795808600"

symbols = [
    {"symbol": "RELIANCE-EQ", "exchange": "NSE", "token": "2885"},
    {"symbol": "SBIN-EQ", "exchange": "NSE", "token": "3045"},
    {"symbol": "TCS-EQ", "exchange": "NSE", "token": "11536"}
]

# === LOGIN ===
obj = SmartConnect(api_key=API_KEY)
data = obj.generateSession(USERNAME, PASSWORD, TOTP)
feed_token = data['feedToken']
client_code = data['data']['clientcode']
print(f"✅ Login successful | Client Code: {client_code}")

# === TELEGRAM ALERT FUNCTION ===
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)

# === STREAM LTP LOOP ===
while True:
    print("📈 Fetching LTPs...")
    for s in symbols:
        ltp_data = obj.ltpData(exchange=s["exchange"], tradingsymbol=s["symbol"], symboltoken=s["token"])
        ltp = ltp_data["data"]["ltp"]
        message = f"📈 {s['symbol']}: ₹{ltp}"
        print(message)
        send_telegram(message)
    time.sleep(60)  # wait 60 seconds before next fetch
