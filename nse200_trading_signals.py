import yfinance as yf
import pandas as pd
import requests

# === Telegram Bot Details ===
BOT_TOKEN = "7990352679:AAEAyI09OsaLTypUBXpHdf3p68Ic2QzRak0"
CHAT_ID = "5795808600"

# === Send Telegram Message ===
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

# === Bollinger Bands Calculation ===
def bollinger_bands(df, n=20):
    df['MA20'] = df['Close'].rolling(n).mean()
    df['STD20'] = df['Close'].rolling(n).std()
    df['Upper'] = df['MA20'] + 2 * df['STD20']
    df['Lower'] = df['MA20'] - 2 * df['STD20']
    return df

# === Signal Generator: BUY/SELL with LTP ===
def signal_generator(df):
    try:
        if df.empty or len(df) < 20:
            return None, None

        last_row = df.iloc[[-1]]
        last_close = last_row['Close'].item()
        last_upper = last_row['Upper'].item()
        last_lower = last_row['Lower'].item()

        if pd.isna(last_close) or pd.isna(last_upper) or pd.isna(last_lower):
            return None, None

        if last_close > last_upper:
            return 'SELL', last_close
        elif last_close < last_lower:
            return 'BUY', last_close
        else:
            return None, None
    except Exception as e:
        return None, None

# === Load NSE 200 symbols ===
df_symbols = pd.read_csv("nse_200.csv")
df_symbols.columns = df_symbols.columns.str.strip()

# Adjust column name based on your CSV header (usually SYMBOL or SYMBOL \n)
symbol_column = [col for col in df_symbols.columns if "symbol" in col.lower()][0]
nse_200 = df_symbols[symbol_column].astype(str).str.strip()
nse_200 = nse_200[nse_200.str.match(r'^[A-Z]+$')] + ".NS"
nse_200 = nse_200.tolist()

# === Main Loop ===
for symbol in nse_200:
    try:
        data = yf.download(symbol, period="60d", interval="1d", auto_adjust=False)
        if data.empty or data.shape[0] < 20:
            continue

        data = bollinger_bands(data)
        signal, ltp = signal_generator(data)

        if signal:  # Only if BUY or SELL
            message = f"{symbol}: {signal} @ ₹{ltp:.2f}"
            print(message)
            send_telegram_message(message)

    except Exception as e:
        print(f"{symbol}: Error - {e}")
