import pyotp
from SmartApi.smartConnect import SmartConnect

# Config
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

def generate_totp(secret):
    return pyotp.TOTP(secret).now()

print("🚀 Logging in...")

sdk = SmartConnect(api_key=API_KEY)

try:
    otp = generate_totp(TOTP_SECRET)
    print("Generated OTP:", otp)

    resp = sdk.generate_session(CLIENT_CODE, PASSWORD, otp)
    print("Raw response from generate_session():", resp)

    if isinstance(resp, dict) and "data" in resp:
        session = resp
        print("✅ Login successful!")
        print("Session data:", session)
        # Now you can get profile or other info
        profile = sdk.get_profile()
        print("User profile:", profile)
    else:
        print("❌ Login failed or unexpected response:")
        print(resp)
        exit()

except Exception as e:
    print("❌ Exception during login:", e)
