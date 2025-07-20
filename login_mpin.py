from SmartApi.smartConnect import SmartConnect
import pyotp

# === Replace your credentials ===
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
MPIN = "998697"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"  # Replace with your TOTP secret

# === Generate TOTP ===
totp = pyotp.TOTP(TOTP_SECRET).now()

# === Login ===
obj = SmartConnect(api_key=API_KEY)
data = obj.generateSession(clientCode=CLIENT_CODE, password=MPIN, totp=totp)

print("✅ Login Success")
print("Feed Token:", data['feedToken'])
print("JWT Token:", data['jwtToken'])
print("Refresh Token:", data['refreshToken'])
