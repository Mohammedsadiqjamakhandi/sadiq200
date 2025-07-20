from dotenv import load_dotenv
import os

load_dotenv()

print("✅ Loaded environment variables:")
print("API KEY:", os.getenv("ANGEL_API_KEY"))
print("CLIENT CODE:", os.getenv("ANGEL_CLIENT_CODE"))
print("PASSWORD:", os.getenv("ANGEL_PASSWORD"))
print("TOTP SECRET:", os.getenv("TOTP_SECRET"))
