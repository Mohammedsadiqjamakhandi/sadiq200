import pyotp
from SmartApi.smartConnect import SmartConnect

# === Login credentials ===
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

print("🚀 Logging in...")
totp = pyotp.TOTP(TOTP_SECRET).now()
print("🔐 TOTP:", totp)

try:
    obj = SmartConnect(api_key=API_KEY)
    raw_response = obj.generate_session(CLIENT_CODE, PASSWORD, totp)

    print("\n🧾 Raw generate_session() response:")
    print(type(raw_response))
    print(raw_response)

except Exception as e:
    print("❌ Exception during login:", e)
