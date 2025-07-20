import pandas as pd
from SmartApi.smartConnect import SmartConnect  # ✅ correct import
import pyotp
from datetime import datetime, timedelta
import time

# 🔐 SmartAPI credentials (put your real keys in .env or directly here)
API_KEY = "YOUR_API_KEY"
CLIENT_CODE = "YOUR_CLIENT_CODE"
PIN = "YOUR_PIN"
TOTP_SECRET = "YOUR_TOTP_SECRET"

# ✅ SmartAPI login function
def smartapi_login():
    obj = SmartConnect(api_key=API_KEY)
    totp = pyotp.TOTP(TOTP_SECRET).now()
    data = obj.generateSession(CLIENT_CODE, PIN, totp)
    return obj

# ⏳ Time window
end_date = datetime.now()
start_date = end_date - timedelta(days=1)

# 📥 Load symbols from your master CSV
df_master = pd.read_csv("smartapi_nse_master.csv")
symbols = df_master[df_master['series'] == 'EQ'][['symbol', 'token']].drop_duplicates()

# 🚀 Login
obj = smartapi_login()

records = []

# ⛳ Fetch candles (limit to 5 first for test, then remove [:5] to run full)
for _, row in symbols.iterrows():
    symbol = row['symbol']
    token = str(row['token'])

    try:
        print(f"🔄 Fetching: {symbol}")
        params = {
            "exchange": "NSE",
            "symboltoken": token,
            "interval": "ONE_MINUTE",
            "fromdate": start_date.strftime("%Y-%m-%d %H:%M"),
            "todate": end_date.strftime("%Y-%m-%d %H:%M"),
        }
        data = obj.getCandleData(params)

        for candle in data['data']:
            records.append({
                "symbol": symbol,
                "date": candle[0],
                "open": candle[1],
                "high": candle[2],
                "low": candle[3],
                "close": candle[4],
                "volume": candle[5]
            })

    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
    time.sleep(0.5)

# 💾 Save to CSV
df = pd.DataFrame(records)
df.to_csv("candles.csv", index=False)
print("\n✅ candles.csv saved with", len(df), "rows.")
