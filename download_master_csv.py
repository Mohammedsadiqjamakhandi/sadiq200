import pandas as pd
import requests

url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
response = requests.get(url)
data = response.json()

df = pd.DataFrame(data)

# Use the correct key names: 'exch_seg' and 'symbol'
df_eq = df[(df['exch_seg'] == 'NSE') & (df['symbol'].str.endswith('-EQ'))].copy()

df_eq.to_csv("smartapi_nse_master.csv", index=False)
print(f"✅ Saved {len(df_eq)} EQ stocks to smartapi_nse_master.csv")
