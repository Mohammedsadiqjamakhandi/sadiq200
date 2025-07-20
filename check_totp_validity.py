import pyotp
import time
from datetime import datetime

TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"
totp = pyotp.TOTP(TOTP_SECRET)

print(f"📅 System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"🔐 Current TOTP: {totp.now()}")
print(f"⏱ Time Left Until Next OTP: {30 - (int(time.time()) % 30)} seconds")
