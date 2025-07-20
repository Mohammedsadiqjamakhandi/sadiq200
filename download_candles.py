import os
import pandas as pd
from datetime import datetime, timedelta
from SmartApi.smartConnect import SmartConnect
import pyotp
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# Login to SmartAPI
smart_api = SmartConnect(api_key=API_KEY)
token = pyotp.TOTP(TOTP_SECRET).now()
smart_api.generateSession(CLIENT_CODE, PASSWORD, token)
print("✅ Login successful.")

# Config
symbol = "RELIANCE-EQ"
symbol_token = "2885"  # RELIANCE-EQ token
exchange = "NSE"
interval = "ONE_MINUTE"
date = datetime.today() - timedelta(days=1)

from_date = datetime.combine(date.date(), datetime.min.time())
to_date = datetime.combine(date.date(), datetime.max.time())

print(f"📥 Downloading {symbol} candles for {from_date.date()}...")

# ✅ WORKING FOR LATEST SDK
params = {
    "exchange": exchange,
    "symboltoken": symbol_token,
    "tradingsymbol": symbol,
    "interval": interval,
    "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
    "todate": to_date.strftime("%Y-%m-%d %H:%M")
}

response = smart_api.getCandleData(params)

# Save to CSV
candles = response["data"]
df = pd.DataFrame(candles, columns=["time", "open", "high", "low", "close", "volume"])
df.to_csv("RELIANCE.csv", index=False)
print("✅ Saved to RELIANCE.csv")
