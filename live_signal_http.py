import os
import time
import pandas as pd
from SmartApi.smartConnect import SmartConnect
from dotenv import load_dotenv

# 🔐 Load .env credentials
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# 🔢 TOTP generation
import pyotp
def generate_totp():
    return pyotp.TOTP(TOTP_SECRET).now()

# 🚀 Login
print("🚀 Logging in...")
obj = SmartConnect(api_key=API_KEY)
data = obj.generateSession(CLIENT_CODE, PASSWORD, generate_totp())
refreshToken = data['data']['refreshToken']
feedToken = obj.getfeedToken()
print("✅ Login successful.")

# 📁 Load symbols and tokens
df = pd.read_csv("nse_eq_symbols.csv")
if "symbol" not in df.columns or "token" not in df.columns:
    raise Exception("❌ CSV must have columns: symbol,token")

symbols = df["symbol"].tolist()
tokens = df["token"].astype(str).tolist()
print(f"📡 Tracking {len(symbols)} stocks...")

# 🔁 Fetch LTP data
for symbol, token in zip(symbols, tokens):
    try:
        ltp_data = obj.ltpData("NSE", symbol, token)
        ltp = ltp_data["data"]["ltp"]
        print(f"📊 {symbol} LTP: {ltp}")
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
    time.sleep(0.1)  # To avoid hitting rate limits
