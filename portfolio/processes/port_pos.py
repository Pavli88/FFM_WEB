from portfolio.models import *
import pandas as pd
import datetime
import numpy as np
from datetime import timedelta
from mysite.my_functions.general_functions import *


def portfolio_cositions(portfolio, calc_date):
    print("==============================")
    print("PORTFOLIO POSITIONS CALCULATOR")
    print("==============================")
    print("PORTFOLIO:", portfolio)
    print("CALCULATION DATE:", calc_date)

    pervious_business_day = previous_business_day(calc_date)

    print("T-1 BUSINESS DAY:", pervious_business_day)
    print("Trade positions calculation")

    date = datetime.datetime.strptime(calc_date, '%Y-%m-%d')

    try:
        # Intraday positioning
        trades_df = pd.DataFrame(list(Trade.objects.filter(portfolio_name=portfolio,
                                                           date=date).values()))

        trades_positions = pd.pivot_table(trades_df, values='quantity', index='security', aggfunc=np.sum)

        print("AGGREGATED POSITIONS")
        print(trades_df)
        print("")
        print(trades_positions)
    except:
        print("There were no trades on", calc_date, "for", portfolio)

        # Previous day positioning
    try:
        print("Fetching previous day positions")
        previous_day_positions = Positions.objects.filter(date=previous_business_day).filter(portfolio_name=portfolio).values()
        print(previous_day_positions)
    except:
        print("There are no positions for T-1.")
    print("Inserting newly calculated position values")

        # for index, row in aggregated_df.iterrows():
        #     Positions(portfolio_name=portfolio,
        #               security=index,
        #               quantity=row['quantity'],
        #               date=date).save()
        #
        # # Final positioning trade pos + T-1 positioning
        #
        # print("END OF PROCESS!")
        # print("")
        #
        # print("There are no positions for this date on the portfolio")
        #
        # Positions(portfolio_name=portfolio,
        #           security=0,
        #           quantity=0,
        #           date=date).save()

    response = "hello"

    return response