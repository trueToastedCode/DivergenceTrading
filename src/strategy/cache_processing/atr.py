import numpy as np


def calc_tr(df, i):
    assert i > 0
    return max(
        df.High[i] - df.Low[i],
        abs(df.High[i] - df.Close[i-1]),
        abs(df.Low[i] - df.Close[i-1])
    )


def add_atr(df, new_data_int_idx, new_data_dt_idx, length):
    if new_data_int_idx == -1:
        result = [np.nan] * length
        atr = sum([calc_tr(df, i) for i in range(1, length + 1)]) / length
        result.append(atr)
        for i in range(length + 1, len(df)):
            atr = (atr * (length - 1) + calc_tr(df, i)) / length
            result.append(atr)
        df['ATR'] = result
    else:
        result = []
        atr = df.ATR[new_data_int_idx-1]
        for i in range(new_data_int_idx, len(df)):
            atr = (atr * (length - 1) + calc_tr(df, i)) / length
            result.append(atr)
        df.loc[df.index >= new_data_dt_idx, 'ATR'] = result
