import os
import pandas as pd
from SmartApi.smartConnect import SmartConnect
import pyotp
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD = os.getenv("ANGEL_PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

print("🔐 Logging in...")

# Generate dynamic TOTP
totp = pyotp.TOTP(TOTP_SECRET).now()

# Initialize SmartAPI
smart_api = SmartConnect(api_key=API_KEY)

try:
    smart_api.generateSession(CLIENT_CODE, PASSWORD, totp)
    print("✅ Logged in.")
except Exception as e:
    print("❌ Login failed:", e)
    exit()

# Read your old CSV
try:
    df_old = pd.read_csv("angel_master_nse.csv")
    df_old.columns = df_old.columns.str.strip().str.lower()
    symbols = df_old["symbol"].tolist()
except Exception as e:
    print("❌ Error reading CSV:", e)
    exit()

# Fetch master from API
try:
    all_data = smart_api.get_instrument_list(exchange="NSE")
except Exception as e:
    print("❌ Could not fetch instrument list:", e)
    exit()

# Create token mapping
final_data = []
symbol_set = set([s.strip().upper() for s in symbols])

for entry in all_data:
    if entry["symbol"].strip().upper() in symbol_set:
        final_data.append({
            "symbol": entry["symbol"],
            "token": entry["token"]
        })

# Save final file
df = pd.DataFrame(final_data)
df.to_csv("final_tokens.csv", index=False)
print(f"✅ Saved token mapping: {len(df)} symbols to final_tokens.csv")
