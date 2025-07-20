import os
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# === Telegram Details ===
BOT_TOKEN = "7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0"
CHAT_ID = "5795808600"

def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

# === Strategy Logic ===
def is_hollow(candle):
    return candle['close'] > candle['open'] and (candle['close'] - candle['open']) > 0.1

def no_engulfing(c1, c2):
    return c2['high'] < c1['high'] and c2['low'] > c1['low']

def check_buy_signal(df):
    if len(df) < 3:
        return False
    c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
    mid_bb = c1['mid_bb']
    
    # Conditions for Buy
    return (
        is_hollow(c1) and is_hollow(c2) and is_hollow(c3) and
        c1['low'] <= c1['lower_bb'] and
        c2['high'] > c1['high'] and c2['low'] > c1['low'] and
        c3['high'] > c2['high'] and c3['low'] > c2['low'] and
        all(c['close'] < c['mid_bb'] and c['high'] < c['mid_bb'] for c in [c1, c2, c3]) and
        all(abs(c['close'] - c['open']) > 0.1 for c in [c1, c2, c3]) and
        no_engulfing(c1, c2) and no_engulfing(c2, c3)
    )

def check_sell_signal(df):
    if len(df) < 3:
        return False
    c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
    mid_bb = c1['mid_bb']
    
    return (
        not is_hollow(c1) and not is_hollow(c2) and not is_hollow(c3) and
        c1['high'] >= c1['upper_bb'] and
        c2['high'] < c1['high'] and c2['low'] < c1['low'] and
        c3['high'] < c2['high'] and c3['low'] < c2['low'] and
        all(c['close'] > c['mid_bb'] and c['low'] > c['mid_bb'] for c in [c1, c2, c3]) and
        all(abs(c['close'] - c['open']) > 0.1 for c in [c1, c2, c3]) and
        no_engulfing(c1, c2) and no_engulfing(c2, c3)
    )

def apply_bollinger_bands(df):
    df['close'] = df['close'].astype(float)
    df['sma'] = df['close'].rolling(window=20).mean()
    df['std'] = df['close'].rolling(window=20).std()
    df['upper_bb'] = df['sma'] + 2 * df['std']
    df['lower_bb'] = df['sma'] - 2 * df['std']
    df['mid_bb'] = df['sma']
    return df

def run_backtest_on_file(file_path):
    symbol = os.path.basename(file_path).replace('.csv', '')
    try:
        df = pd.read_csv(file_path)
        df = df[['timestamp', 'open', 'high', 'low', 'close']]
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = apply_bollinger_bands(df).dropna().reset_index(drop=True)

        for i in range(20, len(df)):
            chunk = df.iloc[i-3:i]
            if check_buy_signal(chunk):
                time = chunk.iloc[-1]['timestamp']
                msg = f"📊 [Backtest] BUY - {symbol}\n🕐 {time}\n📉 Close: {chunk.iloc[-1]['close']:.2f}"
                print(msg)
                send_telegram_alert(msg)
            elif check_sell_signal(chunk):
                time = chunk.iloc[-1]['timestamp']
                msg = f"📊 [Backtest] SELL - {symbol}\n🕐 {time}\n📈 Close: {chunk.iloc[-1]['close']:.2f}"
                print(msg)
                send_telegram_alert(msg)

    except Exception as e:
        print(f"❌ Error processing {symbol}: {e}")

# === Run Backtest on All Files ===
data_folder = r"D:\saniya\data"
files = [os.path.join(data_folder, f) for f in os.listdir(data_folder) if f.endswith(".csv")]

print(f"🚀 Running backtest on {len(files)} stocks...")
for file in files:
    run_backtest_on_file(file)

print("✅ Backtest complete.")
