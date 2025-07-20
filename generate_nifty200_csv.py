import pandas as pd

symbols = [
    "RELIANCE-EQ", "TCS-EQ", "INFY-EQ", "HDFCBANK-EQ", "ICICIBANK-EQ",
    "LT-EQ", "SBIN-EQ", "HINDUNILVR-EQ", "AXISBANK-EQ", "ITC-EQ"
]
df = pd.DataFrame({"symbol": symbols})
df.to_csv("nifty_200.csv", index=False)
print("✅ New nifty_200.csv file created.")
