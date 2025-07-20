import requests
import pyotp

API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

def generate_totp(secret):
    return pyotp.TOTP(secret).now()

otp = generate_totp(TOTP_SECRET)

url = "https://apiconnect.angelbroking.com/rest/secure/angelbroking/user/v1/loginByPassword"

headers = {
    "Content-Type": "application/json",
    "X-UserType": "USER",
    "X-SourceID": "WEB",
    "X-ClientLocalIP": "127.0.0.1",
    "X-ClientPublicIP": "127.0.0.1",
    "X-MACAddress": "00:00:00:00:00:00",
    "X-ApiKey": API_KEY,
}

payload = {
    "clientcode": CLIENT_CODE,
    "password": PASSWORD,
    "ip": "127.0.0.1",
    "otp": otp,
}

response = requests.post(url, json=payload, headers=headers)

print("Status code:", response.status_code)
print("Response text:", response.text)
