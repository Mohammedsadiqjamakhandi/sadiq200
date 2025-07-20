import os
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
BB_PERIOD = 20
BB_STD = 2
DATA_FOLDER = "data"
NSE200_LIST = "nse200_symbols.csv"  # must contain Symbol column like: RELIANCE, HDFCBANK, etc
SEND_TELEGRAM = True

BOT_TOKEN = "7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0"
CHAT_ID = "5795808600"

def send_telegram(message):
    if not SEND_TELEGRAM:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

# --- Strategy: Your 3-candle BB reversal pattern ---
def check_bollinger_reversal(df):
    signals = []
    if len(df) < BB_PERIOD + 3:
        return signals

    df["MA"] = df["close"].rolling(BB_PERIOD).mean()
    df["STD"] = df["close"].rolling(BB_PERIOD).std()
    df["Upper"] = df["MA"] + BB_STD * df["STD"]
    df["Lower"] = df["MA"] - BB_STD * df["STD"]

    for i in range(BB_PERIOD, len(df)-2):
        c1, c2, c3 = df.iloc[i], df.iloc[i+1], df.iloc[i+2]

        def is_hollow(c): return c["close"] > c["open"]
        def has_body(c): return abs(c["close"] - c["open"]) > 0.1
        def higher_high_low(cA, cB): return cB["high"] > cA["high"] and cB["low"] > cA["low"]
        def touches_lower(c): return c["low"] <= c["Lower"]
        def below_midband(c): return c["high"] < c["MA"] and c["close"] < c["MA"]
        def not_engulfing(cA, cB): return not (cB["open"] < cA["close"] and cB["close"] > cA["open"])

        if (
            is_hollow(c1) and touches_lower(c1) and below_midband(c1)
            and is_hollow(c2) and higher_high_low(c1, c2) and below_midband(c2) and not_engulfing(c1, c2)
            and is_hollow(c3) and higher_high_low(c2, c3) and below_midband(c3) and not_engulfing(c2, c3)
            and has_body(c1) and has_body(c2) and has_body(c3)
        ):
            signals.append((df.index[i+2], "BUY"))

        elif (
            not is_hollow(c1) and c1["high"] >= c1["Upper"] and c1["low"] > c1["MA"]
            and not is_hollow(c2) and c2["low"] < c1["low"] and c2["high"] < c1["high"] and c2["low"] > c2["MA"]
            and not is_hollow(c3) and c3["low"] < c2["low"] and c3["high"] < c2["high"] and c3["low"] > c3["MA"]
            and not_engulfing(c1, c2) and not_engulfing(c2, c3)
            and has_body(c1) and has_body(c2) and has_body(c3)
        ):
            signals.append((df.index[i+2], "SELL"))

    return signals

# --- Backtest Runner ---
def backtest_stock(symbol):
    filepath = f"{DATA_FOLDER}/{symbol}.csv"
    if not os.path.exists(filepath):
        print(f"❌ Missing file: {filepath}")
        return

    df = pd.read_csv(filepath, parse_dates=["timestamp"])
    df.set_index("timestamp", inplace=True)
    df.sort_index(inplace=True)

    signals = check_bollinger_reversal(df)
    for dt, signal in signals:
        msg = f"{signal} signal for {symbol} at {dt.strftime('%Y-%m-%d %H:%M')}"
        print("✅", msg)
        send_telegram(msg)

# --- Run backtest on all NSE 200 ---
if __name__ == "__main__":
    print("🚀 Running backtest on NSE 200 stocks...")

    if not os.path.exists(NSE200_LIST):
        print(f"❌ Missing file: {NSE200_LIST}")
        exit()

    df_symbols = pd.read_csv(NSE200_LIST)
    for symbol in df_symbols["Symbol"]:
        backtest_stock(symbol)
