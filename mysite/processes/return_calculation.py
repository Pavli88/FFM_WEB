
def cumulative_return_calc(data_series):
    return_list = [100]
    for record in enumerate(data_series):
        if record[0] == 0:
            return_record = return_list[-1]*((record[1]*100/100)+1)
        else:
            return_record = return_list[-1]*((record[1]*100/100)+1)
        return_list.append(round(return_record, 3))
    return return_list


def total_pnl_calc(data_series):
    return sum(data_series)
