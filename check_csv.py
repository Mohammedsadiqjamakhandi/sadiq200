import pandas as pd

df = pd.read_csv("candles.csv")
print("Columns:", df.columns)

if "symbol" in df.columns:
    print("✅ 'symbol' column found.")
    print("📊 Unique Stocks:", df['symbol'].nunique())
    print("🧾 Sample symbols:", df['symbol'].unique()[:10])
else:
    print("❌ 'symbol' column not found. Please check the file structure.")
