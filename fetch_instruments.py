import pandas as pd
from SmartApi.smartConnect import SmartConnect
import pyotp

# === Login credentials ===
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"

import pyotp

TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

print("🚀 Logging in...")
obj = SmartConnect(api_key=API_KEY)
totp = pyotp.TOTP(TOTP_SECRET).now()
print("🔐 TOTP:", totp)

try:
    session = obj.generate_session(CLIENT_CODE, PASSWORD, totp)
    print("🔍 Raw Login Response:")
    print(session)

    # Handle failed login
    if not isinstance(session, dict) or "data" not in session:
        print("❌ Login failed. Check TOTP or credentials.")
        exit()

    print("✅ Login successful")

except Exception as e:
    print("❌ Login error:", e)
    exit()

# Download instrument list
print("📥 Downloading instrument file...")
try:
    df = pd.DataFrame(obj.get_instrument_list(exchange="NSE"))
    df.to_csv("instruments.csv", index=False)
    print("✅ Saved instruments.csv")
except Exception as e:
    print("❌ Failed to download instruments.csv:", e)
