import pyotp
import requests
import json

# === Login details ===
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

def generate_totp():
    return pyotp.TOTP(TOTP_SECRET).now()

print("🚀 Logging in...")
totp = generate_totp()
print("🔐 TOTP:", totp)

url = "https://apiconnect.angelone.in/rest/auth/angelbroking/user/v1/loginByPassword"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

payload = {
    "clientcode": CLIENT_CODE,
    "password": PASSWORD,
    "totp": totp
}

try:
    res = requests.post(url, headers=headers, json=payload)
    res_json = res.json()
    print("🧾 Raw Response:")
    print(json.dumps(res_json, indent=2))

    if res_json.get("status") == True:
        jwt_token = res_json["data"]["jwtToken"]
        refresh_token = res_json["data"]["refreshToken"]
        feed_token = res_json["data"]["feedToken"]

        print("✅ Login successful.")
        print("🔐 JWT Token:", jwt_token[:60] + "...")
        print("🔄 Refresh Token:", refresh_token[:60] + "...")
        print("📡 Feed Token:", feed_token[:60] + "...")
    else:
        print("❌ Login failed:", res_json)

except Exception as e:
    print("❌ Exception during login:", e)
