import os
import time
import pyotp
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from SmartApi.smartConnect import SmartConnect

# Load credentials
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# Generate TOTP and login
totp = pyotp.TOTP(TOTP_SECRET).now()
print("🚀 Logging in...")
obj = SmartConnect(api_key=API_KEY)
data = obj.generateSession(CLIENT_CODE, PASSWORD, totp)
tokens = data['data']
feed_token = tokens['feedToken']
print("✅ Login successful.")

# Stocks to track (NIFTY 50 always works)
symbols = {
    "NIFTY 50": "26000"
}

# Candle data
candles = {sym: [] for sym in symbols}

# Bollinger logic
def calculate_bbands(df, period=20, std_dev=2):
    df['MA'] = df['close'].rolling(window=period).mean()
    df['Upper'] = df['MA'] + std_dev * df['close'].rolling(window=period).std()
    df['Lower'] = df['MA'] - std_dev * df['close'].rolling(window=period).std()
    return df

def check_signal(df):
    if len(df) < 20:
        return None
    last = df.iloc[-1]
    if last['close'] > last['Upper']:
        return "SELL"
    elif last['close'] < last['Lower']:
        return "BUY"
    return None

def place_order(symbol, signal):
    try:
        print(f"📥 Placing {signal} order for {symbol}")
        order = obj.placeOrder(
            variety="NORMAL",
            tradingsymbol=symbol,
            symboltoken=symbols[symbol],
            transactiontype="BUY" if signal == "BUY" else "SELL",
            exchange="NSE",
            ordertype="MARKET",
            producttype="INTRADAY",
            duration="DAY",
            price="0",
            quantity=1
        )
        print("✅ Order placed:", order)
    except Exception as e:
        print("❌ Order failed:", e)

# Main loop
print("📡 Starting live polling (every 5 seconds)...")
while True:
    for symbol, token in symbols.items():
        try:
            ltp_data = obj.ltpData("NSE", symbol, token)
            ltp = float(ltp_data['data']['ltp'])
            candles[symbol].append({'close': ltp})
            print(f"📊 {symbol} LTP: {ltp}")
            if len(candles[symbol]) > 25:
                candles[symbol] = candles[symbol][-25:]

            if len(candles[symbol]) >= 20:
                df = pd.DataFrame(candles[symbol])
                df = calculate_bbands(df)
                signal = check_signal(df)
                if signal:
                    place_order(symbol, signal)
                    candles[symbol] = []  # reset after signal
        except Exception as e:
            print(f"⚠️ LTP fetch failed for {symbol}:", e)

    time.sleep(5)
