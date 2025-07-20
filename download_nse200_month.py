import os
import time
import pandas as pd
from datetime import datetime, timedelta
from SmartApi.smartConnect import SmartConnect
import pyotp
from dotenv import load_dotenv

# === Load .env credentials ===
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# === Login ===
smart_api = SmartConnect(api_key=API_KEY)
token = pyotp.TOTP(TOTP_SECRET).now()
smart_api.generateSession(CLIENT_CODE, PASSWORD, token)
print("✅ Logged in to SmartAPI")

# === Load NSE 200 Symbols ===
symbols_df = pd.read_csv("nse200_symbols.csv")
symbols_df.columns = symbols_df.columns.str.strip()

# === Setup days to fetch ===
days_to_check = 30  # last 30 calendar days
base_path = "candles"

# === Start downloading ===
for _, row in symbols_df.iterrows():
    symbol = row["symbol"]
    token = str(row["token"])
    all_candles = []

    print(f"\n📥 Downloading: {symbol}")

    for i in range(days_to_check, 0, -1):
        date = datetime.today() - timedelta(days=i)
        if date.weekday() >= 5:
            continue  # Skip Saturday (5) and Sunday (6)

        from_dt = datetime.combine(date.date(), datetime.min.time())
        to_dt = datetime.combine(date.date(), datetime.max.time())

        params = {
            "exchange": "NSE",
            "symboltoken": token,
            "tradingsymbol": symbol,
            "interval": "ONE_MINUTE",
            "fromdate": from_dt.strftime("%Y-%m-%d %H:%M"),
            "todate": to_dt.strftime("%Y-%m-%d %H:%M")
        }

        try:
            response = smart_api.getCandleData(params)
            data = response.get("data", [])
            if data:
                all_candles.extend(data)
                print(f"  ✅ {date.date()} - {len(data)} candles")
            else:
                print(f"  ⚠️ {date.date()} - No data returned")
        except Exception as e:
            print(f"  ❌ {date.date()} error: {e}")
        time.sleep(1)

    if all_candles:
        df = pd.DataFrame(all_candles, columns=["time", "open", "high", "low", "close", "volume"])
        df.to_csv(os.path.join(base_path, f"{symbol}.csv"), index=False)
        print(f"  💾 Saved: {symbol}.csv ({len(all_candles)} rows)")
    else:
        print(f"  ⚠️ No valid data for {symbol}")
