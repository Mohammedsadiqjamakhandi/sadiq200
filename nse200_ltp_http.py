import os
import time
import pandas as pd
import requests
import pyotp
from SmartApi.smartConnect import SmartConnect
from dotenv import load_dotenv

# 📩 Telegram Setup
TELEGRAM_BOT_TOKEN = "7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0"
TELEGRAM_CHAT_ID = "5795808600"

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, data=payload)
    except Exception as e:
        print("❌ Telegram error:", e)

# 🔐 Load credentials
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# 🔢 Generate TOTP
def generate_totp():
    return pyotp.TOTP(TOTP_SECRET).now()

# 🚀 Login
print("🚀 Logging in...")
obj = SmartConnect(api_key=API_KEY)
data = obj.generateSession(CLIENT_CODE, PASSWORD, generate_totp())
feedToken = obj.getfeedToken()
print("✅ Login successful.")

# 📁 Load NSE 200 stocks (symbol, token)
nse200_df = pd.read_csv("nse200_symbols.csv")
symbols = nse200_df["symbol"].tolist()
tokens = nse200_df["token"].astype(str).tolist()
print(f"📡 Tracking {len(symbols)} NSE 200 stocks...")

# 🧠 Store candles for strategy
candles = {symbol: [] for symbol in symbols}

# 📏 Bollinger Band + 3 hollow candle reversal pattern
def is_hollow(candle):
    return candle['close'] > candle['open'] and abs(candle['close'] - candle['open']) > 0.1

def check_bollinger_signal(symbol):
    df = pd.DataFrame(candles[symbol])
    if len(df) < 20:
        return None  # Not enough data

    df['ma'] = df['close'].rolling(window=20).mean()
    df['std'] = df['close'].rolling(window=20).std()
    df['upper'] = df['ma'] + 2 * df['std']
    df['lower'] = df['ma'] - 2 * df['std']

    last3 = df.iloc[-3:]
    if len(last3) < 3:
        return None

    c1, c2, c3 = last3.iloc[0], last3.iloc[1], last3.iloc[2]

    # BUY setup
    if all(is_hollow(c) for c in [c1, c2, c3]):
        if c1['low'] <= c1['lower'] and c2['high'] > c1['high'] and c2['low'] > c1['low'] and c3['high'] > c2['high'] and c3['low'] > c2['low']:
            if all(c['close'] < c['ma'] and c['high'] < c['ma'] for c in [c1, c2, c3]):
                return "BUY"

    # SELL setup
    if all(not is_hollow(c) for c in [c1, c2, c3]):  # all solid
        if c1['high'] >= c1['upper'] and c2['high'] < c1['high'] and c2['low'] < c1['low'] and c3['high'] < c2['high'] and c3['low'] < c2['low']:
            if all(c['close'] > c['ma'] and c['low'] > c['ma'] for c in [c1, c2, c3]):
                return "SELL"

    return None

# 🔁 Poll LTP and update candles
while True:
    for symbol, token in zip(symbols, tokens):
        try:
            ltp_data = obj.ltpData("NSE", symbol, token)
            ltp = float(ltp_data["data"]["ltp"])
            now = pd.Timestamp.now().floor("min")

            # Store new candle
            candle_list = candles[symbol]
            if not candle_list or candle_list[-1]['time'] != now:
                # start new candle
                candles[symbol].append({"time": now, "open": ltp, "high": ltp, "low": ltp, "close": ltp})
                if len(candle_list) > 60:
                    candle_list.pop(0)
            else:
                # update current candle
                candle_list[-1]['high'] = max(candle_list[-1]['high'], ltp)
                candle_list[-1]['low'] = min(candle_list[-1]['low'], ltp)
                candle_list[-1]['close'] = ltp

            signal = check_bollinger_signal(symbol)
            if signal:
                msg = f"{'🟢' if signal == 'BUY' else '🔴'} {signal} Signal: {symbol}\nLTP: ₹{ltp}\n1-min BB Reversal Pattern"
                print(msg)
                send_telegram_message(msg)

        except Exception as e:
            print(f"❌ {symbol}: {e}")
        time.sleep(0.1)
