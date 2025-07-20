from smartapi import SmartConnect
from smartapi.websocket.smartWebSocketV2 import SmartWebSocketV2
import pyotp
import os

# Replace with your actual credentials or load from .env
API_KEY = "your_api_key"
CLIENT_CODE = "your_client_code"
PASSWORD = "your_password"
TOTP_SECRET = "your_totp_secret"

# Generate TOTP
totp = pyotp.TOTP(TOTP_SECRET).now()
print("🚀 Logging in...")
obj = SmartConnect(api_key=API_KEY)
data = obj.generate_session(CLIENT_CODE, PASSWORD, totp)
print("✅ Login successful.")

jwt_token = data["data"]["jwtToken"]
feed_token = data["data"]["feedToken"]
client_code = data["data"]["clientcode"]

print("🚀 Connecting to WebSocket...")
sws = SmartWebSocketV2(
    auth_token=jwt_token,
    api_key=API_KEY,
    client_code=client_code,
    feed_token=feed_token
)
sws.connect()