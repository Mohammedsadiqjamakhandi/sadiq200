import os
from SmartApi.smartConnect import SmartConnect
import pyotp
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

def generate_totp():
    return pyotp.TOTP(TOTP_SECRET).now()

print(f"🔐 TOTP: {generate_totp()}")
print("🚀 Logging in...")

obj = SmartConnect(api_key=API_KEY)

try:
    data = obj.generate_session(CLIENT_CODE, PASSWORD, generate_totp())
    print("✅ Login successful.")
except Exception as e:
    print(f"❌ Login failed: {e}")
