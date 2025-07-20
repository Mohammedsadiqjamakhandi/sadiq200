from dotenv import load_dotenv
import os

load_dotenv()

print("ANGEL_API_KEY =", os.getenv("ANGEL_API_KEY"))
print("ANGEL_CLIENT_CODE =", os.getenv("ANGEL_CLIENT_CODE"))
print("ANGEL_PASSWORD =", os.getenv("ANGEL_PASSWORD"))
print("TOTP_SECRET =", os.getenv("TOTP_SECRET"))
