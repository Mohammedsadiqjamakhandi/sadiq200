import requests
import pyotp
import json

API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "YOUR_NEW_SECRET_FROM_TOTP_SITE"

totp = pyotp.TOTP("6VDXFQ23A54VT6AISO6XKYX5NE").now()
print("🔐 TOTP:", totp)

url = "https://apiconnect.angelone.in/rest/auth/angelbroking/user/v1/loginByPassword"

payload = {
    "clientcode": CLIENT_CODE,
    "password": PASSWORD,
    "totp": totp
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print("🔍 Raw response:")
print(json.dumps(response.json(), indent=2))
