import pyotp

totp = pyotp.TOTP("6VDXFQ23A54VT6AISO6XKYX5NE")
print("🔐 Your current TOTP is:", totp.now())
