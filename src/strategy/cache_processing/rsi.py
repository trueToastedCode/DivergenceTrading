def add_rsi(df, new_data_int_idx, new_data_dt_idx):
    if new_data_int_idx == -1:
        df['RSI'] = df.apply(
            lambda row: 100 - (100 / (1 + (row.SMMAUp / row.SMMADown))),
            axis=1
        )
    else:
        df.loc[df.index >= new_data_dt_idx, 'RSI'] = df.iloc[new_data_int_idx:].apply(
            lambda row: 100 - (100 / (1 + (row.SMMAUp / row.SMMADown))),
            axis=1
        )
