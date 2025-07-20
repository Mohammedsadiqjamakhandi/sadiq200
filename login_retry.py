import time
import pyotp
from requests.exceptions import ReadTimeout
from SmartApi import SmartConnect

CLIENT_ID = "Shcr9brZ"
USERNAME = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

def get_totp_token(secret):
    totp = pyotp.TOTP(secret)
    return totp.now()

def login_and_get_session():
    obj = SmartConnect(api_key=CLIENT_ID)
    totp_token = get_totp_token(TOTP_SECRET)

    for attempt in range(5):  # 5 attempts
        try:
            print(f"Login attempt {attempt + 1}...")
            data = obj.generateSession(USERNAME, PASSWORD, totp_token)
            print("✅ Logged in successfully!")
            return obj
        except ReadTimeout:
            print("⏳ Timeout occurred, retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"❌ Login failed with error: {e}")
            break
    raise Exception("Failed to login after multiple attempts.")

if __name__ == "__main__":
    session_obj = login_and_get_session()
