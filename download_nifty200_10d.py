import os
import pandas as pd
import datetime as dt
import time
from SmartApi.smartConnect import SmartConnect
import pyotp
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

print("🚀 Logging in...")
obj = SmartConnect(api_key=API_KEY)
totp = pyotp.TOTP(TOTP_SECRET).now()
try:
    data = obj.generate_session(CLIENT_CODE, PASSWORD, totp)
    refreshToken = data["data"]["refreshToken"]
    feedToken = obj.getfeedToken()
    print("✅ Login successful.")
except Exception as e:
    print("❌ Login failed:", e)
    exit()

# === Load instrument data ===
instrument_df = pd.read_csv("instruments.csv")
nifty200_df = instrument_df[
    (instrument_df["name"] == "NIFTY200") & (instrument_df["exchange"] == "NSE") & (instrument_df["symbol"].str.endswith("-EQ"))
]
symbols = nifty200_df["symbol"].tolist()
print(f"📈 Found {len(symbols)} NIFTY 200 symbols.")

# === Candle download ===
start_time = (dt.datetime.now() - dt.timedelta(days=10)).replace(hour=9, minute=15)
end_time = dt.datetime.now().replace(hour=15, minute=30)

output_dir = "nifty200_1min"
os.makedirs(output_dir, exist_ok=True)

for symbol in symbols:
    token_row = instrument_df[(instrument_df["symbol"] == symbol) & (instrument_df["exchange"] == "NSE")]
    if token_row.empty:
        print(f"⚠️ Token not found for {symbol}")
        continue

    token = str(token_row.iloc[0]["token"])
    try:
        candle_data = obj.getCandleData(
            interval="ONE_MINUTE",
            exchange="NSE",
            symboltoken=token,
            fromdate=start_time.strftime("%Y-%m-%d %H:%M"),
            todate=end_time.strftime("%Y-%m-%d %H:%M")
        )

        candles = candle_data["data"]
        if candles:
            df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df.to_csv(f"{output_dir}/{symbol}.csv", index=False)
            print(f"✅ Saved {symbol}.csv")
        else:
            print(f"❌ No data for {symbol}")
    except Exception as e:
        print(f"❌ Error for {symbol}: {e}")
    time.sleep(1)  # avoid rate limiting
