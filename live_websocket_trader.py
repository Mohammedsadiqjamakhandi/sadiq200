from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import json
import time

# Replace these with your actual values from login
CLIENT_CODE = "YOUR_CLIENT_CODE"
FEED_TOKEN = "YOUR_FEED_TOKEN"
TOKEN = "26000"  # NSE:NIFTY index, replace with your desired token
TRADING_SYMBOL = "NIFTY"  # Just for print/logs

# Setup WebSocket object
sws = SmartWebSocketV2(FEED_TOKEN, CLIENT_CODE)

def on_data(wsapp, message):
    data = json.loads(message)
    if "data" in data:
        for tick in data["data"]:
            token = tick["token"]
            ltp = tick.get("last_traded_price", 0) / 100  # Price comes in paise
            print(f"📈 Live Tick: {TRADING_SYMBOL} - ₹{ltp}")

            # Example Trading Logic
            if ltp > 22000:
                print("🔔 Condition met! You can place a BUY order here")
                # Optional: Call your order placement logic here

def on_open(wsapp):
    print("✅ WebSocket connected.")
    # Subscribe to the token
    sws.subscribe([{"token": TOKEN, "action": 1}])  # 1 for subscribe

def on_error(wsapp, error):
    print(f"❌ WebSocket Error: {error}")

def on_close(wsapp):
    print("🔌 WebSocket connection closed.")

# Bind the events
sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error
sws.on_close = on_close

# Start WebSocket
print("🚀 Starting WebSocket for Live Market Data...")
sws.connect()
