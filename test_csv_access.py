import pandas as pd

try:
    df = pd.read_csv("nifty_200.csv")
    print("✅ File loaded successfully.")
    print(df.head())
except PermissionError:
    print("❌ Still facing permission issue. Please close Excel or any app using the file.")
except Exception as e:
    print(f"❌ Other error: {e}")
