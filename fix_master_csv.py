import pandas as pd

# Load original file
df = pd.read_csv("smartapi_nse_master.csv")

# Remove rows with missing or non-EQ instrumenttype
df_cleaned = df[df["instrumenttype"] == "EQ"].copy()

# Drop rows with missing symbol/token
df_cleaned = df_cleaned.dropna(subset=["symbol", "token"])

# Save cleaned version
df_cleaned.to_csv("nse_eq_cleaned.csv", index=False)

print("✅ Cleaned EQ stock list saved to nse_eq_cleaned.csv")
print("✅ Total EQ stocks:", len(df_cleaned))
