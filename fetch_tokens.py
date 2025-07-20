import os
import pandas as pd
from SmartApi.smartConnect import SmartConnect
from dotenv import load_dotenv
import pyotp

# Load environment variables from .env
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

print("📥 Fetching NSE instrument list...")
instruments = obj.getInstruments(exchange="NSE")

df = pd.DataFrame(instruments)
df.to_csv("correct_nse_eq_symbols.csv", index=False)
print("✅ Saved correct_nse_eq_symbols.csv")

print(df.head())
