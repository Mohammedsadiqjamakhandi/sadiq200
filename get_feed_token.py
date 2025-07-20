from SmartApi.smartConnect import SmartConnect
import pyotp

API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

# Generate TOTP
totp = pyotp.TOTP(TOTP_SECRET).now()

# Login
obj = SmartConnect(api_key=API_KEY)
data = obj.generateSession(CLIENT_CODE, PASSWORD, totp)
feed_token = obj.getfeedToken()

print("✅ Feed Token:", feed_token)
print("✅ Auth Token:", data["data"]["jwtToken"])
