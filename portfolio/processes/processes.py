from portfolio.models import *
import pandas as pd
import datetime
import numpy as np


def pos_calc(portfolio, calc_date):
    print("==============================")
    print("PORTFOLIO POSITIONS CALCULATOR")
    print("==============================")
    print("PORTFOLIO:", portfolio)
    print("CALCULATION DATE:", calc_date)
    print("")
    print("Fetching all trades from database")
    print("")

    date = datetime.datetime.strptime(calc_date, '%Y-%m-%d')

    try:
        trades_df = pd.DataFrame(list(Trade.objects.filter(portfolio_name=portfolio,
                                                           date=date).values()))

        aggregated_df = pd.pivot_table(trades_df, values='quantity', index='security', aggfunc=np.sum)

        print("AGGREGATED POSITIONS")
        print(trades_df)
        print("")
        print(aggregated_df)

        print("Clearing out previous records from database")

        Positions.objects.filter(date=date).delete()

        print("Inserting newly calculated position values")

        for index, row in aggregated_df.iterrows():
            Positions(portfolio_name=portfolio,
                      security=index,
                      quantity=row['quantity'],
                      date=date).save()

        print("END OF PROCESS!")
        print("")
    except:
        print("There are no positions for this date on the portfolio")

        Positions(portfolio_name=portfolio,
                  security=0,
                  quantity=0,
                  date=date).save()


def port_holding(portfolio, calc_date):
    print("=============================")
    print("PORTFOLIO HOLDING CALCULATION")
    print("=============================")
    print("PORTFOLIO:", portfolio)
    print("CALCULATION DATE:", calc_date)
    print("")