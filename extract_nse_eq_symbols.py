import pandas as pd

# Load all candle data
df = pd.read_csv("candles.csv")

# Drop rows with missing symbol/token
df = df.dropna(subset=['symbol', 'token'])

# Extract unique symbol-token pairs
df_tokens = df[['symbol', 'token']].drop_duplicates()

# Clean token format
df_tokens['token'] = df_tokens['token'].astype(float).astype(int).astype(str)

# Save to nse_eq_symbols.csv
df_tokens.to_csv("nse_eq_symbols.csv", index=False)

print(f"✅ Saved {len(df_tokens)} stocks to nse_eq_symbols.csv")
