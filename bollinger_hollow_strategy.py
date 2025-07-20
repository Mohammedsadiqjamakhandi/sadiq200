def check_bollinger_signal(symbol, candles, bbands):
    if len(candles) < 3:
        return None  # Not enough candles

    c1, c2, c3 = candles[-3], candles[-2], candles[-1]

    def is_hollow(c): return c['close'] > c['open']
    def is_filled(c): return c['close'] < c['open']
    def has_body(c):
        return abs(c['close'] - c['open']) >= 0.3 * (c['high'] - c['low'])

    def not_engulfing(prev, curr):
        return not (curr['open'] < prev['close'] and curr['close'] > prev['open'])

    def touches_band(c, band):
        return c['low'] <= band <= c['high']

    def touches_middle(c, mid):
        return c['low'] <= mid <= c['high'] or c['close'] >= mid if is_hollow(c) else c['close'] <= mid

    entry = round(c3['close'], 2)
    stop_loss = round(entry * 0.99, 2)
    target = round(entry * 1.01, 2)

    mid = bbands['middle']
    upper = bbands['upper']
    lower = bbands['lower']

    # === BUY CHECK ===
    if (
        is_hollow(c1) and touches_band(c1, lower) and has_body(c1) and
        is_hollow(c2) and has_body(c2) and
        is_hollow(c3) and has_body(c3) and
        not_engulfing(c1, c2) and not_engulfing(c2, c3) and
        not touches_middle(c1, mid) and
        not touches_middle(c2, mid) and
        not touches_middle(c3, mid) and
        c2['high'] > c1['high'] and c2['low'] > c1['low'] and
        c3['high'] > c2['high'] and c3['low'] > c2['low']
    ):
        return {
            'symbol': symbol,
            'signal': 'BUY',
            'entry': entry,
            'sl': stop_loss,
            'target': target,
            'time': c3['time']
        }

    # === SELL CHECK ===
    if (
        is_filled(c1) and touches_band(c1, upper) and has_body(c1) and
        is_filled(c2) and has_body(c2) and
        is_filled(c3) and has_body(c3) and
        not_engulfing(c1, c2) and not_engulfing(c2, c3) and
        not touches_middle(c1, mid) and
        not touches_middle(c2, mid) and
        not touches_middle(c3, mid) and
        c2['high'] < c1['high'] and c2['low'] < c1['low'] and
        c3['high'] < c2['high'] and c3['low'] < c2['low']
    ):
        return {
            'symbol': symbol,
            'signal': 'SELL',
            'entry': entry,
            'sl': round(entry * 1.01, 2),
            'target': round(entry * 0.99, 2),
            'time': c3['time']
        }

    return None
