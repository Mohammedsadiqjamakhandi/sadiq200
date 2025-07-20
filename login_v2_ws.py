from SmartApi.smartConnect import SmartConnectV2
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import pyotp

# Your credentials
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
MPIN = "998697"
TOTP_SECRET = "YOUR_TOTP_SECRET"  # Replace this

# Generate TOTP
totp = pyotp.TOTP(TOTP_SECRET).now()

# Login
obj = SmartConnectV2(api_key=API_KEY)
data = obj.generateSession(clientCode=CLIENT_CODE, mpin=MPIN, totp=totp)

print("✅ Login Successful")
print("JWT:", data['data']['jwtToken'])
print("Feed Token:", data['data']['feedToken'])

# Optional: Start WebSocket
sws = SmartWebSocketV2(
    auth_token=data['data']['jwtToken'],
    api_key=API_KEY,
    client_code=CLIENT_CODE,
    feed_token=data['data']['feedToken']
)

def on_open(wsapp):
    print("📡 WebSocket Connected")

def on_data(wsapp, msg):
    print("📈 Tick:", msg)

sws.on_open = on_open
sws.on_data = on_data

# Uncomment to start WebSocket:
# sws.connect()
