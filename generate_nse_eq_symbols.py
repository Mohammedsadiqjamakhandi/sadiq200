import pandas as pd

# Load the JSON file you just downloaded
df = pd.read_json("ScripMaster.json")

# Filter for only NSE and EQ segment
df_eq = df[(df["exch_seg"] == "NSE") & (df["symbol"].str.endswith("EQ"))]

# Keep only required columns
df_eq = df_eq[["symbol", "token"]].drop_duplicates()

# Clean and save to CSV
df_eq['token'] = df_eq['token'].astype(str)
df_eq.to_csv("nse_eq_symbols.csv", index=False)

print(f"✅ Saved {len(df_eq)} real NSE EQ stocks to nse_eq_symbols.csv")
