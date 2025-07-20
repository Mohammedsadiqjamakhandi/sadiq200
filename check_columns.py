import pandas as pd

df = pd.read_csv("candles.csv")
print("🧾 CSV Columns:", df.columns.tolist())
print(df.head(2))
