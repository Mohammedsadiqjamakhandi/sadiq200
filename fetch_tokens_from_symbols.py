import os
import pandas as pd
from SmartApi.smartConnect import SmartConnect
from dotenv import load_dotenv
import pyotp

load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

def generate_totp():
    return pyotp.TOTP(TOTP_SECRET).now()

print("🚀 Logging in...")
obj = SmartConnect(api_key=API_KEY)
data = obj.generateSession(CLIENT_CODE, PASSWORD, generate_totp())
print("✅ Logged in successfully.")

print("📥 Fetching all NSE instruments...")
try:
    instruments = obj.get_all_instruments(exchange="NSE")
except AttributeError:
    print("❌ get_all_instruments() not found. Please update your SDK or ask me for help.")
    exit()

df = pd.DataFrame(instruments)
df.to_csv("all_nse_instruments.csv", index=False)
print("✅ Saved all NSE instruments to all_nse_instruments.csv")
