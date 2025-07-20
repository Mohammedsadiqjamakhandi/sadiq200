import os
import time
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from SmartApi.smartConnect import SmartConnect
import pyotp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# === Setup ===
INTERVAL = 60  # seconds for 1-minute candle
symbol_df = pd.read_csv("nifty_200.csv")
symbols = symbol_df["symbol"].tolist()
live_data = {sym: [] for sym in symbols}
candles = {sym: [] for sym in symbols}

# === Login ===
print("🚀 Logging in...")
smart_api = SmartConnect(api_key=API_KEY)
totp = pyotp.TOTP(TOTP_SECRET).now()
session = smart_api.generate_session(CLIENT_CODE, PASSWORD, totp)
auth_token = session["data"]["access_token"]
feed_token = smart_api.getfeedToken()

# === Telegram ===
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=data)
    except:
        pass

# === LTP fetch ===
def fetch_ltp(symbol):
    try:
        params = {
            "exchange": "NSE",
            "tradingsymbol": symbol,
            "symboltoken": smart_api.get_instrument_by_symbol("NSE", symbol)["token"]
        }
        res = smart_api.ltpData(params)
        return float(res["data"]["ltp"])
    except:
        return None

# === Bollinger Band Calc ===
def get_bbands(prices, window=20, num_std=2):
    series = pd.Series(prices)
    mid = series.rolling(window).mean()
    std = series.rolling(window).std()
    upper = mid + num_std * std
    lower = mid - num_std * std
    return upper, mid, lower

# === Signal Logic ===
def check_signal(symbol):
    df = pd.DataFrame(candles[symbol], columns=["time", "open", "high", "low", "close"])
    if len(df) < 30:
        return

    upper, mid, lower = get_bbands(df["close"])
    df["upper"] = upper
    df["mid"] = mid
    df["lower"] = lower

    last3 = df.iloc[-3:]
    b1, b2, b3 = last3.iloc[0], last3.iloc[1], last3.iloc[2]

    def is_hollow(c): return c["close"] > c["open"] and abs(c["close"] - c["open"]) > 0.1
    def is_bearish(c): return c["open"] > c["close"] and abs(c["open"] - c["close"]) > 0.1
    def not_engulfing(c1, c2): return c2["open"] > c1["open"] and c2["close"] > c1["close"]

    # Buy Signal
    if (
        is_hollow(b1) and
        b1["low"] <= b1["lower"] and
        is_hollow(b2) and is_hollow(b3) and
        b2["high"] > b1["high"] and b2["low"] > b1["low"] and
        b3["high"] > b2["high"] and b3["low"] > b2["low"] and
        b1["close"] < b1["mid"] and b2["close"] < b2["mid"] and b3["close"] < b3["mid"] and
        not_engulfing(b1, b2) and not_engulfing(b2, b3)
    ):
        send_telegram(f"🟢 BUY SIGNAL: {symbol} at {b3['close']}")

    # Sell Signal
    if (
        is_bearish(b1) and
        b1["high"] >= b1["upper"] and
        is_bearish(b2) and is_bearish(b3) and
        b2["high"] < b1["high"] and b2["low"] < b1["low"] and
        b3["high"] < b2["high"] and b3["low"] < b2["low"] and
        b1["close"] > b1["mid"] and b2["close"] > b2["mid"] and b3["close"] > b3["mid"] and
        not_engulfing(b1, b2) and not_engulfing(b2, b3)
    ):
        send_telegram(f"🔴 SELL SIGNAL: {symbol} at {b3['close']}")

# === Main Loop ===
print(f"📡 Tracking {len(symbols)} Nifty 200 stocks...\n")
send_telegram("🚀 Live strategy started. Tracking Nifty 200 stocks.")

start = datetime.now()
while True:
    now = datetime.now()
    for symbol in symbols:
        ltp = fetch_ltp(symbol)
        if ltp:
            live_data[symbol].append((now, ltp))

    if (datetime.now() - start).seconds >= INTERVAL:
        for symbol in symbols:
            prices = live_data[symbol]
            if len(prices) == 0: continue
            o = prices[0][1]
            h = max(x[1] for x in prices)
            l = min(x[1] for x in prices)
            c = prices[-1][1]
            candles[symbol].append((now.strftime("%H:%M"), o, h, l, c))
            if len(candles[symbol]) >= 30:
                check_signal(symbol)
            live_data[symbol] = []
        start = datetime.now()

    time.sleep(2)
