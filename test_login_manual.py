from SmartApi.smartConnect import SmartConnect

# === Angel One credentials ===
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP = "922650"  # 👈 Paste the fresh TOTP here

# === Login attempt ===
obj = SmartConnect(api_key=API_KEY)
try:
    response = obj.generate_session(CLIENT_CODE, PASSWORD, TOTP)
    print("✅ Login response:")
    print(response)
except Exception as e:
    print("❌ Login failed:", e)
