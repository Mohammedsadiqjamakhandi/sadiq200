from SmartApi.smartConnect import SmartConnect
import os
import pyotp
from dotenv import load_dotenv
import pandas as pd

# Load environment variables from .env
load_dotenv()

api_key = os.getenv("ANGEL_API_KEY")
client_code = os.getenv("ANGEL_CLIENT_CODE")
password = os.getenv("ANGEL_PASSWORD")
totp_secret = os.getenv("ANGEL_TOTP")
totp_code = pyotp.TOTP(totp_secret).now()

# Step 1: Login
smart_api = SmartConnect(api_key)
session = smart_api.generateSession(client_code, password, totp_code)

if not session.get("status"):
    print("❌ Login failed.")
    exit()
print("✅ Logged in successfully.")

# Step 2: Fetch instrument list
print("📥 Downloading NSE master contract...")
instrument_list = smart_api.getMasterContract("NSE")

# Step 3: Convert to DataFrame
instrument_df = pd.DataFrame(instrument_list)
print("✅ Master contract loaded with", len(instrument_df), "rows.")

# Step 4: Save to CSV (optional)
instrument_df.to_csv("angel_master_nse.csv", index=False)
print("💾 Saved as 'angel_master_nse.csv'")
