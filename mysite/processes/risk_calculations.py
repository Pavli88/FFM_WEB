from mysite.processes.return_calculation import *


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