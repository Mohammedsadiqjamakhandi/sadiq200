import os
from datetime import datetime, timedelta
import pandas as pd
from SmartApi.smartConnect import SmartConnect
import pyotp
from dotenv import load_dotenv

# Load .env credentials
load_dotenv()
api_key = os.getenv("ANGEL_API_KEY")
client_code = os.getenv("ANGEL_CLIENT_CODE")
password = os.getenv("ANGEL_PASSWORD")
totp_secret = os.getenv("TOTP_SECRET")

# Login to Angel One
smart_api = SmartConnect(api_key)
totp = pyotp.TOTP(totp_secret).now()
session = smart_api.generateSession(client_code, password, totp)

print("✅ Logged in successfully")

# === CONFIG ===
symbol = "TATAMOTORS"
symbol_token = "2885"  # update based on your token map
exchange = "NSE"
interval = "ONE_MINUTE"
days = 1  # how many past days

# === Time Range ===
to_date = datetime.now()
from_date = to_date - timedelta(days=days)

from_str = from_date.strftime('%Y-%m-%d %H:%M')
to_str = to_date.strftime('%Y-%m-%d %H:%M')

# === Fetch Data ===
params = {
    "exchange": exchange,
    "symboltoken": symbol_token,
    "interval": interval,
    "fromdate": from_str,
    "todate": to_str
}

try:
    response = smart_api.getCandleData(params)
    candles = response.get("data", [])
    if not candles:
        print("⚠️ No data found.")
    else:
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        filename = f"{symbol}_1min_candles.csv"
        df.to_csv(filename, index=False)
        print(f"📁 Saved to {filename}")
except Exception as e:
    print(f"❌ Error: {e}")
