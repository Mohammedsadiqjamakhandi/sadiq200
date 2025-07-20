from SmartApi.smartConnect import SmartConnect
from smartapi.websocket import WebSocket
from dotenv import load_dotenv
import os
import pyotp
import json
from telegram_alerts import send_telegram_message

# Load credentials
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# Step 1: Login
totp = pyotp.TOTP(TOTP_SECRET).now()
obj = SmartConnect(api_key=API_KEY)
data = obj.generateSession(CLIENT_CODE, PASSWORD, totp)
tokens = data['data']
feed_token = tokens['feedToken']
client_code = tokens['client_code']
jwt_token = tokens['jwtToken']

# Step 2: Tokens stored to re-use later
with open("session_tokens.env", "w") as f:
    f.write(f"FEED_TOKEN={feed_token}\n")
    f.write(f"JWT_TOKEN={jwt_token}\n")
    f.write(f"CLIENT_CODE={client_code}\n")

print("✅ Logged in & tokens saved.")
send_telegram_message("✅ Angel One Login Successful & WebSocket Starting...")

# Step 3: List of stocks (add more here)
symbols = {
    "RELIANCE-EQ": "2885",
    "INFY-EQ": "1594",
    "SBIN-EQ": "3045"
}

# Step 4: Define WebSocket callbacks
def on_tick(ws, tick):
    for item in tick:
        token = str(item['token'])
        ltp = item['last_traded_price'] / 100
        symbol = [s for s, t in symbols.items() if t == token][0]
        msg = f"📈 <b>{symbol}</b>: ₹{ltp}"
        print(msg)
        send_telegram_message(msg)

def on_connect(ws):
    print("🔌 WebSocket Connected. Subscribing...")
    ws.subscribe(list(symbols.values()))
    ws.send_channel_request(token_list=list(symbols.values()), feed_type="LTP")

def on_close(ws):
    print("❌ WebSocket Closed.")
    send_telegram_message("❌ Angel One WebSocket disconnected.")

def on_error(ws, code, reason):
    print("⚠️ WebSocket Error:", code, reason)
    send_telegram_message(f"⚠️ WebSocket Error: {code} | {reason}")

# Step 5: Start WebSocket
ws = WebSocket(api_key=API_KEY,
               client_code=client_code,
               feed_token=feed_token)

ws.on_ticks = on_tick
ws.on_connect = on_connect
ws.on_close = on_close
ws.on_error = on_error

print("🌐 Connecting to WebSocket...")
ws.connect()
