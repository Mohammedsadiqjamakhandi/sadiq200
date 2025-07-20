import pyotp
from SmartApi.smartConnect import SmartConnect

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

    print("\n📦 RAW RESPONSE:")
    print("Type:", type(response))
    print("Content:", response)

except Exception as e:
    print("❌ Exception:", e)
