import datetime as dt
from datetime import datetime
import pandas as pd
from portfolio.models import Portfolio, Nav, Transaction, TotalReturn


def first_day_calculator(day):
    if day.weekday() == 6:
        print('SUNDAY')
        return 2
    elif day.weekday() == 5:
        print('SATURDAY')
        return 3
    else:
        return 1


def total_return_calc(portfolio_code, period, end_date):
    print('TOTAL RETURN CALC')
    print('PORTFOLIO CODE:', portfolio_code, 'PERIOD:', period, 'END DATE:', end_date)

    response_list = []
    error_list = []

    portfolio_data = Portfolio.objects.get(portfolio_code=portfolio_code)
    print(portfolio_data.perf_start_date)

    # Check if performance start date is assigned to the fund
    if portfolio_data.perf_start_date is None:
        error_list.append({'portfolio_code': portfolio_code,
                           'date': end_date,
                           'process': 'Total Return',
                           'exception': 'Missing Performance Start Date',
                           'status': 'Error',
                           'comment': 'Performance start date is not assigned to the portfolio'})
        return response_list + error_list

    print('Inception Date:', portfolio_data.inception_date, type(portfolio_data.inception_date))
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    mtd_date = end_date.replace(day=1)
    ytd_date = end_date.replace(month=1).replace(day=1)

    if end_date.month == 1 or end_date.month == 2 or end_date.month == 3:
        qtd_date = end_date.replace(month=1).replace(day=1)
    elif end_date.month == 4 or end_date.month == 5 or end_date.month == 6:
        qtd_date = end_date.replace(month=4).replace(day=1)
    elif end_date.month == 7 or end_date.month == 8 or end_date.month == 9:
        qtd_date = end_date.replace(month=7).replace(day=1)
    else:
        qtd_date = end_date.replace(month=10).replace(day=1)

    print(end_date.replace(day=1).weekday())
    print(end_date.replace(month=1).replace(day=1))
    period_mapping = {
        '1m': 4,
        '3m': 12,
        '6m': 24,
        '1y': 52,
    }

    period_text_mapping = {
        '1m': '1 Month',
        '3m': '3 Months',
        '6m': '6 Months',
        'mtd': 'Month to Date',
        'qtd': 'Quarter to Date',
        'ytd': 'Year to Date',
        'si': 'Since Inception'
    }

    if period == 'si':
        start_date = portfolio_data.perf_start_date
    else:
        if portfolio_data.weekend_valuation is False:
            print('WEEKEND VALUATION NOT ALLOWED')
            if period == 'mtd':
                start_date = mtd_date.replace(day=first_day_calculator(day=mtd_date))
            elif period == 'ytd':
                start_date = ytd_date.replace(day=first_day_calculator(day=ytd_date))
            elif period == 'qtd':
                start_date = qtd_date.replace(day=first_day_calculator(day=qtd_date))
            else:
                start_date = end_date - dt.timedelta(weeks=period_mapping[period])
        else:
            if period == 'mtd':
                start_date = mtd_date
            elif period == 'ytd':
                start_date = ytd_date
            else:
                start_date = end_date - dt.timedelta(weeks=period_mapping[period])

    print('END DATE:', end_date, type(end_date))
    print('START DATE:', start_date, type(start_date))
    print('CURRENT MONTH', end_date.month)

    if end_date < portfolio_data.perf_start_date:
        error_list.append({'portfolio_code': portfolio_code,
                           'date': end_date,
                           'process': 'Total Return',
                           'exception': 'Incorrect End Date',
                           'status': 'Alert',
                           'comment': period_text_mapping[period] + ' end date (' + str(end_date) + ') is less than inception date (' + str(portfolio_data.perf_start_date) + ')'})
        return response_list + error_list

    # Check if start date is less than inception date
    if start_date < portfolio_data.perf_start_date:
        error_list.append({'portfolio_code': portfolio_code,
                           'date': end_date,
                           'process': 'Total Return',
                           'exception': 'Incorrect Start Date',
                           'status': 'Alert',
                           'comment': period_text_mapping[period] + ' start date (' + str(start_date) + ') is less than inception date (' + str(portfolio_data.perf_start_date) + ')'})
        return response_list + error_list

    number_of_days = (end_date - start_date).days

    print('NUMBER OF DAYS:', number_of_days)
    print('')

    # Quering out start and end NAV
    try:
        start_nav = Nav.objects.filter(date=start_date, portfolio_code=portfolio_code).values()[0]['total']
    except:
        error_list.append({'portfolio_code': portfolio_code,
                           'date': end_date,
                           'process': 'Total Return',
                           'exception': 'Missing Starting Valuation',
                           'status': 'Error',
                           'comment': 'Missing Valuation as of ' + str(start_date)})
        return response_list + error_list

    try:
        end_nav = Nav.objects.filter(date=end_date, portfolio_code=portfolio_code).values()[0]['total']
    except:
        error_list.append({'portfolio_code': portfolio_code,
                           'date': end_date,
                           'process': 'Total Return',
                           'exception': 'Missing Ending Valuation',
                           'status': 'Error',
                           'comment': 'Missing Valuation as of ' + str(end_date)})
        return response_list + error_list

    print('')
    print('START NAV')
    print(start_nav)
    print('')
    print('END NAV')
    print(end_nav)
    print('')

    # Quering out transactions for the period
    transactions = pd.DataFrame(
        Transaction.objects.filter(portfolio_code=portfolio_code, trade_date__gte=start_date, trade_date__lte=end_date).values())

    # Weighted Cash Flow table calculation------------------------------------------------------------------------------
    cash_flow_table = transactions[
        (transactions['transaction_type'] == 'Subscription') | (transactions['transaction_type'] == 'Redemption')][['net_cashflow', 'trade_date']]
    cash_flow_table['days_left'] = [(date-start_date).days for date in cash_flow_table['trade_date']]
    cash_flow_table['ratio'] = cash_flow_table['days_left'] / number_of_days
    cash_flow_table['weighted_cf'] = cash_flow_table['ratio'] * cash_flow_table['net_cashflow']
    total_cf = cash_flow_table['net_cashflow'].sum()
    total_weighted_cf = cash_flow_table['weighted_cf'].sum()

    print(cash_flow_table)
    print('TOTAL CF', total_cf)
    print('TOTAL WEIGHTED CF', total_weighted_cf)
    print('')

    # Total Return Calculation
    total_return = round((end_nav - start_nav - total_cf) / (start_nav + total_weighted_cf), 4)
    print('RET 1', total_return)

    # Saving record to database
    try:
        existing_return = TotalReturn.objects.get(portfolio_code=portfolio_code,
                                                  end_date=end_date,
                                                  period=period)
        existing_return.total_return = total_return
        existing_return.save()
    except TotalReturn.DoesNotExist:
        TotalReturn(portfolio_code=portfolio_data.portfolio_code,
                    end_date=end_date,
                    total_return=total_return,
                    period=period).save()

    response_list.append({'portfolio_code': portfolio_code,
                          'date': end_date,
                          'process': 'Total Return',
                          'exception': '-',
                          'status': 'Completed',
                          'comment': period_text_mapping[period] + ' Return: ' + str(round(total_return * 100, 2)) + ' %'})

    return response_list + error_list