
import pandas as pd

# Load the CSV
df = pd.read_csv("EQUITY_L.csv")

# Just get the SYMBOL column
symbols = df['SYMBOL'].tolist()

# Show a few symbols
print("Total symbols found:", len(symbols))
print("Some examples:", symbols[:20])  # first 20
