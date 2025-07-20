from SmartApi.smartConnect import SmartConnect
from dotenv import load_dotenv
import os
import pyotp
from logzero import logger

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

if not all([API_KEY, CLIENT_CODE, PASSWORD, TOTP_SECRET]):
    raise ValueError("Missing one or more credentials from .env file")

# Generate TOTP
totp = pyotp.TOTP(TOTP_SECRET).now()

# Login
logger.info("🚀 Logging into Angel One...")
obj = SmartConnect(api_key=API_KEY)

try:
    data = obj.generateSession(CLIENT_CODE, PASSWORD, totp)

    tokens = data['data']  # ✅ FIX: Access nested 'data' key

    logger.info("✅ Login successful.")
    logger.info(f"Feed Token: {tokens['feedToken']}")
    logger.info(f"JWT Token: {tokens['jwtToken']}")
    logger.info(f"Refresh Token: {tokens['refreshToken']}")

except Exception as e:
    # Avoid using emojis that may break console encoding
    logger.error(f"Login failed: {e}")
