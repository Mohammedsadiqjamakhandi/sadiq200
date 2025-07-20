import pandas as pd
import numpy as np
import requests
import time

# === Telegram Config ===
BOT_TOKEN = "7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0"
CHAT_ID = "5795808600"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Telegram error:", e)

# === Load Candle Data ===
df = pd.read_csv("RELIANCE.csv")
df["time"] = pd.to_datetime(df["time"])
df.set_index("time", inplace=True)

# === Bollinger Bands ===
df["ma20"] = df["close"].rolling(20).mean()
df["std20"] = df["close"].rolling(20).std()
df["upper"] = df["ma20"] + 2 * df["std20"]
df["lower"] = df["ma20"] - 2 * df["std20"]

# === Strategy ===
signals = []

for i in range(2, len(df)):
    c1 = df.iloc[i-2]
    c2 = df.iloc[i-1]
    c3 = df.iloc[i]

    def is_hollow(c): return c["close"] > c["open"]
    def not_doji(c): return abs(c["close"] - c["open"]) > 0.1
    def not_engulf(prev, curr): return not (curr["open"] < prev["close"] and curr["close"] > prev["open"])

    # --- BUY SIGNAL ---
    if (
        is_hollow(c1) and c1["low"] <= c1["lower"] and
        is_hollow(c2) and is_hollow(c3) and
        c2["high"] > c1["high"] and c2["low"] > c1["low"] and
        c3["high"] > c2["high"] and c3["low"] > c2["low"] and
        all(c["close"] < c["ma20"] and c["high"] < c["ma20"] for c in [c1, c2, c3]) and
        all(not_doji(c) for c in [c1, c2, c3]) and
        not_engulf(c1, c2) and not_engulf(c2, c3)
    ):
        msg = f"🟢 BUY SIGNAL: RELIANCE at {c3.name.strftime('%Y-%m-%d %H:%M')} | ₹{c3['close']:.2f}"
        print(msg)
        send_telegram(msg)
        signals.append([c3.name, "BUY", c3["close"]])
        time.sleep(0.5)

    # --- SELL SIGNAL ---
    elif (
        not is_hollow(c1) and c1["high"] >= c1["upper"] and
        not is_hollow(c2) and not is_hollow(c3) and
        c2["high"] < c1["high"] and c2["low"] < c1["low"] and
        c3["high"] < c2["high"] and c3["low"] < c2["low"] and
        all(c["close"] > c["ma20"] and c["low"] > c["ma20"] for c in [c1, c2, c3]) and
        all(not_doji(c) for c in [c1, c2, c3]) and
        not_engulf(c1, c2) and not_engulf(c2, c3)
    ):
        msg = f"🔴 SELL SIGNAL: RELIANCE at {c3.name.strftime('%Y-%m-%d %H:%M')} | ₹{c3['close']:.2f}"
        print(msg)
        send_telegram(msg)
        signals.append([c3.name, "SELL", c3["close"]])
        time.sleep(0.5)

# === Save result ===
if signals:
    pd.DataFrame(signals, columns=["time", "signal", "price"]).to_csv("backtest_log.csv", index=False)
    print("✅ Signals saved to backtest_log.csv")
else:
    print("📭 No signals found.")
