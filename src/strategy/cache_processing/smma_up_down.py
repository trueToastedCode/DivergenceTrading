import numpy as np


def add_smma_up_down(df, new_data_int_idx, new_data_dt_idx, length):
    if new_data_int_idx == -1:
        _df = df.Close[:length + 1]
        c_up, c_down = 0, 0
        for a, b in zip(_df[::1], _df[1::1]):
            if b > a:
                c_up += b - a
            elif b < a:
                c_down += a - b
        smma_up, smma_down = [np.nan] * length, [np.nan] * length
        prev_smma_up, prev_smma_down = c_up / length, c_down / length
        prev_close = df.Close[length]
        smma_up.append(prev_smma_up)
        smma_down.append(prev_smma_down)
        for i in range(length + 1, len(df)):
            curr_close = df.Close[i]
            if curr_close > prev_close:
                c_up = curr_close - prev_close
                c_down = 0
            elif curr_close < prev_close:
                c_up = 0
                c_down = prev_close - curr_close
            else:
                c_up = 0
                c_down = 0
            curr_smma_up = (c_up + (prev_smma_up * (length - 1))) / length
            curr_smma_down = (c_down + (prev_smma_down * (length - 1))) / length
            smma_up.append(curr_smma_up)
            smma_down.append(curr_smma_down)
            prev_smma_up, prev_smma_down = curr_smma_up, curr_smma_down
            prev_close = curr_close
        df['SMMAUp'] = smma_up
        df['SMMADown'] = smma_down
    else:
        smma_up, smma_down = [], []
        prev_smma_up, prev_smma_down = df.SMMAUp[new_data_int_idx-1], df.SMMADown[new_data_int_idx-1]
        prev_close = df.Close[new_data_int_idx-1]
        for i in range(new_data_int_idx, len(df)):
            curr_close = df.Close[i]
            if curr_close > prev_close:
                c_up = curr_close - prev_close
                c_down = 0
            elif curr_close < prev_close:
                c_up = 0
                c_down = prev_close - curr_close
            else:
                c_up = 0
                c_down = 0
            curr_smma_up = (c_up + (prev_smma_up * (length - 1))) / length
            curr_smma_down = (c_down + (prev_smma_down * (length - 1))) / length
            smma_up.append(curr_smma_up)
            smma_down.append(curr_smma_down)
            prev_smma_up, prev_smma_down = curr_smma_up, curr_smma_down
            prev_close = curr_close
        df.loc[df.index >= new_data_dt_idx, 'SMMAUp'] = smma_up
        df.loc[df.index >= new_data_dt_idx, 'SMMADown'] = smma_down
