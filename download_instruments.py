import os
import pyotp
import requests
import pandas as pd
from SmartApi.smartConnect import SmartConnect
from dotenv import load_dotenv

# === Load credentials ===
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

# === Generate TOTP ===
totp = pyotp.TOTP(TOTP_SECRET).now()

# === Login to SmartAPI ===
obj = SmartConnect(api_key=API_KEY)
data = obj.generateSession(CLIENT_CODE, PASSWORD, totp)
refreshToken = data['data']['refreshToken']
userProfile = obj.getProfile(refreshToken)
print("✅ Logged in.")

# === Download instruments file ===
url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)
    df.to_csv("instruments.csv", index=False)
    print("📥 instruments.csv downloaded successfully.")
else:
    print("❌ Failed to download instrument file.")
