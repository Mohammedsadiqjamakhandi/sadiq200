import pandas as pd

df = pd.read_csv("smartapi_nse_master.csv")
df.columns = df.columns.str.strip().str.lower()
print("🧾 CSV Columns:", df.columns.tolist())
print("\n🔍 Sample Rows:")
print(df.head())
