import pandas as pd

# Load full symbol-token map (from Angel One)
df_all = pd.read_csv("nse_eq_symbols.csv")

# Load NSE 200 raw file downloaded from NSE website
df_200 = pd.read_csv("nse200_raw.csv")

# Strip spaces and make sure formats match
df_all["symbol"] = df_all["symbol"].str.strip()
df_200.columns = df_200.columns.str.strip()

# NSE CSV usually has column like "Symbol" or "SYMBOL" or "Company Name"
symbol_column = [col for col in df_200.columns if "symbol" in col.lower()][0]
df_200[symbol_column] = df_200[symbol_column].str.strip()

# Merge to find token for only NSE 200 stocks
filtered = df_all[df_all["symbol"].isin(df_200[symbol_column] + "-EQ")]

# Save only the needed columns
filtered[["symbol", "token"]].to_csv("nse200_symbols.csv", index=False)
print(f"✅ Saved nse200_symbols.csv with {len(filtered)} symbols.")
