import asyncio
import logging
import time
import pandas as pd
from datetime import datetime
from binance import AsyncClient


# based on: https://binance-docs.github.io/apidocs/spot/en/#compressed-aggregate-trades-list
def parse_klines(klines):
    data = map(
        lambda kline: (
             float(kline[1]),
             float(kline[2]),
             float(kline[3]),
             float(kline[4]),
             float(kline[5]),
             datetime.utcfromtimestamp(kline[0] / 1000)
        ), klines)
    df = pd.DataFrame(data, columns=['Open', 'High', 'Low', 'Close', 'Volume', 'Datetime'])
    df.set_index('Datetime', inplace=True)
    return df


class KlinesClient:
    @classmethod
    async def create(cls, symbol: str, interval: str):
        self = KlinesClient()
        self.symbol = symbol
        self.interval = interval
        self.client = await AsyncClient.create()
        return self

    async def close_connection(self):
        await self.client.close_connection()

    async def fetch_klines_with_next_periodic_dt(self, next_periodic_dt: datetime, start: str = '1 day ago UTC',
                                                 timeout_s: int = 40):
        logging.debug(f'Fetching Klines starting from {start} for {next_periodic_dt}')
        seconds = (next_periodic_dt - datetime.utcnow()).total_seconds()
        if seconds > 0:
            await asyncio.sleep(seconds)
        time_before = time.perf_counter()
        while time.perf_counter() - time_before < timeout_s:
            klines = await self.client.get_historical_klines(self.symbol, self.interval, start)
            for i in range(len(klines) - 1, -1, -1):
                dt = datetime.utcfromtimestamp(klines[i][0] / 1000)
                if dt == next_periodic_dt:
                    if i == 0:
                        # no data left
                        raise ValueError(f'Klines wont\'t contain next periodic dt {next_periodic_dt}')
                    df = parse_klines(klines[:i])
                    len_before = len(df)
                    df = df.dropna()
                    len_after = len(df)
                    if len_after != len_before:
                        logging.warning(f'Dropped {len_before - len_after} columns with missing data')
                    return df
        raise TimeoutError
