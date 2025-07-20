import os
import time
import pyotp
import requests
from SmartApi.smartConnect import SmartConnect

# ✅ Load credentials
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

# ✅ Step 1: Generate TOTP
totp = pyotp.TOTP(TOTP_SECRET).now()
print(f"🔐 TOTP: {totp}")

# ✅ Step 2: Create SmartConnect object
obj = SmartConnect(api_key=API_KEY)

# ✅ Step 3: Try to login
try:
    data = obj.generate_session(client_code=CLIENT_CODE, password=PASSWORD, totp=totp)
    if "data" in data and "refreshToken" in data["data"]:
        print("✅ Login successful.")
        print("🔑 Auth Token:", obj.session_token)
    else:
        print("❌ Login failed.")
        print("🧾 Full response:", data)
except Exception as e:
    print("❌ Exception during login:", str(e))
