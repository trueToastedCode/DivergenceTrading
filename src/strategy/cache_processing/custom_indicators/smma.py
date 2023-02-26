import pandas_ta as ta
import pandas as pd


def add_smma(df, new_data_int_idx, new_data_dt_idx, source, length, target):
    if new_data_int_idx == -1:
        first_dt_idx = df.query(f'{source}.notnull()').index.min()
        assert pd.notnull(first_dt_idx)
        my_int_idx = df.index.get_loc(first_dt_idx) + length
        smma = ta.sma(df[source].iloc[:my_int_idx], length=length).to_list()
        prev_smma = smma[-1]
        assert pd.notnull(prev_smma)
        for i in range(my_int_idx, len(df)):
            current_smma = (prev_smma * (length - 1) + df[source][i]) / length
            smma.append(current_smma)
            prev_smma = current_smma
        df[target] = smma
    else:
        smma = []
        prev_smma = df[target][new_data_int_idx - 1]
        assert pd.notnull(prev_smma)
        for i in range(new_data_int_idx, len(df)):
            current_smma = (prev_smma * (length - 1) + df[source][i]) / length
            smma.append(current_smma)
            prev_smma = current_smma
        df.loc[df.index >= new_data_dt_idx, target] = smma
