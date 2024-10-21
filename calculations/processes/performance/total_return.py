import datetime as dt
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
import pandas as pd
from portfolio.models import Portfolio, Nav, Transaction, TotalReturn
from django.db.models import Q
from django.db.models import Sum
from calculations.processes.performance.modified_dietz_return import modified_dietz_return

def first_day_calculator(day):
    if day.weekday() == 6:
        print('SUNDAY')
        return 2
    elif day.weekday() == 5:
        print('SATURDAY')
        return 3
    else:
        return 1


def previous_month_end(input_date):
    if isinstance(input_date, str):
        input_date = datetime.strptime(input_date, '%Y-%m-%d')
    first_day_of_current_month = input_date.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - relativedelta(days=1)
    return last_day_of_previous_month.date()

def previous_qtd_date(input_date):
    if isinstance(input_date, str):
        input_date = datetime.strptime(input_date, '%Y-%m-%d')  # Adjust format as needed
    year = input_date.year
    month = input_date.month

    if month in [1, 2, 3]:
        return datetime(year - 1, 12, 31).date()
    elif month in [4, 5, 6]:
        return datetime(year, 3, 31).date()
    elif month in [7, 8, 9]:
        return datetime(year, 6, 30).date()
    elif month in [10, 11, 12]:
        return datetime(year, 9, 30).date()

def previous_year_end(input_date):
    if isinstance(input_date, str):
        input_date = datetime.strptime(input_date, '%Y-%m-%d')  # Adjust format as needed
    last_day_of_previous_year = datetime(input_date.year - 1, 12, 31)
    return last_day_of_previous_year.date()

def months_earlier(input_date, months):
    if isinstance(input_date, str):
        input_date = datetime.strptime(input_date, '%Y-%m-%d')  # Adjust format as needed
    new_date = input_date - relativedelta(months=months)
    return new_date.date()

def month_end_dates(month, month_range, year=None):
    if year is None:
        year = datetime.now().year

    if month < 1 or month > 12:
        raise ValueError("Month must be between 1 and 12.")

    last_day_of_month = calendar.monthrange(year, month)[1]
    end_date_of_month = datetime(year, month, last_day_of_month)

    if month == 1:
        previous_month_end_date = datetime(year - 1, 12, 31)
    else:
        last_day_of_previous_month = calendar.monthrange(year, month - 1)[1]
        previous_month_end_date = datetime(year, month - month_range, last_day_of_previous_month)

    return end_date_of_month, previous_month_end_date

def total_return_calc(portfolio_code, period, end_date, start_date=None):
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

    # period_mapping = {
    #     '1m': 4,
    #     '3m': 12,
    #     '6m': 24,
    #     '1y': 52,
    # }
    #
    period_text_mapping = {
        '1m': '1 Month',
        '3m': '3 Months',
        '6m': '6 Months',
        'mtd': 'Month to Date',
        'qtd': 'Quarter to Date',
        'ytd': 'Year to Date',
        'si': 'Since Inception',
        'adhoc': 'Ad-Hoc'
    }

    # Defining start and end dates
    if period == 'si':
        start_date = portfolio_data.perf_start_date
    else:
        if portfolio_data.weekend_valuation is False:
            print('WEEKEND VALUATION NOT ALLOWED')
            if period == 'mtd':
                start_date = previous_month_end(input_date=end_date)
            elif period == 'ytd':
                start_date = previous_year_end(input_date=end_date)
            elif period == 'qtd':
                start_date = previous_qtd_date(input_date=end_date)
            elif period == '1m':
                start_date = months_earlier(input_date=end_date, months=1)
            else:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            if period == 'mtd':
                start_date = mtd_date
            elif period == 'ytd':
                start_date = ytd_date
            else:
                start_date = end_date - dt.timedelta(weeks=period_mapping[period])

    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Date checks if calculation period is valid
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

        # Calculation based on parameters
    nav_data = pd.DataFrame(Nav.objects.filter(portfolio_code=portfolio_code, date__range=(start_date, end_date)).values()).sort_values('date')[
        ['holding_nav', 'total_cf', 'date']]
    initial_value = nav_data['holding_nav'].to_list()[0]
    final_value = nav_data['holding_nav'].to_list()[-1]
    cash_flows = nav_data[nav_data['total_cf'] != 0]['total_cf'].to_list()
    cash_flow_dates = nav_data[nav_data['total_cf'] != 0]['date'].to_list()
    calculated_return = modified_dietz_return(start_date=start_date,
                                              end_date=end_date,
                                              initial_value=initial_value,
                                              final_value=final_value,
                                              cash_flows=cash_flows,
                                              cash_flow_dates=cash_flow_dates)

    print('NAV')
    print(nav_data)
    print('init', initial_value, 'final', final_value, 'cf', cash_flows, 'cfd', cash_flow_dates)
    print(calculated_return * 100)

    # # Saving record to database
    try:
        existing_return = TotalReturn.objects.get(portfolio_code=portfolio_code,
                                                  end_date=end_date,
                                                  period=period)
        existing_return.total_return = calculated_return
        existing_return.save()
    except TotalReturn.DoesNotExist:
        TotalReturn(portfolio_code=portfolio_data.portfolio_code,
                    end_date=end_date,
                    total_return=calculated_return,
                    period=period).save()

    response_list.append({'portfolio_code': portfolio_code,
                          'date': end_date,
                          'process': 'Total Return',
                          'exception': '-',
                          'status': 'Completed',
                          'comment': period_text_mapping[period] + ' Return: ' + str(
                              round(calculated_return * 100, 2)) + ' %'})

    return response_list + error_list