# live_strategy_signals_only.py
import os
import time
import requests
import pandas as pd
import pyotp
from datetime import datetime
from dotenv import load_dotenv
from SmartApi.smartConnect import SmartConnect

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Generate TOTP
totp = pyotp.TOTP(TOTP_SECRET).now()

# Login
print("\U0001F680 Logging in...")
obj = SmartConnect(api_key=API_KEY)
data = obj.generateSession(CLIENT_CODE, PASSWORD, totp)
tokens = data['data']
feed_token = tokens['feedToken']
print("✅ Login successful.")

# Load symbols
df_symbols = pd.read_csv("nse_eq_symbols.csv")
symbol_map = dict(zip(df_symbols['symbol'], df_symbols['token'].astype(str)))

# Candle storage
candles = {symbol: [] for symbol in symbol_map}

# BBands
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

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram error:", e)

# Live LTP loop
print(f"\U0001F4F0 Tracking {len(symbol_map)} NSE stocks...")
while True:
    for symbol, token in list(symbol_map.items())[:100]:  # limit batch for free tier
        try:
            ltp_data = obj.ltpData("NSE", symbol, token)
            ltp = float(ltp_data['data']['ltp'])

            candles[symbol].append({'close': ltp})
            if len(candles[symbol]) > 25:
                candles[symbol] = candles[symbol][-25:]

            if len(candles[symbol]) >= 20:
                df = pd.DataFrame(candles[symbol])
                df = calculate_bbands(df)
                signal = check_signal(df)
                if signal:
                    now = datetime.now().strftime("%H:%M:%S")
                    msg = f"{'📈' if signal=='BUY' else '📉'} {signal} SIGNAL\n{symbol} @ ₹{ltp}\nTime: {now}"
                    print(msg)
                    send_telegram_message(msg)
                    with open("signals.csv", "a") as f:
                        f.write(f"{now},{symbol},{signal},{ltp}\n")
        except Exception as e:
            print(f"⚠️ {symbol} failed: {e}")

    time.sleep(5)
