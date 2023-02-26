import numpy as np


def is_edge_rsi_pivot_low(df, i, n):
    if i < n:
        # n values before index don't exist
        return False
    # True if n values are higher than value at current index
    return df.RSI.iloc[i-n:i+1].idxmin() == df.index[i]


def add_rsi_edge_pivots_low(df, new_data_int_idx, n):
    if new_data_int_idx == -1:
        start = n
        df['RSIPivotLow'] = np.nan
    else:
        start = new_data_int_idx
    for i in range(start, len(df)):
        if not is_edge_rsi_pivot_low(df, i, n):
            continue
        df.loc[df.index[i], 'RSIPivotLow'] = df.RSI[i]
