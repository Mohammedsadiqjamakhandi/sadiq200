"""
Utility helpers for Bollinger‑Band strategy
Save this file as utils.py in the same directory
"""

from datetime import datetime
from statistics import mean, stdev


# ────────────────────────────────────────────────
# Bollinger‑Band calculator
# ────────────────────────────────────────────────
def calculate_bollinger_bands(candles, period: int = 20, multiplier: int = 2):
    """
    candles : list of dicts with at least a 'close' key
    Returns a dict with upper / middle / lower band levels
    """

    if len(candles) < period:
        # not enough data yet
        return None

    closes = [c['close'] for c in candles[-period:]]
    sma = mean(closes)
    std = stdev(closes)
    upper = sma + multiplier * std
    lower = sma - multiplier * std

    return {"upper": upper, "middle": sma, "lower": lower}


# ────────────────────────────────────────────────
# Minute‑candle builder (for live WebSocket ticks)
# ────────────────────────────────────────────────
def update_candle_data(symbol: str, ltp: float, candles_dict: dict):
    """
    Builds/updates 1‑minute OHLC candles from tick prices.

    candles_dict is a dict keyed by symbol, each value is a list of
    candle dicts: {'time','open','high','low','close'}
    """
    now = datetime.now()
    minute_stamp = now.replace(second=0, microsecond=0).strftime("%H:%M:%S")

    data = candles_dict.setdefault(symbol, [])

    if data and data[-1]["time"] == minute_stamp:
        # still within the same minute → update current candle
        candle = data[-1]
        candle["high"] = max(candle["high"], ltp)
        candle["low"]  = min(candle["low"], ltp)
        candle["close"] = ltp
    else:
        # new minute → start a fresh candle
        candle = {
            "time":   minute_stamp,
            "open":   ltp,
            "high":   ltp,
            "low":    ltp,
            "close":  ltp,
        }
        data.append(candle)

        # (optional) keep list from growing forever
        if len(data) > 1000:          # keep last ~17 h of 1‑min candles
            data.pop(0)
