import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

import pyotp
from SmartApi.smartConnect import SmartConnect

print("🚀 Generating TOTP...")
totp = pyotp.TOTP(TOTP_SECRET).now()

print("🔐 Logging in...")
obj = SmartConnect(api_key=API_KEY)
data = obj.generateSession(CLIENT_CODE, PASSWORD, totp)

if data['status'] and 'data' in data:
    print("✅ Login successful.")
    print("📥 Downloading ScripMaster...")

    scripmaster_url = f"https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    response = requests.get(scripmaster_url)

    if response.status_code == 200:
        with open("ScripMaster.json", "wb") as f:
            f.write(response.content)
        print("✅ ScripMaster.json saved.")
    else:
        print("❌ Failed to download ScripMaster.json. Status:", response.status_code)
else:
    print("❌ Login failed:", data)
