import os
import pyotp
import logging
from SmartApi.smartConnect import SmartConnect
from SmartApi.webSocket import WebSocket
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(filename="log.txt", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# Generate TOTP
totp = pyotp.TOTP(TOTP_SECRET).now()

logging.info("🚀 Logging into Angel One...")
obj = SmartConnect(api_key=API_KEY)
try:
    data = obj.generateSession(CLIENT_CODE, PASSWORD, totp)
except Exception as e:
    logging.error(f"Login failed: {e}")
    exit()

if not data.get("status"):
    logging.error(f"❌ Login failed: {data}")
    exit()
logging.info("✅ Logged in successfully!")

# Get feed token
feed_token = obj.getfeedToken()

# Create WebSocket in LTP mode
ws = WebSocket(obj, CLIENT_CODE, feed_token, "ltp")

def on_open():
    logging.info("🔗 WebSocket connected. Subscribing...")
    try:
        ws.subscribe([
            {"exchangeType": 1, "token": "2885"},  # RELIANCE
            {"exchangeType": 1, "token": "1594"}   # INFY
        ])
    except Exception as e:
        logging.error(f"Subscription error: {e}")

def on_tick(tick_data):
    logging.info(f"📈 Tick Data: {tick_data}")

def on_error(error):
    logging.error(f"❌ WebSocket error: {error}")

def on_close():
    logging.info("🔌 WebSocket closed")

# Assign callbacks
ws.on_open = on_open
ws.on_data = on_tick
ws.on_error = on_error
ws.on_close = on_close

logging.info("🌐 Connecting to WebSocket...")
try:
    ws.connect()
except Exception as e:
    logging.error(f"WebSocket failed to connect: {e}")
