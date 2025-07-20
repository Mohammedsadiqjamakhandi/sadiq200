import os
import json
import pyotp
import time
from datetime import datetime
from dotenv import load_dotenv
from SmartApi.smartConnect import SmartConnect
from smartapi.websocketV2 import SmartWebSocketV2

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# Generate TOTP
print("🚀 Generating TOTP...")
totp = pyotp.TOTP(TOTP_SECRET).now()

# Login
print("🚀 Logging into Angel One...")
obj = SmartConnect(api_key=API_KEY)
session = obj.generateSession(CLIENT_CODE, PASSWORD, totp)
feed_token = session['data']['feedToken']
print("✅ Logged in successfully!")

# Tokens to track (example: NIFTY 50, RELIANCE, INFY)
tokens = ['26000', '2885', '1594']  # Replace with your own NSE tokens

# Message handler
def on_message(ws, message):
    data = json.loads(message)
    token = data.get("tk")
    ltp = data.get("ltp")
    ts = datetime.now().strftime('%H:%M:%S')
    if token and ltp:
        print(f"[{ts}] Token {token} → LTP: {ltp}")

# Error handler
def on_error(ws, error):
    print("❌ WebSocket error:", error)

# Open handler
def on_open(ws):
    print("🌐 WebSocket opened. Subscribing to tokens...")
    sws.subscribe(tokens)

# Close handler
def on_close(ws, code, reason):
    print(f"🔌 WebSocket closed | Code: {code} | Reason: {reason}")

# Start WebSocket
sws = SmartWebSocketV2(
    feed_token=feed_token,
    client_code=CLIENT_CODE,
    on_message=on_message,
    on_error=on_error,
    on_open=on_open,
    on_close=on_close
)

sws.connect()

# Keep script running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    sws.close()
    print("👋 Exiting...")
