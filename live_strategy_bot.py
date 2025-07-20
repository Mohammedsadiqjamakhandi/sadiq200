# live_strategy_bot.py

from smartapi.websocket import WebSocket
from smartapi.smartConnect import SmartConnect
import pandas as pd, numpy as np, datetime, time, threading, requests

# ---- SETUP ----
TELEGRAM_BOT_TOKEN = "7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0"
TELEGRAM_CHAT_ID = "5795808600"
API_KEY = "your_api_key"
CLIENT_CODE = "your_client_code"
PASSWORD = "your_password"
TOTP = "your_totp"

# ---- CANDLE STORAGE ----
symbol_tokens = pd.read_csv("smartapi_nse_master.csv")  # Must contain 'symbol' and 'token' columns
symbols_to_track = symbol_tokens[symbol_tokens['series'] == 'EQ'].head(50)  # Modify as needed
live_candles = {}

# ---- STRATEGY FUNCTION ----
def check_bollinger_signal(symbol, df):
    if len(df) < 20:
        return None

    df['MA'] = df['close'].rolling(20).mean()
    df['STD'] = df['close'].rolling(20).std()
    df['Upper'] = df['MA'] + (2 * df['STD'])
    df['Lower'] = df['MA'] - (2 * df['STD'])

    last_3 = df.iloc[-3:]
    bb_mid = df['MA'].iloc[-1]

    if (
        last_3.iloc[0]['low'] <= last_3.iloc[0]['Lower'] and
        all(last_3.iloc[i]['low'] > last_3.iloc[i-1]['low'] and last_3.iloc[i]['high'] > last_3.iloc[i-1]['high'] for i in [1, 2]) and
        all(last_3.iloc[i]['close'] < bb_mid for i in range(3)) and
        all(not (last_3.iloc[i]['open'] > last_3.iloc[i-1]['close'] and last_3.iloc[i]['close'] < last_3.iloc[i-1]['open']) for i in [1, 2])
    ):
        return "BUY"

    elif (
        last_3.iloc[0]['high'] >= last_3.iloc[0]['Upper'] and
        all(last_3.iloc[i]['low'] < last_3.iloc[i-1]['low'] and last_3.iloc[i]['high'] < last_3.iloc[i-1]['high'] for i in [1, 2]) and
        all(last_3.iloc[i]['close'] > bb_mid for i in range(3)) and
        all(not (last_3.iloc[i]['open'] < last_3.iloc[i-1]['close'] and last_3.iloc[i]['close'] > last_3.iloc[i-1]['open']) for i in [1, 2])
    ):
        return "SELL"

    return None

# ---- TELEGRAM ----
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    try:
        requests.post(url, data=payload)
    except:
        print("❌ Failed to send Telegram alert.")

# ---- HANDLE LIVE LTP ----
def update_candle(symbol, ltp):
    now = datetime.datetime.now()
    minute = now.replace(second=0, microsecond=0)

    if symbol not in live_candles:
        live_candles[symbol] = []

    if not live_candles[symbol] or live_candles[symbol][-1]['minute'] != minute:
        # Start new candle
        live_candles[symbol].append({'minute': minute, 'open': ltp, 'high': ltp, 'low': ltp, 'close': ltp})
    else:
        # Update current candle
        candle = live_candles[symbol][-1]
        candle['high'] = max(candle['high'], ltp)
        candle['low'] = min(candle['low'], ltp)
        candle['close'] = ltp

    if len(live_candles[symbol]) > 100:
        live_candles[symbol] = live_candles[symbol][-100:]

# ---- CHECK SIGNALS PERIODICALLY ----
def signal_checker():
    while True:
        for symbol in live_candles:
            df = pd.DataFrame(live_candles[symbol])
            if len(df) >= 20:
                signal = check_bollinger_signal(symbol, df)
                if signal:
                    msg = f"📢 {signal} Signal on {symbol} at {datetime.datetime.now().strftime('%H:%M:%S')}"
                    print(msg)
                    send_telegram(msg)
        time.sleep(30)

# ---- LOGIN AND WS START ----
def start_live_feed():
    smartapi = SmartConnect(api_key=API_KEY)
    data = smartapi.generateSession(client_code=CLIENT_CODE, password=PASSWORD, totp=TOTP)
    auth_token = data['data']['jwtToken']
    feed_token = smartapi.getfeedToken()

    ws = WebSocket(api_key=API_KEY, client_code=CLIENT_CODE, jwt_token=auth_token, feed_token=feed_token)

    def on_tick(ws, tick_data):
        token = str(tick_data['tk'])
        symbol_row = symbols_to_track[symbols_to_track['token'] == int(token)]
        if not symbol_row.empty:
            symbol = symbol_row.iloc[0]['symbol']
            ltp = tick_data['lp']
            update_candle(symbol, ltp)

    def on_open(ws):
        print("✅ WebSocket connected.")
        token_list = [{"token": str(row['token']), "action": 1, "segment": "nse_cm"} for _, row in symbols_to_track.iterrows()]
        ws.subscribe(token_list)

    ws.on_ticks = on_tick
    ws.on_connect = on_open
    ws.on_close = lambda ws: print("❌ WebSocket disconnected.")

    threading.Thread(target=signal_checker, daemon=True).start()
    ws.connect()

# ---- RUN ----
if __name__ == "__main__":
    start_live_feed()
