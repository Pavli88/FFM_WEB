# Package Imports
import pandas as pd

# Model Imports
from robots.models import Balance, MonthlyReturns


def monthly_return_calc(robot_id, start_date, end_date):
    balances = pd.DataFrame(Balance.objects.filter(robot_id=robot_id,
                                                   date__gte=start_date,
                                                   date__lte=end_date).values())
    # print(balances)
    if balances.empty:
        return 'No balance'
    total_cash_flow = balances['cash_flow'].sum()
    opening_balance = list(balances['opening_balance'])[0]
    closing_balance = list(balances['close_balance'])[-1]
    performance = round((closing_balance - opening_balance - total_cash_flow) / opening_balance, 5)
    try:
        monthly_return = MonthlyReturns.objects.get(robot_id=robot_id, date=end_date)
        monthly_return.ret = performance
        monthly_return.save()
    except MonthlyReturns.DoesNotExist:
        MonthlyReturns(robot_id=robot_id,
                       date=end_date,
                       ret=performance).save()
    return 'Calculation completed'