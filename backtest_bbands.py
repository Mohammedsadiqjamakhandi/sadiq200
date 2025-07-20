import os
import pandas as pd
import numpy as np
from tqdm import tqdm
import requests

# === Telegram config ===
SEND_TELEGRAM = True  # Set to False to disable Telegram alerts
BOT_TOKEN = "7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0"
CHAT_ID = "5795808600"

# === Bollinger Band config ===
BB_PERIOD = 20
BB_STD_DEV = 2

# === File paths ===
DATA_FOLDER = r"D:\saniya\candles"
OUTPUT_CSV = "signals.csv"

# === Helper functions ===

def calculate_bbands(df):
    df["ma"] = df["close"].rolling(BB_PERIOD).mean()
    df["std"] = df["close"].rolling(BB_PERIOD).std()
    df["upper"] = df["ma"] + BB_STD_DEV * df["std"]
    df["lower"] = df["ma"] - BB_STD_DEV * df["std"]
    return df

def is_hollow(candle):
    return candle["close"] > candle["open"] and (candle["close"] - candle["open"]) > 0.1

def is_engulfing(c1, c2):
    return c2["open"] < c1["close"] and c2["close"] > c1["open"]

def buy_signal(df, i):
    c1, c2, c3 = df.iloc[i-2], df.iloc[i-1], df.iloc[i]

    if not (is_hollow(c1) and is_hollow(c2) and is_hollow(c3)):
        return False
    if c1["low"] > c1["lower"] or c2["low"] > c2["lower"] or c3["low"] > c3["lower"]:
        return False
    if any([x["high"] >= x["ma"] or x["close"] >= x["ma"] for x in [c1, c2, c3]]):
        return False
    if is_engulfing(c1, c2) or is_engulfing(c2, c3):
        return False
    if any(abs(c["close"] - c["open"]) < 0.1 for c in [c1, c2, c3]):
        return False
    return True

def sell_signal(df, i):
    c1, c2, c3 = df.iloc[i-2], df.iloc[i-1], df.iloc[i]

    if not (is_hollow(c1) and is_hollow(c2) and is_hollow(c3)):
        return False
    if c1["high"] < c1["upper"] or c2["high"] < c2["upper"] or c3["high"] < c3["upper"]:
        return False
    if any([x["low"] <= x["ma"] or x["close"] <= x["ma"] for x in [c1, c2, c3]]):
        return False
    if is_engulfing(c1, c2) or is_engulfing(c2, c3):
        return False
    if any(abs(c["close"] - c["open"]) < 0.1 for c in [c1, c2, c3]):
        return False
    return True

def send_telegram_message(msg):
    if SEND_TELEGRAM:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {"chat_id": CHAT_ID, "text": msg}
            requests.post(url, data=data)
        except Exception as e:
            print("⚠️ Telegram error:", e)

# === Main logic ===

signals = []
files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]
print(f"🔍 Found {len(files)} stock files. Running strategy...")

for file in tqdm(files):
    symbol = file.replace(".csv", "")
    path = os.path.join(DATA_FOLDER, file)

    try:
        df = pd.read_csv(path)
        df.columns = [col.strip().lower() for col in df.columns]
        df.rename(columns={"time": "timestamp"}, inplace=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")

        df = calculate_bbands(df)

        for i in range(BB_PERIOD + 2, len(df)):
            if buy_signal(df, i):
                ts = df.iloc[i]["timestamp"]
                price = df.iloc[i]["close"]
                signals.append({"symbol": symbol, "timestamp": ts, "price": price, "signal": "BUY"})
                send_telegram_message(f"🟢 BUY Signal: {symbol} at {price} on {ts}")
            elif sell_signal(df, i):
                ts = df.iloc[i]["timestamp"]
                price = df.iloc[i]["close"]
                signals.append({"symbol": symbol, "timestamp": ts, "price": price, "signal": "SELL"})
                send_telegram_message(f"🔴 SELL Signal: {symbol} at {price} on {ts}")

    except Exception as e:
        print(f"⚠️ Error with {symbol}: {e}")

# === Save output ===
if signals:
    pd.DataFrame(signals).to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ Backtest complete. Signals saved to {OUTPUT_CSV}")
else:
    print("\n⚠️ No signals found.")
