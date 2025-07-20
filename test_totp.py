import pyotp

TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"
otp = pyotp.TOTP(TOTP_SECRET).now()
print("🔐 Current TOTP:", otp)
