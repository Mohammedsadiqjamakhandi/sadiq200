import os
import pandas as pd
import numpy as np
from tqdm import tqdm
import requests

# === Config ===
DATA_FOLDER = r"D:\saniya\candles"
OUTPUT_CSV = "signals.csv"
BOT_TOKEN = "7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0"
CHAT_ID = "5795808600"
SEND_TELEGRAM = True

BB_PERIOD = 20
BB_STD_DEV = 2
TARGET_PCT = 0.01
STOPLOSS_PCT = 0.01

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

# === Helpers ===
def is_hollow(c):
    return c['close'] > c['open'] and abs(c['close'] - c['open']) > 0.1

def is_body_increasing(c1, c2):
    return abs(c2['close'] - c2['open']) > abs(c1['close'] - c1['open'])

def is_engulfing(c1, c2):
    return c2['open'] < c1['close'] and c2['close'] > c1['open']

def calculate_bbands(df):
    df['ma'] = df['close'].rolling(BB_PERIOD).mean()
    df['std'] = df['close'].rolling(BB_PERIOD).std()
    df['upper'] = df['ma'] + BB_STD_DEV * df['std']
    df['lower'] = df['ma'] - BB_STD_DEV * df['std']
    return df

# === BUY logic ===
def is_valid_buy(c1, c2, c3):
    if not all(is_hollow(c) for c in [c1, c2, c3]): return False
    if not (is_body_increasing(c1, c2) and is_body_increasing(c2, c3)): return False
    if c1['low'] > c1['lower']: return False
    if c2['low'] <= c2['lower'] or c3['low'] <= c3['lower']: return False
    if not (c2['high'] > c1['high'] and c2['low'] > c1['low']): return False
    if not (c3['high'] > c2['high'] and c3['low'] > c2['low']): return False
    if any(c['high'] >= c['ma'] or c['close'] >= c['ma'] for c in [c1, c2, c3]): return False
    if any(abs(c['close'] - c['open']) < 0.1 for c in [c1, c2, c3]): return False
    if is_engulfing(c1, c2) or is_engulfing(c2, c3): return False
    wick1 = c1['open'] - c1['low']
    body1 = c1['close'] - c1['open']
    if wick1 > 1.5 * body1:
        if c2['low'] <= c1['low'] or c3['low'] <= c1['low']:
            return False
    return True

# === SELL logic ===
def is_valid_sell(c1, c2, c3):
    if not all(is_hollow(c) for c in [c1, c2, c3]): return False
    if not (abs(c2['close'] - c2['open']) < abs(c1['close'] - c1['open']) and 
            abs(c3['close'] - c3['open']) < abs(c2['close'] - c2['open'])): return False
    if c1['high'] < c1['upper']: return False
    if c2['high'] >= c2['upper'] or c3['high'] >= c3['upper']: return False
    if not (c2['high'] < c1['high'] and c2['low'] < c1['low']): return False
    if not (c3['high'] < c2['high'] and c3['low'] < c2['low']): return False
    if any(c['low'] <= c['ma'] or c['close'] <= c['ma'] for c in [c1, c2, c3]): return False
    if any(abs(c['close'] - c['open']) < 0.1 for c in [c1, c2, c3]): return False
    if is_engulfing(c1, c2) or is_engulfing(c2, c3): return False
    wick1 = c1['high'] - c1['close']
    body1 = c1['close'] - c1['open']
    if wick1 > 1.5 * body1:
        if c2['high'] >= c1['high'] or c3['high'] >= c1['high']:
            return False
    return True

# === Backtest ===
signals = []
files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]
print(f"📊 Processing {len(files)} stocks...")

for file in tqdm(files):
    symbol = file.replace(".csv", "")
    path = os.path.join(DATA_FOLDER, file)
    try:
        df = pd.read_csv(path)
        df.columns = [c.lower().strip() for c in df.columns]
        df.rename(columns={"time": "timestamp"}, inplace=True)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values("timestamp")
        df = calculate_bbands(df)

        for i in range(BB_PERIOD + 2, len(df)-1):
            c1, c2, c3 = df.iloc[i-2], df.iloc[i-1], df.iloc[i]
            ts = c3['timestamp']
            entry = c3['close']
            sl = round(entry * (1 - STOPLOSS_PCT), 2)
            tgt = round(entry * (1 + TARGET_PCT), 2)

            direction = None
            if is_valid_buy(c1, c2, c3):
                direction = "BUY"
                send_telegram(f"🟢 BUY Signal: {symbol} at ₹{entry:.2f}\n📅 Time: {ts}\n🎯 Target: ₹{tgt:.2f}\n🛑 Stoploss: ₹{sl:.2f}")
            elif is_valid_sell(c1, c2, c3):
                direction = "SELL"
                sl = round(entry * (1 + STOPLOSS_PCT), 2)
                tgt = round(entry * (1 - TARGET_PCT), 2)
                send_telegram(f"🔴 SELL Signal: {symbol} at ₹{entry:.2f}\n📅 Time: {ts}\n🎯 Target: ₹{tgt:.2f}\n🛑 Stoploss: ₹{sl:.2f}")

            if direction:
                exit_price, exit_time, outcome = None, None, None
                for j in range(i+1, len(df)):
                    row = df.iloc[j]
                    high, low = row['high'], row['low']
                    if direction == "BUY":
                        if high >= tgt:
                            exit_price, exit_time, outcome = tgt, row['timestamp'], "TARGET"
                            break
                        elif low <= sl:
                            exit_price, exit_time, outcome = sl, row['timestamp'], "STOPLOSS"
                            break
                    else:
                        if low <= tgt:
                            exit_price, exit_time, outcome = tgt, row['timestamp'], "TARGET"
                            break
                        elif high >= sl:
                            exit_price, exit_time, outcome = sl, row['timestamp'], "STOPLOSS"
                            break
                if exit_price:
                    pnl = round(exit_price - entry, 2) if direction == "BUY" else round(entry - exit_price, 2)
                    signals.append({"symbol": symbol, "timestamp": ts, "price": entry, "signal": direction,
                                     "target": tgt, "stoploss": sl, "exit_price": exit_price,
                                     "exit_time": exit_time, "outcome": outcome, "pnl": pnl})
    except Exception as e:
        print(f"⚠️ Error in {symbol}: {e}")

if signals:
    df_signals = pd.DataFrame(signals)
    df_signals.to_csv(OUTPUT_CSV, index=False)
    total_pnl = df_signals['pnl'].sum()
    winners = (df_signals['outcome'] == "TARGET").sum()
    losers = (df_signals['outcome'] == "STOPLOSS").sum()
    print(f"\n✅ Backtest done: {len(df_signals)} trades")
    print(f"📈 Winners: {winners}  📉 Losers: {losers}  💰 Net P&L: ₹{total_pnl:.2f}")
else:
    print("\n⚠️ No signals found.")