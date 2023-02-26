import time
import logging

from .technical_indicators import *
from .custom_indicators.smma import *
from .custom_indicators.edge_pivot import add_rsi_edge_pivots_low
from .custom_indicators.divergences import add_divergences
from .custom_indicators.total_signal import add_total_signal


class CacheProcessing:
    def __init__(self,
                 atr_idx,
                 rsi_len,
                 smmas,
                 rsi_edge_pivot_n,
                 div_max_backpivots,
                 div_backcandles_min,
                 div_backcandles_max,
                 timeframe,
                 total_long_smma_confirmation_min_rsi,
                 total_long_conflict_smma_confirmation_max_rsi,
                 total_long_stop_rsi,
                 total_long_conflict_stop_rsi):
        self.atr_idx = atr_idx
        self.rsi_len = rsi_len
        self.smmas = smmas
        self.rsi_edge_pivot_n = rsi_edge_pivot_n
        self.div_max_backpivots = div_max_backpivots
        self.div_backcandles_min = div_backcandles_min
        self.div_backcandles_max = div_backcandles_max
        self.timeframe = timeframe
        self.total_long_smma_confirmation_min_rsi = total_long_smma_confirmation_min_rsi
        self.total_long_conflict_smma_confirmation_max_rsi = total_long_conflict_smma_confirmation_max_rsi
        self.total_long_stop_rsi = total_long_stop_rsi
        self.total_long_conflict_stop_rsi = total_long_conflict_stop_rsi

    def process_cache(self, df, new_data_int_idx=-1):
        time_before = time.perf_counter()

        new_data_dt_idx = None if new_data_int_idx == -1 else df.index[new_data_int_idx]

        default_args = dict(df=df, new_data_int_idx=new_data_int_idx, new_data_dt_idx=new_data_dt_idx)

        add_atr(df=df, atr_idx=self.atr_idx)

        add_rsi(**default_args, rsi_len=self.rsi_len)

        for source, length, target in self.smmas:
            add_smma(**default_args, source=source, length=length, target=target)

        add_rsi_edge_pivots_low(df=df, new_data_int_idx=new_data_int_idx, n=self.rsi_edge_pivot_n)

        add_divergences(**default_args, max_backpivots=self.div_max_backpivots,
                        backcandles_min=self.div_backcandles_min, backcandles_max=self.div_backcandles_max,
                        timeframe=self.timeframe)

        add_total_signal(**default_args,
                         long_smma_confirmation_min_rsi=self.total_long_smma_confirmation_min_rsi,
                         long_conflict_smma_confirmation_max_rsi=self.total_long_conflict_smma_confirmation_max_rsi,
                         long_stop_rsi=self.total_long_stop_rsi,
                         long_conflict_stop_rsi=self.total_long_conflict_stop_rsi)

        elapsed = time.perf_counter() - time_before
        logging.debug(f'Processed cache in {round(elapsed, 2)}s')
