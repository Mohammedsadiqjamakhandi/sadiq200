import pyotp
import time

TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"
totp = pyotp.TOTP(TOTP_SECRET)

for i in range(30):
    print("⏳ TOTP Now:", totp.now())
    time.sleep(1)
