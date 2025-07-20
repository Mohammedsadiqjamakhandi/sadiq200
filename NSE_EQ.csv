import requests

url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"

print("📥 Downloading instrument list...")
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    # Filter only NSE EQ stocks
    nse_eq = [row for row in data if row["exch_seg"] == "NSE" and row["symbol"].endswith("-EQ")]

    import pandas as pd
    df = pd.DataFrame(nse_eq)
    df[["token", "symbol"]].to_csv("nse_eq_symbols.csv", index=False)
    print("✅ Saved nse_eq_symbols.csv with", len(df), "symbols.")
else:
    print("❌ Failed to download data:", response.status_code)
