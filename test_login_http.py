import pyotp
import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# Generate TOTP
totp = pyotp.TOTP(TOTP_SECRET).now()
print(f"🔐 TOTP: {totp}")

# Prepare request
url = "https://apiconnect.angelbroking.com/rest/auth/angelbroking/user/v1/loginByPassword"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-UserType": "USER",
    "X-SourceID": "WEB",
    "X-ClientLocalIP": "127.0.0.1",
    "X-ClientPublicIP": "127.0.0.1",
    "X-MACAddress": "00:00:00:00:00:00",
    "X-PrivateKey": API_KEY
}
payload = {
    "clientcode": CLIENT_CODE,
    "password": PASSWORD,
    "totp": totp
}

# Make request
response = requests.post(url, json=payload, headers=headers)

try:
    data = response.json()
    print("🔍 Raw Response:", data)
    if data.get("status") == True:
        print("✅ Login Success")
        print("🔑 JWT Token:", data["data"]["jwtToken"])
    else:
        print("❌ Login Failed:", data.get("message", "Unknown error"))
except Exception as e:
    print("❌ Exception:", e)
