import os
import pandas as pd
from datetime import datetime, timedelta
from SmartApi.smartConnect import SmartConnect
import pyotp
from dotenv import load_dotenv

# Load credentials
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# Login
smart_api = SmartConnect(api_key=API_KEY)
token = pyotp.TOTP(TOTP_SECRET).now()
smart_api.generateSession(CLIENT_CODE, PASSWORD, token)
print("✅ Login successful.")

# Config
symbol = "RELIANCE-EQ"
symbol_token = "2885"
exchange = "NSE"
interval = "ONE_MINUTE"
days_to_fetch = 3  # Fetch last 3 trading days

all_candles = []

for offset in range(1, days_to_fetch + 1):
    date = datetime.today() - timedelta(days=offset)
    from_date = datetime.combine(date.date(), datetime.min.time())
    to_date = datetime.combine(date.date(), datetime.max.time())

    print(f"📥 Fetching for {date.date()}...")

    params = {
        "exchange": exchange,
        "symboltoken": symbol_token,
        "tradingsymbol": symbol,
        "interval": interval,
        "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
        "todate": to_date.strftime("%Y-%m-%d %H:%M")
    }

    try:
        response = smart_api.getCandleData(params)
        candles = response["data"]
        all_candles.extend(candles)
    except Exception as e:
        print(f"❌ Error fetching for {date.date()}: {e}")

# Save all candles to a single CSV
df = pd.DataFrame(all_candles, columns=["time", "open", "high", "low", "close", "volume"])
df.to_csv("RELIANCE.csv", index=False)
print("✅ Saved full history to RELIANCE.csv")

# TEST ONLY: Force a dummy alert
send_telegram("🚨 Test Alert: RELIANCE Buy Signal Simulation")
print("✅ Test signal sent to Telegram.")

