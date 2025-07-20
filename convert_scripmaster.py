import json
import pandas as pd

# Load JSON file
with open("C:/Users/azt/ScripMaster.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Confirm data is a list
if not isinstance(data, list):
    print("❌ Unexpected data format. Expected a list.")
    exit()

# Convert to DataFrame
df = pd.DataFrame(data)

# Show available columns for confirmation
print("📊 Available columns:", list(df.columns))

# Try best guess filtering (some Angel CSVs use 'exchange', some use 'exch_seg')
exchange_col = None
for col in df.columns:
    if col.lower() in ['exch', 'exchange', 'exch_seg']:
        exchange_col = col
        break

if not exchange_col:
    print("❌ No exchange column like 'exch', 'exchange', or 'exch_seg' found.")
    exit()

# Filter only NSE
df_nse = df[df[exchange_col].str.upper() == "NSE"]

# Select only useful columns, if they exist
keep = []
for col in ['symbol', 'token', 'name', 'instrumenttype']:
    if col in df_nse.columns:
        keep.append(col)

df_nse = df_nse[keep]

# Save final
output_path = "C:/Users/azt/Desktop/saniya/smartapi_nse_master.csv"
df_nse.to_csv(output_path, index=False)

print(f"✅ Saved {len(df_nse)} NSE instruments to {output_path}")
