import json
import time
import pyotp
import requests
from SmartApi import SmartConnect

# Your Angel One credentials
API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

# Your Telegram bot info
TELEGRAM_BOT_TOKEN = "7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0"
TELEGRAM_CHAT_ID = "5795808600"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        resp = requests.post(url, data=data)
        if resp.status_code == 200:
            print("Telegram message sent.")
        else:
            print(f"Telegram error: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Telegram send error: {e}")

def login_and_get_session():
    obj = SmartConnect(api_key=API_KEY)
    totp = pyotp.TOTP(TOTP_SECRET).now()
    print(f"Generated TOTP: {totp}")
    data = obj.generateSession(CLIENT_CODE, PASSWORD, totp)
    print("Logged in successfully!")
    return obj

def get_token(obj, symbol):
    try:
        result = obj.searchScrip("NSE", symbol)
        time.sleep(2)  # avoid rate limit
        if isinstance(result, str):
            result = json.loads(result)
        data_list = None
        if isinstance(result, dict):
            if 'data' in result:
                data_list = result['data']
            else:
                data_list = result
        elif isinstance(result, list):
            data_list = result

        if data_list:
            for item in data_list:
                if (item.get('tradingsymbol') == symbol or item.get('tradingsymbol') == f"{symbol}-EQ") and item.get('exchange') == 'NSE':
                    return item.get('symboltoken')
        print(f"Token not found for {symbol}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON for symbol {symbol}: {result}")
    except Exception as e:
        print(f"Error fetching token for {symbol}: {e}")
    return None

def fetch_ltp(obj, symbol, token):
    try:
        # ltpData requires exchange, tradingsymbol, symboltoken
        data = obj.ltpData("NSE", symbol, token)
        ltp = None
        if 'data' in data and 'ltp' in data['data']:
            ltp = data['data']['ltp']
        return ltp
    except Exception as e:
        print(f"Error fetching LTP for {symbol}: {e}")
        return None

def main():
    print("Starting script...")
    obj = login_and_get_session()

    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK"]

    for sym in symbols:
        print(f"Fetching token for {sym}")
        token = get_token(obj, sym)
        print(f"Token for {sym}: {token}")
        if token:
            print(f"Fetching LTP for {sym}")
            ltp = fetch_ltp(obj, sym, token)
            print(f"LTP for {sym}: {ltp}")
            if ltp:
                send_telegram_message(f"LTP of {sym} is ₹{ltp}")
            else:
                print(f"Could not fetch LTP for {sym}")
        else:
            print(f"Skipping LTP for {sym} due to missing token.")

    print("Script finished.")

if __name__ == "__main__":
    main()
