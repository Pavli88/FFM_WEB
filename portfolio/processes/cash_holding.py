from portfolio.models import *
import pandas as pd
import datetime
import numpy as np
from datetime import timedelta
from mysite.my_functions.general_functions import *


def cash_holding(portfolio, calc_date):

    t_min_one_date = previous_business_day(str(calc_date))
    date = datetime.datetime.strptime(str(calc_date), '%Y-%m-%d')

    try:
        # Intraday cash movement
        trades_df = pd.DataFrame(list(CashFlow.objects.filter(portfolio_code=portfolio).filter(date=date).values('portfolio_code', 'amount', 'date', 'currency')))
    except:
        trades_df = pd.DataFrame(columns=["portfolio_code", "amount", "date", "currency"])

    # Previous day cash holding
    try:
        previous_day_positions = pd.DataFrame(list(CashHolding.objects.filter(date=t_min_one_date).filter(portfolio_code=portfolio).values()))
    except:
        previous_day_positions = pd.DataFrame(columns=["portfolio_code", "amount", "date", "currency"])

    added_df = trades_df.append(previous_day_positions)

    if added_df.empty is True:
        return 'empty portfolio'
    else:
        aggregated_df = pd.pivot_table(added_df, values='amount', index='currency', aggfunc=np.sum)

    # Saving data to database
    for index, row in aggregated_df.iterrows():
        if row['amount'] == 0.0:
            try:
                CashHolding.objects.get(portfolio_code=portfolio, currency=index, date=date).delete()
            except:
                pass
        else:
            try:
                position = CashHolding.objects.get(portfolio_code=portfolio, currency=index, date=date)
                position.amount = row['amount']
                position.save()
            except:
                CashHolding(portfolio_code=portfolio,
                            currency=index,
                            amount=row['amount'],
                            date=date).save()

    return str(calc_date) + " Ending Balance " + str(row['amount'])