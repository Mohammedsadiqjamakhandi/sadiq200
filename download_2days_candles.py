import os
import pandas as pd
from datetime import datetime, timedelta
from SmartApi.smartConnect import SmartConnect
import pyotp
import time

# === Angel One Login Credentials ===
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

# === Load NSE 200 stock symbols ===
nse200_df = pd.read_csv("nse200.csv")  # Must have column 'symbol'
symbols = nse200_df['symbol'].tolist()

# === Load instrument tokens ===
instrument_df = pd.read_csv("instruments.csv")
instrument_df = instrument_df[instrument_df['exchange'] == "NSE"]

# === Login ===
print("🚀 Logging in...")
obj = SmartConnect(api_key=API_KEY)
totp = pyotp.TOTP(TOTP_SECRET).now()
try:
    data = obj.generate_session(CLIENT_CODE, PASSWORD, totp)
    if "data" not in data:
        print("❌ Login failed:", data)
        exit()
    print("✅ Login successful")
except Exception as e:
    print("❌ Login error:", e)
    exit()

# === Time Range: last 2 days ===
to_date = datetime.now()
from_date = to_date - timedelta(days=2)

# === Loop through all NSE 200 symbols ===
for symbol in symbols:
    try:
        row = instrument_df[instrument_df['symbol'] == symbol]
        if row.empty:
            print(f"⚠️ Skipping {symbol}: token not found")
            continue

        token = str(int(row['token'].values[0]))
        print(f"📥 {symbol} | Token: {token}")

        params = {
            "exchange": "NSE",
            "symboltoken": token,
            "interval": "ONE_MINUTE",
            "fromdate": from_date.strftime('%Y-%m-%d %H:%M'),
            "todate": to_date.strftime('%Y-%m-%d %H:%M')
        }

        data = obj.getCandleData(params)
        candles = data['data']

        df = pd.DataFrame(candles, columns=["datetime", "open", "high", "low", "close", "volume"])
        filename = f"data/{symbol.replace('-EQ', '')}_2days.csv"
        os.makedirs("data", exist_ok=True)
        df.to_csv(filename, index=False)
        print(f"✅ Saved {filename}")
        time.sleep(0.5)  # avoid rate limit

    except Exception as e:
        print(f"❌ Error for {symbol}: {e}")
