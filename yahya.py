import os
import time
import pandas as pd
from dotenv import load_dotenv
from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger

# Load credentials from .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# Generate TOTP
totp = pyotp.TOTP(TOTP_SECRET).now()

print("🚀 Logging in...")
smart_api = SmartConnect(api_key=API_KEY)
data = smart_api.generateSession(CLIENT_CODE, PASSWORD, totp)
refreshToken = data['data']['refreshToken']
feedToken = smart_api.getfeedToken()
print("✅ Login successful.")

# Load NSE 200 stock list from tab-separated file
try:
    stock_df = pd.read_csv("nse200_symbols.csv", sep=",")
    stock_df.columns = stock_df.columns.str.strip().str.lower()  # Normalize column names
    print("📄 Columns detected:", stock_df.columns.tolist())

    symbols = stock_df['symbol'].tolist()
    tokens = stock_df['token'].tolist()
except Exception as e:
    print(f"❌ Failed to load symbol list: {e}")
    exit(1)

print(f"📡 Tracking {len(symbols)} NSE 200 stocks...")

while True:
    try:
        for symbol, token in zip(symbols, tokens):
            try:
                ltp_data = smart_api.ltpData(
                    exchange="NSE",
                    tradingsymbol=symbol,
                    symboltoken=str(token)
                )
                ltp = float(ltp_data['data']['ltp'])
                print(f"📊 {symbol} LTP: {ltp}")
            except Exception as e:
                print(f"❌ Error fetching {symbol}: {e}")

        time.sleep(60)  # wait 1 minute

    except KeyboardInterrupt:
        print("🛑 Stopped by user.")
        break
    except Exception as e:
        print(f"❌ Error in main loop: {e}")
        time.sleep(5)
