import os
import time
import pyotp
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from SmartApi.smartConnect import SmartConnect

# Load credentials from .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# Login
totp = pyotp.TOTP(TOTP_SECRET).now()
print("🚀 Logging in...")
obj = SmartConnect(api_key=API_KEY)
data = obj.generateSession(CLIENT_CODE, PASSWORD, totp)
tokens = data['data']
print("✅ Login successful.")

# Load and clean all NSE stock symbols
df_symbols = pd.read_csv("nse_eq_symbols.csv")

# Drop rows where token is missing
df_symbols = df_symbols.dropna(subset=['token'])

# Convert token to clean string (removes .0)
df_symbols['token'] = df_symbols['token'].astype(float).astype(int).astype(str)

# Make symbol-token map
symbols = dict(zip(df_symbols['symbol'], df_symbols['token']))
print(f"📡 Tracking {len(symbols)} NSE stocks...")

# Store LTP candles
candles = {sym: [] for sym in symbols}

# --- Bollinger Band Logic ---
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
        print(f"❌ Order failed for {symbol}:", e)

# --- Main Polling Loop ---
while True:
    for symbol, token in symbols.items():
        try:
            ltp_data = obj.ltpData("NSE", symbol, token)
            ltp = float(ltp_data['data']['ltp'])
            print(f"📊 {symbol} LTP: {ltp}")
            candles[symbol].append({'close': ltp})

            if len(candles[symbol]) > 25:
                candles[symbol] = candles[symbol][-25:]

            if len(candles[symbol]) >= 20:
                df = pd.DataFrame(candles[symbol])
                df = calculate_bbands(df)
                signal = check_signal(df)
                if signal:
                    place_order(symbol, signal)
                    candles[symbol] = []  # Reset after signal
        except Exception as e:
            print(f"⚠️ {symbol} LTP fetch failed:", e)

    time.sleep(5)
