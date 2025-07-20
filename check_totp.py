import pyotp

TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"  # replace with yours
print("✅ Current TOTP:", pyotp.TOTP(TOTP_SECRET).now())
