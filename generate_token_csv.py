import pandas as pd

# Load the correct CSV
df = pd.read_csv("angel_master_nse.csv")

# Clean column names
df.columns = df.columns.str.strip().str.lower()

# Only keep necessary columns
df = df[['symbol']]  # Keep only symbol
df['token'] = 999999  # Add dummy token

# Save new token map CSV
df.to_csv("smartapi_nse_master.csv", index=False)
print("✅ Created smartapi_nse_master.csv with dummy tokens.")
