import os
import json
import time
import pyotp
from dotenv import load_dotenv
from smartapi import SmartConnect
from smartapi.websocket import WebSocket

load_dotenv()

API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD = os.getenv("ANGEL_PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# ✅ Login and get token
def login():
    obj = SmartConnect(api_key=API_KEY)
    totp = pyotp.TOTP(TOTP_SECRET).now()
    data = obj.generateSession(CLIENT_CODE, PASSWORD, totp)
    feed_token = obj.getfeedToken()
    return obj, feed_token

# ✅ Callback functions
def on_open(ws):
    print("🔌 WebSocket Connected")
    # Subscribe to multiple tokens (example: RELIANCE & SBIN)
    symbols = {
        "RELIANCE-EQ": "2885",
        "SBIN-EQ": "3045"
    }
    for sym, token in symbols.items():
        print(f"📡 Subscribing to {sym}")
        ws.subscribe(ws.build_request(token=token, task="mw", segment="nse_cm"))

def on_data(ws, message):
    data = json.loads(message)
    if 'ltp' in data:
        print(f"📈 {data['tk']}: LTP = {data['ltp']}")

def on_error(ws, error):
    print("❌ Error:", error)

def on_close(ws):
    print("🔌 WebSocket Disconnected")

# ✅ Run WebSocket
def start_websocket():
    obj, feed_token = login()
    ws = WebSocket(
        client_code=CLIENT_CODE,
        feed_token=feed_token,
        auth_token=obj.session_token
    )
    ws.on_open = on_open
    ws.on_data = on_data
    ws.on_error = on_error
    ws.on_close = on_close
    ws.connect()
    while True:
        time.sleep(1)

if __name__ == "__main__":
    print("🚀 Starting Live WebSocket Feed...")
    start_websocket()
