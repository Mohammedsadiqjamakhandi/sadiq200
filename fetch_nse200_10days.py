import os
import time
import pandas as pd
import numpy as np
import requests
import pyotp
from datetime import datetime, timedelta
from SmartApi.smartConnect import SmartConnect

# === Load credentials from .env ===
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

NSE200_LIST = "nse200.csv"
INSTRUMENTS_FILE = "instruments.csv"
OUTPUT_FOLDER = "nse200_candles"

# === Login ===
totp = pyotp.TOTP(TOTP_SECRET).now()
obj = SmartConnect(api_key=API_KEY)
data = obj.generateSession(CLIENT_CODE, PASSWORD, totp)
authToken = data['data']['jwtToken']
refreshToken = data['data']['refreshToken']
feedToken = obj.getfeedToken()

print("✅ Logged in.")

# === Load instruments file ===
df_instruments = pd.read_csv(INSTRUMENTS_FILE, low_memory=False)

# FIX: Use correct column for exchange/segment
if 'exchange' in df_instruments.columns:
    df_instruments = df_instruments[df_instruments['exchange'] == 'NSE']
elif 'exch_seg' in df_instruments.columns:
    df_instruments = df_instruments[df_instruments['exch_seg'] == 'NSE']
else:
    raise Exception("❌ 'exchange' or 'exch_seg' column not found in instruments.csv")

# === Load NSE200 list ===
df_nse200 = pd.read_csv(NSE200_LIST)
nse200_symbols = df_nse200['Symbol'].tolist()

# === Filter only EQ series NSE200 stocks ===
df_filtered = df_instruments[df_instruments['symbol'].isin(nse200_symbols)]
df_filtered = df_filtered[df_filtered['instrumenttype'] == 'EQ']

# === Prepare output folder ===
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Time range for last 10 days ===
to_date = datetime.now()
from_date = to_date - timedelta(days=10)

def get_candles(symbol, token):
    try:
        params = {
            "exchange": "NSE",
            "symboltoken": str(token),
            "interval": "ONE_MINUTE",
            "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
            "todate": to_date.strftime("%Y-%m-%d %H:%M")
        }
        response = obj.getCandleData(params)
        if response["status"] and response["data"]:
            data = response["data"]
            df = pd.DataFrame(data, columns=["datetime", "open", "high", "low", "close", "volume"])
            df.to_csv(f"{OUTPUT_FOLDER}/{symbol}.csv", index=False)
            print(f"✅ Saved: {symbol}")
        else:
            print(f"⚠️ No data: {symbol}")
    except Exception as e:
        print(f"❌ Error for {symbol}: {e}")

# === Fetch candles for each stock ===
print(f"📥 Downloading 1-min candles for {len(df_filtered)} NSE 200 stocks...")

for index, row in df_filtered.iterrows():
    symbol = row['symbol']
    token = row['token']
    get_candles(symbol, token)
    time.sleep(0.5)  # to avoid rate limits

print("✅ Done.")
