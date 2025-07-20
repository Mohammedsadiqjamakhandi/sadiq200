# smartapi_connection.py

import os
from dotenv import load_dotenv
from SmartApi.smartConnect import SmartConnect
import pyotp

# 🔐 Load environment variables from .env
load_dotenv()

API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
PIN = os.getenv("ANGEL_PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")  # Base32

def get_smart_api():
    # Create SmartConnect object
    obj = SmartConnect(api_key=API_KEY)

    # Generate TOTP
    totp = pyotp.TOTP(TOTP_SECRET).now()

    # Generate session
    data = obj.generateSession(CLIENT_CODE, PIN, totp)

    # Get feed token
    feed_token = obj.getfeedToken()

    # JWT is needed for WebSocket V2
    jwt_token = data['data']['jwtToken']
    
    return obj, feed_token, jwt_token

# 🧪 For testing login directly
if __name__ == "__main__":
    obj, feed_token, jwt_token = get_smart_api()
    print("✅ Login successful")
    print("Feed Token:", feed_token)
    print("JWT Token:", jwt_token)
