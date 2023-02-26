import logging
from periodic_simpletime import get_previous_periodic_dt

from ..trading_cache import TradingCache


async def make_trading_cache(period, klines_client, time_delta, cache_size, cache_processing):
    last_dt = get_previous_periodic_dt(period)
    start_dt = last_dt - time_delta
    logging.debug(f'Making klines cache with interval {period}, oldest data may start at {start_dt}')
    df = await klines_client.fetch_klines_with_next_periodic_dt(
        last_dt, start_dt.strftime('%d %b, %Y'))
    trading_cache = TradingCache(df, cache_size)
    if not trading_cache.is_full():
        raise ValueError(f'Cache has {len(trading_cache.df)} rows, expected {cache_size}.')
    df = trading_cache.df
    cache_processing.process_cache(df)
    return trading_cache
