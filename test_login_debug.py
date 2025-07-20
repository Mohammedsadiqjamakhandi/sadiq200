import pyotp
from SmartApi.smartConnect import SmartConnect

API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

def generate_totp():
    return pyotp.TOTP(TOTP_SECRET).now()

print("🚀 Logging in...")
totp = generate_totp()
print(f"🔐 TOTP: {totp}")

try:
    obj = SmartConnect(api_key=API_KEY)
    response = obj.generate_session(CLIENT_CODE, PASSWORD, totp)

    print("📦 Type of response:", type(response))
    print("🧾 Full response:", response)
except Exception as e:
    print("❌ Exception during login:")
    print(e)
