import pandas as pd
from bollinger_hollow_strategy import check_bollinger_signal
from utils import calculate_bollinger_bands

# === Load CSV data for one stock ===
df = pd.read_csv("candles/INFY.csv")

# === Format candles for processing ===
candles = []
signals = []

for i in range(len(df)):
    row = df.iloc[i]
    candle = {
        'time': row['time'],
        'open': row['open'],
        'high': row['high'],
        'low': row['low'],
        'close': row['close']
    }
    candles.append(candle)

    if len(candles) >= 20:
        bb = calculate_bollinger_bands(candles, period=20)
        signal = check_bollinger_signal("INFY", candles, bb)
        if signal:
            signals.append(signal)

# === Output results ===
for s in signals:
    print(f"{s['time']} | {s['signal']} | Entry: ₹{s['entry']} | SL: ₹{s['sl']} | Target: ₹{s['target']}")
