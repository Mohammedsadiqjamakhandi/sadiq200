import os
import time
import pandas as pd
import requests
from SmartApi.smartConnect import SmartConnect
from dotenv import load_dotenv
import pyotp
import numpy as np

# Load .env credentials
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

def generate_totp():
    return pyotp.TOTP(TOTP_SECRET).now()

# Login
print("🚀 Logging in...")
obj = SmartConnect(api_key=API_KEY)
data = obj.generateSession(CLIENT_CODE, PASSWORD, generate_totp())
refreshToken = data['data']['refreshToken']
feedToken = obj.getfeedToken()
print("✅ Login successful.")

# Load NSE 200 symbols and tokens
df = pd.read_csv("nse200_symbols.csv")
if "symbol" not in df.columns or "token" not in df.columns:
    raise Exception("❌ CSV must have columns: symbol,token")

symbols = df["symbol"].tolist()
tokens = df["token"].astype(str).tolist()
print(f"📡 Tracking {len(symbols)} NSE 200 stocks...")

# Telegram details
TELEGRAM_BOT_TOKEN = "<your_bot_token_here>"
TELEGRAM_CHAT_ID = "<your_chat_id_here>"

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"📨 Telegram alert sent: {message}")
        else:
            print(f"⚠️ Telegram failed: {response.text}")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

def is_hollow_candle(open_, close):
    return close > open_

def check_bollinger_band_signal(df):
    """
    df: DataFrame with 1-min candles with columns: ['Open', 'High', 'Low', 'Close']
    Assumes 'Upper', 'Middle', 'Lower' Bollinger Bands columns are added already.
    Returns 'BUY' or 'SELL' or None.
    """

    # Require at least 3 candles for pattern
    if len(df) < 3:
        return None

    # Use last 3 candles
    last3 = df.iloc[-3:].copy()

    # Check all 3 candles are hollow (close > open)
    if not all(is_hollow_candle(row['Open'], row['Close']) for idx, row in last3.iterrows()):
        return None

    # Check none of 3 candles touch or close above middle BB line
    if (last3[['High', 'Close']] >= last3['Middle'].values.reshape(-1,1)).any().any():
        return None

    # Check 1st candle touches lower BB and closes reversing upward (close > open)
    c1 = last3.iloc[0]
    if c1['Low'] > c1['Lower']:  # first candle must touch or go below lower BB
        return None

    # Check candle 2 and 3 higher highs and higher lows, no engulfing
    c2 = last3.iloc[1]
    c3 = last3.iloc[2]

    if not (c2['High'] > c1['High'] and c2['Low'] > c1['Low']):
        return None
    if not (c3['High'] > c2['High'] and c3['Low'] > c2['Low']):
        return None

    # Check bodies (no doji)
    def body_size(row):
        return abs(row['Close'] - row['Open'])
    if any(body_size(row) < 0.0001 for idx, row in last3.iterrows()):
        return None

    # Passed all checks, signal BUY
    return "BUY"

# You can implement SELL similarly by mirror image if you want.

# For this example, we only implement BUY signal detection.

# We'll keep last candle data stored here per symbol
candle_data = {symbol: pd.DataFrame() for symbol in symbols}

while True:
    for symbol, token in zip(symbols, tokens):
        try:
            # Fetch latest LTP
            ltp_data = obj.ltpData("NSE", symbol, token)
            ltp = ltp_data["data"]["ltp"]
            print(f"📊 {symbol} LTP: {ltp}")

            # Build 1-min candle data here.
            # For simplicity, we assume you get or store 1-min OHLC candles from somewhere,
            # but since SmartAPI HTTP doesn't provide historical 1-min candles directly,
            # you must implement or use websocket or other method.
            # Here just a placeholder empty DataFrame:
            df_candles = candle_data[symbol]

            # For demonstration, we skip candle update and signal check:
            # Replace with your actual candle updating logic here.

            # signal = check_bollinger_band_signal(df_candles)

            # For demo only, let's say no signal:
            signal = None

            if signal in ['BUY', 'SELL']:
                msg = f"<b>{symbol}</b>: {signal} signal at LTP {ltp}"
                send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, msg)

        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")

        time.sleep(0.15)

    print("⏳ Cycle complete, sleeping 30 seconds...\n")
    time.sleep(30)
