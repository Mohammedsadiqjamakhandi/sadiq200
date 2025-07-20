# save as: download_infy_yesterday.py
from smartapi import SmartConnect
import pandas as pd
from datetime import datetime, timedelta

API_KEY = "Shcr9brZ"
CLIENT_CODE = "ASIFA1491"
PASSWORD = "9986"
TOTP_SECRET = "6VDXFQ23A54VT6AISO6XKYX5NE"

smartapi = SmartConnect(api_key=API_KEY)
session = smartapi.generateSession(CLIENT_CODE, PASSWORD, TOTP_SECRET)

symbol = "INFY-EQ"
exchange = "NSE"
token = "1594"
interval = "ONE_MINUTE"

end = datetime.now().replace(hour=15, minute=30, second=0, microsecond=0)
start = end - timedelta(days=1)

start_str = start.strftime("%Y-%m-%d %H:%M")
end_str = end.strftime("%Y-%m-%d %H:%M")

data = smartapi.getCandleData(
    interval=interval,
    exchange=symbol.split("-")[1],
    symboltoken=token,
    symbolname=symbol.split("-")[0],
    fromdate=start_str,
    todate=end_str
)

candles = data['data']

df = pd.DataFrame(candles, columns=["time", "open", "high", "low", "close", "volume"])
df.to_csv("candles/INFY.csv", index=False)
print("✅ Saved candles/INFY.csv")
