import os
import pandas as pd
import numpy as np
import requests

# === Telegram Setup ===
SEND_TELEGRAM = False
BOT_TOKEN = "7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0"
CHAT_ID = "5795808600"

def send_telegram(message):
    if not SEND_TELEGRAM:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except:
        pass

# === Signal Logging ===
def log_signal(symbol, side, price, time_str, signals):
    signals.append({
        "time": time_str,
        "symbol": symbol,
        "signal": side,
        "price": price
    })

# === Backtest Strategy ===
def run_strategy_on_dataframe(df, symbol, signals):
    df = df.copy()
    df["mid"] = df["close"].rolling(20).mean()
    df["std"] = df["close"].rolling(20).std()
    df["upper"] = df["mid"] + 2 * df["std"]
    df["lower"] = df["mid"] - 2 * df["std"]

    def is_hollow(c): return c["close"] > c["open"] and abs(c["close"] - c["open"]) > 0.1

    for i in range(22, len(df)):
        c1, c2, c3 = df.iloc[i-3], df.iloc[i-2], df.iloc[i-1]

        # BUY
        if (
            is_hollow(c1) and c1["low"] <= c1["lower"] and
            is_hollow(c2) and is_hollow(c3) and
            c2["high"] > c1["high"] and c2["low"] > c1["low"] and
            c3["high"] > c2["high"] and c3["low"] > c2["low"] and
            all(c["close"] < c["mid"] and c["open"] < c["mid"] for c in [c1, c2, c3])
        ):
            msg = f"📈 BUY: {symbol} at {c3['close']} ({c3['timestamp']})"
            print(msg)
            send_telegram(msg)
            log_signal(symbol, "BUY", c3['close'], c3['timestamp'], signals)

        # SELL
        if (
            not is_hollow(c1) and c1["high"] >= c1["upper"] and
            not is_hollow(c2) and not is_hollow(c3) and
            c2["high"] < c1["high"] and c2["low"] < c1["low"] and
            c3["high"] < c2["high"] and c3["low"] < c2["low"] and
            all(c["close"] > c["mid"] and c["open"] > c["mid"] for c in [c1, c2, c3])
        ):
            msg = f"📉 SELL: {symbol} at {c3['close']} ({c3['timestamp']})"
            print(msg)
            send_telegram(msg)
            log_signal(symbol, "SELL", c3['close'], c3['timestamp'], signals)

# === Main Backtest ===
data_path = r"D:\saniya\data"
signals = []

print(f"🔍 Backtesting using files from: {data_path}")

for file in os.listdir(data_path):
    if file.endswith(".csv"):
        symbol = file.replace(".csv", "")
        try:
            df = pd.read_csv(os.path.join(data_path, file))
            df.columns = [c.lower() for c in df.columns]
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            run_strategy_on_dataframe(df, symbol, signals)
        except Exception as e:
            print(f"❌ Error with {symbol}: {e}")

# === Save All Signals ===
if signals:
    out_df = pd.DataFrame(signals)
    out_df.to_csv("backtest_signals.csv", index=False)
    print("✅ Backtest complete. Signals saved to backtest_signals.csv")
    send_telegram("✅ Backtest complete. Check backtest_signals.csv for results.")
else:
    print("⚠️ No signals generated.")
