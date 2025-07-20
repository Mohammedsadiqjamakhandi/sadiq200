from SmartApi.smartConnect import SmartConnect
import pyotp
import time

# Angel One Credentials
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PIN = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

# Generate TOTP
totp = pyotp.TOTP(TOTP_SECRET).now()

# Create SmartConnect Object
obj = SmartConnect(api_key=API_KEY)

# Login and get tokens
data = obj.generateSession(CLIENT_CODE, PIN, totp)
refreshToken = data['data']['refreshToken']
feed_token = obj.getfeedToken()
client_code = data['data']['clientcode']

print("✅ Login successful")
print("Feed Token:", feed_token)
print("Client Code:", client_code)

# Optional: Get LTP for multiple symbols
symbols = [
    {"exchange": "NSE", "tradingsymbol": "RELIANCE-EQ", "symboltoken": "2885"},
    {"exchange": "NSE", "tradingsymbol": "SBIN-EQ", "symboltoken": "3045"},
]

for s in symbols:
    ltp_data = obj.ltpData(s["exchange"], s["tradingsymbol"], s["symboltoken"])
    print(f'📈 {s["tradingsymbol"]}: ₹{ltp_data["data"]["ltp"]}')
    time.sleep(1)
