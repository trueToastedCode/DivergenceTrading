import pandas as pd
import numpy as np

from ..candles_since import candles_since


class Div:
    SRC_PIVOT = None
    SRC_OSC = 'RSI'
    SRC_PRICE = None

    @staticmethod
    def is_div(osc_before, osc_now, price_before, price_now):
        raise NotImplemented


class BullDiv(Div):
    SRC_PIVOT = 'RSIPivotLow'
    SRC_PRICE = 'Low'

    @staticmethod
    def is_div(osc_before, osc_now, price_before, price_now):
        # Osc: Higher Low
        # Price: Lower Low
        return osc_now > osc_before and price_now < price_before


class AnotherBearDiv(Div):
    SRC_PIVOT = 'RSIPivotLow'
    SRC_PRICE = 'High'

    @staticmethod
    def is_div(osc_before, osc_now, price_before, price_now):
        # Osc: Lower Low
        # Price: Higher High
        return osc_now < osc_before and price_now > price_before


def get_div_to_latest_pivot(pivot_rows, div, max_backpivots, backcandles_min, backcandles_max, timeframe):
    """
    @param pivot_rows: Rows containing the pivots
    @param div: Implementation of Div (Divergence)
    @param max_backpivots: Allowed distance of pivots starting after min candles
    @param backcandles_min: Minimum Candles between past and current
    @param backcandles_max: Maximum Candles between past and current
    """
    if len(pivot_rows) < 2:
        return
    i = len(pivot_rows) - 1
    row_now = pivot_rows.iloc[i]

    k = None

    for j in range(i - 1, -1, -1):
        row_before = pivot_rows.iloc[j]
        candle_count = candles_since(row_before.name, row_now.name, timeframe)
        if candle_count < backcandles_min:
            continue
        # first pivot that matches min backcandles
        k = j
        break

    if k is None:
        return

    for j in range(k,
                   -1 if max_backpivots is None else max(k - max_backpivots - 1, -1),
                   -1):
        row_before = pivot_rows.iloc[j]
        candle_count = candles_since(row_before.name, row_now.name, timeframe)
        if candle_count > backcandles_max:
            break
        if div.is_div(
                row_before[div.SRC_OSC], row_now[div.SRC_OSC],
                row_before[div.SRC_PRICE], row_now[div.SRC_PRICE]):
            return row_before.name, row_now.name


def add_divergences(df, new_data_int_idx, new_data_dt_idx, max_backpivots, backcandles_min,
                    backcandles_max, timeframe):
    if new_data_int_idx == -1:
        df['BullDiv'] = np.nan
        df['AnotherBearDiv'] = np.nan
        return

    rsi_pivot_low_rows = df[pd.notnull(df.RSIPivotLow)]
    if rsi_pivot_low_rows.empty:
        return

    new_rsi_pivot_low_rows = rsi_pivot_low_rows.iloc[
        rsi_pivot_low_rows.index >= new_data_dt_idx]

    for i in range(len(new_rsi_pivot_low_rows)):
        now = new_rsi_pivot_low_rows.index[i]

        _rsi_pivot_low_rows = rsi_pivot_low_rows[
            rsi_pivot_low_rows.index <= now]

        bull_div = get_div_to_latest_pivot(
            _rsi_pivot_low_rows, BullDiv, max_backpivots, backcandles_min, backcandles_max, timeframe)
        if bull_div is not None:
            df.loc[now, 'BullDiv'] = bull_div[0]

        another_bear_div = get_div_to_latest_pivot(
            _rsi_pivot_low_rows, AnotherBearDiv, max_backpivots, backcandles_min, backcandles_max, timeframe)
        if another_bear_div is not None:
            df.loc[now, 'AnotherBearDiv'] = another_bear_div[0]
