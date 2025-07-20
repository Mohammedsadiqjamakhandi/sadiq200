import pandas as pd
import mplfinance as mpf

# Load the full candles.csv
df = pd.read_csv("candles.csv", parse_dates=["date"])

# Select one stock, e.g., RELIANCE
symbol = "RELIANCE"
df_stock = df[df["symbol"] == symbol].copy()

# Set date as index for mplfinance
df_stock.set_index("date", inplace=True)

# Rename columns as required
df_stock.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"}, inplace=True)

# Calculate Bollinger Bands
df_stock['MA20'] = df_stock['Close'].rolling(window=20).mean()
df_stock['Upper'] = df_stock['MA20'] + 2 * df_stock['Close'].rolling(window=20).std()
df_stock['Lower'] = df_stock['MA20'] - 2 * df_stock['Close'].rolling(window=20).std()

# Plot hollow candlestick chart with Bollinger Bands
mpf.plot(
    df_stock,
    type='candle',
    style='yahoo',
    title=f"{symbol} Hollow Candles with Bollinger Bands",
    ylabel='Price',
    volume=True,
    mav=(20),
    addplot=[
        mpf.make_addplot(df_stock['Upper'], color='blue'),
        mpf.make_addplot(df_stock['Lower'], color='red')
    ],
    show_nontrading=False
)
