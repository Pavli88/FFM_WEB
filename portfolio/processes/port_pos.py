from portfolio.models import *
import pandas as pd
import datetime
import numpy as np
from datetime import timedelta
from mysite.my_functions.general_functions import *


def portfolio_positions(portfolio, calc_date):

    """
    Portfolio position calculator
    :param portfolio: name of the porfolio
    :param calc_date: calculation date. Date time format
    :return:
    """

    t_min_one_date = previous_business_day(str(calc_date))
    date = datetime.datetime.strptime(str(calc_date), '%Y-%m-%d')

    try:
        # Intraday positioning
        trades_df = pd.DataFrame(list(Trade.objects.filter(portfolio_name=portfolio).filter(date=date).values('portfolio_name', 'security', 'quantity', 'date')))
    except:
        trades_df = pd.DataFrame(columns=['portfolio_name', 'security', 'quantity', 'date'])

    # Previous day positioning
    try:
        previous_day_positions = pd.DataFrame(list(Positions.objects.filter(date=t_min_one_date).filter(portfolio_name=portfolio).values()))
    except:
        previous_day_positions = pd.DataFrame(columns=['portfolio_name', 'security', 'quantity', 'date'])

    added_df = trades_df.append(previous_day_positions)

    if added_df.empty is True:
        return 'empty portfolio'
    else:
        aggregated_df = pd.pivot_table(added_df, values='quantity', index='security', aggfunc=np.sum)

    # Saving data to database
    for index, row in aggregated_df.iterrows():

        if row['quantity'] == 0.0:
            try:
                Positions.objects.get(portfolio_name=portfolio, security=index, date=date).delete()
            except:
                pass
        else:
            try:
                position = Positions.objects.get(portfolio_name=portfolio, security=index, date=date)
                position.quantity = row['quantity']
                position.save()
            except:
                Positions(portfolio_name=portfolio,
                          security=index,
                          quantity=row['quantity'],
                          date=date).save()

    response = "Process finished"

    return response