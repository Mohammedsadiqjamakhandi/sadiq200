import os
from SmartApi.smartConnect import SmartConnect
from dotenv import load_dotenv
import pyotp

# Load .env file
load_dotenv()

# Get environment variables
api_key = os.getenv("ANGEL_API_KEY")
client_code = os.getenv("ANGEL_CLIENT_CODE")
password = os.getenv("ANGEL_PASSWORD")
totp_secret = os.getenv("ANGEL_TOTP")  # This is your TOTP SECRET — NOT the 6-digit code!

# Debug print
print("🔍 Debugging environment variables:")
print(f"API Key: {api_key}")
print(f"Client Code: {client_code}")
print(f"Password: {password}")
print(f"TOTP Secret: {totp_secret}")

# ✅ Generate 6-digit TOTP code using pyotp
totp_code = pyotp.TOTP(totp_secret).now()
print(f"TOTP Code: {totp_code}")

# Authenticate with Angel One
smart_api = SmartConnect(api_key)
session = smart_api.generateSession(client_code, password, totp_code)

# Check if login succeeded
if session and session.get('status'):
    print("✅ Logged in successfully.")
    refresh_token = session['data']['refreshToken']
    feed_token = smart_api.getfeedToken()
    print(f"📦 Feed Token: {feed_token}")
else:
    print("❌ Login failed:", session)

# ⚠️ Removed broken code block below — no `getMaster()` or instruments loop used
# Your script ends here for now, login is working successfully

