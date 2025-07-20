import pandas as pd

# Load Angel's NSE master
df = pd.read_csv("angel_master_nse.csv")

# Filter only EQ series stocks from NSE
df_eq = df[(df['exchange'] == 'NSE') & (df['symbol'].str.endswith('-EQ'))]

# Extract symbol and token columns
df_eq = df_eq[['symbol', 'token']].drop_duplicates()

# Clean token format
df_eq['token'] = df_eq['token'].astype(str)

# Save clean file
df_eq.to_csv("nse_eq_symbols.csv", index=False)

print(f"✅ Created nse_eq_symbols.csv with {len(df_eq)} valid NSE EQ stocks")
