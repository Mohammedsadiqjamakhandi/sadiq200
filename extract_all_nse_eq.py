import pandas as pd

# Load the file with all candle data
df = pd.read_csv("candles.csv")

# Extract unique symbol-token pairs
df_tokens = df[['symbol', 'token']].drop_duplicates()

# Save to new file for live trading
df_tokens.to_csv("nse_eq_symbols.csv", index=False)

print(f"✅ Extracted {len(df_tokens)} unique NSE EQ symbols to nse_eq_symbols.csv")
