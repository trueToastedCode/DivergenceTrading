from datetime import timedelta
import os
from periodic_simpletime import PeriodicSimpleTime


TIMEFRAME        = timedelta(minutes=5)
KLINES_SYMBOL    = 'BTCUSDT'
KLINES_INTERVAL  = '5m'
PERIOD           = PeriodicSimpleTime(minute=5)
INIT_TIMEDELTA   = timedelta(days=3)
CACHE_SIZE       = 500
COOKIE_FILE      = 'papertrading.txt'
PAPER_SYMBOL     = 'BITSTAMP:BTCUSD'
MAX_ERROR_COUNT  = 3

ATR_LEN   = 14
RSI_LEN   = 14

SMMA1_SRC = 'Close'
SMMA1_LEN = 21
SMMA1_TAR = 'SMMA1'

SMMA2_SRC = 'Close'
SMMA2_LEN = 50
SMMA2_TAR = 'SMMA2'

SMMA3_SRC = 'Close'
SMMA3_LEN = 200
SMMA3_TAR = 'SMMA3'

RSI_EDGE_PIVOT_N = 5

DIV_MAX_BACKPIVOTS  = 4
DIV_BACKCANDLES_MIN = 5
DIV_BACKCANDLES_MAX = 55

TOTAL_LONG_SMMA_CONFIRMATION_MIN_RSI          = 70
TOTAL_LONG_CONFLICT_SMMA_CONFIRMATION_MAX_RSI = 30
TOTAL_LONG_STOP_RSI                           = 90
TOTAL_LONG_CONFLICT_STOP_RSI                  = 10

MIN_BALANCE = 150
AMOUNT_USE  = 0.99
SLAT_RATIO  = 1.2
TPSL_RATIO  = 2.71


class Args:
    @staticmethod
    def klines_cache():
        return dict(symbol=KLINES_SYMBOL, interval=KLINES_INTERVAL)

    @staticmethod
    def make_trading_cache(klines_client, cache_processing):
        return dict(period=PERIOD, klines_client=klines_client, time_delta=INIT_TIMEDELTA,
                    cache_size=CACHE_SIZE, cache_processing=cache_processing)

    @staticmethod
    def trading_cache_init():
        return dict(atr_len=ATR_LEN,
                    rsi_len=RSI_LEN,
                    smmas=[
                        (SMMA1_SRC, SMMA1_LEN, SMMA1_TAR),
                        (SMMA2_SRC, SMMA2_LEN, SMMA2_TAR),
                        (SMMA3_SRC, SMMA3_LEN, SMMA3_TAR)
                    ],
                    rsi_edge_pivot_n=RSI_EDGE_PIVOT_N,
                    timeframe=TIMEFRAME,
                    div_max_backpivots=DIV_MAX_BACKPIVOTS,
                    div_backcandles_min=DIV_BACKCANDLES_MIN,
                    div_backcandles_max=DIV_BACKCANDLES_MAX,
                    total_long_smma_confirmation_min_rsi=TOTAL_LONG_SMMA_CONFIRMATION_MIN_RSI,
                    total_long_conflict_smma_confirmation_max_rsi=TOTAL_LONG_CONFLICT_SMMA_CONFIRMATION_MAX_RSI,
                    total_long_stop_rsi=TOTAL_LONG_STOP_RSI,
                    total_long_conflict_stop_rsi=TOTAL_LONG_CONFLICT_STOP_RSI)

    @staticmethod
    def create_paper_trading_with_cookie_file():
        dir_path = os.path.dirname(os.path.realpath(__file__))
        cookie_path = os.sep.join([dir_path, 'cookies', COOKIE_FILE])
        return dict(cookie_path=cookie_path, default_symbol=PAPER_SYMBOL)
