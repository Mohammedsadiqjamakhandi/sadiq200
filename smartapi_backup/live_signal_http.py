import os
import time
import pandas as pd
import pyotp
from dotenv import load_dotenv
from SmartApi.smartConnect import SmartConnect
from logzero import logger

# Load .env credentials
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# Login
print("🚀 Generating TOTP...")
totp = pyotp.TOTP(TOTP_SECRET).now()
print("🚀 Logging into Angel One...")
obj = SmartConnect(api_key=API_KEY)
session = obj.generateSession(CLIENT_CODE, PASSWORD, totp)
feed_token = session['data']['feedToken']
print("✅ Logged in successfully!")

# Load symbols from CSV
df = pd.read_csv("nse_eq_symbols.csv")
symbols = df['symbol'].tolist()[:50]  # Limit for testing
print(f"📡 Tracking {len(symbols)} stocks via HTTP...")

# Candle storage
candles = {sym: [] for sym in symbols}

# Bollinger Bands calculation
def calculate_bbands(df, period=20, std_dev=2):
    df['MA'] = df['close'].rolling(window=period).mean()
    df['Upper'] = df['MA'] + std_dev * df['close'].rolling(window=period).std()
    df['Lower'] = df['MA'] - std_dev * df['close'].rolling(window=period).std()
    return df

# 3-candle pattern strategy
def check_bollinger_signal(df):
    if len(df) < 20:
        return None
    df = calculate_bbands(df)
    c1, c2, c3 = df.iloc[-3:]
    
    # Buy pattern
    if (c1['close'] <= c1['Lower'] and
        c2['close'] > c1['close'] and
        c3['close'] > c2['close'] and
        all(x['close'] < x['MA'] for _, x in df.iloc[-3:].iterrows())):
        return "BUY"
    
    # Sell pattern
    if (c1['close'] >= c1['Upper'] and
        c2['close'] < c1['close'] and
        c3['close'] < c2['close'] and
        all(x['close'] > x['MA'] for _, x in df.iloc[-3:].iterrows())):
        return "SELL"
    
    return None

# Main loop
while True:
    for symbol in symbols:
        try:
            ltp_data = obj.ltpData("NSE", symbol, "")
            ltp = float(ltp_data['data']['ltp'])
            candles[symbol].append({'close': ltp})
            print(f"📊 {symbol} LTP: {ltp}")

            if len(candles[symbol]) > 25:
                candles[symbol] = candles[symbol][-25:]

            if len(candles[symbol]) >= 20:
                df = pd.DataFrame(candles[symbol])
                signal = check_bollinger_signal(df)
                if signal:
                    print(f"📈 Signal: {signal} for {symbol} at {ltp}")
                    candles[symbol] = []  # Reset after signal
        except Exception as e:
            logger.warning(f"⚠️ Failed to fetch LTP for {symbol}: {e}")
    
    time.sleep(5)
