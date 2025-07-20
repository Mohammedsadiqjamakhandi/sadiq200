import os
import time
import pandas as pd
import numpy as np
import requests
import pyotp
from datetime import datetime
from collections import defaultdict

# === Credentials ===
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

# === Telegram ===
SEND_TELEGRAM = True
BOT_TOKEN = "7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0"
CHAT_ID = "5795808600"

# === Login and Get Token ===
def generate_totp():
    return pyotp.TOTP(TOTP_SECRET).now()

def smartapi_login():
    print("🚀 Logging in...")
    url = "https://apiconnect.angelone.in/rest/auth/angelbroking/user/v1/loginByPassword"
    headers = {
        "Content-Type": "application/json",
        "X-PrivateKey": API_KEY,
        "Accept": "application/json",
        "X-SourceID": "WEB",
        "X-ClientLocalIP": "127.0.0.1",
        "X-ClientPublicIP": "127.0.0.1",
        "X-MACAddress": "00:00:00:00:00:00",
        "X-UserType": "USER"
    }
    payload = {
        "clientcode": CLIENT_CODE,
        "password": PASSWORD,
        "totp": generate_totp()
    }
    res = requests.post(url, headers=headers, json=payload).json()
    return res["data"]["jwtToken"], res["data"]["feedToken"]

jwt_token, feed_token = smartapi_login()
headers = {
    "Authorization": f"Bearer {jwt_token}",
    "X-PrivateKey": API_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# === Load NSE 200 Symbols ===
df_tokens = pd.read_csv("nse200_market.csv")  # must contain columns: symbol, token
symbols = df_tokens["symbol"].tolist()
token_map = dict(zip(df_tokens["symbol"], df_tokens["token"]))

# === Strategy State ===
candles = defaultdict(list)

def send_telegram(msg):
    if not SEND_TELEGRAM:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=payload)
    except:
        pass

def fetch_ltp(symbol):
    token = str(token_map[symbol])
    url = "https://apiconnect.angelone.in/rest/secure/angelbroking/order/v1/getLtpData"
    payload = {
        "mode": "LTP",
        "exchange": "NSE",
        "symboltoken": token,
        "tradingsymbol": symbol,
        "exchangeType": "1"
    }
    try:
        res = requests.post(url, headers=headers, json=payload).json()
        return float(res["data"]["ltp"])
    except:
        return None

def build_candle(symbol, ltp):
    now = datetime.now()
    minute = now.strftime("%Y-%m-%d %H:%M")
    c = candles[symbol]

    if not c or c[-1]["minute"] != minute:
        # Start new candle
        candles[symbol].append({
            "minute": minute,
            "open": ltp,
            "high": ltp,
            "low": ltp,
            "close": ltp
        })
        if len(candles[symbol]) > 50:
            candles[symbol] = candles[symbol][-50:]
    else:
        # Update current candle
        c[-1]["high"] = max(c[-1]["high"], ltp)
        c[-1]["low"] = min(c[-1]["low"], ltp)
        c[-1]["close"] = ltp

def check_signal(symbol):
    df = pd.DataFrame(candles[symbol])
    if len(df) < 23:
        return
    df["mid"] = df["close"].rolling(20).mean()
    df["std"] = df["close"].rolling(20).std()
    df["upper"] = df["mid"] + 2 * df["std"]
    df["lower"] = df["mid"] - 2 * df["std"]

    last3 = df.iloc[-3:]
    if len(last3) < 3:
        return

    def is_hollow(c): return c["close"] > c["open"] and abs(c["close"] - c["open"]) > 0.1

    c1, c2, c3 = last3.iloc[0], last3.iloc[1], last3.iloc[2]

    # BUY Condition
    if (
        is_hollow(c1) and c1["low"] <= c1["lower"] and
        is_hollow(c2) and is_hollow(c3) and
        c2["high"] > c1["high"] and c2["low"] > c1["low"] and
        c3["high"] > c2["high"] and c3["low"] > c2["low"] and
        all(c["close"] < c["mid"] and c["open"] < c["mid"] for c in [c1, c2, c3])
    ):
        msg = f"📈 BUY: {symbol} at {c3['close']} ({c3['minute']})"
        print(msg)
        send_telegram(msg)
        log_signal(symbol, "BUY", c3['close'], c3['minute'])

    # SELL Condition
    if (
        not is_hollow(c1) and c1["high"] >= c1["upper"] and
        not is_hollow(c2) and not is_hollow(c3) and
        c2["high"] < c1["high"] and c2["low"] < c1["low"] and
        c3["high"] < c2["high"] and c3["low"] < c2["low"] and
        all(c["close"] > c["mid"] and c["open"] > c["mid"] for c in [c1, c2, c3])
    ):
        msg = f"📉 SELL: {symbol} at {c3['close']} ({c3['minute']})"
        print(msg)
        send_telegram(msg)
        log_signal(symbol, "SELL", c3['close'], c3['minute'])

def log_signal(symbol, side, price, time_str):
    with open("live_signals.csv", "a") as f:
        f.write(f"{time_str},{symbol},{side},{price}\n")

# === Main Loop ===
print(f"📡 Tracking {len(symbols)} NSE 200 stocks...")
while True:
    for symbol in symbols:
        ltp = fetch_ltp(symbol)
        if ltp:
            build_candle(symbol, ltp)
            check_signal(symbol)
        time.sleep(0.4)  # respect rate limits
