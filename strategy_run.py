import os
import time
import pandas as pd
import datetime
import requests
from SmartApi.smartConnect import SmartConnect
from dotenv import load_dotenv
import pyotp

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

TELEGRAM_TOKEN = "7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0"
CHAT_ID = "5795808600"

def generate_totp():
    return pyotp.TOTP(TOTP_SECRET).now()

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("❌ Telegram send failed:", e)

def calculate_bbands(prices, period=20, std_dev=2):
    if len(prices) < period:
        return None, None, None
    sma = prices[-period:].mean()
    std = prices[-period:].std()
    upper = sma + std_dev * std
    lower = sma - std_dev * std
    return upper, sma, lower

symbol_data = {}
alerted = set()

def update_candles(symbol, ltp):
    now = datetime.datetime.now()
    minute = now.replace(second=0, microsecond=0)
    if symbol not in symbol_data:
        symbol_data[symbol] = pd.DataFrame([{"time": minute, "close": ltp}])
        return
    df = symbol_data[symbol]
    if not df.empty and df.iloc[-1]["time"] == minute:
        symbol_data[symbol].at[df.index[-1], "close"] = ltp
    else:
        new_row = pd.DataFrame([{"time": minute, "close": ltp}])
        symbol_data[symbol] = pd.concat([df, new_row], ignore_index=True)

def check_signal(symbol):
    df = symbol_data[symbol]
    if len(df) < 5:
        return
    closes = df["close"]
    upper, middle, lower = calculate_bbands(closes)
    if upper is None:
        return
    last = df.iloc[-3:]
    c1, c2, c3 = last["close"].values
    # Buy condition
    if (
        c1 < lower and
        c2 > c1 and
        c3 > c2 and
        all(x < middle for x in [c1, c2, c3]) and
        f"{symbol}_BUY" not in alerted
    ):
        msg = f"🟢 BUY SIGNAL: {symbol}\nLTP: {df.iloc[-1]['close']}"
        print(msg)
        send_telegram(msg)
        alerted.add(f"{symbol}_BUY")
    # Sell condition
    elif (
        c1 > upper and
        c2 < c1 and
        c3 < c2 and
        all(x > middle for x in [c1, c2, c3]) and
        f"{symbol}_SELL" not in alerted
    ):
        msg = f"🔴 SELL SIGNAL: {symbol}\nLTP: {df.iloc[-1]['close']}"
        print(msg)
        send_telegram(msg)
        alerted.add(f"{symbol}_SELL")

print("🚀 Logging in...")
obj = SmartConnect(api_key=API_KEY)
data = obj.generateSession(CLIENT_CODE, PASSWORD, generate_totp())
print("✅ Logged in successfully.")

# Your watchlist symbols
symbols = ["RELIANCE-EQ", "HDFCBANK-EQ", "INFY-EQ", "ICICIBANK-EQ", "TCS-EQ"]

# Fetch fresh tokens for symbols
symbol_token_map = {}
for symbol in symbols:
    try:
        info = obj.getTokenInfo(exchange="NSE", symbol=symbol)
        token = info.get("token")
        if token:
            symbol_token_map[symbol] = token
            print(f"✅ Token fetched: {symbol} -> {token}")
        else:
            print(f"❌ No token found for {symbol}")
    except Exception as e:
        print(f"❌ Error fetching token for {symbol}: {e}")

print(f"📡 Tracking {len(symbol_token_map)} stocks...")

while True:
    for symbol, token in symbol_token_map.items():
        try:
            ltp_data = obj.ltpData("NSE", symbol, token)
            ltp = float(ltp_data["data"]["ltp"])
            print(f"📊 {symbol} LTP: {ltp}")
            update_candles(symbol, ltp)
            check_signal(symbol)
        except Exception as e:
            print(f"❌ Error fetching LTP for {symbol}: {e}")
        time.sleep(0.1)  # To avoid rate limiting
    print("⏳ Waiting for next candle...\n")
    time.sleep(60)
