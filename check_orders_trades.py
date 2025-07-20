import os
from SmartApi.smartConnect import SmartConnect
from dotenv import load_dotenv
import pyotp

print("🚀 Script started")
load_dotenv()

API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD = os.getenv("ANGEL_PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

def login():
    print("🔐 Logging into Angel One...")
    obj = SmartConnect(api_key=API_KEY)

    # Generate TOTP
    totp = pyotp.TOTP(TOTP_SECRET).now()
    print("🔐 Generated TOTP:", totp)

    try:
        data = obj.generateSession(CLIENT_CODE, PASSWORD, totp)
        if data and data.get("status"):
            print("✅ Logged in successfully")
        else:
            print("❌ Login failed:", data)
            return None
    except Exception as e:
        print("❌ Exception during login:", e)
        return None

    return obj

def check_orders(obj):
    print("📄 Orders:")
    try:
        orders = obj.orderBook()
        if orders and isinstance(orders, list):
            for order in orders:
                print(order)
        else:
            print("ℹ️ No orders found.")
    except Exception as e:
        print("❌ Failed to fetch orders:", e)

def check_trades(obj):
    print("📈 Trades:")
    try:
        trades = obj.tradeBook()
        if trades and isinstance(trades, list):
            for trade in trades:
                print(trade)
        else:
            print("ℹ️ No trades found.")
    except Exception as e:
        print("❌ Failed to fetch trades:", e)

def main():
    obj = login()
    if obj:
        check_orders(obj)
        check_trades(obj)

if __name__ == "__main__":
    main()
