import pyotp
import json
from SmartApi.smartConnect import SmartConnect

# === Angel One Credentials ===
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

print("🚀 Logging in...")

# Generate TOTP
totp = pyotp.TOTP(TOTP_SECRET).now()
print("🔐 TOTP:", totp)

try:
    obj = SmartConnect(api_key=API_KEY)

    raw_response = obj.generate_session(CLIENT_CODE, PASSWORD, totp)

    # 🧪 Check and parse if needed
    if isinstance(raw_response, str):
        print("📜 Parsing string response...")
        response = json.loads(raw_response)
    else:
        response = raw_response

    print("📦 Full Parsed Response:")
    print(json.dumps(response, indent=2))

    if response.get("status") is True:
        jwt = response["data"]["jwtToken"]
        feed_token = response["data"]["feedToken"]
        print("✅ Login successful!")
        print("🔐 JWT Token:", jwt)
        print("📡 Feed Token:", feed_token)
    else:
        print("❌ Login failed:", response)

except json.JSONDecodeError:
    print("❌ Failed to parse JSON response. Response was:")
    print(raw_response)
except Exception as e:
    print("❌ Exception during login:", e)
