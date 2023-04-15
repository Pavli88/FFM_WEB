from robots.models import *
import pandas as pd
import numpy as np
import datetime
from datetime import timedelta
from mysite.models import *


def balance_calc(robot_id, calc_date):
    date = calc_date
    robot_data = Robots.objects.filter(id=robot_id).values()
    # Checking if calculation date is less then robot inception data
    if date < robot_data[0]["inception_date"]:
        return robot_id + " - " + "Calculation date (" + str(date.date()) +") is less than robot inception date (" + \
               str(robot_data[0]["inception_date"]) + ". Calculation is stopped."

    # Checking if calculation date is weekend or not
    if date.weekday() == 6:
        return str(robot_id) + " - " + str(calc_date) + " is Sunday. Calculation is not executed at weekends"
    elif date.weekday() == 5:
        return str(robot_id) + " - " + str(calc_date) + " is Saturday. Calculation is not executed at weekends"
    elif date.weekday() == 0:
        day_swift = 3
    else:
        day_swift = 1

    t_min_one_date = date + timedelta(days=-day_swift)

    # Aggregated trade pnl calculation
    trades_df_closed = pd.DataFrame(list(RobotTrades.objects.filter(robot=robot_id,
                                                                    close_time=date,
                                                                    status="CLOSED").values()))

    if trades_df_closed.empty:
        realized_pnl = 0.0
    else:
        realized_pnl = trades_df_closed["pnl"].sum()

    # Aggregated cash flow calculation
    cash_flow_table = pd.DataFrame(list(RobotCashFlow.objects.filter(robot_name=robot_id,
                                                              date=date).values()))

    if cash_flow_table.empty:
        cash_flow = 0.0
    else:
        cash_flow = cash_flow_table["cash_flow"].sum()

    open_balance_table = pd.DataFrame(list(Balance.objects.filter(robot_id=robot_id, date=t_min_one_date).values()))

    if open_balance_table.empty:
        if robot_data[0]["inception_date"] == date:
            open_balance = 0.0
            if cash_flow == 0.0:
                return str(robot_id) + " - " + str(calc_date) + " - Robot is not funded. Calculation is not possible."
            else:
                ret = ((realized_pnl + cash_flow) / cash_flow)-1
        else:
            return str(robot_id) + " - " + str(calc_date) + " There is no opening balance data for T-1"
    else:
        open_balance = open_balance_table["close_balance"].sum()

        # Checks if previous day's opening balance is zero or not
        if open_balance == 0.0:
            ret = 0.0
        else:
            ret = ((realized_pnl + open_balance) / open_balance)-1

    close_balance = cash_flow + realized_pnl + open_balance

    # Saving down calculated balance to database
    try:
        robot_balance = Balance.objects.get(date=date, robot_id=robot_id)
        robot_balance.opening_balance = round(open_balance, 4)
        robot_balance.close_balance = round(close_balance, 4)
        robot_balance.cash_flow = cash_flow
        robot_balance.realized_pnl = round(realized_pnl, 4)
        robot_balance.ret = round(ret, 4)
        robot_balance.unrealized_pnl = 0.0
        robot_balance.date = date
        robot_balance.save()
        rec_status = "Updated Record"
    except:
        Balance(robot_id=robot_id,
                opening_balance=round(open_balance, 4),
                close_balance=round(close_balance, 4),
                cash_flow=cash_flow,
                realized_pnl=round(realized_pnl, 4),
                ret=round(ret, 4),
                unrealized_pnl=0.0,
                date=date).save()
        rec_status = "New Record"

    return str(robot_id) + " - " + str(rec_status) + " - Date " + str(calc_date) + " - T-1 Date " + \
           str(t_min_one_date) + " - Realized Pnl " + str(round(realized_pnl, 2)) + \
           " - Cash Flow " + str(cash_flow) + " - Opening Balance " + str(round(open_balance, 2)) + \
           " - Closing Balance: " + str(round(close_balance, 2)) + " - Return " + str(round(ret, 4))
