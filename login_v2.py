from SmartApi.smartConnect import SmartConnect
import pyotp

API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
MPIN = "998697"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

totp = pyotp.TOTP(TOTP_SECRET).now()

obj = SmartConnect(api_key=API_KEY)
data = obj.generateSession(clientCode=CLIENT_CODE, mpin=MPIN, totp=totp)

print("✅ Login Successful")
print("Feed Token:", data['data']['feedToken'])
print("JWT Token:", data['data']['jwtToken'])
