from SmartApi import SmartConnect  # Old SDK for login
from smartapi.websocket import WebSocket  # New SDK for WebSocket
import pyotp
import os
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP")

# Generate TOTP code
totp = pyotp.TOTP(TOTP_SECRET).now()

# ✅ Login to Angel One
print("🚀 Logging into Angel One...")
smart_api = SmartConnect(api_key=API_KEY)
session = smart_api.generateSession(CLIENT_CODE, PASSWORD, totp)
jwt_token = session["data"]["jwtToken"]
feed_token = smart_api.getfeedToken()
print("✅ Login successful!")
print("📨 Feed Token:", feed_token)

# Tokens to subscribe (you can add more)
symbols = {
    "RELIANCE-EQ": "2885",
    "TCS-EQ": "11536"
}

# ✅ WebSocket Callbacks
def on_tick(ws, ticks):
    for tick in ticks:
        print(f"📈 {tick['token']}: LTP ₹{tick['ltp']}")

def on_connect(ws):
    print("🌐 Connected. Subscribing to tokens...")
    ws.subscribe([
        {"token": token, "action": 1, "type": "ltp"} for token in symbols.values()
    ])

def on_error(ws, error):
    print("❌ WebSocket Error:", error)

def on_close(ws, code, reason):
    print(f"🔌 WebSocket closed: {code} - {reason}")

# ✅ Start WebSocket connection
ws = WebSocket(
    api_key=API_KEY,
    client_code=CLIENT_CODE,
    feed_token=feed_token
)
ws.on_open = on_connect
ws.on_data = on_tick
ws.on_error = on_error
ws.on_close = on_close

print("🔌 Connecting to WebSocket...")
ws.connect(threaded=False)
