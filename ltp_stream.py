import os
import time
import pyotp
import pandas as pd
from smartapi.smartConnect import SmartConnect
from dotenv import load_dotenv

load_dotenv()

# 🔐 Credentials
API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD = os.getenv("ANGEL_PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# 🔑 Generate TOTP and login
totp = pyotp.TOTP(TOTP_SECRET).now()
obj = SmartConnect(api_key=API_KEY)
data = obj.generateSession(CLIENT_CODE, PASSWORD, totp)
feed_token = data["feedToken"]
print("✅ Logged in successfully!")

# 📁 Load master file
df = pd.read_csv("smartapi_nse_master.csv")
symbols_to_check = df.head(5)  # first 5 symbols
token_map = dict(zip(symbols_to_check["token"].astype(str), symbols_to_check["symbol"]))

# 🟢 Get LTP for each token
ltps = obj.ltpData("NSE", symbols_to_check["symbol"].tolist())
for stock in ltps["data"]:
    symbol = stock["symbol"]
    ltp = stock["ltp"]
    print(f"📈 {symbol}: ₹{ltp}")
