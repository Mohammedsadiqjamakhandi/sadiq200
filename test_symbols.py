import pandas as pd

CSV_PATH = "smartapi_nse_master.csv"  # Make sure this matches your actual CSV file name

try:
    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip().str.lower()

    if 'symbol' in df.columns and 'token' in df.columns:
        print(f"✅ Found {len(df)} symbols.")
        print(df[['symbol', 'token']].head())  # Show sample rows
    else:
        print(f"❌ 'symbol' and/or 'token' column not found. Columns are:\n{df.columns.tolist()}")

except Exception as e:
    print(f"❌ Failed to read CSV: {e}")
