import pyotp
import json
from SmartApi.smartConnect import SmartConnect

# === Angel One credentials ===
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

print("🚀 Logging in...")

# Step 1: Generate TOTP
totp = pyotp.TOTP(TOTP_SECRET).now()
print("🔐 TOTP:", totp)

try:
    obj = SmartConnect(api_key=API_KEY)
    response = obj.generate_session(CLIENT_CODE, PASSWORD, totp)

    # Step 2: Convert string to dict if needed
    if isinstance(response, str):
        print("📜 Parsing string response...")
        response = json.loads(response)

    print("🧾 Parsed response:")
    print(json.dumps(response, indent=2))

    # Step 3: Extract tokens
    if response.get("status") is True:
        jwt = response["data"]["jwtToken"]
        feed_token = response["data"]["feedToken"]
        print("✅ Login successful!")
        print("🔐 JWT Token:", jwt)
        print("📡 Feed Token:", feed_token)
    else:
        print("❌ Login failed:", response)

except Exception as e:
    print("❌ Exception during login:", e)
