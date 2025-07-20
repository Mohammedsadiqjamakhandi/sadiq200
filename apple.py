import os
import time
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv
from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")
TELEGRAM_BOT_TOKEN = "7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0"
TELEGRAM_CHAT_ID = "5795808600"

# Telegram alert function
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, data=data)
    except Exception as e:
        logger.error(f"Telegram error: {e}")

# 3-Candle Bollinger Band Reversal Strategy
def check_bollinger_signal(df):
    if len(df) < 20:
        return None

    df['MA'] = df['close'].rolling(window=20).mean()
    df['STD'] = df['close'].rolling(window=20).std()
    df['Upper'] = df['MA'] + 2 * df['STD']
    df['Lower'] = df['MA'] - 2 * df['STD']

    c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]

    def is_hollow(c): return c['close'] > c['open'] and abs(c['close'] - c['open']) > 0.1
    def is_engulfing(c1, c2): return c2['open'] < c1['close'] and c2['close'] > c1['open']

    # Buy condition
    if (is_hollow(c1) and
        c1['low'] <= c1['Lower'] and
        is_hollow(c2) and c2['high'] > c1['high'] and c2['low'] > c1['low'] and
        is_hollow(c3) and c3['high'] > c2['high'] and c3['low'] > c2['low'] and
        c1['close'] < c1['MA'] and c2['close'] < c2['MA'] and c3['close'] < c3['MA'] and
        not is_engulfing(c1, c2) and not is_engulfing(c2, c3)):
        return "BUY"

    # Sell condition
    if (not is_hollow(c1) and
        c1['high'] >= c1['Upper'] and
        not is_hollow(c2) and c2['high'] < c1['high'] and c2['low'] < c1['low'] and
        not is_hollow(c3) and c3['high'] < c2['high'] and c3['low'] < c2['low'] and
        c1['close'] > c1['MA'] and c2['close'] > c2['MA'] and c3['close'] > c3['MA'] and
        not is_engulfing(c2, c1) and not is_engulfing(c3, c2)):
        return "SELL"

    return None

# Login to Angel One SmartAPI
print("🚀 Logging in...")
smart_api = SmartConnect(api_key=API_KEY)
data = smart_api.generateSession(CLIENT_CODE, PASSWORD, pyotp.TOTP(TOTP_SECRET).now())
feedToken = smart_api.getfeedToken()
print("✅ Login successful.")

# Load stocks
stock_df = pd.read_csv("nse200_symbols.csv", sep=",")
stock_df.columns = stock_df.columns.str.strip().str.lower()
symbols = stock_df['symbol'].tolist()
tokens = stock_df['token'].tolist()
print(f"📡 Tracking {len(symbols)} NSE 200 stocks...")

# Track candle data
candles = {symbol: [] for symbol in symbols}

# CSV log file
log_file = "ltp_log.csv"
if not os.path.exists(log_file):
    with open(log_file, "w") as f:
        f.write("timestamp,symbol,ltp,signal\n")

# Main loop
while True:
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for symbol, token in zip(symbols, tokens):
            try:
                ltp_data = smart_api.ltpData(
                    exchange="NSE",
                    tradingsymbol=symbol,
                    symboltoken=str(token)
                )
                ltp = float(ltp_data['data']['ltp'])

                # Simulated candle (you can later replace with real OHLC)
                candles[symbol].append({
                    'open': ltp, 'high': ltp, 'low': ltp, 'close': ltp
                })

                # Limit to last 30 candles
                if len(candles[symbol]) > 30:
                    candles[symbol] = candles[symbol][-30:]

                df = pd.DataFrame(candles[symbol])
                signal = check_bollinger_signal(df)

                if signal:
                    alert = f"📈 {signal} SIGNAL: {symbol}\nPrice: ₹{ltp}\nTime: {timestamp}"
                    send_telegram(alert)
                    print(alert)

                # Log to CSV
                with open(log_file, "a") as f:
                    f.write(f"{timestamp},{symbol},{ltp},{signal or ''}\n")

                print(f"📊 {symbol} LTP: {ltp}")

            except Exception as e:
                print(f"❌ Error fetching {symbol}: {e}")

        time.sleep(60)

    except KeyboardInterrupt:
        print("🛑 Stopped by user.")
        break
    except Exception as e:
        print(f"❌ Error in main loop: {e}")
        time.sleep(5)
