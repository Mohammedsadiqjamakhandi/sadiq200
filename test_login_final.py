import pyotp
import json
from SmartApi.smartConnect import SmartConnect

# === Credentials ===
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

print("🚀 Logging in...")
totp = pyotp.TOTP(TOTP_SECRET).now()
print("🔐 TOTP:", totp)

try:
    obj = SmartConnect(api_key=API_KEY)
    response = obj.generate_session(CLIENT_CODE, PASSWORD, totp)

    # 👇 PRINT RAW OUTPUT before processing
    print("\n📦 Raw response from generate_session:")
    print("Type:", type(response))
    print("Content:", response)

    # 👇 Only parse if it's a string
    if isinstance(response, str):
        print("📜 Parsing string response...")
        response = json.loads(response)

    print("\n🧾 Parsed response:")
    print(json.dumps(response, indent=2))

    if response.get("status") is True:
        jwt_token = response["data"]["jwtToken"]
        print("✅ Login successful!")
        print("🔐 JWT Token:", jwt_token)
    else:
        print("❌ Login failed:", response)

except Exception as e:
    print("❌ Exception during login:", e)
