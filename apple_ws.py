import os
import json
import time
import pandas as pd
import numpy as np
from datetime import datetime
from angel_one.smartconnect import SmartConnect
from smartapi.ws import SmartWebSocketV2
import pyotp
import requests

# === Config ===
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"
BOT_TOKEN = "7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0"
CHAT_ID = "5795808600"

NSE200_SYMBOLS = ["RELIANCE-EQ", "HDFCBANK-EQ", "INFY-EQ", "TCS-EQ"]  # Add all NSE200 here
TOKEN_MAP = {}  # token: symbol
CANDLES = {}  # symbol: list of candles

def generate_totp():
    return pyotp.TOTP(TOTP_SECRET).now()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print("❌ Telegram error:", e)

def create_candle(symbol, ltp):
    now = datetime.now()
    minute = now.replace(second=0, microsecond=0)
    candles = CANDLES.setdefault(symbol, [])

    if not candles or candles[-1]["time"] != minute:
        # start new candle
        candles.append({
            "time": minute,
            "open": ltp,
            "high": ltp,
            "low": ltp,
            "close": ltp
        })
        if len(candles) > 50:
            candles.pop(0)
    else:
        # update last candle
        candle = candles[-1]
        candle["high"] = max(candle["high"], ltp)
        candle["low"] = min(candle["low"], ltp)
        candle["close"] = ltp

def calculate_bollinger(df):
    df["ma"] = df["close"].rolling(20).mean()
    df["std"] = df["close"].rolling(20).std()
    df["upper"] = df["ma"] + 2 * df["std"]
    df["lower"] = df["ma"] - 2 * df["std"]
    return df

def is_hollow(candle):
    return candle["close"] > candle["open"]

def check_strategy(symbol):
    df = pd.DataFrame(CANDLES[symbol])
    if len(df) < 25:
        return
    df = calculate_bollinger(df)
    last3 = df.iloc[-3:]

    c1, c2, c3 = last3.iloc[0], last3.iloc[1], last3.iloc[2]

    if (
        is_hollow(c1) and c1["low"] <= c1["lower"] and
        is_hollow(c2) and is_hollow(c3) and
        c2["high"] > c1["high"] and c2["low"] > c1["low"] and
        c3["high"] > c2["high"] and c3["low"] > c2["low"] and
        all(c["close"] < c["ma"] and c["high"] < c["ma"] for c in [c1, c2, c3])
    ):
        send_telegram(f"📈 BUY signal: {symbol} at ₹{round(c3['close'], 2)}")

    elif (
        not is_hollow(c1) and c1["high"] >= c1["upper"] and
        not is_hollow(c2) and not is_hollow(c3) and
        c2["high"] < c1["high"] and c2["low"] < c1["low"] and
        c3["high"] < c2["high"] and c3["low"] < c2["low"] and
        all(c["close"] > c["ma"] and c["low"] > c["ma"] for c in [c1, c2, c3])
    ):
        send_telegram(f"📉 SELL signal: {symbol} at ₹{round(c3['close'], 2)}")

# === Login ===
print("🚀 Logging in...")
obj = SmartConnect(api_key=API_KEY)
data = obj.generate_session(CLIENT_CODE, PASSWORD, generate_totp())
auth_token = data["data"]["jwtToken"]
feed_token = obj.getfeedToken()
profile = obj.get_profile()

# === Token Mapping ===
instruments = pd.read_csv("instruments.csv")  # Full NSE file from Angel One
for sym in NSE200_SYMBOLS:
    row = instruments[(instruments["name"] == sym.split("-")[0]) & (instruments["symbol"] == sym)]
    if not row.empty:
        token = str(row.iloc[0]["token"])
        TOKEN_MAP[token] = sym

print("📡 Subscribing to:", list(TOKEN_MAP.values()))

# === WebSocket ===
sws = SmartWebSocketV2(Apikey=API_KEY, ClientId=CLIENT_CODE, FeedToken=feed_token)

@sws.on_open
def open_handler():
    print("✅ WebSocket connected. Subscribing tokens...")
    sws.subscribe([{"exchangeType": 1, "tokens": list(TOKEN_MAP.keys())}])

@sws.on_data
def data_handler(msg):
    token = str(msg["token"])
    ltp = float(msg["last_traded_price"]) / 100
    symbol = TOKEN_MAP.get(token)
    if symbol:
        create_candle(symbol, ltp)
        check_strategy(symbol)

@sws.on_error
def error_handler(err):
    print("❌ WebSocket error:", err)

@sws.on_close
def close_handler():
    print("🔌 WebSocket closed. Reconnecting in 5s...")
    time.sleep(5)
    sws.connect()

# === Start ===
sws.connect()
