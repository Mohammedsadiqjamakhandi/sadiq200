import tkinter as tk
from datetime import datetime, timedelta
import pandas as pd
import threading
import time
import os
from dotenv import load_dotenv
from SmartApi.smartConnect import SmartConnect
import pyotp

# Load environment
load_dotenv()
ANGEL_API_KEY = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_PASSWORD = os.getenv("ANGEL_PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# CSV with symbols
CSV_PATH = "angel_master_nse.csv"

# GUI Setup
window = tk.Tk()
window.title("Live Trade Alerts")
text_widget = tk.Text(window, height=30, width=100, bg="black", fg="lime", font=("Courier", 10))
text_widget.pack()

def log(msg):
    timestamp = datetime.now().strftime("[%H:%M:%S]")
    text_widget.insert(tk.END, f"{timestamp} {msg}\n")
    text_widget.see(tk.END)

# Login
log("🔐 Logging in...")
smart_api = SmartConnect(api_key=ANGEL_API_KEY)
totp = pyotp.TOTP(TOTP_SECRET).now()

try:
    data = smart_api.generateSession(ANGEL_CLIENT_CODE, ANGEL_PASSWORD, totp)
    log("✅ Logged in.")
except Exception as e:
    log(f"❌ Login failed: {e}")
    exit()

# Load symbols
def load_symbols():
    try:
        df = pd.read_csv(CSV_PATH)
        df.columns = df.columns.str.strip().str.lower()
        return df['symbol'].dropna().unique().tolist()
    except Exception as e:
        log(f"❌ Failed to load symbols: {e}")
        return []

# Fetch dummy candles (mock)
def get_candles(symbol):
    now = datetime.now()
    return [
        [now.strftime("%Y-%m-%d %H:%M:%S"), 100, 101, 102, 99, 100],
        [now.strftime("%Y-%m-%d %H:%M:%S"), 101, 102, 103, 100, 101],
        [now.strftime("%Y-%m-%d %H:%M:%S"), 102, 103, 104, 101, 102],
    ]

# Buy/sell pattern
def check_buy_sell(candles):
    if len(candles) < 3:
        return None
    highs = [x[3] for x in candles]
    lows = [x[4] for x in candles]
    closes = [x[5] for x in candles]

    if highs[2] > highs[1] > highs[0] and closes[2] > closes[1] > closes[0]:
        return "BUY"
    if lows[2] < lows[1] < lows[0] and closes[2] < closes[1] < closes[0]:
        return "SELL"
    return None

# Strategy loop
def run_strategy():
    symbols = load_symbols()
    log(f"🔍 Scanning {len(symbols)} symbols...")

    while True:
        now = datetime.now()
        if now.second != 0:
            time.sleep(1)
            continue

        for symbol in symbols:
            candles = get_candles(symbol)
            action = check_buy_sell(candles)
            if action:
                log(f"🚨 {action} Signal: {symbol}")

        log("⏱️ Waiting for next minute...")
        time.sleep(60)

# Start strategy
threading.Thread(target=run_strategy, daemon=True).start()
window.mainloop()
