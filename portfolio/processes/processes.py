from portfolio.models import *
import pandas as pd
import datetime
from datetime import timedelta
import numpy as np
from django.http import JsonResponse





def port_holding(portfolio, calc_date):
    print("=============================")
    print("PORTFOLIO HOLDING CALCULATION")
    print("=============================")
    print("PORTFOLIO:", portfolio)
    print("CALCULATION DATE:", calc_date)
    print("")


def nav_calc(portfolio, calc_date):
    print("=========================")
    print("PORTFOLIO NAV CALCULATION")
    print("=========================")
    print("PORTFOLIO:", portfolio)
    print("CALCULATION DATE:", calc_date)

    date = datetime.datetime.strptime(calc_date, '%Y-%m-%d').date()

    if date.weekday() == 6:
        response = {"message": calc_date + ": Sunday. Calculation is not executed at weekends"}
        return response
    elif date.weekday() == 5:
        response = {"message": calc_date + ": Saturday. Calculation is not executed at weekends"}
        return response
    elif date.weekday() == 0:
        day_swift = 3
    else:
        day_swift = 1

    t_min_one_date = date + timedelta(days=-day_swift)

    print("T-1 DATE:", t_min_one_date)
    print("Loading portfolio data from database")

    portfolio_data = Portfolio.objects.filter(portfolio_name=portfolio).values()

    # Checking if portfolio status is funded
    if portfolio_data[0]["status"] == "Not Funded":
        response = {"message": calc_date + ": Portfolio is not funded"}
        return response

    port_incep_date = portfolio_data[0]["inception_date"]

    print("PORTFOLIO INCEPTION DATE:", port_incep_date)

    if date < port_incep_date:
        response = {"message": calc_date + ": Calculation date is less than portfolio inception date. Calculation stopped!"}
        return response

    print(portfolio_data)
    print("--------------")
    print("Cash Valuation")
    print("--------------")

    if date == port_incep_date:
        cash_tmin_one = 0.0
        print("Cash T-1:", cash_tmin_one)
    else:
        cash_flow_t_min_one_table = pd.DataFrame(list(CashFlow.objects.filter(portfolio_name=portfolio, date=t_min_one_date).values()))

        try:
            cash_tmin_one = cash_flow_t_min_one_table["amount"].sum()
            print("Cash T-1:", cash_tmin_one)
        except:
            response = {"message": calc_date + ": There is no data for T-1. Calculation cannot be continued!"}
            return response

    cash_flow_table = pd.DataFrame(list(CashFlow.objects.filter(portfolio_name=portfolio, date=date).values()))
    cash_t = cash_flow_table["amount"].sum()

    print("Cash T:", cash_t)
    print("Cash T+T-1:", cash_t + cash_tmin_one)

    print("------------------")
    print("Position Valuation")
    print("------------------")

    response = {"message": ["Process finished"]}

    return response