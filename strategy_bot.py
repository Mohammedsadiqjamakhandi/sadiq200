import os
import time
import requests
import pandas as pd
import pyotp
from datetime import datetime, timedelta
from SmartApi.smartConnect import SmartConnect
import talib
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === SmartAPI credentials from .env ===
api_key = os.getenv("ANGEL_API_KEY")
client_code = os.getenv("ANGEL_CLIENT_CODE")
password = os.getenv("ANGEL_PASSWORD")
totp_secret = os.getenv("ANGEL_TOTP")

# === Telegram credentials ===
TELEGRAM_BOT_TOKEN = '7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0'
TELEGRAM_CHAT_ID = '5795808600'

# === CSV path ===
CSV_PATH = 'C:/Users/azt/Desktop/saniya/angel_master_nse.csv'

# === Send Telegram Alert ===
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("📩 Telegram alert sent.")
        else:
            print("❌ Telegram error:", response.text)
    except Exception as e:
        print("❌ Telegram exception:", str(e))

# === Login to SmartAPI ===
def login():
    smart_api = SmartConnect(api_key)
    totp = pyotp.TOTP(totp_secret).now()
    session = smart_api.generateSession(client_code, password, totp)
    if session and session.get('status'):
        print("✅ Logged in.")
        return smart_api
    else:
        print("❌ Login failed.")
        exit()

# === Bollinger Band Strategy Logic ===
def check_bollinger_signal(df):
    close = df['close'].values
    upper, middle, lower = talib.BBANDS(close, timeperiod=20)

    if len(close) < 3:
        return None

    # Get last 3 candles
    c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
    m1, m2, m3 = middle[-3], middle[-2], middle[-1]
    l1, l2, l3 = lower[-3], lower[-2], lower[-1]
    u1, u2, u3 = upper[-3], upper[-2], upper[-1]

    # --- Buy Check ---
    if c1['low'] <= l1 and c1['close'] > l1:
        if all(c['low'] > m for c, m in zip([c1, c2, c3], [m1, m2, m3])):
            if c2['low'] > c1['low'] and c3['low'] > c2['low']:
                if not (c2['high'] > c1['high'] and c1['low'] > c2['low']):
                    return "BUY"

    # --- Sell Check ---
    if c1['high'] >= u1 and c1['close'] < u1:
        if all(c['high'] < m for c, m in zip([c1, c2, c3], [m1, m2, m3])):
            if c2['high'] < c1['high'] and c3['high'] < c2['high']:
                if not (c2['low'] < c1['low'] and c1['high'] < c2['high']):
                    return "SELL"

    return None

# === Main Scanner ===
def run_strategy():
    smart_api = login()

    # Load symbols
    df = pd.read_csv(CSV_PATH)
    symbols = df['SYMBOL'].str.strip().tolist()

    print(f"🔍 Scanning {len(symbols)} symbols...")

    for symbol in symbols[:50]:  # Limit to 50 for speed
        try:
            exchange = "NSE"
            interval = "ONE_MINUTE"
            to_date = datetime.now()
            from_date = to_date - timedelta(minutes=40)

            # NOTE: getCandleData is correct method, not getMasterContract
            historical_data = smart_api.getCandleData({
                "exchange": exchange,
                "symboltoken": "999999",  # Dummy token just for testing
                "interval": interval,
                "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
                "todate": to_date.strftime("%Y-%m-%d %H:%M")
            })

            candles = historical_data['data']
            if candles and len(candles) >= 30:
                df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
                signal = check_bollinger_signal(df)
                if signal:
                    msg = f"{signal} Signal: {symbol} @ ₹{df.iloc[-1]['close']}"
                    print(msg)
                    send_telegram_message(msg)
        except Exception as e:
            print(f"⚠️ Error processing {symbol}: {str(e)}")

# === Run every minute ===
if __name__ == "__main__":
    while True:
        run_strategy()
        print("⏱️ Waiting for next minute...\n")
        time.sleep(60)
