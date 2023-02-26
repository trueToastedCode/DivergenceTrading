def candles_since(a, b, timeframe):
    count = abs((b - a) / timeframe)
    assert count % 1 == 0
    return int(count)
