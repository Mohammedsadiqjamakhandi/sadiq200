import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Load candle data
df = pd.read_csv("candles.csv", parse_dates=["date"])
print("✅ Data loaded")

# Calculate Bollinger Bands
window = 20
std_dev = 2
df["middle_band"] = df["close"].rolling(window=window).mean()
df["std"] = df["close"].rolling(window=window).std()
df["upper_band"] = df["middle_band"] + std_dev * df["std"]
df["lower_band"] = df["middle_band"] - std_dev * df["std"]
print("✅ Bollinger Bands calculated")

# Detect Buy and Sell Signals
signals = []
for i in range(2, len(df)):
    c1, c2, c3 = df.iloc[i - 2], df.iloc[i - 1], df.iloc[i]

    # BUY condition
    if (
        c1["low"] <= c1["lower_band"] and
        c2["low"] > c1["low"] and
        c3["low"] > c2["low"] and
        all(x < y for x, y in zip([c1["high"], c2["high"]], [c2["high"], c3["high"]])) and
        all(c["middle_band"] > c["low"] for c in [c1, c2, c3]) and
        not (c2["high"] >= c1["high"] and c2["low"] <= c1["low"] or c3["high"] >= c2["high"] and c3["low"] <= c2["low"])
    ):
        signals.append({"type": "BUY", "index": i, "price": c3["close"], "date": c3["date"]})

    # SELL condition
    if (
        c1["high"] >= c1["upper_band"] and
        c2["high"] < c1["high"] and
        c3["high"] < c2["high"] and
        all(x > y for x, y in zip([c1["low"], c2["low"]], [c2["low"], c3["low"]])) and
        all(c["middle_band"] < c["high"] for c in [c1, c2, c3]) and
        not (c2["low"] <= c1["low"] and c2["high"] >= c1["high"] or c3["low"] <= c2["low"] and c3["high"] >= c2["high"])
    ):
        signals.append({"type": "SELL", "index": i, "price": c3["close"], "date": c3["date"]})

print("\n📈 Signals:")
for sig in signals:
    print(f"✅ {sig['type']} on {sig['date']} at price {sig['price']}")

# Backtest Logic with 1% target or 1% stop-loss or exit at 3:15 PM
trades = []
for sig in signals:
    entry_index = sig['index']
    entry_price = sig['price']
    entry_date = sig['date']
    entry_type = sig['type']

    target_price = entry_price * (1.01 if entry_type == 'BUY' else 0.99)
    stop_price = entry_price * (0.99 if entry_type == 'BUY' else 1.01)

    for i in range(entry_index + 1, len(df)):
        row = df.iloc[i]
        time = row['date'].time()

        if entry_type == 'BUY':
            if row['high'] >= target_price:
                trades.append({
                    'type': 'BUY', 'entry_date': entry_date, 'exit_date': row['date'],
                    'entry_price': entry_price, 'exit_price': target_price, 'pnl': target_price - entry_price,
                    'percent': 1.0
                })
                break
            elif row['low'] <= stop_price:
                trades.append({
                    'type': 'BUY', 'entry_date': entry_date, 'exit_date': row['date'],
                    'entry_price': entry_price, 'exit_price': stop_price, 'pnl': stop_price - entry_price,
                    'percent': -1.0
                })
                break

        elif entry_type == 'SELL':
            if row['low'] <= target_price:
                trades.append({
                    'type': 'SELL', 'entry_date': entry_date, 'exit_date': row['date'],
                    'entry_price': entry_price, 'exit_price': target_price, 'pnl': entry_price - target_price,
                    'percent': 1.0
                })
                break
            elif row['high'] >= stop_price:
                trades.append({
                    'type': 'SELL', 'entry_date': entry_date, 'exit_date': row['date'],
                    'entry_price': entry_price, 'exit_price': stop_price, 'pnl': entry_price - stop_price,
                    'percent': -1.0
                })
                break

        if time >= datetime.strptime("15:15:00", "%H:%M:%S").time():
            trades.append({
                'type': entry_type,
                'entry_date': entry_date,
                'exit_date': row['date'],
                'entry_price': entry_price,
                'exit_price': row['close'],
                'pnl': row['close'] - entry_price if entry_type == 'BUY' else entry_price - row['close'],
                'percent': (row['close'] - entry_price) / entry_price * 100 if entry_type == 'BUY'
                else (entry_price - row['close']) / entry_price * 100
            })
            break

# Report
df_report = pd.DataFrame(trades)
df_report.to_csv("backtest_report.csv", index=False)
total_pnl = df_report['pnl'].sum()
total_percent = df_report['percent'].sum()
print("\n💰 Intraday Trade Summary:")
print(f"\n✅ Total Intraday Trades: {len(df_report)}")
print(f"💹 Net P&L: ₹{total_pnl:.2f} | Total %: {total_percent:.2f}%")
print("📄 Backtest report saved: backtest_report.csv")
