import pandas_ta as ta


def add_atr(df, atr_idx):
    df['ATR'] = ta.atr(df.High, df.Low, df.Close, index=atr_idx)
