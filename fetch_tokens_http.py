import requests
import pandas as pd

print("📥 Downloading official NSE symbol-token list CSV...")

url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/NSEEquity.csv"

response = requests.get(url)
if response.status_code == 200:
    with open("correct_nse_eq_symbols.csv", "wb") as f:
        f.write(response.content)
    print("✅ Saved correct_nse_eq_symbols.csv")
    df = pd.read_csv("correct_nse_eq_symbols.csv")
    print(df.head())
else:
    print("❌ Failed to download CSV. Status code:", response.status_code)
