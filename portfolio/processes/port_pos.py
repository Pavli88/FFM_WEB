from portfolio.models import *
import pandas as pd
import datetime
import numpy as np
from datetime import timedelta
from mysite.my_functions.general_functions import *


def portfolio_cositions(portfolio, calc_date):

    """
    Portfolio position calculator
    :param portfolio: name of the porfolio
    :param calc_date: calculation date. Date time format
    :return:
    """

    print("==============================")
    print("PORTFOLIO POSITIONS CALCULATOR")
    print("==============================")
    print("PORTFOLIO:", portfolio)
    print("CALCULATION DATE:", calc_date)

    t_min_one_date = previous_business_day(str(calc_date))

    print("T-1 BUSINESS DAY:", t_min_one_date)

    date = datetime.datetime.strptime(str(calc_date), '%Y-%m-%d')

    try:
        # Intraday positioning
        trades_df = pd.DataFrame(list(Trade.objects.filter(portfolio_name=portfolio).filter(date=date).values('portfolio_name', 'security', 'quantity', 'date')))
        print("")
        print("TRADES")
        print(trades_df)
    except:
        print("There were no trades on", str(calc_date), "for", portfolio)

    # Previous day positioning
    try:
        print("")
        print("T-1 POSITIONS")
        previous_day_positions = pd.DataFrame(list(Positions.objects.filter(date=t_min_one_date).filter(portfolio_name=portfolio).values()))
        print(previous_day_positions)
    except:
        print("There are no positions for T-1.")

    print("")
    print("CALCULATION DATE POSITIONS")
    added_df = trades_df.append(previous_day_positions)
    print(added_df)

    if added_df.empty is True:
        print("There are no positions held in the portfolio")
        return 'empty portfolio'
    else:
        aggregated_df = pd.pivot_table(added_df, values='quantity', index='security', aggfunc=np.sum)

    print("")
    print("AGGREGATED POSITIONS")
    print(aggregated_df)

    print("")
    print("Inserting newly calculated position values")

    for index, row in aggregated_df.iterrows():

        if row['quantity'] == 0.0:
            print("Traded out position, deleting from positions table", index)
            try:
                Positions.objects.get(portfolio_name=portfolio, security=index, date=date).delete()
            except:
                pass
        else:
            try:
                position = Positions.objects.get(portfolio_name=portfolio, security=index, date=date)
                position.quantity = row['quantity']
                position.save()
                print("Updating existing position record:", index, row['quantity'])
            except:
                Positions(portfolio_name=portfolio,
                          security=index,
                          quantity=row['quantity'],
                          date=date).save()
                print("New position record:", index, row['quantity'])

    response = "Process finished"

    return response