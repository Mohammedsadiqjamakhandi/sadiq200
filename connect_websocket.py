from smartapi import WebSocket
import json

# Replace with your actual credentials
API_KEY = "your_api_key"
CLIENT_CODE = "your_client_code"
FEED_TOKEN = "your_feed_token"

# Callback functions
def on_open(ws):
    print("✅ WebSocket connection opened")
    # Example: Subscribe to NIFTY 50 index (token=99926000 for index)
    token = "nse_cm|26000"  # Change this to your desired instrument
    ws.subscribe([token])

def on_data(ws, data):
    print("📈 Tick Data Received:")
    print(json.dumps(data, indent=2))

def on_error(ws, error):
    print("❌ Error:", error)

def on_close(ws):
    print("🔌 WebSocket closed")

# Setup WebSocket
ws = WebSocket(api_key=API_KEY,
               client_code=CLIENT_CODE,
               feed_token=FEED_TOKEN,
               task="mw",  # 'mw' for market watch
               connect_timeout=10)

# Assign callbacks
ws.on_open = on_open
ws.on_data = on_data
ws.on_error = on_error
ws.on_close = on_close

# Start the WebSocket connection
ws.connect()
