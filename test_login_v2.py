import pyotp
from SmartApi.smartConnect import SmartConnect
from dotenv import load_dotenv
import os

# Load from .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# Generate OTP
totp = pyotp.TOTP(TOTP_SECRET).now()
print(f"🔐 TOTP: {totp}")
print("🚀 Logging in...")

# Login
obj = SmartConnect(api_key=API_KEY)
try:
    data = obj.generate_session(CLIENT_CODE, PASSWORD, totp)
    print("✅ Login Successful.")
    print("🔑 JWT Token:", data['data']['jwtToken'])
except Exception as e:
    print("❌ Login failed:", e)
