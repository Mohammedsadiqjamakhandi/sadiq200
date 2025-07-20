import json
import pandas as pd

# Load the ScripMaster JSON
with open("ScripMaster.json", "r") as f:
    scrip_data = json.load(f)

# Load the list of EQ symbols
eq_symbols_df = pd.read_csv("nse_eq_symbols.csv")  # contains column: symbol
eq_symbols = set(eq_symbols_df["symbol"].str.upper())  # match in uppercase

# Create a mapping from symbol to token
symbol_token_map = {}

for entry in scrip_data:
    symbol = entry.get("symbol", "").upper()
    exch = entry.get("exch_seg", "")
    token = entry.get("token", "")

    if exch == "NSE" and symbol in eq_symbols:
        symbol_token_map[symbol] = token

# Save the final map
df = pd.DataFrame(symbol_token_map.items(), columns=["symbol", "token"])
df.to_csv("symbol_token_map.csv", index=False)
print(f"✅ Saved token map for {len(df)} stocks to symbol_token_map.csv")
