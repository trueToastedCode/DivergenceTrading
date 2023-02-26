import pandas as pd
import numpy as np

from ....signal import *


def add_total_signal(df, new_data_int_idx, new_data_dt_idx,
                     long_smma_confirmation_min_rsi,
                     long_conflict_smma_confirmation_max_rsi,
                     long_stop_rsi,
                     long_conflict_stop_rsi):
    if new_data_int_idx == -1:
        df['TotalSignal'] = np.nan
        return

    bull_div_rows = df[(df.index >= new_data_dt_idx) & (pd.notnull(df.BullDiv))]

    for i in range(len(bull_div_rows)):
        row = bull_div_rows.iloc[i]
        # if rsi above x, 2 more confirmations:
        # - smma's have to line up above each other
        # - open of current candle has to be above the smma3
        if row.RSI >= long_smma_confirmation_min_rsi \
                and (row.Low <= row.SMMA3
                     or row.SMMA2 <= row.SMMA3
                     or row.SMMA1 <= row.SMMA2
                     or row.Open <= row.SMMA3):
            # conditions don't match
            continue
        if row.RSI >= long_stop_rsi:
            # conditions don't match
            continue
        df.loc[row.name, 'TotalSignal'] = LONG_SIGNAL

    another_bear_div_rows = df[(df.index >= new_data_dt_idx) & (pd.notnull(df.AnotherBearDiv))]

    for i in range(len(another_bear_div_rows)):
        row = another_bear_div_rows.iloc[i]
        # if rsi below x, 2 more confirmations:
        # - smma's have to line up under each other
        # - open of current candle has to be below the smma3
        if row.RSI <= long_conflict_smma_confirmation_max_rsi \
                and (row.Low >= row.SMMA3
                     or row.SMMA2 >= row.SMMA3
                     or row.SMMA1 >= row.SMMA2
                     or row.Open >= row.SMMA3):
            # conditions don't match
            continue
        if row.RSI <= long_conflict_stop_rsi:
            # conditions don't match
            continue
        df.loc[row.name, 'TotalSignal'] = np.nan
