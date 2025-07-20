import pandas as pd
from datetime import datetime

# Load candle data
df = pd.read_csv("candles.csv", parse_dates=["date"])
print("✅ Data loaded")

# Prepare results
signals = []

# Get list of all symbols
symbols = df["symbol"].unique()

# Loop through each symbol
for symbol in symbols:
    df_symbol = df[df["symbol"] == symbol].sort_values("date").copy()
    
    # Calculate Bollinger Bands
    df_symbol["middle_band"] = df_symbol["close"].rolling(window=20).mean()
    df_symbol["std"] = df_symbol["close"].rolling(window=20).std()
    df_symbol["upper_band"] = df_symbol["middle_band"] + 2 * df_symbol["std"]
    df_symbol["lower_band"] = df_symbol["middle_band"] - 2 * df_symbol["std"]

    # Scan for signals
    for i in range(2, len(df_symbol)):
        c1, c2, c3 = df_symbol.iloc[i - 2], df_symbol.iloc[i - 1], df_symbol.iloc[i]

        # BUY condition
        if (
            c1["low"] <= c1["lower_band"] and
            c2["low"] > c1["low"] and c3["low"] > c2["low"] and
            c2["high"] > c1["high"] and c3["high"] > c2["high"] and
            all(c["middle_band"] > c["low"] for c in [c1, c2, c3]) and
            not (c2["high"] >= c1["high"] and c2["low"] <= c1["low"] or c3["high"] >= c2["high"] and c3["low"] <= c2["low"])
        ):
            signals.append({"symbol": symbol, "type": "BUY", "date": c3["date"], "price": c3["close"]})

        # SELL condition
        if (
            c1["high"] >= c1["upper_band"] and
            c2["high"] < c1["high"] and c3["high"] < c2["high"] and
            c2["low"] < c1["low"] and c3["low"] < c2["low"] and
            all(c["middle_band"] < c["high"] for c in [c1, c2, c3]) and
            not (c2["low"] <= c1["low"] and c2["high"] >= c1["high"] or c3["low"] <= c2["low"] and c3["high"] >= c2["high"])
        ):
            signals.append({"symbol": symbol, "type": "SELL", "date": c3["date"], "price": c3["close"]})

# Save signals
df_signals = pd.DataFrame(signals)
df_signals.to_csv("signals_summary.csv", index=False)
print(f"📈 Total Signals: {len(signals)}")
print("📄 Saved to signals_summary.csv")
