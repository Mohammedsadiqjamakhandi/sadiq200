import os
import time
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from SmartApi.smartConnect import SmartConnect
import pyotp

# === Config ===
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"
SEND_TELEGRAM = True
BOT_TOKEN = "7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0"
CHAT_ID = "5795808600"
TARGET_PCT = 0.01
STOPLOSS_PCT = 0.01
POLL_INTERVAL = 5  # seconds

# === Load NSE200 symbols and tokens ===
symbols_df = pd.read_csv("nse200_tokens.csv")  # Must have 'symbol','token' columns
symbol_token_map = dict(zip(symbols_df.symbol, symbols_df.token))

# === Telegram ===
def send_telegram(msg):
    if SEND_TELEGRAM:
        try:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={
                "chat_id": CHAT_ID,
                "text": msg
            })
        except:
            print("⚠️ Telegram failed")

# === Login ===
def generate_totp(secret):
    return pyotp.TOTP(secret).now()

print("🚀 Logging in...")
sdk = SmartConnect(api_key=API_KEY)

try:
    otp = generate_totp(TOTP_SECRET)

    try:
        session = sdk.generate_session(CLIENT_CODE, PASSWORD, otp)
    except Exception as e:
        print("❌ generate_session() failed:", e)
        exit()

    print("🔍 Raw session =", session)
    print("🔍 Type of session =", type(session))

    if not isinstance(session, dict) or "data" not in session:
        raise Exception(f"Unexpected login response: {session}")

    refresh_token = session["data"]["refreshToken"]
    user_profile = sdk.get_profile()
    print("✅ Login successful.")

except Exception as e:
    print("❌ Login failed:", e)
    exit()



# === Candle Data ===
candle_data = {sym: [] for sym in symbol_token_map.keys()}
last_minute = None

# === Strategy Conditions ===
def is_hollow(c):
    return c['close'] > c['open'] and abs(c['close'] - c['open']) > 0.1

def is_body_increasing(c1, c2):
    return abs(c2['close'] - c2['open']) > abs(c1['close'] - c1['open'])

def is_valid_buy(c1, c2, c3):
    if not all(is_hollow(c) for c in [c1, c2, c3]): return False
    if not (is_body_increasing(c1, c2) and is_body_increasing(c2, c3)): return False
    if c1['low'] > c1['lower']: return False
    if c2['low'] <= c2['lower'] or c3['low'] <= c3['lower']: return False
    if not (c2['high'] > c1['high'] and c2['low'] > c1['low']): return False
    if not (c3['high'] > c2['high'] and c3['low'] > c2['low']): return False
    return True

def calculate_bbands(df):
    df['ma'] = df['close'].rolling(20).mean()
    df['std'] = df['close'].rolling(20).std()
    df['upper'] = df['ma'] + 2 * df['std']
    df['lower'] = df['ma'] - 2 * df['std']
    return df

# === Live Polling Loop ===
print(f"📡 Tracking {len(symbol_token_map)} stocks...")
while True:
    try:
        now = datetime.now()
        minute_key = now.replace(second=0, microsecond=0)

        for symbol, token in symbol_token_map.items():
            try:
                ltp_data = sdk.get_ltp_data("NSE", symbol, token)
                ltp = float(ltp_data['data']['ltp'])
            except:
                continue

            # Init or update 1-minute candle
            if not candle_data[symbol] or candle_data[symbol][-1]['minute'] != minute_key:
                candle_data[symbol].append({
                    'minute': minute_key,
                    'open': ltp,
                    'high': ltp,
                    'low': ltp,
                    'close': ltp
                })
                candle_data[symbol] = candle_data[symbol][-50:]  # Keep only last 50 candles
            else:
                c = candle_data[symbol][-1]
                c['high'] = max(c['high'], ltp)
                c['low'] = min(c['low'], ltp)
                c['close'] = ltp

        # After minute closes, run strategy
        if last_minute != minute_key and now.second < 5:
            for symbol, candles in candle_data.items():
                if len(candles) < 23:
                    continue
                df = pd.DataFrame(candles)
                df = calculate_bbands(df)
                c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
                if is_valid_buy(c1, c2, c3):
                    entry = c3['close']
                    sl = round(entry * (1 - STOPLOSS_PCT), 2)
                    tgt = round(entry * (1 + TARGET_PCT), 2)
                    ts = c3['minute'].strftime("%Y-%m-%d %H:%M")
                    send_telegram(f"🟢 BUY Signal: {symbol} at ₹{entry:.2f}\n📅 Time: {ts}\n🎯 Target: ₹{tgt:.2f}\n🛑 Stoploss: ₹{sl:.2f}")
            last_minute = minute_key

        time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("👋 Exiting...")
        break
    except Exception as e:
        print("⚠️ Error:", e)
        time.sleep(5)
