import os
import sys
import ssl
import json
import base64
import time
from urllib.parse import unquote

# Fix module import path
sys.path.append(os.path.join(os.getcwd(), "SmartApi"))

from smartConnect import SmartConnect
from smartWebSocket import SmartWebSocket

# Angel One credentials
CLIENT_ID = "ASIFA1491"
MPIN = "9986"             # Replace with your MPIN
TOTP = "261197"           # Replace with your current TOTP

# Create SmartConnect instance
obj = SmartConnect(api_key="Shcr9brZ")

# Login using MPIN + TOTP
try:
    data = obj.generateSessionV2(
        client_id=CLIENT_ID,
        mpin=MPIN,
        totp=TOTP
    )
    print("✅ Login successful.")

    feed_token = data["data"]["feedToken"]
    print(f"Feed Token: {feed_token}")

    jwt_payload = data["data"]["jwtToken"].split('.')[1]
    padded = jwt_payload + '=' * (-len(jwt_payload) % 4)  # base64 padding
    decoded = base64.urlsafe_b64decode(padded)
    print("🔍 JWT Payload:", json.dumps(json.loads(decoded), indent=2))

except Exception as e:
    print(f"❌ Login failed: {e}")
    sys.exit(1)

# Define callback functions for WebSocket
def on_data(wsapp, message):
    print("📥 LTP Data:", message)

def on_open(wsapp):
    print("🔌 WebSocket connection opened.")
    # Subscribe format: { "task":"subscribe", "k":"nse_cm|RELIANCE", "mode":"ltp"}
    wsapp.send(json.dumps({"task": "subscribe", "k": "nse_cm|RELIANCE", "mode": "ltp"}))

def on_error(wsapp, error):
    print("❌ WebSocket error:", error)

def on_close(wsapp, code, reason):
    print(f"🔌 WebSocket closed with code: {code}, reason: {reason}")

# Create WebSocket connection
try:
    token = data["data"]["jwtToken"]
    ws = SmartWebSocket(client_code=CLIENT_ID, feed_token=feed_token, jwt_token=token)

    ws.on_open = on_open
    ws.on_data = on_data
    ws.on_error = on_error
    ws.on_close = on_close

    ws.connect()
except Exception as e:
    print(f"❌ Connection failed: {e}")
