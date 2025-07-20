import pandas as pd

# Load your SmartAPI NSE master CSV
df = pd.read_csv("smartapi_nse_master.csv")

# Normalize and rename columns
df.columns = df.columns.str.strip().str.lower()
df.rename(columns={
    "instrument type": "instrumenttype"
}, inplace=True)

# Manually add 'exch_seg' as 'NSE' for all rows (since this file is only for NSE)
df["exch_seg"] = "NSE"

# Filter only NSE EQ stocks
if "instrumenttype" in df.columns:
    df = df[(df["instrumenttype"] == "EQ") & (df["exch_seg"] == "NSE")]
    print(f"✅ Total EQ stocks found: {len(df)}")
    print(df.head())
else:
    print("❌ 'instrumenttype' column not found in your master CSV.")
    exit()
