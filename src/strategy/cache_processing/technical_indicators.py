import pandas_ta as ta


def add_atr(df, atr_idx):
    df['ATR'] = ta.atr(df.High, df.Low, df.Close, index=atr_idx)


def add_rsi(df, new_data_int_idx, new_data_dt_idx, rsi_len):
    if new_data_int_idx == -1:
        df['RSI'] = ta.rsi(df.Close, length=rsi_len)
    else:
        _df = df.iloc[new_data_int_idx - rsi_len:new_data_int_idx + 1]
        df.loc[df.index >= new_data_dt_idx, 'RSI'] = ta.rsi(
            _df.Close, length=rsi_len)
