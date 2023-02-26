import pandas as pd


class NoOverlapError(Exception):
    pass


class TradingCache:
    def __init__(self, df, max_size):
        self.max_size = max_size
        self.set_df(df)

    def set_df(self, df):
        if len(df) > self.max_size:
            self.df = df.iloc[-self.max_size:]
        else:
            self.df = df

    def concat(self, df):
        """
        :param df: DataFrame
        :return: Integer index at where new data has been added
        """
        latest_cache_dt = self.df.iloc[-1].name
        result = df[df.index == latest_cache_dt]
        if result.empty:
            raise NoOverlapError('Update DataFrame has no overlap with cached DataFrame')
        df = df[df.index > latest_cache_dt]
        df = pd.concat([self.df, df])
        self.set_df(df)
        return self.df.index.get_loc(latest_cache_dt) + 1

    def get_copy_df(self, count=-1):
        if count == -1 or count >= len(self.df):
            return self.df.copy()
        df = self.df.iloc[count * -1:]
        return df.copy()

    def is_full(self):
        return len(self.df) >= self.max_size
