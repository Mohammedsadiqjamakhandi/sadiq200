import requests
import pyotp

API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

def generate_totp(secret):
    return pyotp.TOTP(secret).now()

otp = generate_totp(TOTP_SECRET)
print("Generated OTP:", otp)

url = "https://apiconnect.angelbroking.com/rest/secure/angelbroking/user/v1/generateSession"

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-API-KEY": API_KEY,
    "User-Agent": "Mozilla/5.0"
}

payload = {
    "userID": CLIENT_CODE,
    "password": PASSWORD,
    "twoFA": otp
}

session = requests.Session()

try:
    response = session.post(url, json=payload, headers=headers, timeout=10)
    print("HTTP status code:", response.status_code)
    print("Response headers:", response.headers)
    print("Response content:", repr(response.content))
    print("Response text:", response.text)
except Exception as e:
    print("Exception during request:", e)
