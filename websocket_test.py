from smartapi.smartConnect import SmartConnect
from smartwebsocket.smartWebSocketV2 import SmartWebSocketV2  # ✅ Corrected import
import os
from dotenv import load_dotenv

# rest of your code...

# Load credentials from .env
api_key = "Shcr9brZ"
client_code = "ASIFA1491"
password = "9986"
totp_secret = "6VDXFQ23A54VT6AISO6XKYX5NE"

# Generate TOTP
totp = pyotp.TOTP(totp_secret).now()

print("🚀 Logging in...")
obj = SmartConnect(api_key=api_key)
data = obj.generateSession(client_code, password, totp)
auth_token = data["data"]["jwtToken"]
feed_token = obj.getfeedToken()
print("✅ Login successful.")
print("🔐 JWT Token:", auth_token)
print("🔐 Feed Token:", feed_token)

# Get token for RELIANCE-EQ
scrip_info = obj.searchScrip("NSE", "RELIANCE-EQ")
token = scrip_info["data"][0]["symboltoken"]
print("📄 RELIANCE token:", token)

# Run WebSocket connection
sws = SmartWebSocketV2(
    auth_token=auth_token,
    api_key=api_key,
    client_code=client_code,
    feed_token=feed_token
)

# Launch WebSocket and subscribe to RELIANCE-EQ
async def main():
    await sws._connect()

async def wrapper():
    await asyncio.sleep(2)
    await sws.subscribe(tokens=[f"nse_cm|{token}"])

asyncio.run(wrapper())
