

# Cumulative return calculation based on return series
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


def drawdown_calc(data_series):
    cum_ret_series = cumulative_return_calc(data_series=data_series)

    drawdown_list = []

    for record in enumerate(cum_ret_series):
        try:
            series_max = max(cum_ret_series[0: record[0]])

            if record[1] > series_max:
                drawdown_list.append(0)
            else:
                drawdown_list.append(round(((record[1]/series_max)-1)*100, 2))
        except:
            pass

    return drawdown_list