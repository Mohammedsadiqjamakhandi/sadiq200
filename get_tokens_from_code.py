from SmartApi.smartConnect import SmartConnectV2

API_KEY = "Shcr9brZ"  # ✅ Replace with your actual API Key
SESSION_TOKEN_CODE = "paste_the_code_you_got_from_URL_here"

# Create object
obj = SmartConnectV2(api_key=API_KEY)

# Generate Session
data = obj.generateSessionBySessionToken(session_token=SESSION_TOKEN_CODE)

# Print tokens
print("Access Token:", data['data']['jwtToken'])
print("Feed Token:", data['data']['feedToken'])
