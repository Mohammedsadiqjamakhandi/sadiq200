import os
import time
import pyotp
import requests
import pandas as pd
from datetime import datetime, timedelta

# === LOGIN DETAILS ===
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

# === FILE PATHS ===
NIFTY_200_CSV = "nifty_200.csv"
OUTPUT_DIR = "candles"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Generate TOTP ===
def generate_totp():
    return pyotp.TOTP(TOTP_SECRET).now()

# === Login to SmartAPI ===
def login():
    otp = generate_totp()
    url = "https://apiconnect.angelbroking.com/rest/auth/angelbroking/user/v1/loginByPassword"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-UserType": "USER",
        "X-SourceID": "WEB",
        "X-ClientLocalIP": "127.0.0.1",
        "X-ClientPublicIP": "127.0.0.1",
        "X-MACAddress": "00:11:22:33:44:55",
        "X-PrivateKey": API_KEY
    }
    payload = {
        "clientcode": CLIENT_CODE,
        "password": PASSWORD,
        "totp": otp
    }
    r = requests.post(url, json=payload, headers=headers).json()
    if r["status"] == True:
        print("✅ Login Success")
        return r["data"]["jwtToken"], r["data"]["feedToken"]
    else:
        print("❌ Login Failed:", r)
        exit()

# === Fetch Historical 1-Minute Candles ===
def fetch_candles(symbol, jwt_token):
    url = "https://apiconnect.angelbroking.com/rest/secure/angelbroking/historical/v1/getCandleData"

    end_time = datetime.now()
    start_time = end_time - timedelta(days=10)

    params = {
        "exchange": "NSE",
        "symboltoken": "",
        "interval": "ONE_MINUTE",
        "fromdate": start_time.strftime("%Y-%m-%d %H:%M"),
        "todate": end_time.strftime("%Y-%m-%d %H:%M")
    }

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-UserType": "USER",
        "X-SourceID": "WEB",
        "X-ClientLocalIP": "127.0.0.1",
        "X-ClientPublicIP": "127.0.0.1",
        "X-MACAddress": "00:11:22:33:44:55",
        "X-PrivateKey": API_KEY
    }

    # === Get instrument token for symbol ===
    instruments = pd.read_csv("instruments.csv")  # Must contain all NSE stocks
    row = instruments[(instruments["symbol"] == symbol) & (instruments["exchange"] == "NSE") & (instruments["instrumenttype"] == "EQ")]
    if row.empty:
        print(f"❌ Token not found for {symbol}")
        return

    token = str(row.iloc[0]["token"])
    params["symboltoken"] = token
    payload = {
        "exchange": params["exchange"],
        "symboltoken": token,
        "interval": params["interval"],
        "fromdate": params["fromdate"],
        "todate": params["todate"]
    }

    res = requests.post(url, json=payload, headers=headers).json()
    if "data" in res and res["data"]:
        candles = pd.DataFrame(res["data"], columns=["timestamp", "open", "high", "low", "close", "volume"])
        candles.to_csv(f"{OUTPUT_DIR}/{symbol}.csv", index=False)
        print(f"✅ Saved {symbol} candles")
    else:
        print(f"⚠️ No data for {symbol}")

# === MAIN ===
def main():
    jwt_token, feed_token = login()

    symbols = pd.read_csv(NIFTY_200_CSV)["symbol"].tolist()
    for symbol in symbols:
        try:
            fetch_candles(symbol, jwt_token)
            time.sleep(0.5)  # Respect rate limits
        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")

if __name__ == "__main__":
    main()
